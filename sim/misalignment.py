"""Lateral misalignment: signed M(dx), k(dx) and eta_link(dx) for the coil pair.

The secondary sits at axial spacing d and is shifted sideways by dx along x.
M is computed with the same Neumann segment sum as A-S1 (sim/coupling.py):
    M = (mu0 / 4 pi) sum_i sum_j (dl_i . dl_j) / |r_i - r_j|
It is SIGNED: M < 0 means the net flux of the primary through the secondary has reversed.
    k = M / sqrt(L1 L2)
Efficiency and load power at f0 from Member B's phasor solver sim/circuit.py solve(...):
    (Z1 + Rs) I1 + j w M I2 = Vs,   j w M I1 + Z2 I2 = 0
    eta_link = P_L / P_in,  P_L = |I2|^2 R_L / 2
At f0 this equals the closed form
    eta_link = [w0^2 M^2 / (R1 (R2 + R_L) + w0^2 M^2)] * [R_L / (R2 + R_L)]   (checked in tests).
The circuit uses the design L, C, R, Vs, Rs from params.py (same values as B's scripts);
k uses the inductance from sim/coupling.py coil_inductances().
Two fixed loads are compared:
  "opt0"  : R_L = R_L,opt at dx = 0 for each d (CONVENTIONS.md default)
  "team"  : R_L = sim.link.fixed_load() (the load B uses for eta(d), P_L(d))

Run from the project root:  python -m sim.misalignment
"""

import csv
from pathlib import Path

import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import brentq

from sim import params
from sim.analytic import coupling
from sim.coupling import mutual_coaxial, coil_inductances
from sim.circuit import solve, RL_opt
from sim.link import fixed_load
from sim.style import SIM, save_fig

ROOT = Path(__file__).resolve().parent.parent
D_LIST = params.d_misalign                           # axial spacings for this task [m]
DX = np.arange(-params.dx_max, params.dx_max + 1e-9, 0.25e-2)   # lateral offsets [m], symmetric about 0
LINESTYLES = ["--", "-.", ":"]                       # simulation = orange, one dash style per d
D_STYLE = {int(round(d * 100)): dict(SIM, linestyle=ls) for d, ls in zip(D_LIST, LINESTYLES)}


def mutual_offset(radii, d, dx):
    """Signed M [H] with secondary at axial spacing d and lateral offset dx."""
    return mutual_coaxial(radii, radii, d, x_offset=dx)


def find_zero_crossing(radii, d, dx_grid, M_grid):
    """Return the positive dx [m] where M changes sign, or None."""
    pos = dx_grid >= 0
    x, m = dx_grid[pos], M_grid[pos]
    idx = np.where(np.sign(m[:-1]) != np.sign(m[1:]))[0]
    if len(idx) == 0:
        return None
    i = idx[0]
    return brentq(lambda t: mutual_offset(radii, d, t), x[i], x[i + 1], xtol=1e-6)


def main():
    g = params.get_geometry()
    c = params.get_circuit()
    tag = "PLACEHOLDER GEOMETRY" if g["placeholder"] else "design geometry"
    radii = g["radii"]
    L1, L2, L_src = coil_inductances(g)                # for k
    f0, R1, R2 = c["f0"], c["R1"], c["R2"]
    circ = dict(L1=params.L1, L2=params.L2, C1=params.C1, C2=params.C2,
                R1=R1, R2=R2, Vs=params.Vs, Rs=params.Rs)  # circuit values, as in B's scripts
    RL_team = fixed_load()
    print(f"=== A-S2 lateral misalignment ({tag}) ===")
    print(f"k uses L1 = L2 = {L1*1e6:.4f} uH ({L_src}); circuit uses params L = {params.L1*1e6:.4f} uH, "
          f"C = {params.C1*1e9:.4f} nF")
    print(f"f0 = {f0/1e3:.0f} kHz, R1 = {R1} ohm, R2 = {R2} ohm, Vs = {params.Vs} V peak, Rs = {params.Rs} ohm"
          f"{' (PLACEHOLDER circuit values)' if c['placeholder'] else ''}")
    print(f"Efficiency from sim/circuit.py solve(); team fixed load R_L = {RL_team:.3f} ohm")

    results = {}
    for d in D_LIST:
        M = np.array([mutual_offset(radii, d, dx) for dx in DX])
        k = coupling(M, L1, L2)
        i0 = np.argmin(np.abs(DX))
        loads = {"opt0": float(RL_opt(M[i0], f0, R1, R2)), "team": RL_team}
        sol = {key: solve(f0, M, circ["L1"], circ["L2"], circ["C1"], circ["C2"], R1, R2, RL,
                          circ["Vs"], Rs=circ["Rs"]) for key, RL in loads.items()}
        dx0 = find_zero_crossing(radii, d, DX, M)
        results[d] = dict(M=M, k=k, loads=loads, sol=sol, dx0=dx0,
                          eta=sol["opt0"].eta, RL=loads["opt0"])

        print(f"\n--- d = {d*100:.0f} cm ---")
        # Validation 1: dx = 0 must reproduce A-S1 exactly (same function, no offset)
        M_as1 = mutual_coaxial(radii, radii, d)
        print(f"dx = 0: M = {M[i0]*1e6:.6f} uH, A-S1 coaxial M = {M_as1*1e6:.6f} uH, "
              f"rel diff = {abs(M[i0]-M_as1)/M_as1:.1e}")
        # Validation 2: symmetry M(+dx) = M(-dx)
        asym = np.max(np.abs(M - M[::-1])) / np.max(np.abs(M))
        print(f"symmetry: max |M(dx) - M(-dx)| / max|M| = {asym:.1e}")
        # Validation 3: |k| <= 1
        print(f"max |k| = {np.max(np.abs(k)):.4f}  (must be <= 1)")
        for key, RL in loads.items():
            print(f"R_L [{key}] = {RL:.3f} ohm: eta(dx=0) = {100*sol[key].eta[i0]:.2f} %, "
                  f"P_L(dx=0) = {sol[key].PL[i0]:.3f} W")
        if dx0 is not None:
            print(f"M changes sign at dx = {dx0*100:.3f} cm  (minimum M = {M.min()*1e6:.4f} uH "
                  f"at dx = {abs(DX[np.argmin(M)])*100:.2f} cm)")
        else:
            print("M does not change sign for |dx| <= 10 cm")
        print(f"{'dx [cm]':>8} {'M [uH]':>10} {'k':>9} {'eta opt0 %':>11} {'eta team %':>11} "
              f"{'PL team W':>10} {'|I1| A':>7}")
        for dxv in [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10]:
            j = np.argmin(np.abs(DX - dxv * 1e-2))
            st = sol["team"]
            print(f"{dxv:8.0f} {M[j]*1e6:10.4f} {k[j]:9.5f} {100*sol['opt0'].eta[j]:11.2f} "
                  f"{100*st.eta[j]:11.2f} {st.PL[j]:10.4f} {abs(st.I1[j]):7.2f}")

    # --- CSV (dx >= 0 only, as specified 0..10 cm) ---
    out = ROOT / "data" / "sim_misalign.csv"
    with open(out, "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["d_cm", "dx_cm", "M_H", "k"])
        for d in D_LIST:
            r = results[d]
            for dx, Mi, ki in zip(DX, r["M"], r["k"]):
                if dx >= -1e-12:
                    w.writerow([f"{d*100:g}", f"{dx*100:.2f}", f"{Mi:.6e}", f"{ki:.6f}"])
    print(f"\nWrote {out.relative_to(ROOT)}")

    out = ROOT / "data" / "sim_eta_dx.csv"
    with open(out, "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["d_cm", "dx_cm", "load_rule", "RL_ohm", "eta_link", "PL_W", "I1_A_peak"])
        for d in D_LIST:
            r = results[d]
            for key, RL in r["loads"].items():
                st = r["sol"][key]
                for j, dx in enumerate(DX):
                    if dx >= -1e-12:
                        w.writerow([f"{d*100:g}", f"{dx*100:.2f}", key, f"{RL:.4f}",
                                    f"{st.eta[j]:.6f}", f"{st.PL[j]:.6e}", f"{abs(st.I1[j]):.5f}"])
    print(f"Wrote {out.relative_to(ROOT)}")

    # --- Figure: signed M, |M| and k vs dx ---
    dx_cm = DX * 100
    k_per_uH = 1e-6 / np.sqrt(L1 * L2)                 # k = M / sqrt(L1 L2), M in uH
    fig, (axa, axb) = plt.subplots(1, 2, figsize=(13, 5))
    for d in D_LIST:
        r, lab = results[d], f"Simulation, d = {d*100:.0f} cm"
        st = D_STYLE[int(round(d * 100))]
        axa.plot(dx_cm, r["M"] * 1e6, label=lab, **st)
        axb.plot(dx_cm, np.abs(r["M"]) * 1e6, label=lab, **st)
        if r["dx0"] is not None:
            for s in (-1, 1):
                axa.plot(s * r["dx0"] * 100, 0, "o", color="tab:orange", mfc="white", ms=8)
    axa.axhline(0, color="gray", lw=1)
    axa.set_ylim(top=1.3 * max(np.max(results[d]["M"]) for d in D_LIST) * 1e6)   # room for legend
    axa.set_title("Signed $M$ (sign change = flux reversal)")
    axa.set_ylabel(r"Signed mutual inductance $M$ ($\mu$H)")
    axb.set_yscale("log")
    axb.set_title("Magnitude $|M|$ and $|k|$")
    axb.set_ylabel(r"$|M|$ ($\mu$H)")
    sec = axb.secondary_yaxis("right", functions=(lambda m: m * k_per_uH, lambda kk: kk / k_per_uH))
    sec.set_ylabel(r"$|k|$")
    for ax, loc in ((axa, "upper left"), (axb, "lower center")):   # legends in empty regions
        ax.set_xlabel(r"Lateral offset $\Delta x$ (cm)")
        ax.legend(loc=loc, fontsize=12)
    if g["placeholder"]:
        fig.suptitle("PLACEHOLDER GEOMETRY", color="red")
    fig.tight_layout()
    for p in save_fig(fig, "fig_k_vs_dx"):
        print(f"Saved {p.relative_to(ROOT)}")
    plt.close(fig)

    # --- Figures: eta and P_L vs dx, one panel per load rule ---
    panel_title = {"opt0": r"$R_L = R_{L,opt}(\Delta x = 0)$ for each $d$",
                   "team": f"Team fixed load $R_L$ = {RL_team:.2f} $\\Omega$"}
    for name, ylabel, getter, ylim in [
            ("fig_eta_vs_dx", r"Link efficiency $\eta_{link}$ (%)", lambda st: 100 * st.eta, (0, 100)),
            ("fig_PL_vs_dx", f"Load power $P_L$ (W), $V_s$ = {params.Vs:g} V peak", lambda st: st.PL, None)]:
        fig, axes = plt.subplots(1, 2, figsize=(13, 5.5), sharey=True)
        for ax, key in zip(axes, ["opt0", "team"]):
            for d in D_LIST:
                r = results[d]
                lab = f"d = {d*100:.0f} cm" + (f", $R_L$ = {r['loads'][key]:.2f} $\\Omega$" if key == "opt0" else "")
                ax.plot(dx_cm, getter(r["sol"][key]), label=lab, **D_STYLE[int(round(d * 100))])
            ax.set_title(panel_title[key], fontsize=13)
            ax.set_xlabel(r"Lateral offset $\Delta x$ (cm)")
            ax.legend(loc="upper left" if name == "fig_PL_vs_dx" else "lower center", fontsize=12)
        axes[0].set_ylabel(ylabel)
        if ylim:
            axes[0].set_ylim(*ylim)
        sup = "Circuit solver (sim/circuit.py) at $f_0$"
        if name == "fig_PL_vs_dx":
            sup += f", source $R_s$ = {params.Rs:g} $\\Omega$: $P_L$ peaks where $k$ falls to $k_c$"
        if g["placeholder"]:
            sup = "PLACEHOLDER GEOMETRY — " + sup
        fig.suptitle(sup, fontsize=14)
        fig.tight_layout()
        for p in save_fig(fig, name):
            print(f"Saved {p.relative_to(ROOT)}")
        plt.close(fig)
    return results


if __name__ == "__main__":
    main()
