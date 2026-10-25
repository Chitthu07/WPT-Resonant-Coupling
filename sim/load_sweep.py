"""B-S3: Load dependence of link efficiency and received power.

Run from the repository root:
    python -m sim.load_sweep

Sweeps load resistance for coil spacings of 1, 3 and 6 cm.
Compares numerical peak locations against analytical predictions.
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from sim import params
from sim.circuit import solve, RL_opt, eta_max
from sim.link import ROOT, M_of_d
from sim.style import SIM, save_fig

VS = params.Vs                  # peak source voltage
RS = params.Rs

# Coil spacings to analyse.
D_CM = [1.0, 3.0, 6.0]

# Logarithmic load-resistance sweep: approximately 0.032 to 3162 ohm.
RL = np.logspace(-1.5, 3.5, 2000)

# Full-bridge rectifier with C filter: R_ac = (8/pi^2) R_DC
RECTIFIER_FACTOR = params.rect_factor

# Simulation colour (orange), one shade per distance
SHADES = {1.0: "#fdae6b", 3.0: "#f16913", 6.0: "#a63603"}


def main():
    f0 = params.f0
    L1, L2 = params.L1, params.L2
    C1, C2 = params.C1, params.C2
    R1, R2 = params.R1, params.R2

    print(f"R1 = R2 = {R1:g} ohm (C-T2 nominal), Vs = {VS:g} V peak, Rs = {RS:g} ohm")
    all_rows = []

    # Store curves for plotting.
    curves = {}

    for d_cm in D_CM:
        M = M_of_d(d_cm)

        # Analytical predictions.
        RL_eta_opt = float(RL_opt(M, f0, R1, R2))
        eta_max_analytic = float(eta_max(M, f0, R1, R2))

        w0 = 2 * np.pi * f0
        RL_power_max = R2 + (w0 * M) ** 2 / (R1 + RS)

        # Vectorised numerical circuit solution over the entire load sweep.
        result = solve(
            f0, M,
            L1, L2,
            C1, C2,
            R1, R2,
            RL, VS, Rs=RS
        )

        eta = np.asarray(result.eta)
        PL = np.asarray(result.PL)

        # Find numerical maxima.
        i_eta = int(np.argmax(eta))
        i_power = int(np.argmax(PL))

        RL_eta_numeric = RL[i_eta]
        RL_power_numeric = RL[i_power]

        # Confirm the sampled peaks agree with the analytical predictions.
        eta_load_error = abs(RL_eta_numeric / RL_eta_opt - 1)
        power_load_error = abs(RL_power_numeric / RL_power_max - 1)

        assert eta_load_error < 0.01, (
            f"d={d_cm:g} cm: numerical efficiency optimum "
            f"{RL_eta_numeric:.4g} ohm differs from analytical "
            f"optimum {RL_eta_opt:.4g} ohm by "
            f"{100 * eta_load_error:.3f}%"
        )

        assert power_load_error < 0.01, (
            f"d={d_cm:g} cm: numerical power optimum "
            f"{RL_power_numeric:.4g} ohm differs from analytical "
            f"optimum {RL_power_max:.4g} ohm by "
            f"{100 * power_load_error:.3f}%"
        )

        # Store curves.
        curves[d_cm] = {
            "eta": eta,
            "PL": PL,
            "RL_eta_opt": RL_eta_opt,
            "eta_max": eta_max_analytic,
            "RL_power_max": RL_power_max,
            "PL_max": PL[i_power],
        }

        # Record every sampled point for CSV output.
        for j, load in enumerate(RL):
            all_rows.append({
                "d_cm": d_cm,
                "RL_ohm": load,
                "RDC_equiv_ohm": load / RECTIFIER_FACTOR,
                "eta": eta[j],
                "PL_W": PL[j],
                "RL_eta_opt_ohm": RL_eta_opt,
                "eta_max_analytic": eta_max_analytic,
                "RL_power_max_ohm": RL_power_max,
            })

        print(f"\nd = {d_cm:g} cm")
        print(
            f"  Maximum-efficiency load: "
            f"analytical = {RL_eta_opt:.3f} ohm, "
            f"numerical = {RL_eta_numeric:.3f} ohm"
        )
        print(
            f"  Maximum efficiency: "
            f"analytical = {100 * eta_max_analytic:.2f}%, "
            f"numerical = {100 * eta[i_eta]:.2f}%"
        )
        print(
            f"  Maximum-power load: "
            f"analytical = {RL_power_max:.3f} ohm, "
            f"numerical = {RL_power_numeric:.3f} ohm"
        )
        print(f"  Maximum load power: {PL[i_power]:.3f} W")
        print(
            f"  Efficiency-optimum load error: "
            f"{100 * eta_load_error:.3f}%"
        )
        print(
            f"  Power-optimum load error: "
            f"{100 * power_load_error:.3f}%"
        )

    # Save the complete sweep data.
    pd.DataFrame(all_rows).to_csv(
        ROOT / "data" / "sim_RL_sweep.csv",
        index=False
    )
    print("\nSaved data/sim_RL_sweep.csv")

    # ---------------------------------------------------------------
    # Figure 1: Link efficiency versus load resistance.
    # ---------------------------------------------------------------
    fig, ax = plt.subplots(figsize=(10, 6))

    for d_cm in D_CM:
        c = curves[d_cm]

        ax.plot(
            RL, 100 * c["eta"],
            label=f"d = {d_cm:g} cm",
            **dict(SIM, color=SHADES[d_cm])
        )

        ax.plot(
            c["RL_eta_opt"],
            100 * c["eta_max"],
            marker="o",
            linestyle="none",
            markersize=8,
            color=SHADES[d_cm],
            markeredgecolor="black",
            label=f"$\\eta_{{max}}$ at $R_{{L,opt}}$, {d_cm:g} cm"
        )

    ax.set_xscale("log")
    ax.set_xlabel(r"Load resistance $R_L$ ($\Omega$)")
    ax.set_ylabel("Link efficiency (%)")
    ax.set_title("Link Efficiency versus Load Resistance")
    ax.grid(True, which="both", alpha=0.25)
    ax.legend(fontsize=9)

    secondary = ax.secondary_xaxis(
        "top",
        functions=(
            lambda load: load / RECTIFIER_FACTOR,
            lambda rdc: rdc * RECTIFIER_FACTOR
        )
    )
    secondary.set_xlabel(
        r"Equivalent rectifier load $R_{DC}=R_L\,\pi^2/8$ ($\Omega$)"
    )

    fig.tight_layout()
    save_fig(fig, "fig_eta_vs_RL")
    plt.close(fig)

    # ---------------------------------------------------------------
    # Figure 2: Load power versus load resistance.
    # ---------------------------------------------------------------
    fig, ax = plt.subplots(figsize=(10, 6))

    for d_cm in D_CM:
        c = curves[d_cm]

        ax.plot(
            RL, c["PL"],
            label=f"d = {d_cm:g} cm",
            **dict(SIM, color=SHADES[d_cm])
        )

        # Mark the analytical maximum-efficiency load.
        i_eta = int(np.argmin(np.abs(RL - c["RL_eta_opt"])))
        ax.plot(
            RL[i_eta], c["PL"][i_eta],
            marker="o",
            linestyle="none",
            markersize=7,
            color=SHADES[d_cm],
            markeredgecolor="black",
            label=f"Efficiency optimum, {d_cm:g} cm"
        )

        # Mark the analytical maximum-power load.
        i_power = int(np.argmin(np.abs(RL - c["RL_power_max"])))
        ax.plot(
            RL[i_power], c["PL"][i_power],
            marker="x",
            linestyle="none",
            markersize=9,
            markeredgewidth=2,
            color=SHADES[d_cm],
            label=f"Power optimum, {d_cm:g} cm"
        )

    ax.set_xscale("log")
    ax.set_xlabel(r"Load resistance $R_L$ ($\Omega$)")
    ax.set_ylabel(r"Load power $P_L$ (W)")
    ax.set_title("Received Power versus Load Resistance")
    ax.grid(True, which="both", alpha=0.25)
    ax.legend(fontsize=8, ncol=2)

    secondary = ax.secondary_xaxis(
        "top",
        functions=(
            lambda load: load / RECTIFIER_FACTOR,
            lambda rdc: rdc * RECTIFIER_FACTOR
        )
    )
    secondary.set_xlabel(
        r"Equivalent rectifier load $R_{DC}=R_L\,\pi^2/8$ ($\Omega$)"
    )

    fig.tight_layout()
    save_fig(fig, "fig_PL_vs_RL")
    plt.close(fig)

    print("Saved figs/fig_eta_vs_RL and figs/fig_PL_vs_RL")
    print("\nAll numerical peak checks passed.")


if __name__ == "__main__":
    main()