# Task C-S2: Shield (Al/Cu Plate) and Ferrite Sheet Simulation Note

**Status:** Complete (`sim/shield.py`, `data/sim_shield.csv`, and `figs/fig_*_shield.*`)

---

## 1. Physical Model & Connection to A-T2 Boundary Conditions

This simulation quantifies the boundary-condition mechanisms derived in `theory/A-T2_course_links.md` using the exact 10-turn spiral geometry in `sim/params.py` ($N = 10$, $d_{\text{out}} = 100\text{ mm}$, $d_w = 0.7\text{ mm}$, $\text{pitch} = 1.0\text{ mm}$, $f_0 = 500\text{ kHz}$, free-space $L_0 = 17.13\text{ }\mu\text{H}$):

1. **Conducting Metal Plate (Aluminium $\sigma = 3.5 \times 10^7\text{ S/m}$, Copper $\sigma = 5.8 \times 10^7\text{ S/m}$):**
   At $f_0 = 500\text{ kHz}$, the skin depths are $\delta_{\text{Al}} = 0.120\text{ mm}$ and $\delta_{\text{Cu}} = 0.094\text{ mm}$. For any plate of thickness $t \ge 1\text{ mm} \gg \delta$, eddy currents screen the interior ($\mathbf{B} \approx 0$ inside), and continuity of normal flux density ($\hat{\mathbf{n}}\cdot\mathbf{B} = 0$) forces $B_n \approx 0$ at the surface. For a plate placed at gap $g$ behind the secondary coil (plane $z = d + g$), the boundary condition $B_n = 0$ is satisfied by an opposing image coil ($\alpha = -1$) at mirror distance $2g$ behind the secondary (and $d + 2g$ from the primary):
   $$L_1' = L_0 - M(2d + 2g), \qquad L_2' = L_0 - M(2g), \qquad M' = M(d) - M(d + 2g), \qquad k' = \frac{M'}{\sqrt{L_1' L_2'}}$$
   *Note per Task C-S2 specification:* This image-method formulation assumes a laterally large conducting plate with $t \gg \delta$ and therefore represents the **theoretical upper bound** on inductive screening.

2. **High-Permeability Ferrite Sheet ($\text{MnZn Ferrite}, \mu_r = 2000$):**
   With low conductivity ($\delta \gg t$) and $\mu_r \gg 1$, tangential $\mathbf{H}$ continuity refracts magnetic flux lines nearly parallel into the sheet, acting as an aiding image coil with reflection factor $\alpha_{\text{fe}} = \frac{\mu_r - 1}{\mu_r + 1} = 0.9990$:
   $$L_1' = L_0 + \alpha_{\text{fe}} M(2d + 2g), \qquad L_2' = L_0 + \alpha_{\text{fe}} M(2g), \qquad M' = M(d) + \alpha_{\text{fe}} M(d + 2g)$$

3. **Eddy-Current Power Dissipation & Reflected Resistance ($\Delta R_{\text{plate}}$):**
   Using the surface resistance $R_s = \frac{1}{\sigma\delta}$ ($R_{s,\text{Al}} = 0.238\text{ m}\Omega$, $R_{s,\text{Cu}} = 0.185\text{ m}\Omega$) and the exact off-axis elliptic-integral radial field $H_t(\rho) = 2 H_{\rho,\text{free}}(\rho, g)$ summed over all 10 spiral turns, the time-averaged eddy loss in the plate is integrated radially via Shevgaonkar §4.9:
   $$P_{\text{plate}} = \frac{1}{2} R_s \int_0^\infty \vert{}H_t(\rho)\vert{}^2 \, 2\pi\rho\,d\rho, \qquad \Delta R_{\text{plate}} = \frac{2 P_{\text{plate}}}{\vert{}I\vert{}^2}$$

---

## 2. Numerical Results (`data/sim_shield.csv`)

### 2.1 Axial Spacing $d = 3\text{ cm}$ (Free-space baseline: $L_1 = L_2 = 17.13\text{ }\mu\text{H}$, $M_0 = 3.721\text{ }\mu\text{H}$, $k_0 = 0.2172$)

| Plate Gap $g$ [mm] | Metal $L_2'$ [$\mu\text{H}$] | Metal $M'$ [$\mu\text{H}$] | Metal $k'$ ($\Delta\%$) | Ferrite $L_2'$ [$\mu\text{H}$] | Ferrite $M'$ [$\mu\text{H}$] | Ferrite $k'$ ($\Delta\%$) | Al Loss $P_{\text{Al}}$ at $1\text{ A}_{\text{pk}}$ [mW] | Al Added $\Delta R_{\text{Al}}$ [$\text{m}\Omega$] | Cu Added $\Delta R_{\text{Cu}}$ [$\text{m}\Omega$] |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **5 mm** | $8.34$ | $1.096$ | **$0.0948$ ($-56.4\%$)** | $25.91$ | $6.343$ | **$0.2921$ ($+34.5\%$)** | $88.85\text{ mW}$ | **$177.7\text{ m}\Omega$** | $138.0\text{ m}\Omega$ |
| **10 mm** | $11.63$ | $1.816$ | **$0.1319$ ($-39.3\%$)** | $22.62$ | $5.624$ | **$0.2791$ ($+28.5\%$)** | $43.68\text{ mW}$ | **$87.4\text{ m}\Omega$** | $67.9\text{ m}\Omega$ |
| **20 mm** | $14.50$ | $2.650$ | **$0.1707$ ($-21.4\%$)** | $19.75$ | $4.791$ | **$0.2567$ ($+18.2\%$)** | $16.53\text{ mW}$ | **$33.1\text{ m}\Omega$** | $25.7\text{ m}\Omega$ |
| **40 mm** | $16.30$ | $3.309$ | **$0.1994$ ($-8.2\%$)** | $17.95$ | $4.132$ | **$0.2341$ ($+7.8\%$)** | $3.94\text{ mW}$ | **$7.9\text{ m}\Omega$** | $6.1\text{ m}\Omega$ |

### 2.2 Axial Spacing $d = 5\text{ cm}$ (Free-space baseline: $L_1 = L_2 = 17.13\text{ }\mu\text{H}$, $M_0 = 1.905\text{ }\mu\text{H}$, $k_0 = 0.1112$)

| Plate Gap $g$ [mm] | Metal $L_2'$ [$\mu\text{H}$] | Metal $M'$ [$\mu\text{H}$] | Metal $k'$ ($\Delta\%$) | Ferrite $L_2'$ [$\mu\text{H}$] | Ferrite $M'$ [$\mu\text{H}$] | Ferrite $k'$ ($\Delta\%$) | Al Added $\Delta R_{\text{Al}}$ [$\text{m}\Omega$] | Cu Added $\Delta R_{\text{Cu}}$ [$\text{m}\Omega$] |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **5 mm** | $8.34$ | $0.490$ | **$0.0415$ ($-62.6\%$)** | $25.91$ | $3.318$ | **$0.1557$ ($+40.0\%$)** | $177.7\text{ m}\Omega$ | $138.0\text{ m}\Omega$ |
| **10 mm** | $11.63$ | $0.834$ | **$0.0597$ ($-46.3\%$)** | $22.62$ | $2.975$ | **$0.1497$ ($+34.6\%$)** | $87.4\text{ m}\Omega$ | $67.9\text{ m}\Omega$ |
| **20 mm** | $14.50$ | $1.260$ | **$0.0805$ ($-27.7\%$)** | $19.75$ | $2.550$ | **$0.1377$ ($+23.8\%$)** | $33.1\text{ m}\Omega$ | $25.7\text{ m}\Omega$ |
| **40 mm** | $16.30$ | $1.629$ | **$0.0978$ ($-12.0\%$)** | $17.95$ | $2.180$ | **$0.1239$ ($+11.4\%$)** | $7.9\text{ m}\Omega$ | $6.1\text{ m}\Omega$ |

---

## 3. Key Physical Insights for the Poster
1. **Triple Penalty of Unshielded Metal:** Placing an aluminium plate $5\text{ mm}$ behind the secondary coil (1) drops $L_2$ from $17.13\text{ }\mu\text{H}$ to $8.34\text{ }\mu\text{H}$ (detuning the secondary resonance upward by $+43\%$ if uncompensated), (2) cuts $k$ by more than half ($-56.4\%$ at $d=3\text{ cm}$), and (3) injects $\Delta R_{\text{Al}} = 177.7\text{ m}\Omega$ of eddy-current resistance into the secondary loop, increasing $R_2$ from $0.455\text{ }\Omega$ to $0.633\text{ }\Omega$ and cutting $Q_2$ from 118 to 85. The primary, 35 mm from the plate, picks up only $\Delta R_{11} = 10.9\text{ m}\Omega$, plus a mutual term $\Delta R_{12} = 33.1\text{ m}\Omega$ (plate loss counted for both coils). Link efficiency at $d = 3\text{ cm}$ ($R_L = 11.7\text{ }\Omega$) falls from 92.5 % to **24.0 %** if nothing is retuned, and to **63.9 %** with $C_2$ retuned to the new $L_2$ (73.1 % if $R_L$ is also re-optimised). Source: 2×2 mesh with the plate-loss matrix and $L', M'$ from `data/sim_shield.csv`; updated 2026-10-25 for $R = 0.455\text{ }\Omega$.
2. **Why Ferrite Backing Solves Both Problems:** Inserting a high-$\mu_r$ ferrite sheet between the coil and a metal chassis guides the tangential magnetic flux inside the low-loss ferrite before it can reach the metal, raising $k$ by $+28.5\%$ to $+34.5\%$ (at $g = 5\text{–}10\text{ mm}$) while eliminating plate eddy losses.