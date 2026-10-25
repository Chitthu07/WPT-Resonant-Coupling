"""Guard against the hand-typed design values in sim/params.py drifting from the geometry.

params.L1 / L2 (design, v1) are a typed copy of the A-C1 filament sum, and C1 / C2 are derived
from them. If the geometry is changed but L1 is not updated (or vice versa), these tests fail.
Once PARAMS_VERSION == "v2-measured", L1/L2 are measured values and may legitimately differ.
"""

import numpy as np
import pytest

from sim import params
from sim.analytic import L_filament
from sim.coupling import coil_inductances

DESIGN = params.PARAMS_VERSION != "v2-measured"


@pytest.mark.skipif(not DESIGN, reason="L1/L2 are measured values in v2")
@pytest.mark.parametrize("name", ["L1", "L2"])
def test_design_L_matches_filament_sum(name):
    """Typed design L within 0.1 % of the filament sum for the current geometry."""
    g = params.get_geometry()
    L_fil = L_filament(g["radii"], g["wire_d"] / 2)
    assert getattr(params, name) == pytest.approx(L_fil, rel=1e-3)


@pytest.mark.parametrize("L, C", [("L1", "C1"), ("L2", "C2")])
def test_capacitors_tune_to_f0(L, C):
    """f0 = 1 / (2 pi sqrt(L C)) reproduces the design f0 within 0.1 %."""
    f = 1 / (2 * np.pi * np.sqrt(getattr(params, L) * getattr(params, C)))
    assert f == pytest.approx(params.f0, rel=1e-3)


def test_k_uses_geometry_not_typed_L_in_design_phase():
    """In v1-design, k is computed from the filament sum, not the typed params.L1."""
    g = params.get_geometry()
    L1, L2, src = coil_inductances(g)
    if DESIGN:
        assert src == "filament sum"
        assert L1 == L_filament(g["radii"], g["wire_d"] / 2)
    else:
        assert src.startswith("measured")
