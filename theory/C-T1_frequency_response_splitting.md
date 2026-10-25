# Task C-T1: Frequency Response, Coupled-Mode Splitting, and Critical Coupling

**Status:** Complete (evaluated for `v1-design` parameters in `sim/params.py` and `theory/hand_values.csv`)

---

## 1. Coupled-Resonator Transfer Function $I_2(\omega)/V_s$

For the series–series resonant wireless power transfer topology (Equation Reference Section 4 and `B-T1`), each resonator $i \in \{1, 2\}$ consists of coil inductance $L_i$, total series parasitic resistance $R_i$, and series tuning capacitor $C_i$, coupled by mutual inductance $M = k\sqrt{L_1 L_2}$:

$$Z_1(\omega) I_1 + j\omega M I_2 = V_s, \qquad j\omega M I_1 + Z_2(\omega) I_2 = 0$$

where the loop impedances are:

$$Z_1(\omega) = R_1 + R_s + j\left(\omega L_1 - \frac{1}{\omega C_1}\right), \qquad Z_2(\omega) = R_2 + R_L + j\left(\omega L_2 - \frac{1}{\omega C_2}\right)$$

*(Per project convention, when $V_s$ is measured directly across the primary resonator input terminals, $R_s = 0$; if referred to a function generator's internal source behind source impedance $R_s$, $R_s$ is included in $Z_1$.)*

Solving the secondary loop equation gives $I_1 = -\frac{Z_2(\omega)}{j\omega M} I_2$. Substituting into the primary loop equation yields the frequency-dependent transadmittance transfer function:

$$\frac{I_2(\omega)}{V_s} = \frac{-j\omega M}{Z_1(\omega) Z_2(\omega) + \omega^2 M^2}$$

Expanding $Z_1(\omega)$ and $Z_2(\omega)$ explicitly in terms of $\omega$:

$$\frac{I_2(\omega)}{V_s} = \frac{-j\omega M}{\left[R_{1,\text{tot}} + j\left(\omega L_1 - \frac{1}{\omega C_1}\right)\right]\left[R_{2,\text{tot}} + j\left(\omega L_2 - \frac{1}{\omega C_2}\right)\right] + \omega^2 M^2}$$

where $R_{1,\text{tot}} = R_1 + R_s$ and $R_{2,\text{tot}} = R_2 + R_L$.

---

## 2. Natural Modes and Coupled-Mode Frequency Splitting ($f_\pm$)

### 2.1 Determinant Derivation in the Low-Loss Limit
Consider two identical resonators tuned to the same uncoupled angular resonance $\omega_0$:

$$L_1 = L_2 = L, \qquad C_1 = C_2 = C, \qquad \omega_0 = \frac{1}{\sqrt{LC}}, \qquad M = kL$$

In the undamped (low-loss) limit ($R_{1,\text{tot}}, R_{2,\text{tot}} \to 0$), the loop impedances become purely reactive: $Z_1(\omega) = Z_2(\omega) = j\left(\omega L - \frac{1}{\omega C}\right) = j\omega L \left(1 - \frac{\omega_0^2}{\omega^2}\right)$. The natural normal-mode frequencies occur where the system determinant $\Delta(\omega) = Z_1(\omega) Z_2(\omega) + \omega^2 M^2$ vanishes:

$$\Delta(\omega) = -\omega^2 L^2 \left(1 - \frac{\omega_0^2}{\omega^2}\right)^2 + \omega^2 k^2 L^2 = 0$$

Dividing by $\omega^2 L^2 \neq 0$:

$$\left(1 - \frac{\omega_0^2}{\omega^2}\right)^2 = k^2 \implies 1 - \frac{\omega_0^2}{\omega^2} = \mp k \implies \frac{\omega_0^2}{\omega^2} = 1 \pm k$$

Taking the positive square root yields the two split natural mode frequencies:

$$\omega_\pm = \frac{\omega_0}{\sqrt{1 \pm k}} \quad \Longleftrightarrow \quad f_l = f_+ = \frac{f_0}{\sqrt{1 + k}}, \qquad f_h = f_- = \frac{f_0}{\sqrt{1 - k}}$$

*(Here $f_l < f_0$ is the lower split peak corresponding to $\sqrt{1+k}$ in the denominator, and $f_h > f_0$ is the higher split peak corresponding to $\sqrt{1-k}$ in the denominator.)*

### 2.2 Physical Interpretation (Even/Symmetric vs. Odd/Anti-Symmetric Modes)
Writing the lossless KVL equations at the natural modes ($V_s = 0$):

$$\left(\omega L - \frac{1}{\omega C}\right) I_1 + \omega M I_2 = 0, \qquad \omega M I_1 + \left(\omega L - \frac{1}{\omega C}\right) I_2 = 0$$

* **Lower-Frequency Mode ($f_l = f_0/\sqrt{1+k}$, In-Phase / Symmetric Mode, $I_2 = +I_1$):**
  When primary and secondary currents oscillate **in phase** ($I_1 = I_2$), the magnetic fluxes of the two coils aid each other. Each coil sees an increased effective inductance $L_{\text{eff},+} = L + M = L(1 + k)$, which lowers the resonant frequency to:
  $$f_l = \frac{1}{2\pi\sqrt{(L + M)C}} = \frac{f_0}{\sqrt{1 + k}}$$
* **Higher-Frequency Mode ($f_h = f_0/\sqrt{1-k}$, Anti-Phase / Anti-Symmetric Mode, $I_2 = -I_1$):**
  When primary and secondary currents oscillate **$180^\circ$ out of phase** ($I_2 = -I_1$), their magnetic fluxes oppose each other in the gap between the coils. Each coil sees a reduced effective inductance $L_{\text{eff},-} = L - M = L(1 - k)$, which raises the resonant frequency to:
  $$f_h = \frac{1}{2\pi\sqrt{(L - M)C}} = \frac{f_0}{\sqrt{1 - k}}$$

### 2.3 Extracting Coupling $k$ from Measured Split Peaks ($f_l, f_h$)
Squaring and inverting the two mode equations gives:

$$\frac{f_0^2}{f_l^2} = 1 + k, \qquad \frac{f_0^2}{f_h^2} = 1 - k$$

Dividing the difference by the sum eliminates $f_0$ completely:

$$\frac{\frac{f_0^2}{f_l^2} - \frac{f_0^2}{f_h^2}}{\frac{f_0^2}{f_l^2} + \frac{f_0^2}{f_h^2}} = \frac{(1 + k) - (1 - k)}{(1 + k) + (1 - k)} = \frac{2k}{2} = k \implies \boxed{k = \frac{f_h^2 - f_l^2}{f_h^2 + f_l^2}}$$

*(Note: As emphasized in Section 5 of the Project Brief, this exact formula contains no square roots.)*

---

## 3. Critical Coupling ($k_c$) and the Three Coupling Regimes

### 3.1 Derivation of Critical Coupling $k_c$
At the uncoupled resonant frequency $\omega = \omega_0$, the series reactances in both loops cancel ($\omega_0 L_i = 1/\omega_0 C_i$), so $Z_1(\omega_0) = R_{1,\text{tot}} = R_1 + R_s$ and $Z_2(\omega_0) = R_2 + R_L$. The secondary loop reflects a purely real resistance $Z_r(\omega_0)$ into the primary loop:

$$Z_r(\omega_0) = \frac{\omega_0^2 M^2}{R_2 + R_L}$$

**Critical coupling** is defined as the coupling strength at which the reflected resistance at $\omega_0$ matches the primary loop resistance ($Z_r(\omega_0) = R_{1,\text{tot}}$), maximizing power transfer at $\omega_0$:

$$\frac{\omega_0^2 M^2}{R_2 + R_L} = R_{1,\text{tot}} \implies \frac{\omega_0^2 k_c^2 L_1 L_2}{R_{1,\text{tot}}(R_2 + R_L)} = 1$$

Defining the primary quality factor $Q_{1,\text{eff}} = \frac{\omega_0 L_1}{R_1 + R_s}$ (which equals the unloaded $Q_1 = \frac{\omega_0 L_1}{R_1}$ when driven/measured directly at the primary terminals with $R_s = 0$) and the loaded secondary quality factor $Q_{2,L} = \frac{\omega_0 L_2}{R_2 + R_L}$:

$$k_c^2 Q_1 Q_{2,L} = 1 \implies \boxed{k_c = \frac{1}{\sqrt{Q_1 Q_{2,L}}}}, \qquad Q_{2,L} = \frac{\omega_0 L_2}{R_2 + R_L}$$

*(Peak-Bifurcation Threshold $k_{\text{split}}$ when $Q_1 \neq Q_{2,L}$: While $k_c = 1/\sqrt{Q_1 Q_{2,L}}$ marks the impedance-match boundary at $\omega_0$, expanding $\vert{}I_2(\omega)\vert{}^2$ around $\omega_0$ shows that the single peak at $f_0$ physically splits into two separate maxima when $\frac{\partial^2 \vert{}I_2\vert{}^2}{\partial \omega^2}\big\vert{}_{\omega_0} > 0$, which occurs at $k > k_{\text{split}} = \sqrt{\frac{1}{2}\left(\frac{1}{Q_1^2} + \frac{1}{Q_{2,L}^2}\right)}$. When $Q_{1,\text{eff}} = Q_{2,L}$, both thresholds coincide: $k_c = k_{\text{split}} = 1/Q_{2,L}$.)*

### 3.2 Behavior in the Three Coupling Regimes
1. **Under-Coupled Regime ($k < k_c$):**
   The reflected impedance $\omega_0^2 M^2/(R_2 + R_L)$ is smaller than $R_{1,\text{tot}}$. The frequency response exhibits a **single peak** centered at $f_0$, whose amplitude drops rapidly ($\propto k^2$) as coil separation increases.
2. **Critically Coupled Regime ($k = k_c$):**
   The reflected secondary resistance exactly matches the primary resistance at $f_0$ ($Z_{\text{in}}(\omega_0) = 2 R_{1,\text{tot}}$). A **single maximal, maximally flat peak** occurs right at $f_0$.
3. **Over-Coupled Regime ($k > k_c$, and $k > k_{\text{split}}$):**
   At $f_0$, the reflected impedance exceeds $R_{1,\text{tot}}$, throttling the primary current $I_1(f_0)$ and creating a local trough at $f_0$. Moving slightly off resonance to $f_l = f_0/\sqrt{1+k}$ and $f_h = f_0/\sqrt{1-k}$ allows the coil-capacitor reactance to cancel the reactive reflected impedance, producing **two split resonance peaks** on either side of $f_0$.

---

## 4. Bandwidth and Detuning Tolerance Rule

In the single-peak regime, the $-3\text{ dB}$ half-power bandwidth of each resonator is set by its loaded quality factor:

$$\Delta f_{3\text{dB}} \approx \frac{f_0}{Q_{\text{loaded}}}$$

For the unloaded resonators ($L = 17.13\text{ }\mu\text{H}$, $R = 0.455\text{ }\Omega$, $f_0 = 500\text{ kHz}$, $Q_1 = Q_2 = 118.3$), the unloaded bandwidth is $\Delta f_{\text{unloaded}} = \frac{500\text{ kHz}}{118.3} = 4.23\text{ kHz}$. With a load $R_L = 6.0\text{ }\Omega$, the loaded secondary quality factor is $Q_{2,L} = \frac{53.82\text{ }\Omega}{0.455 + 6.0\text{ }\Omega} = 8.34$, giving a loaded secondary passband of $\Delta f_{2,L} \approx 60.0\text{ kHz}$.

**Hardware Tuning Precision Rule:** For both resonators to exchange energy coherently at $f_0$ without reactive detuning loss, their uncoupled resonant frequencies $f_{01}$ and $f_{02}$ must match within the unloaded resonator bandwidth:

$$\frac{\vert{}f_{01} - f_{02}\vert{}}{f_0} \lesssim \frac{1}{Q} \approx 0.85\% \quad (\text{i.e., } \vert{}f_{01} - f_{02}\vert{} \lesssim 4.2\text{ kHz at } f_0 = 500\text{ kHz})$$

Since $f_0 \propto C^{-1/2}$ ($\frac{\Delta f_0}{f_0} \approx -\frac{1}{2}\frac{\Delta C}{C}$), matching $f_{01}$ and $f_{02}$ within $0.85\%$ requires capacitor matching within $\vert{}\Delta C\vert{}/C \lesssim 1.7\%$ (which is why C0G/film capacitors plus a small trimmer are specified in Task B-H1).

---

## 5. Quantitative Prediction for Task B-H3 ($d = 1, 5, \text{ and } 10\text{ cm}$)

Using our `v1-design` parameters ($f_0 = 500\text{ kHz}$, $L_1 = L_2 = 17.13\text{ }\mu\text{H}$, $R_1 = R_2 = 0.455\text{ }\Omega$, $Q_1 = 118.3$) and the fixed load $R_L = 6.0\text{ }\Omega$ ($Q_{2,L} = 8.34$, so $k_c = 0.0318$ for terminal drive $R_s = 0$, $k_{\text{split}} = 0.0850$ for $\vert{}I_2/V_s\vert{}$ peak bifurcation, and $k_{c,\text{gen}} = 0.3353$ if driven through a $50\text{ }\Omega$ function generator output impedance):

* **At $d = 1\text{ cm}$ ($k = 0.5131 \gg k_{\text{split}}$):** Strongly **over-coupled**. The frequency sweep in B-H3 will show a deep dip at $500\text{ kHz}$ and two widely separated split peaks near $f_l = 406.5\text{ kHz}$ (numerical $\vert{}I_2\vert{}$ peak at $407.9\text{ kHz}$) and $f_h = 716.5\text{ kHz}$ ($714.0\text{ kHz}$ with damping). Applying $k = (f_h^2 - f_l^2)/(f_h^2 + f_l^2)$ to the damped peaks gives $k = 0.508$ ($1.0\%$ below the true $k$; `data/val_split_peaks.csv`).
* **At $d = 5\text{ cm}$ ($k = 0.1112 > k_{\text{split}} = 0.0850$):** Moderately **over-coupled** under low-impedance terminal drive (or under-coupled if driven directly from an unbuffered $50\text{ }\Omega$ generator). Under terminal drive, $\vert{}I_2(f)\vert{}$ and $P_L(f)$ exhibit two closely spaced split peaks at $483.5\text{ kHz}$ and $519.6\text{ kHz}$ (lossless $f_\pm = 474.3\text{ kHz}$ and $530.3\text{ kHz}$; these loaded peaks give $k = 0.072$, 35 % low), while link efficiency $\eta(f)$ peaks right at $f_0 = 500\text{ kHz}$ at $\eta = 85.9\%$ because $R_L = 6.0\text{ }\Omega$ equals $R_{L,\text{opt}}(5\text{ cm})$.
* **At $d = 10\text{ cm}$ ($k = 0.0299$, just below $k_c = 0.0318$, and $k < k_{\text{split}} = 0.0850$):** **Near critical (slightly under-coupled)** at $f_0$ for terminal drive; $k = k_c$ at $d = 9.72$ cm, where $P_L$ (6 Ω) peaks (and well below the peak-splitting threshold $k_{\text{split}}$). The two split modes have coalesced into a **single sharp resonance peak** centered at $f_0 = 500.0\text{ kHz}$ with link efficiency $\eta(500\text{ kHz}) = 43.5\%$ (for $R_L = 6.0\text{ }\Omega$) and maximum achievable efficiency $\eta_{\max} = 57.2\%$ (at $R_{L,\text{opt}} = 1.67\text{ }\Omega$).

*(See generated plot `figs/fig_c_t1_regimes.pdf` / `.png` illustrating the normalized response across $d = 1, 3, 5, \text{ and } 10\text{ cm}$.)*

---

## 6. Chosen Poster Equations (2)

1. **Split-Mode Natural Frequencies & Coupling Extraction:**
   $$f_\pm = \frac{f_0}{\sqrt{1 \pm k}}, \qquad k = \frac{f_h^2 - f_l^2}{f_h^2 + f_l^2}$$
2. **Critical Coupling Condition:**
   $$k_c = \frac{1}{\sqrt{Q_1 Q_{2,L}}}, \qquad Q_{2,L} = \frac{\omega_0 L_2}{R_2 + R_L}$$