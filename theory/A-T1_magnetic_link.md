# A-T1 — The magnetic link: from Maxwell to M and k

Member A, EE2025 resonant WPT (series-series). Conventions follow CONVENTIONS.md Section 3.

**Result in one line.** At $f_0 = 500$ kHz the coils are tiny next to the wavelength ($ka \approx 5\times10^{-4}$), so the field is quasi-static. Biot–Savart gives the field of the primary, its flux through the secondary defines $M$ (Neumann, $M_{12}=M_{21}$), Faraday turns that into an EMF $V_2 = -j\omega M I_1$, and $k = M/\sqrt{L_1L_2}$ is set by geometry alone, falling like $1/d^3$ far away. Radiation is about $10^{-9}\ \Omega$ and can be ignored.

## Symbols (SI units)

| Symbol | Meaning | Unit |
|---|---|---|
| $\mathbf H$, $\mathbf B$ | magnetic field intensity, flux density ($\mathbf B=\mu_0\mathbf H$ in air) | A/m, T |
| $\mathbf E$, $\mathbf D$ | electric field, electric flux density ($\mathbf D=\varepsilon_0\mathbf E$) | V/m, C/m² |
| $\mathbf J$ | conduction current density | A/m² |
| $\mu_0$, $\varepsilon_0$ | $4\pi\times10^{-7}$ H/m, $8.854\times10^{-12}$ F/m | |
| $c$ | speed of light, $3\times10^{8}$ | m/s |
| $\sigma$ | conductivity (copper $5.8\times10^7$) | S/m |
| $f$, $\omega=2\pi f$ | frequency, angular frequency ($f_0$ at resonance) | Hz, rad/s |
| $\lambda=c/f$, $k_0=\omega/c$ | free-space wavelength, wavenumber | m, rad/m |
| $a$, $b$ | radius of primary, secondary coil | m |
| $N_1$, $N_2$ | number of turns | – |
| $d$ | spacing between coil planes along the common axis | m |
| $z$ | axial position measured from the primary plane | m |
| $I_1$, $I_2$ | coil currents (phasor peaks), both into the dotted terminals | A |
| $\Phi_{21}$ | flux linkage of coil 2 due to $I_1$ ($N_2\times$ flux) | Wb (= V·s) |
| $L_1$, $L_2$, $M$ | self- and mutual inductance | H |
| $k$ | coupling coefficient $M/\sqrt{L_1L_2}$ | – |
| $V_2$ | EMF induced in the open secondary | V |
| $A$ | coil area $\pi a^2$ | m² |
| $R_{\rm rad}$ | radiation resistance | Ω |

Note: $k$ (coupling) and $k_0$ (wavenumber) are different; the brief writes the wavenumber product as "$ka$", which I write $k_0a$ below.

## 1. Ampère's law and the quasi-static approximation

$$\nabla\times\mathbf H = \mathbf J + \frac{\partial\mathbf D}{\partial t} \quad\xrightarrow{\text{phasors}}\quad \nabla\times\mathbf H = \mathbf J + j\omega\varepsilon_0\mathbf E$$

Units: A/m per m = A/m² on both sides.

Two separate checks show the displacement term is negligible:

- **Size against wavelength.** $\lambda = c/f_0 = 3\times10^8/5\times10^5 = 600$ m. For $a = 5$ cm, $k_0a = \omega a/c = 2\pi(5\times10^5)(0.05)/(3\times10^8) = 5.2\times10^{-4}$. Retardation (the time for the field to cross the coil) changes the near field by terms of relative order $(k_0a)^2 \approx 2.7\times10^{-7}$. The field "sees" a current that is the same everywhere at each instant.
- **Inside the copper.** $|j\omega\varepsilon_0\mathbf E|/|\sigma\mathbf E| = \omega\varepsilon_0/\sigma = 2\pi(5\times10^5)(8.854\times10^{-12})/(5.8\times10^7) = 4.8\times10^{-13}$.

So $\nabla\times\mathbf H \approx \mathbf J$: the magnetostatic laws (Biot–Savart, Neumann) hold at each instant, with $I$ replaced by $i(t)$. Assumptions: air core, no nearby metal (that is A-T2), coil much smaller than $\lambda$.

## 2. Biot–Savart: field on the axis of an N-turn loop

$$\mathbf B(\mathbf r) = \frac{\mu_0 I}{4\pi}\oint \frac{d\mathbf l\times\hat{\mathbf R}}{R^2}$$

where $\mathbf R$ points from the current element $d\mathbf l$ to the field point and $R = |\mathbf R|$.

Take one loop of radius $a$ in the plane $z=0$ and a point on the axis at height $z$.

1. Every element is the same distance away: $R = \sqrt{a^2+z^2}$.
2. $d\mathbf l$ is tangential and $\hat{\mathbf R}$ lies in the plane containing the axis, so $d\mathbf l\perp\hat{\mathbf R}$ and $|d\mathbf l\times\hat{\mathbf R}| = dl$. Each element gives $|d\mathbf B| = \mu_0 I\,dl/(4\pi R^2)$.
3. $d\mathbf B$ is perpendicular to $\mathbf R$. Split it into an axial part $dB_z = |d\mathbf B|\,(a/R)$ and a radial part $|d\mathbf B|\,(z/R)$.
4. **Radial parts cancel:** the element diametrically opposite gives an equal radial part in the opposite direction.
5. **Axial parts add:** $\oint dl = 2\pi a$, so

$$B_z = \frac{\mu_0 I}{4\pi R^2}\cdot\frac{a}{R}\cdot 2\pi a = \frac{\mu_0 I a^2}{2(a^2+z^2)^{3/2}}.$$

For $N$ closely wound turns (all at about the same radius and plane) the contributions add:

$$\boxed{B_z(z) = \frac{\mu_0 N I a^2}{2\,(a^2+z^2)^{3/2}}}$$

Units: (H/m)(A)(m²)/m³ = H·A/m² = Wb/m² = T. ✓
Checks: at the centre, $B_z(0) = \mu_0NI/(2a)$ (textbook loop result). Far away, $B_z \to \mu_0NIa^2/(2z^3)$.

## 3. Flux linkage, mutual inductance and reciprocity

The flux linkage of the secondary due to the primary current is

$$\Phi_{21} = N_2\int_{S_2}\mathbf B_1\cdot d\mathbf A, \qquad M_{21} = \frac{\Phi_{21}}{I_1}\quad[\text{Wb/A} = \text{H}].$$

Because $\mathbf B$ is linear in $I_1$ (quasi-static), $M$ does not depend on the current.

**Neumann form.** Write $\mathbf B_1 = \nabla\times\mathbf A_1$ with $\mathbf A_1 = \dfrac{\mu_0 I_1}{4\pi}\oint_1\dfrac{d\mathbf l_1}{r}$. Stokes turns the surface integral into a line integral round coil 2:

$$\int_{S_2}\mathbf B_1\cdot d\mathbf A = \oint_2\mathbf A_1\cdot d\mathbf l_2 = \frac{\mu_0 I_1}{4\pi}\oint_2\oint_1\frac{d\mathbf l_1\cdot d\mathbf l_2}{r}$$

so, for single-filament loops (an $N$-turn coil is the sum over all turn pairs),

$$\boxed{M = \frac{\mu_0}{4\pi}\oint_1\oint_2\frac{d\mathbf l_1\cdot d\mathbf l_2}{r}}$$

where $r$ is the distance between the two elements (m). Units: (H/m)(m·m)/m = H. ✓

**Reciprocity.** Swapping the labels 1 and 2 leaves $d\mathbf l_1\cdot d\mathbf l_2$ and $r$ unchanged, so $M_{12} = M_{21} = M$: the flux in coil 2 per amp in coil 1 equals the flux in coil 1 per amp in coil 2, even when the coils differ. The integrand contains only positions and directions of the wire, so **$M$ is pure geometry**.

For coaxial filament loops the double integral has the closed form (equation reference):

$$M = \mu_0\sqrt{ab}\left[\left(\frac{2}{\kappa}-\kappa\right)K(\kappa) - \frac{2}{\kappa}E(\kappa)\right], \qquad \kappa^2 = \frac{4ab}{(a+b)^2+d^2},$$

with $K$, $E$ the complete elliptic integrals of the first and second kind (multiply by $N_1N_2$ for bundled turns). This is what A-C1 and A-S1 evaluate.

## 4. Faraday's law on the secondary

$$\oint_{C_2}\mathbf E\cdot d\mathbf l = -\frac{d}{dt}\int_{S_2}\mathbf B\cdot d\mathbf A$$

For an open secondary ($i_2 = 0$) the only flux it links is from coil 1, $\Phi_{21} = M i_1$, so the EMF is

$$v_2 = -\frac{d\Phi_{21}}{dt} = -M\frac{di_1}{dt}.$$

With $i_1 = \mathrm{Re}\{I_1e^{j\omega t}\}$, $d/dt\to j\omega$:

$$\boxed{V_2 = -j\omega M I_1, \qquad |V_2| = \omega M|I_1|}$$

Units: (rad/s)(H)(A) = V. ✓ The EMF lags $I_1$ by 90°.

**Sign check against the circuit (Section 3 convention).** In the secondary KVL $j\omega M I_1 + Z_2I_2 = 0$, the term $+j\omega MI_1$ is the voltage *drop* across the coupling, i.e. minus the EMF. Solving gives $I_2 = -j\omega MI_1/Z_2 = V_2/Z_2$: the EMF above drives the secondary current, and at $f_0$ this is $I_2 = -j\omega_0MI_1/(R_2+R_L)$, matching the equation reference. Only $|V_2|$ and $M^2$ appear in power and efficiency, so the sign of $M$ does not matter.

## 5. Coupling coefficient, and the large-distance limit

$$k = \frac{M}{\sqrt{L_1L_2}}, \qquad 0\le k\le 1 \ \ [\text{H/H, dimensionless}].$$

$k$ is the fraction of the field that is shared. $L_1$ and $L_2$ (Neumann with both elements on the same coil) and $M$ are all geometric integrals of the wire paths, so **$k$ depends only on coil sizes, turns layout, spacing and alignment**. Frequency, the capacitors and the load do not appear (they enter later through $Q$ and $Z_2$). Nearby metal or ferrite changes $k$ because it changes the field shape (A-T2).

**Dipole limit ($d \gg a$, and $b$ small enough that $B$ is uniform over coil 2).** From Section 2, at $z = d \gg a$, $B_z \approx \mu_0N_1I_1a^2/(2d^3)$, the field of a magnetic dipole $m = N_1I_1\pi a^2$. Over the secondary area $\pi b^2$:

$$\Phi_{21}\approx N_2\,\pi b^2\,\frac{\mu_0N_1I_1a^2}{2d^3} \;\Rightarrow\; \boxed{M\approx\frac{\mu_0\pi N_1N_2a^2b^2}{2d^3}}$$

Units: (H/m)(m⁴)/m³ = H. ✓ Since $L_1$, $L_2$ do not depend on $d$, $k(d)\propto 1/d^3$: doubling the distance cuts $k$ by 8, and the efficiency figure $k^2Q_1Q_2$ by 64. That is why the link is short-range.

**Where the dipole limit holds (my check, flagged).** For filament loops with $a = b = 5$ cm, $N_1 = N_2 = 10$ (illustrative, not our final coils):

| $d$ (cm) | $M$ exact (µH) | $M$ dipole (µH) | dipole / exact |
|---|---|---|---|
| 1 | 10.77 | 1234 | 114 |
| 2 | 6.75 | 154 | 23 |
| 5 | 2.47 | 9.87 | 4.0 |
| 10 | 0.709 | 1.23 | 1.74 |
| 20 | 0.130 | 0.154 | 1.19 |

Example: $d = 10$ cm, $M_{\rm dip} = (4\pi\times10^{-7})\pi(100)(0.05)^4/(2\cdot0.1^3) = 1.23\ \mu$H. The dipole formula is only within ~20 % once $d \gtrsim 4a$. **Over our test range (1 to 10 cm, $d \le 2a$) $M$ falls much more slowly than $1/d^3$, so use the elliptic (or numerical Neumann) formula for every plotted point.** The brief's line "M and k drop like 1/d³ once d is larger than the coil radius" is too optimistic; it should say "for d several times the coil radius". This is also a good check for A-S1: the log-log slope should approach −3 only at the far end.

## 6. Radiation is negligible

Small-loop radiation resistance:

$$R_{\rm rad}\approx 31171\left(\frac{NA}{\lambda^2}\right)^2\ \Omega$$

With $N = 10$, $A = \pi(0.05)^2 = 7.85\times10^{-3}$ m², $\lambda = 600$ m: $NA/\lambda^2 = 0.0785/3.6\times10^5 = 2.18\times10^{-7}$, so $R_{\rm rad} = 31171\times(2.18\times10^{-7})^2 = 1.5\times10^{-9}\ \Omega$.

Against a coil resistance of about 0.1 to 1 Ω, radiation takes about $10^{-9}$ of the power. The energy stays in the reactive near field and is either dissipated in $R_1$, $R_2$, $R_L$ or returned to the source, which is exactly the assumption behind the circuit model.

## Poster equations chosen (3)

1. **Biot–Savart, on-axis field** $B_z = \dfrac{\mu_0NIa^2}{2(a^2+z^2)^{3/2}}$: current in the primary makes a field that falls with distance along the axis.
2. **Neumann mutual inductance** $M = \dfrac{\mu_0}{4\pi}\oint\oint\dfrac{d\mathbf l_1\cdot d\mathbf l_2}{r}$, with $k = M/\sqrt{L_1L_2}$: how much of that field links the secondary, set by geometry alone and reciprocal.
3. **Faraday's law** $V_2 = -j\omega MI_1$: the changing shared flux induces the voltage that drives the secondary.

(Ampère quasi-static and the $1/d^3$ dipole limit go in as one-line supporting statements.)

## Oral questions

**Q1. Why can you use magnetostatic formulas at 500 kHz?**
Because the coil is about $10^{-4}$ of a wavelength ($k_0a\approx5\times10^{-4}$). The displacement current and retardation change the near field by order $(k_0a)^2\approx10^{-7}$, so at each instant the field is the static field of the instantaneous current.

**Q2. Why is $M_{12} = M_{21}$ even if the coils are different sizes?**
The Neumann integral contains only $d\mathbf l_1\cdot d\mathbf l_2$ and the distance $r$, both symmetric under swapping the coils. So the flux in 2 per amp in 1 equals the flux in 1 per amp in 2.

**Q3. Does adding the resonant capacitors increase $k$?**
No. $k$ is geometry only. Resonance cancels the reactances so the small induced EMF $\omega MI_1$ drives a large current, and high $Q$ makes $k^2Q_1Q_2$ large; that raises efficiency at a given $k$ but does not change $k$.
