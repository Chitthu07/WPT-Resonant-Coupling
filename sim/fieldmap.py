"""|B| field map of the coil pair (1 A in the primary) by the Biot-Savart law.

Biot-Savart (CONVENTIONS.md Section 4), discretised over the same straight segments as A-S1:
    B(r) = (mu0 I / 4 pi) sum_j dl_j x R_j / |R_j|^3,   R_j = r - r_mid,j
Only the primary carries current (secondary open-circuited); the secondary is drawn
for reference at z = d. Evaluated on the x-z plane through the common axis (y = 0).

Validation reference, on-axis field of a loop of radius a (summed over turns, N = 1 each):
    Bz(z) = mu0 I a^2 / [2 (a^2 + z^2)^(3/2)]

Run from the project root:  python -m sim.fieldmap
"""

from pathlib import Path

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import LogNorm

from sim import params
from sim.params import MU0
from sim.coupling import coil_segments
from sim.style import save_fig

ROOT = Path(__file__).resolve().parent.parent
I1 = 1.0                                   # primary current for the map [A]
D_MAP = params.d_fieldmap                  # secondary position for the map [m]
X_RANGE = (-0.15, 0.15)                    # [m]
Z_RANGE = (-0.05, 0.15)                    # [m]
STEP = 1e-3                                # grid spacing [m]


def biot_savart(points, mid, dl, current=1.0, chunk=4000):
    """B [T] at points (P, 3) from segments (mid, dl): (mu0 I/4pi) sum dl x R / |R|^3."""
    B = np.zeros((len(points), 3))
    for s in range(0, len(points), chunk):
        R = points[s:s + chunk, None, :] - mid[None, :, :]        # (p, n, 3)
        Rn3 = np.linalg.norm(R, axis=2, keepdims=True) ** 3
        B[s:s + chunk] = np.sum(np.cross(dl[None, :, :], R) / Rn3, axis=1)
    return MU0 * current / (4 * np.pi) * B


def bz_axis_closed_form(radii, z, current=1.0):
    """On-axis Bz [T] of coaxial loops at z = 0: sum_i mu0 I a_i^2 / [2 (a_i^2 + z^2)^(3/2)]."""
    a = np.asarray(radii)[:, None]
    return np.sum(MU0 * current * a ** 2 / (2 * (a ** 2 + np.asarray(z)[None, :] ** 2) ** 1.5), axis=0)


def field_on_grid(radii, x, z, current=1.0):
    """Bx, Bz [T] on the y = 0 plane for the primary at z = 0 (arrays shaped (len(z), len(x)))."""
    mid, dl = coil_segments(radii, z=0.0)
    X, Z = np.meshgrid(x, z)
    pts = np.column_stack([X.ravel(), np.zeros(X.size), Z.ravel()])
    B = biot_savart(pts, mid, dl, current)
    return B[:, 0].reshape(X.shape), B[:, 2].reshape(X.shape)


def near_wire_mask(radii, x, z, z_coils, r_mask):
    """True where a grid point is within r_mask of any wire cross-section (x = +/- r_i, z = z_coil)."""
    X, Z = np.meshgrid(x, z)
    mask = np.zeros(X.shape, dtype=bool)
    for zc in z_coils:
        for r in radii:
            for sx in (-1, 1):
                mask |= np.hypot(X - sx * r, Z - zc) < r_mask
    return mask


def validate(radii):
    """Print and return the on-axis, monotonic and symmetry checks."""
    mid, dl = coil_segments(radii, z=0.0)
    z = np.array([-0.05, -0.02, 0.0, 0.01, 0.03, 0.05, 0.10, 0.15])
    pts = np.column_stack([np.zeros_like(z), np.zeros_like(z), z])
    B = biot_savart(pts, mid, dl, I1)
    Bcf = bz_axis_closed_form(radii, z, I1)
    err = 100 * (B[:, 2] - Bcf) / Bcf
    print("On-axis check (Biot-Savart segments vs closed form, 1 A):")
    print(f"{'z [cm]':>7} {'Bz num [uT]':>12} {'Bz cf [uT]':>12} {'diff %':>8} {'|Bx|/|Bz|':>10}")
    for zi, b, bc, e in zip(z, B, Bcf, err):
        print(f"{zi*100:7.1f} {b[2]*1e6:12.4f} {bc*1e6:12.4f} {e:8.4f} {np.hypot(b[0], b[1])/abs(b[2]):10.1e}")
    max_err = np.max(np.abs(err))
    print(f"  max |diff| = {max_err:.4f} %  -> {'PASS' if max_err < 1 else 'FAIL'} (< 1 %)")

    zf = np.linspace(0, 0.15, 151)                          # monotonic decrease away from primary
    Bp = np.linalg.norm(biot_savart(np.column_stack([0 * zf, 0 * zf, zf]), mid, dl), axis=1)
    Bm = np.linalg.norm(biot_savart(np.column_stack([0 * zf, 0 * zf, -zf]), mid, dl), axis=1)
    mono = np.all(np.diff(Bp) < 0) and np.all(np.diff(Bm) < 0)
    print(f"|B| strictly decreasing along the axis for z > 0 and z < 0: {mono}")
    return max_err, mono


def main():
    g = params.get_geometry()
    tag = "PLACEHOLDER GEOMETRY" if g["placeholder"] else "design geometry"
    radii, r_w = g["radii"], g["wire_d"] / 2
    print(f"=== A-S3 |B| field map ({tag}), I1 = {I1} A, secondary at d = {D_MAP*100:.0f} cm (open) ===")
    max_err, mono = validate(radii)

    x = np.arange(X_RANGE[0], X_RANGE[1] + STEP / 2, STEP)
    z = np.arange(Z_RANGE[0], Z_RANGE[1] + STEP / 2, STEP)
    x[np.abs(x) < 1e-12] = 0.0
    Bx, Bz = field_on_grid(radii, x, z, I1)
    Bmag = np.hypot(Bx, Bz)
    sym = np.nanmax(np.abs(Bmag - Bmag[:, ::-1]) / Bmag)
    print(f"Mirror symmetry max | |B|(x) - |B|(-x) | / |B| on grid = {sym:.1e}")

    # Mask points within ~2 wire radii of the primary wires (segment discretisation is poor there)
    mask = near_wire_mask(radii, x, z, [0.0], 2 * r_w)
    Bplot = np.ma.array(Bmag * 1e6, mask=mask)                # uT
    vmin, vmax = np.percentile(Bplot.compressed(), [0.5, 99.0])
    print(f"Colour range: {vmin:.2f} .. {vmax:.0f} uT (0.5 / 99 percentiles); "
          f"|B| at coil centre = {Bmag[np.argmin(np.abs(z)), np.argmin(np.abs(x))]*1e6:.1f} uT")

    # --- Poster figure ---
    with plt.rc_context({"font.size": 18, "axes.labelsize": 20, "xtick.labelsize": 18,
                         "ytick.labelsize": 18, "legend.fontsize": 16, "axes.grid": False}):
        fig, ax = plt.subplots(figsize=(12, 8))
        pc = ax.pcolormesh(x * 100, z * 100, Bplot, norm=LogNorm(vmin=vmin, vmax=vmax),
                           cmap="viridis", shading="auto", rasterized=True)
        ax.streamplot(x * 100, z * 100, np.where(mask, np.nan, Bx), np.where(mask, np.nan, Bz),
                      color="white", linewidth=0.8, density=1.6, arrowsize=1.0)
        for zc, col, lab in [(0.0, "red", f"Primary, {I1:g} A"),
                             (D_MAP, "orange", f"Secondary (open), d = {D_MAP*100:g} cm")]:
            xs = np.concatenate([-radii, radii]) * 100
            ax.plot(xs, np.full_like(xs, zc * 100), "s", color=col, ms=4, mec="black", mew=0.5,
                    linestyle="none", label=lab)
        ax.set_xlabel("x (cm)")
        ax.set_ylabel("z (cm)")
        ax.set_aspect("equal")
        ax.set_xlim(x[0] * 100, x[-1] * 100)
        ax.set_ylim(z[0] * 100, z[-1] * 100)
        cb = fig.colorbar(pc, ax=ax, shrink=0.85, pad=0.02)
        cb.set_label(r"$|B|$ ($\mu$T) for $I_1$ = 1 A")
        ticks = [t for t in (1, 2, 5, 10, 20, 50, 100, 200, 500, 1000) if vmin <= t <= vmax]
        cb.set_ticks(ticks)
        cb.set_ticklabels([f"{t:g}" for t in ticks])           # plain uT values, readable on a poster
        cb.minorticks_off()
        ax.legend(loc="upper right", framealpha=0.9)
        title = r"Magnetic flux density $|B|$, x-z plane through the axis"
        if g["placeholder"]:
            title = "PLACEHOLDER GEOMETRY\n" + title
        ax.set_title(title)
        fig.tight_layout()
        for p in save_fig(fig, "fig_B_map"):
            print(f"Saved {p.relative_to(ROOT)}")
        plt.close(fig)
    return max_err, mono, sym


if __name__ == "__main__":
    main()
