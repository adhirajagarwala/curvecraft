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

CurveCraft can compare parsed ngspice sweep output with the Python diode model evaluated at the same voltages. This validates that the generated SPICE model behaves like the fitted Python model for the chosen sweep.

This still does not prove the original CSV data is perfect. Mismatch can come from parameter mapping, current sign convention, sweep setup, numerical settings, or model assumptions.

M1 validation does not generate final engineering reports; report generation is a separate step.

## M2 MOSFET Id-Vgs Validation

CurveCraft M2 can also generate an ngspice LEVEL=1 NMOS netlist for Id-Vgs
transfer-curve validation at fixed Vds. This checks implementation consistency
between the Python Level-1 model and ngspice's LEVEL=1 model. It does not prove
that the fitted model is physically true for a real MOSFET.

### MOSFET Parameter Mapping

CurveCraft stores M2 MOSFET parameters with explicit names:

| CurveCraft name | Meaning | ngspice LEVEL=1 parameter |
| --- | --- | --- |
| `vth_v` | threshold voltage, volts | `VTO` |
| `beta_a_per_v2` | effective beta in A/V^2 | `KP` |
| `lambda_1_per_v` | channel-length modulation in 1/V | `LAMBDA` |
| `vds_v` | fixed drain-source voltage, volts | drain supply voltage |

The Python model uses:

```text
Id_sat = 0.5 * beta * (Vgs - Vth)^2
```

For M2, CurveCraft maps `beta_a_per_v2` directly to `KP` and uses a normalized
MOSFET instance with `W=1` and `L=1`:

```spice
M1 drain gate 0 0 curve_nmos W=1 L=1
.model curve_nmos NMOS (LEVEL=1 VTO=<volts> KP=<A/V^2> LAMBDA=<1/V>)
```

This normalized W/L convention is deliberate. M2 is not extracting physical
geometry, oxide capacitance, mobility, or a foundry-grade model.

### MOSFET DC Sweep Netlist

The M2 validation circuit is intentionally plain:

- `Vds`, a fixed drain-source voltage source from drain to ground
- `Vgs`, a gate-source voltage source from gate to ground
- `M1`, an NMOS with drain at `drain`, gate at `gate`, source/body at ground
- a `.dc` sweep over `Vgs`
- a `.print` line for `v(gate)` and `i(Vds)`

As with the diode validation, ngspice's voltage-source current convention is
handled explicitly when parsing the output.
