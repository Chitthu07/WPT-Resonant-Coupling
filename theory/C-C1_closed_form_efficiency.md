# Task C-C1: Closed-Form $\eta(R_L)$, $\eta_{\max}(d)$, $P_L(d)$, and Coupling Regime Analysis

**Status:** Complete (generated from `sim/params.py` and `theory/hand_values.csv` via `sim/run_c_c1.py`)

---

## 1. Governing Closed-Form Equations (at $f = f_0$)

From the Equation Reference (Section 4) and `B-T2`, at the resonant frequency $\omega_0 = 2\pi f_0 = 1/\sqrt{L_1 C_1} = 1/\sqrt{L_2 C_2}$, both loop reactances vanish. Define the dimensionless figure of merit $x$ and normalized load ratio $r$:

$$Q_1 = \frac{\omega_0 L_1}{R_1}, \qquad Q_2 = \frac{\omega_0 L_2}{R_2}, \qquad x(d) = k(d)^2 Q_1 Q_2 = \frac{\omega_0^2 M(d)^2}{R_1 R_2}, \qquad r = \frac{R_L}{R_2}$$

1. **Link Efficiency as a Function of Load $\eta(R_L, d)$:**
   $$\eta(R_L, d) = \left[\frac{\omega_0^2 M^2}{R_1(R_2 + R_L) + \omega_0^2 M^2}\right] \cdot \left[\frac{R_L}{R_2 + R_L}\right] = \frac{x \cdot r}{(1 + r)(1 + r + x)}$$
2. **Optimal Load Resistance $R_{L,\text{opt}}(d)$ and Maximum Link Efficiency $\eta_{\max}(d)$:**
   $$\frac{\partial \eta}{\partial r} = 0 \implies r_{\text{opt}}(d) = \sqrt{1 + x(d)}, \qquad R_{L,\text{opt}}(d) = R_2 \sqrt{1 + k(d)^2 Q_1 Q_2}$$
   $$\eta_{\max}(d) = \frac{x(d)}{\left(1 + \sqrt{1 + x(d)}\right)^2}$$
3. **Input Impedance, Currents, and Delivered Load Power $P_L(d)$ at Fixed $V_s$ and Fixed $R_L$:**
   For a sinusoidal source of peak amplitude $V_s$ applied across the primary resonator terminals at $f_0$:
   $$Z_{\text{in}}(d) = R_1 + \frac{\omega_0^2 M(d)^2}{R_2 + R_L}, \qquad \vert{}I_1(d)\vert{} = \frac{V_s}{Z_{\text{in}}(d)}, \qquad \vert{}I_2(d)\vert{} = \frac{\omega_0 M(d) \vert{}I_1(d)\vert{}}{R_2 + R_L}$$
   $$P_{\text{in}}(d) = \frac{1}{2} V_s \vert{}I_1(d)\vert{}, \qquad P_L(d) = \frac{1}{2} \vert{}I_2(d)\vert{}^2 R_L = \frac{1}{2} V_s^2 \frac{\omega_0^2 M(d)^2 R_L}{\left[R_1(R_2 + R_L) + \omega_0^2 M(d)^2\right]^2}$$

---

## 2. Resonator Baseline Parameters (`sim/params.py` & `theory/hand_values.csv`)

* $f_0 = 500\text{ kHz}$ ($\omega_0 = 3.14159 \times 10^6\text{ rad/s}$)
* $L_1 = L_2 = 17.13\text{ }\mu\text{H}$ ($\omega_0 L_1 = \omega_0 L_2 = 53.815\text{ }\Omega$)
* $C_1 = C_2 = 5.915\text{ nF}$
* $R_1 = R_2 = 0.455\text{ }\Omega$ (C-T2 budget with the computed proximity loss; was 0.40 Ω before 2026-10-25)
* Unloaded Quality Factors: $Q_1 = Q_2 = 118.3$ ($Q_1 Q_2 = 13\,989$)
* Standard Source Excitation (per Task B-C1): $V_s = 5.0\text{ V}_{\text{pk}}$ ($3.536\text{ V}_{\text{rms}}$)

---

## 3. Selection of Fixed Load Resistance $R_L$ for Distance Sweeps (Task C-C1 Step 4)

Per Task C-C1 Step 4 (*"Choose the fixed $R_L$ for the hardware distance sweep (suggest the $R_{L,\text{opt}}$ at a mid distance such as 5 cm) and tell A"*):
* At the mid-range distance $d = 5\text{ cm}$, the analytical coupling is $k(5\text{ cm}) = 0.111219$, giving figure of merit $x = k^2 Q_1 Q_2 = 173.0$.
* The exact optimal load at $d = 5\text{ cm}$ is:
  $$R_{L,\text{opt}}(5\text{ cm}) = 0.455\text{ }\Omega \times \sqrt{1 + 173.0} = 6.003\text{ }\Omega \approx 6.0\text{ }\Omega$$
  (For $R_1 = R_2$ and $x \gg 1$, $R_{L,\text{opt}} \approx \omega_0 M$, independent of $R$, so the choice survived the change of R.)
* Conveniently, **$R_L = 6.0\text{ }\Omega$** is an exact standard entry in `params.RL_list = [0.5, 1, 2, 4, 6, 8, 12, 20, 30]`.
* **Decision:** We fix **$R_{L,\text{fixed}} = 6.0\text{ }\Omega$** for all fixed-load distance sweeps (`A-H3`, `B-S1`, `C-C1`). With $R_L = 6.0\text{ }\Omega$, the loaded secondary quality factor is $Q_{2,L} = \frac{53.815\text{ }\Omega}{0.455 + 6.0\text{ }\Omega} = 8.337$, yielding:
  * **Impedance-match critical coupling ($R_s = 0$):** $k_c = \frac{1}{\sqrt{Q_1 Q_{2,L}}} = 0.03185$ (reached at $d = 9.72$ cm)
  * **Frequency-splitting bifurcation threshold ($R_s = 0$):** $k_{\text{split}} = \sqrt{\frac{1}{2}(Q_1^{-2} + Q_{2,L}^{-2})} = 0.08503$
  * **Generator-driven critical coupling ($R_s = 50\text{ }\Omega$):** $k_{c,\text{gen}} = 0.3353$

---

## 4. Closed-Form $\eta(R_L)$ Table Across `params.RL_list` at $d = 1, 3, 5, 10\text{ cm}$

Full data saved to `data/c_c1_eta_vs_RL.csv`.

| Load $R_L$ [$\Omega$] | Ratio $r = R_L/R_2$ | $\eta(R_L)$ at $d = 1\text{ cm}$ ($k = 0.5131$) | $\eta(R_L)$ at $d = 3\text{ cm}$ ($k = 0.2172$) | $\eta(R_L)$ at $d = 5\text{ cm}$ ($k = 0.1112$) | $\eta(R_L)$ at $d = 10\text{ cm}$ ($k = 0.0299$) |
|---:|---:|---:|---:|---:|---:|
| **0.5** | $1.10$ | $52.33\%$ | $52.19\%$ | $51.73\%$ | $44.84\%$ |
| **1** | $2.20$ | $68.67\%$ | $68.40\%$ | $67.48\%$ | $54.74\%$ |
| **2** | $4.40$ | $81.35\%$ | $80.81\%$ | $79.00\%$ | **$56.92\%$ (Peak)** |
| **4** | $8.79$ | $89.55\%$ | $88.47\%$ | $84.98\%$ | $50.37\%$ |
| **6 (Fixed $R_L$)** | $13.19$ | $92.59\%$ | $91.00\%$ | **$85.91\%$ (Peak)** | $43.56\%$ |
| **8** | $17.58$ | $94.14\%$ | $92.03\%$ | $85.44\%$ | $38.07\%$ |
| **12** | $26.37$ | $95.64\%$ | **$92.51\%$ (Peak)** | $83.19\%$ | $30.22\%$ |
| **20** | $43.96$ | $96.60\%$ | $91.54\%$ | $77.61\%$ | $21.29\%$ |
| **30** | $65.93$ | **$96.75\%$ (Peak)** | $89.44\%$ | $71.03\%$ | $15.51\%$ |
| **Exact $R_{L,\text{opt}}$** | $\sqrt{1+x}$ | **$27.62\text{ }\Omega \to 96.76\%$** | **$11.70\text{ }\Omega \to 92.51\%$** | **$6.00\text{ }\Omega \to 85.91\%$** | **$1.67\text{ }\Omega \to 57.23\%$** |

---

## 5. Master Table: $\eta_{\max}(d)$, $\eta(d, R_L=6\text{ }\Omega)$, $P_L(d)$, and Coupling Regimes

Full data across all distances saved to `data/c_c1_closed_form.csv` (for $V_s = 5.0\text{ V}_{\text{pk}}$ and $R_{L,\text{fixed}} = 6.0\text{ }\Omega$).

| Axial Spacing $d$ [cm] | Analytical $M(d)$ [$\mu\text{H}$] | Coupling $k(d)$ [-] | Figure of Merit $x = k^2 Q_1 Q_2$ | Optimal Load $R_{L,\text{opt}}$ [$\Omega$] | Max Efficiency $\eta_{\max}(d)$ [%] | Fixed-Load $\eta(R_L = 6\text{ }\Omega)$ [%] | Input Impedance $Z_{\text{in}}$ [$\Omega$] | Load Power $P_L(d)$ at $V_s=5\text{ V}_{\text{pk}}$ [W] | Coupling Regime ($k$ vs. $k_c = 0.0318$, $k_{\text{split}} = 0.0850$) |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|:---|
| **1 cm** | $8.789$ | $0.51315$ | $3683.6$ | $27.62\text{ }\Omega$ | **$96.76\%$** | $92.59\%$ | $118.57\text{ }\Omega$ | $0.098\text{ W}$ | **Over-coupled** ($k \gg k_{\text{split}}$; strong 2-peak split) |
| **2 cm** | $5.500$ | $0.32114$ | $1442.8$ | $17.29\text{ }\Omega$ | **$94.87\%$** | $92.05\%$ | $46.72\text{ }\Omega$ | $0.246\text{ W}$ | **Over-coupled** ($k > k_{\text{split}}$; clear 2-peak split) |
| **3 cm** | $3.721$ | $0.21724$ | $660.2$ | $11.70\text{ }\Omega$ | **$92.51\%$** | $91.00\%$ | $21.62\text{ }\Omega$ | $0.526\text{ W}$ | **Over-coupled** ($k > k_{\text{split}}$; 2-peak split) |
| **5 cm** | $1.905$ | $0.11122$ | $173.0$ | $6.00\text{ }\Omega$ | **$85.91\%$** | $85.91\%$ | $6.00\text{ }\Omega$ | $1.789\text{ W}$ | **Over-coupled** ($k > k_{\text{split}}$; mild 2-peak split) |
| **8 cm** | $0.825$ | $0.04816$ | $32.5$ | $2.63\text{ }\Omega$ | **$70.52\%$** | $64.67\%$ | $1.50\text{ }\Omega$ | $5.406\text{ W}$ | **Transition** ($k_c < k < k_{\text{split}}$; single peak at $f_0$) |
| **10 cm** | $0.512$ | $0.02991$ | $12.5$ | $1.67\text{ }\Omega$ | **$57.23\%$** | $43.56\%$ | $0.86\text{ }\Omega$ | $6.359\text{ W}$ | **Near critical** ($k$ just below $k_c = 0.0318$; single peak; $P_L$ max at 9.75 cm) |

### Key Takeaway on Efficiency vs. Delivered Power ($P_L(d)$):
With a constant-voltage source $V_s = 5\text{ V}_{\text{pk}}$ applied directly across the primary terminals ($R_s = 0$), **efficiency $\eta(d)$ is highest at $d = 1\text{ cm}$ ($96.76\%$)**, whereas **delivered power $P_L(d)$ peaks near the critical-coupling distance $d \approx 9.75\text{ cm}$ ($6.38\text{ W}$; 6.36 W at 10 cm)**! Why? At $d = 1\text{ cm}$, the large reflected resistance $Z_r = 118.1\text{ }\Omega$ throttles the primary current to $\vert{}I_1\vert{} = 42.2\text{ mA}$, limiting input power to $0.105\text{ W}$. At $d = 10\text{ cm}$ ($k = 0.0299$, just below $k_c = 0.0318$), the reflected resistance $Z_r = 0.401\text{ }\Omega$ is close to $R_1 = 0.455\text{ }\Omega$, so the source delivers nearly its maximum power ($\eta_{\text{link}} = 43.56\%$), vividly proving the `B-T2` theorem that **maximum efficiency and maximum power occur at completely different operating points**.