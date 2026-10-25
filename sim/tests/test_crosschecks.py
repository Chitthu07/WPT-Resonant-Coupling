"""Independent cross-checks of numbers quoted in theory notes (A-V1 discussion, C-S2 shield study).

1. Richardson extrapolation of the Neumann sum, M_inf = M_300 + (M_300 - M_150)/3, lands on the
   elliptic closed form: the only error of the segment method is the O(1/n^2) polygon area deficit.
2. C-S2 (sim/shield.py, data/sim_shield.csv), image model of a thick metal plate at gap g behind
   the secondary (plate ~8 skin depths thick, B_n = 0 at its surface):
     L2' = L - M(2g),  L1' = L - M(2(d+g)),  M' = M(d) - M(d + 2g)    (image coil carries -I)
   and the eddy loss  P = 1/2 R_s * integral |H_t|^2 dA,  H_t = 2 * H_radial(free space),
   R_s = 1/(sigma delta), added series resistance dR = 2P/|I|^2.
   Recomputed here with A's own elliptic M and Biot-Savart code.
"""

from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from sim import params
from sim.params import MU0
from sim.analytic import coil_mutual, L_filament
from sim.coupling import mutual_coaxial, coil_segments
from sim.fieldmap import biot_savart

ROOT = Path(__file__).resolve().parents[2]
GEOM = params.get_geometry()
RADII = GEOM["radii"]
SHIELD_CSV = ROOT / "data" / "sim_shield.csv"


@pytest.mark.parametrize("d_cm", [1, 3, 10])
def test_richardson_neumann_hits_closed_form(d_cm):
    d = d_cm * 1e-2
    M150 = mutual_coaxial(RADII, RADII, d, n_seg=150)
    M300 = mutual_coaxial(RADII, RADII, d, n_seg=300)
    M_inf = M300 + (M300 - M150) / 3                  # removes the 1/n^2 term
    assert M_inf == pytest.approx(coil_mutual(RADII, RADII, d), rel=1e-6)


def _shield_rows():
    if not SHIELD_CSV.exists():
        pytest.skip("data/sim_shield.csv not found (run python -m sim.shield)")
    return pd.read_csv(SHIELD_CSV).to_dict("records")


def test_shield_image_model_L_and_M():
    """C's L1', L2', M' with an aluminium plate match the image-coil formulas (to the CSV's 4 decimals)."""
    L = L_filament(RADII, GEOM["wire_d"] / 2)
    M = lambda z: coil_mutual(RADII, RADII, z)
    for row in _shield_rows():
        d, g = row["d_cm"] * 1e-2, row["gap_mm"] * 1e-3
        assert row["L2_al_uH"] == pytest.approx((L - M(2 * g)) * 1e6, abs=2e-4)
        assert row["L1_al_uH"] == pytest.approx((L - M(2 * (d + g))) * 1e6, abs=2e-4)
        assert row["M_al_uH"] == pytest.approx((M(d) - M(d + 2 * g)) * 1e6, abs=2e-4)


@pytest.mark.parametrize("metal, sigma, col", [("Al", 3.5e7, "dR_al_mOhm"), ("Cu", 5.8e7, "dR_cu_mOhm")])
def test_shield_eddy_resistance(metal, sigma, col):
    """C's added plate resistance dR agrees with an independent Biot-Savart surface integral within 1 %."""
    w0 = 2 * np.pi * params.f0
    Rs = np.sqrt(w0 * MU0 / (2 * sigma))              # R_s = 1/(sigma delta)
    mid, dl = coil_segments(RADII, z=0.0)
    h, half = 3e-3, 0.20                              # plate grid [m]; coarse but within 1 % here
    x = np.arange(-half, half + h / 2, h)
    X, Y = np.meshgrid(x, x)
    for row in _shield_rows()[:2]:                    # closest gaps (largest loss)
        g = row["gap_mm"] * 1e-3
        B = biot_savart(np.column_stack([X.ravel(), Y.ravel(), np.full(X.size, g)]), mid, dl, 1.0)
        Ht = 2 * np.hypot(B[:, 0], B[:, 1]) / MU0     # image model doubles tangential H
        dR = 2 * 0.5 * Rs * np.sum(Ht ** 2) * h * h   # dR = 2P / |I|^2 at I = 1 A
        assert dR * 1e3 == pytest.approx(row[col], rel=0.01), f"{metal}, g = {row['gap_mm']} mm"
