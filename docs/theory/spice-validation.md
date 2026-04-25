# SPICE Validation

CurveCraft M1 exports fitted diode parameters to an ngspice netlist so the Python model can be checked against an independent simulator using the same parameters and voltage sweep.

This is a consistency check. It does not prove that the original CSV data is perfect, and it does not make the fitted model valid outside the measured voltage and current range.

## Parameter Mapping

CurveCraft stores diode parameters with Python names:

| CurveCraft name | Meaning | ngspice diode parameter |
| --- | --- | --- |
| `saturation_current_a` | saturation current `Is`, amps | `IS` |
| `ideality_factor` | ideality factor `n` | `N` |
| `series_resistance_ohm` | series resistance `Rs`, ohms | `RS` |

The generated model card has this shape:

```spice
.model curve_diode D (IS=<amps> N=<unitless> RS=<ohms>)
```

## DC Sweep Netlist

The validation circuit is intentionally plain:

- `Vin`, a voltage source from the diode anode to ground
- `D1`, a diode instance from anode to ground
- a `.dc` sweep over `Vin`
- a `.print` line for `v(anode)` and `i(Vin)`

The current reported as `i(Vin)` follows ngspice's voltage-source current convention. CurveCraft handles that sign convention in one explicit parser step instead of hiding it in the comparison code.

## M1 Limitations

CurveCraft compares parsed ngspice sweep output with the Python diode model evaluated at the same voltages. If they agree, the generated SPICE model is behaving like the fitted Python model for that sweep.

This still does not prove the original CSV data is perfect. Mismatch can come from parameter mapping, current sign convention, sweep setup, numerical settings, or model assumptions.

M1 validation does not generate final engineering reports; report generation is a separate step.
