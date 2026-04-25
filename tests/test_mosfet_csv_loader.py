from pathlib import Path

import pandas as pd
import pytest

from curvecraft.io.csv_loader import load_mosfet_id_vgs_curve_csv


def test_load_mosfet_id_vgs_curve_csv_returns_clean_dataframe(
    tmp_path: Path,
) -> None:
    csv_path = tmp_path / "mosfet-id-vgs.csv"
    csv_path.write_text(
        "vgs_v,id_a,vds_v,ignored\n"
        "0.0,0.0,5.0,note\n"
        "2.0,1.2e-3,5.0,note\n",
        encoding="utf-8",
    )

    result = load_mosfet_id_vgs_curve_csv(csv_path)

    expected = pd.DataFrame(
        {
            "vgs_v": [0.0, 2.0],
            "id_a": [0.0, 1.2e-3],
            "vds_v": [5.0, 5.0],
        }
    )
    pd.testing.assert_frame_equal(result, expected)


def test_load_mosfet_id_vgs_curve_csv_allows_absent_vds(
    tmp_path: Path,
) -> None:
    csv_path = tmp_path / "mosfet-id-vgs-no-vds.csv"
    csv_path.write_text(
        "vgs_v,id_a\n"
        "0.0,0.0\n"
        "1.5,2.5e-4\n",
        encoding="utf-8",
    )

    result = load_mosfet_id_vgs_curve_csv(csv_path)

    assert result.columns.tolist() == ["vgs_v", "id_a"]
    assert result["id_a"].tolist() == [0.0, 2.5e-4]


def test_load_mosfet_id_vgs_curve_csv_preserves_current_sign(
    tmp_path: Path,
) -> None:
    csv_path = tmp_path / "mosfet-id-vgs-signed.csv"
    csv_path.write_text(
        "vgs_v,id_a\n"
        "0.0,-1e-9\n"
        "1.0,2e-6\n",
        encoding="utf-8",
    )

    result = load_mosfet_id_vgs_curve_csv(csv_path)

    assert result["id_a"].tolist() == [-1e-9, 2e-6]


def test_load_mosfet_id_vgs_curve_csv_rejects_missing_vgs_column(
    tmp_path: Path,
) -> None:
    csv_path = tmp_path / "missing-vgs.csv"
    csv_path.write_text("id_a\n1e-6\n", encoding="utf-8")

    with pytest.raises(ValueError, match="Missing required MOSFET Id-Vgs.*vgs_v"):
        load_mosfet_id_vgs_curve_csv(csv_path)


def test_load_mosfet_id_vgs_curve_csv_rejects_missing_id_column(
    tmp_path: Path,
) -> None:
    csv_path = tmp_path / "missing-id.csv"
    csv_path.write_text("vgs_v\n1.0\n", encoding="utf-8")

    with pytest.raises(ValueError, match="Missing required MOSFET Id-Vgs.*id_a"):
        load_mosfet_id_vgs_curve_csv(csv_path)


def test_load_mosfet_id_vgs_curve_csv_rejects_non_numeric_values(
    tmp_path: Path,
) -> None:
    csv_path = tmp_path / "non-numeric.csv"
    csv_path.write_text(
        "vgs_v,id_a\n"
        "1.0,not-a-number\n",
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="id_a.*numeric"):
        load_mosfet_id_vgs_curve_csv(csv_path)


def test_load_mosfet_id_vgs_curve_csv_rejects_empty_file(
    tmp_path: Path,
) -> None:
    csv_path = tmp_path / "empty.csv"
    csv_path.write_text("", encoding="utf-8")

    with pytest.raises(ValueError, match="empty"):
        load_mosfet_id_vgs_curve_csv(csv_path)


def test_load_mosfet_id_vgs_curve_csv_rejects_nan_values(
    tmp_path: Path,
) -> None:
    csv_path = tmp_path / "nan.csv"
    csv_path.write_text(
        "vgs_v,id_a,vds_v\n"
        "1.0,,5.0\n",
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="NaN or missing values.*id_a"):
        load_mosfet_id_vgs_curve_csv(csv_path)


def test_load_mosfet_id_vgs_curve_csv_sorts_by_vgs(
    tmp_path: Path,
) -> None:
    csv_path = tmp_path / "unsorted.csv"
    csv_path.write_text(
        "vgs_v,id_a\n"
        "2.0,1.0e-3\n"
        "0.0,0.0\n"
        "1.0,1.0e-6\n",
        encoding="utf-8",
    )

    result = load_mosfet_id_vgs_curve_csv(csv_path)

    assert result["vgs_v"].tolist() == [0.0, 1.0, 2.0]
    assert result["id_a"].tolist() == [0.0, 1.0e-6, 1.0e-3]
