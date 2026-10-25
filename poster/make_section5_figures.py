"""B-P1: poster figures for Section 5 (Analysis and Simulation), at the exact slot sizes of the template.

Run from the repo root:  python poster/make_section5_figures.py

Writes PNG files at 300 dpi into poster/ (figs/ is not touched):
  fig_s5_k_vs_d.png      6.9 x 5.0 in (2070 x 1500 px)   closed form vs Neumann k(d), log-log
  fig_s5_eta_vs_d.png    6.9 x 5.0 in                     eta_max(d) and eta(d) at the fixed load
  fig_s5_eta_vs_f.png    6.9 x 5.0 in                     eta(f) and normalised P_L(f): splitting
  fig_s5_eta_vs_RL.png   6.9 x 5.0 in                     eta(R_L) with the closed-form optimum
  fig_s5_B_map.png       8.8 x 5.4 in (2640 x 1620 px)   |B| in the x-z plane, d = 3 cm
Fonts are >= 20 pt at printed size (A-P1 Section 1.3), except legends (18 pt).
Every number comes from sim/params.py, data/sim_M_k.csv and the project modules.
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.colors import LogNorm
from matplotlib.ticker import FixedLocator, FuncFormatter, MultipleLocator, NullLocator

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from sim import params
from sim.analytic import coil_mutual, coupling
from sim.circuit import solve, RL_opt, eta_max
from sim.coupling import coil_inductances
from sim.fieldmap import field_on_grid, near_wire_mask, X_RANGE, Z_RANGE, STEP, D_MAP, I1 as I_MAP
from sim.link import M_of_d, fixed_load
from sim.style import THEORY, SIM

OUT = ROOT / "poster"
SLOT = (6.35, 4.6)                      # plot slot in the template [in] (A0 layout, 2026-10-25)
MAP_SLOT = (8.09, 4.97)                 # field-map slot [in]
ORANGES = ["#fd8d3c", "#d94801", "#7f2704"]   # several simulation curves, dark enough to print on white
POSTER_RC = {"font.size": 20, "axes.labelsize": 22, "xtick.labelsize": 20, "ytick.labelsize": 20,
             "legend.fontsize": 18, "lines.linewidth": 3, "savefig.bbox": "standard",
             "figure.constrained_layout.use": True}


def save(fig, name):
    path = OUT / f"{name}.png"
    fig.savefig(path, dpi=300)
    plt.close(fig)
    print(f"  {path.relative_to(ROOT)}")


def fig_k_vs_d():
    g = params.get_geometry()
    L1, L2, _ = coil_inductances(g)
    mk = pd.read_csv(ROOT / "data" / "sim_M_k.csv")
    d_cm, k_num = mk["d_cm"].to_numpy(), mk["k"].to_numpy()
    k_cf = coupling(np.array([coil_mutual(g["radii"], g["radii"], d / 100) for d in d_cm]), L1, L2)
    fig, ax = plt.subplots(figsize=SLOT)
    ax.loglog(d_cm, k_cf, label="Theory (closed form)", **dict(THEORY, linewidth=3))
    ax.loglog(d_cm, k_num, label="Simulation (Neumann)", **dict(SIM, linewidth=3))
    ref = k_num[-1] * (d_cm / d_cm[-1]) ** -3
    keep = ref < 0.6
    ax.loglog(d_cm[keep], ref[keep], color="gray", ls=":", lw=2.5, label=r"$\propto d^{-3}$ (dipole)")
    ax.xaxis.set_major_locator(FixedLocator([0.5, 1, 2, 5, 10]))
    ax.xaxis.set_major_formatter(FuncFormatter(lambda v, _: f"{v:g}")); ax.xaxis.set_minor_locator(NullLocator())
    ax.yaxis.set_major_locator(FixedLocator([0.01, 0.02, 0.05, 0.1, 0.2, 0.5]))
    ax.yaxis.set_major_formatter(FuncFormatter(lambda v, _: f"{v:g}")); ax.yaxis.set_minor_locator(NullLocator())
    ax.set_xlabel("Coil spacing $d$ (cm)"); ax.set_ylabel("Coupling $k$ (–)")
    ax.legend(loc="lower left")
    save(fig, "fig_s5_k_vs_d")
    i1, i10 = np.argmin(np.abs(d_cm - 1)), np.argmin(np.abs(d_cm - 10))
    print(f"    k(1 cm) = {k_num[i1]:.3f}, k(10 cm) = {k_num[i10]:.4f}, "
          f"max |closed form - Neumann| = {100*np.max(np.abs(k_cf - k_num)/k_cf):.3f} %")


def fig_eta_vs_d():
    e = pd.read_csv(ROOT / "data" / "sim_eta_d.csv")
    RL = fixed_load()
    fig, ax = plt.subplots(figsize=SLOT)
    ax.plot(e.d_cm, 100 * e.eta_max, label=r"$\eta_{max}$ at $R_{L,opt}(d)$ (theory)", **dict(THEORY, linewidth=3))
    ax.plot(e.d_cm, 100 * e.eta_fixedRL, label=rf"$R_L$ = {RL:g} $\Omega$ fixed (solver)", **dict(SIM, linewidth=3))
    ax.set_xlim(0, 15); ax.set_ylim(0, 100); ax.xaxis.set_major_locator(MultipleLocator(5))
    ax.set_xlabel("Coil spacing $d$ (cm)"); ax.set_ylabel(r"Link efficiency $\eta_{link}$ (%)")
    ax.legend(loc="lower left")
    save(fig, "fig_s5_eta_vs_d")
    for d in (1, 5, 10):
        r = e[e.d_cm == d].iloc[0]
        print(f"    d = {d:>2} cm: eta_max = {100*r.eta_max:.1f} %, eta(6 ohm) = {100*r.eta_fixedRL:.1f} %")


def fig_eta_vs_f():
    f0, RL = params.f0, fixed_load()
    f = np.linspace(0.75 * f0, 1.35 * f0, 6001)
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=SLOT, sharex=True)
    for d, col in zip((2, 5, 10), ORANGES):
        r = solve(f, M_of_d(d), params.L1, params.L2, params.C1, params.C2, params.R1, params.R2, RL, params.Vs)
        ax1.plot(f / 1e3, 100 * r.eta, color=col, ls="--", lw=3, label=f"{d} cm")
        ax2.plot(f / 1e3, r.PL / r.PL.max(), color=col, ls="--", lw=3)
        k = M_of_d(d) / np.sqrt(params.L1 * params.L2)
        pk = [j for j in range(1, len(f) - 1) if r.PL[j] > r.PL[j - 1] and r.PL[j] >= r.PL[j + 1]
              and r.PL[j] > 0.2 * r.PL.max()]
        print(f"    d = {d:>2} cm (k = {k:.3f}): eta(f0) = {100*r.eta[np.argmin(np.abs(f - f0))]:.1f} %, "
              f"P_L peaks at {np.round(f[pk] / 1e3, 1)} kHz")
    for ax in (ax1, ax2):
        ax.axvline(f0 / 1e3, color="gray", lw=1.5)
    ax1.set_ylabel(r"$\eta_{link}$ (%)"); ax1.set_ylim(0, 100)
    ax2.set_ylabel(r"$P_L/P_{L,max}$"); ax2.set_ylim(0, 1.08)
    ax2.set_xlabel("Frequency $f$ (kHz)")
    fig.legend(*ax1.get_legend_handles_labels(), loc="outside upper center", ncol=3,
               handlelength=1.5, columnspacing=1.2, frameon=False)
    save(fig, "fig_s5_eta_vs_f")


def fig_eta_vs_RL():
    f0, RLfix = params.f0, fixed_load()
    RL = np.logspace(-1, 3, 801)
    fig, ax = plt.subplots(figsize=SLOT)
    for d, col in zip((1, 5, 10), ORANGES):
        M = M_of_d(d)
        r = solve(f0, M, params.L1, params.L2, params.C1, params.C2, params.R1, params.R2, RL, params.Vs)
        ax.plot(RL, 100 * r.eta, color=col, ls="--", lw=3, label=f"{d} cm")
        Ro, em = float(RL_opt(M, f0, params.R1, params.R2)), float(eta_max(M, f0, params.R1, params.R2))
        ax.plot(Ro, 100 * em, "o", color="tab:blue", ms=11, zorder=5,
                label=r"$R_{L,opt}=R_2\sqrt{1+x}$" if d == 1 else None)
        print(f"    d = {d:>2} cm: R_L,opt = {Ro:.2f} ohm, eta_max = {100*em:.1f} %, "
              f"solver max = {100*r.eta.max():.1f} % at {RL[np.argmax(r.eta)]:.2f} ohm")
    ax.axvline(RLfix, color="gray", ls=":", lw=2.5)
    ax.text(RLfix * 1.12, 4, rf"{RLfix:g} $\Omega$", color="gray", fontsize=20)
    ax.set_xscale("log"); ax.set_ylim(0, 100); ax.set_xlim(RL[0], RL[-1])
    ax.xaxis.set_major_formatter(FuncFormatter(lambda v, _: f"{v:g}"))
    ax.set_xlabel(r"Load resistance $R_L$ ($\Omega$)"); ax.set_ylabel(r"$\eta_{link}$ (%)")
    h, l = ax.get_legend_handles_labels()
    order = [i for i, t in enumerate(l) if "cm" in t] + [i for i, t in enumerate(l) if "cm" not in t]
    fig.legend([h[i] for i in order], [l[i] for i in order], loc="outside upper center", ncol=4,
               handlelength=1.2, columnspacing=0.8, handletextpad=0.4, frameon=False)
    save(fig, "fig_s5_eta_vs_RL")


def fig_B_map():
    g = params.get_geometry()
    radii, r_w = g["radii"], g["wire_d"] / 2
    x = np.arange(X_RANGE[0], X_RANGE[1] + STEP / 2, STEP)
    z = np.arange(Z_RANGE[0], Z_RANGE[1] + STEP / 2, STEP)
    x[np.abs(x) < 1e-12] = 0.0
    Bx, Bz = field_on_grid(radii, x, z, I_MAP)
    mask = near_wire_mask(radii, x, z, [0.0], 2 * r_w)
    B = np.ma.array(np.hypot(Bx, Bz) * 1e6, mask=mask)
    vmin, vmax = np.percentile(B.compressed(), [0.5, 99.0])
    fig, ax = plt.subplots(figsize=MAP_SLOT)
    pc = ax.pcolormesh(x * 100, z * 100, B, norm=LogNorm(vmin=vmin, vmax=vmax), cmap="viridis",
                       shading="auto", rasterized=True)
    ax.streamplot(x * 100, z * 100, np.where(mask, np.nan, Bx), np.where(mask, np.nan, Bz),
                  color="white", linewidth=1.0, density=1.3, arrowsize=1.2)
    for zc, col, lab in ((0.0, "red", "Primary, 1 A"), (D_MAP, "orange", f"Secondary, d = {D_MAP*100:g} cm")):
        xs = np.concatenate([-radii, radii]) * 100
        ax.plot(xs, np.full_like(xs, zc * 100), "s", color=col, ms=5, mec="black", mew=0.5, ls="none", label=lab)
    ax.set_aspect("equal"); ax.set_xlim(x[0] * 100, x[-1] * 100); ax.set_ylim(z[0] * 100, z[-1] * 100)
    ax.set_xlabel("$x$ (cm)"); ax.set_ylabel("$z$ (cm)")
    cb = fig.colorbar(pc, ax=ax, shrink=0.9, pad=0.02)
    cb.set_label(r"$|B|$ ($\mu$T), $I_1$ = 1 A")
    ticks = [t for t in (1, 2, 5, 10, 20, 50, 100, 200, 500) if vmin <= t <= vmax]
    cb.set_ticks(ticks); cb.set_ticklabels([f"{t:g}" for t in ticks]); cb.minorticks_off()
    ax.legend(loc="upper right", framealpha=0.9, fontsize=18)
    save(fig, "fig_s5_B_map")
    iz, ix = np.argmin(np.abs(z - D_MAP)), np.argmin(np.abs(x))
    print(f"    |B| at coil-1 centre = {B[np.argmin(np.abs(z)), ix]:.0f} uT, at coil-2 centre = {B[iz, ix]:.0f} uT")


def main():
    with plt.rc_context(POSTER_RC):
        print("Section 5 poster figures:")
        fig_k_vs_d(); fig_eta_vs_d(); fig_eta_vs_f(); fig_eta_vs_RL(); fig_B_map()


if __name__ == "__main__":
    main()
