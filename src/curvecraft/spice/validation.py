"""Validate CurveCraft's Python compact models against ngspice results."""

from dataclasses import dataclass
from os import PathLike
from pathlib import Path

import numpy as np
import pandas as pd

from curvecraft.fitting.metrics import rmse_current, rmse_log10_current
from curvecraft.models import (
    DiodeParameters,
    MosfetLevel1Parameters,
    diode_current,
    mosfet_level1_current,
)
from curvecraft.plotting import plot_mosfet_id_vgs_linear, plot_python_vs_ngspice
from curvecraft.spice.netlist_writer import (
    write_diode_netlist,
    write_mosfet_id_vgs_netlist,
)
from curvecraft.spice.ngspice_parser import (
    parse_mosfet_id_vgs_ngspice_output_file,
    parse_ngspice_dc_output_file,
)
from curvecraft.spice.ngspice_runner import NgspiceRunResult, run_ngspice


@dataclass(frozen=True)
class SpiceValidationMetrics:
    """Comparison metrics between Python and ngspice diode currents."""

    max_abs_current_difference_a: float
    rmse_current_difference_a: float
    rmse_log10_current_difference: float | None


@dataclass(frozen=True)
class SpiceValidationResult:
    """Structured result for Python-vs-ngspice diode validation."""

    comparison: pd.DataFrame
    metrics: SpiceValidationMetrics
    plot_path: Path | None = None
    ngspice_run: NgspiceRunResult | None = None


def validate_diode_against_ngspice_results(
    parameters: DiodeParameters,
    ngspice_results: pd.DataFrame,
    *,
    plot_path: str | PathLike[str] | None = None,
) -> SpiceValidationResult:
    """Compare Python diode current against parsed ngspice sweep results."""
    required_columns = {"voltage_v", "current_a"}
    missing = required_columns.difference(ngspice_results.columns)
    if missing:
        raise ValueError(
            f"ngspice results missing required column(s): {sorted(missing)}"
        )

    comparison = ngspice_results.loc[:, ["voltage_v", "current_a"]].copy()
    comparison = comparison.sort_values("voltage_v").reset_index(drop=True)
    comparison["python_current_a"] = diode_current(
        comparison["voltage_v"].to_numpy(dtype=float),
        parameters,
    )
    comparison = comparison.rename(columns={"current_a": "ngspice_current_a"})
    comparison["current_difference_a"] = (
        comparison["python_current_a"] - comparison["ngspice_current_a"]
    )

    log_rmse: float | None
    if np.any(
        (comparison["python_current_a"].to_numpy() > 0)
        & (comparison["ngspice_current_a"].to_numpy() > 0)
    ):
        log_rmse = rmse_log10_current(
            comparison["ngspice_current_a"].to_numpy(),
            comparison["python_current_a"].to_numpy(),
        )
    else:
        log_rmse = None

    metrics = SpiceValidationMetrics(
        max_abs_current_difference_a=float(
            np.max(np.abs(comparison["current_difference_a"].to_numpy()))
        ),
        rmse_current_difference_a=rmse_current(
            comparison["ngspice_current_a"].to_numpy(),
            comparison["python_current_a"].to_numpy(),
        ),
        rmse_log10_current_difference=log_rmse,
    )

    saved_plot: Path | None = None
    if plot_path is not None:
        saved_plot = plot_python_vs_ngspice(
            comparison["voltage_v"].to_numpy(),
            comparison["python_current_a"].to_numpy(),
            comparison["ngspice_current_a"].to_numpy(),
            plot_path,
        )

    return SpiceValidationResult(
        comparison=comparison,
        metrics=metrics,
        plot_path=saved_plot,
    )


def validate_diode_with_ngspice(
    parameters: DiodeParameters,
    work_dir: str | PathLike[str],
    *,
    start_v: float = -0.1,
    stop_v: float = 0.8,
    step_v: float = 0.01,
    plot_path: str | PathLike[str] | None = None,
) -> SpiceValidationResult:
    """Generate a netlist, run ngspice, parse output, and compare currents."""
    output_dir = Path(work_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    netlist_path = write_diode_netlist(
        output_dir / "diode_validation.cir",
        parameters,
        start_v=start_v,
        stop_v=stop_v,
        step_v=step_v,
    )
    run_result = run_ngspice(netlist_path, output_dir / "diode_validation.out")
    parsed = parse_ngspice_dc_output_file(run_result.output_path)
    validation = validate_diode_against_ngspice_results(
        parameters,
        parsed,
        plot_path=plot_path,
    )
    return SpiceValidationResult(
        comparison=validation.comparison,
        metrics=validation.metrics,
        plot_path=validation.plot_path,
        ngspice_run=run_result,
    )


def validate_mosfet_id_vgs_against_ngspice_results(
    parameters: MosfetLevel1Parameters,
    ngspice_results: pd.DataFrame,
    *,
    plot_path: str | PathLike[str] | None = None,
) -> SpiceValidationResult:
    """Compare Python MOSFET Id-Vgs current against parsed ngspice results."""
    required_columns = {"vgs_v", "id_a"}
    missing = required_columns.difference(ngspice_results.columns)
    if missing:
        raise ValueError(
            f"MOSFET ngspice results missing required column(s): {sorted(missing)}"
        )

    comparison = ngspice_results.loc[:, ["vgs_v", "id_a"]].copy()
    comparison = comparison.sort_values("vgs_v").reset_index(drop=True)
    comparison["python_current_a"] = mosfet_level1_current(
        comparison["vgs_v"].to_numpy(dtype=float),
        parameters,
    )
    comparison = comparison.rename(columns={"id_a": "ngspice_current_a"})
    comparison["current_difference_a"] = (
        comparison["python_current_a"] - comparison["ngspice_current_a"]
    )

    log_rmse: float | None
    if np.any(
        (comparison["python_current_a"].to_numpy() > 0)
        & (comparison["ngspice_current_a"].to_numpy() > 0)
    ):
        log_rmse = rmse_log10_current(
            comparison["ngspice_current_a"].to_numpy(),
            comparison["python_current_a"].to_numpy(),
        )
    else:
        log_rmse = None

    metrics = SpiceValidationMetrics(
        max_abs_current_difference_a=float(
            np.max(np.abs(comparison["current_difference_a"].to_numpy()))
        ),
        rmse_current_difference_a=rmse_current(
            comparison["ngspice_current_a"].to_numpy(),
            comparison["python_current_a"].to_numpy(),
        ),
        rmse_log10_current_difference=log_rmse,
    )

    saved_plot: Path | None = None
    if plot_path is not None:
        saved_plot = plot_mosfet_id_vgs_linear(
            comparison["vgs_v"].to_numpy(),
            comparison["ngspice_current_a"].to_numpy(),
            comparison["python_current_a"].to_numpy(),
            plot_path,
        )

    return SpiceValidationResult(
        comparison=comparison,
        metrics=metrics,
        plot_path=saved_plot,
    )


def validate_mosfet_id_vgs_with_ngspice(
    parameters: MosfetLevel1Parameters,
    work_dir: str | PathLike[str],
    *,
    start_v: float = 0.0,
    stop_v: float = 5.0,
    step_v: float = 0.05,
    plot_path: str | PathLike[str] | None = None,
) -> SpiceValidationResult:
    """Generate a MOSFET Id-Vgs netlist, run ngspice, parse, and compare."""
    output_dir = Path(work_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    netlist_path = write_mosfet_id_vgs_netlist(
        output_dir / "mosfet_id_vgs_validation.cir",
        parameters,
        start_v=start_v,
        stop_v=stop_v,
        step_v=step_v,
    )
    run_result = run_ngspice(
        netlist_path,
        output_dir / "mosfet_id_vgs_validation.out",
    )
    parsed = parse_mosfet_id_vgs_ngspice_output_file(run_result.output_path)
    validation = validate_mosfet_id_vgs_against_ngspice_results(
        parameters,
        parsed,
        plot_path=plot_path,
    )
    return SpiceValidationResult(
        comparison=validation.comparison,
        metrics=validation.metrics,
        plot_path=validation.plot_path,
        ngspice_run=run_result,
    )
