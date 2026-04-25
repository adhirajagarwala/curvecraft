# Diode I-V CSV Schema

CurveCraft M1 starts from a plain CSV file. Each row is one voltage/current measurement for the diode.

## Required Columns

| Column | Unit | Meaning |
| --- | --- | --- |
| `voltage_v` | volts (V) | Diode terminal voltage. |
| `current_a` | amps (A) | Measured diode current. |

Both columns are required. Values must be numeric. Blank values and NaNs are rejected.

## Loader Behavior

The loader does a few boring but important things:

- reads the file with pandas
- keeps only `voltage_v` and `current_a`
- converts both columns to numeric values
- rejects empty files
- rejects missing, NaN, or nonnumeric values
- sorts rows by `voltage_v`
- preserves the measured sign of `current_a`

CurveCraft does not take `abs(current_a)`. Reverse-bias current and instrument sign conventions are part of the data, so the sign has to survive loading.

## M1 Limitations

The CSV loader is intentionally small. It does not parse metadata, digitize datasheet images, define MOSFET schemas, fit models, generate SPICE, or validate simulations.

Real data must include provenance in `data/README.md`. Synthetic data must be clearly labeled as synthetic.
