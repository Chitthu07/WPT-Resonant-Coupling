"""Member A cross-check of C-T2 Section 3.1: proximity-effect resistance of the 10-turn spiral.

Model (per turn i, each wire treated as a straight round conductor of radius r_w in the
uniform transverse field of all OTHER turns, I = 1 A peak):
  Field at turn i, coplanar loops (elliptic form, m = 4 a rho / (a + rho)^2):
      H_z(a -> rho) = I / (2 pi (a + rho)) [ K(m) + (a^2 - rho^2)/(a - rho)^2 E(m) ]
      cross-checked with the Biot-Savart segment sum of sim/fieldmap.py
  Thin-skin (surface impedance) limit, surface field H_phi = 2 H sin(phi), R_s = 1/(sigma delta):
      P' = 1/2 R_s * integral_0^2pi (2 H sin phi)^2 r_w dphi = 2 pi r_w R_s H^2      (per metre)
  Exact cylinder at finite r_w/delta (Bessel), k = (1 - j)/delta:
      A_z = c J1(k rho) cos(phi),  c = 2 mu0 H / (k J0(k r_w)),  P' = 1/2 integral |J|^2 / sigma dA
  Resistance: R_prox = 2 P_total / I^2,  P_total = sum_i P'_i * 2 pi r_i
Neglected: field non-uniformity across the wire (spacing 1 mm vs r_w = 0.35 mm) and the screening
by eddy currents in the neighbouring wires, so the result is an estimate, not a bound.

Run from the project root:  python -m sim.proximity_check
"""

import numpy as np
from scipy.special import ellipk, ellipe, jv
from scipy.integrate import quad

from sim import params
from sim.params import MU0
from sim.coupling import coil_segments
from sim.fieldmap import biot_savart

SIGMA_CU = 5.8e7                     # copper conductivity [S/m]


def h_coplanar(a, rho):
    """Axial field [A/m per A] in the plane of a loop of radius a, at radius rho != a."""
    m = 4 * a * rho / (a + rho) ** 2
    return (ellipk(m) + (a ** 2 - rho ** 2) / (a - rho) ** 2 * ellipe(m)) / (2 * np.pi * (a + rho))


def field_from_other_turns(radii):
    """H_ext at each turn from all other turns (elliptic form) [A/m per A]."""
    return np.array([sum(h_coplanar(a, ri) for a in np.delete(radii, i)) for i, ri in enumerate(radii)])


def loss_per_length_thin(r_w, Rs):
    """Thin-skin loss per metre per (A/m)^2 of transverse field: 2 pi r_w R_s."""
    return 2 * np.pi * r_w * Rs


def loss_per_length_bessel(r_w, delta, w0, sigma):
    """Exact loss per metre per (A/m)^2 for a round conductor in a uniform transverse field."""
    k = (1 - 1j) / delta
    c = 2 * MU0 / (k * jv(0, k * r_w))
    radial = quad(lambda p: abs(jv(1, k * p)) ** 2 * p, 0, r_w, limit=200)[0]
    return 0.5 * w0 ** 2 * sigma * abs(c) ** 2 * np.pi * radial     # J = -j w sigma A_z


def main():
    g = params.get_geometry()
    radii, r_w = g["radii"], g["wire_d"] / 2
    w0 = 2 * np.pi * params.f0
    delta = np.sqrt(2 / (w0 * MU0 * SIGMA_CU))
    Rs = 1 / (SIGMA_CU * delta)
    print("=== Proximity resistance cross-check (C-T2 Section 3.1) ===")
    print(f"delta = {delta*1e3:.4f} mm, R_s = {Rs*1e3:.4f} mOhm, r_w/delta = {r_w/delta:.3f}")

    H = field_from_other_turns(radii)
    H_bs = []                                                # Biot-Savart check, fine segments
    for i, ri in enumerate(radii):
        mid, dl = coil_segments(np.delete(radii, i), z=0.0, n_seg=6000)
        H_bs.append(biot_savart(np.array([[ri, 0.0, 0.0]]), mid, dl, 1.0)[0, 2] / MU0)
    print("H_ext per turn, elliptic    [A/m]:", np.round(H, 1))
    print("H_ext per turn, Biot-Savart [A/m]:", np.round(H_bs, 1))
    S = np.sum(H ** 2 * 2 * np.pi * radii)
    print(f"sum_i H_i^2 (2 pi r_i) = {S:.4e} 1/m")

    p_thin = loss_per_length_thin(r_w, Rs)
    p_bes = loss_per_length_bessel(r_w, delta, w0, SIGMA_CU)
    print(f"R_prox, thin-skin limit  = {2 * p_thin * S:.4f} ohm")
    print(f"R_prox, exact cylinder   = {2 * p_bes * S:.4f} ohm  (Bessel / thin-skin = {p_bes / p_thin:.3f})")


if __name__ == "__main__":
    main()
