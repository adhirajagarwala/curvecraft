"""Markdown report generation for M1 diode fitting."""

from os import PathLike
from pathlib import Path

from curvecraft.fitting import DiodeFitResult
from curvecraft.spice.validation import SpiceValidationResult

DEFAULT_EXPERIMENT_QUESTION = (
    "How well does a Shockley diode model with series resistance fit this "
    "diode I-V curve?"
)


def write_diode_report(
    path: str | PathLike[str],
    *,
    input_csv_path: str | PathLike[str],
    fit_result: DiodeFitResult,
    plot_paths: list[str | PathLike[str]] | None = None,
    spice_netlist_path: str | PathLike[str] | None = None,
    validation_result: SpiceValidationResult | None = None,
    experiment_question: str = DEFAULT_EXPERIMENT_QUESTION,
) -> Path:
    """Write a Markdown engineering report for one M1 diode fitting run."""
    report_path = Path(path)
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(
        _render_diode_report(
            report_path=report_path,
            input_csv_path=Path(input_csv_path),
            fit_result=fit_result,
            plot_paths=[Path(plot) for plot in plot_paths or []],
            spice_netlist_path=Path(spice_netlist_path)
            if spice_netlist_path is not None
            else None,
            validation_result=validation_result,
            experiment_question=experiment_question,
        ),
        encoding="utf-8",
    )
    return report_path


def _render_diode_report(
    *,
    report_path: Path,
    input_csv_path: Path,
    fit_result: DiodeFitResult,
    plot_paths: list[Path],
    spice_netlist_path: Path | None,
    validation_result: SpiceValidationResult | None,
    experiment_question: str,
) -> str:
    parameters = fit_result.parameters
    lines = [
        "# M1 Diode I-V Fit Report",
        "",
        "## Experiment Question",
        "",
        experiment_question,
        "",
        "## Input Data",
        "",
        f"- CSV: `{_relative_path(input_csv_path, report_path.parent)}`",
        f"- Total rows: {fit_result.total_points}",
        (
            "- Positive-current rows used for log fit: "
            f"{fit_result.positive_current_points}"
        ),
        "",
        "## Fitted Parameters",
        "",
        f"- Is: `{parameters.saturation_current_a:.6g} A`",
        f"- n: `{parameters.ideality_factor:.6g}`",
        f"- Rs: `{parameters.series_resistance_ohm:.6g} ohm`",
        f"- Temperature assumption: `{parameters.temperature_k:.6g} K`",
        "",
        "## Model Equation",
        "",
        "For `Rs = 0`, CurveCraft uses:",
        "",
        "```text",
        "I = Is * (exp(V / (n * Vt)) - 1)",
        "```",
        "",
        "For `Rs > 0`, CurveCraft solves the implicit equation:",
        "",
        "```text",
        "I = Is * (exp((V - I * Rs) / (n * Vt)) - 1)",
        "```",
        "",
        "## Fitting Error Metrics",
        "",
        f"- RMSE current: `{fit_result.metrics.rmse_current_a:.6g} A`",
        f"- RMSE log10 current: `{fit_result.metrics.rmse_log10_current:.6g}`",
        (
            "- Max absolute current error: "
            f"`{fit_result.metrics.max_abs_current_error_a:.6g} A`"
        ),
        f"- Optimizer status: `{_inline_code(fit_result.message)}`",
        "",
        "## Generated Artifacts",
        "",
    ]
    lines.extend(_artifact_lines(report_path.parent, plot_paths, spice_netlist_path))
    lines.extend(_validation_lines(validation_result))
    lines.extend(
        [
            "## Interpretation",
            "",
            (
                "This report records one compact diode fit for the provided "
                "I-V data. Read the parameters inside the measured voltage "
                "and current range, and keep the fixed-temperature M1 "
                "assumption in mind."
            ),
            "",
            "## Limitations",
            "",
            "- Shockley plus series resistance is a compact approximation.",
            "- Fit quality depends on CSV quality and voltage/current range.",
            "- Temperature is assumed fixed in M1.",
            (
                "- ngspice validation checks implementation consistency, not truth "
                "against a physical device."
            ),
            (
                "- SPICE/Python mismatch can come from current sign convention, "
                "parameter mapping, sweep setup, numerical settings, or model "
                "assumptions."
            ),
            "",
        ]
    )
    return "\n".join(lines)


def _artifact_lines(
    report_dir: Path,
    plot_paths: list[Path],
    spice_netlist_path: Path | None,
) -> list[str]:
    lines: list[str] = []
    if plot_paths:
        for plot_path in plot_paths:
            relative = _relative_path(plot_path, report_dir)
            lines.append(f"- Plot: [`{relative}`]({relative})")
    else:
        lines.append("- Plots: not provided")
    if spice_netlist_path is None:
        lines.append("- SPICE netlist: not provided")
    else:
        relative = _relative_path(spice_netlist_path, report_dir)
        lines.append(f"- SPICE netlist: [`{relative}`]({relative})")
    lines.append("")
    return lines


def _validation_lines(validation_result: SpiceValidationResult | None) -> list[str]:
    lines = ["## ngspice Validation", ""]
    if validation_result is None:
        lines.extend(
            [
                "ngspice validation was not provided for this report.",
                "",
            ]
        )
        return lines

    metrics = validation_result.metrics
    lines.extend(
        [
            (
                "- Max absolute Python-vs-ngspice current difference: "
                f"`{metrics.max_abs_current_difference_a:.6g} A`"
            ),
            (
                "- RMSE Python-vs-ngspice current difference: "
                f"`{metrics.rmse_current_difference_a:.6g} A`"
            ),
            (
                "- RMSE log10 current difference: "
                f"`{metrics.rmse_log10_current_difference}`"
            ),
            "",
        ]
    )
    return lines


def _relative_path(path: Path, start: Path) -> str:
    try:
        return path.resolve().relative_to(start.resolve()).as_posix()
    except ValueError:
        return Path(
            __import__("os").path.relpath(path.resolve(), start.resolve())
        ).as_posix()


def _inline_code(value: str) -> str:
    return value.replace("`", "\\`")
