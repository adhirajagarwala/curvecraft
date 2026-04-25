import shutil
from pathlib import Path

import numpy as np
import pytest

from curvecraft.models import DiodeParameters, MosfetLevel1Parameters
from curvecraft.spice import (
    parse_mosfet_id_vds_ngspice_output_file,
    parse_mosfet_id_vgs_ngspice_output_file,
    parse_ngspice_dc_output_file,
    validate_diode_against_ngspice_results,
    validate_diode_with_ngspice,
    validate_mosfet_id_vds_against_ngspice_results,
    validate_mosfet_id_vds_with_ngspice,
    validate_mosfet_id_vgs_against_ngspice_results,
    validate_mosfet_id_vgs_with_ngspice,
)


def test_validate_diode_against_fixture_data_and_create_plot(tmp_path) -> None:  # type: ignore[no-untyped-def]
    fixture = (
        Path(__file__).parent
        / "fixtures"
        / "ngspice"
        / "diode_dc_output_model_match.txt"
    )
    parsed = parse_ngspice_dc_output_file(fixture)
    plot_path = tmp_path / "python-vs-ngspice.png"

    result = validate_diode_against_ngspice_results(
        DiodeParameters(
            saturation_current_a=1e-12,
            ideality_factor=1.5,
            series_resistance_ohm=0.0,
        ),
        parsed,
        plot_path=plot_path,
    )

    assert list(result.comparison.columns) == [
        "voltage_v",
        "ngspice_current_a",
        "python_current_a",
        "current_difference_a",
    ]
    assert result.metrics.max_abs_current_difference_a < 1e-18
    assert result.metrics.rmse_current_difference_a < 1e-18
    assert result.metrics.rmse_log10_current_difference is not None
    assert result.plot_path == plot_path
    assert plot_path.exists()
    assert plot_path.stat().st_size > 0


def test_validate_diode_against_results_aligns_by_voltage() -> None:
    parsed = parse_ngspice_dc_output_file(
        Path(__file__).parent
        / "fixtures"
        / "ngspice"
        / "diode_dc_output_model_match.txt"
    ).sample(frac=1.0, random_state=1)

    result = validate_diode_against_ngspice_results(
        DiodeParameters(
            saturation_current_a=1e-12,
            ideality_factor=1.5,
            series_resistance_ohm=0.0,
        ),
        parsed,
    )

    assert np.all(np.diff(result.comparison["voltage_v"]) >= 0)


def test_validate_mosfet_id_vgs_against_fixture_data_and_create_plot(
    tmp_path,
) -> None:  # type: ignore[no-untyped-def]
    fixture = (
        Path(__file__).parent
        / "fixtures"
        / "ngspice"
        / "mosfet_id_vgs_output_model_match.txt"
    )
    parsed = parse_mosfet_id_vgs_ngspice_output_file(fixture)
    plot_path = tmp_path / "mosfet-python-vs-ngspice.png"

    result = validate_mosfet_id_vgs_against_ngspice_results(
        MosfetLevel1Parameters(vth_v=1.0, beta_a_per_v2=0.002, vds_v=5.0),
        parsed,
        plot_path=plot_path,
    )

    assert list(result.comparison.columns) == [
        "vgs_v",
        "ngspice_current_a",
        "python_current_a",
        "current_difference_a",
    ]
    assert result.metrics.max_abs_current_difference_a < 1e-18
    assert result.metrics.rmse_current_difference_a < 1e-18
    assert result.metrics.rmse_log10_current_difference is not None
    assert result.plot_path == plot_path
    assert plot_path.exists()
    assert plot_path.stat().st_size > 0


def test_validate_mosfet_id_vgs_against_results_aligns_by_vgs() -> None:
    parsed = parse_mosfet_id_vgs_ngspice_output_file(
        Path(__file__).parent
        / "fixtures"
        / "ngspice"
        / "mosfet_id_vgs_output_model_match.txt"
    ).sample(frac=1.0, random_state=1)

    result = validate_mosfet_id_vgs_against_ngspice_results(
        MosfetLevel1Parameters(vth_v=1.0, beta_a_per_v2=0.002, vds_v=5.0),
        parsed,
    )

    assert np.all(np.diff(result.comparison["vgs_v"]) >= 0)


def test_validate_mosfet_id_vds_against_fixture_data_and_create_plot(
    tmp_path,
) -> None:  # type: ignore[no-untyped-def]
    fixture = (
        Path(__file__).parent
        / "fixtures"
        / "ngspice"
        / "mosfet_id_vds_output_model_match.txt"
    )
    parsed = parse_mosfet_id_vds_ngspice_output_file(fixture, fixed_vgs_v=2.0)
    plot_path = tmp_path / "mosfet-id-vds-python-vs-ngspice.png"

    result = validate_mosfet_id_vds_against_ngspice_results(
        MosfetLevel1Parameters(vth_v=1.0, beta_a_per_v2=0.002),
        parsed,
        plot_path=plot_path,
    )

    assert list(result.comparison.columns) == [
        "vgs_v",
        "vds_v",
        "ngspice_current_a",
        "python_current_a",
        "current_difference_a",
    ]
    assert result.metrics.max_abs_current_difference_a < 1e-18
    assert result.metrics.rmse_current_difference_a < 1e-18
    assert result.metrics.rmse_log10_current_difference is not None
    assert result.plot_path == plot_path
    assert plot_path.exists()
    assert plot_path.stat().st_size > 0


def test_validate_mosfet_id_vds_against_results_aligns_by_vgs_then_vds() -> None:
    parsed = parse_mosfet_id_vds_ngspice_output_file(
        Path(__file__).parent
        / "fixtures"
        / "ngspice"
        / "mosfet_id_vds_output_model_match.txt",
        fixed_vgs_v=2.0,
    ).sample(frac=1.0, random_state=1)

    result = validate_mosfet_id_vds_against_ngspice_results(
        MosfetLevel1Parameters(vth_v=1.0, beta_a_per_v2=0.002),
        parsed,
    )

    assert result.comparison["vgs_v"].tolist() == [2.0, 2.0, 2.0, 2.0]
    assert np.all(np.diff(result.comparison["vds_v"]) >= 0)


@pytest.mark.skipif(shutil.which("ngspice") is None, reason="ngspice is not installed")
def test_validate_diode_with_ngspice_integration_when_available(tmp_path) -> None:  # type: ignore[no-untyped-def]
    result = validate_diode_with_ngspice(
        DiodeParameters(
            saturation_current_a=1e-12,
            ideality_factor=1.5,
            series_resistance_ohm=0.0,
        ),
        tmp_path,
        start_v=-0.1,
        stop_v=0.2,
        step_v=0.1,
        plot_path=tmp_path / "validation.png",
    )

    assert result.ngspice_run is not None
    assert result.plot_path is not None
    assert result.plot_path.exists()


@pytest.mark.skipif(shutil.which("ngspice") is None, reason="ngspice is not installed")
def test_validate_mosfet_id_vgs_with_ngspice_integration_when_available(
    tmp_path,
) -> None:  # type: ignore[no-untyped-def]
    result = validate_mosfet_id_vgs_with_ngspice(
        MosfetLevel1Parameters(vth_v=1.0, beta_a_per_v2=0.002, vds_v=5.0),
        tmp_path,
        start_v=0.0,
        stop_v=2.0,
        step_v=0.5,
        plot_path=tmp_path / "mosfet-validation.png",
    )

    assert result.ngspice_run is not None
    assert result.plot_path is not None
    assert result.plot_path.exists()


@pytest.mark.skipif(shutil.which("ngspice") is None, reason="ngspice is not installed")
def test_validate_mosfet_id_vds_with_ngspice_integration_when_available(
    tmp_path,
) -> None:  # type: ignore[no-untyped-def]
    result = validate_mosfet_id_vds_with_ngspice(
        MosfetLevel1Parameters(vth_v=1.0, beta_a_per_v2=0.002),
        tmp_path,
        fixed_vgs_values_v=(2.0,),
        start_v=0.0,
        stop_v=1.0,
        step_v=0.5,
        plot_path=tmp_path / "mosfet-id-vds-validation.png",
    )

    assert result.ngspice_run is not None
    assert result.plot_path is not None
    assert result.plot_path.exists()
