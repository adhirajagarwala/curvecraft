"""MOSFET Id-Vds Level-1 parameter fitting."""

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
from curvecraft.models import MosfetLevel1Parameters, mosfet_level1_id_vds_current


@dataclass(frozen=True)
class MosfetIdVdsFitMetrics:
    """Error metrics for a fitted MOSFET Id-Vds model."""

    rmse_current_a: float
    rmse_log10_current: float | None
    max_abs_current_error_a: float
    normalized_rmse_current: float


@dataclass(frozen=True)
class MosfetIdVdsFitResult:
    """Result from fitting M3 MOSFET Id-Vds Level-1 parameters."""

    parameters: MosfetLevel1Parameters
    fitted_parameters: tuple[str, ...]
    fixed_parameters: tuple[str, ...]
    success: bool
    status: int
    message: str
    metrics: MosfetIdVdsFitMetrics
    optimizer_cost: float
    optimizer_nfev: int
    total_points: int
    used_points: int
    positive_current_points: int
    unique_vgs_v: tuple[float, ...]
    notes: tuple[str, ...]


def fit_mosfet_id_vds(
    data: pd.DataFrame,
    *,
    fixed_vth_v: float | None = None,
    fit_vth_v: bool | None = None,
    min_positive_points: int = 3,
) -> MosfetIdVdsFitResult:
    """Fit n-channel Level-1 parameters to MOSFET Id-Vds output curves.

    By default, this fits ``beta_a_per_v2`` and ``lambda_1_per_v`` while using
    a caller-provided fixed ``vth_v``. If no fixed threshold is provided, the
    threshold voltage is fitted jointly with conservative data-derived bounds.
    Nonnegative-current rows are used in the optimizer; negative-current rows
    are excluded with a note and still appear in the returned error metrics.
    """
    _validate_required_columns(data)
    vgs = data["vgs_v"].to_numpy(dtype=float)
    vds = data["vds_v"].to_numpy(dtype=float)
    measured_current = data["id_a"].to_numpy(dtype=float)
    if len(data) == 0:
        raise ValueError("MOSFET Id-Vds fitting requires at least one data row.")
    if (
        np.any(~np.isfinite(vgs))
        or np.any(~np.isfinite(vds))
        or np.any(~np.isfinite(measured_current))
    ):
        raise ValueError("MOSFET Id-Vds fitting data must contain finite values.")
    if np.any(vds < 0):
        raise ValueError("MOSFET Id-Vds fitting requires nonnegative vds_v values.")

    should_fit_vth = fixed_vth_v is None if fit_vth_v is None else fit_vth_v
    if fixed_vth_v is not None and should_fit_vth:
        raise ValueError("fixed_vth_v cannot be provided when fit_vth_v is true.")
    if fixed_vth_v is not None and not np.isfinite(fixed_vth_v):
        raise ValueError("fixed_vth_v must be finite.")

    positive_mask = measured_current > 0
    positive_points = int(np.count_nonzero(positive_mask))
    if positive_points < min_positive_points:
        raise ValueError(
            "MOSFET Id-Vds fitting requires at least "
            f"{min_positive_points} positive-current points; got {positive_points}."
        )

    fit_mask = measured_current >= 0
    used_points = int(np.count_nonzero(fit_mask))
    if used_points < min_positive_points:
        raise ValueError(
            "MOSFET Id-Vds fitting selected too few usable nonnegative-current "
            f"points: got {used_points}, need {min_positive_points}."
        )

    fit_vgs = vgs[fit_mask]
    fit_vds = vds[fit_mask]
    fit_current = measured_current[fit_mask]
    current_scale = max(float(np.max(fit_current)), float(np.finfo(float).tiny))
    initial_beta = _initial_beta_guess(
        vgs[positive_mask],
        vds[positive_mask],
        measured_current[positive_mask],
        fixed_vth_v,
    )

    notes: list[str] = []
    excluded_negative_points = int(np.count_nonzero(measured_current < 0))
    if excluded_negative_points:
        notes.append(
            f"{excluded_negative_points} negative-current point(s) excluded from "
            "the Id-Vds fit objective but included in linear-current metrics."
        )
    if should_fit_vth:
        notes.append(
            "vth_v fitted jointly from Id-Vds data; Id-Vgs data often constrains "
            "threshold voltage more clearly."
        )
    else:
        notes.append("vth_v fixed during Id-Vds fitting.")

    if should_fit_vth:
        lower_vth, upper_vth = _vth_bounds(vgs)
        initial_vth = _initial_vth_guess(vgs, measured_current, lower_vth, upper_vth)
        initial = np.array([initial_vth, np.log10(initial_beta), 0.01])
        lower_bounds = np.array([lower_vth, -18.0, 0.0])
        upper_bounds = np.array([upper_vth, 6.0, 2.0])
        fitted_parameters: tuple[str, ...] = (
            "vth_v",
            "beta_a_per_v2",
            "lambda_1_per_v",
        )
        fixed_parameters: tuple[str, ...] = ()
    else:
        vth = float(cast(float, fixed_vth_v))
        initial = np.array([np.log10(initial_beta), 0.01])
        lower_bounds = np.array([-18.0, 0.0])
        upper_bounds = np.array([6.0, 2.0])
        fitted_parameters = ("beta_a_per_v2", "lambda_1_per_v")
        fixed_parameters = ("vth_v",)

    def residuals(variables: np.ndarray) -> np.ndarray:
        if should_fit_vth:
            vth_v = float(variables[0])
            beta = 10.0 ** float(variables[1])
            lambda_1_per_v = float(variables[2])
        else:
            vth_v = vth
            beta = 10.0 ** float(variables[0])
            lambda_1_per_v = float(variables[1])
        parameters = MosfetLevel1Parameters(
            vth_v=vth_v,
            beta_a_per_v2=beta,
            lambda_1_per_v=lambda_1_per_v,
        )
        predicted = np.asarray(
            mosfet_level1_id_vds_current(fit_vgs, fit_vds, parameters)
        )
        return cast(np.ndarray, (predicted - fit_current) / current_scale)

    optimizer_result = scipy.optimize.least_squares(
        residuals,
        initial,
        bounds=(lower_bounds, upper_bounds),
        loss="soft_l1",
    )
    if should_fit_vth:
        fitted_vth = float(optimizer_result.x[0])
        fitted_beta = 10.0 ** float(optimizer_result.x[1])
        fitted_lambda = float(optimizer_result.x[2])
    else:
        fitted_vth = vth
        fitted_beta = 10.0 ** float(optimizer_result.x[0])
        fitted_lambda = float(optimizer_result.x[1])

    parameters = MosfetLevel1Parameters(
        vth_v=fitted_vth,
        beta_a_per_v2=fitted_beta,
        lambda_1_per_v=fitted_lambda,
    )
    predicted_current = np.asarray(mosfet_level1_id_vds_current(vgs, vds, parameters))
    log_rmse: float | None
    if np.any((measured_current > 0) & (predicted_current > 0)):
        log_rmse = rmse_log10_current(measured_current, predicted_current)
    else:
        log_rmse = None

    measured_span = float(np.max(measured_current) - np.min(measured_current))
    normalized_rmse = (
        rmse_current(measured_current, predicted_current) / measured_span
        if measured_span > 0
        else float("nan")
    )

    return MosfetIdVdsFitResult(
        parameters=parameters,
        fitted_parameters=fitted_parameters,
        fixed_parameters=fixed_parameters,
        success=bool(optimizer_result.success),
        status=int(optimizer_result.status),
        message=str(optimizer_result.message),
        metrics=MosfetIdVdsFitMetrics(
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
        used_points=used_points,
        positive_current_points=positive_points,
        unique_vgs_v=tuple(float(value) for value in sorted(set(vgs))),
        notes=tuple(notes),
    )


def _validate_required_columns(data: pd.DataFrame) -> None:
    required_columns = {"vgs_v", "vds_v", "id_a"}
    missing = required_columns.difference(data.columns)
    if missing:
        raise ValueError(
            f"MOSFET Id-Vds fitting requires column(s): {', '.join(sorted(missing))}."
        )


def _vth_bounds(vgs_v: np.ndarray) -> tuple[float, float]:
    vgs_min = float(np.min(vgs_v))
    vgs_max = float(np.max(vgs_v))
    span = max(vgs_max - vgs_min, 1.0)
    return vgs_min - span, vgs_max


def _initial_vth_guess(
    vgs_v: np.ndarray,
    id_a: np.ndarray,
    lower_vth_v: float,
    upper_vth_v: float,
) -> float:
    positive_vgs = vgs_v[id_a > 0]
    if positive_vgs.size:
        guess = float(np.min(positive_vgs) - 0.1)
    else:
        guess = float(np.median(vgs_v))
    return float(np.clip(guess, lower_vth_v, upper_vth_v))


def _initial_beta_guess(
    vgs_v: np.ndarray,
    vds_v: np.ndarray,
    id_a: np.ndarray,
    fixed_vth_v: float | None,
) -> float:
    if fixed_vth_v is None:
        vth_guess = float(np.min(vgs_v) - 0.1)
    else:
        vth_guess = float(fixed_vth_v)
    overdrive = vgs_v - vth_guess
    conducting = overdrive > 0
    denominator = np.zeros_like(id_a, dtype=float)
    triode = conducting & (vds_v < overdrive)
    saturation = conducting & ~triode
    denominator[triode] = overdrive[triode] * vds_v[triode] - 0.5 * vds_v[triode] ** 2
    denominator[saturation] = 0.5 * overdrive[saturation] ** 2
    usable = denominator > 0
    if np.any(usable):
        estimate = float(np.median(id_a[usable] / denominator[usable]))
        if np.isfinite(estimate) and estimate > 0:
            return estimate
    return 1e-3
