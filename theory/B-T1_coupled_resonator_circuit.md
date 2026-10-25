# B-T1: Coupled-Resonator Circuit Theory

## 1. Objective

This document develops the circuit model for a series-series
resonant inductive wireless power transfer system.

The model will be implemented in `sim/circuit.py` and used to
calculate primary and secondary currents, input power, load
power, and transfer efficiency.

## 2. Circuit topology and notation

The system consists of two magnetically coupled resonators.

The primary resonator contains an AC voltage source, primary
resistance R1, inductance L1, and series capacitor C1.

The secondary resonator contains secondary resistance R2,
inductance L2, series capacitor C2, and load resistance RL.

The two coils are coupled through mutual inductance M.

Circuit (series-series). The dot (•) marks the TOP terminal of each coil, and both mesh
currents are drawn so that they ENTER that dotted terminal:

```
       Rs         R1        C1                            C2        R2
   +--/\/\/----/\/\/------||------•+                +•------||------/\/\/----+
   |  I1 ------------------------->|                |<------------------- I2 |
   |                               ) L1          L2 (                        /
  (~) Vs                           )    <-- M -->   (                        \  RL
   |                               )                (                        /
   +-------------------------------+                +------------------------+

  I1 flows clockwise:      up through Vs, right along the top, DOWN through L1 (enters its dot).
  I2 flows anticlockwise:  left along the top, DOWN through L2 (enters its dot), up through RL.
```

Why this gives the + signs used in Section 4. With both currents entering dotted terminals,
the flux of each current adds to the flux of the other inside the coils, so the voltage induced
in a coil by the other coil's current has the SAME polarity as its own L di/dt drop:

    primary loop (KVL, going round with I1):   Vs = (Rs + Z1) I1 + j*omega*M*I2
    secondary loop (KVL, going round with I2):  0 =  Z2 I2       + j*omega*M*I1

These are exactly the mesh equations of Section 4 and of `sim/circuit.py` (Zm = +j*omega*M).
If one coil is wound the other way round (its dot moves to the bottom terminal), M is replaced by -M:
I2 changes sign (it then LEADS I1 by 90° instead of lagging), but |I2|, Pin, PL and eta are unchanged
(Section 10). The 90° lag stated in Section 6 is for the dot convention drawn here.

Rs is the source (generator) resistance, 0 for an ideal voltage source. Both mesh
currents are drawn into the dotted terminals.

The angular operating frequency is

    omega = 2*pi*f

Both resonators are tuned to the same resonant frequency

    omega0 = 1/sqrt(L1*C1) = 1/sqrt(L2*C2),    f0 = omega0/(2*pi)

For the design, f0 = 500 kHz.

Symbols:

- Vs: source voltage, peak phasor [V]
- Rs: source (generator) resistance, 0 for an ideal source [ohm]
- I1, I2: primary and secondary mesh currents, peak phasors [A]
- L1, L2: self-inductances [H]
- M: mutual inductance [H]
- k: coupling coefficient M/sqrt(L1*L2) [-]
- R1, R2: total series resistance of each resonator (wire, skin, proximity, capacitor ESR) [ohm]
- C1, C2: series tuning capacitances [F]
- RL: load resistance, in series with the secondary [ohm]
- Z1, Z2: loop impedances of the primary and secondary (Section 3) [ohm]
- Zr: impedance reflected into the primary, omega^2*M^2/Z2 [ohm]
- Zin: input impedance at the primary resonator terminals, Z1 + Zr [ohm]
- f, omega: operating frequency [Hz] and angular frequency 2*pi*f [rad/s]
- f0, omega0: resonant frequency [Hz] and angular resonant frequency [rad/s]
- Q1, Q2: unloaded quality factors omega0*L1/R1, omega0*L2/R2 [-]
- Pin, PL: average power into the primary resonator terminals and into the load [W]
- eta_link: AC link efficiency PL/Pin [-]

The phasor convention uses peak-value phasors.

## 3. Resonator impedances

The impedance of an inductor is

    ZL = j*omega*L

The impedance of a capacitor is

    ZC = 1/(j*omega*C)

Therefore, the primary impedance is

    Z1 = R1 + j*omega*L1 + 1/(j*omega*C1)

The secondary impedance, including the load, is

    Z2 = R2 + RL + j*omega*L2 + 1/(j*omega*C2)

The load resistance is included in Z2 because it is connected
in series with the secondary resonator.

## 4. Coupled mesh equations

Using the selected dot convention, with both mesh currents
referenced into dotted terminals, the primary equation is

    Z1*I1 + j*omega*M*I2 = Vs

Here Rs = 0. With a source resistance, Z1 is replaced by Z1 + Rs, as in
the KVL of Section 2. Zin = Z1 + Zr below is the impedance at the primary
resonator terminals, so it excludes Rs.

The secondary equation is

    j*omega*M*I1 + Z2*I2 = 0

In matrix form,

    [ Z1       j*omega*M ] [ I1 ]   [ Vs ]
    [ j*omega*M      Z2  ] [ I2 ] = [  0 ]

Equivalently,

    A = [[Z1, j*omega*M],
         [j*omega*M, Z2]]

    A @ [I1, I2] = [Vs, 0]

The numerical implementation evaluates the coupled equations using the closed-form Cramer's rule solution at each requested operating frequency. The result is verified against numpy.linalg.solve in a unit test.

## 5. Closed-form current expressions

From the secondary equation,

    I2 = -j*omega*M*I1/Z2

Substituting into the primary equation gives

    I1 = Vs/(Z1 + omega^2*M^2/Z2)

The secondary current is then

    I2 = -j*omega*M*I1/Z2

The reflected impedance is

    Zr = omega^2*M^2/Z2

The input impedance seen by the source is

    Zin = Z1 + Zr

The reflected impedance represents the effect of the
secondary resonator and load on the primary circuit.

## 6. Expressions at resonance

When both resonators are tuned to omega0,

    omega0*L1 = 1/(omega0*C1)
    omega0*L2 = 1/(omega0*C2)

The inductive and capacitive reactances cancel, giving

    Z1 = R1
    Z2 = R2 + RL

Therefore,

    Zin = R1 + omega0^2*M^2/(R2 + RL)

    I1 = Vs/(R1 + omega0^2*M^2/(R2 + RL))

    I2 = -j*omega0*M*I1/(R2 + RL)

Under the stated phasor and dot conventions, the secondary
current lags the primary current by 90 degrees at resonance.

The sign convention for M must be used consistently in the
coupled equations. The physical power-transfer results do
not depend on the arbitrary choice of mutual-inductance sign.

## 7. Input power, load power, and efficiency

Using peak-value phasors, the average real power entering
the primary resonator is

    Pin = 0.5*real(Vs*conj(I1))          (Rs = 0)
    Pin = 0.5*real((Vs - Rs*I1)*conj(I1)) (general: voltage at the resonator terminals)

The power dissipated in the load is

    PL = 0.5*abs(I2)^2*RL

The AC link efficiency is

    eta_link = PL/Pin

This is the efficiency from the primary resonator terminals to the load
resistor, not the DC-to-DC system efficiency (which would also include the
driver and rectifier losses). In `sim/circuit.py` it is the output `eta`.

These equations use peak phasors. With RMS phasors, the
factor of 0.5 is omitted from both power expressions.

The solver must handle the case Pin = 0 without producing
an invalid division result.

If a source resistance Rs is included, Pin is defined at
the primary resonator terminals, excluding source-resistor
losses.

## 8. Numerical implementation requirements

The function will be implemented in `sim/circuit.py` with
the interface

    solve(f, M, L1, L2, C1, C2, R1, R2, RL, Vs, Rs=0)

Inputs:

- f: operating frequency in Hz; scalar or NumPy array
- M: mutual inductance in H
- L1, L2: self-inductances in H
- C1, C2: capacitances in F
- R1, R2: resonator series resistances in ohms
- RL: load resistance in ohms
- Vs: peak source-voltage phasor in V
- Rs: source resistance in ohms, default zero

Outputs:

- I1: primary current phasor
- I2: secondary current phasor
- Pin: average real power entering the primary resonator
- PL: average power delivered to the load
- eta: power-transfer efficiency

For Rs > 0, the matrix includes Rs in the primary diagonal
term. The reported Pin must exclude the power dissipated
in Rs.

The implementation uses the closed-form Cramer's rule solution rather than explicitly calculating the matrix inverse. A unit test compares its results against numpy.linalg.solve.

## 9. Validation requirements

The implementation will be checked against the following:

1. The numerical solution agrees with the closed-form
   expressions at resonance.
2. At resonance, the phase of I2/I1 is -90 degrees under
   the chosen convention.
3. Numerical and analytical efficiencies agree to within
   1e-6 for a suitable reference case.
4. Efficiency approaches one as the series resistances
   approach zero, for nonzero coupling and positive load.
5. Efficiency approaches zero when M approaches zero.
6. A frequency sweep reproduces the expected resonance
   splitting for the strongly coupled, low-loss reference case
   with a lightly loaded secondary (RL -> 0, see Section 12).

These checks will be implemented as automated tests in
`sim/tests/test_circuit.py`.

## 10. The sign of M does not matter (shown, not just stated)

Eliminating I2 gives Zin = Z1 + omega^2*M^2/Z2 and I2 = -j*omega*M*I1/Z2.
M appears in Zin only as M^2, so I1, Pin and the input impedance are the same
for +M and -M. In I2 the sign of M only flips the sign of I2:
|I2| is unchanged, so PL = 0.5*|I2|^2*RL and eta = PL/Pin are unchanged.
Physically, reversing the winding direction of one coil reverses the phase of the
induced voltage but not the power it delivers.

## 11. Physical meaning (link to Faraday's law)

The secondary voltage source is the induced EMF v2 = -M di1/dt, i.e.
V2 = -j*omega*M*I1 in phasor form (A-T1). At resonance the secondary loop is purely
resistive (R2 + RL), so I2 = V2/(R2 + RL) = -j*omega0*M*I1/(R2 + RL): the
-j is the 90 degree lag. The reflected resistance omega0^2*M^2/(R2 + RL) is how the
source "feels" the load.

## 12. Reference-case check values (used in tests/test_circuit.py)

L1 = L2 = 15 uH, f0 = 500 kHz, C1 = C2 = 6.755 nF, R1 = R2 = 0.3 ohm, k = 0.1 (M = 1.5 uH):
Q = 157.1, k^2*Q1*Q2 = 246.7, RL,opt = 4.72 ohm, eta_max = 88.05 %, phase(I2/I1) = -90 degrees.
With R1 = R2 = 0.01 ohm and RL = 0.01 ohm (secondary effectively shorted,
RL << omega0*M) the two |I2| peaks are at 476.7 and 527.0 kHz and
k = (fh^2 - fl^2)/(fh^2 + fl^2) = 0.100.

The split-peak formula assumes a lightly loaded secondary. A load resistance
damps the secondary and pulls the peaks together: with RL = 4.72 ohm (the
optimal load of this case) the peaks move to 483.7 and 519.1 kHz and the
formula gives k = 0.071, 30 % low; at RL = 10 ohm there is only one peak.
A k obtained from the peaks of a loaded secondary therefore underestimates k.

## 13. Equations chosen for the poster

1. Coupled mesh equations: Z1*I1 + j*omega*M*I2 = Vs and j*omega*M*I1 + Z2*I2 = 0,
   with Z1 = R1 + j*omega*L1 + 1/(j*omega*C1), Z2 = R2 + RL + j*omega*L2 + 1/(j*omega*C2).
2. Reflected and input impedance: Zr = omega^2*M^2/Z2, Zin = Z1 + Zr
   (at f0: Zin = R1 + omega0^2*M^2/(R2 + RL)).
3. Secondary current at resonance: I2 = -j*omega0*M*I1/(R2 + RL), which lags I1 by 90 degrees.
