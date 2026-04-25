# M3 MOSFET Id-Vds and Rds_on Report

## Experiment Question

How well does a simple Level-1 n-channel MOSFET model fit these Id-Vds output curves, and what low-Vds Rds_on values are extracted?

## Input Data

- CSV: `../../../data/examples/mosfet_id_vds_example.csv`
- Total rows: 11
- Unique Vgs values used: `1 V, 2 V, 3 V`
- Vds sweep range: `0 V to 2 V`

## Fitted Parameters

| Parameter | Value | Status |
| --- | ---: | --- |
| Vth | `1.00001 V` | fitted |
| beta | `0.000999994 A/V^2` | fitted |
| lambda | `7.24592e-06 1/V` | fitted |

## Rds_on Extraction

| Vgs (V) | Rds_on (ohm) | Conductance (S) | Points | Max Vds (V) | RMSE (A) |
| ---: | ---: | ---: | ---: | ---: | ---: |
| 2 | 2000 | 0.0005 | 3 | 1 | 5.89256e-05 |
| 3 | 666.667 | 0.0015 | 3 | 1 | 5.89256e-05 |

## Fitting Error Metrics

- RMSE current: `3.16709e-09 A`
- Max absolute current error: `6.54828e-09 A`
- Normalized RMSE current: `1.58354e-06`
- RMSE log10 current: `2.660276027589144e-06`
- Optimizer status: `\`gtol\` termination condition is satisfied.`

## Generated Artifacts

- Plot: [`mosfet_id_vds_family.png`](mosfet_id_vds_family.png)
- Plot: [`mosfet_id_vds_fit.png`](mosfet_id_vds_fit.png)
- SPICE netlist: [`mosfet_id_vds_vgs_0_1.cir`](mosfet_id_vds_vgs_0_1.cir)
- SPICE netlist: [`mosfet_id_vds_vgs_1_2.cir`](mosfet_id_vds_vgs_1_2.cir)
- SPICE netlist: [`mosfet_id_vds_vgs_2_3.cir`](mosfet_id_vds_vgs_2_3.cir)

## ngspice Validation

- Max absolute Python-vs-ngspice current difference: `3.45172e-09 A`
- RMSE Python-vs-ngspice current difference: `1.28514e-09 A`
- RMSE log10 current difference: `4.941564564574041e-07`

## Interpretation

This report summarizes a simple Level-1 MOSFET output-curve fit and low-Vds Rds_on extraction. Interpret the fitted parameters and Rds_on values only over the measured Vgs/Vds range and under the fixed assumptions represented by the CSV.

## Limitations

- The Level-1/square-law MOSFET model is simplified.
- Rds_on depends on Vgs, temperature, and device/package details.
- Extracted Rds_on here is based on the low-Vds slope of the input curves.
- beta/KP is an effective fitted parameter under normalized W/L.
- lambda is a simple channel-length modulation approximation.
- ngspice validation checks implementation consistency, not physical truth.
- This is not BSIM or production-grade model extraction.
