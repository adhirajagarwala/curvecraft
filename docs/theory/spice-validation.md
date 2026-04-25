# SPICE Validation

CurveCraft M1 exports fitted diode parameters to an ngspice netlist so the Python compact model can later be checked against ngspice using the same parameters and voltage sweep.

This validation checks implementation consistency. It does not prove that the original CSV data is physically perfect or that the fitted compact model is valid outside the measured voltage and current range.

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

The generated validation circuit uses:

- `Vin`, a voltage source from the diode anode to ground
- `D1`, a diode instance from anode to ground
- a `.dc` sweep over `Vin`
- a `.print` line for `v(anode)` and `i(Vin)`

The current reported as `i(Vin)` follows ngspice's voltage-source current convention. Later parsing and validation code must handle that sign convention explicitly instead of silently changing signs.

## M1 Limitations

Issue 6 only generates netlist text. It does not run ngspice, parse ngspice output, compare Python and ngspice currents, or generate final reports.
