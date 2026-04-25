# MOSFET Level-1 Id-Vgs Model

CurveCraft M2 uses a deliberately small n-channel enhancement MOSFET model for
transfer curves at fixed drain-source voltage. The goal is to make the model
easy to inspect and useful for learning, not to replace production MOSFET
compact models.

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

## Limitations

This is an educational Level-1 / square-law compact model. It ignores
subthreshold conduction, body effect, capacitance, gate charge, temperature
dependence, velocity saturation, self-heating, and switching behavior. It is
not BSIM and should not be treated as a production MOSFET model.

M2 covers Id-Vgs transfer-curve evaluation only. It does not add Id-Vds fitting,
p-channel devices, SPICE netlists, reports, or datasheet digitization.
