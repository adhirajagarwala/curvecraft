# 0002 M1 Verification

Date: 2026-04-25

Milestone: M1 - diode I-V fitting and ngspice validation.

## Automated Checks

Commands run from the repository root:

```bash
pytest
ruff check .
mypy src
```

Results:

- `pytest`: 31 passed.
- `ruff check .`: all checks passed.
- `mypy src`: success, no issues found in 20 source files.

`pytest` emitted cache warnings because the sandbox could not write `.pytest_cache` under the Desktop repository. The tests themselves passed.

## ngspice Setup

`ngspice` was not initially installed on PATH. It was installed with Homebrew:

```bash
brew install ngspice
```

Verified version:

```text
ngspice-46
```

After installation, the ngspice integration tests ran instead of being skipped.

## End-to-End Demo

Command run:

```bash
MPLCONFIGDIR=/tmp/curvecraft-mplconfig python -m curvecraft.cli diode-demo \
  --data data/examples/diode_basic.csv \
  --output-dir docs/reports/m1_diode_basic
```

Input data:

- `data/examples/diode_basic.csv`
- Synthetic data, labeled in `data/README.md`.

Generated artifacts:

- `docs/reports/m1_diode_basic/diode_fit_linear.png`
- `docs/reports/m1_diode_basic/diode_fit_semilog.png`
- `docs/reports/m1_diode_basic/python_vs_ngspice.png`
- `docs/reports/m1_diode_basic/diode_validation.cir`
- `docs/reports/m1_diode_basic/diode_validation.out`
- `docs/reports/m1_diode_basic/ngspice_validation_comparison.csv`
- `docs/reports/m1_diode_basic/diode_m1_fit_report.md`

Fitted parameters from the run:

- `Is = 1.09488e-10 A`
- `n = 1.69631`
- `Rs = 3.12551e-08 ohm`
- `temperature = 300 K`

Fit metrics from the report:

- RMSE current: `8.31862e-08 A`
- RMSE log10 current: `0.0119348`
- Max absolute current error: `2.03744e-07 A`

Python-vs-ngspice validation metrics:

- Max absolute current difference: `5.27556e-08 A`
- RMSE current difference: `2.16106e-08 A`
- RMSE log10 current difference: `0.02813004592674843`

The generated PNG files were inspected and are nonempty 900 by 600 pixel images. The linear fit plot, semilog fit plot, and Python-vs-ngspice plot all show the expected diode-like increasing current curve for the synthetic input.

## Datasheet Cross-Check

A real 1N4148 datasheet was consulted as a sanity reference, not as a fitted validation dataset. The Vishay 1N4148 datasheet lists the device as a small-signal fast switching diode and gives, at ambient temperature 25 C unless otherwise specified, a forward voltage condition of `VF = 1 V` at `IF = 10 mA`, plus reverse-current and breakdown specifications.

Source: https://www.digikey.com/htmldatasheets/production/1227458/0/0/1/1n4148.html

No datasheet curve was digitized in this verification pass. CurveCraft M1 explicitly excludes datasheet image digitization, and adding that workflow here would expand the milestone. A future milestone should handle real datasheet curve extraction with provenance, digitization uncertainty, and separate tests.

## Conclusion

M1 is complete for the bundled synthetic diode example:

```text
CSV diode I-V data
-> fitted Is, n, Rs
-> measured-vs-fit plots
-> generated ngspice diode netlist
-> ngspice batch simulation
-> Python-vs-ngspice comparison
-> Markdown engineering report
-> one-command demo
```

The result is suitable as an educational, reproducible M1 workflow. It should not be treated as a validated physical model for a real device without real measured data, provenance, and operating-range review.
