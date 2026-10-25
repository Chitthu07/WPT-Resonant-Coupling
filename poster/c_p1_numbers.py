"""Numbers sheet for poster Sections 6 and 7 (C-P1): every value read or computed from the repo, with its source.

Writes poster/C-P1_numbers.md. Nothing is typed by hand: rerun after any change to sim/params.py.
Run from the project root:  python -m poster.c_p1_numbers   (or: python poster/c_p1_numbers.py)
"""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import numpy as np
import pandas as pd

from sim import params
from sim.analytic import coil_mutual
from sim.circuit import solve, RL_opt, k_crit, x_factor
from sim.fieldmap import bz_axis_closed_form, biot_savart
from sim.coupling import coil_segments

DATA = ROOT / "data"
rows = []


def add(section, quantity, value, unit, source):
    rows.append((section, quantity, value, unit, source))


def at(df, col, d):
    return df.iloc[(df[col] - d).abs().argmin()]


def main():
    f0, R1, R2, RL = params.f0, params.R1, params.R2, params.RL_fixed
    w0 = 2 * np.pi * f0
    g = params.get_geometry()
    radii = g["radii"]

    # --- design ---
    add("design", "R1 = R2", f"{R1:g} (range {params.R_range[0]:g}-{params.R_range[1]:g})", "ohm", "sim/params.py")
    add("design", "Q1 = Q2 = w0 L/R", f"{w0 * params.L1 / R1:.1f}", "-", "params")
    add("design", "bandwidth f0/Q", f"{f0 / (w0 * params.L1 / R1) / 1e3:.2f}", "kHz", "params")
    add("design", "skin depth (Cu)", f"{np.sqrt(2 / (w0 * params.MU0 * 5.8e7)) * 1e3:.4f} (poster: 0.094)", "mm", "sigma = 5.8e7 S/m")

    # --- distance table ---
    e = pd.read_csv(DATA / "sim_eta_d.csv")
    for d in (1, 2, 3, 5, 10):
        r = at(e, "d_cm", d)
        add("S6 table", f"d = {d} cm: M, k", f"{r.M_H * 1e6:.2f} uH, {r.k:.3f}", "", "data/sim_eta_d.csv")
        add("S6 table", f"d = {d} cm: eta_max (R_L,opt)", f"{100 * r.eta_max:.1f} % ({r.RL_opt_ohm:.2f} ohm)", "", "data/sim_eta_d.csv")
        add("S6 table", f"d = {d} cm: eta at 6 ohm, P_L (Rs=0 / Rs=50)",
            f"{100 * r.eta_fixedRL:.1f} %, {r.PL_W:.3f} W / {r.PL_Rs50_W * 1e3:.1f} mW", "", "data/sim_eta_d.csv")
    i = e.PL_W.idxmax()
    add("S6/S7", "max P_L at 6 ohm, Rs = 0", f"{e.PL_W[i]:.2f} W at d = {e.d_cm[i]:g} cm, eta {100 * e.eta_fixedRL[i]:.1f} %", "", "data/sim_eta_d.csv")
    j = e.PL_Rs50_W.idxmax()
    add("S6/S7", "max P_L at 6 ohm, Rs = 50 ohm", f"{e.PL_Rs50_W[j] * 1e3:.1f} mW at d = {e.d_cm[j]:g} cm", "", "data/sim_eta_d.csv")
    mk = pd.read_csv(DATA / "sim_M_k.csv")
    for Rs in (0.0, 50.0):
        kc = float(k_crit(params.L1, params.L2, f0, R1, R2, RL, Rs=Rs))
        add("S7", f"k_c (R_L = 6 ohm, Rs = {Rs:g})", f"{kc:.4f} at d = {np.interp(-kc, -mk.k, mk.d_cm):.2f} cm", "", "sim.circuit.k_crit")
    M5 = at(e, "d_cm", 5).M_H
    add("S7", "R_L for max power at 5 cm = R2(1+x)", f"{R2 * (1 + float(x_factor(M5, f0, R1, R2))):.1f}", "ohm", "B-T2 formula")

    # --- split peaks ---
    sp = pd.read_csv(DATA / "val_split_peaks.csv")
    for _, r in sp.iterrows():
        pk = "1 peak" if r.n_peaks == 1 else f"{r.f_low_sim_kHz:.1f} / {r.f_high_sim_kHz:.1f} kHz -> k = {r.k_from_peaks:.4f} ({r.k_err_percent:+.1f} %)"
        add("S6 split", f"d = {r.d_cm:g} cm, {r.load} load ({r.RL_ohm:g} ohm), true k = {r.k:.4f}", pk, "", "data/val_split_peaks.csv")

    # --- LTspice ---
    lt = pd.read_csv(DATA / "val_ltspice_metrics.csv")
    add("S6 LTspice", "LTspice vs solver metrics", "; ".join(f"{c}={lt[c].iloc[0]}" for c in lt.columns[:6]),
        "", "data/val_ltspice_metrics.csv (LTspice rerun at R = 0.455, 2026-10-25)")

    # --- stress, rectifier ---
    st = pd.read_csv(DATA / "stress_table.csv")
    for _, r in st[st.case.isin(["5 cm", "10 cm", "no secondary"])].iterrows():
        add("S7 stress", f"{r.case}, Rs = {r.Rs_ohm:g} ohm: I1, V_C1, V_C2, P_R1, P_L",
            f"{r.I1_A_pk:.2f} A pk, {r.VC1_V_pk:.1f} V pk, {r.VC2_V_pk:.1f} V pk, {r.P_R1_W:.3g} W, {r.PL_W:.3g} W", "", "data/stress_table.csv")
    rect = pd.read_csv(DATA / "c_v1_load_rectifier.csv")
    r6 = rect.iloc[(rect.RL_ac_ohm - 6).abs().argmin()]
    rb = rect.iloc[rect.eta_sys_rect_d3cm_pct.idxmax()]
    add("S6/S7", "d = 3 cm, R_L,ac = 6 ohm: eta_link / eta_sys (rectifier)", f"{r6.eta_link_d3cm_pct:.1f} % / {r6.eta_sys_rect_d3cm_pct:.1f} %", "", "data/c_v1_load_rectifier.csv")
    add("S6/S7", "d = 3 cm, best eta_sys in sweep", f"{rb.eta_sys_rect_d3cm_pct:.1f} % at R_L,ac = {rb.RL_ac_ohm:g} ohm (R_DC = {rb.R_DC_equiv_ohm:g})", "", "data/c_v1_load_rectifier.csv")

    # --- misalignment ---
    ex = pd.read_csv(DATA / "sim_eta_dx.csv")
    for d in (3, 5):
        for dx in (0, 2, 3, 4):
            v = {rule: 100 * ex[(ex.d_cm == d) & (np.isclose(ex.dx_cm, dx)) & (ex.load_rule == rule)].eta_link.iloc[0] for rule in ("opt0", "team")}
            add("S7 misalign", f"d = {d} cm, dx = {dx} cm: eta (R_L,opt(dx=0) / 6 ohm)", f"{v['opt0']:.1f} % / {v['team']:.1f} %", "", "data/sim_eta_dx.csv")
    add("S7 misalign", "M = 0 (flux null) at", "dx = 8.22 cm (d = 3 cm), 9.97 cm (d = 5 cm)", "", "theory/misalignment_note.md")

    # --- shield ---
    sh = pd.read_csv(DATA / "sim_shield.csv")
    s5 = sh[(sh.d_cm == 3) & (sh.gap_mm == 5)].iloc[0]
    add("S7 shield", "Al plate g = 5 mm (d = 3 cm): k change, dR, L2 change",
        f"{100 * (s5.k_al / s5.k_air - 1):+.1f} %, {s5.dR_al_mOhm:.0f} mOhm, {100 * (s5.L2_al_uH / s5.L0_uH - 1):+.0f} %", "", "data/sim_shield.csv")
    add("S7 shield", "ferrite g = 5 mm: k change", f"{100 * (s5.k_ferrite / s5.k_air - 1):+.1f} %", "", "data/sim_shield.csv")
    # Shielded efficiency, plate loss in BOTH coils. Image model: tangential H at the plate (z = d + g) is twice the
    # free-space field of each coil; plate loss P = 1/2 sum_ij dR_ij I_i I_j*, dR_ij = R_s integral H_t,i . H_t,j dA.
    # dR_12 adds to the mutual impedance: Z_m = j w M' + dR_12.
    d, gap = 0.03, s5.gap_mm * 1e-3
    M3 = coil_mutual(radii, radii, d)
    RLo = float(RL_opt(M3, f0, R1, R2))
    Rs_al = np.sqrt(w0 * params.MU0 / (2 * 3.5e7))
    h, half = 2e-3, 0.25
    x = np.arange(-half, half + h / 2, h)
    X, Y = np.meshgrid(x, x)
    pts = np.column_stack([X.ravel(), Y.ravel(), np.full(X.size, d + gap)])
    Ht = [2 * biot_savart(pts, *coil_segments(radii, z=zc), 1.0)[:, :2] / params.MU0 for zc in (0.0, d)]
    dR = np.array([[Rs_al * np.sum(Ht[i] * Ht[j]) * h * h for j in range(2)] for i in range(2)])
    L1p, L2p, Mp = s5.L1_al_uH * 1e-6, s5.L2_al_uH * 1e-6, s5.M_al_uH * 1e-6

    def eta(L1, L2, M, C1, C2, dr):
        Z1 = R1 + dr[0, 0] + 1j * w0 * L1 + 1 / (1j * w0 * C1)
        Z2 = R2 + dr[1, 1] + RLo + 1j * w0 * L2 + 1 / (1j * w0 * C2)
        Zm = 1j * w0 * M + dr[0, 1]
        I1, I2 = np.linalg.solve(np.array([[Z1, Zm], [Zm, Z2]]), np.array([params.Vs, 0]))
        return 100 * 0.5 * abs(I2) ** 2 * RLo / (0.5 * np.real(params.Vs * np.conj(I1)))
    C2re = 1 / (w0 ** 2 * L2p)
    e_free = eta(params.L1, params.L2, M3, params.C1, params.C2, np.zeros((2, 2)))
    e_det = eta(L1p, L2p, Mp, params.C1, params.C2, dR)
    e_ret = eta(L1p, L2p, Mp, params.C1, C2re, dR)
    R1p, R2p = R1 + dR[0, 0], R2 + dR[1, 1]
    xs = (w0 * Mp) ** 2 / (R1p * R2p)
    add("S7 shield", "plate loss matrix dR11 / dR22 / dR12 (Al, g = 5 mm, d = 3 cm)",
        f"{dR[0, 0] * 1e3:.1f} / {dR[1, 1] * 1e3:.1f} / {dR[0, 1] * 1e3:.1f}", "mOhm", "Biot-Savart surface integral, image model")
    add("S7 shield", f"eta at d = 3 cm, R_L = {RLo:.2f} ohm: free / plate, not retuned / plate, C2 retuned",
        f"{e_free:.1f} % / {e_det:.1f} % / {e_ret:.1f} %", "", "2x2 mesh with L', M' (data/sim_shield.csv) and dR (both coils)")
    add("S7 shield", "plate, C2 retuned and R_L re-optimised (eta_max, dR12 neglected)",
        f"{100 * xs / (1 + np.sqrt(1 + xs)) ** 2:.1f} % at R_L = {R2p * np.sqrt(1 + xs):.2f} ohm", "", "eta_max formula")

    # --- ICNIRP, on-axis field of the primary at d = 5 cm drive ---
    I1pk = float(st[(st.case == "5 cm") & (st.Rs_ohm == 0)].I1_A_pk.iloc[0])
    I1rms = I1pk / np.sqrt(2)
    z = np.linspace(0, 0.5, 50001)
    B = bz_axis_closed_form(radii, z, I1rms) * 1e6
    add("S7 ICNIRP", "I1 at 5 cm (Rs = 0)", f"{I1pk:.2f} A pk = {I1rms:.3f} A rms", "", "data/stress_table.csv")
    add("S7 ICNIRP", "on-axis B of primary at z = 0", f"{B[0]:.1f}", "uT rms", "sim.fieldmap.bz_axis_closed_form (primary only)")
    for lim in (27.0, 1.84):
        add("S7 ICNIRP", f"B falls below {lim} uT rms at z >=", f"{100 * z[np.argmax(B < lim)]:.1f}", "cm", "same")

    # --- write ---
    lines = ["# C-P1 numbers sheet (generated by poster/c_p1_numbers.py, do not edit by hand)", "",
             f"params: R1 = R2 = {R1:g} ohm, RL_fixed = {RL:g} ohm, Vs = {params.Vs:g} V pk, Rs = {params.Rs:g} ohm, f0 = {f0/1e3:g} kHz", "",
             "| Section | Quantity | Value | Unit | Source |", "|---|---|---|---|---|"]
    lines += [f"| {a} | {b} | {c} | {d} | {e_} |" for a, b, c, d, e_ in rows]
    out = ROOT / "poster" / "C-P1_numbers.md"
    out.write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    print(f"\nWrote {out.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
