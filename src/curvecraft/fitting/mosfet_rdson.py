"""Rds_on extraction helpers for MOSFET Id-Vds output curves."""

from dataclasses import dataclass

import numpy as np
import pandas as pd

from curvecraft.io.csv_loader import group_mosfet_id_vds_curves_by_vgs


@dataclass(frozen=True)
class RdsonEstimate:
    """Low-Vds Rds_on estimate for one MOSFET output curve."""

    vgs_v: float | None
    rds_on_ohm: float
    conductance_siemens: float
    fit_intercept_a: float
    rmse_current_a: float
    selected_point_count: int
    max_selected_vds_v: float


def extract_rdson_for_curve(
    vds_v: np.ndarray | list[float],
    id_a: np.ndarray | list[float],
    *,
    max_vds_v: float | None = None,
    low_vds_fraction: float = 0.2,
    min_points: int = 2,
    vgs_v: float | None = None,
) -> RdsonEstimate:
    """Estimate Rds_on from the low-Vds slope of one Id-Vds curve.

    The method fits ``Id ~= conductance * Vds + intercept`` over the selected
    low-Vds region and returns ``Rds_on = 1 / conductance``. The result is
    condition-dependent and should be interpreted at the associated Vgs and
    fixed measurement assumptions.
    """
    if min_points < 2:
        raise ValueError("min_points must be at least 2.")
    vds = np.asarray(vds_v, dtype=float)
    current = np.asarray(id_a, dtype=float)
    if vds.shape != current.shape:
        raise ValueError("vds_v and id_a must have the same shape.")
    if vds.ndim != 1:
        raise ValueError("vds_v and id_a must be one-dimensional.")
    if len(vds) == 0:
        raise ValueError("Rds_on extraction requires at least one data row.")
    if np.any(~np.isfinite(vds)) or np.any(~np.isfinite(current)):
        raise ValueError("vds_v and id_a must contain only finite values.")
    if np.any(vds < 0):
        raise ValueError("vds_v must be nonnegative for Rds_on extraction.")

    selected = _low_vds_mask(vds, max_vds_v, low_vds_fraction)
    selected_count = int(np.count_nonzero(selected))
    if selected_count < min_points:
        raise ValueError(
            "Rds_on extraction selected too few low-Vds points: "
            f"got {selected_count}, need {min_points}."
        )

    selected_vds = vds[selected]
    selected_current = current[selected]
    if np.unique(selected_vds).size < 2:
        raise ValueError(
            "Rds_on extraction requires at least two distinct low-Vds voltages."
        )
    fit = np.polyfit(selected_vds, selected_current, deg=1)
    conductance = float(fit[0])
    intercept = float(fit[1])
    if conductance <= 0:
        raise ValueError(
            "Rds_on extraction requires positive low-Vds conductance; "
            f"got {conductance:.6g} S."
        )

    predicted = conductance * selected_vds + intercept
    rmse = float(np.sqrt(np.mean((predicted - selected_current) ** 2)))
    return RdsonEstimate(
        vgs_v=vgs_v,
        rds_on_ohm=1.0 / conductance,
        conductance_siemens=conductance,
        fit_intercept_a=intercept,
        rmse_current_a=rmse,
        selected_point_count=selected_count,
        max_selected_vds_v=float(np.max(selected_vds)),
    )


def extract_rdson_by_vgs(
    data: pd.DataFrame | dict[float, pd.DataFrame],
    *,
    max_vds_v: float | None = None,
    low_vds_fraction: float = 0.2,
    min_points: int = 2,
) -> tuple[RdsonEstimate, ...]:
    """Estimate Rds_on for each stepped Vgs output curve."""
    if isinstance(data, pd.DataFrame):
        curves = group_mosfet_id_vds_curves_by_vgs(data)
    else:
        curves = data
    estimates: list[RdsonEstimate] = []
    for vgs_v, curve in sorted(curves.items()):
        estimates.append(
            extract_rdson_for_curve(
                curve["vds_v"].to_numpy(dtype=float),
                curve["id_a"].to_numpy(dtype=float),
                max_vds_v=max_vds_v,
                low_vds_fraction=low_vds_fraction,
                min_points=min_points,
                vgs_v=float(vgs_v),
            )
        )
    return tuple(estimates)


def _low_vds_mask(
    vds_v: np.ndarray,
    max_vds_v: float | None,
    low_vds_fraction: float,
) -> np.ndarray:
    if max_vds_v is not None:
        max_selected = float(max_vds_v)
        if not np.isfinite(max_selected) or max_selected < 0:
            raise ValueError("max_vds_v must be a nonnegative finite voltage.")
    else:
        if not 0 < low_vds_fraction <= 1:
            raise ValueError("low_vds_fraction must be greater than 0 and at most 1.")
        max_vds = float(np.max(vds_v))
        max_selected = max_vds * low_vds_fraction
    return vds_v <= max_selected
