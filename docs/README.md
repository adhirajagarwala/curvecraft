# CurveCraft Documentation Index

This page maps the tracked CurveCraft documentation and artifacts for quick
review. It separates source data, fitted Python outputs, generated SPICE
artifacts, ngspice outputs, comparison files, plots, examples, and engineering
notes.

## Reports

| Milestone | Scope | Report |
| --- | --- | --- |
| M1 | Diode I-V fitting + ngspice validation | [M1 diode report](reports/m1_diode_basic/diode_m1_fit_report.md) |
| M2 | MOSFET Id-Vgs fitting + ngspice validation | [M2 MOSFET Id-Vgs report](reports/m2_mosfet_id_vgs/mosfet_m2_id_vgs_fit_report.md) |
| M3 | MOSFET Id-Vds fitting + Rds_on extraction | [M3 MOSFET Id-Vds / Rds_on report](reports/m3_mosfet_id_vds/mosfet_m3_id_vds_rdson_report.md) |

## Engineering Logs

| Milestone | Log |
| --- | --- |
| M1 | [M1 verification log](logs/0002-m1-verification.md) |
| M2 | [M2 MOSFET Id-Vgs fitting log](logs/2026-04-25-mosfet-id-vgs-fitting.md) |
| M3 | [M3 MOSFET Id-Vds / Rds_on log](logs/2026-04-25-mosfet-id-vds-rdson.md) |

Project setup context: [project start log](logs/0001-project-start.md).

## Theory Docs

| Topic | Docs |
| --- | --- |
| Diode model | [Diode model](theory/diode-model.md) |
| Diode data schema | [Diode data schema](theory/diode-data-schema.md) |
| MOSFET model | [MOSFET model](theory/mosfet-model.md) |
| MOSFET Id-Vgs schema | [MOSFET Id-Vgs data schema](theory/mosfet-data-schema.md) |
| MOSFET threshold extraction | [Threshold extraction](theory/mosfet-threshold-extraction.md) |
| MOSFET Id-Vds schema and fitting | [Id-Vds data schema](theory/mosfet-id-vds-data-schema.md), [Id-Vds fitting](theory/mosfet-id-vds-fitting.md) |
| Rds_on extraction | [Rds_on extraction](theory/rdson-extraction.md) |
| SPICE validation | [SPICE validation](theory/spice-validation.md) |

## Examples

| Demo | Example docs | Source data |
| --- | --- | --- |
| Diode I-V | [Diode demo](../examples/diode_basic/README.md) | [diode_basic.csv](../data/examples/diode_basic.csv), [diode_iv_example.csv](../data/examples/diode_iv_example.csv) |
| MOSFET Id-Vgs | [MOSFET Id-Vgs demo](../examples/mosfet_id_vgs/README.md) | [mosfet_id_vgs_example.csv](../data/examples/mosfet_id_vgs_example.csv) |
| MOSFET Id-Vds / Rds_on | [MOSFET Id-Vds demo](../examples/mosfet_id_vds/README.md) | [mosfet_id_vds_example.csv](../data/examples/mosfet_id_vds_example.csv) |

## Artifact Map

| Milestone | Source data | Fitted Python outputs | Generated SPICE netlists | ngspice raw outputs | Comparison CSVs | Plots |
| --- | --- | --- | --- | --- | --- | --- |
| M1 diode | [CSV](../data/examples/diode_basic.csv) | [Report](reports/m1_diode_basic/diode_m1_fit_report.md) | [Netlist](reports/m1_diode_basic/diode_validation.cir) | [Output](reports/m1_diode_basic/diode_validation.out) | [Comparison CSV](reports/m1_diode_basic/ngspice_validation_comparison.csv) | [Linear](reports/m1_diode_basic/diode_fit_linear.png), [semilog](reports/m1_diode_basic/diode_fit_semilog.png), [Python vs ngspice](reports/m1_diode_basic/python_vs_ngspice.png) |
| M2 MOSFET Id-Vgs | [CSV](../data/examples/mosfet_id_vgs_example.csv) | [Report](reports/m2_mosfet_id_vgs/mosfet_m2_id_vgs_fit_report.md) | [Netlist](reports/m2_mosfet_id_vgs/mosfet_id_vgs_validation.cir) | [Output](reports/m2_mosfet_id_vgs/mosfet_id_vgs_validation.out) | [Comparison CSV](reports/m2_mosfet_id_vgs/mosfet_ngspice_validation_comparison.csv) | [Linear](reports/m2_mosfet_id_vgs/mosfet_id_vgs_fit_linear.png), [semilog](reports/m2_mosfet_id_vgs/mosfet_id_vgs_fit_semilog.png), [Python vs ngspice](reports/m2_mosfet_id_vgs/mosfet_python_vs_ngspice.png) |
| M3 MOSFET Id-Vds / Rds_on | [CSV](../data/examples/mosfet_id_vds_example.csv) | [Report](reports/m3_mosfet_id_vds/mosfet_m3_id_vds_rdson_report.md) | [Vgs 0.1 netlist](reports/m3_mosfet_id_vds/mosfet_id_vds_validation_0.cir), [Vgs 1.2 netlist](reports/m3_mosfet_id_vds/mosfet_id_vds_validation_1.cir), [Vgs 2.3 netlist](reports/m3_mosfet_id_vds/mosfet_id_vds_validation_2.cir) | [Output 0](reports/m3_mosfet_id_vds/mosfet_id_vds_validation_0.out), [output 1](reports/m3_mosfet_id_vds/mosfet_id_vds_validation_1.out), [output 2](reports/m3_mosfet_id_vds/mosfet_id_vds_validation_2.out) | [Comparison CSV](reports/m3_mosfet_id_vds/mosfet_id_vds_ngspice_validation_comparison.csv) | [Family](reports/m3_mosfet_id_vds/mosfet_id_vds_family.png), [fit](reports/m3_mosfet_id_vds/mosfet_id_vds_fit.png), [Python vs ngspice](reports/m3_mosfet_id_vds/mosfet_id_vds_python_vs_ngspice.png) |

The `mosfet_id_vds_vgs_*.cir` files in
[M3 reports](reports/m3_mosfet_id_vds/) are additional generated per-curve
netlists retained with the tracked M3 artifacts.

## Validation Artifact Meaning

- Source data: CSV files in [`../data/examples/`](../data/examples/) used as
  the measured or synthetic input curves for fitting.
- Fitted Python model outputs: report tables, fitted parameter summaries, and
  Python-generated curves from CurveCraft's compact-model implementation.
- Generated SPICE netlists: `.cir` files written from fitted parameters for
  ngspice validation.
- ngspice raw outputs: `.out` files captured from ngspice batch runs.
- Comparison CSVs: tabular Python-vs-ngspice current comparisons.
- Plots: measured/source curves, fitted Python curves, and Python-vs-ngspice
  validation visualizations.

ngspice validation checks implementation consistency between CurveCraft's
Python equations and generated simulator artifacts. It does not prove that the
input data is a physically true device model or that fitted parameters are
valid outside the documented assumptions.

## Releases

- [v0.3.0 MOSFET Id-Vds / Rds_on release notes](releases/v0.3.0-mosfet-id-vds-rdson.md)
- [Project changelog](../CHANGELOG.md)

## Scope And Limitations

- CurveCraft uses educational compact models.
- M2 and M3 use simplified Level-1 / square-law MOSFET modeling, not BSIM.
- This is not production-grade semiconductor model extraction.
- ngspice validation checks implementation consistency, not physical model
  truth.
- Datasheet image digitization is not implemented yet.
