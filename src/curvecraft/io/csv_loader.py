"""CSV loading helpers."""

from os import PathLike
from pathlib import Path

import pandas as pd
from pandas.errors import EmptyDataError

from curvecraft.io.schema import (
    OPTIONAL_MOSFET_ID_VGS_COLUMNS,
    REQUIRED_DIODE_COLUMNS,
    REQUIRED_MOSFET_ID_VDS_COLUMNS,
    REQUIRED_MOSFET_ID_VGS_COLUMNS,
)


def load_diode_curve_csv(path: str | PathLike[str]) -> pd.DataFrame:
    """Load diode I-V curve data from a CSV file.

    The returned frame contains the required columns as numeric values:
    ``voltage_v`` and ``current_a``.
    """
    csv_path = Path(path)
    try:
        data = pd.read_csv(csv_path)
    except EmptyDataError as error:
        raise ValueError("Diode CSV is empty.") from error

    missing_columns = [
        column for column in REQUIRED_DIODE_COLUMNS if column not in data.columns
    ]
    if missing_columns:
        missing = ", ".join(missing_columns)
        required = ", ".join(REQUIRED_DIODE_COLUMNS)
        raise ValueError(
            f"Missing required diode CSV column(s): {missing}. "
            f"Required columns are: {required}."
        )

    clean_data = data.loc[:, REQUIRED_DIODE_COLUMNS].copy()
    if clean_data.empty:
        raise ValueError("Diode CSV must contain at least one data row.")

    for column in REQUIRED_DIODE_COLUMNS:
        try:
            clean_data[column] = pd.to_numeric(clean_data[column], errors="raise")
        except (TypeError, ValueError) as error:
            raise ValueError(
                f"Column '{column}' must contain only numeric values."
            ) from error

    nan_columns = [
        column for column in REQUIRED_DIODE_COLUMNS if clean_data[column].isna().any()
    ]
    if nan_columns:
        columns = ", ".join(nan_columns)
        raise ValueError(f"Diode CSV contains NaN or missing values in: {columns}.")

    return clean_data.sort_values("voltage_v", kind="mergesort").reset_index(drop=True)


def load_mosfet_id_vgs_curve_csv(path: str | PathLike[str]) -> pd.DataFrame:
    """Load n-channel enhancement MOSFET Id-Vgs transfer data from a CSV file.

    The returned frame contains required numeric columns ``vgs_v`` and
    ``id_a``. If the optional ``vds_v`` column is present, it is also returned
    as numeric data. Current sign is preserved.
    """
    csv_path = Path(path)
    try:
        data = pd.read_csv(csv_path)
    except EmptyDataError as error:
        raise ValueError("MOSFET Id-Vgs CSV is empty.") from error

    missing_columns = [
        column
        for column in REQUIRED_MOSFET_ID_VGS_COLUMNS
        if column not in data.columns
    ]
    if missing_columns:
        missing = ", ".join(missing_columns)
        required = ", ".join(REQUIRED_MOSFET_ID_VGS_COLUMNS)
        raise ValueError(
            f"Missing required MOSFET Id-Vgs CSV column(s): {missing}. "
            f"Required columns are: {required}."
        )

    selected_columns = list(REQUIRED_MOSFET_ID_VGS_COLUMNS)
    selected_columns.extend(
        column for column in OPTIONAL_MOSFET_ID_VGS_COLUMNS if column in data.columns
    )
    clean_data = data.loc[:, selected_columns].copy()
    if clean_data.empty:
        raise ValueError("MOSFET Id-Vgs CSV must contain at least one data row.")

    for column in selected_columns:
        try:
            clean_data[column] = pd.to_numeric(clean_data[column], errors="raise")
        except (TypeError, ValueError) as error:
            raise ValueError(
                f"Column '{column}' must contain only numeric values."
            ) from error

    nan_columns = [
        column for column in selected_columns if clean_data[column].isna().any()
    ]
    if nan_columns:
        columns = ", ".join(nan_columns)
        raise ValueError(
            f"MOSFET Id-Vgs CSV contains NaN or missing values in: {columns}."
        )

    return clean_data.sort_values("vgs_v", kind="mergesort").reset_index(drop=True)


def load_mosfet_id_vds_curve_csv(path: str | PathLike[str]) -> pd.DataFrame:
    """Load n-channel enhancement MOSFET Id-Vds output-curve data.

    The returned frame contains numeric ``vgs_v``, ``vds_v``, and ``id_a``
    columns sorted by ``vgs_v`` and then ``vds_v``. Current sign is preserved.
    """
    csv_path = Path(path)
    try:
        data = pd.read_csv(csv_path)
    except EmptyDataError as error:
        raise ValueError("MOSFET Id-Vds CSV is empty.") from error

    missing_columns = [
        column
        for column in REQUIRED_MOSFET_ID_VDS_COLUMNS
        if column not in data.columns
    ]
    if missing_columns:
        missing = ", ".join(missing_columns)
        required = ", ".join(REQUIRED_MOSFET_ID_VDS_COLUMNS)
        raise ValueError(
            f"Missing required MOSFET Id-Vds CSV column(s): {missing}. "
            f"Required columns are: {required}."
        )

    clean_data = data.loc[:, REQUIRED_MOSFET_ID_VDS_COLUMNS].copy()
    if clean_data.empty:
        raise ValueError("MOSFET Id-Vds CSV must contain at least one data row.")

    for column in REQUIRED_MOSFET_ID_VDS_COLUMNS:
        try:
            clean_data[column] = pd.to_numeric(clean_data[column], errors="raise")
        except (TypeError, ValueError) as error:
            raise ValueError(
                f"Column '{column}' must contain only numeric values."
            ) from error

    nan_columns = [
        column
        for column in REQUIRED_MOSFET_ID_VDS_COLUMNS
        if clean_data[column].isna().any()
    ]
    if nan_columns:
        columns = ", ".join(nan_columns)
        raise ValueError(
            f"MOSFET Id-Vds CSV contains NaN or missing values in: {columns}."
        )

    return clean_data.sort_values(
        ["vgs_v", "vds_v"],
        kind="mergesort",
    ).reset_index(drop=True)


def group_mosfet_id_vds_curves_by_vgs(
    data: pd.DataFrame,
) -> dict[float, pd.DataFrame]:
    """Return Id-Vds output curves keyed by their stepped ``vgs_v`` value."""
    required_columns = set(REQUIRED_MOSFET_ID_VDS_COLUMNS)
    missing_columns = required_columns.difference(data.columns)
    if missing_columns:
        raise ValueError(
            "MOSFET Id-Vds grouping requires column(s): "
            f"{', '.join(sorted(missing_columns))}."
        )
    if data.empty:
        raise ValueError("MOSFET Id-Vds grouping requires at least one data row.")

    clean_data = data.loc[:, REQUIRED_MOSFET_ID_VDS_COLUMNS].copy()
    for column in REQUIRED_MOSFET_ID_VDS_COLUMNS:
        values = pd.to_numeric(clean_data[column], errors="raise")
        if values.isna().any():
            raise ValueError(
                f"MOSFET Id-Vds grouping contains NaN or missing values in: {column}."
            )
        clean_data[column] = values

    sorted_data = clean_data.sort_values(
        ["vgs_v", "vds_v"],
        kind="mergesort",
    ).reset_index(drop=True)
    return {
        float(vgs_v): curve.reset_index(drop=True)
        for vgs_v, curve in sorted_data.groupby("vgs_v", sort=True)
    }


def load_curve_csv(path: str | PathLike[str]) -> pd.DataFrame:
    """Load diode curve data from a CSV file.

    This compatibility wrapper currently loads the M1 diode CSV schema only.
    """
    return load_diode_curve_csv(path)
