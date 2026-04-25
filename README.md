# CurveCraft

CurveCraft is a Python package for fitting compact semiconductor models from curve data, validating generated models in ngspice, and producing engineering reports.

## Current Status

This repository is at the initial skeleton stage. The package layout, documentation placeholders, and import test exist, but modeling and fitting behavior are not implemented yet.

## First Milestone

M1 focuses only on diode I-V fitting and ngspice validation.

Planned M1 work includes:

- Loading diode I-V curve data from documented CSV files.
- Fitting a compact diode model with clear equations, units, and assumptions.
- Writing ngspice netlists for validation.
- Comparing fitted model results against source curves.
- Producing simple engineering reports.

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

## Warning

Modeling, fitting, plotting, ngspice validation, and report generation are not implemented yet. Do not use this package for engineering decisions until those features are implemented, tested, and documented.
