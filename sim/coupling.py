"""Numerical mutual inductance of the coil pair by the Neumann formula: M(d), k(d).

Neumann formula (CONVENTIONS.md Section 4):
    M = (mu0 / 4 pi) closed-int closed-int (dl1 . dl2) / r
Discretised: each circular turn is split into n_seg straight segments (chords of
the circle). Each segment is represented by its midpoint and its vector dl, and
    M ~ (mu0 / 4 pi) sum_i sum_j (dl_i . dl_j) / |r_i - r_j|
over all segment pairs of coil 1 and coil 2 (all turns included).
k = M / sqrt(L1 L2), with L1, L2 from the filament sum of A-C1 (sim/analytic.py).

Run from the project root:  python -m sim.coupling
"""

import csv
from pathlib import Path

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import ScalarFormatter

from sim import params
from sim.params import MU0
from sim.analytic import coil_mutual, L_filament, coupling
from sim.style import THEORY, SIM, save_fig

ROOT = Path(__file__).resolve().parent.parent
N_SEG = 150                     # straight segments per turn (CONVENTIONS.md: 100 to 200)


def coil_segments(radii, z=0.0, x_offset=0.0, n_seg=N_SEG):
    """Segment midpoints and dl vectors of a flat coil [m].

    Each turn of radius r is approximated by an n_seg-sided polygon in the plane z,
    centred at (x_offset, 0, z), current flowing counter-clockwise (seen from +z).
    Returns (mid, dl), each of shape (n_turns * n_seg, 3).
    """
    phi = np.linspace(0, 2 * np.pi, n_seg + 1)          # polygon vertices (last = first)
    mids, dls = [], []
    for r in np.atleast_1d(radii):
        pts = np.column_stack([x_offset + r * np.cos(phi), r * np.sin(phi), np.full_like(phi, z)])
        dls.append(pts[1:] - pts[:-1])                    # segment vector dl
        mids.append(0.5 * (pts[1:] + pts[:-1]))           # segment midpoint
    return np.vstack(mids), np.vstack(dls)


def neumann_mutual(mid1, dl1, mid2, dl2, chunk=2000):
    """M [H] = (mu0/4pi) sum_i sum_j (dl1_i . dl2_j) / |r1_i - r2_j|.

    Loops over chunks of coil-1 segments so the pair matrix never gets too large.
    """
    total = 0.0
    for s in range(0, len(mid1), chunk):
        m1, d1 = mid1[s:s + chunk], dl1[s:s + chunk]
        r = np.linalg.norm(m1[:, None, :] - mid2[None, :, :], axis=2)   # distances |r_ij|
        dot = d1 @ dl2.T                                                 # dl_i . dl_j
        total += np.sum(dot / r)
    return MU0 / (4 * np.pi) * total


def mutual_coaxial(radii1, radii2, d, n_seg=N_SEG, x_offset=0.0):
    """Numerical M [H] between coil 1 at z=0 and coil 2 at z=d (optionally offset sideways)."""
    m1, d1 = coil_segments(radii1, z=0.0, n_seg=n_seg)
    m2, d2 = coil_segments(radii2, z=d, x_offset=x_offset, n_seg=n_seg)
    return neumann_mutual(m1, d1, m2, d2)


def coil_inductances(g):
    """(L1, L2, source) used for k = M / sqrt(L1 L2).

    Measured L from params.py only when PARAMS_VERSION == "v2-measured"; otherwise the
    filament sum computed from the geometry (A-C1). The design L1, L2 typed into params.py
    are NOT used here, so k can never drift from the geometry (tests/test_params_consistency.py).
    """
    if params.PARAMS_VERSION == "v2-measured" and params.L1 is not None and params.L2 is not None:
        return params.L1, params.L2, "measured (params.py)"
    L_fil = L_filament(g["radii"], g["wire_d"] / 2)
    return L_fil, L_fil, "filament sum"


def main():
    g = params.get_geometry()
    tag = "PLACEHOLDER GEOMETRY" if g["placeholder"] else "design geometry"
    radii = g["radii"]
    print(f"=== A-S1 numerical Neumann coupling ({tag}), {N_SEG} segments/turn ===")

    # Self-inductances: measured if given in params.py, else A-C1 filament sum
    L1, L2, L_src = coil_inductances(g)
    print(f"L1 = {L1*1e6:.3f} uH, L2 = {L2*1e6:.3f} uH ({L_src})")

    # --- Check 1: numerical vs closed form at the A-C1 distances ---
    print("\nCheck 1: Neumann vs closed-form (A-C1)")
    print(f"{'d [cm]':>7} {'M num [uH]':>11} {'M cf [uH]':>11} {'diff %':>8}")
    max_err = 0.0
    for d in params.d_hand:
        Mn, Mc = mutual_coaxial(radii, radii, d), coil_mutual(radii, radii, d)
        err = 100 * (Mn - Mc) / Mc
        max_err = max(max_err, abs(err))
        print(f"{d*100:7.1f} {Mn*1e6:11.5f} {Mc*1e6:11.5f} {err:8.3f}")
    print(f"  max |diff| = {max_err:.3f} %  -> {'PASS' if max_err < 2 else 'FAIL'} (< 2 %)")

    # --- Convergence: double the segments per turn ---
    print("\nConvergence: N_SEG -> 2 N_SEG")
    max_conv = 0.0
    for d in np.array([0.5, 1, 3, 10]) * 1e-2:
        Ma = mutual_coaxial(radii, radii, d, n_seg=N_SEG)
        Mb = mutual_coaxial(radii, radii, d, n_seg=2 * N_SEG)
        ch = 100 * abs(Mb - Ma) / Mb
        max_conv = max(max_conv, ch)
        print(f"  d = {d*100:4.1f} cm: M({N_SEG}) = {Ma*1e6:.5f} uH, M({2*N_SEG}) = {Mb*1e6:.5f} uH, "
              f"change = {ch:.4f} %")
    print(f"  max change = {max_conv:.4f} %  -> {'PASS' if max_conv < 0.5 else 'FAIL'} (< 0.5 %)")

    # --- Check 2: single-turn pair vs dipole ---
    a = radii[0]
    print(f"\nCheck 2: single turn pair (a = {a*1e3:.2f} mm), Neumann vs dipole mu0 pi a^4 / (2 d^3)")
    for ratio in [5, 10, 20, 50]:
        d = ratio * a
        Mn = mutual_coaxial([a], [a], d)
        Md = MU0 * np.pi * a ** 4 / (2 * d ** 3)
        print(f"  d = {ratio:3d} a: M num = {Mn*1e12:10.4f} pH, dipole = {Md*1e12:10.4f} pH, "
              f"diff = {100*(Md-Mn)/Mn:6.2f} %")

    # --- Check 3: log-log slope at large d ---
    print("\nCheck 3: log-log slope of numerical M(d) (full coils)")
    for d1, d2 in [(0.08, 0.10), (0.10, 0.50), (0.20, 0.50), (0.50, 1.00)]:
        s = np.log(mutual_coaxial(radii, radii, d2) / mutual_coaxial(radii, radii, d1)) / np.log(d2 / d1)
        print(f"  {d1*100:4.0f} -> {d2*100:4.0f} cm: slope = {s:.3f}")

    # --- Sweep d = 0.5 .. 15 cm ---
    d_sweep = params.d_sweep
    M_num = np.array([mutual_coaxial(radii, radii, d) for d in d_sweep])
    M_cf = np.array([coil_mutual(radii, radii, d) for d in d_sweep])
    k_num, k_cf = coupling(M_num, L1, L2), coupling(M_cf, L1, L2)
    assert np.all(k_num < 1) and np.all(np.diff(k_num) < 0), "k out of range or not decreasing"

    out = ROOT / "data" / "sim_M_k.csv"
    with open(out, "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["d_cm", "M_H", "k"])
        for d, Mi, ki in zip(d_sweep, M_num, k_num):
            w.writerow([f"{d*100:.2f}", f"{Mi:.6e}", f"{ki:.6f}"])
    print(f"\nWrote {out.relative_to(ROOT)} ({len(d_sweep)} rows)")

    # --- Figures: linear and log-log panels ---
    d_cm = d_sweep * 100
    for name, y_cf, y_num, ylabel, scale in [
            ("fig_M_vs_d", M_cf * 1e6, M_num * 1e6, r"Mutual inductance $M$ ($\mu$H)", 1),
            ("fig_k_vs_d", k_cf, k_num, r"Coupling coefficient $k$", 1)]:
        fig, axes = plt.subplots(1, 2, figsize=(13, 5))
        for ax, loglog in zip(axes, [False, True]):
            ax.plot(d_cm, y_cf, label="Theory (closed form)", **THEORY)
            ax.plot(d_cm, y_num, label="Simulation (Neumann)", **SIM)
            if loglog:
                ax.set_xscale("log")
                ax.set_yscale("log")
                ax.xaxis.set_major_formatter(ScalarFormatter())   # show 1, 10 instead of 10^0, 10^1
            ax.set_xlabel("Coil spacing $d$ (cm)")
            ax.set_ylabel(ylabel)
            ax.legend()
        axes[0].set_title("Linear axes")
        axes[1].set_title("Log-log axes")
        if g["placeholder"]:
            fig.suptitle("PLACEHOLDER GEOMETRY", color="red")
        fig.tight_layout()
        pdf, png = save_fig(fig, name)
        plt.close(fig)
        print(f"Saved {pdf.relative_to(ROOT)} and {png.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
