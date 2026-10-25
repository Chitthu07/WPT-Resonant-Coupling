"""Tests for A-S2 (sim/misalignment.py) and the closed-form efficiency it is checked against."""

import numpy as np
import pytest

from sim import params
from sim.analytic import L_filament, coupling
from sim.coupling import mutual_coaxial
from sim.misalignment import mutual_offset
from sim.circuit import eta_closed as eta_link, RL_opt   # closed-form eta at f0 (B-T2)

GEOM = params.get_geometry()
RADII = GEOM["radii"]


@pytest.mark.parametrize("d_cm", [3, 5])
def test_zero_offset_reproduces_coaxial(d_cm):
    """dx = 0 gives exactly the A-S1 coaxial M."""
    d = d_cm * 1e-2
    assert mutual_offset(RADII, d, 0.0) == mutual_coaxial(RADII, RADII, d)


@pytest.mark.parametrize("dx_cm", [1, 4, 8.5])
def test_symmetric_in_dx(dx_cm):
    """M(+dx) = M(-dx)."""
    d, dx = 0.03, dx_cm * 1e-2
    Mp, Mm = mutual_offset(RADII, d, dx), mutual_offset(RADII, d, -dx)
    assert abs(Mp - Mm) <= 1e-9 * abs(Mp)


def test_k_bounded_and_sign_change():
    """|k| <= 1 over the sweep; at d = 3 cm M is positive at 7 cm and negative at 9 cm."""
    L = L_filament(RADII, GEOM["wire_d"] / 2)
    M = np.array([mutual_offset(RADII, 0.03, x * 1e-2) for x in range(0, 11)])
    assert np.all(np.abs(coupling(M, L, L)) <= 1)
    assert M[7] > 0 and M[9] < 0


def test_closed_form_eta_reference_case():
    """CONVENTIONS.md reference case: L = 15 uH, R = 0.3 ohm, f0 = 500 kHz, M = 1.5 uH -> 4.72 ohm, 88.05 %."""
    rl = RL_opt(1.5e-6, 500e3, 0.3, 0.3)
    assert rl == pytest.approx(4.72, abs=0.01)
    assert 100 * eta_link(1.5e-6, 500e3, 0.3, 0.3, rl) == pytest.approx(88.05, abs=0.01)


@pytest.mark.parametrize("x, eta_pct", [(0.1, 2.4), (1, 17.2), (10, 53.7), (100, 81.9), (1000, 93.9)])
def test_closed_form_eta_table(x, eta_pct):
    """Best possible eta against x = k^2 Q1 Q2 (CONVENTIONS.md table); choose M so that w0^2 M^2/(R1 R2) = x."""
    f0, R = 500e3, 0.3
    M = np.sqrt(x) * R / (2 * np.pi * f0)
    assert 100 * eta_link(M, f0, R, R, RL_opt(M, f0, R, R)) == pytest.approx(eta_pct, abs=0.06)


def test_circuit_solver_matches_closed_form_along_misalignment():
    """B's phasor solve() at f0 equals the closed-form eta for M(dx), including M < 0."""
    from sim.circuit import solve
    M = np.array([mutual_offset(RADII, 0.03, x * 1e-2) for x in (0, 4, 7, 9)])
    f0, R = params.f0, params.R1
    RL = RL_opt(M[0], f0, R, R)
    eta_solver = solve(f0, M, params.L1, params.L2, params.C1, params.C2, R, R, RL, params.Vs).eta
    assert np.allclose(eta_solver, eta_link(M, f0, R, R, RL), atol=1e-9)


def test_eta_stub_matches_circuit_closed_form():
    """sim/eta_stub.py (still imported by C's run_c_s1_c_v1.py) must equal B's circuit closed forms."""
    from sim import eta_stub
    M = np.array([0.1e-6, 1.5e-6, 3.7e-6])
    f0, R = params.f0, params.R1
    assert np.allclose(eta_stub.RL_opt(M, f0, R, R), RL_opt(M, f0, R, R), rtol=1e-12)
    assert np.allclose(eta_stub.eta_link(M, f0, R, R, 6.0), eta_link(M, f0, R, R, 6.0), rtol=1e-12)
