# MOSFET Threshold Extraction

CurveCraft M2 includes small helper methods for estimating n-channel MOSFET
threshold voltage from Id-Vgs transfer data. These helpers are intended to
produce transparent initial guesses for later fitting, not definitive device
characterization.

## Constant-Current Method

The constant-current method chooses a target drain current and interpolates the
gate-source voltage where the measured Id-Vgs curve crosses that current:

```text
Vth = Vgs where Id = target_current
```

This mirrors how many datasheets specify threshold voltage: a device is measured
at a stated drain current and drain-source voltage, and the corresponding
gate-source voltage is reported. That value is not a universal turn-on point.
Changing the target current changes the extracted threshold voltage.

## sqrt(Id) Linearization

For the simple saturation-region square-law model with `lambda = 0`:

```text
Id = 0.5 * beta * (Vgs - Vth)^2
```

Taking the square root gives an approximately linear relationship:

```text
sqrt(Id) = sqrt(0.5 * beta) * (Vgs - Vth)
```

CurveCraft fits `sqrt(Id)` versus `Vgs` over positive-current points and uses
the x-intercept as the threshold estimate. The slope can also provide a rough
initial beta guess.

## Why Vth Is Method-Dependent

Threshold voltage is not a single perfectly observable point on a real transfer
curve. It depends on the extraction method, current range, measurement setup,
device geometry, temperature, and model assumptions. Datasheet threshold
voltage is often measured at a specified drain current, so it should not be read
as the voltage where a MOSFET suddenly changes from off to on.

## Limitations

These helpers are for n-channel enhancement MOSFET Id-Vgs transfer curves at
fixed Vds. They do not perform nonlinear fitting, Id-Vds extraction,
subthreshold-slope extraction, p-channel support, BSIM modeling, or datasheet
digitization.
