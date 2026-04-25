from pathlib import Path

import pandas as pd
import pytest

from curvecraft.io.csv_loader import (
    group_mosfet_id_vds_curves_by_vgs,
    load_mosfet_id_vds_curve_csv,
)


def test_load_mosfet_id_vds_curve_csv_returns_clean_dataframe(
    tmp_path: Path,
) -> None:
    csv_path = tmp_path / "mosfet-id-vds.csv"
    csv_path.write_text(
        "vgs_v,vds_v,id_a,ignored\n"
        "2.0,0.0,0.0,note\n"
        "2.0,0.5,3.75e-4,note\n"
        "3.0,0.5,8.75e-4,note\n",
        encoding="utf-8",
    )

    result = load_mosfet_id_vds_curve_csv(csv_path)

    expected = pd.DataFrame(
        {
            "vgs_v": [2.0, 2.0, 3.0],
            "vds_v": [0.0, 0.5, 0.5],
            "id_a": [0.0, 3.75e-4, 8.75e-4],
        }
    )
    pd.testing.assert_frame_equal(result, expected)


def test_load_mosfet_id_vds_curve_csv_preserves_current_sign(
    tmp_path: Path,
) -> None:
    csv_path = tmp_path / "mosfet-id-vds-signed.csv"
    csv_path.write_text(
        "vgs_v,vds_v,id_a\n"
        "1.0,0.1,-1e-9\n"
        "2.0,0.1,2e-6\n",
        encoding="utf-8",
    )

    result = load_mosfet_id_vds_curve_csv(csv_path)

    assert result["id_a"].tolist() == [-1e-9, 2e-6]


def test_load_mosfet_id_vds_curve_csv_rejects_missing_vgs_column(
    tmp_path: Path,
) -> None:
    csv_path = tmp_path / "missing-vgs.csv"
    csv_path.write_text("vds_v,id_a\n0.1,1e-6\n", encoding="utf-8")

    with pytest.raises(ValueError, match="Missing required MOSFET Id-Vds.*vgs_v"):
        load_mosfet_id_vds_curve_csv(csv_path)


def test_load_mosfet_id_vds_curve_csv_rejects_missing_vds_column(
    tmp_path: Path,
) -> None:
    csv_path = tmp_path / "missing-vds.csv"
    csv_path.write_text("vgs_v,id_a\n2.0,1e-6\n", encoding="utf-8")

    with pytest.raises(ValueError, match="Missing required MOSFET Id-Vds.*vds_v"):
        load_mosfet_id_vds_curve_csv(csv_path)


def test_load_mosfet_id_vds_curve_csv_rejects_missing_id_column(
    tmp_path: Path,
) -> None:
    csv_path = tmp_path / "missing-id.csv"
    csv_path.write_text("vgs_v,vds_v\n2.0,0.1\n", encoding="utf-8")

    with pytest.raises(ValueError, match="Missing required MOSFET Id-Vds.*id_a"):
        load_mosfet_id_vds_curve_csv(csv_path)


def test_load_mosfet_id_vds_curve_csv_rejects_non_numeric_values(
    tmp_path: Path,
) -> None:
    csv_path = tmp_path / "non-numeric.csv"
    csv_path.write_text(
        "vgs_v,vds_v,id_a\n"
        "2.0,not-a-number,1e-6\n",
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="vds_v.*numeric"):
        load_mosfet_id_vds_curve_csv(csv_path)


def test_load_mosfet_id_vds_curve_csv_rejects_empty_file(
    tmp_path: Path,
) -> None:
    csv_path = tmp_path / "empty.csv"
    csv_path.write_text("", encoding="utf-8")

    with pytest.raises(ValueError, match="empty"):
        load_mosfet_id_vds_curve_csv(csv_path)


def test_load_mosfet_id_vds_curve_csv_rejects_nan_values(
    tmp_path: Path,
) -> None:
    csv_path = tmp_path / "nan.csv"
    csv_path.write_text(
        "vgs_v,vds_v,id_a\n"
        "2.0,,1e-6\n",
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="NaN or missing values.*vds_v"):
        load_mosfet_id_vds_curve_csv(csv_path)


def test_load_mosfet_id_vds_curve_csv_sorts_by_vgs_then_vds(
    tmp_path: Path,
) -> None:
    csv_path = tmp_path / "unsorted.csv"
    csv_path.write_text(
        "vgs_v,vds_v,id_a\n"
        "3.0,1.0,1.5e-3\n"
        "2.0,0.5,3.75e-4\n"
        "2.0,0.0,0.0\n"
        "3.0,0.5,8.75e-4\n",
        encoding="utf-8",
    )

    result = load_mosfet_id_vds_curve_csv(csv_path)

    assert result["vgs_v"].tolist() == [2.0, 2.0, 3.0, 3.0]
    assert result["vds_v"].tolist() == [0.0, 0.5, 0.5, 1.0]


def test_group_mosfet_id_vds_curves_by_vgs_returns_sorted_curves() -> None:
    data = pd.DataFrame(
        {
            "vgs_v": [3.0, 2.0, 3.0, 2.0],
            "vds_v": [1.0, 0.5, 0.5, 0.0],
            "id_a": [1.5e-3, 3.75e-4, 8.75e-4, 0.0],
        }
    )

    curves = group_mosfet_id_vds_curves_by_vgs(data)

    assert list(curves) == [2.0, 3.0]
    assert curves[2.0]["vds_v"].tolist() == [0.0, 0.5]
    assert curves[3.0]["vds_v"].tolist() == [0.5, 1.0]
