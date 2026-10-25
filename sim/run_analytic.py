"""Runner for task A-C1: closed-form L, M(d), k(d) -> theory/hand_values.csv + note.

Uses sim/analytic.py (elliptic-integral loop formula, filament sum,
Mohan and modified-Wheeler spiral formulas). All numbers come from sim/params.py.
Run from the project root:  python -m sim.run_analytic
"""

import csv
from pathlib import Path

import numpy as np

from sim import params
from sim.analytic import (loop_mutual, loop_mutual_dipole, coil_mutual, L_filament,
                          L_mohan, L_wheeler, spiral_d_in, coupling, loglog_slope)

ROOT = Path(__file__).resolve().parent.parent
D_TABLE = params.d_hand                            # A-C1 distances [m]


def main():
    g = params.get_geometry()
    tag = "PLACEHOLDER GEOMETRY" if g["placeholder"] else "design geometry"
    radii, n, wd = g["radii"], g["N"], g["wire_d"]
    r_w = wd / 2
    d_in = params.d_in if (params.d_in is not None and not g["placeholder"]) else spiral_d_in(radii, wd)

    print(f"=== A-C1 closed-form results ({tag}) ===")
    print(f"N = {n}, d_out = {g['d_out']*1e3:.2f} mm, d_in = {d_in*1e3:.2f} mm, "
          f"wire_d = {wd*1e3:.2f} mm, pitch = {g['pitch']*1e3:.2f} mm")

    # --- Self-inductance, three ways (both coils identical) ---
    L_fil = L_filament(radii, r_w)
    L_moh = L_mohan(n, g["d_out"], d_in)
    L_whe = L_wheeler(n, g["d_out"], d_in)                    # octagonal coefficients
    L_whe_sq = L_wheeler(n, g["d_out"], d_in, K1=2.34, K2=2.75)  # square, for reference only
    pct = lambda x, ref: 100 * (x - ref) / ref
    print(f"\nL (filament sum)   = {L_fil*1e6:.3f} uH")
    print(f"L (Mohan)          = {L_moh*1e6:.3f} uH   ({pct(L_moh, L_fil):+.2f} % vs filament)")
    print(f"L (Wheeler, oct.)  = {L_whe*1e6:.3f} uH   ({pct(L_whe, L_fil):+.2f} % vs filament)")
    print(f"L (Wheeler, sq.)   = {L_whe_sq*1e6:.3f} uH   ({pct(L_whe_sq, L_fil):+.2f} % vs filament)  [square coil, not applicable]")
    print(f"Mohan vs Wheeler   : {pct(L_whe, L_moh):+.2f} %")
    L1 = L2 = L_fil                            # filament sum used for k (most physical of the three)

    # --- M(d) and k(d) ---
    M = np.array([coil_mutual(radii, radii, d) for d in D_TABLE])
    k = coupling(M, L1, L2)
    print(f"\n{'d [cm]':>7} {'M [uH]':>10} {'k':>9}")
    for d, Mi, ki in zip(D_TABLE, M, k):
        print(f"{d*100:7.1f} {Mi*1e6:10.4f} {ki:9.5f}")

    # --- Validation ---
    print("\n--- Validation ---")
    ok_bound = np.all(M < np.sqrt(L1 * L2))
    ok_mono = np.all(np.diff(k) < 0)
    print(f"M < sqrt(L1 L2) at all d: {ok_bound}  (max k = {k.max():.4f})")
    print(f"k strictly decreasing with d: {ok_mono}")

    a = radii[0]                               # single outer turn as the test loop
    print(f"\nSingle-turn pair (a = b = {a*1e3:.2f} mm) vs dipole formula:")
    print(f"{'d/a':>6} {'M exact [nH]':>14} {'M dipole [nH]':>14} {'diff %':>8}")
    for ratio in [2, 5, 10, 20, 50]:
        d = ratio * a
        Me, Md = loop_mutual(a, a, d), loop_mutual_dipole(a, a, d)
        print(f"{ratio:6d} {Me*1e9:14.5f} {Md*1e9:14.5f} {pct(Md, Me):8.2f}")

    fM = lambda d: coil_mutual(radii, radii, d)
    print("\nLog-log slope of M(d) for the full coils:")
    for d1, d2 in [(0.08, 0.10), (0.10, 0.50), (0.10, 0.20), (0.20, 0.50), (0.50, 1.00)]:
        print(f"  {d1*100:5.0f} -> {d2*100:5.0f} cm : slope = {loglog_slope(fM, d1, d2):.3f}")

    # --- Write CSV ---
    rows = [("L1", L_fil, "H", "filament sum"), ("L1", L_moh, "H", "Mohan current sheet"),
            ("L1", L_whe, "H", "modified Wheeler (octagonal approx.)"),
            ("L2", L_fil, "H", "filament sum"), ("L2", L_moh, "H", "Mohan current sheet"),
            ("L2", L_whe, "H", "modified Wheeler (octagonal approx.)")]
    for d, Mi, ki in zip(D_TABLE, M, k):
        rows.append((f"M_d{d*100:g}cm", Mi, "H", "coaxial elliptic, turn-pair sum"))
        rows.append((f"k_d{d*100:g}cm", ki, "-", "M/sqrt(L1 L2), L from filament sum"))
    out = ROOT / "theory" / "hand_values.csv"
    with open(out, "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["quantity", "value", "unit", "method"])
        for q, v, u, m in rows:
            w.writerow([q, f"{v:.6e}", u, m + (f" [{tag}]" if g["placeholder"] else "")])
    print(f"\nWrote {out.relative_to(ROOT)}")
    return dict(L_fil=L_fil, L_moh=L_moh, L_whe=L_whe, d_in=d_in, tag=tag, M=M, k=k)


if __name__ == "__main__":
    main()
