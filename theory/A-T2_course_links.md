# A-T2 — Tying the link to the course: boundary conditions, eddy currents, Poynting

Member A, EE2025 resonant WPT (series-series). Conventions and symbols follow CONVENTIONS.md Section 3 and A-T1 (`theory/A-T1_magnetic_link.md`).

**Course map (Shevgaonkar, *Electromagnetic Waves*, checked against the contents page):**
§3.3 Maxwell's equations (p. 125), §3.4 surface charge and surface current (p. 131), **§3.5 boundary conditions at a media interface** (p. 131); §4.6 wave propagation in a conducting medium, i.e. skin depth (p. 172), **§4.8 power flow and the Poynting vector** (p. 183), §4.9 surface current and power loss in a conductor (p. 191).

**Result in one line.** The boundary conditions explain why a metal plate near a coil lowers $L$ and $k$ and adds loss (it forces normal $B$ to about zero) while a ferrite sheet raises them (it pulls flux in). The complex Poynting theorem shows that the source sees real power $=$ losses in $R_1$, $R_2$ and $R_L$ plus a reactive term $2\omega(W_m-W_e)$ that is zero at resonance, which is why $Z_{\rm in}$ is purely resistive at $f_0$.

## Symbols added in A-T2 (SI units)

| Symbol | Meaning | Unit |
|---|---|---|
| $\hat{\mathbf n}$ | unit normal to an interface, pointing from medium 2 into medium 1 | – |
| $\mathbf K$ | surface current density | A/m |
| $\mu_r$, $\mu=\mu_r\mu_0$ | relative and absolute permeability | –, H/m |
| $\sigma$ | conductivity (Cu $5.8\times10^7$, Al $3.5\times10^7$) | S/m |
| $\delta$ | skin depth $\sqrt{2/(\omega\mu\sigma)}$ | m |
| $R_s$ | surface resistance $1/(\sigma\delta)$ | Ω (per square) |
| $t$ | plate or sheet thickness | m |
| $h$ | spacing from coil plane to plate or sheet | m |
| $\mathbf S$ | complex Poynting vector $\tfrac12\mathbf E\times\mathbf H^*$ | W/m² |
| $W_m$, $W_e$ | time-averaged stored magnetic, electric energy | J |
| $P_{\rm in}$, $P_{\rm loss}$ | time-averaged input and dissipated power | W |
| $V_s$ | source voltage (phasor peak) at the primary terminals | V |
| $Z_{\rm in}$ | input impedance seen by the source | Ω |

Phasors are peak values, so time averages carry a factor $\tfrac12$ (power) or $\tfrac14$ (energy).

## 1. Boundary conditions for B and H (Shevgaonkar §3.5)

From $\nabla\cdot\mathbf B = 0$ (pillbox) and $\nabla\times\mathbf H = \mathbf J$ (thin rectangular loop) at an interface:

$$\hat{\mathbf n}\cdot(\mathbf B_1-\mathbf B_2) = 0, \qquad \hat{\mathbf n}\times(\mathbf H_1-\mathbf H_2) = \mathbf K.$$

Units: T on both sides; A/m on both sides. ✓

In words: **normal $B$ is always continuous**; **tangential $H$ jumps by the surface current**, and is continuous when $\mathbf K = 0$. A real conductor of finite $\sigma$ has no true surface current ($\mathbf K$ needs infinite $\sigma$); its current is a volume current squeezed into a layer about $\delta$ thick. So for a real metal plate tangential $H$ is continuous, then decays inside as $e^{-x/\delta}$. When $t \gg \delta$ that layer acts like a sheet $\mathbf K$, and the perfect-conductor form with $\mathbf K$ is a good model. (The brief's "tangential H continuous (no surface current)" is right for finite $\sigma$; I add the $\mathbf K$ form because that is what the textbook uses for good conductors.)

### (i) Good conductor: aluminium plate

Skin depth at $f_0 = 500$ kHz: $\delta_{\rm Al} = 1/\sqrt{\pi f\mu_0\sigma} = 1/\sqrt{\pi(5\times10^5)(4\pi\times10^{-7})(3.5\times10^7)} = 0.120$ mm. A 1 mm plate is about $8\delta$ thick, so fields inside the bulk are about $e^{-8}\approx 3\times10^{-4}$ of their surface value: $\mathbf B\approx 0$ inside.

Apply the conditions at the plate surface:
- Normal $B$ continuous and $B\approx0$ inside, so **$B_n\approx 0$ just outside**. Field lines cannot enter the plate; they are bent to run parallel to it.
- Tangential $H$ outside equals the sheet current: $|\mathbf K| = |H_t|$. That is the eddy current (Section 2).

### (ii) High-µ ferrite sheet

MnZn ferrite: $\mu_r$ of order 1000 to 3000 at hundreds of kHz, and $\sigma$ only about 0.1 to 10 S/m, so $\delta$ is many cm and eddy currents in it are negligible. Take $\mathbf K = 0$:
- $B_{n}$ continuous and $H_{t}$ continuous, so $B_t^{\rm ferrite} = \mu_r B_t^{\rm air}$.
- The field lines refract: $\tan\theta_{\rm ferrite}/\tan\theta_{\rm air} = \mu_r$ (angles from the normal). With $\mu_r = 2000$, a line entering at $10°$ from the normal runs at $\arctan(2000\tan10°) = 89.8°$ inside, i.e. almost along the sheet. The ferrite acts as a low-reluctance path that collects and guides flux. ($\mu_r$ values are typical datasheet ranges, not our measured material.)

## 2. Metal plate: Faraday, Lenz and eddy currents

The coil's changing flux crosses the plate, so by Faraday ($\oint\mathbf E\cdot d\mathbf l = -d\Phi/dt$) an EMF drives circulating currents $\mathbf J = \sigma\mathbf E$ in it. By Lenz their field opposes the coil's flux. For $t\gg\delta$ the cancellation is almost complete inside, which is exactly the $B_n\approx0$ condition of Section 1.

**Image model (quasi-static, plate large and $t\gg\delta$).** $B_n = 0$ on a plane is met by an image coil at distance $2h$ carrying the opposite current. So the plate subtracts the image's mutual inductance:

$$L' = L - M(2h).$$

Illustrative numbers (A-T1 coil: $a = 5$ cm, $N = 10$, wire radius 0.3 mm; not our final coil). Self-inductance $L\approx N^2\mu_0a[\ln(8a/r_w)-2] = 100(4\pi\times10^{-7})(0.05)[\ln(1333)-2] = 32.6\ \mu$H. With a plate at $h = 1$ cm, $M(2h = 2\text{ cm}) = 6.75\ \mu$H (A-T1 table), so

$$L' = 32.6 - 6.75 = 25.9\ \mu\text{H} \quad(-21\,\%).$$

**Effect on $k$.** Plate 1 cm behind the primary, secondary at $d = 5$ cm: the image (opposite current) sits $d+2h = 7$ cm from the secondary, so $M' = M(5) - M(7) = 2.47 - 1.43 = 1.04\ \mu$H against $2.47\ \mu$H without the plate, and $k' = 1.04/\sqrt{25.9\times32.6} = 0.036$ against $k = 2.47/32.6 = 0.076$. **$k$ roughly halves.** Since $\eta_{\max}$ depends on $k^2Q_1Q_2$, that is a factor of about 4 lost.

**Extra loss (Shevgaonkar §4.9).** The plate dissipates $P = \tfrac12R_s\int|H_t|^2dA$ with $R_s = 1/(\sigma\delta) = 1/(3.5\times10^7\times1.2\times10^{-4}) = 0.24$ mΩ. Using the image model, $H_t$ at the plate is twice the free-space radial field of the coil. My numerical integral of that over the plate gives $P\approx 0.052$ W per 1 A peak coil current, i.e. an added series resistance $\Delta R = 2P/|I|^2\approx 0.10\ \Omega$. Against a coil resistance of about 0.3 Ω this cuts $Q$ by about 25 %. (Flagged: one-off script estimate using the off-axis loop field; worth re-checking in Claude Code if we put it on the poster.)

**Summary: metal plate means lower $L$, lower $k$, extra loss.** Practical lesson for the demo: keep the bench, screws and any metal enclosure several coil radii away, or note them as an error source in A-V1.

## 3. Ferrite: higher L and k, plus core loss

A thick, wide high-µ sheet is met by an image coil with the **same** current direction, scaled by $(\mu_r-1)/(\mu_r+1)$ (= 0.999 for $\mu_r = 2000$):

$$L' = L + \frac{\mu_r-1}{\mu_r+1}M(2h).$$

Same example, ferrite 1 cm behind the primary: $L' = 32.6 + 0.999\times6.75 = 39.4\ \mu$H (+21 %), $M' = 2.47 + 0.999\times1.43 = 3.90\ \mu$H, $k' = 3.90/\sqrt{39.4\times32.6} = 0.109$ against 0.076 (+44 %). These are upper bounds: a real sheet is finite in size and thickness and pulls in less.

Costs: (1) **core loss** (hysteresis and residual eddy loss), modelled by a complex permeability $\mu = \mu'-j\mu''$, which adds a series resistance $\propto\omega\mu''$ and lowers $Q$; (2) saturation at high field; (3) weight and cost. Ferrite backing is used in EV pads and phone chargers mainly because it both raises $k$ and **shields** metal behind it (the ferrite carries the flux so it never reaches the metal).

## 4. Complex Poynting theorem for the two-coil system (Shevgaonkar §4.8)

Phasor form, for a volume $V$ with surface $S$ (outward normal), with $\mathbf S = \tfrac12\mathbf E\times\mathbf H^*$:

$$-\oint_S\mathbf S\cdot d\mathbf A = \underbrace{\tfrac12\int_V\sigma|\mathbf E|^2dV}_{P_{\rm loss}} + j2\omega\underbrace{\int_V\left(\tfrac14\mu|\mathbf H|^2-\tfrac14\varepsilon|\mathbf E|^2\right)dV}_{W_m-W_e}$$

Units: W/m² × m² = W; (rad/s)(J) = W. ✓

**Applied to our circuit.** Enclose both coils, capacitors and the load, with only the source terminals crossing $S$. The power flowing in is $\tfrac12V_sI_1^*$. In the lumped model the same theorem appears if each KVL equation is multiplied by the conjugate current and the two are added:

$$V_sI_1^* = Z_1|I_1|^2 + Z_2|I_2|^2 + j\omega M(I_2I_1^* + I_1I_2^*) = Z_1|I_1|^2 + Z_2|I_2|^2 + j2\omega M\,\mathrm{Re}(I_1I_2^*).$$

Halving and splitting into real and imaginary parts:

$$\tfrac12V_sI_1^* = \underbrace{\tfrac12R_1|I_1|^2 + \tfrac12(R_2+R_L)|I_2|^2}_{P_{\rm loss}\ \text{(incl. the load)}} + j2\omega(W_m-W_e),$$

$$W_m = \tfrac14L_1|I_1|^2 + \tfrac14L_2|I_2|^2 + \tfrac12M\,\mathrm{Re}(I_1I_2^*), \qquad W_e = \frac{|I_1|^2}{4\omega^2C_1} + \frac{|I_2|^2}{4\omega^2C_2}.$$

(Check: $2\omega\cdot\tfrac14L_1|I_1|^2 = \tfrac12\omega L_1|I_1|^2$, which is half of the $\omega L_1|I_1|^2$ in $Z_1|I_1|^2$. ✓)

**At resonance the reactive term vanishes.** At $\omega_0$, $\omega_0L_i = 1/(\omega_0C_i)$, so $\tfrac14L_i|I_i|^2 = |I_i|^2/(4\omega_0^2C_i)$: $W_m = W_e$ **in each resonator separately**. The mutual term is zero too, because $I_2 = -j\omega_0MI_1/(R_2+R_L)$ is 90° from $I_1$, so $I_1I_2^*$ is purely imaginary. Hence $\tfrac12V_sI_1^*$ is real and

$$Z_{\rm in} = R_1 + \frac{\omega_0^2M^2}{R_2+R_L}\quad\text{(purely resistive), as in the equation reference.}$$

**Numbers (reference test case, $I_1 = 1$ A peak):** $L = 15\ \mu$H, $R_1=R_2 = 0.3\ \Omega$, $M = 1.5\ \mu$H, $R_L = 4.72\ \Omega$, $f_0 = 500$ kHz.
- $\omega_0M = 2\pi(5\times10^5)(1.5\times10^{-6}) = 4.712\ \Omega$; $|I_2| = 4.712/(0.3+4.72) = 0.939$ A.
- $P_{R1} = \tfrac12(0.3)(1)^2 = 0.150$ W; $P_{R2} = \tfrac12(0.3)(0.939)^2 = 0.132$ W; $P_{RL} = \tfrac12(4.72)(0.939)^2 = 2.080$ W; total $2.362$ W.
- $\eta_{\rm link} = 2.080/2.362 = 88.05\,\%$ ✓ (matches $\eta_{\max}$ of the reference case).
- $Z_{\rm in} = 0.3 + 4.712^2/5.02 = 4.724\ \Omega$, so $\tfrac12|I_1|^2Z_{\rm in} = 2.362$ W ✓ (Poynting input = sum of losses).
- Stored energy $W_m+W_e = 2W_m = 2[\tfrac14(15\,\mu)(1) + \tfrac14(15\,\mu)(0.881)] = 14.1\ \mu$J, about 3 cycles' worth of delivered energy ($2.362/5\times10^5 = 4.72\ \mu$J per cycle).

Off resonance (e.g. 1 % above $f_0$, same circuit) $W_m > W_e$, $Z_{\rm in} = 4.66 + j0.12\ \Omega$, and the source must also supply reactive power that sloshes back and forth without doing work.

## 5. Why this is near-field transfer

The coils are about $10^{-4}\lambda$ across and the whole link sits well inside $\lambda/2\pi = 600/2\pi = 95$ m, so the field is the reactive near field of a magnetic dipole: it falls like $1/r^3$ and is almost purely magnetic (wave impedance about $\eta_0k_0r = 377\times(0.0105)(0.05) = 0.2\ \Omega$ at 5 cm, against 377 Ω for a plane wave). Most of the energy is stored, about 14 µJ in the example, and is swapped between coils and capacitors each cycle rather than launched outward, which is why $R_{\rm rad}\approx10^{-9}\ \Omega$ (A-T1). Real power crosses the gap only because the secondary carries a current: the real part of $\mathbf S$ through any surface separating the coils equals $\tfrac12(R_2+R_L)|I_2|^2$, and the useful part appears as $\tfrac12R_L|I_2|^2$ in the load. Remove the secondary and the net real flux falls back to the primary's own losses: nothing is "broadcast".

**Skin depth link (Shevgaonkar §4.6).** The same $\delta$ sets the coil's own loss: copper at 500 kHz has $\delta = 0.094$ mm, smaller than a 0.6 mm wire's 0.3 mm radius, so $R_{\rm ac}/R_{\rm dc}\approx r_w/(2\delta) = 0.3/(2\times0.094) = 1.6$ before proximity effect. That is why $R$ (and therefore $Q$) must be measured at $f_0$, not with a DC ohmmeter.

## Poster equations chosen (2)

1. **Interface conditions** $\hat{\mathbf n}\cdot(\mathbf B_1-\mathbf B_2) = 0$, $\hat{\mathbf n}\times(\mathbf H_1-\mathbf H_2) = \mathbf K$: why nearby metal (B_n → 0, eddy currents) weakens the link and ferrite (flux guiding) strengthens it.
2. **Complex Poynting theorem** $\tfrac12V_sI_1^* = P_{\rm loss} + j2\omega(W_m-W_e)$: the source supplies only the power burnt in $R_1$, $R_2$, $R_L$; at $f_0$, $W_m = W_e$ so the input is purely resistive.

(Skin depth $\delta = \sqrt{2/(\omega\mu_0\sigma)}$ goes in as a supporting line next to the conductor-loss bullet.)

## Oral questions

**Q1. Why does an aluminium plate behind the coil reduce $k$, when aluminium is not magnetic?**
At 500 kHz the plate is about 8 skin depths thick, so eddy currents (Faraday plus Lenz) cancel the field inside. Continuity of normal $B$ then forces $B_n\approx0$ at the surface, which acts like an opposing image coil: $L$ drops and $M$ drops more, so $k$ falls (about halved in our example) and the eddy currents add loss.

**Q2. If the field stores energy, why does the source see a pure resistance at resonance?**
By the complex Poynting theorem the imaginary part of the input power is $2\omega(W_m-W_e)$. At $f_0$ each coil's magnetic energy equals its capacitor's electric energy, so that term is zero and only the dissipated power $\tfrac12R_1|I_1|^2 + \tfrac12(R_2+R_L)|I_2|^2$ remains.

**Q3. Ferrite raises $k$. Why not always use it?**
It adds core loss (through $\mu''$), which lowers $Q$, it can saturate at high field, and it adds weight and cost. It is worth it when $k$ is small or when metal behind the coil must be shielded, as in EV and phone chargers.
