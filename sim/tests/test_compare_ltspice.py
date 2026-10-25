"""B-V1 part 2: the saved LTspice .ac results of sim/wpt.asc (data/ltspice_ac.csv) match solve()."""
import numpy as np
import pandas as pd
import pytest

from sim import params
from sim.circuit import solve
from sim.compare_ltspice import CSV, netlist_values

pytestmark = pytest.mark.skipif(not CSV.exists(), reason="run `python -m sim.compare_ltspice --run` first")


def test_three_k_values_saved():
    assert pd.read_csv(CSV).k.nunique() == 3


def test_ltspice_matches_solver_within_1_percent():
    sp = pd.read_csv(CSV)
    C1, C2, RL = netlist_values()
    for k, g in sp.groupby("k"):
        f = g.f_Hz.to_numpy()
        r = solve(f, k * np.sqrt(params.L1 * params.L2), params.L1, params.L2, C1, C2,
                  params.R1, params.R2, RL, params.Vs)
        I1 = (g.I1_re + 1j * g.I1_im).to_numpy()
        I2 = (g.I2_re + 1j * g.I2_im).to_numpy()
        assert np.max(np.abs(I1 - r.I1) / np.abs(r.I1)) < 1e-2
        assert np.max(np.abs(I2 - r.I2) / np.abs(r.I2)) < 1e-2


def test_ltspice_secondary_current_lags_by_90_degrees_at_f0():
    sp = pd.read_csv(CSV)
    for _, g in sp.groupby("k"):
        row = g.iloc[int(np.argmin(np.abs(g.f_Hz - params.f0)))]
        phase = np.degrees(np.angle((row.I2_re + 1j * row.I2_im) / (row.I1_re + 1j * row.I1_im)))
        assert phase == pytest.approx(-90.0, abs=0.01)
