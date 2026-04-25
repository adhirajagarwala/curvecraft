# Data Directory

CurveCraft data files must be traceable.

Real measurement data must include provenance, including source, device identity when available, measurement conditions, units, and any preprocessing steps.

Synthetic data must be clearly labeled as synthetic in the filename, metadata, README, or adjacent notes. Synthetic data must not be presented as measured data.

## Example Data

- `examples/diode_basic.csv` is synthetic diode I-V data for loader tests and examples. It is not measured device data and must not be used as validation evidence.
- `examples/diode_iv_example.csv` is synthetic diode-like I-V data for M1 CSV loader tests and demos. It is not measured device data and must not be used as validation evidence.

Do not commit private, proprietary, or license-restricted data unless the repository is allowed to contain it.
