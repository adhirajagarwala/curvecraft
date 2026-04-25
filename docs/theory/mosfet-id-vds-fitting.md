# MOSFET Id-Vds Fitting

CurveCraft M3 fits a small educational Level-1 n-channel MOSFET model to
Id-Vds output-curve data. The input data uses the long/tidy columns:

```text
vgs_v,vds_v,id_a
```

Each row is one drain-current point at one gate-source voltage and one
drain-source voltage.

## Parameters

Id-Vds output curves can help refine the current scale
`beta_a_per_v2` and the channel-length modulation term `lambda_1_per_v`.
Positive `lambda_1_per_v` causes saturation-region drain current to increase
with `Vds`, which corresponds to finite output resistance in this simplified
model.

`vth_v` can be fitted jointly, but it is often better constrained by Id-Vgs
transfer data. CurveCraft therefore supports using a fixed `vth_v` from an
earlier M2-style transfer-curve fit while fitting `beta_a_per_v2` and
`lambda_1_per_v` from the output curves.

## Fitting Notes

The fitter uses `scipy.optimize.least_squares` with bounded parameters:

- `beta_a_per_v2 > 0`
- `lambda_1_per_v >= 0`
- fitted `vth_v` is bounded relative to the observed `vgs_v` range

Nonnegative-current rows are used in the optimizer. Negative-current rows are
excluded from the objective and recorded in the result notes, while fit metrics
are still computed over the full input data.

## Limitations

This is an educational Level-1 / square-law fit, not BSIM extraction. It does
not add p-channel devices, capacitance, gate charge, switching loss, thermal
modeling, package resistance modeling, or datasheet image digitization. Fit
quality should be interpreted only over the measured voltage range and under
the assumptions represented by the input CSV data.
