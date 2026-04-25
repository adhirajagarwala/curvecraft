# Basic Diode Example

This example runs the M1 diode workflow on the bundled synthetic CSV data. It is meant to show the plumbing working end to end: load data, fit the diode model, make plots, write a SPICE netlist, optionally run ngspice, and generate a report.

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

The input data is synthetic. Treat it as a demo, not as evidence about a real diode.
