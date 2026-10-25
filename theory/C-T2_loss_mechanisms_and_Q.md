# Task C-T2: Loss Mechanisms and Unloaded Quality Factor ($Q$)

**Status:** Complete (evaluated for `v1-design` parameters in `sim/params.py`)

---

## 1. Definition of Unloaded Quality Factor ($Q$)

For a series resonant coil-capacitor tank operating at angular resonance $\omega_0 = 2\pi f_0 = \frac{1}{\sqrt{LC}}$, the **unloaded quality factor** $Q$ measures the ratio of peak reactive energy stored in the resonator to the energy dissipated per radian:

$$Q_i = \frac{\omega_0 L_i}{R_i} = \frac{1}{\omega_0 C_i R_i} \quad (i \in \{1, 2\})$$

Per project conventions, $Q$ always denotes the **unloaded** quality factor, where $R_i$ is the total parasitic series resistance of resonator $i$ alone (excluding the external load resistance $R_L$). The total series resistance is the sum of five distinct physical loss mechanisms:

$$R_i = R_{\text{ac,skin}} + R_{\text{prox}} + R_{\text{ESR}} + R_{\text{conn}} + R_{\text{rad}} + R_{\text{eddy,env}}$$

where:
* $R_{\text{ac,skin}}$: Ohmic resistance of the copper winding including the high-frequency skin effect (which subsumes the DC resistance $R_{\text{dc}}$).
* $R_{\text{prox}}$: Additional ohmic loss induced by the magnetic fields of adjacent turns (proximity effect).
* $R_{\text{ESR}}$: Equivalent series resistance of the tuning capacitor due to dielectric dissipation.
* $R_{\text{conn}}$: Contact and solder-joint resistance at the resonator terminals.
* $R_{\text{rad}}$: Radiation resistance representing power lost as propagating electromagnetic waves.
* $R_{\text{eddy,env}}$: Reflected resistance from eddy currents induced in nearby conductive objects.

---

## 2. Skin Depth and High-Frequency Winding Resistance ($R_{\text{dc}}$ and $R_{\text{ac,skin}}$)

### 2.1 Derivation of Skin Depth ($\delta$)
In a good conductor such as copper ($\sigma \approx 5.8 \times 10^7\text{ S/m}$, $\mu = \mu_0 = 4\pi \times 10^{-7}\text{ H/m}$), conduction current greatly exceeds displacement current ($\sigma \gg \omega\varepsilon$) at hundreds of kHz. Starting from Maxwell's curl equations in phasor form:

$$\nabla \times \mathbf{E} = -j\omega\mu_0\mathbf{H}, \qquad \nabla \times \mathbf{H} = \mathbf{J} = \sigma\mathbf{E}$$

Taking the curl of Faraday's law and applying the vector identity $\nabla \times (\nabla \times \mathbf{E}) = \nabla(\nabla \cdot \mathbf{E}) - \nabla^2\mathbf{E}$ (with $\nabla \cdot \mathbf{E} = 0$ in a uniform conductor) yields the vector Helmholtz diffusion equation:

$$\nabla^2 \mathbf{E} = j\omega\mu_0\sigma\mathbf{E} = \gamma^2 \mathbf{E}$$

where the propagation constant is:

$$\gamma = \sqrt{j\omega\mu_0\sigma} = (1 + j)\sqrt{\frac{\omega\mu_0\sigma}{2}} = \frac{1 + j}{\delta}$$

For a uniform plane wave penetrating into a conductor surface along depth $z$, the electric field and current density decay exponentially as $J(z) = J_0 e^{-z/\delta} e^{-jz/\delta}$. The **skin depth** $\delta$—the depth at which current density falls to $1/e \approx 36.8\%$ of its surface value—is:

$$\delta = \sqrt{\frac{2}{\omega\mu_0\sigma}} = \sqrt{\frac{1}{\pi f \mu_0 \sigma}}$$

### 2.2 Skin Depth and $R_{\text{ac}}/R_{\text{dc}}$ in Copper
For a solid cylindrical wire of radius $r_w$ and total unwound length $\ell$, the uniform low-frequency DC resistance is:

$$R_{\text{dc}} = \frac{\ell}{\sigma \pi r_w^2} = \frac{\rho_{\text{Cu}} \ell}{\pi r_w^2}$$

When operating at high frequency where $r_w \gg \delta$, the current is confined to a thin annular shell of thickness $\delta$ near the wire circumference $2\pi r_w$, giving an effective conducting cross-sectional area $A_{\text{eff}} \approx 2\pi r_w \delta$ (assuming $r_w \gg \delta$). The resulting high-frequency AC resistance and ratio are:

$$R_{\text{ac,skin}} \approx \frac{\ell}{\sigma (2\pi r_w \delta)} \implies \frac{R_{\text{ac,skin}}}{R_{\text{dc}}} \approx \frac{\pi r_w^2}{2\pi r_w \delta} = \frac{r_w}{2\delta}$$

*(Note: Using the thin-annulus correction $\pi r_w^2 - \pi(r_w - \delta)^2 = 2\pi r_w \delta(1 - \delta/2r_w)$ gives the exact tubular ratio $\frac{r_w}{2\delta(1 - \delta/2r_w)}$ when $\delta$ is a noticeable fraction of $r_w$.)*

Evaluating $\delta$ and $R_{\text{ac,skin}}/R_{\text{dc}}$ for our `v1-design` wire diameter $d_w = 0.7\text{ mm}$ ($r_w = 0.35\text{ mm}$) with $\sigma = 5.8 \times 10^7\text{ S/m}$ ($\rho_{\text{Cu}} = 1.724 \times 10^{-8}\text{ }\Omega\cdot\text{m}$):

| Frequency ($f$) | Skin Depth $\delta$ [mm] | Asymptotic Ratio $\frac{r_w}{2\delta}$ | Exact Annular Ratio $\frac{r_w}{2\delta(1 - \delta/2r_w)}$ |
| :--- | :--- | :--- | :--- |
| **100 kHz** | $0.209\text{ mm}$ ($\approx 0.21\text{ mm}$) | $0.837$ (floor $= 1.00$) | $1.19$ |
| **500 kHz ($f_0$)** | $0.0935\text{ mm}$ ($\approx 0.094\text{ mm}$) | **$1.87$** | **$2.16$** |
| **1 MHz** | $0.0661\text{ mm}$ ($\approx 0.066\text{ mm}$) | $2.65$ | $2.92$ |

---

## 3. Proximity Effect and Litz Wire Mitigation ($R_{\text{prox}}$)

When wire is wound into a compact multi-turn flat spiral ($N = 10$, pitch $p = 1.0\text{ mm}$, wire diameter $d_w = 0.7\text{ mm}$, edge-to-edge turn gap $= 0.3\text{ mm}$), each turn $i$ (at radius $r_i$) sits inside the time-varying transverse magnetic field $H_{\text{ext},i}$ produced by all neighbouring turns $j \neq i$.

### 3.1 First-Principles Calculation for Our 10-Turn Spiral (`v1-design`)
1. **Transverse Field at Each Turn:** Evaluating the exact coplanar elliptic-integral field $H_{z,j\to i} = \frac{I}{2\pi(r_j + r_i)}\left[K(m_{ij}) + \frac{r_j^2 - r_i^2}{(r_j - r_i)^2}E(m_{ij})\right]$ summed over $j \neq i$ for $I = 1\text{ A}_{\text{pk}}$ gives $|H_{\text{ext},0}| = 383.4\text{ A/m}$ (outer turn), a minimum of $|H_{\text{ext},3}| = 21.1\text{ A/m}$ (turn 3, where inner and outer turns partially cancel), and $|H_{\text{ext},9}| = 525.8\text{ A/m}$ (inner turn), with length-weighted sum $\sum_{i=0}^{9} (H_{\text{ext},i}/I)^2 (2\pi r_i) = 1.946 \times 10^5\text{ m}^{-1}$ (cross-checked by the Biot–Savart segment sum, `python -m sim.proximity_check`).
2. **Surface-Impedance & Bessel Bounds ($r_w/\delta = 3.745$):**
   * In the high-frequency surface-impedance model ($R_s = \frac{1}{\sigma\delta} = 0.1845\text{ m}\Omega$, tangential surface field $H_\phi = 2 H_{\text{ext}}\sin\phi$), the eddy power per unit length is $P_{\text{prox}}' = \frac{1}{2} R_s \int_0^{2\pi} (2 H_{\text{ext}}\sin\phi)^2 r_w\,d\phi = 2\pi r_w R_s H_{\text{ext}}^2$ (since $\int_0^{2\pi}\sin^2\phi\,d\phi = \pi$), and with $R = 2P/I^2$:
     $$R_{\text{prox,surface}} = 4\pi r_w R_s \sum_{i=0}^{9} \left(\frac{H_{\text{ext},i}}{I}\right)^2 (2\pi r_i) = \mathbf{0.158\text{ }\Omega}$$
   * Solving the exact interior cylindrical Bessel boundary-value problem $A_z(\rho,\phi) = \frac{2\mu_0 H_{\text{ext}}}{k J_0(k r_w)} J_1(k\rho)\cos\phi$ with $k = \frac{1-j}{\delta}$ at $r_w/\delta = 3.745$ gives $\mathbf{0.136\text{ }\Omega}$, i.e. 0.862 times the surface-impedance value. At finite $r_w/\delta$ the field penetrates less than the thin-skin model assumes, so the thin-skin value (0.158 Ω) lies *above* the exact one; it is not a lower bound.
   * **Best estimate: $R_{\text{prox}} = 0.136\text{ }\Omega$** (exact isolated-cylinder solution, about 50 % of $R_{\text{ac,skin}}$). Neglected: field non-uniformity across the wire (1 mm pitch vs $r_w = 0.35$ mm) and screening by eddy currents in neighbouring turns, which can only lower it; the budget allows up to 25 % lower (0.10 Ω). This raises the team value to $R_1 = R_2 = 0.455\text{ }\Omega$ (`sim/params.py`, 2026-10-25), range 0.38–0.48 Ω.
   * *(Corrected 2026-10-25: the earlier text had the sum 1.131e5 /m, the loss per metre $\pi r_w R_s H^2$ (missing a factor 2) and 0.079 Ω, and treated the thin-skin value as a lower bound.)*

**Why Litz Wire Helps:** Litzendraht (Litz) wire replaces a single solid conductor of radius $r_w$ with a bundle of many individually insulated thin copper strands, each having a strand radius $r_s \ll \delta$ (for $500\text{ kHz}$, AWG 40–44 strands with $r_s \approx 0.025\text{–}0.04\text{ mm} < 0.094\text{ mm}$). Because each strand is thinner than a skin depth and twisted across all radial/azimuthal bundle positions, proximity eddy currents are suppressed by over an order of magnitude.

## 4. Capacitor Dielectric Loss ($R_{\text{ESR}}$)

Real tuning capacitors dissipate energy through dielectric polarization relaxation and electrode resistance, quantified by the datasheet **loss tangent** (dissipation factor) $\tan\delta_C$:

$$R_{\text{ESR}} = \frac{\tan\delta_C}{\omega_0 C}$$

At $f_0 = 500\text{ kHz}$ with $L = 17.13\text{ }\mu\text{H}$, the required series capacitance from `sim/params.py` is:

$$C_1 = C_2 = \frac{1}{(2\pi f_0)^2 L} = 5.915\text{ nF}, \qquad \frac{1}{\omega_0 C} = \omega_0 L = 53.82\text{ }\Omega$$

* **C0G / NP0 Ceramic or Polypropylene Film Capacitors** ($\tan\delta_C \approx 5 \times 10^{-4}$ to $1 \times 10^{-3}$):
  $$R_{\text{ESR}} = (5 \times 10^{-4} \text{ to } 1 \times 10^{-3}) \times 53.82\text{ }\Omega \approx 0.027\text{ to } 0.054\text{ }\Omega$$
* **Why X7R/Y5V Ceramics Must Be Avoided:** Standard high-permittivity ceramics have $\tan\delta_C \approx 0.025$, which would add $R_{\text{ESR}} \approx 1.35\text{ }\Omega$—single-handedly tripling the resonator resistance and collapsing $Q$.

---

## 5. Secondary & System-Level Losses

1. **Radiation Resistance ($R_{\text{rad}}$):** At $f_0 = 500\text{ kHz}$, the free-space wavelength is $\lambda = c/f_0 = 600\text{ m}$. Because the coil radius ($a \approx 4.5\text{ cm}$) satisfies $ka = 2\pi a/\lambda \approx 4.7 \times 10^{-4} \ll 1$, the coil is electrically tiny. For an $N$-turn small magnetic loop of effective area $A_{\text{eff}} = \sum_{i=0}^{N-1} \pi r_i^2 = 0.0643\text{ m}^2$:
   $$R_{\text{rad}} \approx 31\,171 \left(\frac{A_{\text{eff}}}{\lambda^2}\right)^2 = 31\,171 \left(\frac{0.0643}{600^2}\right)^2 \approx 9.9 \times 10^{-10}\text{ }\Omega \sim 10^{-9}\text{ }\Omega$$
   This is nine orders of magnitude smaller than the ohmic winding resistance and is completely negligible.
2. **Environmental Eddy Losses ($R_{\text{eddy,env}}$):** Any non-magnetic conductor (such as an aluminium plate or bench chassis) placed near the coils experiences induced eddy currents of skin depth $\delta_{\text{plate}}$, reflecting a dissipative resistance back into the coil loop and reducing $Q$.
3. **System-Level DC-to-DC Losses ($\eta_{\text{sys}}$ vs $\eta_{\text{link}}$):** While $\eta_{\text{link}}$ depends only on resonator resistances $R_1, R_2$ and coupling $k$, the overall DC-to-DC efficiency $\eta_{\text{sys}}$ is further reduced by:
   * **Rectifier Diode Conduction Loss:** In a full-bridge rectifier, two diodes conduct during each half-cycle, dropping $2 V_F$ (using Schottky diodes with $V_F \approx 0.3\text{–}0.4\text{ V}$ minimizes this compared to $2 \times 0.7\text{ V} = 1.4\text{ V}$ for standard PN diodes).
   * **Driver Output Impedance & Switching Loss:** Source output impedance ($50\text{ }\Omega$ if driven directly from a function generator without measuring at the resonator terminals) or MOSFET $R_{\text{DS(on)}}$ and switching transitions in a half-bridge driver.

---

## 6. Expected $R$ and $Q$ Calculation for `v1-design` (`sim/params.py`)

### 6.1 Exact Coil Wire Length from `sim/params.py` Geometry
Using the flat-spiral convention in `sim/params.py` ($N = 10$, $d_{\text{out}} = 0.10\text{ m}$, $d_w = 0.7\text{ mm}$, $\text{pitch} = 1.0\text{ mm}$):

$$r_i = \frac{d_{\text{out}}}{2} - \frac{d_w}{2} - i \cdot \text{pitch} = 0.04965 - 0.001\,i\text{ [m]} \quad (i = 0, 1, \dots, 9)$$

* Outermost turn radius: $r_0 = 49.65\text{ mm}$
* Innermost turn radius: $r_9 = 40.65\text{ mm}$
* Mean turn radius: $\bar{r} = 45.15\text{ mm}$
* Total spiral wire length: $\ell_{\text{spiral}} = \sum_{i=0}^{9} 2\pi r_i = 2\pi (10 \times 0.04515\text{ m}) = 2.837\text{ m}$
* Including $2 \times 15\text{ cm} = 0.30\text{ m}$ termination leads (per Task A-H1): $\ell_{\text{total}} = 3.137\text{ m}$
* Wire cross-sectional area: $A_w = \pi r_w^2 = \pi (0.35 \times 10^{-3}\text{ m})^2 = 3.848 \times 10^{-7}\text{ m}^2$

### 6.2 Resistance Breakdown & Dominance Ranking (at $f_0 = 500\text{ kHz}$)

| Rank | Loss Component | Formula / Evaluation (`v1-design`) | Expected Value [$\Omega$] | Share of Total $R$ |
| :--- | :--- | :--- | :--- | :--- |
| **1 (Dominant)** | **AC Skin-Effect Winding Resistance ($R_{\text{ac,skin}}$)** | $R_{\text{dc}} = \frac{\rho_{\text{Cu}}\ell}{A_w} = 0.127\text{ }\Omega$ (spiral) to $0.141\text{ }\Omega$ (with leads)<br>$R_{\text{ac,skin}} = R_{\text{dc}} \times \frac{r_w}{2\delta} = 0.141\text{ }\Omega \times 1.87$ *(or $0.275\text{ }\Omega$ using exact tubular factor $2.16$)* | **$0.24\text{ – }0.28\text{ }\Omega$** (nominal 0.269) | **$\sim 59\%$** |
| **2** | **Turn-to-Turn Proximity Loss ($R_{\text{prox}}$)** | Exact cylinder (Bessel) in the field of the other turns, Section 3.1; up to 25 % lower with screening | **$0.10\text{ – }0.136\text{ }\Omega$** (nominal 0.136) | **$\sim 30\%$** |
| **3** | **Capacitor Dielectric ESR ($R_{\text{ESR}}$)** | $\frac{\tan\delta_C}{\omega_0 C} = \tan\delta_C \times 53.82\text{ }\Omega$ (for C0G/film with $\tan\delta_C \approx 5\times 10^{-4}\text{–}7\times 10^{-4}$) | **$0.03\text{ – }0.04\text{ }\Omega$** (nominal 0.035) | **$\sim 8\%$** |
| **4** | **Terminal & Solder Connections ($R_{\text{conn}}$)** | Contact resistance of solder joints and shunt connections | **$0.01\text{ – }0.02\text{ }\Omega$** (nominal 0.015) | **$\sim 3\%$** |
| **5 (Negligible)** | **Radiation Resistance ($R_{\text{rad}}$)** | $31\,171 (A_{\text{eff}}/\lambda^2)^2$ at $\lambda = 600\text{ m}$ | **$1.0 \times 10^{-9}\text{ }\Omega$** | **$< 10^{-7}\%$** |
| — | **Total Expected Series Resistance ($R_1 = R_2$)** | Sum of the low / high ends of each term (matches `R1 = R2 = 0.455`, `R_range = (0.38, 0.48)` in `sim/params.py`; lopsided because only the proximity term can fall, by screening) | **$0.38\text{ – }0.48\text{ }\Omega$<br>(Nominal: $0.455\text{ }\Omega$)** | **$100\%$** |

### 6.3 Summary of Expected Resonator Parameters ($Q_1, Q_2$)

Using the `sim/params.py` design values ($f_0 = 500\text{ kHz}$, $L_1 = L_2 = 17.13\text{ }\mu\text{H}$, $\omega_0 L = 53.82\text{ }\Omega$, $C_1 = C_2 = 5.915\text{ nF}$):

| Parameter | Symbol | Expected Range (Analytical Sum) | Nominal Value in `sim/params.py` |
| :--- | :--- | :--- | :--- |
| **Resonant Inductive Reactance** | $\omega_0 L_1 = \omega_0 L_2$ | $53.82\text{ }\Omega$ | $53.82\text{ }\Omega$ |
| **Total Series Resistance** | $R_1, R_2$ | $0.38\text{ – }0.48\text{ }\Omega$ | **$0.455\text{ }\Omega$** |
| **Unloaded Quality Factor** | $Q_1, Q_2 = \frac{\omega_0 L}{R}$ | $112\text{ – }142$ | **$118.3$** |
| **Unloaded 3 dB Bandwidth** | $\Delta f = \frac{f_0}{Q}$ | $3.53\text{ – }4.46\text{ kHz}$ | **$4.23\text{ kHz}$** |
