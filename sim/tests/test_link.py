"""Tests for sim/link.py, params consistency and circuit-level results (B-S1, B-C1, B-T2)."""
import numpy as np
import pytest

from sim import params
from sim.analytic import L_filament, coil_mutual
from sim.circuit import solve, RL_opt, k_crit
from sim.link import M_of_d, k_of_d, fixed_load


def test_params_L_matches_geometry():
    """params.L1, L2 equal the filament-sum L of the geometry in params.py."""
    g = params.get_geometry()
    L = L_filament(g["radii"], g["wire_d"] / 2)
    assert params.L1 == pytest.approx(L, rel=1e-3)
    assert params.L2 == pytest.approx(L, rel=1e-3)


def test_params_C_tunes_to_f0():
    for L, C in ((params.L1, params.C1), (params.L2, params.C2)):
        assert 1 / (2 * np.pi * np.sqrt(L * C)) == pytest.approx(params.f0, rel=1e-9)


def test_M_of_d_matches_closed_form():
    """M from the A-S1 CSV agrees with the A-C1 elliptic formula."""
    r = params.get_geometry()["radii"]
    for d in (1, 3, 5, 10):
        assert M_of_d(d) == pytest.approx(coil_mutual(r, r, d * 1e-2), rel=1e-3)


def test_fixed_load_default_is_RL_opt_at_d_RL_fixed():
    if params.RL_fixed is not None:
        assert fixed_load() == params.RL_fixed
    else:
        M = M_of_d(params.d_RL_fixed * 100)
        assert fixed_load() == pytest.approx(RL_opt(M, params.f0, params.R1, params.R2))


@pytest.mark.parametrize("Rs", [0.0, 50.0])
def test_PL_vs_M_peaks_at_critical_coupling(Rs):
    """At f0: P_L(M) is maximal where w0^2 M^2 = (R1 + Rs)(R2 + RL), i.e. k = k_crit(..., Rs=Rs)."""
    f0, L1, L2, C1, C2, R1, R2 = params.f0, params.L1, params.L2, params.C1, params.C2, params.R1, params.R2
    RL = 6.0
    k = np.linspace(0.001, 0.6, 600001)
    PL = solve(f0, k * np.sqrt(L1 * L2), L1, L2, C1, C2, R1, R2, RL, 5.0, Rs=Rs).PL
    assert k[np.argmax(PL)] == pytest.approx(float(k_crit(L1, L2, f0, R1, R2, RL, Rs=Rs)), rel=1e-3)


@pytest.mark.parametrize("Rs", [0.0, 50.0])
def test_power_optimal_load_and_its_efficiency(Rs):
    """R_L,Pmax = R2 + w0^2 M^2/(R1+Rs); eta there = eta(x, r = 1 + x R1/(R1+Rs)) < 1/2 (-> x/(2(2+x)) for Rs=0)."""
    p = params
    M = M_of_d(3.0)
    w0 = 2 * np.pi * p.f0
    RL = np.logspace(-1, 4, 400001)
    r = solve(p.f0, M, p.L1, p.L2, p.C1, p.C2, p.R1, p.R2, RL, p.Vs, Rs=Rs)
    RLp = p.R2 + (w0 * M) ** 2 / (p.R1 + Rs)
    assert RL[np.argmax(r.PL)] == pytest.approx(RLp, rel=1e-3)
    x = (w0 * M) ** 2 / (p.R1 * p.R2)
    rr = 1 + x * p.R1 / (p.R1 + Rs)
    eta_p = x * rr / ((1 + rr) * (1 + rr + x))
    eta_num = solve(p.f0, M, p.L1, p.L2, p.C1, p.C2, p.R1, p.R2, RLp, p.Vs, Rs=Rs).eta
    assert eta_num == pytest.approx(eta_p, rel=1e-9)
    if Rs == 0:
        assert eta_p == pytest.approx(x / (2 * (2 + x)), rel=1e-12) and eta_p < 0.5


def test_no_secondary_current_is_Vs_over_R1():
    """Worst-case stress (B-C1): with M = 0, I1 = Vs/(R1 + Rs) at f0."""
    p = params
    for Rs in (0.0, 50.0):
        I1 = solve(p.f0, 0.0, p.L1, p.L2, p.C1, p.C2, p.R1, p.R2, 6.0, p.Vs, Rs=Rs).I1
        assert abs(I1) == pytest.approx(p.Vs / (p.R1 + Rs), rel=1e-9)


def test_k_of_d_decreasing():
    d = np.array([1, 2, 3, 5, 8, 10])
    assert np.all(np.diff(k_of_d(d)) < 0)


@pytest.mark.parametrize("Rs", [0.0, 1.0, 50.0, 1000.0])
def test_eta_independent_of_Rs(Rs):
    """Pin is at the resonator terminals, so eta and the closed forms hold for any source resistance."""
    from sim.circuit import eta_closed, eta_max
    p = params
    M = np.array([M_of_d(d) for d in (1, 3, 5, 10)])
    r = solve(p.f0, M, p.L1, p.L2, p.C1, p.C2, p.R1, p.R2, 6.0, p.Vs, Rs=Rs)
    assert np.allclose(r.eta, eta_closed(M, p.f0, p.R1, p.R2, 6.0), atol=1e-9)
    ro = solve(p.f0, M, p.L1, p.L2, p.C1, p.C2, p.R1, p.R2, RL_opt(M, p.f0, p.R1, p.R2), p.Vs, Rs=Rs)
    assert np.allclose(ro.eta, eta_max(M, p.f0, p.R1, p.R2), atol=1e-9)


def test_k_of_d_and_M_of_d_reject_out_of_range():
    """Distances outside the CSV range raise ValueError."""
    for f in (M_of_d, k_of_d):
        with pytest.raises(ValueError):
            f(0.1)
        with pytest.raises(ValueError):
            f(50.0)
        with pytest.raises(ValueError):
            f(np.array([1.0, 20.0]))


def test_B_C1_stress_table_matches_script():
    """The stress table in theory/B-C1 matches sim/stress.py."""
    import pandas as pd
    from sim.link import ROOT
    from sim.stress import stress_rows, markdown_table
    df = pd.DataFrame(stress_rows(params.Rs) + stress_rows(params.Rs_gen))
    table = markdown_table(df)
    doc = (ROOT / "theory" / "B-C1_resonance_numbers.md").read_text(encoding="utf-8")
    assert table in doc, "run `python -m sim.stress` and copy data/stress_table.md into B-C1"
