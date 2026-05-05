import numpy as np
import pytest

from curvecraft.models import DiodeParameters, diode_current, thermal_voltage


def test_package_level_model_import() -> None:
    parameters = DiodeParameters(
        saturation_current_a=1e-12,
        ideality_factor=1.8,
    )

    assert parameters.saturation_current_a == 1e-12


def test_thermal_voltage_near_room_temperature_value() -> None:
    np.testing.assert_allclose(thermal_voltage(300.0), 0.02585, rtol=1e-3)


def test_thermal_voltage_rejects_nonfinite_temperature() -> None:
    with pytest.raises(ValueError, match="temperature_k must be finite"):
        thermal_voltage(float("nan"))


def test_diode_parameters_reject_nonfinite_values() -> None:
    with pytest.raises(ValueError, match="saturation_current_a must be finite"):
        DiodeParameters(saturation_current_a=float("nan"), ideality_factor=1.5)

    with pytest.raises(ValueError, match="ideality_factor must be finite"):
        DiodeParameters(saturation_current_a=1e-12, ideality_factor=float("inf"))

    with pytest.raises(ValueError, match="series_resistance_ohm must be finite"):
        DiodeParameters(
            saturation_current_a=1e-12,
            ideality_factor=1.5,
            series_resistance_ohm=float("nan"),
        )

    with pytest.raises(ValueError, match="temperature_k must be finite"):
        DiodeParameters(
            saturation_current_a=1e-12,
            ideality_factor=1.5,
            temperature_k=float("inf"),
        )


def test_forward_current_is_monotonic_increasing() -> None:
    parameters = DiodeParameters(
        saturation_current_a=1e-12,
        ideality_factor=1.6,
    )
    voltage = np.linspace(0.0, 0.7, 20)

    current = diode_current(voltage, parameters)

    assert np.all(np.diff(current) > 0)


def test_reverse_bias_current_is_limited_by_saturation_current() -> None:
    parameters = DiodeParameters(
        saturation_current_a=1e-12,
        ideality_factor=1.5,
    )
    voltage = np.array([-1.0, -0.8, -0.6])

    current = diode_current(voltage, parameters)

    np.testing.assert_allclose(current, -1e-12, rtol=0.0, atol=1e-18)


def test_series_resistance_reduces_high_forward_current() -> None:
    no_resistance = DiodeParameters(
        saturation_current_a=1e-12,
        ideality_factor=1.6,
        series_resistance_ohm=0.0,
    )
    with_resistance = DiodeParameters(
        saturation_current_a=1e-12,
        ideality_factor=1.6,
        series_resistance_ohm=25.0,
    )
    voltage = np.array([0.8])

    assert diode_current(voltage, with_resistance)[0] < diode_current(
        voltage,
        no_resistance,
    )[0]
