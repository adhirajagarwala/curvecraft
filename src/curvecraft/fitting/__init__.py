"""Fitting routines."""

from curvecraft.fitting.metrics import (
    max_abs_current_error,
    rmse_current,
    rmse_log10_current,
)
from curvecraft.fitting.mosfet_extract import (
    InitialMosfetParameterEstimate,
    SqrtIdThresholdEstimate,
    estimate_initial_mosfet_params,
    estimate_threshold_by_constant_current,
    estimate_threshold_by_sqrt_id_linear_fit,
)
from curvecraft.fitting.optimizer import (
    DiodeFitError,
    DiodeFitResult,
    MosfetFitError,
    MosfetIdVgsFitMetrics,
    MosfetIdVgsFitResult,
    fit_diode_iv,
    fit_mosfet_id_vgs,
)

__all__ = [
    "DiodeFitError",
    "DiodeFitResult",
    "InitialMosfetParameterEstimate",
    "MosfetFitError",
    "MosfetIdVgsFitMetrics",
    "MosfetIdVgsFitResult",
    "SqrtIdThresholdEstimate",
    "estimate_initial_mosfet_params",
    "estimate_threshold_by_constant_current",
    "estimate_threshold_by_sqrt_id_linear_fit",
    "fit_diode_iv",
    "fit_mosfet_id_vgs",
    "max_abs_current_error",
    "rmse_current",
    "rmse_log10_current",
]
