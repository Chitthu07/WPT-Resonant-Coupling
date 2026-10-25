import numpy as np
import pytest

from sim.circuit import solve


def test_secondary_current_lags_primary_at_resonance():
    """At resonance, I2/I1 should have phase -90 degrees."""
    f0 = 500e3
    L1 = L2 = 15e-6
    C1 = C2 = 1 / ((2 * np.pi * f0) ** 2 * L1)

    I1, I2, Pin, PL, eta = solve(
        f=f0,
        M=0.1 * np.sqrt(L1 * L2),
        L1=L1,
        L2=L2,
        C1=C1,
        C2=C2,
        R1=0.3,
        R2=0.3,
        RL=4.72,
        Vs=5.0,
    )

    phase_difference = np.angle(I2 / I1, deg=True)

    assert phase_difference == pytest.approx(-90.0, abs=1e-6)


def test_efficiency_matches_closed_form_at_resonance():
    """Numerical efficiency should agree with the analytical expression."""
    f0 = 500e3
    L1 = L2 = 15e-6
    C1 = C2 = 1 / ((2 * np.pi * f0) ** 2 * L1)

    R1 = R2 = 0.3
    RL = 4.72
    M = 0.1 * np.sqrt(L1 * L2)

    _, _, _, _, eta_numeric = solve(
        f0, M, L1, L2, C1, C2, R1, R2, RL, 5.0
    )

    w0M2 = (2 * np.pi * f0) ** 2 * M**2

    eta_analytic = (
        w0M2 / (R1 * (R2 + RL) + w0M2)
        * RL / (R2 + RL)
    )

    assert eta_numeric == pytest.approx(eta_analytic, abs=1e-6)


def test_efficiency_approaches_one_for_negligible_losses():
    """With nonzero coupling and positive load, vanishing losses give eta -> 1."""
    f0 = 500e3
    L1 = L2 = 15e-6
    C1 = C2 = 1 / ((2 * np.pi * f0) ** 2 * L1)

    _, _, _, _, eta = solve(
        f=f0,
        M=0.1 * np.sqrt(L1 * L2),
        L1=L1,
        L2=L2,
        C1=C1,
        C2=C2,
        R1=1e-9,
        R2=1e-9,
        RL=4.0,
        Vs=5.0,
    )

    assert eta == pytest.approx(1.0, abs=1e-6)


def test_efficiency_is_zero_without_mutual_coupling():
    """With M=0, no power reaches the secondary load."""
    f0 = 500e3
    L1 = L2 = 15e-6
    C1 = C2 = 1 / ((2 * np.pi * f0) ** 2 * L1)

    _, _, _, PL, eta = solve(
        f=f0,
        M=0.0,
        L1=L1,
        L2=L2,
        C1=C1,
        C2=C2,
        R1=0.3,
        R2=0.3,
        RL=4.0,
        Vs=5.0,
    )

    assert PL == pytest.approx(0.0, abs=1e-12)
    assert eta == pytest.approx(0.0, abs=1e-12)


def test_array_frequency_input():
    """The solver should support frequency arrays."""
    f0 = 500e3
    L1 = L2 = 15e-6
    C1 = C2 = 1 / ((2 * np.pi * f0) ** 2 * L1)

    frequencies = np.array([450e3, 500e3, 550e3])

    I1, I2, Pin, PL, eta = solve(
        f=frequencies,
        M=0.1 * np.sqrt(L1 * L2),
        L1=L1,
        L2=L2,
        C1=C1,
        C2=C2,
        R1=0.3,
        R2=0.3,
        RL=4.72,
        Vs=5.0,
    )

    assert I1.shape == frequencies.shape
    assert I2.shape == frequencies.shape
    assert Pin.shape == frequencies.shape
    assert PL.shape == frequencies.shape
    assert eta.shape == frequencies.shape

    assert np.all(np.isfinite(eta))

# ---------------------------------------------------------------------------------------
# Added tests (reference case from the project brief)
# ---------------------------------------------------------------------------------------
from scipy.signal import find_peaks
from sim.circuit import eta_closed, eta_max, RL_opt, x_factor

F0 = 500e3
L = 15e-6
C = 1 / ((2 * np.pi * F0) ** 2 * L)
MREF = 0.1 * L


def test_reference_case_numbers():
    """Q = 157.1, k^2 Q1 Q2 = 246.7, RL,opt = 4.72 ohm, eta_max = 88.05 %."""
    assert 2 * np.pi * F0 * L / 0.3 == pytest.approx(157.1, abs=0.05)
    assert x_factor(MREF, F0, 0.3, 0.3) == pytest.approx(246.7, abs=0.1)
    assert RL_opt(MREF, F0, 0.3, 0.3) == pytest.approx(4.72, abs=0.01)
    assert eta_max(MREF, F0, 0.3, 0.3) == pytest.approx(0.8805, abs=1e-4)
    eta = solve(F0, MREF, L, L, C, C, 0.3, 0.3, RL_opt(MREF, F0, 0.3, 0.3), 5.0)[4]
    assert eta == pytest.approx(0.8805, abs=1e-4)


def test_split_peaks_low_loss_reference():
    """R1 = R2 = RL = 0.01 ohm (lightly loaded): peaks at 476.7 and 527.0 kHz, k from the peaks = 0.100."""
    f = np.linspace(430e3, 570e3, 140001)
    _, I2, _, _, _ = solve(f, MREF, L, L, C, C, 0.01, 0.01, 0.01, 5.0)
    pk, _ = find_peaks(np.abs(I2))
    assert len(pk) == 2
    fl, fh = f[pk] / 1e3
    assert fl == pytest.approx(476.7, abs=0.1) and fh == pytest.approx(527.0, abs=0.1)
    assert (fh**2 - fl**2) / (fh**2 + fl**2) == pytest.approx(0.100, abs=0.001)


def test_sign_of_M_does_not_matter():
    a = solve(F0, MREF, L, L, C, C, 0.3, 0.3, 4.72, 5.0)
    b = solve(F0, -MREF, L, L, C, C, 0.3, 0.3, 4.72, 5.0)
    assert a[4] == pytest.approx(b[4], abs=1e-12) and a[3] == pytest.approx(b[3], abs=1e-12)


def test_cramer_equals_numpy_linalg_solve():
    f = 480e3
    w = 2 * np.pi * f
    Z1 = 0.3 + 1j * w * L + 1 / (1j * w * C)
    Z2 = 0.3 + 4.72 + 1j * w * L + 1 / (1j * w * C)
    ref = np.linalg.solve(np.array([[Z1, 1j * w * MREF], [1j * w * MREF, Z2]]), [5.0, 0])
    I1, I2, *_ = solve(f, MREF, L, L, C, C, 0.3, 0.3, 4.72, 5.0)
    assert I1 == pytest.approx(ref[0], abs=1e-12) and I2 == pytest.approx(ref[1], abs=1e-12)


def test_eta_vs_RL_peaks_at_RL_opt():
    RL = np.linspace(0.5, 15, 20000)                    # RL array
    eta = solve(F0, MREF, L, L, C, C, 0.3, 0.3, RL, 5.0)[4]
    i = np.argmax(eta)
    assert RL[i] == pytest.approx(4.72, abs=0.01) and eta[i] == pytest.approx(0.8805, abs=1e-4)


def test_M_array_and_C2_array_broadcast():
    M = np.array([0.5e-6, 1.5e-6, 3e-6])
    eta = solve(F0, M, L, L, C, C, 0.3, 0.3, 4.72, 5.0)[4]
    assert eta.shape == M.shape and np.all(np.diff(eta) > 0)
    C2 = C * np.array([0.97, 1.0, 1.03])
    eta2 = solve(F0, MREF, L, L, C, C2, 0.3, 0.3, 4.72, 5.0)[4]
    assert eta2.shape == C2.shape and eta2[1] == pytest.approx(eta_closed(MREF, F0, 0.3, 0.3, 4.72), abs=1e-6)


def test_sanity_table_eta_max_vs_x():
    for x, expect in [(0.1, 0.024), (1, 0.172), (10, 0.537), (100, 0.819), (1000, 0.939)]:
        M = np.sqrt(x * 0.3 * 0.3) / (2 * np.pi * F0)
        assert eta_max(M, F0, 0.3, 0.3) == pytest.approx(expect, abs=0.001)


def test_source_resistance_excluded_from_Pin():
    I1, _, Pin, _, _ = solve(F0, MREF, L, L, C, C, 0.3, 0.3, 4.72, 5.0, Rs=2.0)
    I1n, _, Pin_n, _, _ = solve(F0, MREF, L, L, C, C, 0.3, 0.3, 4.72, 5.0, Rs=0.0)
    assert Pin < Pin_n                                  # less voltage reaches the resonator
    assert Pin == pytest.approx(0.5 * abs(I1) ** 2 * (0.3 + (2 * np.pi * F0 * MREF) ** 2 / 5.02), rel=1e-9)
