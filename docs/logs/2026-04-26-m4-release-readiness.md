# 2026-04-26 - M4 Release Readiness

## What I polished

M4 focused on making CurveCraft easier to review as a GitHub portfolio project.
I added GitHub Actions CI, tightened the README story, added changelog and
release notes, created a docs index and artifact map, cleaned report/example
artifact links, and documented the release-readiness state here.

No new semiconductor modeling scope was added during M4.

## Why polish matters

M1-M3 already showed the core learning arc: fit compact models, generate plots,
write reports, and validate generated ngspice artifacts. M4 makes that work
legible to a skimmer by showing what is complete, where the evidence lives, and
what the validation does and does not prove.

## CI and reproducibility

The repository now has a GitHub Actions workflow at
[`../../.github/workflows/ci.yml`](../../.github/workflows/ci.yml). It runs the
same repo-standard checks used locally:

```bash
python -m pytest
ruff check .
mypy src
```

The workflow installs with:

```bash
python -m pip install -e ".[dev]"
```

One CI failure surfaced a Python 3.11 mypy typing issue in the MOSFET Level-1
model. The fix was a type-only cast around the `np.maximum` result; it did not
change model equations or fitting behavior.

## README and project story

The README now opens with a concise pitch and a status table:

- M1 diode I-V fitting + ngspice validation: complete.
- M2 MOSFET Id-Vgs fitting + ngspice validation: complete.
- M3 MOSFET Id-Vds fitting + Rds_on extraction: complete.
- M4 portfolio polish and release readiness: in progress at the time of this
  log.

It also includes quickstart commands, demo commands, artifact links, validation
meaning, and explicit limitations. The public story distinguishes source curve
data, fitted Python compact-model outputs, generated ngspice artifacts, and
Python-vs-ngspice comparisons.

## Reports and artifact navigation

The docs index at [`../README.md`](../README.md) maps reports, engineering
logs, theory docs, examples, data files, release notes, and tracked artifacts.

The M1/M2/M3 reports now link relevant tracked artifacts:

- Plots.
- Generated SPICE/netlist files.
- ngspice `.out` files.
- Python-vs-ngspice comparison CSVs.
- Python-vs-ngspice plots.

The example READMEs point to their corresponding verified tracked reports.

## Release notes and changelog

M4 added [`../../CHANGELOG.md`](../../CHANGELOG.md) and
[`../releases/v0.3.0-mosfet-id-vds-rdson.md`](../releases/v0.3.0-mosfet-id-vds-rdson.md).

The changelog summarizes:

- M1 diode I-V fitting with Shockley + Rs and ngspice validation.
- M2 MOSFET Id-Vgs fitting, threshold extraction, and ngspice validation.
- M3 MOSFET Id-Vds fitting, Rds_on extraction, reports, demos, logs, and
  ngspice validation.
- Unreleased M4 polish work.

The release notes document the `v0.3.0-mosfet-id-vds-rdson` tag without
creating a new tag.

## Validation meaning

CurveCraft validation follows this chain:

```text
source curve data
-> fitted Python compact model
-> generated ngspice model/netlist
-> Python-vs-ngspice comparison
-> report and plots
```

The ngspice validation checks Python/SPICE implementation consistency. It does
not prove physical truth, real device fidelity, or validity outside the input
data and stated assumptions.

## Limitations I kept explicit

CurveCraft uses educational compact models. The MOSFET workflows are simplified
Level-1 / square-law examples, not BSIM and not production-grade model
extraction.

The documentation keeps these limitations visible:

- Threshold voltage is extraction-method-dependent.
- Rds_on depends on extraction method and operating assumptions.
- `beta_a_per_v2` is an effective fitted parameter under the demo assumptions.
- ngspice validation checks implementation consistency, not physical truth.
- Datasheet image digitization is not implemented.
- pMOS, BSIM, capacitance, gate charge, switching-loss, and thermal modeling
  are outside the current implemented scope.

## Evidence

- CI workflow: [`../../.github/workflows/ci.yml`](../../.github/workflows/ci.yml)
- Tests: `python -m pytest`
- Lint: `ruff check .`
- Type checking: `mypy src`
- Demos:
  - `python -m curvecraft.cli diode-demo`
  - `python -m curvecraft.cli mosfet-id-vgs-demo`
  - `python -m curvecraft.cli mosfet-id-vds-demo`
- Docs/reports:
  - [`../reports/m1_diode_basic/diode_m1_fit_report.md`](../reports/m1_diode_basic/diode_m1_fit_report.md)
  - [`../reports/m2_mosfet_id_vgs/mosfet_m2_id_vgs_fit_report.md`](../reports/m2_mosfet_id_vgs/mosfet_m2_id_vgs_fit_report.md)
  - [`../reports/m3_mosfet_id_vds/mosfet_m3_id_vds_rdson_report.md`](../reports/m3_mosfet_id_vds/mosfet_m3_id_vds_rdson_report.md)
- Release notes:
  - [`../releases/v0.3.0-mosfet-id-vds-rdson.md`](../releases/v0.3.0-mosfet-id-vds-rdson.md)

## What I learned

The implementation work and the portfolio story need different kinds of
precision. The code needs tests and small typed modules; the project page needs
clear boundaries, artifact trails, and honest wording about validation. The CI
failure also showed why running checks under the same Python version as CI
matters, especially for NumPy typing.

## Remaining rough edges

- Some older M3 planning issues in Linear still exist and may no longer match
  the completed repository state.
- The example data is synthetic and small.
- The reports are intentionally lightweight Markdown, not a full publication
  or datasheet-style extraction notebook.
- The generated artifacts are discoverable now, but a future docs pass could
  add screenshots or a compact visual artifact gallery.

## Next steps

Good next steps would be to review the pushed CI status, decide whether to cut
a final M4 polish commit or PR, and consider future work with real-data-style
examples or PDK-related tooling. Those future directions should be scoped
deliberately; this log does not promise exact scope or start a new project.
