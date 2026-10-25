"""Master figure pipeline and consistent poster plot generator (Task C-S3).

Calls `sim.run_ab.main()` to generate all Member A and Member B CSVs and figures
without overwriting their styles or filenames, and then runs Member C's tasks
(`sim.shield`, `sim.run_c_c1`, `sim.run_c_s1_c_v1`) to generate all Member C
CSVs and `fig_c_*` / `fig_*_shield` figures.

Also retains the reusable `read_csv_columns`, `to_float_array`, `load_hand_M_k`,
and `overlay_from_csv` helpers used by C-C1, C-S1, C-S2, and C-V1.

Usage from repo root:
    python -m sim.make_figures
    # or
    python sim/make_figures.py
"""

from pathlib import Path
import sys
import csv
import numpy as np
import matplotlib.pyplot as plt

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from sim import params, style

DATA_DIR = REPO_ROOT / "data"
THEORY_DIR = REPO_ROOT / "theory"
FIG_DIR = REPO_ROOT / "figs"

POSTER_FIGSIZE = (7.2, 4.8)


def apply_poster_rc():
    """Enforce poster-legible font and tick sizes on top of sim/style.py."""
    plt.rcParams.update({
        "figure.figsize": POSTER_FIGSIZE,
        "font.size": 14,
        "axes.labelsize": 15,
        "axes.titlesize": 15,
        "xtick.labelsize": 13,
        "ytick.labelsize": 13,
        "legend.fontsize": 12,
        "lines.linewidth": 2.2,
        "lines.markersize": 7,
    })


def read_csv_columns(csv_path):
    """Read a numeric/string CSV into a dict of column lists."""
    with open(csv_path, mode="r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        cols = {name: [] for name in (reader.fieldnames or [])}
        for row in reader:
            for k, v in row.items():
                cols[k].append(v)
    return cols


def to_float_array(values):
    """Convert a list of string values to a NumPy float array (empty -> NaN)."""
    out = []
    for v in values:
        try:
            out.append(float(v))
        except (ValueError, TypeError):
            out.append(np.nan)
    return np.array(out, dtype=float)


def load_hand_M_k():
    """Extract analytical (d_cm, M_uH, k) arrays from theory/hand_values.csv."""
    path = THEORY_DIR / "hand_values.csv"
    if not path.exists():
        return None
    cols = read_csv_columns(path)
    m_dict, k_dict = {}, {}
    for q, val in zip(cols["quantity"], cols["value"]):
        if q.startswith("M_d") and q.endswith("cm"):
            d_cm = float(q[len("M_d"):-len("cm")])
            m_dict[d_cm] = float(val) * 1e6  # H -> uH
        elif q.startswith("k_d") and q.endswith("cm"):
            d_cm = float(q[len("k_d"):-len("cm")])
            k_dict[d_cm] = float(val)
    d_sorted = np.array(sorted(m_dict.keys()), dtype=float)
    M_uH = np.array([m_dict[d] for d in d_sorted], dtype=float)
    k_val = np.array([k_dict[d] for d in d_sorted], dtype=float)
    return d_sorted, M_uH, k_val


def overlay_from_csv(
    ax,
    x_col,
    y_col,
    xlabel,
    ylabel,
    title=None,
    theory_data=None,
    sim_csv=None,
    meas_csv=None,
    y_scale=1.0,
    sim_label="Simulation",
    theory_label="Analytical theory",
    meas_label="Measured",
    yerr_col=None,
):
    """Reusable helper to overlay theory, simulation, and measurement on one axis."""
    theory_tuple = None
    if theory_data is not None:
        theory_tuple = (theory_data[0], theory_data[1], theory_label)

    sim_tuple = None
    if sim_csv is not None and Path(sim_csv).exists():
        scols = read_csv_columns(sim_csv)
        if x_col in scols and y_col in scols:
            sx = to_float_array(scols[x_col])
            sy = to_float_array(scols[y_col]) * y_scale
            sim_tuple = (sx, sy, sim_label)

    meas_list = []
    if meas_csv is not None and Path(meas_csv).exists():
        mcols = read_csv_columns(meas_csv)
        if x_col in mcols and y_col in mcols and len(mcols[x_col]) > 0:
            mx = to_float_array(mcols[x_col])
            my = to_float_array(mcols[y_col]) * y_scale
            valid = ~np.isnan(mx) & ~np.isnan(my)
            if np.any(valid):
                if yerr_col and yerr_col in mcols:
                    yerr = to_float_array(mcols[yerr_col])[valid] * y_scale
                    ax.errorbar(
                        mx[valid], my[valid], yerr=yerr,
                        label=meas_label, capsize=4, **style.MEAS
                    )
                else:
                    meas_list.append((mx[valid], my[valid], meas_label, "o"))

    style.overlay(ax, theory=theory_tuple, sim=sim_tuple, meas=meas_list)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    if title:
        ax.set_title(title)


def make_shield_figures():
    """Generate fig_k_vs_gap_shield and fig_loss_vs_gap_shield from data/sim_shield.csv."""
    sh_path = DATA_DIR / "sim_shield.csv"
    if not sh_path.exists():
        print("[skip] data/sim_shield.csv not found (run `python -m sim.shield` first).")
        return []

    cols = read_csv_columns(sh_path)
    g_mm = to_float_array(cols["gap_mm"])
    d_cm = to_float_array(cols["d_cm"])
    k_no = to_float_array(cols["k_air"])
    k_al = to_float_array(cols["k_al"])
    k_fe = to_float_array(cols["k_ferrite"])
    dR_al = to_float_array(cols["dR_al_mOhm"])
    dR_cu = to_float_array(cols["dR_cu_mOhm"])

    mask = np.isclose(d_cm, 3.0)
    if not np.any(mask):
        mask = np.ones_like(d_cm, dtype=bool)

    generated = []

    # 1. k vs shield gap g
    fig, ax = plt.subplots()
    ax.axhline(k_no[mask][0], color="black", linestyle=":", linewidth=2, label="Free space (no plate)")
    ax.plot(g_mm[mask], k_fe[mask], color="tab:blue", linestyle="-", marker="s",
            label="With ferrite backing (μr = 2000)")
    ax.plot(g_mm[mask], k_al[mask], color="tab:orange", linestyle="--", marker="o",
            label="With Al/Cu metal plate (image limit)")
    ax.set_xlabel("Plate-to-secondary gap g [mm]")
    ax.set_ylabel("Coupling coefficient k [-]")
    ax.set_title("Effect of Metal Shield and Ferrite Backing on Coupling (d = 3 cm)")
    ax.legend()
    style.save_fig(fig, "fig_k_vs_gap_shield")
    plt.close(fig)
    generated.append("fig_k_vs_gap_shield")

    # 2. Eddy loss / added resistance vs gap g
    fig, ax = plt.subplots()
    ax.plot(g_mm[mask], dR_al[mask], color="tab:blue", linestyle="-", marker="o",
            label="Aluminium plate (σ = 3.5×10⁷ S/m)")
    ax.plot(g_mm[mask], dR_cu[mask], color="tab:orange", linestyle="--", marker="s",
            label="Copper plate (σ = 5.8×10⁷ S/m)")
    ax.set_xlabel("Plate-to-secondary gap g [mm]")
    ax.set_ylabel("Reflected eddy resistance ΔR [mΩ] ( ≡ 2 P_plate at 1 A pk)")
    ax.set_title("Conducting Plate Eddy-Current Loss vs. Gap at f₀ = 500 kHz")
    ax.legend()
    style.save_fig(fig, "fig_loss_vs_gap_shield")
    plt.close(fig)
    generated.append("fig_loss_vs_gap_shield")

    return generated


def main():
    # 1. Run all Member A and Member B scripts via run_ab so A/B figures use their exact generators
    from sim import run_ab
    run_ab.main()

    # 2. Run all Member C figure & table generators (using non-clashing fig_c_* and *_shield names)
    from sim import shield, run_c_c1, run_c_s1_c_v1
    print(f"\n{'=' * 70}\n[C-S2] python -m sim.shield\n{'=' * 70}")
    shield.main()
    print(f"\n{'=' * 70}\n[C-T1 & C-C1] python -m sim.run_c_c1\n{'=' * 70}")
    run_c_c1.main()
    print(f"\n{'=' * 70}\n[C-S1 & C-V1] python -m sim.run_c_s1_c_v1\n{'=' * 70}")
    run_c_s1_c_v1.main()
    print("\nmake_figures.py finished: all Member A, B, and C figures generated without name clashes.")


if __name__ == "__main__":
    main()