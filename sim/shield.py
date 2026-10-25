"""Task C-S2: Shield (Al/Cu plate) and ferrite sheet effect behind the secondary coil.

Implements the electromagnetic boundary-condition image model and surface-impedance
eddy-current loss integral from A-T2 (theory/A-T2_course_links.md) using the exact
10-turn spiral geometry in sim/params.py.

Outputs:
    - data/sim_shield.csv
    - figs/fig_k_vs_gap_shield.pdf / .png
    - figs/fig_loss_vs_gap_shield.pdf / .png
    - figs/fig_B_shield_compare.pdf / .png

Run from repo root:
    python -m sim.shield
"""

from pathlib import Path
import sys
import csv
import numpy as np
from scipy.special import ellipk, ellipe
import matplotlib.pyplot as plt
from matplotlib.colors import LogNorm

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from sim import params, style

DATA_DIR = REPO_ROOT / "data"

# Material constants (matching theory/A-T2_course_links.md)
SIGMA_AL = 3.5e7          # Aluminium conductivity [S/m]
SIGMA_CU = 5.8e7          # Copper conductivity [S/m]
MU_R_FERRITE = 2000.0     # MnZn ferrite relative permeability [-]
GAPS_MM = np.array([5.0, 10.0, 20.0, 40.0])  # Plate-to-secondary gaps g [mm] (Task C-S2)
D_LIST_CM = np.array([3.0, 5.0])             # Axial coil spacings d [cm]


def M_coaxial_loops(a, b, z_sep):
    """Exact mutual inductance [H] between two coaxial filament loops of radii a, b at spacing z_sep."""
    z_sep = float(abs(z_sep))
    if z_sep == 0.0 and np.isclose(a, b):
        return 0.0
    m = 4.0 * a * b / ((a + b) ** 2 + z_sep ** 2)
    k = np.sqrt(m)
    return params.MU0 * np.sqrt(a * b) * ((2.0 / k - k) * ellipk(m) - (2.0 / k) * ellipe(m))


def M_spiral_pair(radii, z_sep):
    """Total mutual inductance [H] between two identical coaxial flat spirals at spacing z_sep [m]."""
    total = 0.0
    for a in radii:
        for b in radii:
            total += M_coaxial_loops(a, b, z_sep)
    return total


def L_spiral_self(radii, wire_radius):
    """Filament-sum self-inductance [H] of the flat spiral coil."""
    total = 0.0
    for i, a in enumerate(radii):
        total += params.MU0 * a * (np.log(8.0 * a / wire_radius) - 2.0)
        for j, b in enumerate(radii):
            if i != j:
                total += M_coaxial_loops(a, b, 0.0)
    return total


def B_components_loop(a, rho, z, I=1.0):
    """Cylindrical field components (B_rho, B_z) [T] of a single loop of radius a at (rho, z)."""
    rho_arr = np.asarray(rho, dtype=float)
    z_arr = np.asarray(z, dtype=float)
    rho_b, z_b = np.broadcast_arrays(rho_arr, z_arr)

    B_rho = np.zeros_like(rho_b, dtype=float)
    B_z = np.zeros_like(rho_b, dtype=float)

    denom = (a + rho_b) ** 2 + z_b ** 2
    denom_minus = (a - rho_b) ** 2 + z_b ** 2
    # Prevent division by zero right on the wire filament
    denom_minus = np.where(denom_minus < 1e-18, 1e-18, denom_minus)
    m = np.clip(4.0 * a * rho_b / denom, 0.0, 1.0 - 1e-15)

    K = ellipk(m)
    E = ellipe(m)

    # Axial component B_z (valid everywhere including rho = 0)
    B_z = (params.MU0 * I / (2.0 * np.pi * np.sqrt(denom))) * (
        K + ((a ** 2 - rho_b ** 2 - z_b ** 2) / denom_minus) * E
    )

    # Radial component B_rho (zero on axis rho = 0)
    mask = rho_b > 1e-12
    if np.any(mask):
        r_m = rho_b[mask]
        z_m = z_b[mask]
        den_m = denom[mask]
        den_min_m = denom_minus[mask]
        K_m = K[mask]
        E_m = E[mask]
        B_rho[mask] = (params.MU0 * I / (2.0 * np.pi)) * (z_m / (r_m * np.sqrt(den_m))) * (
            -K_m + ((a ** 2 + r_m ** 2 + z_m ** 2) / den_min_m) * E_m
        )

    return B_rho, B_z


def B_components_spiral(radii, rho, z, I=1.0):
    """Superpose (B_rho, B_z) [T] over all N turns of the flat spiral at plane z=0."""
    B_rho_tot = 0.0
    B_z_tot = 0.0
    for a in radii:
        br, bz = B_components_loop(a, rho, z, I=I)
        B_rho_tot = B_rho_tot + br
        B_z_tot = B_z_tot + bz
    return B_rho_tot, B_z_tot


def compute_plate_eddy_loss(radii, g_m, f0_Hz, rho_max=0.30, n_pts=1500):
    """Compute time-averaged eddy power loss P_plate [W] (for 1 A peak coil current)
    and reflected series resistance dR = 2 * P_plate / |I|^2 [Ohm] for Al and Cu plates
    at distance g_m from a spiral coil carrying 1 A peak.

    By the PEC boundary condition (t >> delta), tangential magnetic field at the plate
    surface is doubled by the opposing image coil: H_t(rho) = 2 * B_rho_free(rho, g_m) / mu0.
    Surface power integral (Shevgaonkar Sec. 4.9 / A-T2 Sec. 2):
        P_plate = 0.5 * Rs * integral_0^inf |H_t(rho)|^2 * 2 * pi * rho d(rho)
    """
    w0 = 2.0 * np.pi * f0_Hz
    delta_al = np.sqrt(2.0 / (w0 * params.MU0 * SIGMA_AL))
    delta_cu = np.sqrt(2.0 / (w0 * params.MU0 * SIGMA_CU))
    Rs_al = 1.0 / (SIGMA_AL * delta_al)
    Rs_cu = 1.0 / (SIGMA_CU * delta_cu)

    rho_grid = np.linspace(0.0, rho_max, n_pts)
    B_rho_free, _ = B_components_spiral(radii, rho_grid, g_m, I=1.0)
    H_t = 2.0 * (B_rho_free / params.MU0)

    integrand = (H_t ** 2) * 2.0 * np.pi * rho_grid
    trapz_fn = getattr(np, "trapezoid", getattr(np, "trapz", None))
    int_Ht2 = float(trapz_fn(integrand, rho_grid))

    P_al_W = 0.5 * Rs_al * int_Ht2
    dR_al_Ohm = 2.0 * P_al_W
    P_cu_W = 0.5 * Rs_cu * int_Ht2
    dR_cu_Ohm = 2.0 * P_cu_W

    return P_al_W, dR_al_Ohm, P_cu_W, dR_cu_Ohm


def run_shield_sweep():
    """Run the gap sweep g = [5, 10, 20, 40] mm for d = 3 cm and 5 cm and write data/sim_shield.csv."""
    geom = params.get_geometry()
    radii = geom["radii"]
    r_w = geom["wire_d"] / 2.0
    f0 = params.f0

    L0 = L_spiral_self(radii, r_w)
    alpha_fe = (MU_R_FERRITE - 1.0) / (MU_R_FERRITE + 1.0)

    DATA_DIR.mkdir(parents=True, exist_ok=True)
    csv_path = DATA_DIR / "sim_shield.csv"

    rows = []
    for d_cm in D_LIST_CM:
        d_m = d_cm * 1e-2
        M0 = M_spiral_pair(radii, d_m)
        k0 = M0 / L0

        for g_mm in GAPS_MM:
            g_m = g_mm * 1e-3
            # Plate sits at z = d + g (gap g behind secondary at z = d; primary is at z = 0).
            # Image of primary sits at z = 2(d + g) -> spacing to primary is 2(d + g).
            # Image of secondary sits at z = d + 2g -> spacing to secondary is 2g.
            # Spacing from primary (z=0) to secondary's image (z=d+2g) is d + 2g.
            M_2g = M_spiral_pair(radii, 2.0 * g_m)
            M_2dg = M_spiral_pair(radii, 2.0 * (d_m + g_m))
            M_d2g = M_spiral_pair(radii, d_m + 2.0 * g_m)

            # Conducting plate (Al/Cu, t >> delta, image factor = -1)
            L1_al = L0 - M_2dg
            L2_al = L0 - M_2g
            M_al = M0 - M_d2g
            k_al = M_al / np.sqrt(L1_al * L2_al)

            # High-mu ferrite backing (mu_r = 2000, image factor = +alpha_fe)
            L1_fe = L0 + alpha_fe * M_2dg
            L2_fe = L0 + alpha_fe * M_2g
            M_fe = M0 + alpha_fe * M_d2g
            k_fe = M_fe / np.sqrt(L1_fe * L2_fe)

            P_al_W, dR_al_Ohm, P_cu_W, dR_cu_Ohm = compute_plate_eddy_loss(radii, g_m, f0)

            rows.append({
                "d_cm": f"{d_cm:.1f}",
                "gap_mm": f"{g_mm:.1f}",
                "L0_uH": f"{L0 * 1e6:.4f}",
                "M_air_uH": f"{M0 * 1e6:.4f}",
                "k_air": f"{k0:.6f}",
                "L1_al_uH": f"{L1_al * 1e6:.4f}",
                "L2_al_uH": f"{L2_al * 1e6:.4f}",
                "M_al_uH": f"{M_al * 1e6:.4f}",
                "k_al": f"{k_al:.6f}",
                "L1_ferrite_uH": f"{L1_fe * 1e6:.4f}",
                "L2_ferrite_uH": f"{L2_fe * 1e6:.4f}",
                "M_ferrite_uH": f"{M_fe * 1e6:.4f}",
                "k_ferrite": f"{k_fe:.6f}",
                "P_al_mW_per_1Apk": f"{P_al_W * 1e3:.3f}",
                "dR_al_mOhm": f"{dR_al_Ohm * 1e3:.3f}",
                "P_cu_mW_per_1Apk": f"{P_cu_W * 1e3:.3f}",
                "dR_cu_mOhm": f"{dR_cu_Ohm * 1e3:.3f}",
            })

    with open(csv_path, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)

    return rows


def plot_shield_field_comparison():
    """Plot side-by-side |B| field map (d = 3 cm) without plate vs with Al plate at g = 10 mm."""
    geom = params.get_geometry()
    radii = geom["radii"]
    d_m = 0.03      # Secondary at z = 3 cm
    g_m = 0.01      # Plate at z = 4 cm (g = 10 mm behind secondary)
    z_plate = d_m + g_m

    x_cm = np.linspace(-12.0, 12.0, 161)
    z_cm = np.linspace(-3.0, 8.0, 141)
    X_cm, Z_cm = np.meshgrid(x_cm, z_cm)
    RHO_m = np.abs(X_cm) * 1e-2
    Z_m = Z_cm * 1e-2
    sign_x = np.where(X_cm >= 0, 1.0, -1.0)

    # Primary coil at z = 0 carrying I = 1 A
    Br_free, Bz_free = B_components_spiral(radii, RHO_m, Z_m, I=1.0)
    Bx_free = Br_free * sign_x
    Bmag_free_uT = np.hypot(Bx_free, Bz_free) * 1e6

    # With conducting plate at z = z_plate: image of primary sits at z = 2 * z_plate with I = -1 A
    Br_img, Bz_img = B_components_spiral(radii, RHO_m, Z_m - 2.0 * z_plate, I=-1.0)
    Bx_sh = (Br_free + Br_img) * sign_x
    Bz_sh = Bz_free + Bz_img
    # Inside/behind thick metal plate (z > z_plate), field is screened (B ~ 0)
    mask_behind = Z_m > z_plate
    Bx_sh = np.where(mask_behind, np.nan, Bx_sh)
    Bz_sh = np.where(mask_behind, np.nan, Bz_sh)
    Bmag_sh_uT = np.where(mask_behind, 1e-3, np.hypot(Bx_sh, Bz_sh) * 1e6)

    fig, axes = plt.subplots(1, 2, figsize=(12.5, 5.2), sharey=True)
    norm = LogNorm(vmin=1.0, vmax=500.0)

    for ax, Bmag, Bx, Bz, title, has_plate in [
        (axes[0], Bmag_free_uT, Bx_free, Bz_free, "(a) Free Space (No Plate)", False),
        (axes[1], Bmag_sh_uT, Bx_sh, Bz_sh, "(b) With Al Plate at g = 10 mm (z = 4 cm)", True),
    ]:
        im = ax.pcolormesh(X_cm, Z_cm, np.clip(Bmag, 1.0, 500.0), norm=norm, cmap="viridis", shading="auto")
        ax.streamplot(x_cm, z_cm, Bx, Bz, color="white", linewidth=0.7, density=1.0, arrowsize=0.8)

        # Draw primary (z = 0 cm) and secondary (z = 3 cm) cross-sections
        r_out_cm = radii[0] * 100.0
        r_in_cm = radii[-1] * 100.0
        ax.plot([-r_out_cm, -r_in_cm], [0, 0], color="tab:red", linewidth=4, label="Primary (z=0)")
        ax.plot([r_in_cm, r_out_cm], [0, 0], color="tab:red", linewidth=4)
        ax.plot([-r_out_cm, -r_in_cm], [3.0, 3.0], color="tab:orange", linewidth=4, label="Secondary (z=3 cm)")
        ax.plot([r_in_cm, r_out_cm], [3.0, 3.0], color="tab:orange", linewidth=4)

        if has_plate:
            ax.axhspan(4.0, 8.0, color="lightgray", alpha=0.85)
            ax.axhline(4.0, color="black", linewidth=2.5, linestyle="-", label="Al plate (B_n ≈ 0)")

        ax.set_xlabel("Radial position x [cm]")
        ax.set_title(title)
        ax.set_xlim(-12, 12)
        ax.set_ylim(-3, 8)
        ax.legend(loc="lower left", fontsize=10)

    axes[0].set_ylabel("Axial position z [cm]")
    cbar = fig.colorbar(im, ax=axes.ravel().tolist(), pad=0.02)
    cbar.set_label("|B| field magnitude [µT] (for 1 A primary)")

    style.save_fig(fig, "fig_B_shield_compare")
    plt.close(fig)


def main():
    run_shield_sweep()
    plot_shield_field_comparison()
    # Also trigger make_figures so fig_k_vs_gap_shield and fig_loss_vs_gap_shield are built
    from sim import make_figures
    make_figures.apply_poster_rc()
    make_figures.make_shield_figures()
    print("Task C-S2 complete: data/sim_shield.csv and shield figures written.")


if __name__ == "__main__":
    main()
