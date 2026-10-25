"""Project parameters for the resonant inductive WPT link (series-series).

This is the ONE place where every project number lives (SI units only).
Unknown values are None until they are decided (design) or measured (bench).
Scripts must import from here and never hard-code project numbers.

Geometry convention (flat circular spiral, CONVENTIONS.md Section 3):
    turn i (i = 0 .. N-1) has centreline radius
        r_i = d_out/2 - wire_d/2 - i * pitch
    and all turns of a flat spiral lie in one plane (axial position z = 0
    relative to the coil plane).
"""

import numpy as np

PARAMS_VERSION = "v1-design"   # set to "v2-measured" by the student after bench work

# ---------------------------------------------------------------------------
# Physical constant
# ---------------------------------------------------------------------------
MU0 = 4e-7 * np.pi             # permeability of free space [H/m]

# ---------------------------------------------------------------------------
# Operating point
# ---------------------------------------------------------------------------
f0 = 500e3                    # design resonant frequency [Hz]

# ---------------------------------------------------------------------------
# Coil geometry (both coils identical)
# ---------------------------------------------------------------------------
N = 10                        # number of turns
d_out = 0.10                  # outer diameter [m]
d_in = None                   # derived from turns, pitch and wire geometry
pitch = 1.0e-3                # turn pitch [m]
wire_d = 0.7e-3               # conductor diameter [m]

# ---------------------------------------------------------------------------
# Circuit values (design estimates, not measurements)
# ---------------------------------------------------------------------------
# L1, L2: filament-sum value for the geometry above (A-C1, python -m sim.run_analytic)
L1 = 17.13e-6                 # primary inductance [H]
L2 = 17.13e-6                 # secondary inductance [H]

# R1, R2: skin (0.269) + proximity (0.136, exact Bessel, sim/proximity_check.py) + capacitor ESR (0.035)
# + joints (0.015) at f0. C-T2 budget with the proximity term computed (2026-10-25); was 0.40 ohm before.
R1 = 0.455                    # primary total series resistance [ohm]
R2 = 0.455                    # secondary total series resistance [ohm]
R_range = (0.38, 0.48)        # expected range of R1 = R2 (C-T2 budget, computed proximity loss) [ohm]

# Tune both resonators to f0
C1 = 1 / ((2 * np.pi * f0)**2 * L1)
C2 = 1 / ((2 * np.pi * f0)**2 * L2)


# ---------------------------------------------------------------------------
# Source and load used by the circuit simulations (B-S1, B-S2, B-S3, B-C1)
# ---------------------------------------------------------------------------
Vs = 5.0                      # source amplitude [V peak]
Rs = 0.0                      # source resistance [ohm] (0 = ideal voltage source)
Rs_gen = 50.0                 # function-generator output resistance [ohm]
RL_fixed = 6.0                # fixed load [ohm], chosen in C-C1 (R_L,opt at 5 cm); None -> R_L,opt at d_RL_fixed
d_RL_fixed = 5e-2             # spacing for the default fixed load [m]
rect_factor = 8 / np.pi**2    # full-bridge rectifier + C filter: R_ac = 0.81 R_DC

# ---------------------------------------------------------------------------
# Sweeps
# ---------------------------------------------------------------------------
distances = np.array([1, 2, 3, 4, 5, 6, 8, 10]) * 1e-2   # coil-plane spacing d [m]
RL_list = np.array([0.5, 1, 2, 4, 6, 8, 12, 20, 30])    # list of load resistances to test [ohm]

# Coil spacings chosen for each analysis task (CONVENTIONS.md Section 6) [m]
d_hand = np.array([1, 2, 3, 5, 8, 10]) * 1e-2          # A-C1 hand-value table
d_sweep = np.arange(0.5, 15.0 + 1e-9, 0.25) * 1e-2     # A-S1 numerical sweep (0.5 .. 15 cm, 0.25 cm steps)
d_misalign = np.array([3.0, 5.0]) * 1e-2               # A-S2 axial spacings for the misalignment study
dx_max = 10e-2                                         # A-S2 largest lateral offset
d_fieldmap = 3e-2                                      # A-S3 secondary position in the field map

# ---------------------------------------------------------------------------
# Placeholder geometry (CONVENTIONS.md Section 3). Used ONLY if the student
# answers "use placeholder"; every output built from it must be labelled
# "PLACEHOLDER GEOMETRY".
# ---------------------------------------------------------------------------
PLACEHOLDER = {
    "N": 10,
    "d_out": 0.10,             # [m]
    "wire_d": 0.7e-3,          # [m]
    "pitch": 1.0e-3,           # [m]
    "f0": 500e3,               # [Hz]
    "R1": 0.3,                 # [ohm]
    "R2": 0.3,                 # [ohm]
}


def turn_radii(n_turns, outer_diameter, wire_diameter, turn_pitch):
    """Centreline radius of each turn of a flat spiral [m].

    r_i = d_out/2 - wire_d/2 - i * pitch,  i = 0 .. N-1   (outermost turn first)
    """
    i = np.arange(n_turns)
    r = outer_diameter / 2 - wire_diameter / 2 - i * turn_pitch
    if np.any(r <= 0):
        raise ValueError("Geometry gives a non-positive turn radius; check N, pitch, d_out.")
    return r


def turn_z(n_turns, z_coil=0.0):
    """Axial position of each turn [m]. Flat spiral: all turns at the coil plane z_coil."""
    return np.full(n_turns, float(z_coil))


def get_geometry(use_placeholder=None):
    """Return a dict with the coil geometry used by every script.

    Keys: N, d_out, wire_d, pitch, radii (array, m), placeholder (bool).
    use_placeholder=None (default): use the real geometry if N is set, else the placeholder.
    Raises if use_placeholder is False and a needed value is None.
    """
    if use_placeholder is None:
        use_placeholder = N is None
    if use_placeholder:
        g = PLACEHOLDER
        n, dout, wd, p = g["N"], g["d_out"], g["wire_d"], g["pitch"]
    else:
        n, dout, wd, p = N, d_out, wire_d, pitch
        missing = [k for k, v in {"N": n, "d_out": dout, "wire_d": wd, "pitch": p}.items() if v is None]
        if missing:
            raise ValueError(f"Geometry values are None in params.py: {missing}. "
                             "Fill them in or call get_geometry(use_placeholder=True).")
    radii = turn_radii(n, dout, wd, p)
    return {"N": n, "d_out": dout, "wire_d": wd, "pitch": p,
            "radii": radii, "placeholder": use_placeholder}


def get_circuit(use_placeholder=None):
    """Return f0 [Hz], R1, R2 [ohm] as a dict (+ placeholder flag).

    use_placeholder=None (default): use the values above if all are set, else the placeholder ones.
    """
    if use_placeholder is None:
        use_placeholder = f0 is None or R1 is None or R2 is None
    if use_placeholder:
        g = PLACEHOLDER
        return {"f0": g["f0"], "R1": g["R1"], "R2": g["R2"], "placeholder": True}
    return {"f0": f0, "R1": R1, "R2": R2, "placeholder": False}
