"""Helpers shared by the circuit scripts (B-S1, B-S2, B-S3, B-C1).

  ROOT          repository root
  M_of_d(d_cm)  mutual inductance from data/sim_M_k.csv (A-S1), linear interpolation
  k_of_d(d_cm)  coupling coefficient from the same file
  fixed_load()  fixed load R_L used by the circuit scripts
"""

from pathlib import Path

import numpy as np
import pandas as pd

from sim import params
from sim.circuit import RL_opt

ROOT = Path(__file__).resolve().parent.parent
_MK = ROOT / "data" / "sim_M_k.csv"


def _table():
    if not _MK.exists():
        raise FileNotFoundError(f"{_MK} not found. Run `python -m sim.coupling` first (task A-S1).")
    df = pd.read_csv(_MK)
    return df["d_cm"].to_numpy(), df["M_H"].to_numpy(), df["k"].to_numpy()


def _interp_checked(d_cm, d, y):
    """Linear interpolation; raises ValueError outside the tabulated range."""
    d_cm = np.asarray(d_cm, dtype=float)
    if np.any(d_cm < d.min()) or np.any(d_cm > d.max()):
        raise ValueError(f"d = {d_cm} cm is outside the A-S1 sweep {d.min()}..{d.max()} cm.")
    out = np.interp(d_cm, d, y)
    return float(out) if out.ndim == 0 else out


def M_of_d(d_cm):
    """Mutual inductance [H] at coil spacing d_cm [cm] (scalar or array), from data/sim_M_k.csv."""
    d, M, _ = _table()
    return _interp_checked(d_cm, d, M)


def k_of_d(d_cm):
    """Coupling coefficient k at coil spacing d_cm [cm] (scalar or array), from data/sim_M_k.csv."""
    d, _, k = _table()
    return _interp_checked(d_cm, d, k)


def fixed_load():
    """Fixed load [ohm]: params.RL_fixed if set, otherwise R_L,opt at params.d_RL_fixed.

    This is the efficiency-optimal load at one spacing, not the power-optimal load (B-T2 Section 5).
    """
    if params.RL_fixed is not None:
        return float(params.RL_fixed)
    M = M_of_d(params.d_RL_fixed * 100)
    return float(RL_opt(M, params.f0, params.R1, params.R2))
