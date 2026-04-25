# CurveCraft

CurveCraft is a Python package for fitting compact semiconductor models from curve data, validating generated models in ngspice, and producing engineering reports.

## Current Status

Milestone 1 is complete and verified against the bundled synthetic diode example as of 2026-04-25. CurveCraft can load diode I-V CSV data, fit the M1 Shockley-plus-series-resistance model, generate plots, export an ngspice netlist, run ngspice when installed, compare Python and ngspice currents, and write a Markdown engineering report.

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

M1 can generate a Markdown engineering report from a diode fit, plots, generated SPICE files, and optional ngspice validation metrics. Reports should describe limitations clearly and should not overstate model accuracy.

Run the bundled synthetic M1 demo from the repository root:

```bash
python -m curvecraft.cli diode-demo
```

The demo writes plots, an ngspice netlist, optional ngspice validation files, and a Markdown report to `examples/diode_basic/output/`. If ngspice is unavailable, the validation step is skipped clearly.

The verified M1 run for `data/examples/diode_basic.csv` writes reproducible artifacts under `docs/reports/m1_diode_basic/`:

```bash
python -m curvecraft.cli diode-demo \
  --data data/examples/diode_basic.csv \
  --output-dir docs/reports/m1_diode_basic
```

## Next Milestone

The next milestone should start only after M1 cleanup is reviewed. Good candidates are improving real-data provenance workflows, adding better fit diagnostics, or planning datasheet curve extraction as a separate scope. MOSFET support remains out of scope until it is explicitly planned.

## Warning

CurveCraft M1 is still an educational compact-modeling tool. Do not use fitted parameters for engineering decisions without checking data provenance, measurement conditions, model validity range, and independent validation.
