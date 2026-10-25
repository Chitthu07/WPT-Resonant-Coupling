"""Tests for A-V1 (sim/compare.py).

The 'measured' numbers below are FAKE, made up only to exercise the code path
(table filling, % differences, flagging, overlay markers). They are never written to data/.
"""

import numpy as np
import pytest

import sim.compare as cmp
import sim.style as style
from sim import params


def test_blank_measured_gives_na():
    rows, _ = cmp.build_table(cmp.load_measured_params(), {})
    assert all(r["measured"] is None for r in rows)
    assert len(rows) == 10 + len(params.distances)


def test_fake_measured_fills_table_and_flags(monkeypatch, tmp_path):
    L_fil = cmp.build_table({}, {})[1]["L_sim"]
    monkeypatch.setattr(params, "PARAMS_VERSION", "v2-measured")
    for k, v in {"L1": 1.2 * L_fil, "L2": L_fil, "R1": 0.3, "R2": 0.3, "C1": 6e-9, "C2": 6e-9}.items():
        monkeypatch.setattr(params, k, v)
    fake = tmp_path / "meas_M_k.csv"
    fake.write_text("d_cm, M_H, k, method\n3, , 0.25, series-aiding\n5, 1.9e-6, 0.11, open-short\n")
    meas_k = cmp.load_measured_k(fake)
    assert set(meas_k) == {"series-aiding", "open-short"}

    rows, info = cmp.build_table(cmp.load_measured_params(), meas_k)
    by_q = {r["quantity"]: r for r in rows}
    assert by_q["L1"]["meas_vs_sim_pct"] == pytest.approx(20.0)          # 1.2 L_fil vs L_fil
    assert by_q["L2"]["meas_vs_sim_pct"] == pytest.approx(0.0, abs=1e-9)
    assert by_q["k (d = 3 cm)"]["measured"] == 0.25
    names = [r["quantity"] for r in cmp.flagged(rows)]
    assert "L1" in names and "k (d = 3 cm)" in names and "L2" not in names

    monkeypatch.setattr(style, "FIG_DIR", tmp_path)                       # keep real figs/ untouched
    paths = cmp.make_overlays(info, meas_k)
    assert all(p.parent == tmp_path and p.exists() for p in paths)
