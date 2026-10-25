"""B-V1 (part 1): analytical vs simulated eta(d), P_L(d), eta(f), P_L(f) and mode splitting.

Run from the repo root:  python -m sim.compare_circuit      (writes data/ and figs/)
                         python -m sim.compare_circuit --out DIR   (writes everything into DIR)

"Simulation" is the phasor solver sim/circuit.py solve(), which solves the 2x2 mesh system by
Cramer's rule. "Analytical" is:
  at f0      the closed forms of B-T2: eta(M, RL), eta_max = x/(1+sqrt(1+x))^2,
             P_L = 0.5 Vs^2 w0^2 M^2 RL / [(R1+Rs)(R2+RL) + w0^2 M^2]^2,
             |I1| = Vs / (R1 + Rs + w0^2 M^2/(R2+RL))
  at any f   the elimination route of B-T1 Section 5: Zin = Z1 + w^2 M^2/Z2, I1 = Vs/(Zin + Rs),
             |I2| = w M |I1| / |Z2|, eta = w^2 M^2 RL / (R1 |Z2|^2 + w^2 M^2 (R2+RL))
  splitting  the lossless mode frequencies f0/sqrt(1 +- k) (B-T1 Section 12), valid only for a
             lightly loaded secondary; the fixed load pulls the peaks together.
The resistance band R1 = R2 = params.R_range (C-T2: 0.38-0.48 ohm) shows how much R moves eta(d).
"""
import argparse
from pathlib import Path

import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

from sim import params
from sim.circuit import solve, eta_closed, RL_opt, eta_max
from sim.link import ROOT, M_of_d, fixed_load
from sim.style import THEORY, SIM, save_fig

D_SPLIT = [1, 2, 5, 10]                 # spacings for eta(f), P_L(f) and the split peaks [cm]
F_LO, F_HI, N_PTS = 0.6, 1.6, 40001     # same frequency window as B-S2
RL_LIGHT = 0.01                         # lightly loaded secondary for the split-peak formula [ohm]


def analytic_f(f, M, RL, Vs, Rs, R1=None, R2=None):
    """Elimination route of B-T1 Section 5 at any frequency: returns (|I1|, PL, eta)."""
    R1 = params.R1 if R1 is None else R1
    R2 = params.R2 if R2 is None else R2
    w = 2 * np.pi * np.asarray(f, dtype=float)
    Z1 = R1 + 1j * w * params.L1 + 1 / (1j * w * params.C1)
    Z2 = R2 + RL + 1j * w * params.L2 + 1 / (1j * w * params.C2)
    Zin = Z1 + (w * M) ** 2 / Z2
    I1 = Vs / (Zin + Rs)
    I2 = w * M * np.abs(I1) / np.abs(Z2)
    PL = 0.5 * I2 ** 2 * RL
    eta = (w * M) ** 2 * RL / (R1 * np.abs(Z2) ** 2 + (w * M) ** 2 * (R2 + RL))
    return np.abs(I1), PL, eta


def peaks(f, y):
    """Local maxima of y(f) above 20 % of the global maximum."""
    idx = [j for j in range(1, len(y) - 1) if y[j] > y[j - 1] and y[j] >= y[j + 1] and y[j] > 0.2 * y.max()]
    return f[idx]


def rel_err(a, b):
    return float(np.max(np.abs(a - b) / np.abs(b)))


def save(fig, out_fig, name):
    """figs/ through style.save_fig, or the same two files in out_fig when --out is given."""
    if out_fig is None:
        save_fig(fig, name)
    else:
        out_fig.mkdir(parents=True, exist_ok=True)
        fig.savefig(out_fig / f"{name}.pdf", metadata={"CreationDate": None})
        fig.savefig(out_fig / f"{name}.png", dpi=300)
    plt.close(fig)


def main(out=None):
    out_data = Path(out) if out else ROOT / "data"
    out_fig = Path(out) if out else None
    out_data.mkdir(parents=True, exist_ok=True)

    f0, R1, R2, L1, L2, C1, C2 = params.f0, params.R1, params.R2, params.L1, params.L2, params.C1, params.C2
    Vs, Rs = params.Vs, params.Rs
    w0 = 2 * np.pi * f0
    RL = fixed_load()
    df = pd.read_csv(ROOT / "data" / "sim_M_k.csv")
    d_cm, M, k = df["d_cm"].to_numpy(), df["M_H"].to_numpy(), df["k"].to_numpy()
    print(f"R1 = R2 = {R1:g} ohm (C-T2 nominal), R_L = {RL:.3f} ohm, Vs = {Vs:g} V peak, Rs = {Rs:g} ohm")

    metrics = []

    # ---- 1. at f0, versus spacing -------------------------------------------------------------
    sim = solve(f0, M, L1, L2, C1, C2, R1, R2, RL, Vs, Rs=Rs)
    RLo = RL_opt(M, f0, R1, R2)
    sim_opt = solve(f0, M, L1, L2, C1, C2, R1, R2, RLo, Vs, Rs=Rs)
    th_eta = eta_closed(M, f0, R1, R2, RL)
    th_etamax = eta_max(M, f0, R1, R2)
    th_PL = 0.5 * Vs ** 2 * w0 ** 2 * M ** 2 * RL / ((R1 + Rs) * (R2 + RL) + w0 ** 2 * M ** 2) ** 2
    th_I1 = Vs / (R1 + Rs + w0 ** 2 * M ** 2 / (R2 + RL))
    for name, s, t in (("eta(d), fixed R_L", sim.eta, th_eta),
                       ("eta_max(d), R_L,opt(d)", sim_opt.eta, th_etamax),
                       ("P_L(d), fixed R_L", sim.PL, th_PL),
                       ("|I1|(d), fixed R_L", np.abs(sim.I1), th_I1)):
        metrics.append(dict(check=name, condition=f"f = f0, d = {d_cm.min():g}-{d_cm.max():g} cm",
                            max_rel_error=rel_err(s, t), reference="B-T2 closed form"))
    pd.DataFrame({"d_cm": d_cm, "k": k, "eta_sim": sim.eta, "eta_theory": th_eta,
                  "eta_max_sim": sim_opt.eta, "eta_max_theory": th_etamax,
                  "PL_sim_W": sim.PL, "PL_theory_W": th_PL,
                  "I1_sim_A": np.abs(sim.I1), "I1_theory_A": th_I1}
                 ).to_csv(out_data / "val_circuit_d.csv", index=False)

    fig, axes = plt.subplots(1, 2, figsize=(13, 5))
    ax = axes[0]
    ax.plot(d_cm, 100 * th_etamax, label=r"$\eta_{max}$, closed form", **THEORY)
    ax.plot(d_cm, 100 * sim_opt.eta, label=r"$\eta$ at $R_{L,opt}(d)$, circuit solver", **SIM)
    ax.plot(d_cm, 100 * th_eta, label=rf"$\eta$, $R_L$ = {RL:.2f} $\Omega$, closed form",
            color="tab:blue", ls="-", lw=1, alpha=0.6)
    ax.plot(d_cm, 100 * sim.eta, label=rf"$\eta$, $R_L$ = {RL:.2f} $\Omega$, circuit solver",
            color="tab:orange", ls=":", lw=2)
    ax.set_xlabel("Coil spacing d (cm)"); ax.set_ylabel(r"Link efficiency $\eta_{link}$ (%)")
    ax.set_ylim(0, 100); ax.legend(fontsize=10)
    ax = axes[1]
    ax.plot(d_cm, th_PL, label="closed form (B-T2)", **THEORY)
    ax.plot(d_cm, sim.PL, label="circuit solver", **SIM)
    ax.set_xlabel("Coil spacing d (cm)"); ax.set_ylabel("Load power $P_L$ (W)")
    ax.set_title(rf"$R_L$ = {RL:.2f} $\Omega$, $V_s$ = {Vs:g} V peak, $R_s$ = {Rs:g} $\Omega$", fontsize=12)
    ax.legend(fontsize=11)
    fig.tight_layout(); save(fig, out_fig, "fig_eta_PL_vs_d_validation")

    # ---- 2. versus frequency, and 3. split peaks ------------------------------------------------
    f = np.linspace(F_LO * f0, F_HI * f0, N_PTS)
    rows, curves = [], {}
    for d in D_SPLIT:
        Md = M_of_d(d); kd = Md / np.sqrt(L1 * L2)
        s = solve(f, Md, L1, L2, C1, C2, R1, R2, RL, Vs, Rs=Rs)
        _, PL_t, eta_t = analytic_f(f, Md, RL, Vs, Rs)
        curves[d] = (kd, s.eta, eta_t, s.PL, PL_t)
        metrics.append(dict(check=f"eta(f), d = {d} cm", condition=f"{F_LO:g}-{F_HI:g} f0, fixed R_L",
                            max_rel_error=rel_err(s.eta, eta_t), reference="B-T1 Sec. 5 elimination"))
        metrics.append(dict(check=f"P_L(f), d = {d} cm", condition=f"{F_LO:g}-{F_HI:g} f0, fixed R_L",
                            max_rel_error=rel_err(s.PL, PL_t), reference="B-T1 Sec. 5 elimination"))

        fl_th, fh_th = f0 / np.sqrt(1 + kd), f0 / np.sqrt(1 - kd)
        for label, load in (("light", RL_LIGHT), ("fixed", RL)):
            pk = peaks(f, solve(f, Md, L1, L2, C1, C2, R1, R2, load, Vs, Rs=Rs).PL)
            two = len(pk) > 1
            fl, fh = (pk[0], pk[-1]) if two else (np.nan, np.nan)
            k_pk = (fh ** 2 - fl ** 2) / (fh ** 2 + fl ** 2) if two else np.nan
            rows.append(dict(d_cm=d, k=kd, load=label, RL_ohm=load, n_peaks=len(pk),
                             f_low_sim_kHz=fl / 1e3, f_high_sim_kHz=fh / 1e3,
                             f_low_theory_kHz=fl_th / 1e3, f_high_theory_kHz=fh_th / 1e3,
                             err_low_kHz=(fl - fl_th) / 1e3, err_high_kHz=(fh - fh_th) / 1e3,
                             k_from_peaks=k_pk, k_err_percent=100 * (k_pk - kd) / kd))
    split = pd.DataFrame(rows)
    split.to_csv(out_data / "val_split_peaks.csv", index=False)

    fig, axes = plt.subplots(2, 2, figsize=(12, 8), sharex=True)
    for ax, d in zip(axes.ravel(), D_SPLIT):
        kd, _, _, PL_s, PL_t = curves[d]
        ax.plot(f / 1e3, PL_t, label="analytical (B-T1 Sec. 5)", **THEORY)
        ax.plot(f / 1e3, PL_s, label="circuit solver", **SIM)
        for ff, lab in ((f0 / np.sqrt(1 + kd), r"$f_0/\sqrt{1\pm k}$ (lossless)"), (f0 / np.sqrt(1 - kd), None)):
            ax.axvline(ff / 1e3, color="gray", ls=":", lw=1.5, label=lab)
        ax.set_title(f"d = {d} cm, k = {kd:.3f}", fontsize=13); ax.legend(fontsize=9)
    for ax in axes[1]: ax.set_xlabel("Frequency f (kHz)")
    for ax in axes[:, 0]: ax.set_ylabel("Load power $P_L$ (W)")
    fig.suptitle(rf"$R_L$ = {RL:.2f} $\Omega$, $V_s$ = {Vs:g} V peak, $R_s$ = {Rs:g} $\Omega$", fontsize=13)
    fig.tight_layout(); save(fig, out_fig, "fig_PL_vs_f_validation")

    fig, ax = plt.subplots()
    kk = np.linspace(0.02, 0.6, 300)
    ax.plot(kk, f0 / np.sqrt(1 + kk) / 1e3, label=r"$f_0/\sqrt{1\pm k}$ (lossless)", **THEORY)
    ax.plot(kk, f0 / np.sqrt(1 - kk) / 1e3, **THEORY)
    for label, mk, txt in (("light", "o", rf"solver, $R_L$ = {RL_LIGHT:g} $\Omega$"),
                           ("fixed", "s", rf"solver, $R_L$ = {RL:.2f} $\Omega$")):
        q = split[(split.load == label) & (split.n_peaks > 1)]
        ax.plot(q.k, q.f_low_sim_kHz, ls="none", marker=mk, color="tab:orange", mfc="none" if mk == "s" else None, label=txt)
        ax.plot(q.k, q.f_high_sim_kHz, ls="none", marker=mk, color="tab:orange", mfc="none" if mk == "s" else None)
    ax.set_xlabel("Coupling coefficient k (-)"); ax.set_ylabel("Peak frequency (kHz)")
    ax.legend(fontsize=11)
    save(fig, out_fig, "fig_split_vs_k_validation")

    # ---- 4. resistance band ---------------------------------------------------------------------
    band = {}
    for tag, R in (("low", params.R_range[0]), ("nom", params.R1), ("high", params.R_range[1])):
        band[tag] = (R, solve(f0, M, L1, L2, C1, C2, R, R, RL, Vs, Rs=Rs).eta, eta_max(M, f0, R, R))
    fig, ax = plt.subplots()
    ax.fill_between(d_cm, 100 * band["high"][2], 100 * band["low"][2], color="tab:blue", alpha=0.15,
                    label=rf"$\eta_{{max}}$, R = {band['low'][0]:.2f}-{band['high'][0]:.2f} $\Omega$ (C-T2 range)")
    ax.plot(d_cm, 100 * band["nom"][2], label=rf"$\eta_{{max}}$, R = {R1:g} $\Omega$ (closed form)", **THEORY)
    ax.fill_between(d_cm, 100 * band["high"][1], 100 * band["low"][1], color="tab:orange", alpha=0.2,
                    label=rf"$\eta$, $R_L$ = {RL:.2f} $\Omega$, same R range")
    ax.plot(d_cm, 100 * band["nom"][1], label=rf"$\eta$, $R_L$ = {RL:.2f} $\Omega$ (circuit solver)", **SIM)
    ax.set_xlabel("Coil spacing d (cm)"); ax.set_ylabel(r"Link efficiency $\eta_{link}$ (%)")
    ax.set_ylim(0, 100); ax.legend(fontsize=10, loc="lower left")
    save(fig, out_fig, "fig_eta_vs_d_Rband")
    pd.DataFrame({"d_cm": d_cm, **{f"eta_R{v[0]:g}": v[1] for v in band.values()},
                  **{f"eta_max_R{v[0]:g}": v[2] for v in band.values()}}
                 ).to_csv(out_data / "val_eta_Rband.csv", index=False)

    met = pd.DataFrame(metrics)
    met.to_csv(out_data / "val_circuit_metrics.csv", index=False)

    # ---- printed summary --------------------------------------------------------------------------
    pd.set_option("display.width", 200)
    print("\nSolver vs analytical (max relative error):")
    print(met.to_string(index=False, float_format=lambda v: f"{v:.1e}"))
    print("\nSplit peaks, solver vs f0/sqrt(1 -+ k):")
    print(split[["d_cm", "k", "RL_ohm", "n_peaks", "f_low_sim_kHz", "f_low_theory_kHz", "f_high_sim_kHz",
                 "f_high_theory_kHz", "k_from_peaks", "k_err_percent"]].to_string(index=False, float_format=lambda v: f"{v:.3f}"))
    print("\nR band:")
    for dd in (1, 3, 5, 8, 10):
        i = int(np.argmin(np.abs(d_cm - dd)))
        print(f"d = {dd:>2} cm: eta(R_L fixed) = " + " / ".join(f"{100*v[1][i]:.1f} %" for v in band.values())
              + "   eta_max = " + " / ".join(f"{100*v[2][i]:.1f} %" for v in band.values())
              + f"   (R = {band['low'][0]:.2f} / {band['nom'][0]:.2f} / {band['high'][0]:.2f} ohm)")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", help="write CSVs and figures here instead of data/ and figs/")
    main(ap.parse_args().out)
