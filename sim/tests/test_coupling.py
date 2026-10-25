"""Tests for A-S1 (sim/coupling.py): the three validation checks plus segment convergence."""

import numpy as np
import pytest

from sim import params
from sim.params import MU0
from sim.analytic import coil_mutual, L_filament, coupling
from sim.coupling import mutual_coaxial, N_SEG

GEOM = params.get_geometry()
RADII = GEOM["radii"]


@pytest.mark.parametrize("d_cm", [1, 2, 3, 5, 8, 10])
def test_neumann_matches_closed_form(d_cm):
    """Check 1: numerical coaxial M within 2 % of the elliptic closed form."""
    d = d_cm * 1e-2
    Mn, Mc = mutual_coaxial(RADII, RADII, d), coil_mutual(RADII, RADII, d)
    assert abs(Mn - Mc) / Mc < 0.02


def test_single_turn_converges_to_dipole():
    """Check 2: single-turn pair approaches mu0 pi a^4 / (2 d^3); error shrinks with d."""
    a = RADII[0]
    errs = []
    for ratio in [10, 20, 50]:
        d = ratio * a
        Mn = mutual_coaxial([a], [a], d)
        Md = MU0 * np.pi * a ** 4 / (2 * d ** 3)
        errs.append(abs(Md - Mn) / Mn)
    assert errs[0] < 0.05                     # a few percent at d = 10a
    assert errs[0] > errs[1] > errs[2]        # converging
    assert errs[2] < 0.005


def test_loglog_slope_tends_to_minus_three():
    """Check 3: local log-log slope of M(d) approaches -3 at large d."""
    d1, d2 = 0.5, 1.0
    s = np.log(mutual_coaxial(RADII, RADII, d2) / mutual_coaxial(RADII, RADII, d1)) / np.log(d2 / d1)
    assert abs(s + 3) < 0.05


@pytest.mark.parametrize("d_cm", [0.5, 3, 10])
def test_segment_convergence(d_cm):
    """Doubling segments per turn changes M by well under 0.5 %."""
    d = d_cm * 1e-2
    Ma = mutual_coaxial(RADII, RADII, d, n_seg=N_SEG)
    Mb = mutual_coaxial(RADII, RADII, d, n_seg=2 * N_SEG)
    assert abs(Mb - Ma) / Mb < 0.005


def test_k_physical():
    """k between 0 and 1 and decreasing over the sweep range."""
    L = L_filament(RADII, GEOM["wire_d"] / 2)
    d = np.array([0.5, 1, 2, 5, 10, 15]) * 1e-2
    k = coupling(np.array([mutual_coaxial(RADII, RADII, x) for x in d]), L, L)
    assert np.all((k > 0) & (k < 1))
    assert np.all(np.diff(k) < 0)
