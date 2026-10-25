# Task C-V1: Comparison of $\eta(R_L)$, Misalignment, and Shielding; Resistance Sensitivity, Engineering Trade-Offs, and ICNIRP Safety

**Status:** Complete (`theory/C-V1_comparison_and_limitations.md`, `data/c_v1_load_rectifier.csv`, `data/c_v1_misalign_table.csv`, `figs/fig_c_v1_eta_vs_RL_rectifier.*`, and `figs/fig_c_v1_misalign_band.*`)

---

## 1. Load Sweep Comparison: $\eta_{\text{link}}(R_L)$, Maximum Power vs. Maximum Efficiency, and Rectifier Equivalent ($0.81\,R_{\text{DC}}$)

### 1.1 Analytical vs. Circuit-Solver $\eta(R_L)$ and Optimum Load $R_{L,\text{opt}}$
Using `sim/params.py` ($f_0 = 500\text{ kHz}$, $L_1 = L_2 = 17.13\text{ }\mu\text{H}$, $R_1 = R_2 = 0.455\text{ }\Omega$, $Q_1 = Q_2 = 118.3$; updated 2026-10-25 from 0.40 Ω), the numerical 2×2 complex impedance solver (`sim.circuit.solve`) and the closed-form efficiency formula (`sim.circuit.eta_closed`) agree to machine precision ($< 10^{-15}$) at $f_0$.

At $d = 3\text{ cm}$, $d = 5\text{ cm}$, and $d = 6\text{ cm}$:

| Metric | $d = 3\text{ cm}$ ($k = 0.2172$, $x = 659.8$) | $d = 5\text{ cm}$ ($k = 0.1112$, $x = 172.9$) | $d = 6\text{ cm}$ ($k = 0.0825$, $x = 95.3$) |
| :--- | :---: | :---: | :---: |
| **Load for Max Efficiency ($R_{L,\text{opt}} = R_2\sqrt{1+x}$)** | **$11.70\text{ }\Omega$** | **$6.00\text{ }\Omega$** | **$4.47\text{ }\Omega$** |
| **Maximum Link Efficiency ($\eta_{\max}$)** | **$92.51\%$** | **$85.90\%$** | **$81.51\%$** |
| **Load for Max Power Transfer at Fixed $V_s$ ($R_{L,P_{\max}} = R_2 + \frac{\omega_0^2 M^2}{R_1}$)** | **$300.7\text{ }\Omega$** | **$79.1\text{ }\Omega$** | **$43.8\text{ }\Omega$** |
| **Delivered Power at $R_{L,P_{\max}}$ ($V_s = 5\text{ V}_{\text{pk}}$)** | $6.86\text{ W}$ ($\eta = 49.8\%$) | $6.83\text{ W}$ ($\eta = 49.4\%$) | $6.80\text{ W}$ ($\eta = 49.0\%$) |
| **Delivered Power at $R_{L,\text{opt}}$ ($V_s = 5\text{ V}_{\text{pk}}$)** | $0.99\text{ W}$ ($\eta = 92.5\%$) | $1.79\text{ W}$ ($\eta = 85.9\%$) | $2.28\text{ W}$ ($\eta = 81.5\%$) |

* **Why $R_{L,\text{opt}} \neq R_{L,P_{\max}}$:** Maximum power transfer from a constant-voltage source $V_s$ matches the secondary load to the reflected primary impedance ($R_{L,P_{\max}} = R_2 + \omega_0^2 M^2/R_1$), which dissipates $50\%$ of the input power in $R_1$ ($\eta < 50\%$). Maximum efficiency instead minimizes total ohmic dissipation in both coils by setting $R_{L,\text{opt}} = R_2\sqrt{1 + k^2 Q_1 Q_2}$.

### 1.2 Full-Bridge Rectifier Equivalent Load ($R_{\text{ac,eq}} = \frac{8}{\pi^2} R_{\text{DC}} \approx 0.8106\,R_{\text{DC}}$)
When the receiver drives a full-wave Schottky bridge rectifier with a parallel smoothing capacitor $C_f$ and DC load $R_{\text{DC}}$ (`params.rect_factor = 8 / np.pi**2`):
* The secondary current $i_2(t)$ is nearly sinusoidal (filtered by the high-$Q$ series $L_2 C_2$ tank), while the bridge input voltage is a square wave of amplitude $\pm (V_{\text{DC}} + 2 V_F)$ in phase with $i_2(t)$.
* Taking the fundamental Fourier component of the square wave ($V_{1,\text{pk}} = \frac{4}{\pi} V_{\text{DC}}$ for ideal diodes, with $I_{\text{DC}} = \frac{2}{\pi} I_{2,\text{pk}}$) yields the effective fundamental AC load resistance seen by the secondary resonator:
  $$R_{\text{ac,eq}} = \frac{V_{1,\text{pk}}}{I_{2,\text{pk}}} = \frac{\frac{4}{\pi} V_{\text{DC}}}{\frac{\pi}{2} I_{\text{DC}}} = \frac{8}{\pi^2} R_{\text{DC}} \approx 0.8106\,R_{\text{DC}}$$
* Including the forward drop $V_F \approx 0.35\text{ V}$ of two conducting Schottky diodes per half-cycle ($2 V_F \approx 0.70\text{ V}$), the overall DC-to-DC efficiency is:
  $$\eta_{\text{sys}}(R_{\text{DC}}) = \eta_{\text{link}}\!\left(R_{\text{ac,eq}} = \frac{8}{\pi^2} R_{\text{DC}}\right) \times \frac{V_{\text{DC}}}{V_{\text{DC}} + 2 V_F}$$
* Consequently, to present the optimal AC load $R_{L,\text{opt}}(3\text{ cm}) = 11.69\text{ }\Omega$ to the secondary tank, the DC load resistor after the rectifier must be scaled by $\pi^2/8 \approx 1.234$: $R_{\text{DC,opt}}(3\text{ cm}) = \frac{\pi^2}{8}(11.69\text{ }\Omega) = 14.43\text{ }\Omega$ (and $R_{\text{DC,opt}}(6\text{ cm}) = 5.50\text{ }\Omega$). Both curves are plotted in `figs/fig_c_v1_eta_vs_RL_rectifier.pdf`.

---

## 2. Lateral Misalignment Comparison (`A-S2` vs. Resistance Sensitivity)

Generated directly from `data/sim_misalign.csv` (`data/c_v1_misalign_table.csv`) using `sim.circuit.eta_closed` and `RL_opt` with fixed load $R_L = R_{L,\text{opt}}(\Delta x = 0)$ at each distance (for `v1-design` $R_1 = R_2 = 0.455\text{ }\Omega$: $R_L = 11.70\text{ }\Omega$ at $d = 3\text{ cm}$ and $R_L = 5.996\text{ }\Omega$ at $d = 5\text{ cm}$; for placeholder $R_1 = R_2 = 0.30\text{ }\Omega$: $R_L = 11.691\text{ }\Omega$ at $d = 3\text{ cm}$ and $R_L = 5.991\text{ }\Omega$ at $d = 5\text{ cm}$):

| Lateral Offset $\Delta x$ [cm] | $M(\Delta x)$ at $d=3\text{ cm}$ [$\mu\text{H}$] | $k(\Delta x)$ at $d=3\text{ cm}$ | $\eta$ at $d=3\text{ cm}$ (`v1-design` $R=0.455\text{ }\Omega$) | $\eta$ at $d=3\text{ cm}$ (Placeholder $R=0.3\text{ }\Omega$) | $M(\Delta x)$ at $d=5\text{ cm}$ [$\mu\text{H}$] | $\eta$ at $d=5\text{ cm}$ (`v1-design` $R=0.455\text{ }\Omega$) | $\eta$ at $d=5\text{ cm}$ (Placeholder $R=0.3\text{ }\Omega$) |
|---:|---:|---:|---:|---:|---:|---:|---:|
| **0 cm** | $3.720\text{ }\mu\text{H}$ | $+0.2172$ | $92.51\%$ | $95.00\%$ | $1.904\text{ }\mu\text{H}$ | $85.90\%$ | $90.46\%$ |
| **2 cm** | $3.147\text{ }\mu\text{H}$ | $+0.1837$ | $91.10\%$ | $94.04\%$ | $1.694\text{ }\mu\text{H}$ | $84.22\%$ | $89.28\%$ |
| **4 cm** | $1.974\text{ }\mu\text{H}$ | $+0.1152$ | $84.15\%$ | $89.16\%$ | $1.192\text{ }\mu\text{H}$ | $76.86\%$ | $83.94\%$ |
| **5 cm** | $1.376\text{ }\mu\text{H}$ | $+0.0803$ | $74.28\%$ | $81.76\%$ | $0.908\text{ }\mu\text{H}$ | $68.31\%$ | $77.31\%$ |
| **6 cm** | $0.834\text{ }\mu\text{H}$ | $+0.0487$ | $53.32\%$ | $63.97\%$ | $0.639\text{ }\mu\text{H}$ | $53.75\%$ | $64.85\%$ |
| **8 cm** | $0.053\text{ }\mu\text{H}$ | $+0.0031$ | $0.49\%$ | $0.75\%$ | $0.217\text{ }\mu\text{H}$ | $12.73\%$ | $18.86\%$ |
| **8.22 cm (Null at $d=3$)** | **$0.000\text{ }\mu\text{H}$** | **$0.0000$** | **$0.00\%$** | **$0.00\%$** | $0.183\text{ }\mu\text{H}$ | $9.43\%$ | $14.24\%$ |
| **10 cm** | $-0.216\text{ }\mu\text{H}$ | $-0.0126$ | $7.41\%$ | $11.08\%$ | $-0.002\text{ }\mu\text{H}$ | $0.00\%$ | $0.00\%$ |

* **Flat Efficiency Plateau Explained:** For $\Delta x \le 3\text{ cm}$ ($\approx 60\%$ of the coil radius $a = 5\text{ cm}$), $\eta$ drops by less than $4$ percentage points because $x = k^2 Q_1 Q_2 \gg 1$.
* **Zero Crossing & Sign Reversal of $M$:** Because $\nabla \cdot \mathbf{B} = 0$, magnetic flux lines exiting the primary core must loop back downward outside the coil perimeter. At $\Delta x = 8.22\text{ cm}$ (for $d = 3\text{ cm}$) and $\Delta x = 9.97\text{ cm}$ (for $d = 5\text{ cm}$), the upward interior flux and downward return flux linking the secondary cancel exactly ($M = 0 \implies \eta = 0\%$). Beyond $\Delta x = 8.22\text{ cm}$ at $d = 3\text{ cm}$, net return flux dominates ($M < 0$), and because $\eta \propto M^2$, efficiency partially rebounds to $8.41\%$ at $\Delta x = 10\text{ cm}$.

---

## 3. Shield & Ferrite Effect Comparison (`C-S2` vs. Free-Space Baseline)

At $d = 3\text{ cm}$ ($R_L = 11.70\text{ }\Omega$), placing an aluminium plate ($t \ge 1\text{ mm} \gg \delta_{\text{Al}} = 0.120\text{ mm}$) or MnZn ferrite sheet ($\mu_r = 2000$) at gap $g$ behind the secondary coil impacts the link through **three coupled mechanisms**:
1. **Coupling Change ($k'$):** At $g = 5\text{ mm}$, the opposing eddy-current image in aluminium cuts $k$ by $-56.4\%$ ($0.2172 \to 0.0948$), whereas ferrite flux guiding boosts $k$ by $+34.5\%$ ($0.2172 \to 0.2921$).
2. **Eddy Resistance Penalty ($\Delta R_{\text{plate}}$):** Surface-impedance integration gives $\Delta R_{\text{Al}} = +177.7\text{ m}\Omega$ at $g = 5\text{ mm}$ ($+87.4\text{ m}\Omega$ at $10\text{ mm}$), increasing total secondary resistance from $R_2 = 0.455\text{ }\Omega$ to $0.633\text{ }\Omega$ and cutting $Q_2$ from $118.3$ to $85.0$ (the primary, 35 mm away, adds only $\Delta R_{11} = 10.9\text{ m}\Omega$, plus a mutual term $\Delta R_{12} = 33.1\text{ m}\Omega$). Even if the secondary capacitor $C_2$ is re-tuned to compensate the inductance drop ($L_2' = 8.34\text{ }\mu\text{H}$), the combined $k'$ and plate-loss penalty reduces link efficiency at $d = 3\text{ cm}$ from $92.5\%$ to $63.9\%$ (73.1 % if $R_L$ is also re-optimised).
3. **Resonant Detuning Penalty (if $C_2$ is NOT re-tuned):** Because the aluminium plate at $g = 5\text{ mm}$ lowers $L_2$ from $17.13\text{ }\mu\text{H}$ to $8.34\text{ }\mu\text{H}$ ($\Delta L_2 = -8.79\text{ }\mu\text{H}$), an uncompensated secondary tank experiences an inductive reactance mismatch $\omega_0 \Delta L_2 = -27.61\text{ }\Omega$ at $500\text{ kHz}$, collapsing link efficiency at fixed $f_0 = 500\text{ kHz}$ from $92.5\%$ down to **$24.0\%$** (plate loss in both coils; 2×2 mesh with the plate-loss matrix and $L', M'$ from `data/sim_shield.csv`).

---

## 4. Parameter Uncertainty & Physical Model Limitations (No-Hardware Roadmap)

1. **Resistance Sensitivity Band (`params.R_range = (0.38, 0.48) Ω` from `C-T2`):**
   * Because series resistance $R$ depends on high-frequency turn-to-turn proximity crowding, capacitor ESR, and termination joints, `C-T2` established an expected range $R_1 = R_2 \in [0.38, 0.48]\text{ }\Omega$ around the $0.455\text{ }\Omega$ nominal design value (corresponding to unloaded $Q \in [112.1, 141.6]$).
   * Plotted as shaded sensitivity bands in `figs/fig_c_v1_eta_vs_RL_rectifier.pdf` and `figs/fig_c_v1_misalign_band.pdf` (and consistent with `B-V1` Section 4), this resistance range shifts $\eta_{\max}$ by at most $+2.2 / -0.7$ percentage points for aligned coils at $d \le 5\text{ cm}$ ($\eta_{\max}(5\text{ cm}) \in [85.2\%, 88.1\%]$) and by $+5.4 / -1.7$ percentage points at $d = 10\text{ cm}$ ($\eta_{\max}(10\text{ cm}) \in [55.5\%, 62.6\%]$).
2. **Physical Factors Beyond the Lumped Filament Model:**
   * **Resonance Detuning Sensitivity ($\vert{}f_{01} - f_{02}\vert{}$):** A $1\%$ capacitance tolerance shifts $f_{02}$ by $2.5\text{ kHz}$ ($\approx 0.59\,\Delta f_{\text{unloaded}}$), introducing reactive impedance $X_2 \approx 0.54\text{ }\Omega$ at $f_0$.
   * **Parasitic Inter-Turn Self-Capacitance:** Distributed turn-to-turn capacitance creates a finite self-resonant frequency ($f_{\text{SRF}} > 5\text{ MHz} \gg 500\text{ kHz}$), raising apparent inductance and loss tangent slightly at $500\text{ kHz}$.
   * **Non-Uniform Proximity Current Distribution:** Filament-sum inductance (`A-C1`) and Neumann integration (`A-S1`) assume current flows along the wire centreline, whereas at $500\text{ kHz}$ skin and proximity crowding shift the current centroid slightly inward on each turn, reducing high-frequency internal inductance by $\sim 1\text{–}2\%$.
   * **Rectifier Conduction Drops & Harmonics:** At low secondary voltages (large $d$ or large $\Delta x$), the $2 V_F \approx 0.7\text{ V}$ Schottky diode drop consumes a substantial fraction of $V_{\text{DC}}$, causing DC-to-DC efficiency $\eta_{\text{sys}}$ to fall below the AC link efficiency $\eta_{\text{link}}$.

---

## 5. Engineering Limitations, Trade-Offs, and ICNIRP Human Exposure Safety (Poster Section 7 Input)

### 5.1 Core Design Trade-Offs
* **Range vs. Efficiency ($1/d^3$ Dipole Penalty):** For $d > a$, mutual inductance decays asymptotically as $M \propto 1/d^3$, so the figure of merit $x = k^2 Q_1 Q_2$ falls as $1/d^6$. In the weak-coupling limit ($x \ll 1$), $\eta_{\max} \approx \frac{k^2 Q_1 Q_2}{4} \propto 1/d^6$, creating a sharp range wall around $d \approx 2 d_{\text{out}}$ ($10\text{–}15\text{ cm}$ for $10\text{ cm}$ coils).
* **Frequency vs. Loss ($f_0$ Selection):** Raising $f_0$ increases inductive reactance $\omega_0 L$, but AC skin depth shrinks as $\delta \propto f^{-1/2}$ ($R_{\text{ac}} \propto f^{1/2}$), proximity losses grow at close pitch, and driver switching losses increase. Operating at $f_0 = 500\text{ kHz}$ balances compact $\text{nF}$ tuning capacitors against manageable skin/proximity resistance.
* **Coil Size vs. $Q$ and Alignment:** Larger coil diameter $d_{\text{out}}$ extends the near-field zone and widens lateral misalignment tolerance ($\Delta x_{\text{null}} \approx 1.6\,a$), but increases wire length $\ell$ and footprint.
* **System Efficiency ($\eta_{\text{sys}}$) vs. Link Efficiency ($\eta_{\text{link}}$):** Driver switching losses and secondary rectifier diode drops reduce end-to-end DC-to-DC efficiency $\eta_{\text{sys}}$ by $8\text{–}18$ percentage points below the AC link efficiency $\eta_{\text{link}}$.
* **High Resonant Capacitor Voltage Stress:** At $f_0$, the capacitor voltage is magnified by $Q$: $V_{C1,\text{pk}} = \frac{\vert{}I_1\vert{}}{\omega_0 C_1} = \omega_0 L_1 \vert{}I_1\vert{} = 53.82\text{ }\Omega \times \vert{}I_1\vert{}$. At $d = 5\text{ cm}$ ($\vert{}I_1\vert{} = 0.833\text{ A}_{\text{pk}}$ for $V_s = 5\text{ V}_{\text{pk}}$), $V_{C1,\text{pk}} = 44.8\text{ V}_{\text{pk}}$; at $d = 10\text{ cm}$ ($\vert{}I_1\vert{} = 5.84\text{ A}_{\text{pk}}$ if driven by an unthrottled $5\text{ V}_{\text{pk}}$ zero-impedance source), $V_{C1,\text{pk}}$ reaches $314.4\text{ V}_{\text{pk}}$ (`B-C1`, R = 0.455 Ω)—requiring current limiting and $\ge 100\text{–}250\text{ V}$ C0G/polypropylene film capacitors.

### 5.2 ICNIRP Human Magnetic-Field Exposure Evaluation at $f_0 = 500\text{ kHz}$
* **ICNIRP Reference Level:** According to the **International Commission on Non-Ionizing Radiation Protection (ICNIRP)** guidelines (*ICNIRP Guidelines for Limiting Exposure to Time-Varying Electric and Magnetic Fields (1 Hz to 100 kHz)*, Health Physics 99(6):818–836, 2010; and *ICNIRP Guidelines for Limiting Exposure to Electromagnetic Fields (100 kHz to 300 GHz)*, Health Physics 118(5):483–524, 2020; alongside ICNIRP 1998), the general-public reference level for continuous magnetic field exposure at $f = 500\text{ kHz}$ ($0.5\text{ MHz}$) is:
  * **ICNIRP (1998) / IEEE C95.1 general public magnetic flux density limit (0.15–150 MHz):** $B_{\text{lim,rms}} = \frac{0.92\text{ }\mu\text{T}}{f_{\text{MHz}}} = \frac{0.92}{0.5} = \mathbf{1.84\text{ }\mu\text{T}_{\text{rms}}}$ (occupational limit: $4.0\text{ }\mu\text{T}_{\text{rms}}$), while the **ICNIRP (2010) electrostimulation reference level** (for localized inductive exposure up to $10\text{ MHz}$) is $\mathbf{27\text{ }\mu\text{T}_{\text{rms}}}$ (general public) and $\mathbf{100\text{ }\mu\text{T}_{\text{rms}}}$ (occupational).
* **Comparison with Our Link's On-Axis Magnetic Field ($d = 5\text{ cm}$ Operating Point, $P_L = 1.79\text{ W}$, $I_1 = 0.833\text{ A}_{\text{pk}} = 0.589\text{ A}_{\text{rms}}$):**
  * **Inside the coil gap ($z = 0\text{ to }5\text{ cm}$):** $B_{\text{rms}}$ ranges from **$82.3\text{ }\mu\text{T}_{\text{rms}}$** (at the primary center $z = 0$) to **$24.6\text{ }\mu\text{T}_{\text{rms}}$** (at $z = 5\text{ cm}$). This exceeds the $27\text{ }\mu\text{T}_{\text{rms}}$ ICNIRP 2010 general-public limit inside the $0\text{–}4.7\text{ cm}$ active air gap (while remaining below the $100\text{ }\mu\text{T}_{\text{rms}}$ occupational ceiling).
  * **Safe Stand-Off Distance:** Because the near-field magnetic flux density decays rapidly as $1/z^3$, $B_{\text{rms}}$ falls below the **$27\text{ }\mu\text{T}_{\text{rms}}$** ICNIRP (2010) public threshold at **$z \ge 4.7\text{ cm}$**, and falls below the stringent **$1.84\text{ }\mu\text{T}_{\text{rms}}$** ICNIRP (1998) whole-body threshold at **$z \ge 15.4\text{ cm}$** ($B_{\text{rms}} = 1.97\text{ }\mu\text{T}_{\text{rms}}$ at $15\text{ cm}$ and $0.88\text{ }\mu\text{T}_{\text{rms}}$ at $20\text{ cm}$). Keeping hands/body $> 16\text{ cm}$ from the active coils ensures full compliance with all ICNIRP public exposure standards.