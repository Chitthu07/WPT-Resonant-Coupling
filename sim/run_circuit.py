"""B-S1: eta(d), eta_max(d) and P_L(d) from the circuit model, using data/sim_M_k.csv.

Run from the repo root:  python -m sim.run_circuit

At f0, P_L = 0.5 Vs^2 RL w0^2 M^2 / [(R1+Rs)(R2+RL) + w0^2 M^2]^2, which is largest at k = k_c,
where w0^2 M^2 = (R1+Rs)(R2+RL). For smaller spacings the reflected resistance w0^2 M^2/(R2+RL)
limits I1, so P_L falls even though eta rises.
Pin is taken at the resonator terminals, so eta does not depend on Rs.
"""
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

from sim import params
from sim.circuit import solve, eta_closed, RL_opt, eta_max, k_crit
from sim.link import ROOT, fixed_load
from sim.style import THEORY, SIM, save_fig


def main():
    df = pd.read_csv(ROOT / "data" / "sim_M_k.csv")
    d_cm, M, k = df["d_cm"].to_numpy(), df["M_H"].to_numpy(), df["k"].to_numpy()
    f0, R1, R2, L1, L2, C1, C2 = params.f0, params.R1, params.R2, params.L1, params.L2, params.C1, params.C2
    Vs, Rs, Rg = params.Vs, params.Rs, params.Rs_gen

    RL_fix = fixed_load()
    print(f"R1 = R2 = {R1:g} ohm (C-T2 nominal), fixed R_L = {RL_fix:.3f} ohm, Vs = {Vs:g} V peak, Rs = {Rs:g} ohm")

    r = solve(f0, M, L1, L2, C1, C2, R1, R2, RL_fix, Vs, Rs=Rs)            # numeric, fixed R_L
    eta_cf = eta_closed(M, f0, R1, R2, RL_fix)                           # closed form, same R_L
    assert np.max(np.abs(r.eta - eta_cf)) < 1e-6, "numeric and closed-form eta disagree"
    RLo = RL_opt(M, f0, R1, R2)
    eta_best = eta_max(M, f0, R1, R2)
    r_opt = solve(f0, M, L1, L2, C1, C2, R1, R2, RLo, Vs, Rs=Rs)
    assert np.max(np.abs(r_opt.eta - eta_best)) < 1e-6
    r_gen = solve(f0, M, L1, L2, C1, C2, R1, R2, RL_fix, Vs, Rs=Rg)      # same link, 50 ohm generator

    # Critical coupling for the fixed load (P_L(d) peaks here)
    kc = float(k_crit(L1, L2, f0, R1, R2, RL_fix, Rs=Rs))
    d_kc = float(np.interp(-kc, -k, d_cm))                                # k falls with d
    i_pk = int(np.argmax(r.PL))
    print(f"k_c = {kc:.4f} at d = {d_kc:.2f} cm; P_L peak at d = {d_cm[i_pk]:.2f} cm (Rs = {Rs:g} ohm)")

    pd.DataFrame({"d_cm": d_cm, "M_H": M, "k": k, "eta_fixedRL": r.eta, "PL_W": r.PL,
                  "I1_A_peak": np.abs(r.I1), "RL_opt_ohm": RLo, "eta_max": eta_best,
                  "PL_at_RLopt_W": r_opt.PL, f"PL_Rs{Rg:g}_W": r_gen.PL}
                 ).to_csv(ROOT / "data" / "sim_eta_d.csv", index=False)

    fig, ax = plt.subplots()
    ax.plot(d_cm, 100 * eta_best, label=r"$\eta_{max}$ with $R_{L,opt}(d)$ (closed form)", **THEORY)
    ax.plot(d_cm, 100 * r.eta, label=f"$R_L$ fixed = {RL_fix:.2f} $\\Omega$ (= $R_{{L,opt}}$ at {100*params.d_RL_fixed:g} cm), circuit solver", **SIM)
    ax.set_xlabel("Coil spacing d (cm)"); ax.set_ylabel(r"Link efficiency $\eta_{link}$ (%)")
    ax.set_ylim(0, 100); ax.legend(fontsize=11, loc="upper center", bbox_to_anchor=(0.5, -0.15))
    save_fig(fig, "fig_eta_vs_d"); plt.close(fig)

    fig, ax = plt.subplots()
    ax.plot(d_cm, r.PL, label=f"$R_s$ = {Rs:g} $\\Omega$, $V_s$ = {Vs:g} V peak", **SIM)
    ax.axvline(d_kc, color="gray", lw=1.5, label=f"$k = k_c$ = {kc:.3f} (d = {d_kc:.1f} cm)")
    ax2 = ax.twinx()
    ax2.plot(d_cm, 1e3 * r_gen.PL, color="tab:brown", ls=":", lw=2,
             label=f"$R_s$ = {Rg:g} $\\Omega$ generator (right axis)")
    ax2.set_ylabel(f"$P_L$ with $R_s$ = {Rg:g} $\\Omega$ (mW)"); ax2.grid(False)
    ax.set_xlabel("Coil spacing d (cm)"); ax.set_ylabel(f"Load power $P_L$, $R_s$ = {Rs:g} $\\Omega$ (W)")
    ax.set_title(f"$R_L$ = {RL_fix:.2f} $\\Omega$")
    h1, l1 = ax.get_legend_handles_labels(); h2, l2 = ax2.get_legend_handles_labels()
    ax.legend(h1 + h2, l1 + l2, fontsize=10, loc="upper center", bbox_to_anchor=(0.5, -0.15), ncol=2)
    save_fig(fig, "fig_PL_vs_d"); plt.close(fig)

    for dd in (1, 2, 3, 5, 8, 10):
        i = np.argmin(np.abs(d_cm - dd))
        print(f"d = {dd:>2} cm: eta(fixed R_L) = {100*r.eta[i]:5.1f} %, eta_max = {100*eta_best[i]:5.1f} %, "
              f"R_L,opt = {RLo[i]:5.2f} ohm, P_L = {r.PL[i]:.3f} W, |I1| = {abs(r.I1[i]):.2f} A, "
              f"P_L(Rs={Rg:g}) = {1e3*r_gen.PL[i]:.1f} mW")


if __name__ == "__main__":
    main()
