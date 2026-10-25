"""Circuit solver for a series-series resonant WPT link (B-S1).

Solves the coupled primary and secondary circuits with complex phasors.
All voltages and currents are peak-value phasors; powers are average real powers.

    (Z1 + Rs) I1 + j w M I2 = Vs
    j w M I1      + Z2 I2   = 0

f, M, C1, C2, R1, R2, RL and Vs may be scalars OR NumPy arrays; they broadcast together
(for example M(d) array at one f, RL array at one M, C2 array for a detuning study).
The 2x2 system is solved exactly by Cramer's rule, which is the same solution as
numpy.linalg.solve (checked in tests/test_circuit.py) but works on whole arrays at once.
"""

from collections import namedtuple

import numpy as np

# Behaves exactly like the plain tuple (I1, I2, Pin, PL, eta) but also allows r.eta, r.PL ...
Result = namedtuple("Result", "I1 I2 Pin PL eta")


def solve(f, M, L1, L2, C1, C2, R1, R2, RL, Vs, Rs=0):
    """Return (I1, I2, Pin, PL, eta).

    Pin is the power into the primary RESONATOR terminals: 0.5*Re[(Vs - Rs*I1) * conj(I1)].
    PL = 0.5*|I2|^2*RL and eta = PL/Pin (0 where Pin <= 0).
    Scalar inputs give plain Python scalars; array inputs give arrays.
    The result unpacks like a tuple: I1, I2, Pin, PL, eta = solve(...)  (or use r.eta, r.PL ...).
    """
    f_a, M_a, C1_a, C2_a = (np.asarray(v, dtype=float) for v in (f, M, C1, C2))
    R1_a, R2_a, RL_a, Rs_a = (np.asarray(v, dtype=float) for v in (R1, R2, RL, Rs))
    if np.any(f_a <= 0):
        raise ValueError("Frequency f must be positive.")
    if np.any(np.asarray(L1) <= 0) or np.any(np.asarray(L2) <= 0):
        raise ValueError("Inductances L1 and L2 must be positive.")
    if np.any(C1_a <= 0) or np.any(C2_a <= 0):
        raise ValueError("Capacitances C1 and C2 must be positive.")
    if np.any(R1_a < 0) or np.any(R2_a < 0) or np.any(Rs_a < 0):
        raise ValueError("Resistances R1, R2 and Rs cannot be negative.")
    if np.any(RL_a <= 0):
        raise ValueError("Load resistance RL must be positive.")

    w = 2 * np.pi * f_a
    Z1 = R1_a + 1j * w * L1 + 1 / (1j * w * C1_a) + Rs_a     # Rs sits in the primary loop
    Z2 = R2_a + RL_a + 1j * w * L2 + 1 / (1j * w * C2_a)
    Zm = 1j * w * M_a

    det = Z1 * Z2 - Zm * Zm
    I1 = np.asarray(Vs, dtype=complex) * Z2 / det
    I2 = -np.asarray(Vs, dtype=complex) * Zm / det

    V_res = Vs - Rs_a * I1                                     # voltage at the resonator terminals
    Pin = 0.5 * np.real(V_res * np.conjugate(I1))
    PL = 0.5 * np.abs(I2) ** 2 * RL_a
    eta = np.divide(PL, Pin, out=np.zeros(np.shape(PL), dtype=float), where=np.asarray(Pin) > 0)

    if np.ndim(I1) == 0:
        return Result(I1.item(), I2.item(), float(Pin), float(PL), float(eta))
    return Result(I1, I2, Pin, PL, eta)


# ---- closed forms at f0 (B-T2); used for cross-checks -------------------------------------
def x_factor(M, f0, R1, R2):
    """x = k^2 Q1 Q2 = w0^2 M^2 / (R1 R2)."""
    return (2 * np.pi * f0) ** 2 * np.asarray(M, dtype=float) ** 2 / (R1 * R2)


def eta_closed(M, f0, R1, R2, RL):
    """eta at resonance = [w0^2M^2/(R1(R2+RL)+w0^2M^2)] * [RL/(R2+RL)]."""
    w0M2 = (2 * np.pi * f0) ** 2 * np.asarray(M, dtype=float) ** 2
    return w0M2 / (R1 * (R2 + RL) + w0M2) * RL / (R2 + RL)


def RL_opt(M, f0, R1, R2):
    """Load for maximum efficiency, R2*sqrt(1+x)."""
    return R2 * np.sqrt(1 + x_factor(M, f0, R1, R2))


def eta_max(M, f0, R1, R2):
    """Maximum efficiency x/(1+sqrt(1+x))^2."""
    x = x_factor(M, f0, R1, R2)
    return x / (1 + np.sqrt(1 + x)) ** 2


def k_crit(L1, L2, f0, R1, R2, RL, Rs=0):
    """Critical coupling kc = 1/sqrt(Q1*Q2L), Q1 = w0 L1/(R1+Rs), Q2L = w0 L2/(R2+RL).

    Condition: w0^2 M^2 = (R1 + Rs)(R2 + RL). For a fixed RL, P_L(M) is largest here.
    """
    w0 = 2 * np.pi * f0
    return 1 / np.sqrt((w0 * L1 / (R1 + Rs)) * (w0 * L2 / (R2 + RL)))
