"""Common plot style for all Member A figures.

Fixed conventions (CONVENTIONS.md Section 2):
    theory      = blue solid line
    simulation  = orange dashed line
    measurement = black markers
Font size >= 14 pt, line width 2, every axis labelled with units, legend on every plot.
save_fig(fig, name) writes figs/<name>.pdf (vector) and figs/<name>.png (300 dpi).
"""

from pathlib import Path

import matplotlib
matplotlib.use("Agg")          # headless: only save files, never need a display
import matplotlib.pyplot as plt

FIG_DIR = Path(__file__).resolve().parent.parent / "figs"

plt.rcParams.update({
    "font.size": 14,
    "axes.labelsize": 14,
    "axes.titlesize": 15,
    "xtick.labelsize": 14,
    "ytick.labelsize": 14,
    "legend.fontsize": 13,
    "lines.linewidth": 2,
    "lines.markersize": 7,
    "axes.grid": True,
    "grid.alpha": 0.3,
    "figure.figsize": (7, 5),
    "savefig.bbox": "tight",
})

# Keyword dicts to pass straight into ax.plot(...)
THEORY = dict(color="tab:blue", linestyle="-", linewidth=2)
SIM = dict(color="tab:orange", linestyle="--", linewidth=2)
MEAS = dict(color="black", linestyle="none", marker="o", markersize=7)


def save_fig(fig, name):
    """Save a figure as figs/<name>.pdf and figs/<name>.png (300 dpi). Returns both paths."""
    FIG_DIR.mkdir(parents=True, exist_ok=True)
    pdf = FIG_DIR / f"{name}.pdf"
    png = FIG_DIR / f"{name}.png"
    fig.savefig(pdf, metadata={"CreationDate": None})   # no timestamp: reruns give identical files in git
    fig.savefig(png, dpi=300)
    return pdf, png


def overlay(ax, theory=None, sim=None, meas=None):
    """Plot theory / simulation / measurement on one axis in the fixed project styles.

    theory, sim: (x, y, label) tuples or None.
    meas: list of (x, y, label, marker) tuples (one per measurement method) or None/empty.
    """
    if theory is not None:
        ax.plot(theory[0], theory[1], label=theory[2], **THEORY)
    if sim is not None:
        ax.plot(sim[0], sim[1], label=sim[2], **SIM)
    for x, y, label, marker in (meas or []):
        ax.plot(x, y, label=label, **dict(MEAS, marker=marker))
    ax.legend()
