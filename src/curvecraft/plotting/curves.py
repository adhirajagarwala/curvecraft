"""Plotting utilities for measured-vs-model semiconductor curves."""

from os import PathLike
from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


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


def plot_python_vs_ngspice(
    voltage_v: np.ndarray,
    python_current_a: np.ndarray,
    ngspice_current_a: np.ndarray,
    output_path: str | PathLike[str],
) -> Path:
    """Save a linear Python-vs-ngspice diode validation plot."""
    return plot_iv_curve(
        voltage_v,
        ngspice_current_a,
        python_current_a,
        output_path,
        semilog_y=False,
    )


def plot_mosfet_id_vgs_curve(
    measured_vgs_v: np.ndarray,
    measured_id_a: np.ndarray,
    model_id_a: np.ndarray,
    output_path: str | PathLike[str],
    *,
    semilog_y: bool = False,
) -> Path:
    """Save a measured-vs-model MOSFET Id-Vgs transfer plot as a PNG file.

    For semilog-y plots, nonpositive drain-current values are masked because a
    logarithmic y-axis cannot display zero or negative current. The linear plot
    preserves the measured current sign.
    """
    measured_vgs = np.asarray(measured_vgs_v, dtype=float)
    measured_id = np.asarray(measured_id_a, dtype=float)
    model_id = np.asarray(model_id_a, dtype=float)
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    fig, ax = plt.subplots(figsize=(6.0, 4.0), constrained_layout=True)
    if semilog_y:
        measured_mask = measured_id > 0
        model_mask = model_id > 0
        ax.semilogy(
            measured_vgs[measured_mask],
            measured_id[measured_mask],
            "o",
            label="Measured",
        )
        ax.semilogy(
            measured_vgs[model_mask],
            model_id[model_mask],
            "-",
            label="Model",
        )
        ax.set_ylabel("Drain current Id (A, positive values only)")
    else:
        ax.plot(measured_vgs, measured_id, "o", label="Measured")
        ax.plot(measured_vgs, model_id, "-", label="Model")
        ax.set_ylabel("Drain current Id (A)")

    ax.set_xlabel("Gate-source voltage Vgs (V)")
    ax.grid(True, which="both", alpha=0.3)
    ax.legend()
    fig.savefig(path, dpi=150)
    plt.close(fig)
    return path


def plot_mosfet_id_vgs_linear(
    measured_vgs_v: np.ndarray,
    measured_id_a: np.ndarray,
    model_id_a: np.ndarray,
    output_path: str | PathLike[str],
) -> Path:
    """Save a linear-scale measured-vs-model MOSFET Id-Vgs plot."""
    return plot_mosfet_id_vgs_curve(
        measured_vgs_v,
        measured_id_a,
        model_id_a,
        output_path,
        semilog_y=False,
    )


def plot_mosfet_id_vgs_semilog_y(
    measured_vgs_v: np.ndarray,
    measured_id_a: np.ndarray,
    model_id_a: np.ndarray,
    output_path: str | PathLike[str],
) -> Path:
    """Save a semilog-y MOSFET Id-Vgs plot for positive current values."""
    return plot_mosfet_id_vgs_curve(
        measured_vgs_v,
        measured_id_a,
        model_id_a,
        output_path,
        semilog_y=True,
    )


def plot_mosfet_id_vds_family(
    data: pd.DataFrame,
    output_path: str | PathLike[str],
) -> Path:
    """Save a MOSFET Id-Vds output-curve family plot grouped by Vgs."""
    required_columns = {"vgs_v", "vds_v", "id_a"}
    missing = required_columns.difference(data.columns)
    if missing:
        raise ValueError(
            f"MOSFET Id-Vds plot data missing column(s): {sorted(missing)}"
        )

    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    sorted_data = data.loc[:, ["vgs_v", "vds_v", "id_a"]].sort_values(
        ["vgs_v", "vds_v"],
        kind="mergesort",
    )

    fig, ax = plt.subplots(figsize=(6.0, 4.0), constrained_layout=True)
    for vgs_v, curve in sorted_data.groupby("vgs_v", sort=True):
        ax.plot(
            curve["vds_v"].to_numpy(dtype=float),
            curve["id_a"].to_numpy(dtype=float),
            "o-",
            label=f"Vgs={float(vgs_v):.6g} V",
        )

    ax.set_xlabel("Drain-source voltage Vds (V)")
    ax.set_ylabel("Drain current Id (A)")
    ax.grid(True, which="both", alpha=0.3)
    ax.legend()
    fig.savefig(path, dpi=150)
    plt.close(fig)
    return path


def plot_mosfet_id_vds_measured_vs_fit(
    measured_data: pd.DataFrame,
    fitted_id_a: np.ndarray,
    output_path: str | PathLike[str],
) -> Path:
    """Save measured-vs-fitted MOSFET Id-Vds output curves grouped by Vgs."""
    required_columns = {"vgs_v", "vds_v", "id_a"}
    missing = required_columns.difference(measured_data.columns)
    if missing:
        raise ValueError(
            f"MOSFET Id-Vds plot data missing column(s): {sorted(missing)}"
        )
    fitted = np.asarray(fitted_id_a, dtype=float)
    if fitted.shape != (len(measured_data),):
        raise ValueError("fitted_id_a must have one value per measured data row.")

    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    plot_data = measured_data.loc[:, ["vgs_v", "vds_v", "id_a"]].copy()
    plot_data["fitted_id_a"] = fitted
    plot_data = plot_data.sort_values(["vgs_v", "vds_v"], kind="mergesort")

    fig, ax = plt.subplots(figsize=(6.0, 4.0), constrained_layout=True)
    for vgs_v, curve in plot_data.groupby("vgs_v", sort=True):
        label = f"Vgs={float(vgs_v):.6g} V"
        ax.plot(
            curve["vds_v"].to_numpy(dtype=float),
            curve["id_a"].to_numpy(dtype=float),
            "o",
            label=f"Measured {label}",
        )
        ax.plot(
            curve["vds_v"].to_numpy(dtype=float),
            curve["fitted_id_a"].to_numpy(dtype=float),
            "-",
            label=f"Fit {label}",
        )

    ax.set_xlabel("Drain-source voltage Vds (V)")
    ax.set_ylabel("Drain current Id (A)")
    ax.grid(True, which="both", alpha=0.3)
    ax.legend()
    fig.savefig(path, dpi=150)
    plt.close(fig)
    return path
