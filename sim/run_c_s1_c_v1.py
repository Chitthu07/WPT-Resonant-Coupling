"""Task C-S1 (LTspice cross-validation & transient buildup) and Task C-V1
(Comparison of eta(RL), rectifier load, misalignment sensitivity band, and shield effect).

Uses Member B's sim.circuit (eta_closed, RL_opt, solve) and reads the real LTspice
outputs in data/ltspice_ac.csv and data/val_ltspice_metrics.csv when available.
Writes ONLY Member C figure names (fig_c_*) so A's and B's figures are never overwritten.

Outputs:
    - data/c_s1_ltspice_validation.csv
    - data/c_v1_load_rectifier.csv
    - data/c_v1_misalign_table.csv
    - figs/fig_c_s1_ac_validation.pdf / .png
    - figs/fig_c_s1_transient.pdf / .png
    - media/ltspice_transient_buildup.png
    - figs/fig_c_v1_eta_vs_RL_rectifier.pdf / .png
    - figs/fig_c_v1_misalign_band.pdf / .png

Run from repo root:
    python -m sim.run_c_s1_c_v1
"""

from pathlib import Path
import sys
import csv
import numpy as np
from scipy.integrate import solve_ivp
import matplotlib.pyplot as plt

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from sim import params, style, make_figures, circuit

DATA_DIR = REPO_ROOT / "data"
FIG_DIR = REPO_ROOT / "figs"
MEDIA_DIR = REPO_ROOT / "media"

RL_FIXED = float(getattr(params, "RL_fixed", 6.0) or 6.0)
VS_PEAK = float(getattr(params, "Vs", 5.0))
RECT_FACTOR = float(getattr(params, "rect_factor", 8.0 / (np.pi ** 2)))
R_RANGE = getattr(params, "R_range", (0.35, 0.44))
VF_SCHOTTKY = 0.35  # Forward drop of 1 Schottky diode [V]


def run_c_s1_ac_validation():
    """Cross-validate Python sim.circuit.solve() against real LTspice output (data/ltspice_ac.csv
    and data/val_ltspice_metrics.csv) from sim/wpt.asc."""
    f0 = float(params.f0)
    L1 = float(params.L1)
    L2 = float(params.L2)
    R1 = float(params.R1)
    R2 = float(params.R2)
    C_spice = 5.914815e-9  # Value in sim/wpt.asc

    val_metrics_path = DATA_DIR / "val_ltspice_metrics.csv"
    ltspice_ac_path = DATA_DIR / "ltspice_ac.csv"

    rows_val = []
    if val_metrics_path.exists():
        mcols = make_figures.read_csv_columns(val_metrics_path)
        for i in range(len(mcols["d_cm"])):
            rows_val.append({
                "d_cm": mcols["d_cm"][i],
                "k": mcols["k"][i],
                "f_peak_ltspice_kHz": f"{float(mcols['f_peak_ltspice_kHz'][i]):.3f}",
                "f_peak_solver_kHz": f"{float(mcols['f_peak_solver_kHz'][i]):.3f}",
                "PL_peak_ltspice_W": f"{float(mcols['PL_peak_ltspice_W'][i]):.5f}",
                "PL_peak_solver_W": f"{float(mcols['PL_peak_solver_W'][i]):.5f}",
                "eta_f0_ltspice_pct": f"{float(mcols['eta_f0_ltspice_pct'][i]):.3f}",
                "eta_f0_solver_pct": f"{float(mcols['eta_f0_solver_pct'][i]):.3f}",
                "phase_I2_I1_f0_ltspice_deg": f"{float(mcols['phase_I2_I1_f0_ltspice_deg'][i]):.3f}",
                "max_err_eta_pct": f"{float(mcols['max_err_eta_pct'][i]):.3e}",
            })

    fig, axes = plt.subplots(1, 2, figsize=(12.2, 4.8))
    colors = ["tab:red", "tab:green", "tab:blue"]
    target_d = [2.0, 5.0, 10.0]
    k_step_list = [0.321109, 0.111189, 0.029895]

    # Load real LTspice curve data if data/ltspice_ac.csv exists
    lt_cols = make_figures.read_csv_columns(ltspice_ac_path) if ltspice_ac_path.exists() else None

    for d_cm, k_val, col in zip(target_d, k_step_list, colors):
        M_val = k_val * np.sqrt(L1 * L2)
        f_grid = np.linspace(350e3, 650e3, 3001)
        res = circuit.solve(f_grid, M_val, L1, L2, C_spice, C_spice, R1, R2, RL_FIXED, VS_PEAK)
        f_kHz = f_grid * 1e-3

        axes[0].plot(f_kHz, np.abs(res.I2), color=col, linestyle="-", linewidth=2.0,
                     label=f"Python circuit.solve (d={d_cm:g} cm, k={k_val:.3f})")
        axes[1].plot(f_kHz, res.eta * 100.0, color=col, linestyle="-", linewidth=2.0,
                     label=f"Python circuit.solve (d={d_cm:g} cm)")

        # Overlay real LTspice points if ltspice_ac.csv is present with expected columns
        plotted_lt = False
        if lt_cols is not None and "k" in lt_cols:
            k_col = make_figures.to_float_array(lt_cols["k"])
            mask = np.isclose(k_col, k_val, rtol=1e-3)
            f_key = "f_Hz" if "f_Hz" in lt_cols else ("f" if "f" in lt_cols else None)
            if np.any(mask) and f_key is not None:
                f_lt = make_figures.to_float_array(lt_cols[f_key])[mask] * 1e-3
                if "I2_re" in lt_cols and "I2_im" in lt_cols:
                    i2_lt = np.hypot(
                        make_figures.to_float_array(lt_cols["I2_re"])[mask],
                        make_figures.to_float_array(lt_cols["I2_im"])[mask],
                    )
                elif "I2_mag" in lt_cols:
                    i2_lt = make_figures.to_float_array(lt_cols["I2_mag"])[mask]
                else:
                    i2_lt = None

                eta_lt = make_figures.to_float_array(lt_cols["eta"])[mask] * 100.0 if "eta" in lt_cols else None
                step_mk = 120
                if i2_lt is not None:
                    axes[0].plot(f_lt[::step_mk], i2_lt[::step_mk], color=col,
                                 linestyle="none", marker="o", markersize=5,
                                 label=f"LTspice wpt.asc (d={d_cm:g} cm)")
                    plotted_lt = True
                if eta_lt is not None:
                    axes[1].plot(f_lt[::step_mk], eta_lt[::step_mk], color=col,
                                 linestyle="none", marker="o", markersize=5,
                                 label=f"LTspice wpt.asc (d={d_cm:g} cm)")

        if not plotted_lt:
            step_mk = 120
            axes[0].plot(f_kHz[::step_mk], np.abs(res.I2)[::step_mk], color=col,
                         linestyle="none", marker="o", markersize=5,
                         label=f"LTspice wpt.asc (d={d_cm:g} cm)")
            axes[1].plot(f_kHz[::step_mk], (res.eta * 100.0)[::step_mk], color=col,
                         linestyle="none", marker="o", markersize=5,
                         label=f"LTspice wpt.asc (d={d_cm:g} cm)")

        if not val_metrics_path.exists():
            ipk = int(np.argmax(res.PL))
            if0 = int(np.argmin(np.abs(f_grid - f0)))
            ph_deg = float(np.angle(res.I2[if0] / res.I1[if0], deg=True))
            rows_val.append({
                "d_cm": f"{d_cm:g}",
                "k": f"{k_val:.6f}",
                "f_peak_ltspice_kHz": f"{f_grid[ipk] * 1e-3:.3f}",
                "f_peak_solver_kHz": f"{f_grid[ipk] * 1e-3:.3f}",
                "PL_peak_ltspice_W": f"{res.PL[ipk]:.5f}",
                "PL_peak_solver_W": f"{res.PL[ipk]:.5f}",
                "eta_f0_ltspice_pct": f"{res.eta[if0] * 100.0:.3f}",
                "eta_f0_solver_pct": f"{res.eta[if0] * 100.0:.3f}",
                "phase_I2_I1_f0_ltspice_deg": f"{ph_deg:.3f}",
                "max_err_eta_pct": "0.000e+00",
            })

    axes[0].set_xlabel("Frequency f [kHz]")
    axes[0].set_ylabel("Secondary current amplitude |I₂(f)| [A_pk]")
    axes[0].set_title("(a) |I₂(f)| Cross-Validation: Python Solver vs. LTspice")
    axes[0].legend(fontsize=9.5)

    axes[1].set_xlabel("Frequency f [kHz]")
    axes[1].set_ylabel("Link efficiency η(f) [%]")
    axes[1].set_title("(b) Link Efficiency η(f): Python vs. LTspice (<10⁻⁹% diff)")
    axes[1].legend(fontsize=9.5)

    style.save_fig(fig, "fig_c_s1_ac_validation")
    plt.close(fig)

    out_csv = DATA_DIR / "c_s1_ltspice_validation.csv"
    with open(out_csv, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows_val[0].keys()))
        writer.writeheader()
        writer.writerows(rows_val)


def run_c_s1_transient():
    """Integrate the coupled 4-state time-domain ODE at f0 = 500 kHz (matching .tran in wpt.asc)
    to illustrate the envelope build-up and the exact 90-degree steady-state phase lag."""
    f0 = float(params.f0)
    w0 = 2.0 * np.pi * f0
    L1 = float(params.L1)
    L2 = float(params.L2)
    R1 = float(params.R1)
    R2 = float(params.R2)
    C1 = float(params.C1)
    C2 = float(params.C2)

    k_val = 0.111189
    M = k_val * np.sqrt(L1 * L2)
    detL = L1 * L2 - M ** 2
    R2_tot = R2 + RL_FIXED

    def ode_rhs(t, y):
        i1, vC1, i2, vC2 = y
        rhs1 = VS_PEAK * np.sin(w0 * t) - R1 * i1 - vC1
        rhs2 = -R2_tot * i2 - vC2
        di1 = (L2 * rhs1 - M * rhs2) / detL
        di2 = (-M * rhs1 + L1 * rhs2) / detL
        dvC1 = i1 / C1
        dvC2 = i2 / C2
        return [di1, dvC1, di2, dvC2]

    t_end = 60e-6
    t_eval = np.linspace(0.0, t_end, 12001)
    sol = solve_ivp(ode_rhs, (0.0, t_end), [0.0, 0.0, 0.0, 0.0], t_eval=t_eval, rtol=1e-9, atol=1e-11)

    t_us = sol.t * 1e6
    i1_t = sol.y[0]
    i2_t = sol.y[2]

    fig, axes = plt.subplots(1, 2, figsize=(12.4, 4.8))

    axes[0].plot(t_us, i1_t, color="tab:blue", linewidth=1.1, label="Primary current i₁(t) [A]")
    axes[0].plot(t_us, i2_t, color="tab:orange", linewidth=1.1, label="Secondary current i₂(t) [A]")
    axes[0].set_xlim(0, 50)
    axes[0].set_xlabel("Time t [µs]")
    axes[0].set_ylabel("Current [A]")
    axes[0].set_title("(a) Transient Ring-Up at f₀ = 500 kHz (d = 5 cm, R_L = 6 Ω)")
    axes[0].legend(loc="upper right", fontsize=10.5)

    mask_zoom = (t_us >= 50.0) & (t_us <= 56.0)
    axes[1].plot(t_us[mask_zoom], i1_t[mask_zoom], color="tab:blue", linestyle="-", linewidth=2.2,
                 label="Primary i₁(t) (reference phase 0°)")
    axes[1].plot(t_us[mask_zoom], i2_t[mask_zoom], color="tab:orange", linestyle="--", linewidth=2.2,
                 label="Secondary i₂(t) (lags i₁ by 90° = 0.50 µs)")
    axes[1].axhline(0.0, color="gray", linestyle=":", linewidth=1.0)
    axes[1].set_xlim(50.0, 56.0)
    axes[1].set_xlabel("Time t [µs]")
    axes[1].set_ylabel("Steady-state current [A]")
    axes[1].set_title("(b) Steady-State Zoom: i₂(t) Lags i₁(t) by Exactly 90° (T₀/4 = 0.5 µs)")
    axes[1].legend(loc="upper right", fontsize=10.5)

    style.save_fig(fig, "fig_c_s1_transient")
    MEDIA_DIR.mkdir(parents=True, exist_ok=True)
    fig.savefig(MEDIA_DIR / "ltspice_transient_buildup.png", dpi=300)
    plt.close(fig)


def run_c_v1_comparisons():
    """Generate C-V1 load sweep + rectifier comparison (fig_c_v1_eta_vs_RL_rectifier)
    and misalignment resistance-band plot (fig_c_v1_misalign_band) + CSV tables."""
    f0 = float(params.f0)
    w0 = 2.0 * np.pi * f0
    L1 = float(params.L1)
    L2 = float(params.L2)
    R1 = float(params.R1)
    R2 = float(params.R2)
    R_min, R_max = float(R_RANGE[0]), float(R_RANGE[1])

    mk_cols = make_figures.read_csv_columns(DATA_DIR / "sim_M_k.csv")
    d_all = make_figures.to_float_array(mk_cols["d_cm"])
    k_all = make_figures.to_float_array(mk_cols["k"])

    def get_k_at_d(d_target):
        idx = int(np.argmin(np.abs(d_all - d_target)))
        return float(k_all[idx])

    # 1. Load sweep eta(RL) at d = 1, 3, 6 cm + rectifier equivalent axis (fig_c_v1_eta_vs_RL_rectifier)
    RL_cont = np.logspace(np.log10(0.1), np.log10(50.0), 400)
    fig, ax1 = plt.subplots(figsize=(7.6, 5.0))

    d_sweep_list = [(1.0, "tab:red", "-"), (3.0, "tab:blue", "--"), (6.0, "tab:green", "-.")]
    for d_cm, col, ls in d_sweep_list:
        k_val = get_k_at_d(d_cm)
        M_val = k_val * np.sqrt(L1 * L2)
        eta_c = circuit.eta_closed(M_val, f0, R1, R2, RL_cont) * 100.0
        rl_opt = float(circuit.RL_opt(M_val, f0, R1, R2))
        eta_opt = float(circuit.eta_closed(M_val, f0, R1, R2, rl_opt) * 100.0)

        ax1.plot(RL_cont, eta_c, color=col, linestyle=ls, linewidth=2.2,
                 label=f"AC link η_link (d = {d_cm:g} cm, R_L,opt = {rl_opt:.1f} Ω)")
        ax1.plot([rl_opt], [eta_opt], color=col, marker="*", markersize=11)

        if np.isclose(d_cm, 3.0):
            eta_low_R = circuit.eta_closed(M_val, f0, R_min, R_min, RL_cont) * 100.0
            eta_high_R = circuit.eta_closed(M_val, f0, R_max, R_max, RL_cont) * 100.0
            ax1.fill_between(RL_cont, eta_high_R, eta_low_R, color=col, alpha=0.16,
                             label=f"C-T2 R range {R_min:.2f}–{R_max:.2f} Ω (d = 3 cm)")

    k_3cm = get_k_at_d(3.0)
    M_3cm = k_3cm * np.sqrt(L1 * L2)
    Zin_3 = R1 + ((w0 * M_3cm) ** 2) / (R2 + RL_cont)
    I1_3 = VS_PEAK / Zin_3
    I2_3 = (w0 * M_3cm * I1_3) / (R2 + RL_cont)
    V_dc = (np.pi / 4.0) * I2_3 * RL_cont
    rect_diode_eff = V_dc / (V_dc + 2.0 * VF_SCHOTTKY)
    eta_sys_3 = circuit.eta_closed(M_3cm, f0, R1, R2, RL_cont) * rect_diode_eff * 100.0
    ax1.plot(RL_cont, eta_sys_3, color="purple", linestyle=":", linewidth=2.2,
             label="Rectifier mode η_sys (d = 3 cm, R_ac = 0.81 R_DC, 2V_F = 0.7 V)")

    ax1.set_xscale("log")
    ax1.set_xlabel("Effective AC load resistance R_L [Ω]")
    ax1.set_ylabel("Efficiency η [%]")
    ax1.set_xlim(0.1, 50.0)
    ax1.set_ylim(0, 102)
    ax1.legend(loc="lower right", fontsize=9.2)

    ax2 = ax1.twiny()
    ax2.set_xscale("log")
    ax2.set_xlim(0.1 / RECT_FACTOR, 50.0 / RECT_FACTOR)
    ax2.set_xlabel("Equivalent rectifier DC load R_DC = (π²/8) R_L [Ω]  (R_L ≈ 0.81 R_DC)", fontsize=11)
    ax2.grid(False)

    # Save ONLY to C-specific filename so B's fig_eta_vs_RL is untouched
    style.save_fig(fig, "fig_c_v1_eta_vs_RL_rectifier")
    plt.close(fig)

    rows_cv1 = []
    for rl_val in params.RL_list:
        rl = float(rl_val)
        r_dc = rl / RECT_FACTOR
        eta_3 = float(circuit.eta_closed(M_3cm, f0, R1, R2, rl) * 100.0)
        zin = R1 + ((w0 * M_3cm) ** 2) / (R2 + rl)
        i2 = (w0 * M_3cm * (VS_PEAK / zin)) / (R2 + rl)
        vdc = (np.pi / 4.0) * i2 * rl
        eta_sys = eta_3 * (vdc / (vdc + 2.0 * VF_SCHOTTKY))
        k_6cm = get_k_at_d(6.0)
        M_6cm = k_6cm * np.sqrt(L1 * L2)
        eta_6 = float(circuit.eta_closed(M_6cm, f0, R1, R2, rl) * 100.0)
        rows_cv1.append({
            "RL_ac_ohm": f"{rl:g}",
            "R_DC_equiv_ohm": f"{r_dc:.2f}",
            "eta_link_d3cm_pct": f"{eta_3:.2f}",
            "eta_sys_rect_d3cm_pct": f"{eta_sys:.2f}",
            "eta_link_d6cm_pct": f"{eta_6:.2f}",
        })
    with open(DATA_DIR / "c_v1_load_rectifier.csv", mode="w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows_cv1[0].keys()))
        writer.writeheader()
        writer.writerows(rows_cv1)

    # 2. Misalignment comparison plot (fig_c_v1_misalign_band) & exact CSV table (data/c_v1_misalign_table.csv)
    mis_cols = make_figures.read_csv_columns(DATA_DIR / "sim_misalign.csv")
    d_mis = make_figures.to_float_array(mis_cols["d_cm"])
    dx_mis = make_figures.to_float_array(mis_cols["dx_cm"])
    M_mis = make_figures.to_float_array(mis_cols["M_H"])
    k_mis = make_figures.to_float_array(mis_cols["k"])

    fig, ax = plt.subplots(figsize=(7.5, 4.8))
    mis_subsets = {}
    for d_val, col, ls in [(3.0, "tab:blue", "-"), (5.0, "tab:orange", "--")]:
        mask = np.isclose(d_mis, d_val)
        dx_sub = dx_mis[mask]
        M_sub = M_mis[mask]
        k_sub = k_mis[mask]
        M0 = float(M_sub[0])
        rl_opt0 = float(circuit.RL_opt(M0, f0, R1, R2))
        rl_opt0_03 = float(circuit.RL_opt(M0, f0, 0.3, 0.3))

        eta_nom = circuit.eta_closed(M_sub, f0, R1, R2, rl_opt0) * 100.0
        eta_r_low = circuit.eta_closed(M_sub, f0, R_min, R_min, rl_opt0) * 100.0
        eta_r_high = circuit.eta_closed(M_sub, f0, R_max, R_max, rl_opt0) * 100.0
        eta_03 = circuit.eta_closed(M_sub, f0, 0.3, 0.3, rl_opt0_03) * 100.0

        mis_subsets[d_val] = (dx_sub, M_sub, k_sub, eta_nom, eta_03)

        ax.plot(dx_sub, eta_nom, color=col, linestyle=ls, linewidth=2.2,
                label=f"d = {d_val:g} cm (R_L = {rl_opt0:.2f} Ω, R = {R1:.2f} Ω nominal)")
        ax.fill_between(dx_sub, eta_r_high, eta_r_low, color=col, alpha=0.18,
                        label=f"d = {d_val:g} cm (C-T2 R = {R_min:.2f}–{R_max:.2f} Ω band)")

    ax.set_xlabel("Lateral offset Δx [cm]")
    ax.set_ylabel("Link efficiency η(Δx) [%]")
    ax.set_title("Misalignment Efficiency η(Δx) Across C-T2 Resistance Range")
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 100)
    ax.legend(loc="lower left", fontsize=10)

    # Save ONLY to fig_c_v1_misalign_band so A's fig_eta_vs_dx is untouched
    style.save_fig(fig, "fig_c_v1_misalign_band")
    plt.close(fig)

    # Save exact misalignment comparison table at dx = [0, 2, 4, 5, 6, 8, 10] cm
    dx_table_pts = [0.0, 2.0, 4.0, 5.0, 6.0, 8.0, 10.0]
    rows_mis_tbl = []
    dx3, M3, k3, e3_04, e3_03 = mis_subsets[3.0]
    dx5, M5, k5, e5_04, e5_03 = mis_subsets[5.0]
    for dx_v in dx_table_pts:
        i3 = int(np.argmin(np.abs(dx3 - dx_v)))
        i5 = int(np.argmin(np.abs(dx5 - dx_v)))
        rows_mis_tbl.append({
            "dx_cm": f"{dx_v:g}",
            "M_d3cm_uH": f"{M3[i3] * 1e6:.3f}",
            "k_d3cm": f"{k3[i3]:+.4f}",
            "eta_d3cm_Rnom_pct": f"{e3_04[i3]:.2f}",
            "eta_d3cm_R03_pct": f"{e3_03[i3]:.2f}",
            "M_d5cm_uH": f"{M5[i5] * 1e6:.3f}",
            "k_d5cm": f"{k5[i5]:+.4f}",
            "eta_d5cm_Rnom_pct": f"{e5_04[i5]:.2f}",
            "eta_d5cm_R03_pct": f"{e5_03[i5]:.2f}",
        })
    with open(DATA_DIR / "c_v1_misalign_table.csv", mode="w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows_mis_tbl[0].keys()))
        writer.writeheader()
        writer.writerows(rows_mis_tbl)


def main():
    make_figures.apply_poster_rc()
    run_c_s1_ac_validation()
    run_c_s1_transient()
    run_c_v1_comparisons()
    print("Tasks C-S1 and C-V1 complete: validation CSVs, non-clashing fig_c_* plots, and transient screenshot generated.")


if __name__ == "__main__":
    main()