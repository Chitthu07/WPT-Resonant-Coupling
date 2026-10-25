"""B-C1: component stress at f0 for every distance, including the worst case (no secondary).

Run from the repo root:  python -m sim.stress
Writes data/stress_table.csv (all values) and data/stress_table.md (table used in B-C1).

At f0, |VC| = |I| / (w0 C) = w0 L |I|. I1 increases with spacing because the reflected resistance
w0^2 M^2 / (R2 + RL) falls; with no secondary I1 = Vs / (R1 + Rs), which is the worst case.
"""
import numpy as np
import pandas as pd

from sim import params
from sim.circuit import solve
from sim.link import ROOT, M_of_d, fixed_load

D_CM = [1, 2, 3, 5, 8, 10, 15]
DOC_CASES = ["1 cm", "3 cm", "5 cm", "10 cm", "15 cm", "no secondary"]   # rows of the B-C1 table


def stress_rows(Rs):
    f0, L1, L2, C1, C2, R1, R2 = params.f0, params.L1, params.L2, params.C1, params.C2, params.R1, params.R2
    w0, Vs, RL = 2 * np.pi * f0, params.Vs, fixed_load()
    rows = []
    cases = [(f"{d:g} cm", M_of_d(d)) for d in D_CM] + [("no secondary", 0.0)]
    for name, M in cases:
        r = solve(f0, M, L1, L2, C1, C2, R1, R2, RL, Vs, Rs=Rs)
        I1, I2 = abs(r.I1), abs(r.I2)
        rows.append(dict(case=name, Rs_ohm=Rs, RL_ohm=RL, M_uH=M * 1e6,
                         I1_A_pk=I1, I2_A_pk=I2, I1_A_rms=I1 / np.sqrt(2), I2_A_rms=I2 / np.sqrt(2),
                         VC1_V_pk=I1 / (w0 * C1), VC2_V_pk=I2 / (w0 * C2),
                         P_R1_W=0.5 * I1**2 * R1, PL_W=r.PL))
    return rows


def markdown_table(df):
    """Markdown table for B-C1: currents in A peak (2 decimals), voltages in V peak (1 decimal)."""
    ideal, gen = df[df.Rs_ohm == params.Rs], df[df.Rs_ohm == params.Rs_gen]
    lines = [f"| Case | I1, Rs = {params.Rs:g} Ω (A pk) | VC1 (V pk) | VC2 (V pk) "
             f"| I1, Rs = {params.Rs_gen:g} Ω (A pk) | VC1 (V pk) |",
             "|---|---:|---:|---:|---:|---:|"]
    for c in DOC_CASES:
        a, b = ideal[ideal.case == c].iloc[0], gen[gen.case == c].iloc[0]
        lines.append(f"| {c} | {a.I1_A_pk:.2f} | {a.VC1_V_pk:.1f} | {a.VC2_V_pk:.1f} "
                     f"| {b.I1_A_pk:.2f} | {b.VC1_V_pk:.1f} |")
    return "\n".join(lines)


def main():
    rows = stress_rows(params.Rs) + stress_rows(params.Rs_gen)
    df = pd.DataFrame(rows)
    df.to_csv(ROOT / "data" / "stress_table.csv", index=False)
    md = markdown_table(df)
    (ROOT / "data" / "stress_table.md").write_text(md + "\n", encoding="utf-8")
    pd.set_option("display.width", 160)
    print(f"R1 = R2 = {params.R1:g} ohm (C-T2 nominal), Vs = {params.Vs:g} V peak, RL = {fixed_load():.2f} ohm")
    print(df.round(3).to_string(index=False))
    for Rs in (params.Rs, params.Rs_gen):
        sub = df[df.Rs_ohm == Rs]
        print(f"Rs = {Rs:g} ohm: worst-case VC1 = {sub.VC1_V_pk.max():.1f} V pk, VC2 = {sub.VC2_V_pk.max():.1f} V pk, "
              f"max capacitor current = {max(sub.I1_A_rms.max(), sub.I2_A_rms.max()):.2f} A rms")
    print("\n" + md)
    print("\nWrote data/stress_table.csv and data/stress_table.md")


if __name__ == "__main__":
    main()
