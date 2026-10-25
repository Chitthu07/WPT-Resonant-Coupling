"""Closed-form inductances for the coil pair: L (three ways), M(d) and k(d).

Equations (CONVENTIONS.md Section 4):
  Coaxial filament loops (Maxwell, elliptic-integral form):
      M = mu0 sqrt(ab) [ (2/kappa - kappa) K(kappa) - (2/kappa) E(kappa) ],
      kappa^2 = 4ab / [(a+b)^2 + d^2]
      SciPy's ellipk(m), ellipe(m) take m = kappa^2.
  Large-distance (dipole) limit:  M ~ mu0 pi N1 N2 a^2 b^2 / (2 d^3)
  Self-inductance of one round-wire loop:  L ~ mu0 a [ln(8a/r_w) - 2]
  Multi-turn coil (filament sum):  L = sum_i L_ii + sum_{i != j} M_ij
  Flat spiral, Mohan current sheet:
      L = (mu0 N^2 d_avg c1 / 2) [ln(c2/rho) + c3 rho + c4 rho^2]
  Flat spiral, modified Wheeler (octagonal K1=2.25, K2=3.55 as circle approximation):
      L = K1 mu0 N^2 d_avg / (1 + K2 rho)
  Coupling coefficient:  k = M / sqrt(L1 L2)
"""

import numpy as np
from scipy.special import ellipk, ellipe

from sim.params import MU0


def loop_mutual(a, b, d):
    """Mutual inductance [H] of two coaxial filament loops, radii a, b [m], axial spacing d [m]."""
    m = 4 * a * b / ((a + b) ** 2 + d ** 2)        # m = kappa^2 (SciPy convention)
    kappa = np.sqrt(m)
    return MU0 * np.sqrt(a * b) * ((2 / kappa - kappa) * ellipk(m) - (2 / kappa) * ellipe(m))


def loop_mutual_dipole(a, b, d, n1=1, n2=1):
    """Dipole (far-field) approximation of M [H]: mu0 pi N1 N2 a^2 b^2 / (2 d^3)."""
    return MU0 * np.pi * n1 * n2 * a ** 2 * b ** 2 / (2 * d ** 3)


def loop_self(a, r_w):
    """Self-inductance [H] of one circular loop of round wire: mu0 a [ln(8a/r_w) - 2]."""
    return MU0 * a * (np.log(8 * a / r_w) - 2)


def coil_mutual(radii1, radii2, d):
    """M [H] between two coaxial flat spirals d [m] apart: sum over all turn pairs."""
    a = np.asarray(radii1)[:, None]
    b = np.asarray(radii2)[None, :]
    return np.sum(loop_mutual(a, b, d))


def L_filament(radii, r_w):
    """Self-inductance [H] of a flat spiral by the filament sum.

    L = sum_i mu0 a_i [ln(8 a_i / r_w) - 2] + sum_{i != j} M(a_i, a_j, 0)
    Axial spacing between turns is zero (flat spiral); radii differ by the pitch,
    so kappa < 1 and the elliptic formula is finite.
    """
    radii = np.asarray(radii)
    self_part = np.sum(loop_self(radii, r_w))
    i, j = np.where(~np.eye(len(radii), dtype=bool))   # all ordered pairs with i != j
    mutual_part = np.sum(loop_mutual(radii[i], radii[j], 0.0))
    return self_part + mutual_part


def spiral_d_in(radii, wire_d):
    """Inner diameter [m] of the winding (inner edge of the innermost turn)."""
    return 2 * np.min(radii) - wire_d


def L_mohan(n, d_out, d_in, c1=1.00, c2=2.46, c3=0.00, c4=0.20):
    """Mohan current-sheet formula for a circular flat spiral [H]."""
    d_avg = (d_out + d_in) / 2
    rho = (d_out - d_in) / (d_out + d_in)
    return MU0 * n ** 2 * d_avg * c1 / 2 * (np.log(c2 / rho) + c3 * rho + c4 * rho ** 2)


def L_wheeler(n, d_out, d_in, K1=2.25, K2=3.55):
    """Modified Wheeler formula for a flat spiral [H].

    Mohan (1999) gives no circular coefficients. Default = octagonal (K1=2.25, K2=3.55),
    the closest polygon to a circle; square is K1=2.34, K2=2.75 (overestimates a circle ~4/pi).
    """
    d_avg = (d_out + d_in) / 2
    rho = (d_out - d_in) / (d_out + d_in)
    return K1 * MU0 * n ** 2 * d_avg / (1 + K2 * rho)


def coupling(M, L1, L2):
    """k = M / sqrt(L1 L2)."""
    return M / np.sqrt(L1 * L2)


def loglog_slope(f, d1, d2):
    """Local log-log slope d(ln f)/d(ln d) between distances d1 and d2."""
    return (np.log(f(d2)) - np.log(f(d1))) / (np.log(d2) - np.log(d1))
