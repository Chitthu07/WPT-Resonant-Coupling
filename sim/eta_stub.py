"""STUB — closed-form link efficiency at resonance. To be REPLACED by Member B's sim/circuit.py solve(...).

Series-series link driven at f0 (both resonators tuned to f0), CONVENTIONS.md Section 4:
    eta_link = [w0^2 M^2 / (R1 (R2 + R_L) + w0^2 M^2)] * [R_L / (R2 + R_L)]
Optimum load for a given M (with x = k^2 Q1 Q2 = w0^2 M^2 / (R1 R2)):
    R_L,opt = R2 sqrt(1 + x)
Only M^2 appears, so the sign of M does not matter for efficiency.
"""

import numpy as np


def eta_link(M, f0, R1, R2, RL):
    """AC link efficiency (load power / primary-terminal input power) at f0."""
    w0M2 = (2 * np.pi * f0) ** 2 * np.asarray(M) ** 2
    return w0M2 / (R1 * (R2 + RL) + w0M2) * RL / (R2 + RL)


def RL_opt(M, f0, R1, R2):
    """Load that maximises eta_link for this M: R2 sqrt(1 + w0^2 M^2 / (R1 R2))."""
    x = (2 * np.pi * f0) ** 2 * M ** 2 / (R1 * R2)
    return R2 * np.sqrt(1 + x)
