from pathlib import Path

import pandas as pd
import pytest

from curvecraft.io.csv_loader import load_diode_curve_csv


def test_load_diode_curve_csv_returns_clean_dataframe(tmp_path: Path) -> None:
    csv_path = tmp_path / "diode.csv"
    csv_path.write_text(
        "voltage_v,current_a,ignored\n"
        "-0.1,-1e-9,note\n"
        "0.0,0.0,note\n",
        encoding="utf-8",
    )

    result = load_diode_curve_csv(csv_path)

    expected = pd.DataFrame(
        {
            "voltage_v": [-0.1, 0.0],
            "current_a": [-1e-9, 0.0],
        }
    )
    pd.testing.assert_frame_equal(result, expected)


def test_load_diode_curve_csv_rejects_missing_required_column(
    tmp_path: Path,
) -> None:
    csv_path = tmp_path / "missing-current.csv"
    csv_path.write_text("voltage_v\n0.1\n", encoding="utf-8")

    with pytest.raises(ValueError, match="Missing required diode CSV column"):
        load_diode_curve_csv(csv_path)


def test_load_diode_curve_csv_rejects_non_numeric_values(tmp_path: Path) -> None:
    csv_path = tmp_path / "non-numeric.csv"
    csv_path.write_text(
        "voltage_v,current_a\n"
        "0.1,not-a-number\n",
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="current_a.*numeric"):
        load_diode_curve_csv(csv_path)


def test_load_diode_curve_csv_rejects_duplicate_required_column(
    tmp_path: Path,
) -> None:
    csv_path = tmp_path / "duplicate-column.csv"
    csv_path.write_text(
        "voltage_v,current_a,current_a\n"
        "0.1,1e-9,2e-9\n",
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="duplicate column.*current_a"):
        load_diode_curve_csv(csv_path)


def test_load_diode_curve_csv_rejects_empty_file(tmp_path: Path) -> None:
    csv_path = tmp_path / "empty.csv"
    csv_path.write_text("", encoding="utf-8")

    with pytest.raises(ValueError, match="empty"):
        load_diode_curve_csv(csv_path)


def test_load_diode_curve_csv_sorts_by_voltage(tmp_path: Path) -> None:
    csv_path = tmp_path / "unsorted.csv"
    csv_path.write_text(
        "voltage_v,current_a\n"
        "0.2,1e-8\n"
        "-0.1,-1e-9\n"
        "0.0,0.0\n",
        encoding="utf-8",
    )

    result = load_diode_curve_csv(csv_path)

    assert result["voltage_v"].tolist() == [-0.1, 0.0, 0.2]
    assert result["current_a"].tolist() == [-1e-9, 0.0, 1e-8]
