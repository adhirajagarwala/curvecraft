# 2026-04-25 - MOSFET Id-Vgs fitting

## What I built

M2 adds a narrow MOSFET transfer-curve workflow to CurveCraft. It loads
synthetic n-channel Id-Vgs CSV data, estimates threshold voltage, fits a simple
Level-1 model, makes plots, writes an ngspice LEVEL=1 netlist, optionally runs
ngspice, compares Python and SPICE currents, and writes a Markdown report.

## Why Id-Vgs matters

An Id-Vgs transfer curve shows how drain current changes as gate-source voltage
is swept at a fixed drain-source voltage. It is one of the simplest ways to see
threshold behavior, transconductance trend, and the operating range where a
compact MOSFET model is plausible.

## Model used

CurveCraft M2 uses an n-channel enhancement MOSFET Level-1 / square-law model.
For overdrive `Vov = Vgs - Vth`, current is zero when `Vov <= 0`. Above
threshold, the model uses a triode approximation when `Vds < Vov` and a
saturation approximation otherwise. M2 fixes `lambda = 0` during nonlinear
Id-Vgs fitting for stability.

## What Vth means

Threshold voltage is not a magical hard turn-on point. In CurveCraft M2 it is a
model parameter and an extraction result. A constant-current method and a
sqrt(Id) linearization can give different Vth values because each method asks a
slightly different question of the data.

## What beta means

`beta_a_per_v2` is an effective fitted current scale in A/V^2. It is useful for
matching this simple transfer curve, but it should not be read as a direct
process parameter unless geometry, mobility, oxide capacitance, and measurement
conditions are known and modeled correctly.

## How fitting worked

The fitter uses the threshold extraction helpers for initial guesses, then runs
`scipy.optimize.least_squares` on positive-current points. The objective uses
sqrt-current residuals, which behaves reasonably for square-law transfer data
without over-weighting the largest current points as aggressively as a purely
linear-current objective.

## How ngspice validation worked

CurveCraft writes a normalized ngspice LEVEL=1 NMOS model:

```spice
.model curve_nmos NMOS (LEVEL=1 VTO=<Vth> KP=<beta> LAMBDA=<lambda>)
M1 drain gate 0 0 curve_nmos W=1 L=1
```

The gate source is swept with `.dc Vgs`, the drain is held at fixed Vds, and
the parsed `i(Vds)` current is compared against the Python model at the same
Vgs points.

## What matched

For the bundled synthetic M2 example, the workflow completes end to end and the
Python model agrees closely with the generated ngspice LEVEL=1 model for the
same parameters and sweep.

## What did not match or remains simplified

The M2 model ignores subthreshold conduction, body effect, capacitance, gate
charge, self-heating, velocity saturation, geometry extraction, and BSIM-level
behavior. The ngspice validation checks consistency with the generated model,
not truth against a real datasheet or fabricated device.

## What I learned

The useful part of M2 is not that the model is sophisticated. It is that every
assumption is visible: which columns are loaded, how Vth is estimated, which
parameters are fitted, how Python maps to ngspice, and where the model stops
being physically trustworthy.

## Evidence

- Tests: `pytest`, `ruff check .`, and `mypy src`
- Plots: `docs/reports/m2_mosfet_id_vgs/mosfet_id_vgs_fit_linear.png` and `docs/reports/m2_mosfet_id_vgs/mosfet_id_vgs_fit_semilog.png`
- Report: `docs/reports/m2_mosfet_id_vgs/mosfet_m2_id_vgs_fit_report.md`
- Demo command:

```bash
python -m curvecraft.cli mosfet-id-vgs-demo \
  --data data/examples/mosfet_id_vgs_example.csv \
  --output-dir docs/reports/m2_mosfet_id_vgs
```

## Next steps

Good next steps are review, small usability polish, and then a separately
scoped Id-Vds milestone. p-channel devices, BSIM, capacitance, gate charge,
switching loss, and datasheet digitization should remain separate milestones.
