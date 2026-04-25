"""CSV loading helpers."""

from os import PathLike
from pathlib import Path

import pandas as pd

from curvecraft.io.schema import REQUIRED_DIODE_COLUMNS


def load_diode_curve_csv(path: str | PathLike[str]) -> pd.DataFrame:
    """Load diode I-V curve data from a CSV file.

    The returned frame contains the required columns as numeric values:
    ``voltage_v`` and ``current_a``.
    """
    csv_path = Path(path)
    data = pd.read_csv(csv_path)

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
    for column in REQUIRED_DIODE_COLUMNS:
        try:
            clean_data[column] = pd.to_numeric(clean_data[column], errors="raise")
        except (TypeError, ValueError) as error:
            raise ValueError(
                f"Column '{column}' must contain only numeric values."
            ) from error

    return clean_data


def load_curve_csv(path: str | PathLike[str]) -> pd.DataFrame:
    """Load diode curve data from a CSV file.

    This compatibility wrapper currently loads the M1 diode CSV schema only.
    """
    return load_diode_curve_csv(path)
