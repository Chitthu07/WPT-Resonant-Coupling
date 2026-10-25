"""Compare analytical, simulated and measured coil parameters, M(d) and k(d).

Columns of the comparison table:
  Analytical  : L from the Mohan current-sheet formula; M from the coaxial elliptic
                closed form (summed over turn pairs); k = M / L_filament (as in A-C1).
  Simulation  : L from the filament sum; M from the numerical Neumann segment sum (A-S1);
                k = M / sqrt(L1 L2).
  Measured    : taken from sim/params.py ONLY when PARAMS_VERSION == "v2-measured",
                and k / M from data/meas_M_k.csv if that file exists. Otherwise "n/a".
Derived rows use
  resonance        f0 = 1 / (2 pi sqrt(L C))
  unloaded Q       Q  = w0 L / R
  capacitor (if C is not set in params.py): C = 1 / (w0^2 L_filament) at the design f0.
Rows whose difference exceeds FLAG_PCT are listed; causes are NOT guessed here.

Run from the project root:  python -m sim.compare
"""

import csv
from pathlib import Path

import numpy as np
import matplotlib.pyplot as plt

from sim import params
from sim.analytic import coil_mutual, L_filament, L_mohan, spiral_d_in
from sim.coupling import mutual_coaxial
from sim.style import overlay, save_fig

ROOT = Path(__file__).resolve().parent.parent
MEAS_FILE = ROOT / "data" / "meas_M_k.csv"      # columns: d_cm, M_H, k, method  (M_H may be blank)
SIM_FILE = ROOT / "data" / "sim_M_k.csv"        # written by A-S1 (python -m sim.coupling)
FLAG_PCT = 10.0
MARKERS = ["o", "s", "^", "D", "v"]             # one marker shape per measurement method


def pct(a, b):
    """Percent difference of a relative to b, or None if either is missing."""
    if a is None or b is None:
        return None
    return 100 * (a - b) / b


def f_res(L, C):
    """f0 = 1 / (2 pi sqrt(L C)), or None if L or C is missing."""
    return None if L is None or C is None else 1 / (2 * np.pi * np.sqrt(L * C))


def q_unloaded(L, C, R):
    """Q = w0 L / R at the resonator's own f0 = 1/(2 pi sqrt(LC))."""
    f = f_res(L, C)
    return None if f is None or R is None else 2 * np.pi * f * L / R


def load_measured_params():
    """Measured L, R, C from params.py if PARAMS_VERSION says so, else all None."""
    keys = ["L1", "L2", "R1", "R2", "C1", "C2"]
    if params.PARAMS_VERSION != "v2-measured":
        return {k: None for k in keys}
    return {k: getattr(params, k) for k in keys}


def load_measured_k(path=MEAS_FILE):
    """Read measured k (and M) per distance and method. Returns {method: (d_cm, M_H, k)} arrays."""
    if not Path(path).exists():
        return {}
    data = {}
    with open(path) as fh:
        for row in csv.DictReader(fh, skipinitialspace=True):
            m = row.get("method", "").strip() or "LCR"
            M = float(row["M_H"]) if row.get("M_H", "").strip() else np.nan
            data.setdefault(m, []).append((float(row["d_cm"]), M, float(row["k"])))
    return {m: tuple(np.array(c) for c in zip(*sorted(v))) for m, v in data.items()}


def build_table(meas_params, meas_k):
    """Return (rows, info): rows = list of dicts quantity/unit/analytical/simulation/measured/diffs."""
    g = params.get_geometry()
    c = params.get_circuit()
    radii, r_w = g["radii"], g["wire_d"] / 2
    d_in = params.d_in if (params.d_in is not None and not g["placeholder"]) else spiral_d_in(radii, g["wire_d"])

    L_an = L_mohan(g["N"], g["d_out"], d_in)
    L_sim = L_filament(radii, r_w)
    w0 = 2 * np.pi * c["f0"]
    # C is a component value, not a model: use params.py if set, else derive C = 1/(w0^2 L_fil)
    c_derived = params.C1 is None or params.C2 is None
    C_design = {"C1": params.C1 if params.C1 is not None else 1 / (w0 ** 2 * L_sim),
                "C2": params.C2 if params.C2 is not None else 1 / (w0 ** 2 * L_sim)}

    R = {"R1": c["R1"], "R2": c["R2"]}
    an = {"L1": L_an, "L2": L_an, "R1": R["R1"], "R2": R["R2"], **C_design}
    sim = {"L1": L_sim, "L2": L_sim, "R1": None, "R2": None, **C_design}
    ms = {k: meas_params.get(k) for k in ["L1", "L2", "R1", "R2", "C1", "C2"]}   # missing -> None
    for col in (an, sim, ms):
        col["f01"] = f_res(col["L1"], col["C1"])
        col["f02"] = f_res(col["L2"], col["C2"])
        col["Q1"] = q_unloaded(col["L1"], col["C1"], col["R1"] if col["R1"] is not None else R["R1"])
        col["Q2"] = q_unloaded(col["L2"], col["C2"], col["R2"] if col["R2"] is not None else R["R2"])
    # Sim column has no own R model: Q uses the design R (same as analytical), stated in the note.

    units = {"L1": ("uH", 1e6), "L2": ("uH", 1e6), "R1": ("ohm", 1), "R2": ("ohm", 1),
             "C1": ("nF", 1e9), "C2": ("nF", 1e9), "f01": ("kHz", 1e-3), "f02": ("kHz", 1e-3),
             "Q1": ("-", 1), "Q2": ("-", 1)}
    rows = []
    for q, (u, s) in units.items():
        a, si, m = an[q], sim[q], ms.get(q)
        rows.append(dict(quantity=q, unit=u,
                         analytical=None if a is None else a * s,
                         simulation=None if si is None else si * s,
                         measured=None if m is None else m * s))

    # k at each test distance
    for d in params.distances:
        k_an = coil_mutual(radii, radii, d) / L_sim
        k_sim = mutual_coaxial(radii, radii, d) / L_sim
        k_m = None
        for method, (dm, _, km) in meas_k.items():          # first method found at this distance
            hit = np.isclose(dm, d * 100)
            if hit.any():
                k_m = float(km[hit][0])
                break
        rows.append(dict(quantity=f"k (d = {d*100:g} cm)", unit="-",
                         analytical=k_an, simulation=k_sim, measured=k_m))

    for r in rows:
        r["sim_vs_an_pct"] = pct(r["simulation"], r["analytical"])
        if r["quantity"] in ("C1", "C2"):
            r["sim_vs_an_pct"] = None          # same component in both columns: not a comparison
        ref = r["simulation"] if r["simulation"] is not None else r["analytical"]
        r["meas_vs_sim_pct"] = pct(r["measured"], ref)
    info = dict(tag="PLACEHOLDER GEOMETRY" if g["placeholder"] else "design geometry",
                c_derived=c_derived, radii=radii, L_sim=L_sim, L_an=L_an,
                R1=R["R1"], R2=R["R2"], R_placeholder=c["placeholder"])
    return rows, info


def fmt(v, nd=4):
    return "n/a" if v is None else f"{v:.{nd}g}"


def fmt_pct(v):
    return "n/a" if v is None else f"{v:+.2f}"


def flagged(rows):
    return [r for r in rows
            if any(v is not None and abs(v) > FLAG_PCT for v in (r["sim_vs_an_pct"], r["meas_vs_sim_pct"]))]


def write_tables(rows, info):
    out_csv = ROOT / "data" / "compare_table.csv"
    with open(out_csv, "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["quantity", "unit", "analytical", "simulation", "measured",
                    "sim_vs_an_pct", "meas_vs_sim_pct"])
        for r in rows:
            w.writerow([r["quantity"], r["unit"], fmt(r["analytical"], 6), fmt(r["simulation"], 6),
                        fmt(r["measured"], 6), fmt_pct(r["sim_vs_an_pct"]), fmt_pct(r["meas_vs_sim_pct"])])

    flags = flagged(rows)
    lines = [f"# Parameter comparison ({info['tag']}, PARAMS_VERSION = {params.PARAMS_VERSION})", "",
             "Generated by `python -m sim.compare`.", "",
             "- Analytical: L from Mohan current sheet; k from the closed-form (elliptic) M divided by L_filament.",
             "- Simulation: L from the filament sum; k from the numerical Neumann M divided by L_filament.",
             "- Measured: from `sim/params.py` when PARAMS_VERSION = v2-measured, and `data/meas_M_k.csv`; otherwise n/a.",
             (f"- R has no model (no Simulation value): Q in both the Analytical and Simulation columns uses the design "
              f"R1 = {info['R1']:g} ohm, R2 = {info['R2']:g} ohm"
              f"{' (PLACEHOLDER)' if info['R_placeholder'] else ' from params.py (provisional until measured)'}."),
             ("- C1, C2 are **derived** as 1/(w0^2 L_filament) at the design f0 because they are not set in "
              "params.py; f0 in the Analytical column therefore shows the shift caused by the Mohan L."
              if info["c_derived"] else "- C1, C2 from `sim/params.py`."),
             "- C1, C2 are the same component value in both columns, so no Sim vs An % is shown (it is not a comparison).",
             "- % columns: Sim vs An = (Sim - An)/An; Meas vs Sim = (Meas - Sim)/Sim.", "",
             "| Quantity | Unit | Analytical | Simulation | Measured | Sim vs An % | Meas vs Sim % |",
             "|---|---|---|---|---|---|---|"]
    for r in rows:
        mark = " **(>10 %)**" if r in flags else ""
        lines.append(f"| {r['quantity']}{mark} | {r['unit']} | {fmt(r['analytical'])} | {fmt(r['simulation'])} | "
                     f"{fmt(r['measured'])} | {fmt_pct(r['sim_vs_an_pct'])} | {fmt_pct(r['meas_vs_sim_pct'])} |")
    lines += ["", f"## Rows with difference above {FLAG_PCT:g} %", ""]
    lines += [f"- {r['quantity']}: Sim vs An {fmt_pct(r['sim_vs_an_pct'])} %, "
              f"Meas vs Sim {fmt_pct(r['meas_vs_sim_pct'])} %" for r in flags] or ["- none"]
    out_md = ROOT / "data" / "compare_table.md"
    out_md.write_text("\n".join(lines) + "\n")
    return out_csv, out_md, flags


def make_overlays(info, meas_k):
    """M(d) and k(d): analytical blue solid, simulation orange dashed, measured black markers."""
    radii, L_sim = info["radii"], info["L_sim"]
    d_th = np.linspace(params.d_sweep[0], params.d_sweep[-1], 146)   # fine grid for the theory curve
    M_th = np.array([coil_mutual(radii, radii, d) for d in d_th])

    with open(SIM_FILE) as fh:                                   # A-S1 output
        sim_rows = list(csv.DictReader(fh))
    d_sim = np.array([float(r["d_cm"]) for r in sim_rows])
    M_sim = np.array([float(r["M_H"]) for r in sim_rows])
    k_sim = np.array([float(r["k"]) for r in sim_rows])
    # Staleness guard: the CSV must match the current geometry
    i3 = np.argmin(np.abs(d_sim - 3.0))
    fresh = mutual_coaxial(radii, radii, d_sim[i3] * 1e-2)
    if abs(M_sim[i3] - fresh) / fresh > 1e-5:
        raise RuntimeError("data/sim_M_k.csv is out of date for the current geometry; "
                           "rerun `python -m sim.coupling` first.")

    paths = []
    for name, y_th, y_sim, key, ylabel in [
            ("fig_M_vs_d_overlay", M_th * 1e6, M_sim * 1e6, 1, r"Mutual inductance $M$ ($\mu$H)"),
            ("fig_k_vs_d_overlay", M_th / L_sim, k_sim, 2, r"Coupling coefficient $k$")]:
        meas = []
        for (method, (dm, Mm, km)), mk in zip(meas_k.items(), MARKERS):
            y = Mm * 1e6 if key == 1 else km
            ok = ~np.isnan(y)
            if ok.any():
                meas.append((dm[ok], y[ok], f"Measured ({method})", mk))
        fig, ax = plt.subplots(figsize=(8, 5.5))
        overlay(ax, theory=(d_th * 100, y_th, "Analytical (closed form)"),
                sim=(d_sim, y_sim, "Simulation (Neumann)"), meas=meas)
        ax.set_yscale("log")
        ax.set_xlabel("Coil spacing $d$ (cm)")
        ax.set_ylabel(ylabel)
        title = "No measured data yet" if not meas else ""
        if info["tag"].startswith("PLACEHOLDER"):
            title = "PLACEHOLDER GEOMETRY" + (f" — {title}" if title else "")
        if title:
            ax.set_title(title, fontsize=13)
        fig.tight_layout()
        paths += list(save_fig(fig, name))
        plt.close(fig)
    return paths


def main():
    print(f"=== A-V1 comparison, PARAMS_VERSION = {params.PARAMS_VERSION} ===")
    meas_params = load_measured_params()
    meas_k = load_measured_k()

    # Step 4: is params.py really holding measured values?
    if params.PARAMS_VERSION == "v2-measured":
        missing = [k for k, v in meas_params.items() if v is None]
        print("params.py measured values:", "all present" if not missing else f"MISSING {missing}")
    else:
        print("NOTE: PARAMS_VERSION is not 'v2-measured' -> params.py holds no measured values; "
              "Measured column for L, R, C, f0, Q is n/a.")
    print(f"Measured k file {MEAS_FILE.relative_to(ROOT)}: "
          f"{'found, methods ' + str(list(meas_k)) if meas_k else 'not found -> k measured n/a'}")

    rows, info = build_table(meas_params, meas_k)
    print(f"\n{info['tag']}")
    print(f"{'Quantity':<16} {'Unit':<5} {'Analytical':>11} {'Simulation':>11} {'Measured':>10} "
          f"{'Sim/An %':>9} {'Meas/Sim %':>10}")
    for r in rows:
        print(f"{r['quantity']:<16} {r['unit']:<5} {fmt(r['analytical']):>11} {fmt(r['simulation']):>11} "
              f"{fmt(r['measured']):>10} {fmt_pct(r['sim_vs_an_pct']):>9} {fmt_pct(r['meas_vs_sim_pct']):>10}")
    out_csv, out_md, flags = write_tables(rows, info)
    print(f"\nRows above {FLAG_PCT:g} %: " + (", ".join(r["quantity"] for r in flags) if flags else "none"))
    print(f"Wrote {out_csv.relative_to(ROOT)}, {out_md.relative_to(ROOT)}")
    for p in make_overlays(info, meas_k):
        print(f"Saved {p.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
