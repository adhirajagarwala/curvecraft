"""Diode I-V parameter fitting."""

from dataclasses import dataclass

import numpy as np
import pandas as pd
import scipy.optimize

from curvecraft.fitting.metrics import (
    max_abs_current_error,
    rmse_current,
    rmse_log10_current,
)
from curvecraft.models.diode import DiodeParameters, diode_current


class DiodeFitError(RuntimeError):
    """Raised when diode fitting cannot produce a usable result."""


@dataclass(frozen=True)
class DiodeFitMetrics:
    """Error metrics for a fitted diode model."""

    rmse_current_a: float
    rmse_log10_current: float
    max_abs_current_error_a: float


@dataclass(frozen=True)
class DiodeFitResult:
    """Result from fitting M1 diode parameters."""

    parameters: DiodeParameters
    success: bool
    message: str
    metrics: DiodeFitMetrics
    optimizer_cost: float
    optimizer_nfev: int
    total_points: int
    positive_current_points: int


def fit_diode_iv(
    data: pd.DataFrame,
    *,
    temperature_k: float = 300.0,
    min_positive_points: int = 3,
) -> DiodeFitResult:
    """Fit diode parameters Is, n, and Rs from loaded diode I-V data.

    The objective uses log10-current residuals for positive measured-current
    points. Nonpositive current rows are intentionally excluded from the fit,
    but they remain part of the returned linear-current error metrics.
    """
    voltage = data["voltage_v"].to_numpy(dtype=float)
    measured_current = data["current_a"].to_numpy(dtype=float)
    positive_mask = measured_current > 0
    positive_points = int(np.count_nonzero(positive_mask))
    if positive_points < min_positive_points:
        raise ValueError(
            "Diode fitting requires at least "
            f"{min_positive_points} positive-current points; got {positive_points}."
        )

    fit_voltage = voltage[positive_mask]
    fit_current = measured_current[positive_mask]
    log_fit_current = np.log10(fit_current)

    def residuals(variables: np.ndarray) -> np.ndarray:
        log10_is, ideality_factor, series_resistance = variables
        parameters = DiodeParameters(
            saturation_current_a=10.0**log10_is,
            ideality_factor=float(ideality_factor),
            series_resistance_ohm=float(series_resistance),
            temperature_k=temperature_k,
        )
        predicted = diode_current(fit_voltage, parameters)
        predicted = np.maximum(predicted, np.finfo(float).tiny)
        return np.log10(predicted) - log_fit_current

    initial_guess = np.array([-12.0, 1.6, 1.0])
    lower_bounds = np.array([-18.0, 1.0, 0.0])
    upper_bounds = np.array([-3.0, 3.0, 1_000.0])

    optimizer_result = scipy.optimize.least_squares(
        residuals,
        initial_guess,
        bounds=(lower_bounds, upper_bounds),
        loss="soft_l1",
    )
    if not optimizer_result.success:
        raise DiodeFitError(f"Diode fit failed: {optimizer_result.message}")

    log10_is, ideality_factor, series_resistance = optimizer_result.x
    parameters = DiodeParameters(
        saturation_current_a=10.0**float(log10_is),
        ideality_factor=float(ideality_factor),
        series_resistance_ohm=float(series_resistance),
        temperature_k=temperature_k,
    )
    predicted_current = diode_current(voltage, parameters)
    metrics = DiodeFitMetrics(
        rmse_current_a=rmse_current(measured_current, predicted_current),
        rmse_log10_current=rmse_log10_current(measured_current, predicted_current),
        max_abs_current_error_a=max_abs_current_error(
            measured_current,
            predicted_current,
        ),
    )

    return DiodeFitResult(
        parameters=parameters,
        success=bool(optimizer_result.success),
        message=str(optimizer_result.message),
        metrics=metrics,
        optimizer_cost=float(optimizer_result.cost),
        optimizer_nfev=int(optimizer_result.nfev),
        total_points=int(len(data)),
        positive_current_points=positive_points,
    )
