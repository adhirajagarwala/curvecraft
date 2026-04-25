# MOSFET Id-Vds CSV Schema

CurveCraft M3 uses a plain long/tidy CSV schema for n-channel enhancement
MOSFET Id-Vds output-curve data. Each row is one drain-current point measured
at a specific gate-source voltage and drain-source voltage.

## Required Columns

| Column | Unit | Meaning |
| --- | --- | --- |
| `vgs_v` | volts (V) | Gate-source voltage for one output curve. |
| `vds_v` | volts (V) | Drain-source voltage sweep point. |
| `id_a` | amps (A) | Measured drain current. |

All three columns are required. Values must be numeric. Blank values and NaNs
are rejected.

## Long/Tidy Curve Families

Multiple Id-Vds output curves are represented by repeated `vgs_v` values:

```text
vgs_v,vds_v,id_a
2.0,0.0,0.0
2.0,0.5,3.75e-4
3.0,0.0,0.0
3.0,0.5,8.75e-4
```

This keeps every measured point in one table while still allowing CurveCraft to
group rows into separate output curves by `vgs_v`.

## Loader Behavior

The MOSFET Id-Vds CSV loader:

- reads the file with pandas
- keeps only `vgs_v`, `vds_v`, and `id_a`
- converts kept columns to numeric values
- rejects empty files
- rejects missing, NaN, or nonnumeric values
- sorts rows by `vgs_v`, then `vds_v`
- preserves the measured sign of `id_a`

CurveCraft does not take `abs(id_a)`. Current sign can reflect instrument setup
or measurement convention, so the loader keeps it exactly as numeric input
data.

## M3 Scope

This schema supports the completed M3 educational Id-Vds/Rds_on workflow:
loading output curves, fitting the simple Level-1 model, extracting low-Vds
Rds_on, plotting, generating ngspice validation artifacts, and reporting.

p-channel MOSFET support, BSIM extraction, capacitance, gate charge, switching
loss, thermal effects, and datasheet image digitization are out of scope.
