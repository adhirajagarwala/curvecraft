# M1 Diode I-V Fit Report

## Experiment Question

How well does a Shockley diode model with series resistance fit this diode I-V curve?

## Input Data

- CSV: `../../../data/examples/diode_basic.csv`
- Total rows: 6
- Positive-current rows used for log fit: 5

## Fitted Parameters

- Is: `1.09488e-10 A`
- n: `1.69631`
- Rs: `3.12551e-08 ohm`
- Temperature assumption: `300 K`

## Model Equation

For `Rs = 0`, CurveCraft uses:

```text
I = Is * (exp(V / (n * Vt)) - 1)
```

For `Rs > 0`, CurveCraft solves the implicit equation:

```text
I = Is * (exp((V - I * Rs) / (n * Vt)) - 1)
```

## Fitting Error Metrics

- RMSE current: `8.31862e-08 A`
- RMSE log10 current: `0.0119348`
- Max absolute current error: `2.03744e-07 A`
- Optimizer status: `\`gtol\` termination condition is satisfied.`

## Generated Artifacts

- Plot: [`diode_fit_linear.png`](diode_fit_linear.png)
- Plot: [`diode_fit_semilog.png`](diode_fit_semilog.png)
- SPICE netlist: [`diode_validation.cir`](diode_validation.cir)

## ngspice Validation

- Max absolute Python-vs-ngspice current difference: `5.27556e-08 A`
- RMSE Python-vs-ngspice current difference: `2.16106e-08 A`
- RMSE log10 current difference: `0.02813004592674843`

## Interpretation

This report summarizes a compact diode fit for the provided I-V data. The fitted parameters should be interpreted within the measured voltage/current range and the fixed-temperature M1 assumption.

## Limitations

- Shockley plus series resistance is a compact approximation.
- Fit quality depends on CSV quality and voltage/current range.
- Temperature is assumed fixed in M1.
- ngspice validation checks implementation consistency, not truth against a physical device.
- SPICE/Python mismatch can come from current sign convention, parameter mapping, sweep setup, numerical settings, or model assumptions.
