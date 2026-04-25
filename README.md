# CurveCraft

CurveCraft is a Python package for fitting compact semiconductor models from
curve data, validating generated models in ngspice, and producing engineering
reports.

## Current Status

M1 diode fitting is complete. CurveCraft can load diode I-V CSV data, fit a
Shockley-plus-series-resistance model, generate plots, export and run an
ngspice validation netlist, compare Python and ngspice currents, and write a
Markdown engineering report.

M2 MOSFET Id-Vgs fitting is complete for a narrow educational scope. CurveCraft
can load n-channel enhancement MOSFET transfer-curve CSV data, fit a simple
Level-1/square-law model at fixed Vds, generate measured-vs-fit plots, export
and run an ngspice LEVEL=1 validation netlist, and write a Markdown engineering
report.

M3 MOSFET Id-Vds and Rds_on extraction is complete for a narrow educational
scope. CurveCraft can load n-channel output-curve CSV data, fit the same simple
Level-1/square-law model, extract low-Vds Rds_on values by Vgs, generate plots,
export and optionally run ngspice LEVEL=1 validation netlists, and write a
Markdown engineering report.

M2 and M3 are not BSIM extraction and are not production MOSFET modeling flows.

## Install

```bash
python -m pip install -e ".[dev]"
```

## Test

```bash
pytest
ruff check .
mypy src
```

## Diode Demo

Run the bundled synthetic M1 diode demo from the repository root:

```bash
python -m curvecraft.cli diode-demo
```

The demo writes plots, an ngspice netlist, optional ngspice validation files,
and a Markdown report to:

```text
examples/diode_basic/output/
```

The verified M1 artifact run used:

```bash
python -m curvecraft.cli diode-demo \
  --data data/examples/diode_basic.csv \
  --output-dir docs/reports/m1_diode_basic
```

M1 report: [docs/reports/m1_diode_basic/diode_m1_fit_report.md](docs/reports/m1_diode_basic/diode_m1_fit_report.md)

## MOSFET Id-Vgs Demo

Run the bundled synthetic M2 MOSFET transfer-curve demo from the repository
root:

```bash
python -m curvecraft.cli mosfet-id-vgs-demo
```

The demo writes measured-vs-fit plots, an ngspice LEVEL=1 netlist, optional
ngspice validation files, and a Markdown report to:

```text
examples/mosfet_id_vgs/output/
```

The verified M2 artifact run used:

```bash
python -m curvecraft.cli mosfet-id-vgs-demo \
  --data data/examples/mosfet_id_vgs_example.csv \
  --output-dir docs/reports/m2_mosfet_id_vgs
```

M2 report: [docs/reports/m2_mosfet_id_vgs/mosfet_m2_id_vgs_fit_report.md](docs/reports/m2_mosfet_id_vgs/mosfet_m2_id_vgs_fit_report.md)

M2 engineering log: [docs/logs/2026-04-25-mosfet-id-vgs-fitting.md](docs/logs/2026-04-25-mosfet-id-vgs-fitting.md)

## MOSFET Id-Vds and Rds_on Demo

Run the bundled synthetic M3 MOSFET output-curve demo from the repository root:

```bash
python -m curvecraft.cli mosfet-id-vds-demo
```

The demo writes Id-Vds plots, ngspice LEVEL=1 netlists, optional ngspice
validation files, and a Markdown report to:

```text
examples/mosfet_id_vds/output/
```

The verified M3 artifact run used:

```bash
python -m curvecraft.cli mosfet-id-vds-demo \
  --data data/examples/mosfet_id_vds_example.csv \
  --output-dir docs/reports/m3_mosfet_id_vds
```

M3 uses a simple educational Level-1 model and extracts Rds_on from the low-Vds
slope of the input curves. It is not BSIM-level extraction or production-grade
model generation.

M3 report: [docs/reports/m3_mosfet_id_vds/mosfet_m3_id_vds_rdson_report.md](docs/reports/m3_mosfet_id_vds/mosfet_m3_id_vds_rdson_report.md)

M3 engineering log: [docs/logs/2026-04-25-mosfet-id-vds-rdson.md](docs/logs/2026-04-25-mosfet-id-vds-rdson.md)

## What M2 Does And Does Not Prove

M2 checks that CurveCraft can move through a reproducible MOSFET Id-Vgs
workflow:

```text
CSV MOSFET transfer data
-> threshold extraction helpers
-> fitted Vth and beta
-> measured-vs-fit plots
-> generated ngspice LEVEL=1 netlist
-> optional ngspice batch simulation
-> Python-vs-ngspice comparison
-> Markdown engineering report
```

This is an implementation and workflow validation. It does not prove that the
synthetic example represents a real MOSFET, and it does not make a fitted
Level-1 model valid outside the measured range.

## What M3 Does And Does Not Prove

M3 checks that CurveCraft can move through a reproducible MOSFET Id-Vds and
Rds_on workflow:

```text
CSV MOSFET output-curve data
-> fitted Level-1 Id-Vds model
-> low-Vds Rds_on extraction by Vgs
-> measured-vs-fit plots
-> generated ngspice LEVEL=1 netlists
-> optional ngspice batch simulation
-> Python-vs-ngspice comparison
-> Markdown engineering report
```

This is still an implementation and workflow validation. It does not prove that
the synthetic example represents a real MOSFET, and it does not make extracted
Rds_on values valid outside the input data and stated assumptions.

## Warning

CurveCraft is an educational compact-modeling tool. Do not use fitted
parameters for engineering decisions without checking data provenance,
measurement conditions, model validity range, and independent validation.
