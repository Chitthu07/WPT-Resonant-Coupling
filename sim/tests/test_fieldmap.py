"""Tests for A-S3 (sim/fieldmap.py): on-axis Biot-Savart vs closed form, monotonic decay, symmetry."""

import numpy as np

from sim import params
from sim.coupling import coil_segments
from sim.fieldmap import biot_savart, bz_axis_closed_form, field_on_grid

RADII = params.get_geometry()["radii"]
MID, DL = coil_segments(RADII, z=0.0)


def _axis(z):
    return np.column_stack([np.zeros_like(z), np.zeros_like(z), z])


def test_on_axis_matches_closed_form():
    """Numerical Bz on the axis within 1 % of sum_i mu0 I a_i^2 / [2 (a_i^2 + z^2)^1.5]."""
    z = np.array([-0.05, -0.02, 0.0, 0.01, 0.03, 0.05, 0.10, 0.15])
    Bz = biot_savart(_axis(z), MID, DL)[:, 2]
    Bcf = bz_axis_closed_form(RADII, z)
    assert np.all(np.abs(Bz - Bcf) / Bcf < 0.01)


def test_axis_field_decreases_away_from_primary():
    """|B| on the axis strictly decreases for z > 0 and for z < 0."""
    z = np.linspace(0, 0.15, 76)
    for sgn in (1, -1):
        B = np.linalg.norm(biot_savart(_axis(sgn * z), MID, DL), axis=1)
        assert np.all(np.diff(B) < 0)


def test_mirror_symmetry():
    """|B|(x, z) = |B|(-x, z) on a symmetric grid."""
    x = np.linspace(-0.15, 0.15, 61)
    z = np.linspace(-0.05, 0.15, 21)
    Bx, Bz = field_on_grid(RADII, x, z)
    Bmag = np.hypot(Bx, Bz)
    assert np.max(np.abs(Bmag - Bmag[:, ::-1]) / Bmag) < 1e-9
