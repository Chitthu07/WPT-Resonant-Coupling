"""C-P1: Section 6 validation-chain figure, figs/fig_c_p1_validation_chain.{pdf,png} (13.85 x 2.75 in).

(a) model chain: series-series circuit as blocks, and closed form <-> Python solver <-> LTspice.
(b) P_L(f) at d = 2, 5, 10 cm, R_L = 6 ohm, Vs = 5 V pk, Rs = 0:
      closed form  P_L = 1/2 R_L |I2|^2,  I2 = -j w M Vs / (Z1 Z2 + w^2 M^2)        (blue solid)
      Python 2x2 phasor solver sim/circuit.solve                                    (orange dashed)
    LTspice (black markers) from data/ltspice_ac.csv (python -m sim.compare_ltspice --run), P_L = 1/2 R_L |I2|^2;
    plotted only if it matches the solver at the current params (otherwise the legend says 'rerun pending').
(c) transient at d = 5 cm, from the coupled-circuit ODEs (Python, orange; LTspice later):
      L1 i1' + M i2' = vs(t) - R1 i1 - q1/C1,   M i1' + L2 i2' = -(R2 + R_L) i2 - q2/C2,   q' = i
    with vs = Vs sin(w0 t) switched on at t = 0; right: steady-state zoom showing i2 lagging i1 by T0/4.
All values from sim/params.py and sim/link.py. Run from the project root:  python poster/make_c_p1_figure.py
"""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager
from matplotlib.lines import Line2D
from matplotlib.patches import FancyBboxPatch
from scipy.integrate import solve_ivp

from sim import params
from sim.circuit import solve
from sim.link import M_of_d
from sim.style import save_fig

SIZE = (13.85, 2.75)                                   # S6 figure slot [in]
WIDTHS = (4.2, 5.45, 4.2)                              # panel widths (a), (b), (c) [in]
BLUES = {2: "#08306b", 5: "#2171b5", 10: "#6baed6"}    # theory, dark = 2 cm ... light = 10 cm
ORANGES = {2: "#7f2704", 5: "#d94801", 10: "#fd8d3c"}  # simulation, same shades as Section 5
NAVY, WINE = "#1B2A4A", "#9B1D3A"
for _f in Path("/usr/share/fonts/truetype/crosextra").glob("Carlito-*.ttf"):   # Calibri-metric font for matplotlib
    font_manager.fontManager.addfont(str(_f))
RC = {"font.family": "Carlito", "font.size": 18, "axes.labelsize": 20, "xtick.labelsize": 18,
      "ytick.labelsize": 18, "legend.fontsize": 16, "lines.linewidth": 2.5, "axes.grid": True, "grid.alpha": 0.3,
      "savefig.bbox": "standard"}                      # keep the exact slot size (no tight bbox)


def pl_closed_form(f, M, RL):
    """Load power from the explicit mesh solution (no matrix solver)."""
    w = 2 * np.pi * f
    Z1 = params.R1 + 1j * w * params.L1 + 1 / (1j * w * params.C1) + params.Rs
    Z2 = params.R2 + RL + 1j * w * params.L2 + 1 / (1j * w * params.C2)
    I2 = -1j * w * M * params.Vs / (Z1 * Z2 + (w * M) ** 2)
    return 0.5 * RL * np.abs(I2) ** 2


def transient(M, RL, t_end, n_per_period=200):
    """i1(t), i2(t) [A] after switching on Vs sin(w0 t) at t = 0."""
    L1, L2, C1, C2, R1, R2 = params.L1, params.L2, params.C1, params.C2, params.R1, params.R2
    w0 = 2 * np.pi * params.f0
    Linv = np.linalg.inv(np.array([[L1, M], [M, L2]]))
    def rhs(t, y):
        q1, i1, q2, i2 = y
        v = np.array([params.Vs * np.sin(w0 * t) - R1 * i1 - q1 / C1, -(R2 + RL) * i2 - q2 / C2])
        di1, di2 = Linv @ v
        return [i1, di1, i2, di2]
    T0 = 1 / params.f0
    t = np.arange(0, t_end, T0 / n_per_period)
    sol = solve_ivp(rhs, (0, t_end), [0, 0, 0, 0], t_eval=t, rtol=1e-9, atol=1e-12, max_step=T0 / 50)
    return sol.t, sol.y[1], sol.y[3]


def phase_lag_deg(t, a, b, f):
    """Phase of b relative of a [deg] from a least-squares fit over the given samples."""
    w = 2 * np.pi * f
    X = np.column_stack([np.cos(w * t), np.sin(w * t)])
    ca, cb = (np.linalg.lstsq(X, y, rcond=None)[0] for y in (a, b))
    pa, pb = np.angle(ca[0] - 1j * ca[1]), np.angle(cb[0] - 1j * cb[1])
    return np.degrees(np.angle(np.exp(1j * (pb - pa))))


def box(ax, x, y, w, h, text, edge, size=15, lw=2.5):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.0,rounding_size=0.03",
                                fc="white", ec=edge, lw=lw, transform=ax.transAxes, clip_on=False))
    ax.text(x + w / 2, y + h / 2, text, ha="center", va="center", fontsize=size, transform=ax.transAxes)


def panel_a(ax, rl):
    ax.axis("off")
    ax.set_xlim(0, 1); ax.set_ylim(0, 1)
    # top: the two series loops as blocks, coupled by M, k
    box(ax, 0.01, 0.62, 0.40, 0.26, "$V_s$ – $C_1$ – $R_1$ – $L_1$", NAVY, size=13, lw=2)
    box(ax, 0.58, 0.62, 0.41, 0.26, "$L_2$ – $C_2$ – $R_2$ – $R_L$", NAVY, size=13, lw=2)
    ax.annotate("", xy=(0.575, 0.75), xytext=(0.415, 0.75), arrowprops=dict(arrowstyle="<->", color=WINE, lw=2.5))
    ax.text(0.495, 0.90, "$M, k$", ha="center", fontsize=16, color=WINE)
    # bottom: validation chain
    for x, text, edge in ((0.01, "Closed form\nA-C1, B-T2,\nC-C1", BLUES[5]),
                          (0.355, "Python\nsolver\nA-S1, B-S1", ORANGES[5]),
                          (0.70, "LTspice\nwpt.asc\nC-S1, B-V1", "black")):
        box(ax, x, 0.06, 0.29, 0.44, text, edge, size=12)
    for xc in (0.3275, 0.6725):
        ax.text(xc, 0.28, "↔", ha="center", va="center", fontsize=20, fontweight="bold")
    if not ltspice_current():
        ax.text(0.845, -0.06, f"rerun at R = {params.R1:g} Ω pending", ha="center", fontsize=11, style="italic")


MARKERS = {2: "o", 5: "s", 10: "^"}
D_OF_K = {0.321109: 2, 0.111189: 5, 0.029895: 10}                  # .step k values in sim/wpt.asc


def ltspice_points(rl):
    """{d: (f_kHz, P_L)} from data/ltspice_ac.csv, or {} if missing or not made at the current params."""
    import pandas as pd
    path = ROOT / "data" / "ltspice_ac.csv"
    if not path.exists():
        return {}
    df = pd.read_csv(path)
    out = {}
    for k, g in df.groupby("k"):
        d = D_OF_K.get(round(k, 6))
        if d is None:
            continue
        f = g.f_Hz.to_numpy()
        pl = 0.5 * rl * (g.I2_re ** 2 + g.I2_im ** 2).to_numpy()
        ref = solve(f, k * np.sqrt(params.L1 * params.L2), params.L1, params.L2, params.C1, params.C2,
                    params.R1, params.R2, rl, params.Vs, Rs=params.Rs).PL
        if np.max(np.abs(pl - ref) / ref) > 1e-3:      # LTspice made with other R (C differs by 4e-6 only)
            return {}
        out[d] = (f / 1e3, pl)
    return out


def ltspice_current():
    return bool(ltspice_points(params.RL_fixed))


def panel_b(ax, rl):
    f = np.linspace(350e3, 650e3, 3001)
    for d in (2, 5, 10):
        M = M_of_d(d)
        ax.plot(f / 1e3, pl_closed_form(f, M, rl), color=BLUES[d], ls="-", lw=3, label=f"{d} cm closed form")
        ax.plot(f / 1e3, solve(f, M, params.L1, params.L2, params.C1, params.C2, params.R1, params.R2,
                               rl, params.Vs, Rs=params.Rs).PL, color=ORANGES[d], ls="--", lw=2.2, label=f"{d} cm solver")
    lt = ltspice_points(rl)
    for d, (fk, pl) in lt.items():
        step = 100                                        # every 10 kHz
        ax.plot(fk[::step], pl[::step], ls="none", marker=MARKERS[d], color="black", ms=6, mfc="none", mew=1.4, zorder=5)
    for fx in (474.4, 530.3):                             # light-load peaks at 5 cm (data/val_split_peaks.csv)
        ax.axvline(fx, color="gray", ls=":", lw=1.8)
    ax.text(536, 3.3, "light-load $f_\\pm$\n(5 cm)", ha="left", color="gray", fontsize=13)
    for d, (x, y) in {2: (437, 1.95), 5: (563, 1.95), 10: (512, 5.7)}.items():
        ax.text(x, y, f"{d} cm", color=BLUES[d], fontsize=14, fontweight="bold", ha="left" if d == 10 else "center")
    keys = [Line2D([], [], color=BLUES[5], lw=3, label="closed form"),
            Line2D([], [], color=ORANGES[5], lw=2.2, ls="--", label="solver"),
            Line2D([], [], color="black", marker="o", mfc="none", ls="none",
                   label="LTspice" if lt else "LTspice (rerun pending)")]
    ax.legend(handles=keys, loc="upper left", fontsize=12, framealpha=0.9, handlelength=1.8)
    ax.set_xlabel("f (kHz)")
    ax.set_ylabel("$P_L$ (W)")
    ax.set_xlim(350, 650)


def panel_c(fig, spec, rl):
    M = M_of_d(5)
    T0 = 1 / params.f0
    t, i1, i2 = transient(M, rl, 80 * T0)
    zoom = t > t[-1] - 4e-6
    lag = phase_lag_deg(t[zoom], i1[zoom], i2[zoom], params.f0)
    sub = spec.subgridspec(1, 2, width_ratios=[1.25, 1], wspace=0.08)
    a1 = fig.add_subplot(sub[0])
    a1.plot(t * 1e6, i1, color=ORANGES[2], lw=1.0, label="$i_1$")
    a1.plot(t * 1e6, i2, color=ORANGES[10], lw=1.0, ls="--", label="$i_2$")
    a1.set_xlabel("t (µs)")
    a1.set_ylabel("i (A)")
    a1.legend(loc="lower right", fontsize=13, framealpha=0.9)
    a2 = fig.add_subplot(sub[1], sharey=a1)
    tz = (t[zoom] - t[zoom][0]) * 1e6
    a2.plot(tz, i1[zoom], color=ORANGES[2], lw=2.5)
    a2.plot(tz, i2[zoom], color=ORANGES[10], lw=2.5, ls="--")
    a2.tick_params(labelleft=False)
    a2.set_xlabel("t (µs)")
    # bracket between an upward zero crossing of i1 and the next one of i2
    def up(y):                                       # upward zero crossings, linearly interpolated [us]
        k = np.where((y[:-1] < 0) & (y[1:] >= 0))[0]
        return tz[k] - y[k] * (tz[k + 1] - tz[k]) / (y[k + 1] - y[k])
    c1 = up(i1[zoom])[1]                             # second crossing, away from the axis edge
    c2 = up(i2[zoom])[up(i2[zoom]) > c1][0]
    ya = 1.15 * np.max(np.abs(i1[zoom]))
    a2.annotate("", xy=(c2, ya), xytext=(c1, ya), arrowprops=dict(arrowstyle="|-|,widthA=0.3,widthB=0.3", lw=2, color="black"))
    a2.text(c2 + 0.15, ya, "$T_0/4$", ha="left", va="center", fontsize=14)
    for c in (c1, c2):
        a2.axvline(c, color="gray", lw=1, ls=":")
    a2.set_ylim(-1.35 * np.max(np.abs(i1)), 1.35 * np.max(np.abs(i1)))
    return a1, lag, (c2 - c1)


def main():
    rl = params.RL_fixed
    with plt.rc_context(RC):
        fig = plt.figure(figsize=SIZE)
        gs = fig.add_gridspec(1, 3, width_ratios=WIDTHS, left=0.012, right=0.995, bottom=0.25, top=0.88, wspace=0.24)
        axa = fig.add_subplot(gs[0])
        panel_a(axa, rl)
        axb = fig.add_subplot(gs[1])
        panel_b(axb, rl)
        a1, lag, dt = panel_c(fig, gs[2], rl)
        for ax, letter in ((axa, "(a)"), (axb, "(b)"), (a1, "(c)")):
            ax.text(-0.01 if ax is axa else -0.26, 1.04, letter, transform=ax.transAxes, fontsize=22,
                    fontweight="bold", va="bottom", ha="left")
        pdf, png = save_fig(fig, "fig_c_p1_validation_chain")
        plt.close(fig)
    print(f"R1 = R2 = {params.R1} ohm, R_L = {rl} ohm, d = 5 cm transient")
    print(f"steady-state phase of i2 relative to i1 = {lag:.3f} deg (expect -90); zero-crossing gap = {dt:.4f} us (T0/4 = {1e6/(4*params.f0):.4f})")
    print(f"Saved {pdf.relative_to(ROOT)}, {png.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
