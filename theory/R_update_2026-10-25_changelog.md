# R update, 2026-10-25: change log

Member A, EE2025 resonant WPT (series-series). Update task: apply the team's new resistance budget to A-V1, A-T3 and the poster (A-P1, A-P2). Source of all new values: Claude Code, origin/main 4072022 (`sim/proximity_check.py` and the design scripts). New values were used as given; only the derived numbers marked † were computed here, from the given values.

**Why R changed.** C computed the proximity loss in C-T2 and it was checked independently: per-turn transverse fields 383.4 to 525.7 A/m, $\sum_i H_i^2(2\pi r_i) = 1.946\times10^5$ /m, thin-skin estimate 0.158 Ω, exact Bessel solution (round wire, uniform transverse field, $r_w/\delta = 3.745$) 0.136 Ω. This replaces the old 30 to 40 % rule of thumb.

$R = 0.269\ (\text{skin}) + 0.136\ (\text{proximity}) + 0.035\ (\text{capacitor ESR}) + 0.015\ (\text{joints}) = 0.455\ \Omega$

Unchanged: $L = 17.13$ µH, $C = 5.915$ nF, $f_0 = 500$ kHz, $\omega_0L = 53.82$ Ω, $k(d)$, $M(d)$, skin depth 0.0935 mm, field map, misalignment $M$, $R_L = 6.0$ Ω.

## 1. Change log

| Quantity | Old | New | Where changed |
|---|---|---|---|
| $R_1 = R_2$ (nominal) | 0.40 Ω | 0.455 Ω | A-V1 header, §2.4, §5, Q3, HANDOFF; A-T3 design line, HANDOFF; poster setup box and eq. (5) line; A-P1 md; A-P2 md |
| $R$ range | 0.35 to 0.44 Ω | 0.38 to 0.48 Ω | A-V1 header, §2.4, §5, Q3; poster limitations line |
| $Q = \omega_0L/R$ | 134.5 | 118.3 | everywhere above |
| $Q$ range | 122 to 154 (122.3 to 153.8) | 112.1 to 141.6 | A-V1 §2.4, §5, HANDOFF; A-T3 design line |
| Bandwidth $f_0/Q$ | 3.72 kHz | 4.23 kHz | A-P2 md arithmetic (not on the poster, no slot) |
| $Q_\text{an}$ (A-V1 table) | 137.1 | 120.5 | A-V1 §2.4, HANDOFF (Sim vs An stays −1.85 %) |
| $Q_\text{an}$ if retuned to 500 kHz † | 139.6 | 122.8 | A-V1 §2.4 (gap stays −3.7 %) |
| $x$ at 1 / 3 / 5 / 6 / 10 cm | 4764 / 852 / 223 / 125 / 16.3 | 3682 / 660 / 173 / 95.3 / 12.5 | A-T3 table, HANDOFF; poster eq. (7) line (5 cm); A-P2 md |
| $x$ at 2 / 8 cm | – | 1442 / 32.4 | not used in these files |
| $\eta_{max}$ at 1 / 3 / 5 / 6 / 10 cm | 97.1 / 93.4 / 87.5 / 83.6 / 61.2 % | 96.76 / 92.51 / 85.90 / 81.51 / 57.21 % | A-T3 table (1 decimal), HANDOFF; poster eq. (7) line 85.9 %; A-P2 md |
| $\eta_{max}$ at 2 / 8 cm | – | 94.87 / 70.50 % | not used in these files |
| $R_{L,opt}$ at 1 / 3 / 5 / 6 / 10 cm | 27.6 / 11.7 / 5.99 / 4.48 / 1.66 Ω | 27.6 / 11.7 / 6.00 / 4.47 / 1.67 Ω | A-T3 table; A-P2 md |
| $1 - 2/\sqrt{x}$ column † | 97.1 / 93.2 / 86.6 / 82.1 / 50.5 % | 96.7 / 92.2 / 84.8 / 79.5 / 43.4 % | A-T3 table |
| Strong-coupling error at 10 cm † | 11 points | 14 points (43.4 vs 57.2 %) | A-T3 §4 text |
| $R_{L,P\max} = R(1+x)$ at 1 / 3 / 6 cm † | 1904 / 342 / 49.7 Ω | 1676 / 301 / 43.9 Ω | A-T3 §4 |
| $P_{L,\max}$ ceiling $V_s^2/(8R_1)$ | 7.81 W | 6.87 W | A-T3 §4, HANDOFF |
| $P_{L,\max}$ at 3 / 6 cm † | 7.80 / 7.75 W | 6.86 / 6.80 W | A-T3 §4 |
| Ideal-source worst case | 12.5 A, 31 W | 11.0 A, 27.5 W | A-T3 §4 (new sentence) |
| $k_c$, $R_s = 0$, $R_L = 6.0$ Ω | 0.0297 near 10 cm | 0.0318 at 9.72 cm | A-T3 §4, HANDOFF |
| $k_c$, $R_s = 50$ Ω | 0.334 near 1.9 cm | 0.335 at 1.90 cm | A-T3 §4, HANDOFF (unchanged within rounding) |
| Al plate at 10 mm, share of $R$ † | +22 %, Q 134.5 → 110 | +19 %, Q 118.3 → 99 | A-P2 md arithmetic |
| Proximity status | "30 to 40 % rule of thumb, not computed" | computed: 0.136 Ω (Bessel), 30 % of $R$ | A-V1 §2.4 (new budget table), §5, Q3, HANDOFF |
| Poster limitations line | "R (0.35 to 0.44 Ω) untested" | "R (0.38 to 0.48 Ω) computed, not measured" | poster S7 body; A-P1 md answer text |

† derived here from the given values with one line of arithmetic, shown in the file where it appears.

**Poster (`poster/EM_WPT_poster_template.pptx`)**: 5 text runs edited in place, formatting kept: eq. (5) meaning line, eq. (7) meaning line (two runs), setup box, S7 limitations line. The A-V1 comparison table is unchanged (all percentages hold). Both preview images were regenerated from the edited file (`EM_WPT_poster_template_preview.jpg`, `A-P2_poster_preview.jpg`); both now show the current poster. `build_poster_template.py` was not run.

`theory/A-T3_review_of_B.md` keeps its old numbers as the record of B's review (it said "provisional R = 0.4"); a note at the top points here.

## 2. Flags (nothing changed for these)

1. **Skin depth on the poster is 0.093 mm, not 0.094 mm.** A-P2 chose 0.093 mm to match A-V1 (both round 0.0935 mm). Left as is; A-P3 picks one value poster-wide.
2. **The R range is lopsided around the nominal.** 0.455 Ω is −16 % / +5.5 % inside 0.38 to 0.48 Ω, so $Q$ is −5 % / +20 % around 118.3. Fine if intended (the budget is near its upper end); worth one sentence from C on how the range was set.
3. **Old values quoted in the update message differ in the last digit from what my files had:** 6 cm was 83.6 % here (message: 83.5), 10 cm was 61.2 % (message: 61.12). Rounding only.
4. **Last-digit check of the new values:** from $k$ = 0.11121, 0.04816, 0.02990 and $Q$ = 118.28 I get $\eta_{max}$ = 85.91, 70.52, 57.22 % vs the given 85.90, 70.50, 57.21 %. This is $k$ rounding; the given values were used.
5. **Not yet on the poster:** bandwidth 4.23 kHz, 6.87 W, 27.5 W and the misalignment numbers have no slot in Sections 3 to 4. They belong to B's and C's sections (5 and 7), which should use these new values.

## 3. Oral questions

**Q1. Your Q fell from 134.5 to 118.3 but the optimal load stayed at 6.0 Ω. Why?**
For identical coils and $x \gg 1$, $R_{L,opt} = R_2\sqrt{1+x} \approx R_2\,kQ = R_2\,k\,\omega_0L/R_2 = \omega_0M$. The resistance cancels, so the optimum load is set by the mutual reactance alone: $\omega_0M = 0.111 \times 53.82 = 6.0$ Ω at 5 cm.

**Q2. Why is the proximity loss 0.136 Ω and not the thin-skin 0.158 Ω?**
The thin-skin formula assumes $r_w \gg \delta$. Here $r_w/\delta = 0.35/0.0935 = 3.7$, which is not large enough, so the exact Bessel solution for a round wire in a uniform transverse field is used. It gives 16 % less.

**Q3. How much did the higher R cost in efficiency?**
$x = k^2Q^2$ scales as $1/R^2$, so $x$ fell by $(0.40/0.455)^2 = 0.77$. Near coupling this barely matters (97.1 → 96.8 % at 1 cm) because $\eta_{max} \approx 1 - 2/\sqrt{x}$ is flat for large $x$. Far out it matters more (61.2 → 57.2 % at 10 cm).

## 4. Re-applied to B's poster version (2026-10-25, later the same day)

The user uploaded B's version of the poster (names, Executive Summary, Section 5 figures and captions filled). The edits were re-applied to it, B's content kept, and saved as `poster/EM_WPT_poster_template.pptx`. The previous file is kept as `poster/EM_WPT_poster_template_backup_2026-10-25_before_B.pptx`. Both previews were regenerated.

| Box | Old | New |
|---|---|---|
| S2 Executive Summary | Q = 134.5 | Q = 118.3 |
| S2 Executive Summary | η_max 97 / 88 / 61 % at 1 / 5 / 10 cm | 97 / 86 / 57 % |
| S2 Executive Summary | power peaks at critical coupling, 7.3 W at 10 cm | 6.4 W at 9.7 cm † |
| S4 eq. (5) line | Q = 134.5 at 0.40 Ω | Q = 118.3 at 0.455 Ω |
| S4 eq. (7) line | x = 223, η_max = 87.5 % | x = 173, η_max = 85.9 % |
| S5 fig_eta_vs_d caption | 97 / 88 / 61 %; fixed 6 Ω gives 47 % at 10 cm | 97 / 86 / 57 %; 44 % at 10 cm † |
| S5 setup box | R = 0.40 Ω, Q = 134.5 | R = 0.455 Ω, Q = 118.3 |
| S7 limitations | R (0.35 to 0.44 Ω) untested | R (0.38 to 0.48 Ω) computed, not measured |

† Derived from the given values. Power at critical coupling ($R_s = 0$, $R_L = 6$ Ω): $P_L = \frac{V_s^2}{8R_1}\cdot\frac{R_L}{R_2+R_L} = 6.87 \times 6/6.455 = 6.39$ W (old: $7.81 \times 6/6.4 = 7.32$ W, which reproduces B's 7.3 W). Fixed-load efficiency at 10 cm: $\omega_0^2M^2 = (0.0299 \times 53.82)^2 = 2.590\ \Omega^2$, $\eta = \frac{2.590 \times 6}{6.455\,(6.455 \times 0.455 + 2.590)} = 15.54/35.68 = 43.6$ % (old formula with 0.40 Ω gives 47.1 %, matching B).

**Flag for B:** the four Section 5 plots (fig_eta_vs_d, fig_eta_vs_f, fig_eta_vs_RL and the k plot) are images made with R = 0.40 Ω. The k plot does not depend on R. The three η / power plots must be regenerated from the code at 4072022 so the curves match the new captions (for example the η_max curve should read 86 % at 5 cm, not 88 %). The fig_k_vs_d caption says "agree to 0.05 %" while the Section 6 table says ≤ 0.04 %: one value should be used.

---

## HANDOFF

```
Task: R update (2026-10-25), applies to A-V1, A-T3, A-P1, A-P2
Produced: theory/R_update_2026-10-25_changelog.md (this file). Changed: theory/A-V1_discussion.md,
  theory/A-T3_cross_check_of_B.md, theory/A-T3_review_of_B.md (note only), poster/A-P1_poster_template.md,
  poster/A-P2_sections_3_4.md, poster/EM_WPT_poster_template.pptx (5 runs), both poster preview jpgs.
Key numbers: R = 0.455 ohm (0.38-0.48) = skin 0.269 + proximity 0.136 + ESR 0.035 + joints 0.015.
  Q = 118.3 (112.1-141.6), f0/Q = 4.23 kHz. x(1,3,5,6,10 cm) = 3682, 660, 173, 95.3, 12.5;
  eta_max = 96.76, 92.51, 85.90, 81.51, 57.21 %; R_L,opt = 27.6, 11.7, 6.00, 4.47, 1.67 ohm (6.0 still optimal at 5 cm).
  k_c = 0.0318 at 9.72 cm (Rs = 0), 0.335 at 1.90 cm (Rs = 50). P_L,max ceiling 6.87 W; worst case 11.0 A, 27.5 W.
  A-V1 table: Q_an 120.5 vs Q_sim 118.3 (-1.85 %).
Poster equations chosen: none new.
Open issues: skin depth 0.093 vs 0.094 mm (A-P3); lopsided R range (ask C); B/C sections to use new values.
```

## STATUS

```
A-T1: DONE
A-T2: DONE
A-T3: DONE (values updated 2026-10-25)
A-V1 discussion: DONE (values updated 2026-10-25)
A-P1: DONE (pending team names/title; setup box updated 2026-10-25)
A-P2: DONE (S4 values updated 2026-10-25)
A-P3: TODO
```
