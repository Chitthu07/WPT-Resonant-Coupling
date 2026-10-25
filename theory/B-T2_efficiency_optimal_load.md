# B-T2: Resonant Efficiency and Optimal Load

## 0. Assumptions

1. Series-series topology: C1 in series with L1, C2 and RL in series with L2.
2. Both resonators are tuned to the same frequency and driven at it: $\omega_0 L_i = 1/(\omega_0 C_i)$.
3. $R_1$, $R_2$ are the TOTAL series resistance of each resonator (wire DC + skin + proximity,
   capacitor ESR, joints). $Q_i=\omega_0L_i/R_i$ is the UNLOADED Q; the load $R_L$ is kept separate.
4. Linear, sinusoidal steady state with peak phasors; $P_{in}$ is measured at the primary resonator
   terminals, so any source resistance $R_s$ does not enter $\eta$.
5. The load that maximises efficiency is not the load that maximises power (Section 5).

## 1. Efficiency at Resonance

For two series-series resonators operating at their common resonant
frequency $\omega_0$, the reactive terms cancel.

The coupled equations become

$$
V_s = R_1 I_1 + j\omega_0 M I_2
$$

$$
0 = j\omega_0 M I_1 + (R_2+R_L)I_2
$$

From the secondary equation,

$$
I_2 = -\frac{j\omega_0 M}{R_2+R_L}I_1
$$

Using peak-value phasors, the input power at the primary resonator
terminals is

$$
P_{\mathrm{in}}
=
\frac12
\left(
R_1+\frac{\omega_0^2M^2}{R_2+R_L}
\right)|I_1|^2
$$

This includes primary resistance losses and the real power transferred
through the reflected impedance.

The load power is

$$
P_L=\frac12R_L|I_2|^2
$$

Therefore, the efficiency is

$$
\boxed{
\eta =
\frac{\omega_0^2M^2R_L}
{(R_2+R_L)
\left[R_1(R_2+R_L)+\omega_0^2M^2\right]}
}
$$

Equivalently, efficiency can be expressed as two factors:

$$
\eta =
\frac{\omega_0^2M^2}
{R_1(R_2+R_L)+\omega_0^2M^2}
\frac{R_L}{R_2+R_L}
$$

The first factor describes power transferred into the secondary network.
The second is the fraction of secondary-network dissipation delivered
to the load.

## 2. Dimensionless Form

Define the quality factors

$$
Q_1=\frac{\omega_0L_1}{R_1},
\qquad
Q_2=\frac{\omega_0L_2}{R_2}
$$

and the coupling coefficient

$$
k=\frac{M}{\sqrt{L_1L_2}}
$$

Introduce the dimensionless variables

$$
x=\frac{\omega_0^2M^2}{R_1R_2}=k^2Q_1Q_2
$$

$$
r=\frac{R_L}{R_2}
$$

Both are dimensionless ($x$: Ω²/Ω², $r$: Ω/Ω).

Divide the numerator and denominator of the boxed $\eta$ by $R_1R_2^{\,2}$ and use
$\omega_0^2M^2=xR_1R_2$ and $R_L=rR_2$:

$$
\eta=\frac{xR_1R_2\cdot rR_2}{R_2(1+r)\left[R_1R_2(1+r)+xR_1R_2\right]}
$$

Cancelling $R_1R_2^{\,2}$ gives

$$
\boxed{
\eta(x,r)=\frac{xr}{(1+r)(1+r+x)}
}
$$

This expression shows how the load resistance affects efficiency.

## 3. Load for Maximum Efficiency

For fixed coupling and resonator parameters,

$$
\eta(r)=\frac{xr}{(1+r)(1+r+x)}
$$

Write $\eta = x\,r/D(r)$ with $D(r)=(1+r)(1+r+x)$. By the quotient rule,

$$
\frac{d\eta}{dr}=x\,\frac{D(r)-r\,D'(r)}{D(r)^2},
\qquad D'(r)=(1+r+x)+(1+r)=2+2r+x .
$$

The numerator is

$$
D-rD'=(1+r)(1+r+x)-r(2+2r+x)
=(1+2r+r^2+x+rx)-(2r+2r^2+rx)
=1+x-r^2 .
$$

Setting $d\eta/dr=0$ gives

$$
1+x-r^2=0
$$

($d\eta/dr>0$ for smaller $r$ and $<0$ for larger $r$, so this is a maximum.)

Therefore,

$$
\boxed{r_{\mathrm{opt}}=\sqrt{1+x}}
$$

Since $r=R_L/R_2$,

$$
\boxed{R_{L,\mathrm{opt}}=R_2\sqrt{1+x}}
$$

Substituting this result into the efficiency expression gives

$$
\boxed{
\eta_{\max}=\frac{x}{(1+\sqrt{1+x})^2}
}
$$

Substituting: $1+r_{opt}=1+\sqrt{1+x}$ and $1+r_{opt}+x=\sqrt{1+x}\,(1+\sqrt{1+x})$, so
$\eta_{max}=x\sqrt{1+x}/[\sqrt{1+x}\,(1+\sqrt{1+x})^2]=x/(1+\sqrt{1+x})^2$.

Sanity table:

| $x=k^2Q_1Q_2$ | 0.1 | 1 | 10 | 100 | 1000 |
|---|---:|---:|---:|---:|---:|
| $\eta_{max}$ | 2.4 % | 17.2 % | 53.7 % | 81.9 % | 93.9 % |

Reference test case ($L=15$ µH, $f_0=500$ kHz, $R=0.3$ Ω, $k=0.1$): $x=246.7$,
$R_{L,opt}=4.72$ Ω, $\eta_{max}=88.05$ %.

## 4. Limiting Cases

For weak coupling, $x\ll1$,

$$
\boxed{\eta_{\max}\approx\frac{x}{4}}
$$

For strong coupling, $x\gg1$,

$$
\boxed{\eta_{\max}\approx1-\frac{2}{\sqrt{x}}}
$$

Thus, efficiency improves as the dimensionless coupling parameter
$x=k^2Q_1Q_2$ increases.

Range of validity (exact values from the sanity table in Section 3):

* $x/4$ is already 5 % high at $x=0.1$ (2.50 % vs 2.38 %) and is not useful above $x\approx0.1$.
* $1-2/\sqrt{x}$ is useless below $x\approx10$ (36.8 % vs 53.7 % at $x=10$), 1.9 points low at
  $x=100$ (80.0 % vs 81.9 %) and 0.2 points low at $x=1000$ (93.68 % vs 93.87 %).

For our coils ($R=0.455$ Ω, the C-T2 nominal value, $Q=118.3$) $x\approx3680$ at 1 cm, 173 at 5 cm and 12.5 at
10 cm, so only the strong-coupling limit is relevant, and up to about 5 cm it is within about one point
of the exact $\eta_{max}$ (84.8 % vs 85.9 % at 5 cm, 43.4 % vs 57.2 % at 10 cm). Use the exact
expression for numbers.

## 5. Maximum Efficiency Versus Maximum Power

The load for maximum efficiency is not generally the load for maximum
received power.

For a fixed source voltage $V_s$ with source resistance $R_s$ ($R_s=0$ for an ideal source), at
resonance $P_L=\tfrac12 V_s^2\,\omega_0^2M^2R_L/[(R_1+R_s)(R_2+R_L)+\omega_0^2M^2]^2$, which is maximized at

$$
\boxed{
R_{L,P_{\max}}=R_2+\frac{\omega_0^2M^2}{R_1+R_s}
}
$$

This differs from the maximum-efficiency load,

$$
R_{L,\mathrm{opt}}=R_2\sqrt{1+x}
$$

Note the different roles of $R_s$. Efficiency is defined with $P_{in}$ at the primary resonator
terminals, so $\eta$, $R_{L,opt}$ and $\eta_{max}$ do not depend on $R_s$ ($R_s$ scales $P_{in}$
and $P_L$ by the same factor). The POWER optimum does depend on $R_s$.

Efficiency at the maximum-power load, ideal source ($R_s=0$): put $r=1+x$ into $\eta(x,r)$,

$$
\eta\big|_{P_{max}}=\frac{x(1+x)}{(2+x)(2+2x)}=\frac{x}{2(2+x)} .
$$

This is below 50 % for every finite $x$ and approaches 50 % from below as $x\to\infty$:
taking the most power from the source costs about half of it, the usual maximum-power-transfer
result. With $R_s>0$, use $r=1+x\,R_1/(R_1+R_s)$ in $\eta(x,r)$ instead.

The maximum load power itself, ideal source ($R_s=0$): put $R_L=R_2(1+x)$ into $P_L$,

$$
P_{L,\max}=\frac{V_s^2}{8R_1}\,\frac{x}{1+x} .
$$

For $x\gg1$ this tends to $V_s^2/(8R_1)$, set by $R_1$ alone and not by distance. That is why the
last column of the table below stays near $5^2/(8\cdot0.455)=6.87$ W at every distance, while the
efficiency at that load is below 50 %.

A related result at the efficiency optimum: the input impedance is
$Z_{in}=R_1\left(1+\frac{x}{1+r_{opt}}\right)=R_1\sqrt{1+x}$, so the source sees $R_1\sqrt{1+x}$
while the load is $R_2\sqrt{1+x}$, the same factor on both sides.

Related result used in B-S1: for a fixed $R_L$, $P_L$ as a function of distance is largest where
$\omega_0^2M^2=(R_1+R_s)(R_2+R_L)$, i.e. at critical coupling $k=k_c$
(`circuit.k_crit(..., Rs=Rs)`). For our coils with $R_L=6.0$ Ω:

* $R_s=0$: $k_c=0.0318$ at $d\approx9.7$ cm, which is why `fig_PL_vs_d` rises to a peak near 9.75 cm.
* $R_s=50$ Ω: $k_c=0.335$ at $d\approx1.9$ cm (the peak of the 50 Ω curve).

The same condition read the other way round is $R_L=R_2+\omega_0^2M^2/(R_1+R_s)$: at the
distance where $k=k_c$, the fixed load happens to be the power-optimal load. At every other
distance it is not. The fixed load used in the scripts (6.0 Ω) is the efficiency-optimal load
at 5 cm for $R_1=R_2=0.455$ Ω and was chosen as the team load in C-C1. Over the C-T2 range
$R=0.38$–$0.48$ Ω, $R_{L,opt}(5\text{ cm})=R\sqrt{1+x}$ hardly moves (about 6.0 Ω), because for
$x\gg1$ it tends to $\omega_0M$, which does not depend on $R$. The $k_c$ values above use $k(d)$ from `data/sim_M_k.csv` and
$L=17.13$ µH, $f_0=500$ kHz from `sim/params.py`.

For the current design, simulation with $R_1=R_2=0.455$ Ω (C-T2 nominal) and an ideal 5 V peak
source (`python -m sim.load_sweep`):

| Distance | Load for maximum efficiency | Maximum efficiency | Load for maximum power ($R_s=0$) | Maximum load power ($R_s=0$) |
|---:|---:|---:|---:|---:|
| 1 cm | 27.6 $\Omega$ | 96.8% | 1676 $\Omega$ | 6.87 W |
| 3 cm | 11.7 $\Omega$ | 92.5% | 301 $\Omega$ | 6.86 W |
| 6 cm | 4.47 $\Omega$ | 81.5% | 43.8 $\Omega$ | 6.80 W |

These are simulation values for the nominal R. Rerun `python -m sim.load_sweep`
if $R_1$, $R_2$ or $R_s$ change.

## 6. Poster Equations

The two recommended equations for the poster are

$$
\boxed{\eta(x,r)=\frac{xr}{(1+r)(1+r+x)}}
$$

and

$$
\boxed{\eta_{\max}=\frac{x}{(1+\sqrt{1+x})^2}}
$$

where $x=k^2Q_1Q_2$ and $r=R_L/R_2$.