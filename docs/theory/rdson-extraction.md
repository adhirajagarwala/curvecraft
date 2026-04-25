# MOSFET Rds_on Extraction

CurveCraft M3 estimates MOSFET `Rds_on` from the low-`Vds` part of Id-Vds
output curves. For one fixed `Vgs` curve, the local low-voltage behavior is
approximated as:

```text
Id ~= conductance * Vds + intercept
Rds_on = 1 / conductance
```

The extraction fits a straight line over a selected low-`Vds` region. The
returned intercept and RMSE are diagnostic values; a large intercept or large
residual can indicate that the chosen region is not behaving like a simple
linear on-resistance region.

## Why Vgs Matters

`Rds_on` is not a single context-free number. For a MOSFET output curve, the
low-`Vds` slope depends strongly on the applied gate-source voltage. A curve at
`Vgs = 2 V` can produce a very different extracted resistance than a curve at
`Vgs = 10 V`.

Datasheet `Rds_on` values are normally specified at stated conditions such as
gate voltage, drain current, pulse width, and temperature. CurveCraft's M3
helper only extracts the inverse low-`Vds` slope from the CSV data it is given.

## Limitations

This is not package-level datasheet `Rds_on` unless the input data actually
represents that measurement condition. The helper does not model package
resistance, self-heating, temperature dependence, p-channel devices, BSIM
behavior, switching loss, capacitance, gate charge, or thermal effects.
