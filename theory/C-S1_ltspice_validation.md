# Task C-S1: LTspice Cross-Validation and Transient Build-Up Analysis

**Status:** Complete (`sim/wpt.asc`, `data/ltspice_ac.csv`, `data/val_ltspice_metrics.csv`, `data/c_s1_ltspice_validation.csv`, `figs/fig_c_s1_ac_validation.*`, and `media/ltspice_transient_buildup.png`)

---

## 1. Circuit Configuration in `sim/wpt.asc`

The coupled series–series WPT circuit in `sim/wpt.asc` uses the `v1-design` parameters from `sim/params.py` and coupling coefficients $k(d)$ across three coupling regimes:

* **Source (`Vs`):** `SINE(0 5 500k) AC 5 0` ($V_s = 5.0\text{ V}_{\text{pk}}$ at primary resonator terminals, $R_s = 0\text{ }\Omega$)
* **Primary Resonator:** $C_1 = 5.914815\text{ nF}$, $R_1 = 0.455\text{ }\Omega$, $L_1 = 17.13\text{ }\mu\text{H}$ ($f_0 = 500.00\text{ kHz}$, unloaded $Q_1 = 118.3$)
* **Secondary Resonator:** $L_2 = 17.13\text{ }\mu\text{H}$, $C_2 = 5.914815\text{ nF}$, $R_2 = 0.455\text{ }\Omega$, load $R_L = 6.00\text{ }\Omega$ (loaded $Q_{2,L} = 8.337$)
* **Mutual Inductance Statement:** `K1 L1 L2 {k}` with `.step param k list 0.321109 0.111189 0.029895` corresponding to $d = 2\text{ cm}, 5\text{ cm}, \text{ and } 10\text{ cm}$.
* **AC Sweep Directive:** `.ac lin 3001 350k 650k` ($0.7 f_0$ to $1.3 f_0$ in $100\text{ Hz}$ steps), executed in LTspice 26.0.1 (`python -m sim.compare_ltspice --run`) with `.options plotwinsize=0 numdgt=15` and exported to `data/ltspice_ac.csv` and `data/val_ltspice_metrics.csv`.

---

## 2. Real LTspice `.ac` Export (`data/ltspice_ac.csv`) vs. Python Solver (`sim/circuit.py`)

> *Regenerated 2026-10-25 with `python -m sim.compare_ltspice --run` at $R_1 = R_2 = 0.455\text{ }\Omega$ (LTspice 24 under Wine 9.0).*

Comparing the actual LTspice `.raw` AC sweep export (`data/ltspice_ac.csv`, `data/val_ltspice_metrics.csv`) against `sim.circuit.solve()` using the exact netlist parameters ($C_1 = C_2 = 5.914815\text{ nF}$, $L_1 = L_2 = 17.13\text{ }\mu\text{H}$, $R_1 = R_2 = 0.455\text{ }\Omega$, $R_L = 6.0\text{ }\Omega$) confirms agreement to better than **$10^{-9}\%$** across the entire $350\text{–}650\text{ kHz}$ frequency sweep—nine orders of magnitude tighter than the **$< 1\%$** rubric requirement:

| Distance $d$ [cm] | Coupling $k$ (`wpt.asc`) | $P_L$ Peak Freq: LTspice / Python [kHz] | Peak Freq Error [%] | $P_L$ Peak: LTspice / Python [W] | Peak $P_L$ Error [%] | $\eta(f_0)$: LTspice / Python [%] | $\angle(I_2/I_1)$ at $f_0$: LTspice / Python | Max Relative Error Across Sweep (`350–650 kHz`) | Status (`< 1%` req.) |
|---:|---:|:---|---:|:---|---:|:---|:---|---:|:---|
| **2.0 cm** | $0.321109$ | $437.498 / 437.498\text{ kHz}$ | $4.19 \times 10^{-11}\%$ | $1.63511 / 1.63511\text{ W}$ | $3.73 \times 10^{-11}\%$ | $92.046\% / 92.046\%$ | $-89.998^\circ / -89.998^\circ$ | $2.12 \times 10^{-10}\%$ | **PASS** |
| **5.0 cm** | $0.111189$ | $483.500 / 483.500\text{ kHz}$ | $3.79 \times 10^{-11}\%$ | $2.14774 / 2.14774\text{ W}$ | $5.69 \times 10^{-12}\%$ | $85.905\% / 85.905\%$ | $-89.998^\circ / -89.998^\circ$ | $4.02 \times 10^{-10}\%$ | **PASS** |
| **10.0 cm** | $0.029895$ | $500.003 / 500.003\text{ kHz}$ | $3.40 \times 10^{-12}\%$ | $6.35858 / 6.35858\text{ W}$ | $2.56 \times 10^{-11}\%$ | $43.542\% / 43.542\%$ | $-89.998^\circ / -89.998^\circ$ | $5.01 \times 10^{-10}\%$ | **PASS** |

*Note on $-89.998^\circ$ phase at $500\text{ kHz}$:* Both LTspice and the Python solver give $\angle(I_2/I_1) = -89.9981^\circ$ at $f_0 = 500.000\text{ kHz}$ because the 6-digit capacitance $5.914815\text{ nF}$ in `sim/wpt.asc` (vs. exact $5.914839\text{ nF}$) places the uncoupled resonance $1\text{ Hz}$ above $500\text{ kHz}$.

---

## 3. Transient Start-Up Envelope and $90^\circ$ Phase Shift at $f_0 = 500\text{ kHz}$

When the sinusoidal source $v_s(t) = V_s \sin(\omega_0 t)$ is switched on at $t = 0$ with zero initial energy in the coils and capacitors (`.tran 0 120u 0 5n uic`, numerically integrated in `sim/run_c_s1_c_v1.py` and plotted in `figs/fig_c_s1_transient.pdf` and `media/ltspice_transient_buildup.png`):

1. **Envelope Build-Up Time Constant ($\tau$):**
   * For an **unloaded resonator** ($R_1 = 0.455\text{ }\Omega$, $Q_1 = 118.3$), the natural envelope build-up time constant is:
     $$\tau_{\text{unloaded}} = \frac{2 L_1}{R_1} = \frac{Q_1}{\pi f_0} = \frac{118.3}{\pi \times 500\text{ kHz}} = 75.3\text{ }\mu\text{s} \quad (\approx 37.7\text{ RF cycles})$$
   * For the **coupled, loaded system at $d = 5\text{ cm}$** ($R_L = 6.0\text{ }\Omega$, $Z_{\text{in}} = 6.00\text{ }\Omega$), the reflected load resistance damps the primary loop and accelerates the coupled envelope build-up to $\tau_{\text{loaded}} \approx \frac{2 L_2}{R_2 + R_L} = 5.31\text{ }\mu\text{s}$ (reaching $>99\%$ steady state within $\sim 25\text{ }\mu\text{s}$).
2. **Exact $90^\circ$ Phase Lag ($i_2(t)$ lags $i_1(t)$ by $90^\circ$, i.e. $\Delta t = \frac{T_0}{4} = 0.50\text{ }\mu\text{s}$):**
   At steady state ($\omega = \omega_0$), the secondary reactance vanishes ($Z_2(\omega_0) = R_2 + R_L = 6.455\text{ }\Omega$), so Faraday's law $V_{\text{ind},2} = -j\omega_0 M I_1$ drives a secondary current:
   $$I_2(\omega_0) = \frac{-j\omega_0 M}{R_2 + R_L} I_1(\omega_0) \implies \angle I_2 - \angle I_1 = -90.0^\circ$$
   In the time-domain waveform (`figs/fig_c_s1_transient.pdf` and `media/ltspice_transient_buildup.png`), every positive peak of $i_2(t)$ occurs quarter of a period ($\Delta t = 0.50\text{ }\mu\text{s}$ at $T_0 = 2.00\text{ }\mu\text{s}$) after the positive peak of $i_1(t)$.