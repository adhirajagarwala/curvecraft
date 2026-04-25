"""Markdown report generation for M2 MOSFET Id-Vgs fitting."""

from os import PathLike
from pathlib import Path

from curvecraft.fitting import MosfetIdVgsFitResult, SqrtIdThresholdEstimate
from curvecraft.spice.validation import SpiceValidationResult

DEFAULT_MOSFET_EXPERIMENT_QUESTION = (
    "How well does a simple Level-1 n-channel MOSFET model fit this Id-Vgs "
    "transfer curve at fixed Vds?"
)


def write_mosfet_id_vgs_report(
    path: str | PathLike[str],
    *,
    input_csv_path: str | PathLike[str],
    fit_result: MosfetIdVgsFitResult,
    plot_paths: list[str | PathLike[str]] | None = None,
    spice_netlist_path: str | PathLike[str] | None = None,
    validation_result: SpiceValidationResult | None = None,
    constant_current_target_a: float | None = None,
    constant_current_vth_v: float | None = None,
    sqrt_id_estimate: SqrtIdThresholdEstimate | None = None,
    experiment_question: str = DEFAULT_MOSFET_EXPERIMENT_QUESTION,
) -> Path:
    """Write a Markdown engineering report for one M2 MOSFET Id-Vgs run."""
    report_path = Path(path)
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(
        _render_mosfet_id_vgs_report(
            report_path=report_path,
            input_csv_path=Path(input_csv_path),
            fit_result=fit_result,
            plot_paths=[Path(plot) for plot in plot_paths or []],
            spice_netlist_path=Path(spice_netlist_path)
            if spice_netlist_path is not None
            else None,
            validation_result=validation_result,
            constant_current_target_a=constant_current_target_a,
            constant_current_vth_v=constant_current_vth_v,
            sqrt_id_estimate=sqrt_id_estimate,
            experiment_question=experiment_question,
        ),
        encoding="utf-8",
    )
    return report_path


def _render_mosfet_id_vgs_report(
    *,
    report_path: Path,
    input_csv_path: Path,
    fit_result: MosfetIdVgsFitResult,
    plot_paths: list[Path],
    spice_netlist_path: Path | None,
    validation_result: SpiceValidationResult | None,
    constant_current_target_a: float | None,
    constant_current_vth_v: float | None,
    sqrt_id_estimate: SqrtIdThresholdEstimate | None,
    experiment_question: str,
) -> str:
    parameters = fit_result.parameters
    lines = [
        "# M2 MOSFET Id-Vgs Fit Report",
        "",
        "## Experiment Question",
        "",
        experiment_question,
        "",
        "## Input Data",
        "",
        f"- CSV: `{_relative_path(input_csv_path, report_path.parent)}`",
        f"- Fixed Vds: `{fit_result.fixed_vds_v:.6g} V`",
        f"- Total rows: {fit_result.total_points}",
        f"- Positive-current rows used for fit: {fit_result.used_points}",
        "",
        "## Fitted Parameters",
        "",
        f"- Vth: `{parameters.vth_v:.6g} V`",
        f"- beta: `{parameters.beta_a_per_v2:.6g} A/V^2`",
        (
            "- lambda: "
            f"`{parameters.lambda_1_per_v:.6g} 1/V` "
            "(fixed at 0 for M2 Id-Vgs fitting)"
        ),
        "",
        "## Extraction Method Summary",
        "",
    ]
    lines.extend(
        _extraction_lines(
            constant_current_target_a,
            constant_current_vth_v,
            sqrt_id_estimate,
            fit_result,
        )
    )
    lines.extend(
        [
            "## Model Equation",
            "",
            "For overdrive `Vov = Vgs - Vth`, CurveCraft M2 uses:",
            "",
            "```text",
            "Id = 0, for Vov <= 0",
            "Id = beta * (Vov * Vds - 0.5 * Vds^2) * (1 + lambda * Vds), "
            "for Vds < Vov",
            "Id = 0.5 * beta * Vov^2 * (1 + lambda * Vds), otherwise",
            "```",
            "",
            "## Fitting Error Metrics",
            "",
            f"- RMSE current: `{fit_result.metrics.rmse_current_a:.6g} A`",
            (
                "- RMSE log10 current: "
                f"`{fit_result.metrics.rmse_log10_current}`"
            ),
            (
                "- Max absolute current error: "
                f"`{fit_result.metrics.max_abs_current_error_a:.6g} A`"
            ),
            (
                "- Normalized RMSE current: "
                f"`{fit_result.metrics.normalized_rmse_current:.6g}`"
            ),
            f"- Optimizer status: `{_inline_code(fit_result.message)}`",
            "",
            "## Generated Artifacts",
            "",
        ]
    )
    lines.extend(_artifact_lines(report_path.parent, plot_paths, spice_netlist_path))
    lines.extend(_validation_lines(validation_result))
    lines.extend(
        [
            "## Interpretation",
            "",
            (
                "This report records a simple Level-1 MOSFET transfer-curve fit. "
                "Read the fitted Vth and beta inside the measured Vgs range and "
                "at the fixed Vds used for this run."
            ),
            "",
            "## Limitations",
            "",
            "- The Level-1/square-law MOSFET model is simplified.",
            "- Subthreshold conduction is ignored in M2.",
            "- Vth is extraction-method-dependent, not a hard turn-on point.",
            (
                "- beta is an effective fitted parameter, not necessarily a "
                "direct process parameter."
            ),
            "- ngspice validation uses a normalized W/L mapping.",
            (
                "- Validation checks implementation consistency, not physical "
                "accuracy against a real fabricated device."
            ),
            "",
        ]
    )
    return "\n".join(lines)


def _extraction_lines(
    constant_current_target_a: float | None,
    constant_current_vth_v: float | None,
    sqrt_id_estimate: SqrtIdThresholdEstimate | None,
    fit_result: MosfetIdVgsFitResult,
) -> list[str]:
    lines: list[str] = []
    if constant_current_target_a is not None and constant_current_vth_v is not None:
        lines.append(
            "- Constant-current estimate: "
            f"`Vth = {constant_current_vth_v:.6g} V` at "
            f"`Id = {constant_current_target_a:.6g} A`"
        )
    else:
        lines.append("- Constant-current estimate: not provided")

    if sqrt_id_estimate is not None:
        lines.extend(
            [
                (
                    "- sqrt(Id) linear estimate: "
                    f"`Vth = {sqrt_id_estimate.vth_v:.6g} V`"
                ),
                (
                    "- sqrt(Id) selected points: "
                    f"`{sqrt_id_estimate.selected_point_count}`"
                ),
            ]
        )
    else:
        lines.append("- sqrt(Id) linear estimate: not provided")

    lines.extend(
        [
            (
                "- Final nonlinear fit: "
                f"`Vth = {fit_result.parameters.vth_v:.6g} V`, "
                f"`beta = {fit_result.parameters.beta_a_per_v2:.6g} A/V^2`"
            ),
            "",
        ]
    )
    return lines


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
        lines.extend(["ngspice validation was not provided for this report.", ""])
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
