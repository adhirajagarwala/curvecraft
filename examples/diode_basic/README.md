# Basic Diode Example

This example runs the M1 diode workflow on the bundled synthetic CSV data.
The source CSV is fitted by CurveCraft's Python model, then a generated
ngspice netlist can be used to compare implementation outputs. That validation
checks consistency, not physical truth.

Run from the repository root:

```bash
python -m curvecraft.cli diode-demo
```

The command writes outputs to `examples/diode_basic/output/`:

- `diode_fit_linear.png`
- `diode_fit_semilog.png`
- `diode_validation.cir`
- `python_vs_ngspice.png` when ngspice is installed and validation runs
- `ngspice_validation_comparison.csv` when ngspice validation runs
- `diode_m1_fit_report.md`

The input data is synthetic and is for demonstration only.

Verified tracked report:
[`docs/reports/m1_diode_basic/diode_m1_fit_report.md`](../../docs/reports/m1_diode_basic/diode_m1_fit_report.md)
