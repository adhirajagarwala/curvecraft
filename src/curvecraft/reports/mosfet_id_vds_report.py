"""Markdown report generation for M3 MOSFET Id-Vds fitting."""

from os import PathLike
from pathlib import Path

from curvecraft.fitting import MosfetIdVdsFitResult, RdsonEstimate
from curvecraft.spice.validation import SpiceValidationResult

DEFAULT_MOSFET_ID_VDS_EXPERIMENT_QUESTION = (
    "How well does a simple Level-1 n-channel MOSFET model fit these Id-Vds "
    "output curves, and what low-Vds Rds_on values are extracted?"
)


def write_mosfet_id_vds_report(
    path: str | PathLike[str],
    *,
    input_csv_path: str | PathLike[str],
    fit_result: MosfetIdVdsFitResult,
    rdson_estimates: list[RdsonEstimate] | tuple[RdsonEstimate, ...],
    plot_paths: list[str | PathLike[str]] | None = None,
    spice_netlist_paths: list[str | PathLike[str]] | None = None,
    validation_result: SpiceValidationResult | None = None,
    vds_min_v: float | None = None,
    vds_max_v: float | None = None,
    experiment_question: str = DEFAULT_MOSFET_ID_VDS_EXPERIMENT_QUESTION,
) -> Path:
    """Write a Markdown engineering report for one M3 MOSFET Id-Vds run."""
    report_path = Path(path)
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(
        _render_mosfet_id_vds_report(
            report_path=report_path,
            input_csv_path=Path(input_csv_path),
            fit_result=fit_result,
            rdson_estimates=rdson_estimates,
            plot_paths=[Path(plot) for plot in plot_paths or []],
            spice_netlist_paths=[
                Path(netlist) for netlist in spice_netlist_paths or []
            ],
            validation_result=validation_result,
            vds_min_v=vds_min_v,
            vds_max_v=vds_max_v,
            experiment_question=experiment_question,
        ),
        encoding="utf-8",
    )
    return report_path


def _render_mosfet_id_vds_report(
    *,
    report_path: Path,
    input_csv_path: Path,
    fit_result: MosfetIdVdsFitResult,
    rdson_estimates: list[RdsonEstimate] | tuple[RdsonEstimate, ...],
    plot_paths: list[Path],
    spice_netlist_paths: list[Path],
    validation_result: SpiceValidationResult | None,
    vds_min_v: float | None,
    vds_max_v: float | None,
    experiment_question: str,
) -> str:
    parameters = fit_result.parameters
    vds_min, vds_max = _vds_range(validation_result, vds_min_v, vds_max_v)
    lines = [
        "# M3 MOSFET Id-Vds and Rds_on Report",
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
            "- Unique Vgs values used: "
            f"`{', '.join(f'{value:.6g} V' for value in fit_result.unique_vgs_v)}`"
        ),
        f"- Vds sweep range: `{_format_optional_range(vds_min, vds_max)}`",
        "",
        "## Fitted Parameters",
        "",
        "| Parameter | Value | Status |",
        "| --- | ---: | --- |",
        _parameter_row("Vth", f"{parameters.vth_v:.6g} V", fit_result, "vth_v"),
        _parameter_row(
            "beta",
            f"{parameters.beta_a_per_v2:.6g} A/V^2",
            fit_result,
            "beta_a_per_v2",
        ),
        _parameter_row(
            "lambda",
            f"{parameters.lambda_1_per_v:.6g} 1/V",
            fit_result,
            "lambda_1_per_v",
        ),
        "",
        "## Rds_on Extraction",
        "",
    ]
    lines.extend(_rdson_table_lines(rdson_estimates))
    lines.extend(
        [
            "## Fitting Error Metrics",
            "",
            f"- RMSE current: `{fit_result.metrics.rmse_current_a:.6g} A`",
            (
                "- Max absolute current error: "
                f"`{fit_result.metrics.max_abs_current_error_a:.6g} A`"
            ),
            (
                "- Normalized RMSE current: "
                f"`{fit_result.metrics.normalized_rmse_current:.6g}`"
            ),
            (
                "- RMSE log10 current: "
                f"`{fit_result.metrics.rmse_log10_current}`"
            ),
            f"- Optimizer status: `{_inline_code(fit_result.message)}`",
            "",
            "## Generated Artifacts",
            "",
        ]
    )
    lines.extend(_artifact_lines(report_path.parent, plot_paths, spice_netlist_paths))
    lines.extend(_validation_lines(validation_result))
    lines.extend(
        [
            "## Interpretation",
            "",
            (
                "This report summarizes a simple Level-1 MOSFET output-curve "
                "fit and low-Vds Rds_on extraction. Interpret the fitted "
                "parameters and Rds_on values only over the measured Vgs/Vds "
                "range and under the fixed assumptions represented by the CSV."
            ),
            "",
            "## Limitations",
            "",
            "- The Level-1/square-law MOSFET model is simplified.",
            (
                "- Rds_on depends on Vgs, temperature, and device/package "
                "details."
            ),
            (
                "- Extracted Rds_on here is based on the low-Vds slope of the "
                "input curves."
            ),
            (
                "- beta/KP is an effective fitted parameter under normalized "
                "W/L."
            ),
            "- lambda is a simple channel-length modulation approximation.",
            (
                "- ngspice validation checks implementation consistency, not "
                "physical truth."
            ),
            "- This is not BSIM or production-grade model extraction.",
            "",
        ]
    )
    return "\n".join(lines)


def _rdson_table_lines(
    rdson_estimates: list[RdsonEstimate] | tuple[RdsonEstimate, ...],
) -> list[str]:
    if not rdson_estimates:
        return ["Rds_on estimates were not provided.", ""]
    lines = [
        (
            "| Vgs (V) | Rds_on (ohm) | Conductance (S) | Points | "
            "Max Vds (V) | RMSE (A) |"
        ),
        "| ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for estimate in rdson_estimates:
        vgs = "not provided" if estimate.vgs_v is None else f"{estimate.vgs_v:.6g}"
        lines.append(
            f"| {vgs} | {estimate.rds_on_ohm:.6g} | "
            f"{estimate.conductance_siemens:.6g} | "
            f"{estimate.selected_point_count} | "
            f"{estimate.max_selected_vds_v:.6g} | "
            f"{estimate.rmse_current_a:.6g} |"
        )
    lines.append("")
    return lines


def _artifact_lines(
    report_dir: Path,
    plot_paths: list[Path],
    spice_netlist_paths: list[Path],
) -> list[str]:
    lines: list[str] = []
    if plot_paths:
        for plot_path in plot_paths:
            relative = _relative_path(plot_path, report_dir)
            lines.append(f"- Plot: [`{relative}`]({relative})")
    else:
        lines.append("- Plots: not provided")
    if spice_netlist_paths:
        for netlist_path in spice_netlist_paths:
            relative = _relative_path(netlist_path, report_dir)
            lines.append(f"- SPICE netlist: [`{relative}`]({relative})")
    else:
        lines.append("- SPICE netlists: not provided")
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


def _parameter_row(
    name: str,
    value: str,
    fit_result: MosfetIdVdsFitResult,
    parameter_name: str,
) -> str:
    if parameter_name in fit_result.fitted_parameters:
        status = "fitted"
    elif parameter_name in fit_result.fixed_parameters:
        status = "fixed"
    else:
        status = "provided"
    return f"| {name} | `{value}` | {status} |"


def _vds_range(
    validation_result: SpiceValidationResult | None,
    fallback_min_v: float | None,
    fallback_max_v: float | None,
) -> tuple[float | None, float | None]:
    if validation_result is None or "vds_v" not in validation_result.comparison:
        return fallback_min_v, fallback_max_v
    values = validation_result.comparison["vds_v"]
    return float(values.min()), float(values.max())


def _format_optional_range(start_v: float | None, stop_v: float | None) -> str:
    if start_v is None or stop_v is None:
        return "not provided"
    return f"{start_v:.6g} V to {stop_v:.6g} V"


def _relative_path(path: Path, start: Path) -> str:
    try:
        return path.resolve().relative_to(start.resolve()).as_posix()
    except ValueError:
        return Path(
            __import__("os").path.relpath(path.resolve(), start.resolve())
        ).as_posix()


def _inline_code(value: str) -> str:
    return value.replace("`", "\\`")
