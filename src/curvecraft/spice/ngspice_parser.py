"""Parse ngspice DC sweep output for diode validation."""

from pathlib import Path

import pandas as pd


def parse_ngspice_dc_output_text(
    text: str,
    *,
    current_sign: float = -1.0,
) -> pd.DataFrame:
    """Parse ngspice DC sweep text into voltage/current columns.

    The Issue 6 netlist prints ``i(Vin)``. For that circuit orientation,
    ngspice reports current through the voltage source, which is opposite the
    diode anode-to-cathode current. The default ``current_sign=-1`` makes the
    returned ``current_a`` column use the diode-current convention.
    """
    rows: list[tuple[float, float]] = []
    for raw_line in text.splitlines():
        parts = raw_line.split()
        if len(parts) < 3:
            continue
        values = _parse_numeric_fields(parts)
        if values is None:
            continue
        rows.append((values[-2], current_sign * values[-1]))

    if not rows:
        raise ValueError("No ngspice DC sweep rows found in output.")

    return pd.DataFrame(rows, columns=["voltage_v", "current_a"])


def parse_ngspice_dc_output_file(
    path: str | Path,
    *,
    current_sign: float = -1.0,
) -> pd.DataFrame:
    """Parse an ngspice DC sweep output file."""
    return parse_ngspice_dc_output_text(
        Path(path).read_text(encoding="utf-8"),
        current_sign=current_sign,
    )


def _parse_numeric_fields(parts: list[str]) -> tuple[float, ...] | None:
    try:
        return tuple(float(part) for part in parts)
    except ValueError:
        return None
