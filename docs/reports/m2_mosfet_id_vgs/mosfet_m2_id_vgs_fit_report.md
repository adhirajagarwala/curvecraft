# M2 MOSFET Id-Vgs Fit Report

## Experiment Question

How well does a simple Level-1 n-channel MOSFET model fit this Id-Vgs transfer curve at fixed Vds?

## Input Data

- CSV: `../../../data/examples/mosfet_id_vgs_example.csv`
- Fixed Vds: `5 V`
- Total rows: 9
- Positive-current rows used for fit: 6

## Fitted Parameters

- Vth: `1.25 V`
- beta: `0.0008 A/V^2`
- lambda: `0 1/V` (fixed at 0 for M2 Id-Vgs fitting)

## Extraction Method Summary

- Constant-current estimate: `Vth = 1.6875 V` at `Id = 0.0001 A`
- sqrt(Id) linear estimate: `Vth = 1.25 V`
- sqrt(Id) selected points: `4`
- Final nonlinear fit: `Vth = 1.25 V`, `beta = 0.0008 A/V^2`

## Model Equation

For overdrive `Vov = Vgs - Vth`, CurveCraft M2 uses:

```text
Id = 0, for Vov <= 0
Id = beta * (Vov * Vds - 0.5 * Vds^2) * (1 + lambda * Vds), for Vds < Vov
Id = 0.5 * beta * Vov^2 * (1 + lambda * Vds), otherwise
```

## Fitting Error Metrics

- RMSE current: `1.84745e-18 A`
- RMSE log10 current: `5.727431010098717e-15`
- Max absolute current error: `2.81893e-18 A`
- Normalized RMSE current: `6.10728e-16`
- Optimizer status: `\`gtol\` termination condition is satisfied.`

## Generated Artifacts

- Plot: [`mosfet_id_vgs_fit_linear.png`](mosfet_id_vgs_fit_linear.png)
- Plot: [`mosfet_id_vgs_fit_semilog.png`](mosfet_id_vgs_fit_semilog.png)
- SPICE netlist: [`mosfet_id_vgs_validation.cir`](mosfet_id_vgs_validation.cir)

## ngspice Validation

- Max absolute Python-vs-ngspice current difference: `5.01e-12 A`
- RMSE Python-vs-ngspice current difference: `2.89252e-12 A`
- RMSE log10 current difference: `5.727431010098717e-15`

## Interpretation

This report records a simple Level-1 MOSFET transfer-curve fit. Read the fitted Vth and beta inside the measured Vgs range and at the fixed Vds used for this run.

## Limitations

- The Level-1/square-law MOSFET model is simplified.
- Subthreshold conduction is ignored in M2.
- Vth is extraction-method-dependent, not a hard turn-on point.
- beta is an effective fitted parameter, not necessarily a direct process parameter.
- ngspice validation uses a normalized W/L mapping.
- Validation checks implementation consistency, not physical accuracy against a real fabricated device.
