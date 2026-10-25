"""Task C-T1 and C-C1 analytical calculation runner and plot generator.

Reads resonator parameters dynamically from sim/params.py, analytical M(d)/k(d)
from theory/hand_values.csv, and numerical sweep M(d)/k(d) from data/sim_M_k.csv.

Outputs:
    - data/c_c1_closed_form.csv        (d, M, k, x, RL_opt, eta_max, eta_fixed, PL, regime)
    - data/c_c1_eta_vs_RL.csv          (RL sweep at d = 1, 3, 5, 10 cm)
    - figs/fig_c_t1_regimes.pdf / .png (frequency response & mode splitting across regimes)
    - figs/fig_c_c1_eta_max_PL_vs_d.pdf / .png (closed-form eta_max(d), eta(d), and PL(d))

Run from repo root:
    python -m sim.run_c_c1
"""

from pathlib import Path
import sys
import csv
import numpy as np
import matplotlib.pyplot as plt

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from sim import params, style, make_figures

DATA_DIR = REPO_ROOT / "data"
THEORY_DIR = REPO_ROOT / "theory"

# Fixed load chosen in C-C1 Step 4 (RL,opt at d = 5 cm is 5.999 Ohm -> 6.0 Ohm in params.RL_list)
RL_FIXED = 6.0
VS_PEAK = 5.0   # Standard 5 V peak excitation (Task B-C1)


def get_resonator_params():
    """Fetch f0, w0, L1, L2, C1, C2, R1, R2, Q1, Q2 from sim/params.py."""
    f0 = float(params.f0)
    w0 = 2.0 * np.pi * f0
    L1 = float(params.L1)
    L2 = float(params.L2)
    R1 = float(params.R1)
    R2 = float(params.R2)
    C1 = float(params.C1)
    C2 = float(params.C2)
    Q1 = w0 * L1 / R1
    Q2 = w0 * L2 / R2
    return f0, w0, L1, L2, C1, C2, R1, R2, Q1, Q2


def write_c_c1_tables():
    """Generate data/c_c1_closed_form.csv and data/c_c1_eta_vs_RL.csv."""
    f0, w0, L1, L2, C1, C2, R1, R2, Q1, Q2 = get_resonator_params()
    hand = make_figures.load_hand_M_k()
    if hand is None:
        raise FileNotFoundError("theory/hand_values.csv not found.")
    d_cm_arr, M_uH_arr, k_arr = hand

    Q2L = w0 * L2 / (R2 + RL_FIXED)
    kc = 1.0 / np.sqrt(Q1 * Q2L)
    k_split = np.sqrt(0.5 * (1.0 / (Q1 ** 2) + 1.0 / (Q2L ** 2)))

    DATA_DIR.mkdir(parents=True, exist_ok=True)

    # 1. Master distance table (data/c_c1_closed_form.csv)
    rows_d = []
    for d_cm, M_uH, k in zip(d_cm_arr, M_uH_arr, k_arr):
        M = M_uH * 1e-6
        x = (k ** 2) * Q1 * Q2
        RL_opt = R2 * np.sqrt(1.0 + x)
        eta_max = x / ((1.0 + np.sqrt(1.0 + x)) ** 2)

        r_fix = RL_FIXED / R2
        eta_fix = (x * r_fix) / ((1.0 + r_fix) * (1.0 + r_fix + x))

        Zin = R1 + ((w0 * M) ** 2) / (R2 + RL_FIXED)
        I1_pk = VS_PEAK / Zin
        I2_pk = (w0 * M * I1_pk) / (R2 + RL_FIXED)
        Pin_W = 0.5 * VS_PEAK * I1_pk
        PL_W = 0.5 * (I2_pk ** 2) * RL_FIXED

        fl_kHz = (f0 / np.sqrt(1.0 + k)) * 1e-3
        fh_kHz = (f0 / np.sqrt(1.0 - k)) * 1e-3

        if k > k_split:
            regime = "Over-coupled (split peaks)"
        elif k >= 0.95 * kc:
            regime = "Critically coupled / transition (single peak)"
        else:
            regime = "Under-coupled (single peak)"

        rows_d.append({
            "d_cm": f"{d_cm:g}",
            "M_uH": f"{M_uH:.4f}",
            "k": f"{k:.6f}",
            "x_fom": f"{x:.2f}",
            "RL_opt_ohm": f"{RL_opt:.3f}",
            "eta_max_pct": f"{eta_max * 100.0:.2f}",
            "RL_fixed_ohm": f"{RL_FIXED:.2f}",
            "eta_fixed_pct": f"{eta_fix * 100.0:.2f}",
            "Zin_ohm": f"{Zin:.3f}",
            "Pin_W": f"{Pin_W:.4f}",
            "PL_W": f"{PL_W:.4f}",
            "fl_lossless_kHz": f"{fl_kHz:.2f}",
            "fh_lossless_kHz": f"{fh_kHz:.2f}",
            "kc": f"{kc:.5f}",
            "k_split": f"{k_split:.5f}",
            "regime": regime,
        })

    out_d = DATA_DIR / "c_c1_closed_form.csv"
    with open(out_d, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows_d[0].keys()))
        writer.writeheader()
        writer.writerows(rows_d)

    # 2. Load sweep table at d = 1, 3, 5, 10 cm (data/c_c1_eta_vs_RL.csv)
    target_d = [1.0, 3.0, 5.0, 10.0]
    k_map = {float(d): float(k) for d, k in zip(d_cm_arr, k_arr)}
    rows_rl = []
    for RL in params.RL_list:
        RL_val = float(RL)
        r = RL_val / R2
        row = {"RL_ohm": f"{RL_val:g}", "r_ratio": f"{r:.3f}"}
        for d_val in target_d:
            k = k_map[d_val]
            x = (k ** 2) * Q1 * Q2
            eta_pct = (x * r) / ((1.0 + r) * (1.0 + r + x)) * 100.0
            row[f"eta_d{int(d_val)}cm_pct"] = f"{eta_pct:.2f}"
        rows_rl.append(row)

    out_rl = DATA_DIR / "c_c1_eta_vs_RL.csv"
    with open(out_rl, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows_rl[0].keys()))
        writer.writeheader()
        writer.writerows(rows_rl)

    return d_cm_arr, M_uH_arr, k_arr


def plot_c_t1_regimes(d_cm_arr, k_arr):
    """Plot frequency response |I2(f)| / |I2_max| across coupling regimes (Task C-T1)."""
    f0, w0, L1, L2, C1, C2, R1, R2, Q1, Q2 = get_resonator_params()
    f_kHz = np.linspace(350.0, 750.0, 2500)
    w = 2.0 * np.pi * f_kHz * 1e3

    Z1 = R1 + 1j * (w * L1 - 1.0 / (w * C1))
    Z2 = (R2 + RL_FIXED) + 1j * (w * L2 - 1.0 / (w * C2))

    k_map = {float(d): float(k) for d, k in zip(d_cm_arr, k_arr)}
    fig, ax = plt.subplots(figsize=(7.5, 4.8))

    styles = [
        (1.0, "tab:red", "-", "d = 1 cm (k = 0.513, strongly over-coupled)"),
        (3.0, "tab:orange", "--", "d = 3 cm (k = 0.217, over-coupled)"),
        (5.0, "tab:green", "-.", "d = 5 cm (k = 0.111, moderately over-coupled)"),
        (10.0, "tab:blue", ":", "d = 10 cm (k = 0.030 ≈ kc, critically coupled)"),
    ]

    for d_val, color, ls, label in styles:
        k = k_map[d_val]
        M = k * np.sqrt(L1 * L2)
        I2 = (-1j * w * M * VS_PEAK) / (Z1 * Z2 + (w * M) ** 2)
        I2_norm = np.abs(I2) / np.max(np.abs(I2))
        ax.plot(f_kHz, I2_norm, color=color, linestyle=ls, linewidth=2.2, label=label)

    ax.axvline(f0 * 1e-3, color="black", linestyle=":", linewidth=1.2, label="f₀ = 500 kHz")
    ax.set_xlabel("Operating frequency f [kHz]")
    ax.set_ylabel("Normalized secondary current |I₂(f)| / |I₂|max [-]")
    ax.set_title("Coupled-Mode Frequency Splitting Across Coupling Regimes (RL = 6 Ω)")
    ax.set_xlim(350, 750)
    ax.set_ylim(0, 1.08)
    ax.legend(fontsize=10.5, loc="upper right")

    style.save_fig(fig, "fig_c_t1_regimes")
    plt.close(fig)


def plot_c_c1_curves(d_hand_cm, k_hand):
    """Plot closed-form eta_max(d), eta(d, RL=6 Ohm), and PL(d) (Task C-C1)."""
    f0, w0, L1, L2, C1, C2, R1, R2, Q1, Q2 = get_resonator_params()

    # Load continuous curve from data/sim_M_k.csv if available, plus hand_values markers
    sim_path = DATA_DIR / "sim_M_k.csv"
    if sim_path.exists():
        scols = make_figures.read_csv_columns(sim_path)
        d_cont = make_figures.to_float_array(scols["d_cm"])
        k_cont = make_figures.to_float_array(scols["k"])
    else:
        d_cont = d_hand_cm
        k_cont = k_hand

    x_cont = (k_cont ** 2) * Q1 * Q2
    eta_max_cont = x_cont / ((1.0 + np.sqrt(1.0 + x_cont)) ** 2) * 100.0
    r_fix = RL_FIXED / R2
    eta_fix_cont = (x_cont * r_fix) / ((1.0 + r_fix) * (1.0 + r_fix + x_cont)) * 100.0

    M_cont = k_cont * np.sqrt(L1 * L2)
    Zin_cont = R1 + ((w0 * M_cont) ** 2) / (R2 + RL_FIXED)
    I2_cont = (w0 * M_cont * (VS_PEAK / Zin_cont)) / (R2 + RL_FIXED)
    PL_cont = 0.5 * (I2_cont ** 2) * RL_FIXED

    # Hand values points
    x_h = (k_hand ** 2) * Q1 * Q2
    eta_max_h = x_h / ((1.0 + np.sqrt(1.0 + x_h)) ** 2) * 100.0
    eta_fix_h = (x_h * r_fix) / ((1.0 + r_fix) * (1.0 + r_fix + x_h)) * 100.0
    M_h = k_hand * np.sqrt(L1 * L2)
    Zin_h = R1 + ((w0 * M_h) ** 2) / (R2 + RL_FIXED)
    I2_h = (w0 * M_h * (VS_PEAK / Zin_h)) / (R2 + RL_FIXED)
    PL_h = 0.5 * (I2_h ** 2) * RL_FIXED

    fig, ax1 = plt.subplots(figsize=(7.5, 4.8))
    ax1.plot(d_cont, eta_max_cont, color="tab:blue", linestyle="-", linewidth=2.2,
             label="η_max(d) (with optimal load R_L,opt(d))")
    ax1.plot(d_cont, eta_fix_cont, color="tab:orange", linestyle="--", linewidth=2.2,
             label=f"η(d) (with fixed R_L = {RL_FIXED:g} Ω)")
    ax1.plot(d_hand_cm, eta_max_h, color="tab:blue", marker="o", linestyle="none")
    ax1.plot(d_hand_cm, eta_fix_h, color="tab:orange", marker="s", linestyle="none")
    ax1.set_xlabel("Axial coil spacing d [cm]")
    ax1.set_ylabel("Link efficiency η [%]", color="tab:blue")
    ax1.set_xlim(0.5, 10.5)
    ax1.set_ylim(0, 105)

    ax2 = ax1.twinx()
    ax2.plot(d_cont, PL_cont, color="tab:green", linestyle="-.", linewidth=2.0,
             label=f"Load power P_L(d) at V_s = {VS_PEAK:g} V_pk (R_L = {RL_FIXED:g} Ω)")
    ax2.plot(d_hand_cm, PL_h, color="tab:green", marker="^", linestyle="none")
    ax2.set_ylabel("Delivered load power P_L [W]", color="tab:green")
    ax2.grid(False)

    # Combine legends from both axes
    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2, loc="center left", fontsize=10.5)
    ax1.set_title("Closed-Form Link Efficiency η(d) and Delivered Power P_L(d)")

    style.save_fig(fig, "fig_c_c1_eta_max_PL_vs_d")
    plt.close(fig)


def main():
    make_figures.apply_poster_rc()
    d_cm_arr, M_uH_arr, k_arr = write_c_c1_tables()
    plot_c_t1_regimes(d_cm_arr, k_arr)
    plot_c_c1_curves(d_cm_arr, k_arr)
    print("Tasks C-T1 and C-C1 complete: CSVs written to data/ and figures written to figs/.")


if __name__ == "__main__":
    main()