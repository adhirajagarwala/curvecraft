# CurveCraft

CurveCraft is a Python package for fitting compact semiconductor models from curve data, validating generated models in ngspice, and producing engineering reports.

## Current Status

This repository is at the initial skeleton stage. The package layout, documentation placeholders, and import test exist, but modeling and fitting behavior are not implemented yet.

## Current Milestone

M1 focuses on diode I-V CSV loading, diode compact-model fitting, ngspice netlist generation, ngspice validation, plots, and a Markdown report.

Planned M1 work includes:

- Loading diode I-V curve data from documented CSV files.
- Fitting a compact diode model with clear equations, units, and assumptions.
- Writing ngspice netlists for validation.
- Comparing fitted model results against source curves.
- Plotting measured and simulated curves.
- Producing simple Markdown engineering reports.

MOSFET support is intentionally out of scope until diode M1 is complete.

## Install

```bash
python -m pip install -e ".[dev]"
```

## Test

```bash
pytest
ruff check .
```

## M1 Demo Outputs

M1 plotting utilities save PNG files for measured-vs-model diode I-V curves. Example scripts should write generated plots under an output folder such as:

```text
examples/diode_basic/output/
```

Generated plots are not committed as final results unless they come from documented input data and reproducible commands.

M1 also includes deterministic ngspice diode netlist generation for fitted `Is`, `n`, and `Rs` parameters. Netlist generation does not run ngspice by itself.

ngspice execution is optional. If `ngspice` is not installed, validation runner tests and demos skip that step clearly instead of pretending simulation happened.

Python-vs-ngspice validation compares CurveCraft's Python diode model with parsed ngspice sweep output for the same parameters and voltage points. This checks implementation consistency, not whether the original CSV data is physically perfect.

## Warning

ngspice validation and report generation are not implemented yet. Do not use this package for engineering decisions until those features are implemented, tested, and documented.
