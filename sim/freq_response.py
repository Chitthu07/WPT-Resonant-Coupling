"""B-S2: frequency response, mode splitting, coupling regime and detuning.

Run from the repo root:  python -m sim.freq_response

3 dB bandwidth and loaded Q are given only for single-peak curves.
Detuning: the shaded band |dC2/C2| ~ 1/Q2L, Q2L = w0 L2/(R2+RL), is an approximate guide from the
secondary loop alone; the actual sensitivity also depends on k (at 3 cm, over-coupled, P_L hardly changes).
"""
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

from sim import params
from sim.circuit import solve, k_crit
from sim.link import ROOT, M_of_d, fixed_load
from sim.style import THEORY, SIM, save_fig

D_CM = [1, 2, 5, 10]            # distances for eta(f)
F_LO, F_HI, N_PTS = 0.6, 1.6, 40001   # 0.6-1.6 f0 so the upper split peak at 1 cm (~717 kHz) is inside


def peak_metrics(f, y):
    """Global peak of y(f): peak frequency, -3 dB (half-power) width around it, loaded Q = f_pk / width.

    For split curves the width is measured around the HIGHEST peak, and only while y stays above half
    of that peak, so it is the bandwidth of one lobe, not of the whole double-hump.
    """
    i = int(np.argmax(y)); half = y[i] / 2
    lo = i
    while lo > 0 and y[lo] >= half: lo -= 1
    hi = i
    while hi < len(y) - 1 and y[hi] >= half: hi += 1
    bw = f[hi] - f[lo]
    return f[i], bw, f[i] / bw


def local_peaks(f, y):
    idx = [j for j in range(1, len(y) - 1) if y[j] > y[j - 1] and y[j] >= y[j + 1] and y[j] > 0.2 * y.max()]
    return f[idx]


def main():
    f0, R1, R2, L1, L2, C1, C2 = params.f0, params.R1, params.R2, params.L1, params.L2, params.C1, params.C2
    VS, Rs = params.Vs, params.Rs
    RL = fixed_load()
    kc = float(k_crit(L1, L2, f0, R1, R2, RL, Rs=Rs))
    f = np.linspace(F_LO * f0, F_HI * f0, N_PTS)
    print(f"R1 = R2 = {R1:g} ohm (C-T2 nominal), Rs = {Rs:g} ohm, R_L fixed = {RL:.3f} ohm, k_c = {kc:.4f}")

    curves, rows = {}, []
    for d in D_CM:
        M = M_of_d(d); k = M / np.sqrt(L1 * L2)
        r = solve(f, M, L1, L2, C1, C2, R1, R2, RL, VS, Rs=Rs)
        vl = np.abs(r.I2) * RL / VS
        curves[d] = (r.eta, r.PL, vl, k)
        fpk, bw, QL = peak_metrics(f, r.PL)
        pks = local_peaks(f, r.PL)
        if len(pks) > 1:                       # split response: no single 3 dB width
            bw, QL = np.nan, np.nan
        regime = "over-coupled" if k > 1.05 * kc else ("under-coupled" if k < 0.95 * kc else "about critical")
        f_lo_th, f_hi_th = f0 / np.sqrt(1 + k), f0 / np.sqrt(1 - k)
        width = (f"3 dB width = {bw/1e3:.2f} kHz, loaded Q = {QL:.0f}" if len(pks) == 1
                 else "split -> no single 3 dB width")
        print(f"d={d:>2} cm k={k:.4f} ({regime}); PL peaks (kHz): {np.round(pks/1e3,1)}; "
              f"ideal lossless mode estimates (kHz) = {f_lo_th/1e3:.1f}, {f_hi_th/1e3:.1f}; "
              f"highest-peak f = {fpk/1e3:.1f} kHz, {width}")
        rows.append(dict(d_cm=d, k=k, regime=regime, RL_ohm=RL, kc=kc, f_peak_kHz=fpk / 1e3,
                         bw3dB_kHz=bw / 1e3, Q_loaded=QL, n_peaks=len(pks),
                         f_low_peak_kHz=pks[0] / 1e3, f_high_peak_kHz=pks[-1] / 1e3,
                         f_low_theory_kHz=f_lo_th / 1e3, f_high_theory_kHz=f_hi_th / 1e3))
    pd.DataFrame(rows).to_csv(ROOT / "data" / "sim_freq_metrics.csv", index=False)

    labels = [(0, r"Link efficiency $\eta_{link}$ (%)", 100.0, "fig_eta_vs_f"),
              (1, r"Load power $P_L$ (W)", 1.0, "fig_PL_vs_f"),
              (2, r"$|V_L/V_s|$ (-)", 1.0, "fig_VL_vs_f")]
    for idx, ylabel, scale, name in labels:
        fig, axes = plt.subplots(2, 2, figsize=(11, 8), sharex=True)
        for ax, d in zip(axes.ravel(), D_CM):
            y = curves[d][idx] * scale; k = curves[d][3]
            ax.plot(f / 1e3, y, label="circuit solver", **SIM)
            ax.axvline(f0 / 1e3, color="gray", lw=1.5, label=r"$f_0$")
            if k > kc and idx != 0:
                for ff, lab in ((f0 / np.sqrt(1 + k), r"$f_0/\sqrt{1\pm k}$"), (f0 / np.sqrt(1 - k), None)):
                    ax.axvline(ff / 1e3, color="tab:blue", ls=":", lw=2, label=lab)
            ax.set_title(f"d = {d} cm, k = {k:.3f}"); ax.legend(fontsize=10)
        for ax in axes[1]: ax.set_xlabel("Frequency f (kHz)")
        for ax in axes[:, 0]: ax.set_ylabel(ylabel)
        fig.tight_layout(); save_fig(fig, name); plt.close(fig)

    # ---- detuning of C2, evaluated at f0 (d = 3 cm required; 10 and 15 cm added for contrast) -------
    dC = np.linspace(-20, 20, 401) / 100
    Q2L = 2 * np.pi * f0 * L2 / (R2 + RL)       # loaded Q of the secondary loop
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))
    out = {"dC2_percent": 100 * dC}
    for d, ls in ((3.0, "-"), (10.0, "--"), (15.0, ":")):
        M = M_of_d(d)
        r0 = solve(f0, M, L1, L2, C1, C2, R1, R2, RL, VS, Rs=Rs)
        r = solve(f0, M, L1, L2, C1, C2 * (1 + dC), R1, R2, RL, VS, Rs=Rs)
        axes[0].plot(100 * dC, 100 * r.eta, ls=ls, color="tab:orange", label=f"d = {d:g} cm")
        axes[1].plot(100 * dC, r.PL / r0.PL, ls=ls, color="tab:orange", label=f"d = {d:g} cm")
        out[f"eta_d{d:g}"] = r.eta; out[f"PL_rel_d{d:g}"] = r.PL / r0.PL
        print(f"d = {d:g} cm: eta(0) = {100*float(r0.eta):.1f} %")
        for dd in (-20, -10, -5, -1, 1, 5, 10, 20):
            q = solve(f0, M, L1, L2, C1, C2 * (1 + dd / 100), R1, R2, RL, VS, Rs=Rs)
            print(f"   C2 {dd:+d} %: eta = {100*float(q.eta):5.1f} %, PL/PL(0) = {float(q.PL/r0.PL):.2f}")
    for ax, yl in zip(axes, (r"Link efficiency $\eta_{link}$ (%)", r"$P_L / P_L$(tuned) (-)")):
        ax.axvspan(-100 / Q2L, 100 / Q2L, color="gray", alpha=0.15,
                   label=rf"guide: $|\Delta C_2/C_2| \approx 1/Q_{{2,L}}$ = {100 / Q2L:.0f} %")
        ax.set_xlabel(r"Detuning of $C_2$, $\Delta C_2/C_2$ (%)"); ax.set_ylabel(yl); ax.legend(fontsize=11)
    axes[0].set_title("d = 3 cm is over-coupled: insensitive to detuning", fontsize=12)
    fig.tight_layout(); save_fig(fig, "fig_eta_vs_detuning"); plt.close(fig)
    pd.DataFrame(out).to_csv(ROOT / "data" / "sim_detuning.csv", index=False)
    print(f"Detuning guide |dC2/C2| ~ 1/Q2L = {100 / Q2L:.1f} % (loaded Q2L = {Q2L:.1f})")


if __name__ == "__main__":
    main()
