"""Diode model placeholders."""

from dataclasses import dataclass


@dataclass(frozen=True)
class DiodeParameters:
    """Placeholder container for future fitted diode parameters."""

    saturation_current_a: float
    ideality_factor: float
    series_resistance_ohm: float | None = None
