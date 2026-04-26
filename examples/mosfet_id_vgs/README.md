# MOSFET Id-Vgs Example

This example runs the M2 MOSFET transfer-curve workflow on bundled synthetic
CSV data. It shows the plumbing working end to end: load data, estimate
threshold voltage, fit the simple Level-1 model, make plots, write a SPICE
netlist, optionally run ngspice, and generate a report.
The source CSV, fitted Python model output, and generated ngspice validation
artifacts are separate pieces of the workflow. ngspice validation checks
implementation consistency, not physical truth.

Run from the repository root:

```bash
python -m curvecraft.cli mosfet-id-vgs-demo
```

The command writes outputs to `examples/mosfet_id_vgs/output/`:

- `mosfet_id_vgs_fit_linear.png`
- `mosfet_id_vgs_fit_semilog.png`
- `mosfet_id_vgs_validation.cir`
- `mosfet_python_vs_ngspice.png` when ngspice is installed and validation runs
- `mosfet_ngspice_validation_comparison.csv` when ngspice validation runs
- `mosfet_m2_id_vgs_fit_report.md`

The input data is synthetic. Treat it as a demo, not as evidence about a real
MOSFET.

Verified tracked report:
[`docs/reports/m2_mosfet_id_vgs/mosfet_m2_id_vgs_fit_report.md`](../../docs/reports/m2_mosfet_id_vgs/mosfet_m2_id_vgs_fit_report.md)
