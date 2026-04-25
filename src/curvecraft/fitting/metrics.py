"""Fit quality metrics for diode I-V data."""

import numpy as np


def rmse_current(
    measured_current_a: np.ndarray,
    predicted_current_a: np.ndarray,
) -> float:
    """Return root mean square error in current, in amps."""
    measured = np.asarray(measured_current_a, dtype=float)
    predicted = np.asarray(predicted_current_a, dtype=float)
    return float(np.sqrt(np.mean((predicted - measured) ** 2)))


def rmse_log10_current(
    measured_current_a: np.ndarray,
    predicted_current_a: np.ndarray,
) -> float:
    """Return RMSE of log10 current for points where both currents are positive."""
    measured = np.asarray(measured_current_a, dtype=float)
    predicted = np.asarray(predicted_current_a, dtype=float)
    mask = (measured > 0) & (predicted > 0)
    if not np.any(mask):
        raise ValueError(
            "Log-current RMSE requires at least one positive-current point."
        )
    log_error = np.log10(predicted[mask]) - np.log10(measured[mask])
    return float(np.sqrt(np.mean(log_error**2)))


def max_abs_current_error(
    measured_current_a: np.ndarray,
    predicted_current_a: np.ndarray,
) -> float:
    """Return maximum absolute current error, in amps."""
    measured = np.asarray(measured_current_a, dtype=float)
    predicted = np.asarray(predicted_current_a, dtype=float)
    return float(np.max(np.abs(predicted - measured)))


def root_mean_square_error(
    measured_current_a: np.ndarray,
    predicted_current_a: np.ndarray,
) -> float:
    """Compatibility wrapper for current RMSE."""
    return rmse_current(measured_current_a, predicted_current_a)
