"""Diode compact model equations."""

from dataclasses import dataclass
from typing import cast

import numpy as np
from scipy.optimize import brentq

BOLTZMANN_J_PER_K = 1.380649e-23
ELEMENTARY_CHARGE_C = 1.602176634e-19


@dataclass(frozen=True)
class DiodeParameters:
    """Parameters for the M1 diode compact model.

    Attributes:
        saturation_current_a: Reverse saturation current, Is, in amps.
        ideality_factor: Ideality factor, n. Typical silicon values are near 1-2.
        series_resistance_ohm: Optional series resistance, Rs, in ohms.
        temperature_k: Junction temperature in kelvin.
    """

    saturation_current_a: float
    ideality_factor: float
    series_resistance_ohm: float = 0.0
    temperature_k: float = 300.0

    def __post_init__(self) -> None:
        if not np.isfinite(self.saturation_current_a):
            raise ValueError("saturation_current_a must be finite.")
        if not np.isfinite(self.ideality_factor):
            raise ValueError("ideality_factor must be finite.")
        if not np.isfinite(self.series_resistance_ohm):
            raise ValueError("series_resistance_ohm must be finite.")
        if not np.isfinite(self.temperature_k):
            raise ValueError("temperature_k must be finite.")
        if self.saturation_current_a <= 0:
            raise ValueError("saturation_current_a must be positive.")
        if self.ideality_factor <= 0:
            raise ValueError("ideality_factor must be positive.")
        if self.series_resistance_ohm < 0:
            raise ValueError("series_resistance_ohm must be nonnegative.")
        if self.temperature_k <= 0:
            raise ValueError("temperature_k must be positive.")


def thermal_voltage(temperature_k: float = 300.0) -> float:
    """Return thermal voltage kT/q in volts."""
    if not np.isfinite(temperature_k):
        raise ValueError("temperature_k must be finite.")
    if temperature_k <= 0:
        raise ValueError("temperature_k must be positive.")
    return BOLTZMANN_J_PER_K * temperature_k / ELEMENTARY_CHARGE_C


def diode_current(
    voltage_v: np.ndarray | float,
    parameters: DiodeParameters,
) -> np.ndarray:
    """Evaluate diode current for applied diode voltage.

    For zero series resistance this uses the Shockley equation directly. For
    nonzero series resistance it solves the implicit equation at each voltage:
    I = Is * (exp((V - I * Rs) / (n * Vt)) - 1).
    """
    voltage = np.asarray(voltage_v, dtype=float)
    flat_voltage = voltage.reshape(-1)

    if parameters.series_resistance_ohm == 0:
        current = _shockley_current(flat_voltage, parameters)
    else:
        current = np.array(
            [_solve_current_with_series_resistance(v, parameters) for v in flat_voltage]
        )

    return current.reshape(voltage.shape)


def _shockley_current(
    voltage_v: np.ndarray,
    parameters: DiodeParameters,
) -> np.ndarray:
    vt = thermal_voltage(parameters.temperature_k)
    exponent = voltage_v / (parameters.ideality_factor * vt)
    return parameters.saturation_current_a * np.expm1(np.clip(exponent, -745.0, 700.0))


def _solve_current_with_series_resistance(
    voltage_v: float,
    parameters: DiodeParameters,
) -> float:
    saturation_current = parameters.saturation_current_a
    series_resistance = parameters.series_resistance_ohm
    vt_scaled = parameters.ideality_factor * thermal_voltage(parameters.temperature_k)

    def residual(current_a: float) -> float:
        exponent = (voltage_v - current_a * series_resistance) / vt_scaled
        diode_rhs = float(
            saturation_current * np.expm1(np.clip(exponent, -745.0, 700.0))
        )
        return current_a - diode_rhs

    if voltage_v <= 0:
        lower = -saturation_current
        upper = 0.0
    else:
        lower = 0.0
        upper = max(voltage_v / series_resistance, saturation_current)

    lower_residual = residual(lower)
    upper_residual = residual(upper)
    while lower_residual * upper_residual > 0:
        upper *= 2.0
        upper_residual = residual(upper)

    solution = brentq(residual, lower, upper, xtol=1e-14, rtol=1e-12, maxiter=100)
    return cast(float, solution)
