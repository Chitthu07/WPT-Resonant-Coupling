# A-T3 — Cross-check of Member B's circuit and efficiency derivations

Member A, EE2025 resonant WPT (series-series). Conventions follow CONVENTIONS.md Section 3 and the symbol table in `theory/A-T1_magnetic_link.md`. Checked against B-T1 (coupled-resonator circuit) and B-T2 (efficiency, optimal load, maximum efficiency), final versions.

*Values updated 2026-10-25 to the new R budget ($R_1 = R_2 = 0.455\ \Omega$, code at origin/main 4072022). Old values and the full change log: `theory/R_update_2026-10-25_changelog.md`.*

**Result in one line.** An independent derivation of $Z_{in}$ and $\eta_{\rm link}$ at $f_0$ agrees with B's results line by line: the mesh equations and signs, $Z_r$, $Z_{in}$, $I_2$, $\eta_{\rm link}$, $r_{opt}$, $\eta_{max}$, the maximum-power load and every number against the reference case and the design values. The k-from-split-peaks formula is valid only with a lightly loaded secondary.

---

## 1. Symbols (SI units)

Symbols not already in A-T1:

| Symbol | Meaning | Unit |
|---|---|---|
| $V_s$ | source voltage, peak phasor | V |
| $R_1$, $R_2$ | total series resistance of each resonator (wire, skin, proximity, capacitor ESR) | Ω |
| $R_L$ | load resistance, in series with the secondary | Ω |
| $R_s$ | source (generator) resistance, 0 for an ideal source | Ω |
| $C_1$, $C_2$ | series tuning capacitors | F |
| $Z_1$, $Z_2$ | loop impedances, $Z_1 = R_1 + j\omega L_1 + 1/(j\omega C_1)$, $Z_2 = R_2 + R_L + j\omega L_2 + 1/(j\omega C_2)$ | Ω |
| $Z_r$, $Z_{in}$ | reflected impedance; input impedance at the primary resonator terminals (excludes $R_s$) | Ω |
| $\omega_0$, $f_0$ | common resonance, $\omega_0 = 1/\sqrt{L_1C_1} = 1/\sqrt{L_2C_2}$, $f_0 = \omega_0/2\pi$ | rad/s, Hz |
| $Q_i$ | unloaded quality factor $\omega_0L_i/R_i$ | – |
| $P_{in}$, $P_L$ | average power into the primary resonator terminals, into the load | W |
| $\eta_{\rm link}$ | AC link efficiency $P_L/P_{in}$ (not the DC-to-DC $\eta_{\rm sys}$) | – |
| $x$, $r$ | $x = k^2Q_1Q_2 = \omega_0^2M^2/(R_1R_2)$, $r = R_L/R_2$ | – |

## 2. Independent derivation at $f_0$

**Mesh equations** (both currents into the dotted terminals, so the coupling terms are $+j\omega M$; $R_s = 0$, otherwise $Z_1 \to Z_1 + R_s$):

$$Z_1I_1 + j\omega M I_2 = V_s, \qquad j\omega M I_1 + Z_2 I_2 = 0$$

Units: every term is Ω·A = V ($\omega M$: rad/s · H = Ω).

**Eliminate $I_2$.** From the second equation $I_2 = -j\omega M I_1/Z_2$. Substituting, and using $(j)(-j) = 1$:

$$Z_{in} = \frac{V_s}{I_1} = Z_1 + Z_r, \qquad Z_r = \frac{\omega^2M^2}{Z_2}$$

$M$ appears only as $M^2$, so the sign of $M$ (winding direction) changes neither $Z_{in}$ nor $|I_2|$, hence neither $P_L$ nor $\eta$.

**At $\omega_0$** each loop's reactances cancel: $Z_1 = R_1$, $Z_2 = R_2 + R_L$.

$$Z_{in} = R_1 + \frac{\omega_0^2M^2}{R_2+R_L}\ \text{(purely real)}, \qquad I_2 = \frac{-j\omega_0 M}{R_2+R_L}\,I_1\ \text{(lags } I_1 \text{ by } 90^\circ)$$

**Powers** (peak phasors, factor ½):

$$P_{in} = \tfrac12 |I_1|^2 Z_{in}, \qquad P_L = \tfrac12 |I_2|^2 R_L = \tfrac12 |I_1|^2\,\frac{\omega_0^2M^2R_L}{(R_2+R_L)^2}$$

$$\eta_{\rm link} = \frac{\omega_0^2M^2R_L}{(R_2+R_L)\left[R_1(R_2+R_L)+\omega_0^2M^2\right]} = \underbrace{\frac{\omega_0^2M^2}{R_1(R_2+R_L)+\omega_0^2M^2}}_{\text{into secondary}}\cdot\underbrace{\frac{R_L}{R_2+R_L}}_{\text{to load}}$$

Units: Ω²·Ω / (Ω·Ω²), dimensionless ✓. $R_s$ scales $P_{in}$ and $P_L$ by the same factor, so $\eta_{\rm link}$ does not depend on it.

**Dimensionless form.** Divide top and bottom by $R_1R_2^{\,2}$, with $\omega_0^2M^2 = xR_1R_2$ and $R_L = rR_2$:

$$\eta_{\rm link} = \frac{xR_1R_2\cdot rR_2}{R_2(1+r)\left[R_1R_2(1+r) + xR_1R_2\right]} = \frac{x\,r}{(1+r)(1+r+x)}$$

**Optimum load.** $\dfrac{d}{dr}\dfrac{r}{(1+r)(1+r+x)} \propto (1+r)(1+r+x) - r(2+2r+x) = 1 + x - r^2$, positive below and negative above the root, so

$$r_{opt} = \sqrt{1+x}, \quad R_{L,opt} = R_2\sqrt{1+x}, \quad \eta_{max} = \frac{x}{(1+\sqrt{1+x})^2}$$

using $1 + r_{opt} + x = \sqrt{1+x}\,(1+\sqrt{1+x})$.

**Input impedance at the optimum.** $Z_{in} = R_1\left(1 + \frac{x}{1+r_{opt}}\right) = R_1\sqrt{1+x}$: the source sees $R_1\sqrt{1+x}$ while the load is $R_2\sqrt{1+x}$.

**Maximum power instead** (fixed $V_s$, source resistance $R_s$):

$$P_L = \frac{\tfrac12V_s^2\,\omega_0^2M^2R_L}{\left[(R_1+R_s)(R_2+R_L)+\omega_0^2M^2\right]^2}, \qquad R_{L,P\max} = R_2 + \frac{\omega_0^2M^2}{R_1+R_s}$$

Units: V²·Ω²·Ω/Ω⁴ = W ✓. For $R_s = 0$, $r = 1+x$, giving $\eta|_{P\max} = x/[2(2+x)] < 50\,\%$ and $P_{L,\max} = \dfrac{V_s^2}{8R_1}\dfrac{x}{1+x}$, which is set by $R_1$ and nearly independent of distance. For a fixed $R_L$, $P_L$ peaks against distance at critical coupling $\omega_0^2M^2 = (R_1+R_s)(R_2+R_L)$.

## 3. Line-by-line comparison with B

| Result | Section 2 (mine) | B-T1 / B-T2 | Agree |
|---|---|---|---|
| Dot convention, $+j\omega M$ in both meshes | as above | B-T1 §2, §4 | ✓ |
| $R_s$ handling, $Z_{in}$ at resonator terminals | as above | B-T1 §4, §7 | ✓ |
| $I_2 = -j\omega MI_1/Z_2$, $Z_r$, $Z_{in}$ | as above | B-T1 §5 | ✓ |
| $Z_{in}$ and $I_2$ at $f_0$, 90° lag | as above | B-T1 §6, §11 | ✓ |
| $P_{in}$, $P_L$ with ½ (peak phasors) | as above | B-T1 §7, B-T2 §1 | ✓ |
| Sign of $M$ irrelevant | as above | B-T1 §10 | ✓ |
| $\eta_{\rm link}$, two-factor form | as above | B-T2 §1 | ✓ |
| $\eta(x,r)$ and the substitution | as above | B-T2 §2 | ✓ |
| $r_{opt}$, $R_{L,opt}$, $\eta_{max}$ | as above | B-T2 §3 | ✓ |
| $x/4$ and $1-2/\sqrt{x}$ limits with range | Section 4 | B-T2 §4 | ✓ |
| $R_{L,P\max}$, $\eta|_{P\max}$, $P_{L,\max}$, $Z_{in,opt}$, $k_c$ condition | as above | B-T2 §5 | ✓ |

## 4. Numerical checks

**Reference case:** $L = 15$ µH, $f_0 = 500$ kHz, $R = 0.3$ Ω, $k = 0.1$.

| Quantity | One-line calculation | Value | B |
|---|---|---|---|
| $C$ | $1/[(2\pi\cdot5\times10^5)^2\cdot15\times10^{-6}]$ | 6.755 nF | ✓ |
| $Q$ | $2\pi(5\times10^5)(15\times10^{-6})/0.3 = 47.12/0.3$ | 157.1 | ✓ |
| $\omega_0M$ | $2\pi(5\times10^5)(1.5\times10^{-6})$ | 4.712 Ω | – |
| $x$ | $4.712^2/(0.3\cdot0.3) = 22.21/0.09$ | 246.7 | ✓ |
| $R_{L,opt}$ | $0.3\sqrt{247.7} = 0.3\cdot15.74$ | 4.72 Ω | ✓ |
| $\eta_{max}$ | $246.7/(1+15.74)^2 = 246.7/280.2$ | 88.05 % | ✓ |
| $Z_{in}$ at $R_{L,opt}$ | $0.3 + 22.21/(0.3+4.72)$ | 4.72 Ω | ✓ |
| phase($I_2/I_1$) at $f_0$ | $-j$ factor | −90° | ✓ |

**Efficiency limit**, $\eta_{max} = x/(1+\sqrt{1+x})^2$:

| $x$ | 0.1 | 1 | 10 | 100 | 1000 |
|---|---:|---:|---:|---:|---:|
| exact | 2.38 % | 17.16 % | 53.67 % | 81.90 % | 93.87 % |
| B | 2.4 % | 17.2 % | 53.7 % | 81.9 % | 93.9 % ✓ |
| $x/4$ | 2.50 % | (25 %) | – | – | – |
| $1 - 2/\sqrt{x}$ | – | – | (36.8 %) | 80.0 % | 93.68 % |

$x/4$ is already 5 % high at $x = 0.1$; $1 - 2/\sqrt{x}$ is useless below $x \approx 10$. Numbers are always quoted from the exact expression.

**Design values** (`sim/params.py`: $L = 17.13$ µH, $f_0 = 500$ kHz; $R_1 = R_2 = 0.455$ Ω, final nominal value: skin 0.269 + proximity 0.136 + capacitor ESR 0.035 + joints 0.015, range 0.38 to 0.48 Ω). $\omega_0L = 2\pi(5\times10^5)(17.13\times10^{-6}) = 53.82$ Ω, $Q = 53.82/0.455 = 118.3$ (range 112.1 to 141.6).

| $d$ | $k$ (`sim_M_k.csv`) | $k$ implied by B's $R_{L,opt}$ | $x = (kQ)^2$ | $R_{L,opt}$ | exact $\eta_{max}$ | $1-2/\sqrt{x}$ |
|---:|---:|---:|---:|---:|---:|---:|
| 1 cm | 0.513 | 0.513 | 3682 | 27.6 Ω | 96.8 % | 96.7 % |
| 3 cm | 0.217 | 0.217 | 660 | 11.7 Ω | 92.5 % | 92.2 % |
| 5 cm | 0.111 | 0.111 | 173 | 6.00 Ω | 85.9 % | 84.8 % |
| 6 cm | 0.083 | 0.083 | 95.3 | 4.47 Ω | 81.5 % | 79.5 % |
| 10 cm | 0.030 | – | 12.5 | 1.67 Ω | 57.2 % | 43.4 % |

The two $k$ columns agree to the third decimal, so B's load sweep, `sim_M_k.csv` and `params.py` are consistent. The 6.0 Ω fixed load is still the 5 cm optimum with the new $R$: for $R_1 = R_2$ and $x \gg 1$, $R_{L,opt} = R_2\sqrt{1+x} \approx R_2kQ = \omega_0M$, which does not depend on $R$. That is why the $R_{L,opt}$ column barely moved (5.99 → 6.00 Ω at 5 cm) while $x$ fell by the factor $(0.40/0.455)^2 = 0.773$. At 10 cm the strong-coupling limit is 14 points low (43.4 vs 57.2 %), so $\eta_{max}$ is always quoted from the exact expression. (B's 50.3 / 61.1 % at 10 cm were for $R = 0.4$ Ω.)

Maximum-power column ($V_s = 5$ V peak, $R_s = 0$): $R_{L,P\max} = 0.455(1+x)$ = 1676, 301, 43.9 Ω at 1, 3, 6 cm, and $P_{L,\max} = 25/(8\cdot0.455)\cdot x/(1+x)$ = 6.87, 6.86, 6.80 W. The ceiling $V_s^2/(8R_1) = 25/3.64 = 6.87$ W. (B's table, 1904/342/49.7 Ω and 7.81/7.80/7.75 W, was for $R = 0.4$ Ω and was correct for it.) Ideal-source worst case: $I_1 \to V_s/R_1 = 5/0.455 = 11.0$ A peak, dissipating $\tfrac12(11.0)^2(0.455) = 27.5$ W in coil 1.

Critical coupling with $R_L = 6.0$ Ω: $k_c = \sqrt{(R_1+R_s)(R_2+R_L)}/(\omega_0L)$ = $\sqrt{0.455 \times 6.455}/53.82 = 1.714/53.82 = 0.0318$ ($R_s = 0$, reached at $d = 9.72$ cm) and $\sqrt{50.455 \times 6.455}/53.82 = 18.05/53.82 = 0.335$ ($R_s = 50$ Ω, at $d = 1.90$ cm). B's 0.0297 at 10 cm was for $R = 0.4$ Ω.

## 5. Result: measuring k from split peaks needs a lightly loaded secondary

The formula $k = (f_h^2 - f_l^2)/(f_h^2 + f_l^2)$ comes from lossless coupled resonators. A load damps the secondary and pulls the two peaks together. Numerical sweep of $|I_2|$ for the reference case with $R_1 = R_2 = 0.01$ Ω:

| $R_L$ | Peaks | $k$ from formula |
|---:|---|---:|
| 0 to 0.1 Ω | 476.7, 527.0 kHz ($= f_0/\sqrt{1.1},\ f_0/\sqrt{0.9}$) | 0.100 |
| 4.72 Ω | 483.7, 519.1 kHz | 0.071 (30 % low) |
| 10 Ω | single peak at 499.5 kHz | – |

So $k$ must be extracted with the secondary shorted or with $R_L \ll \omega_0M$ (here $\omega_0M = 4.71$ Ω); a loaded measurement underestimates $k$. B-T1 §12 and the unit test use $R_L = 0.01$ Ω. This also applies to the bench measurement of $k$ discussed in A-V1.

---

## Oral questions

**Q1. Why is the input impedance purely resistive at $f_0$, and what is the reflected resistance physically?**
At $f_0$ each loop's $j\omega L$ cancels its $1/j\omega C$, so $Z_1 = R_1$ and $Z_2 = R_2 + R_L$ are real, and $Z_r = \omega_0^2M^2/(R_2+R_L)$ is real too. The reflected resistance is the power the secondary draws through the magnetic link: $\tfrac12|I_1|^2Z_r = \tfrac12|I_2|^2(R_2+R_L)$. The source "feels" the load as an extra resistance in series with $R_1$.

**Q2. Why isn't the efficiency-optimal load the same as the maximum-power load?**
Maximum power makes the load match everything in front of it, $R_L = R_2 + \omega_0^2M^2/R_1$, so as much power is burnt on the source side as in the load and efficiency is below 50 %. Maximum efficiency balances two losses instead: a small $R_L$ wastes power in $R_2$, a large $R_L$ reflects too little resistance so $R_1$ dominates. The balance is $R_L = R_2\sqrt{1+k^2Q_1Q_2}$.

**Q3. You measured two peaks to get $k$. Why did you short (or lightly load) the secondary first?**
The split formula comes from lossless coupled resonators. A load damps the secondary and pulls the peaks together: in the reference case they move from 476.7/527.0 kHz ($R_L \to 0$) to 483.7/519.1 kHz at $R_L = 4.72$ Ω, which gives $k = 0.071$ instead of 0.100, and at 10 Ω they merge.

---

## HANDOFF

```
Task: A-T3
Produced: theory/A-T3_cross_check_of_B.md (independent derivation, comparison with B-T1/B-T2, numerical checks)
Key numbers: reference case confirmed (C = 6.755 nF, Q = 157.1, x = 246.7, R_L,opt = 4.72 ohm,
  eta_max = 88.05 %, Z_in at R_L,opt = 4.72 ohm).
  Design (params.py, R = 0.455 ohm final, updated 2026-10-25): L = 17.13 uH, f0 = 500 kHz, omega0*L = 53.82 ohm, Q = 118.3.
  k(1, 3, 5, 6, 10 cm) = 0.513, 0.217, 0.111, 0.083, 0.030; x = 3682, 660, 173, 95.3, 12.5;
  exact eta_max = 96.76, 92.51, 85.90, 81.51, 57.21 %; R_L,opt = 27.6, 11.7, 6.00, 4.47, 1.67 ohm.
  k_c = 0.0318 at 9.72 cm (Rs = 0), 0.335 at 1.90 cm (Rs = 50 ohm), with R_L = 6.0 ohm. P_L,max ceiling 6.87 W.
  Closed forms: Z_in,opt = R1*sqrt(1+x); P_L,max = Vs^2/(8 R1) * x/(1+x) (Rs = 0).
  Split peaks give k = 0.100 only with R_L -> 0; at R_L = 4.72 ohm k reads 0.071.
Poster equations chosen: none new (B keeps mesh eqs, Z_in/Z_r, eta(x,r), eta_max; suggest eta(x,r) in Analysis)
Open issues: one LaTeX equation style for all equations when they go onto the poster (A-P2).
  For A-V1: measure k from split peaks with the secondary shorted. Quote exact eta_max, not 1 - 2/sqrt(x).
```

## STATUS

```
A-T1: DONE
A-T2: DONE
A-T3: DONE
A-V1 discussion: TODO
A-P1: TODO
A-P2: TODO
A-P3: TODO
```
