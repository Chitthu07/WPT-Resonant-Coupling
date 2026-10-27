# Wireless Power by Resonant Magnetic Coupling

EE2025 Engineering Electromagnetics course project, Department of Electrical Engineering, IIT Madras.
**Team:** Chittharanjan S (magnetic link), Deekshitha R (circuit), Dani Firas Payyanakadavan (losses and validation).

Two identical 10-turn, 10 cm air-core spiral coils, each series-tuned to 500 kHz, transfer power across a 1–10 cm gap.
This repository contains every model, simulation, figure and write-up behind our poster
(**[`poster/EM_WPT_poster.pdf`](poster/EM_WPT_poster.pdf)**, A0; source `poster/EM_WPT_poster_v2_portrait.pptx`). No prototype was built: validation is model against model
(closed form ↔ numerical ↔ LTspice).

## Key results

Design: N = 10, d_out = 100 mm, wire 0.7 mm, pitch 1.0 mm, L = 17.13 µH, C = 5.915 nF, f0 = 500 kHz,
R = 0.455 Ω per resonator (skin 0.269 + proximity 0.136 + capacitor ESR 0.035 + joints 0.015 Ω), Q = 118.3,
load R_L = 6.0 Ω, source 5 V peak (ideal).

| d (cm) | M (µH) | k | η_max (R_L,opt) | η at 6 Ω | P_L at 6 Ω (W) |
|---:|---:|---:|---:|---:|---:|
| 1 | 8.79 | 0.513 | 96.8 % (27.6 Ω) | 92.6 % | 0.098 |
| 3 | 3.72 | 0.217 | 92.5 % (11.7 Ω) | 91.0 % | 0.526 |
| 5 | 1.90 | 0.111 | 85.9 % (6.00 Ω) | 85.9 % | 1.79 |
| 10 | 0.51 | 0.030 | 57.2 % (1.67 Ω) | 43.5 % | 6.36 |

- **Two independent M methods agree:** elliptic-integral closed form vs numerical Neumann sum, ≤ 0.05 % over 0.5–15 cm
  (Richardson extrapolation of the Neumann sum hits the closed form to < 10⁻⁶).
- **Circuit solver vs LTspice** (`sim/wpt.asc`): agreement to 5 × 10⁻¹⁰ % at 2, 5, 10 cm, 350–650 kHz; i2 lags i1 by 90° at f0.
- **Maximum efficiency ≠ maximum power:** P_L at the fixed 6 Ω load peaks at 6.4 W near 9.75 cm (critical coupling
  k_c = 0.0318), not where η is highest.
- **Split peaks:** with a lightly loaded secondary, f± = f0/√(1 ± k) returns k within 0.3 %; with the 6 Ω load the
  peaks are pulled together and k reads 35 % low at 5 cm.
- **Lateral misalignment:** M changes sign at Δx = 8.22 cm (d = 3 cm), where the primary's return flux cancels its
  forward flux through the secondary.
- **Shielding:** an aluminium plate 5 mm behind the receiver cuts k by 56 % and adds 178 mΩ; η at 3 cm drops from
  92.5 % to 24 % (64 % with C2 retuned). Ferrite backing raises k by 34 %.

## Run it

Tested with Python 3.12 (numpy 2.5, scipy 1.18, matplotlib 3.11, pandas 3.0).

```bash
python -m pip install -r requirements.txt
python -m sim.make_figures          # regenerates every CSV in data/ and every figure in figs/ (about 1 minute)
python -m pytest sim/tests -q       # 84 tests
```

Individual steps (all from the repository root):

| Command | What it does |
|---|---|
| `python -m sim.run_analytic` | closed-form L (filament sum, Mohan, Wheeler), M(d), k(d) → `theory/hand_values.csv` |
| `python -m sim.coupling` | numerical Neumann M(d), k(d) → `data/sim_M_k.csv`, `fig_M_vs_d`, `fig_k_vs_d` |
| `python -m sim.misalignment` | signed M(Δx), η(Δx), P_L(Δx) → `fig_k_vs_dx`, `fig_eta_vs_dx`, `fig_PL_vs_dx` |
| `python -m sim.fieldmap` | Biot–Savart \|B\| map with streamlines → `fig_B_map` |
| `python -m sim.compare` | analytical vs simulation table → `data/compare_table.md` |
| `python -m sim.run_circuit`, `freq_response`, `load_sweep`, `stress` | 2×2 phasor circuit: η(d), P_L(d), η(f), η(R_L), component stress |
| `python -m sim.compare_circuit` | solver vs closed forms, split peaks, R sensitivity band |
| `python -m sim.compare_ltspice` | LTspice vs solver from the saved `data/ltspice_ac.csv` (`--run` reruns LTspice; needs LTspice, under Wine on Linux) |
| `python -m sim.shield` | metal plate / ferrite backing (image model) |
| `python -m sim.proximity_check` | proximity-effect resistance of the spiral (thin-skin and exact Bessel) |
| `python -m sim.run_ab` | all Member A and B scripts in dependency order (called by `make_figures`) |

## Repository layout

```
sim/        all models and scripts; sim/params.py holds every project number; sim/wpt.asc is the LTspice schematic
sim/tests/  pytest suite (84 tests: closed form vs numerical, circuit vs closed form, LTspice, consistency guards)
data/       simulation outputs (CSV)
figs/       figures (vector PDF + 300 dpi PNG)
theory/     derivations, design notes and validation write-ups (A-*, B-*, C-* by task)
poster/     poster (.pptx), its figures and the scripts that fill it
media/      LTspice transient screenshot
```

Conventions (symbols, plot colours, equation reference, reference test case) are in `CONVENTIONS.md`.

## References

1. A. Kurs, A. Karalis, R. Moffatt, J. D. Joannopoulos, P. Fisher and M. Soljačić, "Wireless power transfer via strongly
   coupled magnetic resonances," *Science*, vol. 317, no. 5834, pp. 83–86, 2007.
2. A. P. Sample, D. A. Meyer and J. R. Smith, "Analysis, experimental results, and range adaptation of magnetically
   coupled resonators for wireless power transfer," *IEEE Trans. Ind. Electron.*, vol. 58, no. 2, pp. 544–554, 2011.
3. S. Y. R. Hui, W. Zhong and C. K. Lee, "A critical review of recent progress in mid-range wireless power transfer,"
   *IEEE Trans. Power Electron.*, vol. 29, no. 9, pp. 4500–4511, 2014.
4. R. K. Shevgaonkar, *Electromagnetic Waves*, Tata McGraw-Hill, 2006.
