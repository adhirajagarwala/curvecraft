# AGENTS.md

## Project Identity

CurveCraft is a semiconductor compact-model fitting and ngspice validation toolkit. The current completed scope should be diode M1, MOSFET Id-Vgs M2, and MOSFET Id-Vds/Rds_on M3.

The repository should show clean EE learning through tested Python modules, plots, reports, examples, and engineering logs. Keep the public story technically honest: distinguish measured/source data, fitted Python models, and ngspice validation.

## Programming Habits

- Make minimal, focused changes and preserve existing passing behavior.
- Prefer small modules with clear responsibilities.
- Use explicit unit-bearing variable names such as `vgs_v`, `id_a`, `vds_v`, `vth_v`, and `beta_a_per_v2`.
- Use dataclasses or typed result objects for fitting and validation results.
- Keep IO, compact models, fitting, SPICE generation, plotting, report generation, and CLI/demo code separated.
- Add or update tests for behavior changes.
- Run the relevant repo-standard test, lint, and type-check commands before claiming completion.
- Keep generated artifacts out of source control unless the repo intentionally tracks example reports, plots, or demo outputs.
- Write clear errors for invalid data rather than silently coercing questionable data.
- Keep docs technically honest and scoped to what the code actually does.

## Python Quality Expectations

- Use NumPy, pandas, and SciPy idiomatically where they fit the task.
- Avoid hidden global state.
- Avoid broad bare `except` blocks.
- Avoid hardcoded absolute paths.
- Avoid silently taking `abs(current)`.
- Avoid overfitting tests to implementation details.
- Avoid excessive class hierarchies unless clearly justified.
- Avoid untested CLI code.
- Keep functions reasonably small and testable.
- Use type hints where practical.
- Keep ruff, mypy, and pytest passing according to existing repo standards.

## Semiconductor and EE Correctness Habits

- Do not overstate compact-model accuracy.
- Always distinguish measured/source data, fitted Python model output, and ngspice validation output.
- State that ngspice validation checks implementation consistency, not real-world device truth.
- Explain that threshold voltage is extraction-method-dependent, not a magical hard turn-on voltage.
- Explain that Level-1/square-law MOSFET modeling is simplified and not BSIM.
- Preserve current sign conventions and document assumptions.
- Document fixed-temperature and fixed-`vds_v` assumptions where relevant.
- Do not pretend `beta_a_per_v2` is a direct process parameter when using normalized W/L.

## Scope Boundaries

- Keep MOSFET Id-Vds/Rds_on work scoped to the completed M3 educational workflow unless explicitly asked to expand it.
- Do not add pMOS support until explicitly asked.
- Do not add BSIM support until explicitly asked.
- Do not add capacitance, gate charge, switching loss, or thermal models until explicitly asked.
- Do not add datasheet image digitization until explicitly asked.
- Do not add Docker or GitHub Actions unless explicitly asked or already part of a current issue.
- Do not start pdk-cartographer or other roadmap projects inside this repository.
- Do not make generic tutorial-style changes.
- Do not rewrite working M1 diode modules unnecessarily.
