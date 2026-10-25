"""Tests for B-V1 part 1 (sim/compare_circuit.py): solver vs analytical routes and split peaks."""
import numpy as np
import pytest

from sim import params
from sim.circuit import solve
from sim.compare_circuit import analytic_f, peaks
from sim.link import M_of_d, fixed_load

L1, L2, C1, C2 = params.L1, params.L2, params.C1, params.C2
R1, R2, f0, Vs = params.R1, params.R2, params.f0, params.Vs


@pytest.mark.parametrize("d", [1, 5, 10])
@pytest.mark.parametrize("Rs", [0.0, 50.0])
def test_elimination_route_equals_solver_off_resonance(d, Rs):
    f = np.linspace(0.6 * f0, 1.6 * f0, 2001)
    M, RL = M_of_d(d), fixed_load()
    r = solve(f, M, L1, L2, C1, C2, R1, R2, RL, Vs, Rs=Rs)
    I1, PL, eta = analytic_f(f, M, RL, Vs, Rs)
    assert np.allclose(np.abs(r.I1), I1, rtol=1e-10)
    assert np.allclose(r.PL, PL, rtol=1e-10)
    assert np.allclose(r.eta, eta, rtol=1e-10)


def _k_from_peaks(d, RL):
    f = np.linspace(0.6 * f0, 1.6 * f0, 100001)
    pk = peaks(f, solve(f, M_of_d(d), L1, L2, C1, C2, R1, R2, RL, Vs).PL)
    if len(pk) < 2:
        return None
    fl, fh = pk[0], pk[-1]
    return (fh**2 - fl**2) / (fh**2 + fl**2)


@pytest.mark.parametrize("d", [1, 2, 5])
def test_split_peaks_give_k_with_light_load(d):
    k = M_of_d(d) / np.sqrt(L1 * L2)
    assert _k_from_peaks(d, 0.01) == pytest.approx(k, rel=0.005)


def test_fixed_load_pulls_split_peaks_together():
    """At 5 cm the 6 ohm load makes the split-peak formula read k about a third low; at 10 cm one peak."""
    k5 = M_of_d(5) / np.sqrt(L1 * L2)
    assert _k_from_peaks(5, fixed_load()) < 0.75 * k5
    assert _k_from_peaks(10, fixed_load()) is None
