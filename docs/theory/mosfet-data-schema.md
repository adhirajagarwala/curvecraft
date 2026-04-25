# MOSFET Id-Vgs CSV Schema

CurveCraft M2 starts MOSFET support with a plain CSV schema for n-channel
enhancement MOSFET transfer curves. Each row is one drain-current measurement
at a gate-source voltage.

## Required Columns

| Column | Unit | Meaning |
| --- | --- | --- |
| `vgs_v` | volts (V) | Gate-source voltage. |
| `id_a` | amps (A) | Measured drain current. |

Both columns are required. Values must be numeric. Blank values and NaNs are
rejected.

## Optional Columns

| Column | Unit | Meaning |
| --- | --- | --- |
| `vds_v` | volts (V) | Drain-source voltage for the transfer-curve measurement. |

For M2, `vds_v` is optional. If it is absent, a caller or future metadata layer
may provide the fixed drain-source voltage later. CurveCraft does not add YAML
metadata in this issue.

## Loader Behavior

The MOSFET Id-Vgs CSV loader:

- reads the file with pandas
- keeps `vgs_v`, `id_a`, and optional `vds_v`
- converts kept columns to numeric values
- rejects empty files
- rejects missing, NaN, or nonnumeric values
- sorts rows by `vgs_v`
- preserves the measured sign of `id_a`

CurveCraft does not take `abs(id_a)`. Current sign can reflect instrument setup
or measurement convention, so the loader keeps it exactly as numeric input data.

## M2 Scope

This page defines the CSV data schema for n-channel enhancement MOSFET Id-Vgs
transfer curves only. Other completed M2 modules handle the Level-1 model
equations, threshold extraction helpers, nonlinear fitting, measured-vs-fit
plots, ngspice validation, and Markdown reporting.

M2 does not define an Id-Vds output-curve schema. It also does not include
Rds_on extraction, p-channel MOSFET support, BSIM, capacitance, gate charge,
switching loss, thermal modeling, or datasheet digitization.
