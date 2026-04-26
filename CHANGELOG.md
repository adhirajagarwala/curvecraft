# Changelog

All notable CurveCraft changes are summarized here. CurveCraft is an
educational compact-model fitting and ngspice validation toolkit; release notes
avoid production-grade model-extraction claims.

## Unreleased

- M4 portfolio polish is in progress: CI, README clarity, release notes,
  documentation navigation, artifact links, and final release-readiness.
- No new semiconductor modeling scope is planned for M4.

## v0.3.0-mosfet-id-vds-rdson

Tag: `v0.3.0-mosfet-id-vds-rdson`  
Commit: `6e824243dd994b873cc6f1f856f7fb834a5fedf5`

### Added

- MOSFET Id-Vds output-curve workflow for educational nMOS Level-1 modeling.
- Low-Vds `Rds_on` extraction by Vgs curve.
- ngspice validation netlists and Python-vs-ngspice comparison artifacts for
  the M3 output-curve workflow.
- M3 demo, report, tracked plots, comparison CSV, generated netlists, ngspice
  outputs, and engineering log.

### Links

- [M3 report](docs/reports/m3_mosfet_id_vds/mosfet_m3_id_vds_rdson_report.md)
- [M3 engineering log](docs/logs/2026-04-25-mosfet-id-vds-rdson.md)
- [M3 example](examples/mosfet_id_vds/README.md)
- [v0.3.0 release notes](docs/releases/v0.3.0-mosfet-id-vds-rdson.md)

## M2 - MOSFET Id-Vgs fitting

### Added

- MOSFET Id-Vgs transfer-curve fitting for educational nMOS Level-1 /
  square-law modeling at fixed Vds.
- Threshold extraction helpers and fitted `vth_v` / `beta_a_per_v2` reporting.
- ngspice LEVEL=1 validation netlist, optional simulator run, and
  Python-vs-ngspice comparison.
- M2 demo, report, plots, comparison CSV, ngspice output, and engineering log.

### Links

- [M2 report](docs/reports/m2_mosfet_id_vgs/mosfet_m2_id_vgs_fit_report.md)
- [M2 engineering log](docs/logs/2026-04-25-mosfet-id-vgs-fitting.md)
- [M2 example](examples/mosfet_id_vgs/README.md)

## M1 - Diode I-V fitting

### Added

- Diode I-V fitting with a Shockley diode plus series resistance model.
- ngspice validation netlist, optional simulator run, and Python-vs-ngspice
  current comparison.
- M1 demo, report, plots, comparison CSV, ngspice output, and engineering log.

### Links

- [M1 report](docs/reports/m1_diode_basic/diode_m1_fit_report.md)
- [M1 engineering log](docs/logs/0002-m1-verification.md)
- [M1 example](examples/diode_basic/README.md)
