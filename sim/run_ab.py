"""Regenerate every CSV and figure of Members A and B from sim/params.py, in dependency order.

(Renamed from sim/make_figures.py: that name belongs to Member C's task C-S3, the team-wide
figure script of the team. This script only covers A and B outputs.)

Member A (magnetic link) runs first, because Member B's circuit scripts read data/sim_M_k.csv:
  A-C1 run_analytic  -> theory/hand_values.csv
  A-S1 coupling      -> data/sim_M_k.csv, fig_M_vs_d, fig_k_vs_d
  A-S2 misalignment  -> data/sim_misalign.csv, data/sim_eta_dx.csv, fig_k_vs_dx, fig_eta_vs_dx, fig_PL_vs_dx
  A-S3 fieldmap      -> fig_B_map
  A-V1 compare       -> data/compare_table.*, fig_M_vs_d_overlay, fig_k_vs_d_overlay
  B-S1 run_circuit   -> data/sim_eta_d.csv, fig_eta_vs_d, fig_PL_vs_d
  B-S2 freq_response -> data/sim_freq_metrics.csv, data/sim_detuning.csv, fig_*_vs_f, fig_eta_vs_detuning
  B-S3 load_sweep    -> data/sim_RL_sweep.csv, fig_eta_vs_RL, fig_PL_vs_RL
  B-C1 stress        -> data/stress_table.*

Run from the project root, either way:
  python -m sim.run_ab
  python sim/run_ab.py
Then run the tests:  python -m pytest sim/tests -q
"""

import importlib
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:                 # allow `python sim/run_ab.py`
    sys.path.insert(0, str(ROOT))

STEPS = [
    ("A-C1", "sim.run_analytic"),
    ("A-S1", "sim.coupling"),
    ("A-S2", "sim.misalignment"),
    ("A-S3", "sim.fieldmap"),
    ("A-V1", "sim.compare"),
    ("B-S1", "sim.run_circuit"),
    ("B-S2", "sim.freq_response"),
    ("B-S3", "sim.load_sweep"),
    ("B-C1", "sim.stress"),
]


def main():
    t_all = time.time()
    for task, module in STEPS:
        print(f"\n{'=' * 70}\n[{task}] python -m {module}\n{'=' * 70}")
        t = time.time()
        importlib.import_module(module).main()
        print(f"[{task}] done in {time.time() - t:.1f} s")
    print(f"\nAll {len(STEPS)} steps finished in {time.time() - t_all:.1f} s. "
          "Now run: python -m pytest sim/tests -q")


if __name__ == "__main__":
    main()
