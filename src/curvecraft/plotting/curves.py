"""Plotting utilities for diode I-V curves."""

from os import PathLike
from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np


def plot_iv_curve(
    measured_voltage_v: np.ndarray,
    measured_current_a: np.ndarray,
    model_current_a: np.ndarray,
    output_path: str | PathLike[str],
    *,
    semilog_y: bool = False,
) -> Path:
    """Save a measured-vs-model diode I-V plot as a PNG file.

    For semilog-y plots, nonpositive current values are masked because a
    logarithmic y-axis cannot display zero or negative current. The linear plot
    should be used when signed reverse-bias current must be inspected directly.
    """
    measured_voltage = np.asarray(measured_voltage_v, dtype=float)
    measured_current = np.asarray(measured_current_a, dtype=float)
    model_current = np.asarray(model_current_a, dtype=float)
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    fig, ax = plt.subplots(figsize=(6.0, 4.0), constrained_layout=True)
    if semilog_y:
        measured_mask = measured_current > 0
        model_mask = model_current > 0
        ax.semilogy(
            measured_voltage[measured_mask],
            measured_current[measured_mask],
            "o",
            label="Measured",
        )
        ax.semilogy(
            measured_voltage[model_mask],
            model_current[model_mask],
            "-",
            label="Model",
        )
        ax.set_ylabel("Current (A, positive values only)")
    else:
        ax.plot(measured_voltage, measured_current, "o", label="Measured")
        ax.plot(measured_voltage, model_current, "-", label="Model")
        ax.set_ylabel("Current (A)")

    ax.set_xlabel("Voltage (V)")
    ax.grid(True, which="both", alpha=0.3)
    ax.legend()
    fig.savefig(path, dpi=150)
    plt.close(fig)
    return path


def plot_iv_linear(
    measured_voltage_v: np.ndarray,
    measured_current_a: np.ndarray,
    model_current_a: np.ndarray,
    output_path: str | PathLike[str],
) -> Path:
    """Save a linear-scale measured-vs-model I-V plot."""
    return plot_iv_curve(
        measured_voltage_v,
        measured_current_a,
        model_current_a,
        output_path,
        semilog_y=False,
    )


def plot_iv_semilog_y(
    measured_voltage_v: np.ndarray,
    measured_current_a: np.ndarray,
    model_current_a: np.ndarray,
    output_path: str | PathLike[str],
) -> Path:
    """Save a semilog-y measured-vs-model I-V plot for positive current values."""
    return plot_iv_curve(
        measured_voltage_v,
        measured_current_a,
        model_current_a,
        output_path,
        semilog_y=True,
    )
