# B-0: Design Parameter Proposal

## 1. Selected design

The proposed wireless power transfer system uses two identical
flat circular spiral coils in a series-series resonant topology.

| Parameter | Symbol | Value |
|---|---|---:|
| Number of turns | N | 10 |
| Outer coil diameter | d_out | 0.10 m |
| Wire diameter | wire_d | 0.7 mm |
| Turn pitch | pitch | 1.0 mm |
| Operating frequency | f0 | 500 kHz |
| Primary inductance | L1 | 17.13 µH |
| Secondary inductance | L2 | 17.13 µH |
| Primary series resistance | R1 | 0.455 Ω (C-T2 nominal; range 0.38–0.48 Ω) |
| Secondary series resistance | R2 | 0.455 Ω (C-T2 nominal; range 0.38–0.48 Ω) |
| Primary resonant capacitance | C1 | 5.915 nF |
| Secondary resonant capacitance | C2 | 5.915 nF |

## 2. Design rationale

The coil geometry follows the existing simulation configuration:
10 turns, 10 cm outer diameter, 0.7 mm wire diameter, and
1 mm pitch.

The inductance values of 17.13 µH are taken from the existing
filament-sum calculation documented in theory/hand_values_note.md.
These are calculated values, not physical measurements.

Both resonators are tuned to 500 kHz using

C = 1 / ((2*pi*f0)^2 * L)

This gives a resonant capacitance of approximately 5.915 nF
for each coil.

The primary and secondary series resistances are set to 0.455 Ω.
The loss analysis C-T2 (skin 0.269, proximity 0.136, capacitor ESR 0.035, joints 0.015 Ω)
gives 0.38–0.48 Ω with a nominal 0.455 Ω. (Until 2026-10-25 the value was 0.40 Ω; the
proximity term is now computed instead of estimated, `python -m sim.proximity_check`.)

## 3. Estimated quality factor and bandwidth

Using

Q = 2*pi*f0*L/R

the estimated unloaded quality factor is approximately 118.3
for each resonator.

The approximate resonator bandwidth is

BW = f0/Q

giving approximately 4.23 kHz.

These estimates depend on the resistance; over the C-T2 range
0.38–0.48 Ω, Q is 112–142 and the bandwidth 3.53–4.46 kHz.

## 4. Coupling and efficiency predictions

The existing numerical coupling data gives the following
analytical maximum-efficiency predictions, using the assumed
quality factors and the optimal load at each distance.

| Coil spacing | Coupling coefficient | Predicted maximum efficiency |
|---|---:|---:|
| 1 cm | 0.513124 | 96.76% |
| 5 cm | 0.111189 | 85.90% |
| 10 cm | 0.029895 | 57.21% |

These are theoretical predictions, not measured efficiencies.
The optimal load may differ at each distance.

## 5. Candidates considered and recommendation

Same estimate method for all three (Wheeler/filament L, R = 1.5 x skin-effect resistance + 0.05 ohm,
f0 = 500 kHz, coaxial filament M):

| Candidate | L | C | est. Q | k at 1 / 5 / 10 cm | eta_max at 1 / 5 / 10 cm |
|---|---:|---:|---:|---|---|
| 10 cm, 10 turns, 0.7 mm | 17.1 uH | 5.9 nF | ~134 | 0.51 / 0.11 / 0.03 | 97 / 87 / 61 % |

*(This comparison used the early R estimate for all three candidates, so they stay comparable. For the chosen coil the final
R = 0.455 Ω gives Q = 118.3 and eta_max = 97 / 86 / 57 %; the ranking does not change.)*
| 12 cm, 12 turns, 0.7 mm | 27.3 uH | 3.7 nF | ~157 | 0.58 / 0.15 / 0.045 | 98 / 92 / 75 % |
| 15 cm, 12 turns, 0.7 mm | 38.1 uH | 2.7 nF | ~174 | 0.61 / 0.19 / 0.067 | 98 / 94 / 84 % |

Recommendation: 10 cm, 10 turns, because
1. its L (17 uH) lies in the 10 to 20 uH target range, while the larger coils give C of only 2.7 to 3.7 nF,
   where stray capacitance would matter more;
2. it matches the geometry already used for M(d), k(d), the misalignment study and the field map, so no results are rerun;
3. it still gives eta_max above 55 % at 10 cm and above 85 % up to 5 cm (57.2 % and 85.9 % at R = 0.455 Ω).

## 6. Limitations

The coil resistance values are estimates (C-T2), not measurements. The inductance
values are calculated rather than experimentally measured.
The predicted efficiencies depend on these assumptions and
will be checked against the circuit-level simulation.

The design uses the existing simulation geometry so that
subsequent analytical and numerical comparisons remain
consistent with the project's existing data.