"""Diode I-V parameter fitting."""

from dataclasses import dataclass
from typing import cast

import numpy as np
import pandas as pd
import scipy.optimize

from curvecraft.fitting.metrics import (
    max_abs_current_error,
    rmse_current,
    rmse_log10_current,
)
from curvecraft.fitting.mosfet_extract import estimate_initial_mosfet_params
from curvecraft.models.diode import DiodeParameters, diode_current
from curvecraft.models.mosfet_level1 import (
    MosfetLevel1Parameters,
    mosfet_level1_current,
)


class DiodeFitError(RuntimeError):
    """Raised when diode fitting cannot produce a usable result."""


class MosfetFitError(RuntimeError):
    """Raised when MOSFET fitting cannot produce a usable result."""


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


@dataclass(frozen=True)
class MosfetIdVgsFitMetrics:
    """Error metrics for a fitted MOSFET Id-Vgs model."""

    rmse_current_a: float
    rmse_log10_current: float | None
    max_abs_current_error_a: float
    normalized_rmse_current: float


@dataclass(frozen=True)
class MosfetIdVgsFitResult:
    """Result from fitting M2 MOSFET Id-Vgs Level-1 parameters."""

    parameters: MosfetLevel1Parameters
    fixed_vds_v: float
    success: bool
    status: int
    message: str
    metrics: MosfetIdVgsFitMetrics
    optimizer_cost: float
    optimizer_nfev: int
    total_points: int
    positive_current_points: int
    used_points: int
    notes: tuple[str, ...]


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
        return cast(np.ndarray, np.log10(predicted) - log_fit_current)

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


def fit_mosfet_id_vgs(
    data: pd.DataFrame,
    *,
    fixed_vds_v: float | None = None,
    min_positive_points: int = 3,
) -> MosfetIdVgsFitResult:
    """Fit M2 n-channel MOSFET Id-Vgs data with a simple Level-1 model.

    M2 fits ``vth_v`` and ``beta_a_per_v2`` only. ``lambda_1_per_v`` is fixed
    at zero to keep the transfer-curve fit stable and technically honest for a
    single fixed-Vds dataset. Nonpositive current rows are excluded from the
    sqrt-current objective but remain part of the returned linear-current
    metrics.
    """
    if "vgs_v" not in data.columns or "id_a" not in data.columns:
        raise ValueError("MOSFET Id-Vgs fitting requires vgs_v and id_a columns.")

    vgs = data["vgs_v"].to_numpy(dtype=float)
    measured_current = data["id_a"].to_numpy(dtype=float)
    if len(vgs) == 0:
        raise ValueError("MOSFET Id-Vgs fitting requires at least one data row.")
    if not np.all(np.isfinite(vgs)) or not np.all(np.isfinite(measured_current)):
        raise ValueError("MOSFET Id-Vgs fitting data must contain finite values.")

    vds = _resolve_fixed_vds(data, fixed_vds_v)
    positive_mask = measured_current > 0
    positive_points = int(np.count_nonzero(positive_mask))
    if positive_points < min_positive_points:
        raise ValueError(
            "MOSFET Id-Vgs fitting requires at least "
            f"{min_positive_points} positive-current points; got {positive_points}."
        )

    fit_vgs = vgs[positive_mask]
    fit_current = measured_current[positive_mask]
    initial = estimate_initial_mosfet_params(fit_vgs, fit_current)

    vgs_min = float(np.min(vgs))
    vgs_max = float(np.max(vgs))
    vgs_span = max(vgs_max - vgs_min, 1.0)
    lower_vth = vgs_min - vgs_span
    upper_vth = vgs_max
    initial_vth = float(np.clip(initial.vth_v, lower_vth, upper_vth))
    initial_log10_beta = float(np.clip(np.log10(initial.beta_a_per_v2), -18.0, 6.0))

    current_scale = max(
        float(np.sqrt(np.max(fit_current))),
        float(np.finfo(float).tiny),
    )

    def residuals(variables: np.ndarray) -> np.ndarray:
        vth_v, log10_beta = variables
        parameters = MosfetLevel1Parameters(
            vth_v=float(vth_v),
            beta_a_per_v2=10.0 ** float(log10_beta),
            lambda_1_per_v=0.0,
            vds_v=vds,
        )
        predicted = np.asarray(mosfet_level1_current(fit_vgs, parameters))
        return cast(
            np.ndarray,
            (np.sqrt(np.maximum(predicted, 0.0)) - np.sqrt(fit_current))
            / current_scale,
        )

    optimizer_result = scipy.optimize.least_squares(
        residuals,
        np.array([initial_vth, initial_log10_beta]),
        bounds=(np.array([lower_vth, -18.0]), np.array([upper_vth, 6.0])),
        loss="soft_l1",
    )
    if not optimizer_result.success:
        raise MosfetFitError(f"MOSFET Id-Vgs fit failed: {optimizer_result.message}")

    fitted_vth, fitted_log10_beta = optimizer_result.x
    parameters = MosfetLevel1Parameters(
        vth_v=float(fitted_vth),
        beta_a_per_v2=10.0 ** float(fitted_log10_beta),
        lambda_1_per_v=0.0,
        vds_v=vds,
    )
    predicted_current = np.asarray(mosfet_level1_current(vgs, parameters))
    log_rmse: float | None
    if np.any((measured_current > 0) & (predicted_current > 0)):
        log_rmse = rmse_log10_current(measured_current, predicted_current)
    else:
        log_rmse = None

    measured_span = float(np.max(measured_current) - np.min(measured_current))
    if measured_span > 0:
        normalized_rmse = (
            rmse_current(measured_current, predicted_current) / measured_span
        )
    else:
        normalized_rmse = float("nan")

    notes = ["lambda_1_per_v fixed at 0 for stable M2 Id-Vgs fitting."]
    excluded_points = int(len(data) - positive_points)
    if excluded_points:
        notes.append(
            f"{excluded_points} nonpositive-current point(s) excluded from the "
            "sqrt-current fit objective but included in linear-current metrics."
        )

    return MosfetIdVgsFitResult(
        parameters=parameters,
        fixed_vds_v=vds,
        success=bool(optimizer_result.success),
        status=int(optimizer_result.status),
        message=str(optimizer_result.message),
        metrics=MosfetIdVgsFitMetrics(
            rmse_current_a=rmse_current(measured_current, predicted_current),
            rmse_log10_current=log_rmse,
            max_abs_current_error_a=max_abs_current_error(
                measured_current,
                predicted_current,
            ),
            normalized_rmse_current=float(normalized_rmse),
        ),
        optimizer_cost=float(optimizer_result.cost),
        optimizer_nfev=int(optimizer_result.nfev),
        total_points=int(len(data)),
        positive_current_points=positive_points,
        used_points=positive_points,
        notes=tuple(notes),
    )


def _resolve_fixed_vds(data: pd.DataFrame, fixed_vds_v: float | None) -> float:
    if fixed_vds_v is not None:
        vds = float(fixed_vds_v)
    elif "vds_v" in data.columns:
        values = data["vds_v"].to_numpy(dtype=float)
        if len(values) == 0 or not np.all(np.isfinite(values)):
            raise ValueError("vds_v values must be finite.")
        vds = float(values[0])
        if not np.allclose(values, vds, rtol=1e-6, atol=1e-12):
            raise ValueError(
                "MOSFET Id-Vgs fitting requires fixed Vds; vds_v is not constant."
            )
    else:
        raise ValueError(
            "MOSFET Id-Vgs fitting requires fixed_vds_v or a constant vds_v column."
        )

    if not np.isfinite(vds) or vds <= 0:
        raise ValueError("fixed Vds must be a positive finite voltage.")
    return vds
