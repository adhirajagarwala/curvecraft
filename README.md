# CurveCraft

[![CI](https://github.com/adhirajagarwala/curvecraft/actions/workflows/ci.yml/badge.svg)](https://github.com/adhirajagarwala/curvecraft/actions/workflows/ci.yml)

CurveCraft is a Python toolkit for fitting educational semiconductor compact
models from curve data, validating generated ngspice implementations, and
writing reproducible engineering reports.

## Current Status

| Milestone | Status | Scope |
| --- | --- | --- |
| M1 | Complete | Diode I-V fitting + ngspice validation |
| M2 | Complete | nMOS Id-Vgs fitting + ngspice validation |
| M3 | Complete | nMOS Id-Vds fitting + Rds_on extraction |
| M4 | In progress | Portfolio polish and release readiness |

Latest completed release tag: `v0.3.0-mosfet-id-vds-rdson`. See the
[changelog](CHANGELOG.md) and
[v0.3.0 release notes](docs/releases/v0.3.0-mosfet-id-vds-rdson.md).

## Milestones At A Glance

| Milestone | Device / curve | Model / extraction | Validation | Report / demo links |
| --- | --- | --- | --- | --- |
| M1 | Diode I-V | Shockley diode with series resistance | Generated ngspice netlist, Python-vs-ngspice current comparison | [Report](docs/reports/m1_diode_basic/diode_m1_fit_report.md), [example](examples/diode_basic/README.md) |
| M2 | nMOS Id-Vgs transfer curve | Simplified Level-1 / square-law fit at fixed Vds | Generated ngspice LEVEL=1 netlist, Python-vs-ngspice comparison | [Report](docs/reports/m2_mosfet_id_vgs/mosfet_m2_id_vgs_fit_report.md), [log](docs/logs/2026-04-25-mosfet-id-vgs-fitting.md), [example](examples/mosfet_id_vgs/README.md) |
| M3 | nMOS Id-Vds output curves | Simplified Level-1 / square-law fit plus low-Vds Rds_on by Vgs | Generated ngspice LEVEL=1 netlists, Python-vs-ngspice comparison | [Report](docs/reports/m3_mosfet_id_vds/mosfet_m3_id_vds_rdson_report.md), [log](docs/logs/2026-04-25-mosfet-id-vds-rdson.md), [example](examples/mosfet_id_vds/README.md) |

## Quickstart

Install from the repository root:

```bash
python -m pip install -e ".[dev]"
```

Run the repo-standard checks:

```bash
python -m pytest
ruff check .
mypy src
```

## Demo Commands

| Demo | Command | Verified report output |
| --- | --- | --- |
| Diode I-V | `python -m curvecraft.cli diode-demo --data data/examples/diode_basic.csv --output-dir docs/reports/m1_diode_basic` | [docs/reports/m1_diode_basic/diode_m1_fit_report.md](docs/reports/m1_diode_basic/diode_m1_fit_report.md) |
| MOSFET Id-Vgs | `python -m curvecraft.cli mosfet-id-vgs-demo --data data/examples/mosfet_id_vgs_example.csv --output-dir docs/reports/m2_mosfet_id_vgs` | [docs/reports/m2_mosfet_id_vgs/mosfet_m2_id_vgs_fit_report.md](docs/reports/m2_mosfet_id_vgs/mosfet_m2_id_vgs_fit_report.md) |
| MOSFET Id-Vds / Rds_on | `python -m curvecraft.cli mosfet-id-vds-demo --data data/examples/mosfet_id_vds_example.csv --output-dir docs/reports/m3_mosfet_id_vds` | [docs/reports/m3_mosfet_id_vds/mosfet_m3_id_vds_rdson_report.md](docs/reports/m3_mosfet_id_vds/mosfet_m3_id_vds_rdson_report.md) |

The demos can also be run without arguments to write into the corresponding
`examples/*/output/` directory.

## Artifact Index

| Category | Links |
| --- | --- |
| Reports | [M1 diode](docs/reports/m1_diode_basic/diode_m1_fit_report.md), [M2 MOSFET Id-Vgs](docs/reports/m2_mosfet_id_vgs/mosfet_m2_id_vgs_fit_report.md), [M3 MOSFET Id-Vds / Rds_on](docs/reports/m3_mosfet_id_vds/mosfet_m3_id_vds_rdson_report.md) |
| Documentation index | [Docs index and artifact map](docs/README.md) |
| Engineering logs | [Project start](docs/logs/0001-project-start.md), [M1 verification](docs/logs/0002-m1-verification.md), [M2 log](docs/logs/2026-04-25-mosfet-id-vgs-fitting.md), [M3 log](docs/logs/2026-04-25-mosfet-id-vds-rdson.md), [M4 release readiness](docs/logs/2026-04-26-m4-release-readiness.md) |
| Examples | [Diode](examples/diode_basic/README.md), [MOSFET Id-Vgs](examples/mosfet_id_vgs/README.md), [MOSFET Id-Vds](examples/mosfet_id_vds/README.md), [CSV data](data/examples/) |
| Theory docs | [Diode model](docs/theory/diode-model.md), [diode data schema](docs/theory/diode-data-schema.md), [MOSFET model](docs/theory/mosfet-model.md), [MOSFET Id-Vgs schema](docs/theory/mosfet-data-schema.md), [threshold extraction](docs/theory/mosfet-threshold-extraction.md), [MOSFET Id-Vds schema](docs/theory/mosfet-id-vds-data-schema.md), [Id-Vds fitting](docs/theory/mosfet-id-vds-fitting.md), [Rds_on extraction](docs/theory/rdson-extraction.md), [SPICE validation](docs/theory/spice-validation.md) |

## What Validation Means

CurveCraft keeps the workflow pieces separate:

```text
source curve data
-> fitted Python compact model
-> generated ngspice model/netlist
-> Python-vs-ngspice comparison
-> Markdown report and plots
```

The source curve data is the input being fitted. The fitted Python model is the
repo's numerical compact-model implementation. The generated ngspice model and
netlist are an independent simulator representation of the same simplified
model. The Python-vs-ngspice comparison checks implementation consistency; it
does not prove that the source data describes a real device or that the fitted
parameters are valid outside the stated input range.

## Limitations And Scope

CurveCraft is an educational compact-modeling project, not a production-grade
model extraction system.

- MOSFET support is nMOS only in the current scope.
- M2 and M3 use simplified Level-1 / square-law modeling, not BSIM.
- Threshold voltage and Rds_on are extraction-method-dependent results, not
  universal device constants.
- ngspice validation checks consistency between generated implementations, not
  real-world physical truth.
- There is no pMOS, BSIM, capacitance, gate-charge, switching-loss, thermal, or
  datasheet image digitization support yet.
- Do not use fitted parameters for engineering decisions without checking data
  provenance, measurement conditions, model validity range, and independent
  validation.
