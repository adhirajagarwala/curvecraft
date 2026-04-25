"""Fitting routines."""

from curvecraft.fitting.metrics import (
    max_abs_current_error,
    rmse_current,
    rmse_log10_current,
)
from curvecraft.fitting.optimizer import DiodeFitError, DiodeFitResult, fit_diode_iv

__all__ = [
    "DiodeFitError",
    "DiodeFitResult",
    "fit_diode_iv",
    "max_abs_current_error",
    "rmse_current",
    "rmse_log10_current",
]
