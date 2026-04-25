# Diode Model Theory

CurveCraft M1 uses a compact diode model for diode I-V data. This document describes the equations implemented in `curvecraft.models.diode`.

## Thermal Voltage

Thermal voltage is:

```text
Vt = kT / q
```

where:

- `k` is Boltzmann's constant in joules per kelvin
- `T` is temperature in kelvin
- `q` is the elementary charge in coulombs

At about 300 K, `Vt` is about 25.85 mV.

## Shockley Equation

For an ideal diode without series resistance:

```text
I = Is * (exp(V / (n * Vt)) - 1)
```

where:

- `I` is diode current in amps
- `V` is applied diode voltage in volts
- `Is` is saturation current in amps
- `n` is the ideality factor
- `Vt` is thermal voltage in volts

At reverse bias, this equation approaches `-Is`. At forward bias, current rises exponentially.

## Ideality Factor

The ideality factor `n` changes the slope of the exponential current. A value near 1 represents diffusion-dominated behavior. Values closer to 2 can appear when recombination or other nonideal effects dominate.

M1 treats `n` as a fitted compact-model parameter. It does not explain every physical mechanism inside a real diode.

## Saturation Current

`Is` sets the approximate reverse-bias current limit in the simple Shockley model and strongly affects the forward current scale.

Real reverse leakage can include effects that this model does not capture, so M1 fitting should not silently treat arbitrary reverse-bias data as valid Shockley leakage.

## Series Resistance

With series resistance `Rs`, the model is implicit:

```text
I = Is * (exp((V - I * Rs) / (n * Vt)) - 1)
```

The `I * Rs` term reduces the voltage actually across the diode junction. This matters most at high forward current, where even a small resistance can cause a meaningful voltage drop.

CurveCraft solves this implicit equation numerically for M1. The implementation is intended to be explainable and robust for small engineering datasets, not a replacement for a full production compact-model simulator.

## M1 Limitations

This model does not include capacitance, breakdown, self-heating, temperature-dependent parameter extraction, or high-injection effects. M1 includes ngspice netlist generation and validation only for checking implementation consistency of this compact model.
