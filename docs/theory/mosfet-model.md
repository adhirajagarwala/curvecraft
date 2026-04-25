# MOSFET Level-1 Model

CurveCraft M2 uses a deliberately small n-channel enhancement MOSFET model for
Id-Vgs transfer curves at fixed drain-source voltage. The completed M2 workflow
includes this educational Level-1/square-law model, threshold extraction
helpers, nonlinear fitting, measured-vs-fit plots, ngspice validation, and
Markdown reporting. The goal is to make the workflow easy to inspect and useful
for learning, not to replace production MOSFET compact models.

## Parameters

| Parameter | Unit | Meaning |
| --- | --- | --- |
| `vth_v` | volts (V) | Threshold voltage used by this extraction model. |
| `beta_a_per_v2` | amps per volt squared (A/V^2) | Effective transconductance parameter. |
| `lambda_1_per_v` | inverse volts (1/V) | Optional channel-length modulation parameter. |
| `vds_v` | volts (V) | Fixed drain-source voltage for the Id-Vgs transfer curve. |

The overdrive voltage is:

```text
overdrive_v = vgs_v - vth_v
```

If `overdrive_v <= 0`, M2 returns `Id = 0`. That is a modeling choice for this
simple square-law model; real MOSFETs can conduct subthreshold current below
the extracted threshold voltage.

In M2, `vth_v` is an extraction-method-dependent model parameter, not a
magical hard turn-on voltage. `beta_a_per_v2` is an effective fitted parameter
for this simplified model and should not be treated as a direct process
parameter.

## Regions

When `vds_v < overdrive_v`, the model uses a triode-region approximation:

```text
Id = beta * (overdrive_v * vds_v - 0.5 * vds_v^2) * (1 + lambda * vds_v)
```

Otherwise, it uses the saturation approximation:

```text
Id = 0.5 * beta * overdrive_v^2 * (1 + lambda * vds_v)
```

`lambda_1_per_v` gives a simple first-order increase in current with `vds_v`.
For M2 it is optional and defaults to zero.

## ngspice Mapping

For ngspice validation, M2 maps the Python model to a normalized LEVEL=1 NMOS
model:

```spice
.model curve_nmos NMOS (LEVEL=1 VTO=<vth_v> KP=<beta_a_per_v2> LAMBDA=<lambda_1_per_v>)
M1 drain gate 0 0 curve_nmos W=1 L=1
```

The normalized `W=1` and `L=1` mapping is used so the Python `beta_a_per_v2`
matches ngspice `KP` directly for implementation validation. This is not
physical geometry extraction.

## Limitations

This is an educational Level-1 / square-law compact model. It ignores
subthreshold conduction, body effect, capacitance, gate charge, temperature
dependence, velocity saturation, self-heating, and switching behavior. It is
not BSIM and should not be treated as a production MOSFET model.

## M3 Id-Vds Output-Curve Evaluation

M3 extends the same educational equations so CurveCraft can evaluate output
curves as `Id = f(Vgs, Vds)`. An Id-Vgs transfer curve sweeps `Vgs` at fixed
`Vds`; an Id-Vds output curve sweeps `Vds` at a stepped `Vgs`.

For `overdrive_v = vgs_v - vth_v`, the Id-Vds evaluator uses:

```text
Id = 0, for overdrive_v <= 0
Id = beta * (overdrive_v * vds_v - 0.5 * vds_v^2) * (1 + lambda * vds_v),
for vds_v < overdrive_v
Id = 0.5 * beta * overdrive_v^2 * (1 + lambda * vds_v), otherwise
```

The first conducting expression is the triode-region approximation. The second
is the saturation-region approximation. `lambda_1_per_v` gives a simple
channel-length-modulation term, so saturation-region current can still increase
with `vds_v` when lambda is positive.

The M3 evaluator is for nonnegative-drain-voltage n-channel output curves. It
does not add fitting, Rds_on extraction, plotting, SPICE validation, reports,
or a CLI demo in this issue.

M3 remains a simplified Level-1 model, not BSIM. It does not add p-channel
devices, capacitance, gate charge, switching loss, thermal modeling, or
datasheet digitization. ngspice validation checks consistency between the
Python model and generated SPICE model, not truth against a real fabricated
device.
