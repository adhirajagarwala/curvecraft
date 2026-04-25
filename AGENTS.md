# AGENTS.md

## Project

This repository is CurveCraft: a software-based semiconductor modeling project.

CurveCraft fits compact semiconductor device models from curve data, validates generated models using ngspice, and produces engineering-readable reports.

The first target is diode I-V fitting. Later targets include MOSFET fitting, datasheet curve extraction, and power-device modeling.

## User background

The project owner is an EE student learning semiconductors seriously from fundamentals. Do not hide physics assumptions. Explain them in docs when relevant.

## Core rules

1. Do not assume missing requirements.
2. If a decision is not specified, choose the smallest reversible implementation and document it.
3. Do not fake experimental, simulation, or benchmark results.
4. Do not invent datasheet data.
5. If using synthetic data, label it clearly as synthetic.
6. If using real data, include provenance in `data/README.md`.
7. Every implemented feature must have tests.
8. Every user-facing feature must have documentation.
9. Every model must state what it captures and what it does not capture.
10. Prefer simple, correct, explainable implementations over clever abstractions.
11. Do not make the project too complicated. Keep workflows streamlined and implement the best practical approach for the current milestone.
12. Write like a human, especially in Markdown files that will be read on GitHub. Keep the tone clear, direct, and technically honest; avoid filler, hype, and obviously generated phrasing.

## Coding standards

- Use Python 3.11+.
- Use a `src/` package layout.
- Use type hints for public functions.
- Use `pytest` for tests.
- Use `ruff` for linting.
- Keep functions small and testable.
- Avoid unnecessary dependencies.
- Do not add web frameworks unless explicitly requested.

## Scientific standards

For every model or fitting method, document:

- equation used
- parameters
- units
- assumptions
- valid operating region
- failure modes
- error metric

## Current milestone

Milestone M1 is diode I-V fitting and ngspice validation.

Do not implement MOSFET support until M1 is complete.

## Required checks before finishing a task

Run:

```bash
pytest
ruff check .
```
