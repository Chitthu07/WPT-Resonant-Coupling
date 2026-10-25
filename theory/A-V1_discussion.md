# A-V1 (discussion part): analytical vs simulation differences

*Status: DONE, approved 2026-10-22. Section 5 records how the open points were closed in Claude Code (origin/main a5e87c8, 84 tests pass).*

*Values updated 2026-10-25 to the new R budget ($R_1 = R_2 = 0.455\ \Omega$, code at origin/main 4072022). Old values and the full change log: `theory/R_update_2026-10-25_changelog.md`.*

**Result.** No row of the comparison table differs by more than 10 %, so the A-V1 playbook (ranked causes for flagged rows) has nothing to rank. The largest difference is $L$ at $-3.7$ %, and $f_0$ and $Q$ inherit it at $\pm 1.9$ %. The coupling $k$ agrees to within 0.04 % at every distance. There is no measured column because the team is on the no-hardware roadmap (decided with B, 2026-10-20). The table therefore compares two **models** with each other, not a model with reality.

Source: `python -m sim.compare`, rerun 2026-10-20, params v1-design. Design geometry: planar spiral, $N = 10$ turns, outer diameter $d_\text{out} = 100$ mm, wire diameter $w = 0.7$ mm, pitch $p = 1.0$ mm, $f_0 = 500$ kHz, $R_1 = R_2 = 0.455\ \Omega$ (final nominal value, budget updated 2026-10-25, range 0.38 to 0.48 Ω), fixed load $R_L = 6.0\ \Omega$ (final, from C-C1). Percentages are (Simulation − Analytical) / Analytical.

All numbers below were recomputed independently (own elliptic-integral and filament code); every table value was reproduced to the printed digits.

---

## 1. Symbols

| Symbol | Meaning | Unit |
|---|---|---|
| $L$ | self-inductance of one coil ($L_1 = L_2$) | H |
| $C$ | series tuning capacitance ($C_1 = C_2$) | F |
| $R$ | total series resistance of one resonator (unloaded) | Ω |
| $f_0,\ \omega_0 = 2\pi f_0$ | resonant frequency, angular frequency | Hz, rad/s |
| $Q = \omega_0 L / R$ | unloaded quality factor | – |
| $M$, $k = M/\sqrt{L_1L_2}$ | mutual inductance, coupling coefficient | H, – |
| $d$ | spacing between the coil planes, coaxial | m |
| $r_i$ | radius of turn $i$ (centre of wire) | m |
| $r_w = w/2$ | wire radius | m |
| $\rho_f = (d_\text{out}-d_\text{in})/(d_\text{out}+d_\text{in})$ | fill ratio | – |
| $n$ | straight segments per turn in the numerical Neumann integral | – |

## 2. Row by row

### 2.1 Inductance, $-3.66$ %

Analytical (Mohan current sheet, circular coefficients $c_1 = 1,\ c_2 = 2.46,\ c_3 = 0,\ c_4 = 0.20$):

$d_\text{in} = d_\text{out} - 2[(N-1)p + w] = 100 - 2(9.7) = 80.6$ mm, $d_\text{avg} = 90.3$ mm, $\rho_f = 19.4/180.6 = 0.1074$

$$L_\text{Mohan} = \frac{\mu_0 N^2 d_\text{avg}}{2}\left[\ln\frac{2.46}{\rho_f} + 0.20\,\rho_f^2\right] = \frac{(4\pi\times10^{-7})(100)(0.0903)}{2}\,[3.1314 + 0.0023] = 17.78\ \mu\text{H}$$

Simulation (filament sum over 10 concentric circular turns, $r_i = 49.65 - i$ mm, $i = 0\ldots9$):

$$L_\text{fil} = \sum_i \mu_0 r_i\left[\ln\frac{8r_i}{r_w} - 2\right] + \sum_{i\ne j} M(r_i, r_j, 0) = 17.13\ \mu\text{H}$$

Difference: $(17.13 - 17.78)/17.78 = -3.66$ %. ✔

**Your cause is right:** the current-sheet formula smears the 10 discrete turns into a uniform sheet, and Mohan et al. state errors of a few per cent for it. A 3.7 % gap is inside that range, so it is not a sign of a bug.

**Two things to add.**

1. *The filament sum is not "truth" either.* It treats the spiral as 10 closed concentric rings (no radial step from turn to turn) and it uses the high-frequency self term ($-2$, i.e. no internal inductance). That second choice is correct here: the skin depth is $\delta = \sqrt{2/(\omega_0\mu_0\sigma)} = \sqrt{2/[(3.1416\times10^6)(4\pi\times10^{-7})(5.8\times10^7)]} = 0.093$ mm, much less than $r_w = 0.35$ mm, so current flows near the surface and the internal inductance has nearly gone. With the DC self term ($-1.75$) the same sum gives 17.27 µH ($+0.8$ %). So the "true" $L$ is uncertain at the ~1 % level even in the better model. Say this if asked which value is right.
2. *The Wheeler number needs its reference.* Octagonal modified Wheeler, $L = 2.25\,\mu_0N^2d_\text{avg}/(1 + 3.55\rho_f) = 18.48$ µH, is $+7.9$ % against the **simulation** (17.13) and $+3.9$ % against the **analytical** value (17.78). The coefficients are for an octagon, not a circle, so it is a sanity bracket, not a third independent check. Write "+7.9 % vs filament sum" in the table caption so nobody reads it against the wrong column.

### 2.2 Capacitance, 0.00 % (by construction)

$C = 1/(\omega_0^2 L_\text{fil}) = 1/[(3.1416\times10^6)^2(17.13\times10^{-6})] = 5.915$ nF. ✔

This row is not a comparison: $C$ is a component value chosen from $L_\text{fil}$ and used in both columns. Say so in the caption, or drop the row from the "% difference" column, otherwise a reader sees 0.00 % as a successful prediction.

### 2.3 Resonant frequency, $+1.88$ %

Because $C$ is fixed, the analytical resonance uses $L_\text{Mohan}$ with the same $C$:

$$f_{0,\text{an}} = \frac{1}{2\pi\sqrt{(17.78\times10^{-6})(5.915\times10^{-9})}} = 500\sqrt{\frac{17.13}{17.78}} = 490.8\ \text{kHz}$$

$(500.0 - 490.8)/490.8 = +1.88$ %. ✔ Your scaling $f_0 \propto 1/\sqrt{L}$ is right, and to first order $\Delta f_0/f_0 \approx -\tfrac12\Delta L/L$. The exact ratio is $\sqrt{17.78/17.13} - 1 = +1.88$ %, a little more than half of 3.66 % because the reference is the analytical column.

### 2.4 Quality factor, $-1.85$ %

$Q_\text{sim} = \omega_0 L_\text{fil}/R = (3.1416\times10^6)(17.13\times10^{-6})/0.455 = 53.82/0.455 = 118.3$ ✔
$Q_\text{an} = 2\pi(490.8\times10^3)(17.78\times10^{-6})/0.455 = 54.83/0.455 = 120.5$ ✔

$(118.3 - 120.5)/120.5 = -1.85$ %, the same percentage as with $R = 0.40$ Ω, because $R$ cancels in the ratio.

Your statement "$Q \propto \sqrt{L}$" is right **only because $C$ and $R$ are held fixed**: $Q = \omega_0L/R = \sqrt{L/C}/R$. Mention that condition when you say it. If the analytical design were instead retuned to 500 kHz (new $C$), $Q$ would scale with $L$ itself: $Q_\text{an} = (3.1416\times10^6)(17.78\times10^{-6})/0.455 = 55.86/0.455 = 122.8$, and the gap would be $-3.7$ %.

**The bigger uncertainty in $Q$ is not in this table.** Both columns use the same $R = 0.455\ \Omega$, so the table cannot test it. The range $0.38$ to $0.48\ \Omega$ gives $Q = 53.82/0.48 = 112.1$ to $53.82/0.38 = 141.6$, i.e. $-5$ % to $+20$ % around 118.3. That is still larger than the $L$ effect.

**Where $R = 0.455\ \Omega$ comes from (updated 2026-10-25).** The budget is now explained term by term:

| Term | Value | Source |
|---|---:|---|
| Skin effect (isolated wire) | 0.269 Ω | wire length $\sum 2\pi r_i = 2.84$ m, $R_\text{dc} = (1.72\times10^{-8})(2.84)/[\pi(0.35\times10^{-3})^2] = 0.127\ \Omega$, $R_\text{ac} \approx R_\text{dc}(r_w/2\delta + 0.25) = 0.127 \times 2.12 = 0.27\ \Omega$ (code: 0.269 Ω) |
| Proximity effect | 0.136 Ω | C-T2, checked independently in `sim/proximity_check.py`: per-turn transverse field 383.4 to 525.7 A/m, $\sum_i H_i^2(2\pi r_i) = 1.946\times10^5$ /m; thin-skin estimate 0.158 Ω, exact Bessel solution (round wire, uniform transverse field, $r_w/\delta = 3.745$) 0.136 Ω |
| Capacitor ESR | 0.035 Ω | team budget |
| Joints | 0.015 Ω | team budget |
| **Total** | **0.455 Ω** | $0.269 + 0.136 + 0.035 + 0.015 = 0.455$ ✔ |

So the gap between the skin-only 0.27 Ω and the total, which the earlier version of this section left as "proximity, not computed here", is now closed: proximity between turns only 0.3 mm apart is computed (0.136 Ω, 30 % of $R$) and replaces the old 30 to 40 % rule of thumb. The thin-skin formula overestimates it by 16 % because $r_w/\delta = 3.7$ is not large enough for the thin-skin limit. All four terms are still model values, not measurements. The A-T2 eddy-loss estimate has since been rechecked for this coil (Section 5).

### 2.5 Coupling coefficient, $\le 0.04$ % at every $d$

Both columns divide by the same $L_\text{fil}$, so the $k$ rows compare only the two ways of computing $M$: closed-form elliptic integral vs numerical Neumann integral on a 150-sided polygon. My elliptic sum over all $10\times10$ turn pairs gives $k$ = 0.51308, 0.32111, 0.21721, 0.15320, 0.11121, 0.08257, 0.04816, 0.02990 at $d$ = 1, 2, 3, 4, 5, 6, 8, 10 cm, matching the analytical column. ✔

**Your cause is right, with one correction to the arithmetic.** A regular $n$-gon inscribed in a circle has area ratio

$$\frac{A_n}{\pi r^2} = \frac{n}{2\pi}\sin\frac{2\pi}{n} \approx 1 - \frac{1}{6}\left(\frac{2\pi}{n}\right)^2 = 1 - \frac{(0.04189)^2}{6} = 1 - 2.92\times10^{-4}$$

so each polygon loop is 0.029 % short of area. ✔ In the far field $M \propto A_1A_2$, and **both** coils are polygons, so the far-field deficit tends to $2 \times 0.029 = 0.058$ %, not 0.03 %. The table reaches $-0.04$ % at 10 cm and is still growing, which fits: 10 cm is only $d \approx 2a$ (outer radius $a = 50$ mm), not yet the far field. At close range the error is smaller because $M$ is dominated by nearby wire whose position the polygon gets nearly right.

**On the convergence check.** Polygon error scales as $1/n^2$, so going from 150 to 300 segments removes about $3/4$ of it. A change of "< 0.04 %" on doubling is therefore the same size as the error itself; it confirms the explanation, it does not show the error is much smaller than 0.04 %. If you want one cleaner number: Richardson extrapolation, $M_\infty \approx M_{300} + (M_{300} - M_{150})/3$, should land on the elliptic value.

## 3. Why there is no measured comparison

The A-V1 playbook asks for bench causes (how $d$ was measured, as-built coil shape, LCR test frequency, leads, nearby metal, capacitor tuning). None of these exist on the no-hardware roadmap, so no measured values are assumed here and the Measured column stays n/a. For the poster this should be stated, not hidden. A suggested caption line:

> *No prototype was built (no-hardware roadmap). Validation is model against model: current-sheet and elliptic-integral formulas vs filament and numerical Neumann sums. All differences are below 4 %.*

What this comparison **does** show: the two independent $M$ methods agree, so the $k(d)$ curve, and with it $x = k^2Q_1Q_2$ and $\eta_\text{max}$, is computed correctly for the ideal geometry. What it **cannot** show: whether the real coil, real wire resistance and real surroundings match the model. The largest model input that is computed but never measured is $R$ (Section 2.4).

## 4. Summary for the poster table

| Quantity | Sim vs An | Cause (checked) |
|---|---|---|
| $L$ | −3.66 % | current sheet vs discrete turns (within Mohan's stated accuracy) |
| $C$ | 0 % | same component in both columns; not a comparison |
| $f_0$ | +1.88 % | from $L$ only, $f_0 \propto 1/\sqrt{L}$ at fixed $C$ |
| $Q$ | −1.85 % | from $L$ only, $Q = \sqrt{L/C}/R$ at fixed $C$, $R$ |
| $k$ (1–10 cm) | −0.00 to −0.04 % | 150-gon area deficit, tends to −0.058 % far field |

---

## 5. Resolution of the open points (Claude Code, 2026-10-22)

| Point raised above | Outcome |
|---|---|
| $C$ row is not a comparison | Table now shows n/a in "Sim vs An" for $C$, with the note "same component, not a comparison". |
| Wheeler reference | Captioned "+7.9 % vs filament sum" in `theory/hand_values_note.md`. |
| Numbers in this file | Re-verified in code: $L$ with DC self term 17.270 µH, $\delta$ = 0.0935 mm, skin-only $R_\text{ac}$ = 0.269 Ω, $Q$ = 122.3 to 153.8 (for the old 0.35 to 0.44 Ω; now 112.1 to 141.6, see below), far-field polygon deficit 0.0585 %. |
| Richardson extrapolation | $M_{300} + (M_{300} - M_{150})/3$ equals the elliptic $M$ to within $10^{-6}$ at $d$ = 1, 3 and 10 cm. It is now a test. |
| $R$ and $R_L$ | Final (updated 2026-10-25): $R_1 = R_2 = 0.455$ Ω nominal, range 0.38 to 0.48 Ω (skin 0.269 + proximity 0.136 + ESR 0.035 + joints 0.015); $R_L = 6.0$ Ω (`params.RL_fixed`), still $R_{L,opt}$ at 5 cm. |
| A-T2 eddy loss (0.10 Ω flag) | Rechecked for this coil (N = 10, $d_\text{out}$ = 10 cm), aluminium plate behind the coil, image model: added series resistance 178 / 87 / 33 mΩ at gap $g$ = 5 / 10 / 20 mm (copper: 138 / 68 / 26 mΩ). C's `shield.py` agrees to < 0.05 %. A-T2's ~0.10 Ω was for a different example coil; for ours it corresponds to $g \approx 9$ mm. |
| No-prototype caption | **Still open, goes on the poster** (A-P2/A-P3): "No prototype was built (no-hardware roadmap). Validation is model against model ... All differences are below 4 %." |

~~Still untested: the proximity part of $R$ is a 30 to 40 % rule of thumb.~~ **Resolved 2026-10-25:** proximity computed by C (C-T2) and checked independently in `sim/proximity_check.py` (exact Bessel 0.136 Ω, thin-skin 0.158 Ω). $R$ is still a model value, not measured; over 0.38 to 0.48 Ω, $Q$ = 112.1 to 141.6.

---

## Oral questions

**Q1. Your analytical and simulated $L$ differ by 3.7 %. Which one did you design with, and why?**
The filament sum, 17.13 µH. It keeps the 10 turns as separate current paths, while Mohan's formula spreads them into a uniform sheet, which Mohan reports as accurate only to a few per cent. The filament model still has ~1 % uncertainty from treating the spiral as concentric rings and from the internal-inductance term (17.27 µH with the DC term), so I would not quote it to better than 1 %.

**Q2. Why does a 3.7 % error in $L$ give only 1.9 % in $f_0$ and $Q$?**
$C$ was chosen once and kept. Then $f_0 = 1/(2\pi\sqrt{LC}) \propto L^{-1/2}$ and $Q = \omega_0L/R = \sqrt{L/C}/R \propto L^{1/2}$, so both move by about half the relative change in $L$, in opposite directions. If $C$ were retuned to hold $f_0$, $Q$ would move with $L$ itself.

**Q3. You never built the coils. What does your validation actually prove?**
That the numbers are computed correctly for the ideal geometry: two independent methods for $M$ agree to 0.04 %, and the remaining differences are explained by known approximations. It does not prove the real coil behaves this way. The biggest input that is computed but never measured is the AC resistance $R$ = 0.455 Ω (skin 0.269, proximity 0.136, capacitor ESR 0.035, joints 0.015). Its 0.38 to 0.48 Ω range moves $Q$ from 112 to 142 around 118.3, more than any difference in the table.

---

## HANDOFF

```
Task: A-V1 (discussion part)
Produced: theory/A-V1_discussion.md
Key numbers: no row > 10 %. L: Mohan 17.78 vs filament 17.13 uH (-3.66 %); filament with DC self term 17.27 uH (+0.8 %).
  Wheeler octagonal 18.48 uH = +7.9 % vs filament, +3.9 % vs Mohan. C = 5.915 nF (same in both columns).
  f0,an = 490.8 kHz (+1.88 %); Q 120.5 vs 118.3 (-1.85 %, holds because C and R fixed). [R = 0.455 ohm, 2026-10-25]
  k max diff -0.04 % at 10 cm; 150-gon area deficit 0.029 % per loop, far-field limit -0.058 %.
  Q range from R = 0.38-0.48 ohm: 112.1 to 141.6. R budget: skin 0.269 + proximity 0.136 (Bessel) + ESR 0.035 + joints 0.015 = 0.455 ohm.
Poster equations chosen: none new.
Resolved (2026-10-22): Wheeler captioned vs filament sum; C row n/a; all numbers re-verified
  (17.270 uH, 0.0935 mm, 0.269 ohm, Q 122.3-153.8, 0.0585 %); Richardson M agrees with elliptic M
  to < 1e-6 (now a test); R = 0.455 ohm (2026-10-25, was 0.40) and R_L = 6.0 ohm final; eddy loss for our coil, Al plate:
  178/87/33 mOhm at g = 5/10/20 mm (Cu 138/68/26), 0.10 ohm <-> g ~ 9 mm.
Open issues: none (caption placed in A-P1; proximity computed 2026-10-25). R is a model value, not measured.
```

## STATUS

```
A-T1: DONE
A-T2: DONE
A-T3: DONE
A-V1 discussion: DONE
A-P1: TODO
A-P2: TODO
A-P3: TODO
```
