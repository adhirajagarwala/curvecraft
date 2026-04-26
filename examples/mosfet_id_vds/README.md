# MOSFET Id-Vds and Rds_on Example

This example runs the M3 MOSFET output-curve workflow on bundled synthetic CSV
data. It shows the end-to-end plumbing: load tidy Id-Vds data, fit the simple
Level-1 model, extract low-Vds Rds_on by Vgs, make plots, write ngspice LEVEL=1
netlists, optionally run ngspice, and generate a Markdown report.
The source CSV, fitted Python model output, and generated ngspice validation
artifacts are separate pieces of the workflow. ngspice validation checks
implementation consistency, not physical truth.

Run from the repository root:

```bash
python -m curvecraft.cli mosfet-id-vds-demo
```

The command writes outputs to `examples/mosfet_id_vds/output/`:

- `mosfet_id_vds_family.png`
- `mosfet_id_vds_fit.png`
- one `mosfet_id_vds_vgs_*.cir` netlist per Vgs value
- `mosfet_id_vds_python_vs_ngspice.png` when ngspice validation runs
- `mosfet_id_vds_ngspice_validation_comparison.csv` when ngspice validation runs
- `mosfet_m3_id_vds_rdson_report.md`

The input data is synthetic. Treat it as a demo, not as evidence about a real
MOSFET.

Verified tracked report:
[`docs/reports/m3_mosfet_id_vds/mosfet_m3_id_vds_rdson_report.md`](../../docs/reports/m3_mosfet_id_vds/mosfet_m3_id_vds_rdson_report.md)
