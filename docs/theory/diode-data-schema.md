# Diode I-V CSV Data Schema

CurveCraft M1 accepts diode I-V curve data as CSV files.

## Required Columns

| Column | Unit | Meaning |
| --- | --- | --- |
| `voltage_v` | volts (V) | Diode terminal voltage. |
| `current_a` | amps (A) | Measured diode current. |

Both columns are required. Values must be numeric and must not be blank or NaN.

## Loader Behavior

The CSV loader:

- reads the file with pandas
- keeps only `voltage_v` and `current_a`
- converts both columns to numeric values
- rejects empty files
- rejects missing, NaN, or nonnumeric values
- sorts rows by `voltage_v`
- preserves the measured sign of `current_a`

Current sign is not changed because reverse-bias measurements and instrument conventions matter.

## M1 Limitations

M1 CSV loading does not include metadata parsing, datasheet image digitization, MOSFET schemas, fitting, SPICE generation, or validation.

Real data must include provenance in `data/README.md`. Synthetic data must be clearly labeled as synthetic.
