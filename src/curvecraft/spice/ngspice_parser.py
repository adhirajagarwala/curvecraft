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
        if not _looks_like_ngspice_data_row(values):
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


def parse_mosfet_id_vgs_ngspice_output_text(
    text: str,
    *,
    current_sign: float = -1.0,
) -> pd.DataFrame:
    """Parse MOSFET Id-Vgs ngspice DC output into Vgs/Id columns.

    The M2 MOSFET netlist prints ``v(gate)`` and ``i(Vds)``. ngspice reports
    voltage-source current using its source-current convention, so the default
    sign converts it to positive n-channel drain current.
    """
    rows: list[tuple[float, float]] = []
    for raw_line in text.splitlines():
        parts = raw_line.split()
        if len(parts) < 3:
            continue
        values = _parse_numeric_fields(parts)
        if values is None:
            continue
        if not _looks_like_ngspice_data_row(values):
            continue
        rows.append((values[-2], current_sign * values[-1]))

    if not rows:
        raise ValueError("No MOSFET Id-Vgs ngspice DC sweep rows found in output.")

    return pd.DataFrame(rows, columns=["vgs_v", "id_a"])


def parse_mosfet_id_vgs_ngspice_output_file(
    path: str | Path,
    *,
    current_sign: float = -1.0,
) -> pd.DataFrame:
    """Parse a MOSFET Id-Vgs ngspice DC sweep output file."""
    return parse_mosfet_id_vgs_ngspice_output_text(
        Path(path).read_text(encoding="utf-8"),
        current_sign=current_sign,
    )


def parse_mosfet_id_vds_ngspice_output_text(
    text: str,
    *,
    fixed_vgs_v: float,
    current_sign: float = -1.0,
) -> pd.DataFrame:
    """Parse one MOSFET Id-Vds ngspice DC output into Vgs/Vds/Id columns.

    The M3 Id-Vds netlist prints ``v(drain)`` and ``i(Vds)`` while holding
    ``Vgs`` fixed. The default sign converts ngspice's voltage-source current
    convention to positive n-channel drain current.
    """
    rows: list[tuple[float, float, float]] = []
    for raw_line in text.splitlines():
        parts = raw_line.split()
        if len(parts) < 3:
            continue
        values = _parse_numeric_fields(parts)
        if values is None:
            continue
        if not _looks_like_ngspice_data_row(values):
            continue
        rows.append((float(fixed_vgs_v), values[-2], current_sign * values[-1]))

    if not rows:
        raise ValueError("No MOSFET Id-Vds ngspice DC sweep rows found in output.")

    return pd.DataFrame(rows, columns=["vgs_v", "vds_v", "id_a"])


def parse_mosfet_id_vds_ngspice_output_file(
    path: str | Path,
    *,
    fixed_vgs_v: float,
    current_sign: float = -1.0,
) -> pd.DataFrame:
    """Parse one MOSFET Id-Vds ngspice DC sweep output file."""
    return parse_mosfet_id_vds_ngspice_output_text(
        Path(path).read_text(encoding="utf-8"),
        fixed_vgs_v=fixed_vgs_v,
        current_sign=current_sign,
    )


def _parse_numeric_fields(parts: list[str]) -> tuple[float, ...] | None:
    try:
        return tuple(float(part) for part in parts)
    except ValueError:
        return None


def _looks_like_ngspice_data_row(values: tuple[float, ...]) -> bool:
    if len(values) < 3:
        return False
    index = values[0]
    return index >= 0 and index.is_integer()
