"""Initial MOSFET Id-Vgs extraction helpers."""

from dataclasses import dataclass
from typing import cast

import numpy as np


@dataclass(frozen=True)
class SqrtIdThresholdEstimate:
    """Result from sqrt(Id)-versus-Vgs threshold extraction."""

    vth_v: float
    slope_sqrt_a_per_v: float
    intercept_sqrt_a: float
    selected_point_count: int
    current_min_a: float
    current_max_a: float


@dataclass(frozen=True)
class InitialMosfetParameterEstimate:
    """Initial guesses for later MOSFET nonlinear fitting."""

    vth_v: float
    beta_a_per_v2: float
    method: str


def estimate_threshold_by_constant_current(
    vgs_v: np.ndarray | list[float],
    id_a: np.ndarray | list[float],
    target_current_a: float,
) -> float:
    """Estimate threshold voltage where Id crosses a target current.

    The crossing is interpolated between adjacent measured points sorted by
    Vgs. A clear error is raised when the target current is outside the
    measured current range or no crossing is found.
    """
    if target_current_a < 0:
        raise ValueError("target_current_a must be nonnegative.")

    vgs, current = _sorted_curve_arrays(vgs_v, id_a)
    delta = current - target_current_a
    exact = np.flatnonzero(delta == 0)
    if exact.size:
        return float(vgs[int(exact[0])])

    for index in range(len(vgs) - 1):
        y0 = delta[index]
        y1 = delta[index + 1]
        if y0 * y1 > 0 or y0 == y1:
            continue
        fraction = -y0 / (y1 - y0)
        return float(vgs[index] + fraction * (vgs[index + 1] - vgs[index]))

    raise ValueError(
        "Target current is not crossed by the provided MOSFET Id-Vgs data."
    )


def estimate_threshold_by_sqrt_id_linear_fit(
    vgs_v: np.ndarray | list[float],
    id_a: np.ndarray | list[float],
    *,
    current_min_a: float | None = None,
    current_max_a: float | None = None,
    lower_percentile: float = 20.0,
    upper_percentile: float = 80.0,
    min_points: int = 3,
) -> SqrtIdThresholdEstimate:
    """Estimate Vth from a linear fit of sqrt(Id) versus Vgs.

    Only positive-current points are eligible. If explicit current bounds are
    not provided, a percentile window of positive-current points is used. The
    threshold estimate is the x-intercept of the fitted line.
    """
    if min_points < 2:
        raise ValueError("min_points must be at least 2.")
    vgs, current = _sorted_curve_arrays(vgs_v, id_a)
    positive_current = current[current > 0]
    if positive_current.size < min_points:
        raise ValueError(
            "sqrt(Id) threshold extraction requires at least "
            f"{min_points} positive-current points."
        )

    lower = (
        float(current_min_a)
        if current_min_a is not None
        else float(np.percentile(positive_current, lower_percentile))
    )
    upper = (
        float(current_max_a)
        if current_max_a is not None
        else float(np.percentile(positive_current, upper_percentile))
    )
    if lower < 0:
        raise ValueError("current_min_a must be nonnegative.")
    if upper <= lower:
        raise ValueError("current_max_a must be greater than current_min_a.")

    selected = (current > 0) & (current >= lower) & (current <= upper)
    selected_count = int(np.count_nonzero(selected))
    if selected_count < min_points:
        raise ValueError(
            "sqrt(Id) threshold extraction selected too few positive-current "
            f"points: got {selected_count}, need {min_points}."
        )

    fit = np.polyfit(vgs[selected], np.sqrt(current[selected]), deg=1)
    slope = float(fit[0])
    intercept = float(fit[1])
    if slope <= 0:
        raise ValueError("sqrt(Id) linear fit slope must be positive.")

    return SqrtIdThresholdEstimate(
        vth_v=-intercept / slope,
        slope_sqrt_a_per_v=slope,
        intercept_sqrt_a=intercept,
        selected_point_count=selected_count,
        current_min_a=lower,
        current_max_a=upper,
    )


def estimate_initial_mosfet_params(
    vgs_v: np.ndarray | list[float],
    id_a: np.ndarray | list[float],
    *,
    current_min_a: float | None = None,
    current_max_a: float | None = None,
) -> InitialMosfetParameterEstimate:
    """Return practical initial Vth and beta guesses for later fitting.

    The estimates come from sqrt(Id) linearization and are meant as optimizer
    starting values, not as definitive physical extraction.
    """
    fit = estimate_threshold_by_sqrt_id_linear_fit(
        vgs_v,
        id_a,
        current_min_a=current_min_a,
        current_max_a=current_max_a,
    )
    beta = 2.0 * fit.slope_sqrt_a_per_v**2
    return InitialMosfetParameterEstimate(
        vth_v=fit.vth_v,
        beta_a_per_v2=beta,
        method="sqrt_id_linear_fit",
    )


def _sorted_curve_arrays(
    vgs_v: np.ndarray | list[float],
    id_a: np.ndarray | list[float],
) -> tuple[np.ndarray, np.ndarray]:
    vgs = np.asarray(vgs_v, dtype=float)
    current = np.asarray(id_a, dtype=float)
    if vgs.shape != current.shape:
        raise ValueError("vgs_v and id_a must have the same shape.")
    if vgs.ndim != 1:
        raise ValueError("vgs_v and id_a must be one-dimensional.")
    if len(vgs) < 2:
        raise ValueError("MOSFET Id-Vgs extraction requires at least two points.")
    if np.any(~np.isfinite(vgs)) or np.any(~np.isfinite(current)):
        raise ValueError("vgs_v and id_a must contain only finite values.")

    order = np.argsort(vgs, kind="mergesort")
    return cast(np.ndarray, vgs[order]), cast(np.ndarray, current[order])
