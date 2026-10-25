"""B-V1 (part 2): LTspice (sim/wpt.asc, C-S1) vs the phasor solver sim/circuit.py solve().

Run from the repo root:
  python -m sim.compare_ltspice --run   run sim/wpt.asc in LTspice (Wine on Linux), save data/ltspice_ac.csv,
                                        then compare
  python -m sim.compare_ltspice         compare using the saved data/ltspice_ac.csv (no LTspice needed)

--run turns sim/wpt.asc into a netlist with LTspice, adds `.options plotwinsize=0 numdgt=15`
(no waveform compression, double precision) and runs it in batch mode in a temporary folder.
The binary .raw file is read directly. I1 = I(L1) and I2 = I(L2) both flow into the dotted
terminals (N002 and N003 are the first pins of L1, L2), the same convention as B-T1.

The solver is evaluated with the values of the netlist (C = 5.914815 nF as typed in wpt.asc, k from
its .step list) and L, R, R_L, Vs from params.py, so both sides solve the same circuit.
Target (project brief): < 1 % in peak value and peak frequency for three k values.
"""
import argparse
import os
import re
import subprocess
import tempfile
from pathlib import Path

import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

from sim import params
from sim.circuit import solve
from sim.link import ROOT
from sim.style import THEORY, SIM, save_fig

ASC = ROOT / "sim" / "wpt.asc"
CSV = ROOT / "data" / "ltspice_ac.csv"
LTSPICE_EXE = os.environ.get("LTSPICE_EXE", r"C:\Program Files\ADI\LTspice\LTspice.exe")
D_OF_K = {0.321109: 2, 0.111189: 5, 0.029895: 10}     # k values of the .step list in wpt.asc -> d [cm]


def _ltspice(args, cwd):
    cmd = ["wine", LTSPICE_EXE, *args] if os.name != "nt" else [LTSPICE_EXE, *args]
    env = dict(os.environ, WINEDEBUG="-all")
    subprocess.run(cmd, cwd=cwd, env=env, check=True, timeout=300,
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def read_raw(path):
    """Read an LTspice binary .raw file: returns (variable names, steps, data[n_points, n_vars] complex)."""
    b = Path(path).read_bytes()
    marker = "Binary:\n".encode("utf-16-le")
    i = b.find(marker)
    header = b[:i].decode("utf-16-le")
    n_vars = int(re.search(r"No\. Variables:\s*(\d+)", header).group(1))
    n_pts = int(re.search(r"No\. Points:\s*(\d+)", header).group(1))
    flags = re.search(r"Flags:(.*)", header).group(1)
    if "complex" not in flags or "compression" in flags.replace("nocompression", ""):
        raise ValueError(f"expected an uncompressed complex (.ac) raw file, flags = {flags.strip()}")
    names = re.findall(r"^\t\d+\t(\S+)\t", header.split("\nVariables:")[1], flags=re.M)
    data = np.frombuffer(b[i + len(marker):], dtype="<c16", count=n_pts * n_vars).reshape(n_pts, n_vars)
    return names, data


def run_ltspice():
    """Run sim/wpt.asc in LTspice and save frequency, k, I1, I2 for every step to data/ltspice_ac.csv."""
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        (tmp / "wpt.asc").write_bytes(ASC.read_bytes())
        _ltspice(["-netlist", "wpt.asc"], tmp)
        net = (tmp / "wpt.net").read_text(encoding="utf-8", errors="replace")
        net = net.replace(".backanno", ".options plotwinsize=0 numdgt=15\n.backanno")
        (tmp / "wpt_run.net").write_text(net, encoding="utf-8")
        _ltspice(["-b", "wpt_run.net"], tmp)
        log = (tmp / "wpt_run.log").read_text(encoding="utf-8", errors="replace").replace("\x00", "")
        steps = [float(v) for v in re.findall(r"\.step k=([0-9.eE+-]+)", log)]
        names, data = read_raw(tmp / "wpt_run.raw")
    col = {n.lower(): j for j, n in enumerate(names)}
    f = data[:, col["frequency"]].real
    starts = np.flatnonzero(np.diff(f) < 0) + 1                  # frequency restarts at every step
    blocks = np.split(np.arange(len(f)), starts)
    if len(blocks) != len(steps):
        raise ValueError(f"{len(blocks)} sweeps in the .raw file but {len(steps)} .step lines in the log")
    k = np.concatenate([np.full(len(blk), s) for blk, s in zip(blocks, steps)])
    I1, I2 = data[:, col["i(l1)"]], data[:, col["i(l2)"]]
    pd.DataFrame({"k": k, "f_Hz": f, "I1_re": I1.real, "I1_im": I1.imag, "I2_re": I2.real, "I2_im": I2.imag}
                 ).to_csv(CSV, index=False, float_format="%.12e")
    print(f"LTspice: {len(steps)} steps x {len(blocks[0])} points -> {CSV.relative_to(ROOT)}")


def netlist_values():
    """C1, C2 and R_L as typed in sim/wpt.asc."""
    asc = ASC.read_text(encoding="utf-8", errors="replace")
    vals = dict(re.findall(r"SYMATTR InstName (\w+)\nSYMATTR Value ([^\n]+)", asc))
    num = lambda s: float(s.replace("n", "e-9").replace("u", "e-6"))
    return num(vals["C1"]), num(vals["C2"]), num(vals["RL"])


def peak(f, y):
    """Global maximum of y(f), refined by a parabola through the three highest grid points."""
    i = int(np.argmax(y))
    if 0 < i < len(y) - 1:
        a, b, c = y[i - 1], y[i], y[i + 1]
        p = 0.5 * (a - c) / (a - 2 * b + c)
        return f[i] + p * (f[1] - f[0]), b - 0.25 * (a - c) * p
    return f[i], y[i]


def main(run=False):
    if run:
        run_ltspice()
    if not CSV.exists():
        raise FileNotFoundError(f"{CSV} not found. Run `python -m sim.compare_ltspice --run` (needs LTspice).")
    sp = pd.read_csv(CSV)
    C1, C2, RL = netlist_values()
    L1, L2, R1, R2, f0, Vs = params.L1, params.L2, params.R1, params.R2, params.f0, params.Vs
    print(f"Netlist: C1 = C2 = {C1*1e9:.6f} nF (params: {params.C1*1e9:.6f} nF), R_L = {RL:g} ohm, "
          f"R1 = R2 = {R1:g} ohm, L = {L1*1e6:g} uH, Vs = {Vs:g} V peak, Rs = 0")

    rows, curves = [], []
    for k, g in sp.groupby("k", sort=False):
        f = g.f_Hz.to_numpy()
        I1_sp = (g.I1_re + 1j * g.I1_im).to_numpy()
        I2_sp = (g.I2_re + 1j * g.I2_im).to_numpy()
        PL_sp = 0.5 * np.abs(I2_sp) ** 2 * RL
        eta_sp = PL_sp / (0.5 * np.real(Vs * np.conj(I1_sp)))
        r = solve(f, k * np.sqrt(L1 * L2), L1, L2, C1, C2, R1, R2, RL, Vs)
        i0 = int(np.argmin(np.abs(f - f0)))
        fp_sp, P_sp = peak(f, PL_sp)
        fp_py, P_py = peak(f, r.PL)
        ph = lambda I2, I1: np.degrees(np.angle(I2[i0] / I1[i0]))
        rows.append(dict(
            d_cm=D_OF_K.get(round(k, 6), np.nan), k=k,
            f_peak_ltspice_kHz=fp_sp / 1e3, f_peak_solver_kHz=fp_py / 1e3,
            f_peak_err_pct=100 * abs(fp_sp - fp_py) / fp_py,
            PL_peak_ltspice_W=P_sp, PL_peak_solver_W=P_py, PL_peak_err_pct=100 * abs(P_sp - P_py) / P_py,
            eta_f0_ltspice_pct=100 * eta_sp[i0], eta_f0_solver_pct=100 * r.eta[i0],
            phase_I2_I1_f0_ltspice_deg=ph(I2_sp, I1_sp), phase_I2_I1_f0_solver_deg=ph(r.I2, r.I1),
            max_err_I1_pct=100 * np.max(np.abs(I1_sp - r.I1) / np.abs(r.I1)),
            max_err_I2_pct=100 * np.max(np.abs(I2_sp - r.I2) / np.abs(r.I2)),
            max_err_PL_pct=100 * np.max(np.abs(PL_sp - r.PL) / r.PL),
            max_err_eta_pct=100 * np.max(np.abs(eta_sp - r.eta) / r.eta)))
        curves.append((k, f, PL_sp, r.PL, eta_sp, r.eta))
    met = pd.DataFrame(rows).sort_values("k", ascending=False)
    met.to_csv(ROOT / "data" / "val_ltspice_metrics.csv", index=False)

    fig, axes = plt.subplots(2, 3, figsize=(15, 8), sharex="col")
    for j, (k, f, PL_sp, PL_py, eta_sp, eta_py) in enumerate(sorted(curves, key=lambda c: -c[0])):
        d = D_OF_K.get(round(k, 6))
        step = max(1, len(f) // 60)
        for ax, ys, yp, lab in ((axes[0, j], PL_sp, PL_py, "Load power $P_L$ (W)"),
                                (axes[1, j], 100 * eta_sp, 100 * eta_py, r"Link efficiency $\eta_{link}$ (%)")):
            ax.plot(f / 1e3, yp, label="circuit solver (Python)", **SIM)
            ax.plot(f[::step] / 1e3, ys[::step], ls="none", marker="o", ms=5, mfc="none",
                    color="tab:blue", label="LTspice wpt.asc (.ac)")
            ax.set_ylabel(lab); ax.legend(fontsize=10)
        axes[0, j].set_title(f"d = {d} cm, k = {k:.4f}", fontsize=13)
        axes[1, j].set_xlabel("Frequency f (kHz)")
    fig.suptitle(rf"$R_L$ = {RL:g} $\Omega$, $V_s$ = {Vs:g} V peak, $R_s$ = 0, R = {R1:g} $\Omega$", fontsize=13)
    fig.tight_layout(); save_fig(fig, "fig_PL_eta_vs_f_ltspice"); plt.close(fig)

    pd.set_option("display.width", 220)
    print(met.to_string(index=False, float_format=lambda v: f"{v:.6g}"))
    worst = met[["f_peak_err_pct", "PL_peak_err_pct", "max_err_PL_pct", "max_err_eta_pct"]].to_numpy().max()
    print(f"Largest difference, LTspice vs solver: {worst:.2e} % (target < 1 %)")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", action="store_true", help="run sim/wpt.asc in LTspice first (needs LTspice/Wine)")
    main(ap.parse_args().run)
