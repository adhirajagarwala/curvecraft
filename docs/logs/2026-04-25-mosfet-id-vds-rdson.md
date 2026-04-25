# 2026-04-25 - MOSFET Id-Vds and Rds_on

## What I built

M3 adds a narrow MOSFET output-curve workflow to CurveCraft. It loads synthetic
n-channel Id-Vds CSV data, evaluates and fits a simple Level-1 model, extracts
low-Vds Rds_on values by Vgs, makes plots, writes ngspice LEVEL=1 Id-Vds
netlists, optionally runs ngspice validation, and writes a Markdown report.

## Why Id-Vds curves matter

Id-Vds curves show drain current as drain-source voltage changes at fixed
gate-source biases. They make output behavior visible across different Vgs
conditions, including the low-Vds linear region and the higher-Vds saturation
trend.

## What Rds_on means

CurveCraft extracts Rds_on as the inverse slope of Id versus Vds in the low-Vds
region. This value depends strongly on Vgs and temperature, and it can also
depend on device and package details. In M3 it is an extraction from the input
curve data, not an automatic datasheet package-level guarantee.

## Model used

M3 uses the same educational n-channel enhancement MOSFET Level-1 / square-law
model as M2. It includes triode and saturation equations plus a simple
`lambda_1_per_v` channel-length modulation approximation. It is simplified
compared with real MOSFET behavior and is not BSIM.

## How fitting worked

The Id-Vds fitter uses `scipy.optimize.least_squares` with bounded parameters.
It can fit beta and lambda while holding Vth fixed, or fit Vth jointly when a
fixed threshold is not supplied. Vth is often better constrained by Id-Vgs data,
so joint Id-Vds fitting should be read as an educational workflow choice.

## How Rds_on extraction worked

For each stepped Vgs curve, CurveCraft selects a low-Vds region and fits:

```text
Id ~= conductance * Vds + intercept
```

Then it reports:

```text
Rds_on = 1 / conductance
```

Curves without a positive low-Vds conductance are rejected by the extraction
helper rather than silently producing a misleading resistance.

## How ngspice validation worked

CurveCraft writes one normalized ngspice LEVEL=1 NMOS netlist per fixed Vgs:

```spice
M1 drain gate 0 0 curve_nmos W=1 L=1
.model curve_nmos NMOS (LEVEL=1 VTO=<Vth> KP=<beta> LAMBDA=<lambda>)
```

Each netlist holds Vgs fixed, sweeps Vds, parses `i(Vds)`, and compares the
result against the Python Level-1 model evaluated at the same Vgs/Vds points.
This validates implementation consistency with the generated SPICE model, not
real-device truth.

## What matched

For the bundled synthetic M3 example, the workflow completes end to end and the
same fitted parameters are used consistently by the Python model, generated
plots, generated SPICE netlists, and Markdown report.

## What did not match or remains simplified

The Level-1 model ignores subthreshold conduction, body effect, capacitance,
gate charge, self-heating, velocity saturation, package resistance, switching
loss, and BSIM-level behavior. The synthetic data is not measured device data.

## What I learned

Id-Vds and Rds_on are useful because they force the project to separate
measured/source curves, fitted Python model behavior, low-Vds extraction, and
ngspice implementation checks. The important part is making the assumptions
visible, not pretending the model is more physically complete than it is.

## Evidence

- Tests: `pytest`, `ruff check .`, and `mypy src`
- Plots: `docs/reports/m3_mosfet_id_vds/mosfet_id_vds_family.png` and `docs/reports/m3_mosfet_id_vds/mosfet_id_vds_fit.png`
- Report: `docs/reports/m3_mosfet_id_vds/mosfet_m3_id_vds_rdson_report.md`
- Demo command:

```bash
python -m curvecraft.cli mosfet-id-vds-demo \
  --data data/examples/mosfet_id_vds_example.csv \
  --output-dir docs/reports/m3_mosfet_id_vds
```

## Next steps

Good next steps are review, small usability polish, and possibly richer
ngspice artifact handling. p-channel devices, BSIM, capacitance, gate charge,
switching loss, thermal modeling, and datasheet digitization should remain
separate milestones.
