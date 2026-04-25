from types import SimpleNamespace

import numpy as np
import pandas as pd
import pytest

import curvecraft.fitting.optimizer as optimizer
from curvecraft.fitting.optimizer import DiodeFitError, fit_diode_iv
from curvecraft.models import DiodeParameters, diode_current


def test_fit_diode_iv_recovers_synthetic_parameters() -> None:
    expected = DiodeParameters(
        saturation_current_a=2e-12,
        ideality_factor=1.7,
        series_resistance_ohm=0.0,
    )
    voltage = np.linspace(0.05, 0.65, 24)
    current = diode_current(voltage, expected)
    data = pd.DataFrame({"voltage_v": voltage, "current_a": current})

    result = fit_diode_iv(data)

    assert result.success
    assert result.positive_current_points == len(data)
    np.testing.assert_allclose(
        result.parameters.saturation_current_a,
        expected.saturation_current_a,
        rtol=0.35,
    )
    np.testing.assert_allclose(
        result.parameters.ideality_factor,
        expected.ideality_factor,
        rtol=0.08,
    )
    assert result.parameters.series_resistance_ohm < 1.0


def test_fit_diode_iv_rejects_insufficient_positive_current_points() -> None:
    data = pd.DataFrame(
        {
            "voltage_v": [-0.2, 0.0, 0.1],
            "current_a": [-1e-12, 0.0, 1e-10],
        }
    )

    with pytest.raises(ValueError, match="positive-current points"):
        fit_diode_iv(data)


def test_fit_diode_iv_counts_nonpositive_points_but_excludes_them_from_fit() -> None:
    parameters = DiodeParameters(
        saturation_current_a=1e-12,
        ideality_factor=1.6,
        series_resistance_ohm=0.0,
    )
    voltage = np.array([-0.2, 0.0, 0.2, 0.3, 0.4, 0.5])
    current = diode_current(voltage, parameters)
    current[0] = -1e-12
    current[1] = 0.0
    data = pd.DataFrame({"voltage_v": voltage, "current_a": current})

    result = fit_diode_iv(data)

    assert result.total_points == 6
    assert result.positive_current_points == 4


def test_fit_diode_iv_optimizer_failure_has_clear_error(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def fake_least_squares(*args: object, **kwargs: object) -> SimpleNamespace:
        return SimpleNamespace(success=False, message="forced failure")

    monkeypatch.setattr(optimizer.scipy.optimize, "least_squares", fake_least_squares)
    data = pd.DataFrame(
        {
            "voltage_v": [0.2, 0.3, 0.4],
            "current_a": [1e-9, 1e-8, 1e-7],
        }
    )

    with pytest.raises(DiodeFitError, match="forced failure"):
        fit_diode_iv(data)
