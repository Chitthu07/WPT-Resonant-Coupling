# Project conventions and equation reference

The code docstrings and the notes in `theory/` refer to the sections of this file.

## Section 2: conventions (used by every script)

- **d** is the spacing between the two coil planes along the common axis (coaxial unless stated). Test distances: 1, 2, 3, 4, 5, 6, 8, 10 cm.
- **Q** always means the unloaded quality factor Q = ω0 L / R, with R the total series resistance of that resonator. The load R_L is separate.
- **η_link** is the AC link efficiency: load power / power into the primary resonator terminals. (η_sys, DC to DC, is not computed: no hardware was built.)
- SI units inside the code; plots in cm, kHz, Ω, µH, %. Every axis has units and every plot a legend.
- Plot colours: **theory = blue solid line, simulation = orange dashed line, measurement/LTspice = black markers.**
- Figure names: `fig_<quantity>_vs_<variable>` as vector PDF plus a 300 dpi PNG.

## Section 3: parameters

All project numbers live in `sim/params.py` (SI units). Geometry: flat circular spiral, N = 10, outer diameter 100 mm,
wire diameter 0.7 mm, pitch 1.0 mm; turn i (i = 0 … N−1) has centreline radius r_i = d_out/2 − wire_d/2 − i·pitch.
`get_geometry()` builds the turn radii so every script uses the same geometry.

## Section 4: equation reference

- Ampère, quasi-static: ∇ × H = J + ∂D/∂t ≈ J (coil much smaller than the 600 m wavelength).
- Faraday: v2 = −M di1/dt; |V2| = ω M |I1| (open secondary).
- Biot–Savart: B(r) = (µ0 I / 4π) ∮ dl × r̂ / r².
- On-axis field of an N-turn loop: Bz(z) = µ0 N I a² / [2 (a² + z²)^(3/2)].
- Neumann: M = (µ0 / 4π) ∮∮ (dl1 · dl2) / r.
- Coaxial filament loops: M = µ0 √(ab) [ (2/κ − κ) K(κ) − (2/κ) E(κ) ], κ² = 4ab / [(a+b)² + d²]
  (SciPy `ellipk(m)`, `ellipe(m)` take m = κ²). Multi-turn coils: sum over all turn pairs.
- Large-distance (dipole) limit: M ≈ µ0 π N1 N2 a² b² / (2 d³).
- Self-inductance of one filament loop: L ≈ µ0 a [ln(8a/r_w) − 2]. Multi-turn: L = Σ L_ii + Σ_{i≠j} M_ij.
- Coupling: k = M / √(L1 L2).
- Resonance: f0 = 1 / (2π √(LC)); Q = ω0 L / R.
- Efficiency at f0: η = [ω0² M² / (R1 (R2 + R_L) + ω0² M²)] · [R_L / (R2 + R_L)].
- With x = k² Q1 Q2 and r = R_L / R2: η = x r / [(1 + r)(1 + r + x)]; r_opt = √(1 + x); η_max = x / (1 + √(1 + x))².
- Flat spiral inductance: Mohan current-sheet L = (µ0 N² d_avg c1 / 2) [ln(c2/ρ) + c3 ρ + c4 ρ²] with circular
  coefficients c1 = 1.00, c2 = 2.46, c3 = 0, c4 = 0.20; modified Wheeler L = K1 µ0 N² d_avg / (1 + K2 ρ) has no circular
  coefficients (octagonal K1 = 2.25, K2 = 3.55 used as the closest polygon), ρ = (d_out − d_in)/(d_out + d_in).

### Reference test case (checks every circuit formula)

L1 = L2 = 15 µH, f0 = 500 kHz so C1 = C2 = 6.755 nF, R1 = R2 = 0.3 Ω, k = 0.1 (M = 1.5 µH):
Q = 157.1, k² Q1 Q2 = 246.7, R_L,opt = 4.72 Ω, η_max = 88.05 %.
Best possible η against x = k² Q1 Q2: 0.1 → 2.4 %, 1 → 17.2 %, 10 → 53.7 %, 100 → 81.9 %, 1000 → 93.9 %.

## Section 6: task list

| Member | Tasks |
|---|---|
| A (magnetic link) | A-C1 closed-form L, M(d), k(d); A-S1 numerical Neumann M(d); A-S2 lateral misalignment; A-S3 field map; A-V1 comparison |
| B (circuit) | B-0 design; B-T1/B-T2 coupled-resonator theory and optimal load; B-S1–B-S3 circuit simulations; B-C1 stress; B-V1 validation incl. LTspice |
| C (losses, validation) | C-T1 frequency response; C-T2 loss mechanisms and Q; C-C1 closed-form η; C-S1 LTspice; C-S2 shielding; C-S3 figure pipeline; C-V1 limitations |
