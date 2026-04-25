# CurveCraft

CurveCraft is a small Python toolkit for compact semiconductor modeling from curve data. The first milestone is deliberately narrow: fit a diode I-V curve, validate the fitted model in ngspice, and leave behind a report that an engineer can actually read.

## Status

Milestone 1 is complete and verified against the bundled synthetic diode example as of 2026-04-25.

CurveCraft can now:

- load diode I-V CSV files with `voltage_v` and `current_a` columns
- fit a Shockley diode model with optional series resistance
- plot measured current against the fitted model
- generate an ngspice diode model and DC sweep netlist
- run ngspice when it is installed
- compare Python-model current against ngspice current
- write a Markdown report with fitted parameters, errors, artifacts, and limitations

The example data in this repository is synthetic. It is useful for testing the workflow, not for claiming anything about a real diode.

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

## Run The M1 Demo

From the repository root:

```bash
python -m curvecraft.cli diode-demo
```

By default, the demo writes outputs to:

```text
examples/diode_basic/output/
```

The output folder contains the fitted plots, ngspice netlist, optional ngspice validation files, and a Markdown report. If `ngspice` is not installed, the demo skips validation clearly instead of pretending simulation happened.

The verified M1 run committed in this repo used:

```bash
python -m curvecraft.cli diode-demo \
  --data data/examples/diode_basic.csv \
  --output-dir docs/reports/m1_diode_basic
```

Those verification artifacts live in `docs/reports/m1_diode_basic/`.

## What M1 Does And Does Not Prove

M1 checks that CurveCraft can move through the full diode workflow:

```text
CSV diode I-V data
-> fitted Is, n, Rs
-> measured-vs-fit plots
-> generated ngspice diode netlist
-> ngspice batch simulation
-> Python-vs-ngspice comparison
-> Markdown report
```

That is an implementation and workflow validation. It does not prove that a fitted model is physically correct for a real device unless the input data has real provenance, known measurement conditions, and a sensible operating range.

## Next

Good next steps are improving real-data provenance, adding fit diagnostics, and planning datasheet curve extraction as its own scoped milestone. MOSFET support stays out of scope until it is explicitly planned.

## Warning

CurveCraft M1 is an educational compact-modeling tool. Do not use fitted parameters for engineering decisions without checking the data source, measurement setup, model validity range, and independent validation.
