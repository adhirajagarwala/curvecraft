"""Command-line entry points for CurveCraft."""

import argparse
import shutil
from collections.abc import Iterable
from dataclasses import dataclass
from pathlib import Path

import numpy as np

from curvecraft.fitting import (
    DiodeFitResult,
    MosfetIdVgsFitResult,
    SqrtIdThresholdEstimate,
    estimate_threshold_by_constant_current,
    estimate_threshold_by_sqrt_id_linear_fit,
    fit_diode_iv,
    fit_mosfet_id_vgs,
)
from curvecraft.io.csv_loader import load_diode_curve_csv, load_mosfet_id_vgs_curve_csv
from curvecraft.models import diode_current, mosfet_level1_current
from curvecraft.plotting import (
    plot_iv_linear,
    plot_iv_semilog_y,
    plot_mosfet_id_vgs_linear,
    plot_mosfet_id_vgs_semilog_y,
)
from curvecraft.reports import write_diode_report, write_mosfet_id_vgs_report
from curvecraft.spice import (
    NgspiceNotFoundError,
    validate_diode_with_ngspice,
    validate_mosfet_id_vgs_with_ngspice,
    write_diode_netlist,
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


if __name__ == "__main__":
    raise SystemExit(main())
