"""Command-line entry points for CurveCraft."""

import argparse
import shutil
from collections.abc import Iterable
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd

from curvecraft.fitting import (
    DiodeFitResult,
    MosfetIdVdsFitResult,
    MosfetIdVgsFitResult,
    RdsonEstimate,
    SqrtIdThresholdEstimate,
    estimate_threshold_by_constant_current,
    estimate_threshold_by_sqrt_id_linear_fit,
    extract_rdson_for_curve,
    fit_diode_iv,
    fit_mosfet_id_vds,
    fit_mosfet_id_vgs,
)
from curvecraft.io.csv_loader import (
    group_mosfet_id_vds_curves_by_vgs,
    load_diode_curve_csv,
    load_mosfet_id_vds_curve_csv,
    load_mosfet_id_vgs_curve_csv,
)
from curvecraft.models import (
    diode_current,
    mosfet_level1_current,
    mosfet_level1_id_vds_current,
)
from curvecraft.plotting import (
    plot_iv_linear,
    plot_iv_semilog_y,
    plot_mosfet_id_vds_family,
    plot_mosfet_id_vds_measured_vs_fit,
    plot_mosfet_id_vgs_linear,
    plot_mosfet_id_vgs_semilog_y,
)
from curvecraft.reports import (
    write_diode_report,
    write_mosfet_id_vds_report,
    write_mosfet_id_vgs_report,
)
from curvecraft.spice import (
    NgspiceNotFoundError,
    validate_diode_with_ngspice,
    validate_mosfet_id_vds_with_ngspice,
    validate_mosfet_id_vgs_with_ngspice,
    write_diode_netlist,
    write_mosfet_id_vds_netlists,
    write_mosfet_id_vgs_netlist,
)
from curvecraft.spice.validation import SpiceValidationResult


@dataclass(frozen=True)
class DiodeDemoResult:
    """Output paths and status from the M1 diode demo."""

    output_dir: Path
    fit_plot_path: Path
    semilog_plot_path: Path
    netlist_path: Path
    report_path: Path
    fit_result: DiodeFitResult
    validation_result: SpiceValidationResult | None
    validation_skipped_reason: str | None


@dataclass(frozen=True)
class MosfetIdVgsDemoResult:
    """Output paths and status from the M2 MOSFET Id-Vgs demo."""

    output_dir: Path
    fit_plot_path: Path
    semilog_plot_path: Path
    netlist_path: Path
    report_path: Path
    fit_result: MosfetIdVgsFitResult
    sqrt_id_estimate: SqrtIdThresholdEstimate
    constant_current_vth_v: float | None
    validation_result: SpiceValidationResult | None
    validation_skipped_reason: str | None


@dataclass(frozen=True)
class MosfetIdVdsDemoResult:
    """Output paths and status from the M3 MOSFET Id-Vds/Rds_on demo."""

    output_dir: Path
    family_plot_path: Path
    fit_plot_path: Path
    netlist_paths: tuple[Path, ...]
    report_path: Path
    fit_result: MosfetIdVdsFitResult
    rdson_estimates: tuple[RdsonEstimate, ...]
    validation_result: SpiceValidationResult | None
    validation_skipped_reason: str | None


def run_diode_demo(
    *,
    data_path: Path | None = None,
    output_dir: Path | None = None,
    run_ngspice_if_available: bool = True,
) -> DiodeDemoResult:
    """Run the full M1 diode workflow on the bundled synthetic example data."""
    project_root = Path(__file__).resolve().parents[2]
    input_csv = data_path or project_root / "data" / "examples" / "diode_iv_example.csv"
    demo_output = output_dir or project_root / "examples" / "diode_basic" / "output"
    demo_output.mkdir(parents=True, exist_ok=True)

    data = load_diode_curve_csv(input_csv)
    fit_result = fit_diode_iv(data)
    voltage = data["voltage_v"].to_numpy(dtype=float)
    measured_current = data["current_a"].to_numpy(dtype=float)
    fitted_current = diode_current(voltage, fit_result.parameters)

    fit_plot = plot_iv_linear(
        voltage,
        measured_current,
        fitted_current,
        demo_output / "diode_fit_linear.png",
    )
    semilog_plot = plot_iv_semilog_y(
        voltage,
        measured_current,
        fitted_current,
        demo_output / "diode_fit_semilog.png",
    )
    netlist = write_diode_netlist(
        demo_output / "diode_validation.cir",
        fit_result.parameters,
        start_v=float(voltage.min()),
        stop_v=float(voltage.max()),
        step_v=_infer_demo_step(voltage),
    )

    validation_result: SpiceValidationResult | None = None
    validation_skipped_reason: str | None = None
    if run_ngspice_if_available and shutil.which("ngspice") is not None:
        try:
            validation_result = validate_diode_with_ngspice(
                fit_result.parameters,
                demo_output,
                start_v=float(voltage.min()),
                stop_v=float(voltage.max()),
                step_v=_infer_demo_step(voltage),
                plot_path=demo_output / "python_vs_ngspice.png",
            )
            validation_result.comparison.to_csv(
                demo_output / "ngspice_validation_comparison.csv",
                index=False,
            )
        except NgspiceNotFoundError as error:
            validation_skipped_reason = str(error)
    else:
        validation_skipped_reason = (
            "ngspice is not installed or validation was disabled."
        )

    report = write_diode_report(
        demo_output / "diode_m1_fit_report.md",
        input_csv_path=input_csv,
        fit_result=fit_result,
        plot_paths=[fit_plot, semilog_plot],
        spice_netlist_path=netlist,
        validation_result=validation_result,
    )

    return DiodeDemoResult(
        output_dir=demo_output,
        fit_plot_path=fit_plot,
        semilog_plot_path=semilog_plot,
        netlist_path=netlist,
        report_path=report,
        fit_result=fit_result,
        validation_result=validation_result,
        validation_skipped_reason=validation_skipped_reason,
    )


def run_mosfet_id_vgs_demo(
    *,
    data_path: Path | None = None,
    output_dir: Path | None = None,
    fixed_vds_v: float | None = None,
    run_ngspice_if_available: bool = True,
    constant_current_target_a: float = 1e-4,
) -> MosfetIdVgsDemoResult:
    """Run the full M2 MOSFET Id-Vgs workflow on bundled synthetic data."""
    project_root = Path(__file__).resolve().parents[2]
    input_csv = (
        data_path
        or project_root / "data" / "examples" / "mosfet_id_vgs_example.csv"
    )
    demo_output = output_dir or project_root / "examples" / "mosfet_id_vgs" / "output"
    demo_output.mkdir(parents=True, exist_ok=True)

    data = load_mosfet_id_vgs_curve_csv(input_csv)
    vds = fixed_vds_v
    if vds is None and "vds_v" in data.columns:
        vds = float(data["vds_v"].iloc[0])

    vgs = data["vgs_v"].to_numpy(dtype=float)
    measured_current = data["id_a"].to_numpy(dtype=float)
    sqrt_id_estimate = estimate_threshold_by_sqrt_id_linear_fit(vgs, measured_current)
    constant_current_vth: float | None
    try:
        constant_current_vth = estimate_threshold_by_constant_current(
            vgs,
            measured_current,
            constant_current_target_a,
        )
    except ValueError:
        constant_current_vth = None

    fit_result = fit_mosfet_id_vgs(data, fixed_vds_v=vds)
    fitted_current = np.asarray(mosfet_level1_current(vgs, fit_result.parameters))

    fit_plot = plot_mosfet_id_vgs_linear(
        vgs,
        measured_current,
        fitted_current,
        demo_output / "mosfet_id_vgs_fit_linear.png",
    )
    semilog_plot = plot_mosfet_id_vgs_semilog_y(
        vgs,
        measured_current,
        fitted_current,
        demo_output / "mosfet_id_vgs_fit_semilog.png",
    )
    netlist = write_mosfet_id_vgs_netlist(
        demo_output / "mosfet_id_vgs_validation.cir",
        fit_result.parameters,
        start_v=float(vgs.min()),
        stop_v=float(vgs.max()),
        step_v=_infer_demo_step(vgs),
    )

    validation_result: SpiceValidationResult | None = None
    validation_skipped_reason: str | None = None
    if run_ngspice_if_available and shutil.which("ngspice") is not None:
        try:
            validation_result = validate_mosfet_id_vgs_with_ngspice(
                fit_result.parameters,
                demo_output,
                start_v=float(vgs.min()),
                stop_v=float(vgs.max()),
                step_v=_infer_demo_step(vgs),
                plot_path=demo_output / "mosfet_python_vs_ngspice.png",
            )
            validation_result.comparison.to_csv(
                demo_output / "mosfet_ngspice_validation_comparison.csv",
                index=False,
            )
        except NgspiceNotFoundError as error:
            validation_skipped_reason = str(error)
    else:
        validation_skipped_reason = (
            "ngspice is not installed or validation was disabled."
        )

    report = write_mosfet_id_vgs_report(
        demo_output / "mosfet_m2_id_vgs_fit_report.md",
        input_csv_path=input_csv,
        fit_result=fit_result,
        plot_paths=[fit_plot, semilog_plot],
        spice_netlist_path=netlist,
        validation_result=validation_result,
        constant_current_target_a=constant_current_target_a,
        constant_current_vth_v=constant_current_vth,
        sqrt_id_estimate=sqrt_id_estimate,
    )

    return MosfetIdVgsDemoResult(
        output_dir=demo_output,
        fit_plot_path=fit_plot,
        semilog_plot_path=semilog_plot,
        netlist_path=netlist,
        report_path=report,
        fit_result=fit_result,
        sqrt_id_estimate=sqrt_id_estimate,
        constant_current_vth_v=constant_current_vth,
        validation_result=validation_result,
        validation_skipped_reason=validation_skipped_reason,
    )


def run_mosfet_id_vds_demo(
    *,
    data_path: Path | None = None,
    output_dir: Path | None = None,
    fixed_vth_v: float | None = None,
    run_ngspice_if_available: bool = True,
) -> MosfetIdVdsDemoResult:
    """Run the full M3 MOSFET Id-Vds/Rds_on workflow on synthetic data."""
    project_root = Path(__file__).resolve().parents[2]
    input_csv = (
        data_path
        or project_root / "data" / "examples" / "mosfet_id_vds_example.csv"
    )
    demo_output = output_dir or project_root / "examples" / "mosfet_id_vds" / "output"
    demo_output.mkdir(parents=True, exist_ok=True)

    data = load_mosfet_id_vds_curve_csv(input_csv)
    fit_result = fit_mosfet_id_vds(data, fixed_vth_v=fixed_vth_v)
    vgs = data["vgs_v"].to_numpy(dtype=float)
    vds = data["vds_v"].to_numpy(dtype=float)
    fitted_current = np.asarray(
        mosfet_level1_id_vds_current(vgs, vds, fit_result.parameters)
    )

    family_plot = plot_mosfet_id_vds_family(
        data,
        demo_output / "mosfet_id_vds_family.png",
    )
    fit_plot = plot_mosfet_id_vds_measured_vs_fit(
        data,
        fitted_current,
        demo_output / "mosfet_id_vds_fit.png",
    )

    curves_by_vgs = group_mosfet_id_vds_curves_by_vgs(data)
    rdson_estimates = _extract_demo_rdson_estimates(curves_by_vgs)
    fixed_vgs_values = tuple(float(value) for value in sorted(curves_by_vgs))
    netlists = write_mosfet_id_vds_netlists(
        demo_output,
        fit_result.parameters,
        fixed_vgs_values_v=fixed_vgs_values,
        start_v=float(data["vds_v"].min()),
        stop_v=float(data["vds_v"].max()),
        step_v=_infer_demo_step(data["vds_v"].to_numpy(dtype=float)),
    )

    validation_result: SpiceValidationResult | None = None
    validation_skipped_reason: str | None = None
    if run_ngspice_if_available and shutil.which("ngspice") is not None:
        try:
            validation_result = validate_mosfet_id_vds_with_ngspice(
                fit_result.parameters,
                demo_output,
                fixed_vgs_values_v=fixed_vgs_values,
                start_v=float(data["vds_v"].min()),
                stop_v=float(data["vds_v"].max()),
                step_v=_infer_demo_step(data["vds_v"].to_numpy(dtype=float)),
                plot_path=demo_output / "mosfet_id_vds_python_vs_ngspice.png",
            )
            validation_result.comparison.to_csv(
                demo_output / "mosfet_id_vds_ngspice_validation_comparison.csv",
                index=False,
            )
        except NgspiceNotFoundError as error:
            validation_skipped_reason = str(error)
    else:
        validation_skipped_reason = (
            "ngspice is not installed or validation was disabled."
        )

    report = write_mosfet_id_vds_report(
        demo_output / "mosfet_m3_id_vds_rdson_report.md",
        input_csv_path=input_csv,
        fit_result=fit_result,
        rdson_estimates=rdson_estimates,
        plot_paths=[family_plot, fit_plot],
        spice_netlist_paths=list(netlists),
        validation_result=validation_result,
        vds_min_v=float(data["vds_v"].min()),
        vds_max_v=float(data["vds_v"].max()),
    )

    return MosfetIdVdsDemoResult(
        output_dir=demo_output,
        family_plot_path=family_plot,
        fit_plot_path=fit_plot,
        netlist_paths=netlists,
        report_path=report,
        fit_result=fit_result,
        rdson_estimates=rdson_estimates,
        validation_result=validation_result,
        validation_skipped_reason=validation_skipped_reason,
    )


def main(argv: list[str] | None = None) -> int:
    """Run the CurveCraft CLI."""
    parser = argparse.ArgumentParser(prog="curvecraft")
    subparsers = parser.add_subparsers(dest="command", required=True)
    demo_parser = subparsers.add_parser("diode-demo")
    demo_parser.add_argument("--data", type=Path, default=None)
    demo_parser.add_argument("--output-dir", type=Path, default=None)
    demo_parser.add_argument("--skip-ngspice", action="store_true")
    mosfet_parser = subparsers.add_parser("mosfet-id-vgs-demo")
    mosfet_parser.add_argument("--data", type=Path, default=None)
    mosfet_parser.add_argument("--output-dir", type=Path, default=None)
    mosfet_parser.add_argument("--fixed-vds", type=float, default=None)
    mosfet_parser.add_argument("--skip-ngspice", action="store_true")
    mosfet_id_vds_parser = subparsers.add_parser("mosfet-id-vds-demo")
    mosfet_id_vds_parser.add_argument("--data", type=Path, default=None)
    mosfet_id_vds_parser.add_argument("--output-dir", type=Path, default=None)
    mosfet_id_vds_parser.add_argument("--fixed-vth", type=float, default=None)
    mosfet_id_vds_parser.add_argument("--skip-ngspice", action="store_true")

    args = parser.parse_args(argv)
    if args.command == "diode-demo":
        diode_result = run_diode_demo(
            data_path=args.data,
            output_dir=args.output_dir,
            run_ngspice_if_available=not args.skip_ngspice,
        )
        print(f"Output directory: {diode_result.output_dir}")
        print(f"Fit plot: {diode_result.fit_plot_path}")
        print(f"Semilog plot: {diode_result.semilog_plot_path}")
        print(f"SPICE netlist: {diode_result.netlist_path}")
        print(f"Report: {diode_result.report_path}")
        print(
            "Fitted parameters: "
            f"Is={diode_result.fit_result.parameters.saturation_current_a:.6g} A, "
            f"n={diode_result.fit_result.parameters.ideality_factor:.6g}, "
            f"Rs={diode_result.fit_result.parameters.series_resistance_ohm:.6g} ohm"
        )
        if diode_result.validation_skipped_reason is not None:
            print(
                "ngspice validation skipped: "
                f"{diode_result.validation_skipped_reason}"
            )
        else:
            print("ngspice validation completed.")
    elif args.command == "mosfet-id-vgs-demo":
        mosfet_result = run_mosfet_id_vgs_demo(
            data_path=args.data,
            output_dir=args.output_dir,
            fixed_vds_v=args.fixed_vds,
            run_ngspice_if_available=not args.skip_ngspice,
        )
        print(f"Output directory: {mosfet_result.output_dir}")
        print(f"Fit plot: {mosfet_result.fit_plot_path}")
        print(f"Semilog plot: {mosfet_result.semilog_plot_path}")
        print(f"SPICE netlist: {mosfet_result.netlist_path}")
        print(f"Report: {mosfet_result.report_path}")
        print(
            "Fitted parameters: "
            f"Vth={mosfet_result.fit_result.parameters.vth_v:.6g} V, "
            f"beta={mosfet_result.fit_result.parameters.beta_a_per_v2:.6g} A/V^2, "
            f"lambda={mosfet_result.fit_result.parameters.lambda_1_per_v:.6g} 1/V, "
            f"Vds={mosfet_result.fit_result.fixed_vds_v:.6g} V"
        )
        if mosfet_result.validation_skipped_reason is not None:
            print(
                "ngspice validation skipped: "
                f"{mosfet_result.validation_skipped_reason}"
            )
        else:
            print("ngspice validation completed.")
    elif args.command == "mosfet-id-vds-demo":
        id_vds_result = run_mosfet_id_vds_demo(
            data_path=args.data,
            output_dir=args.output_dir,
            fixed_vth_v=args.fixed_vth,
            run_ngspice_if_available=not args.skip_ngspice,
        )
        print(f"Output directory: {id_vds_result.output_dir}")
        print(f"Family plot: {id_vds_result.family_plot_path}")
        print(f"Fit plot: {id_vds_result.fit_plot_path}")
        for netlist_path in id_vds_result.netlist_paths:
            print(f"SPICE netlist: {netlist_path}")
        print(f"Report: {id_vds_result.report_path}")
        print(
            "Fitted parameters: "
            f"Vth={id_vds_result.fit_result.parameters.vth_v:.6g} V, "
            f"beta={id_vds_result.fit_result.parameters.beta_a_per_v2:.6g} A/V^2, "
            f"lambda={id_vds_result.fit_result.parameters.lambda_1_per_v:.6g} 1/V"
        )
        for estimate in id_vds_result.rdson_estimates:
            print(
                "Rds_on: "
                f"Vgs={estimate.vgs_v:.6g} V, "
                f"Rds_on={estimate.rds_on_ohm:.6g} ohm"
            )
        if id_vds_result.validation_skipped_reason is not None:
            print(
                "ngspice validation skipped: "
                f"{id_vds_result.validation_skipped_reason}"
            )
        else:
            print("ngspice validation completed.")
    return 0


def _infer_demo_step(voltage: Iterable[float]) -> float:
    unique_voltage = sorted(set(float(value) for value in voltage))
    if len(unique_voltage) < 2:
        return 0.01
    return min(
        stop - start
        for start, stop in zip(unique_voltage, unique_voltage[1:], strict=False)
        if stop > start
    )


def _extract_demo_rdson_estimates(
    curves_by_vgs: dict[float, pd.DataFrame],
) -> tuple[RdsonEstimate, ...]:
    estimates: list[RdsonEstimate] = []
    for vgs_v, curve in sorted(curves_by_vgs.items()):
        try:
            estimates.append(
                extract_rdson_for_curve(
                    curve["vds_v"].to_numpy(dtype=float),
                    curve["id_a"].to_numpy(dtype=float),
                    low_vds_fraction=0.5,
                    vgs_v=float(vgs_v),
                )
            )
        except ValueError:
            continue
    return tuple(estimates)


if __name__ == "__main__":
    raise SystemExit(main())
