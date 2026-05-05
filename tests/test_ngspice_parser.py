from pathlib import Path

import pandas as pd
import pytest

from curvecraft.spice import (
    parse_mosfet_id_vds_ngspice_output_file,
    parse_mosfet_id_vds_ngspice_output_text,
    parse_mosfet_id_vgs_ngspice_output_file,
    parse_mosfet_id_vgs_ngspice_output_text,
    parse_ngspice_dc_output_file,
    parse_ngspice_dc_output_text,
)


def test_parse_ngspice_dc_output_file_uses_diode_current_sign() -> None:
    fixture = Path(__file__).parent / "fixtures" / "ngspice" / "diode_dc_output.txt"

    result = parse_ngspice_dc_output_file(fixture)

    expected = pd.DataFrame(
        {
            "voltage_v": [-0.1, 0.0, 0.1, 0.2],
            "current_a": [-9.99e-13, 0.0, 1.2e-11, 2.0e-10],
        }
    )
    pd.testing.assert_frame_equal(result, expected)


def test_parse_ngspice_dc_output_text_rejects_output_without_rows() -> None:
    with pytest.raises(ValueError, match="No ngspice DC sweep rows"):
        parse_ngspice_dc_output_text("No. of Data Rows : 0\n")


def test_parse_ngspice_dc_output_text_ignores_non_index_numeric_footer() -> None:
    text = (
        "Index   v(anode)        i(vin)\n"
        "0       0.000000e+00   -0.000000e+00\n"
        "1       1.000000e-01   -1.200000e-11\n"
        "1.5     2.0            3.0\n"
    )

    result = parse_ngspice_dc_output_text(text)

    assert result["voltage_v"].tolist() == [0.0, 0.1]


def test_parse_mosfet_id_vgs_ngspice_output_file_uses_drain_current_sign() -> None:
    fixture = (
        Path(__file__).parent / "fixtures" / "ngspice" / "mosfet_id_vgs_output.txt"
    )

    result = parse_mosfet_id_vgs_ngspice_output_file(fixture)

    expected = pd.DataFrame(
        {
            "vgs_v": [0.0, 1.0, 1.5, 2.0],
            "id_a": [0.0, 0.0, 2.5e-4, 1.0e-3],
        }
    )
    pd.testing.assert_frame_equal(result, expected)


def test_parse_mosfet_id_vgs_ngspice_output_text_rejects_output_without_rows() -> None:
    with pytest.raises(ValueError, match="No MOSFET Id-Vgs ngspice"):
        parse_mosfet_id_vgs_ngspice_output_text("No. of Data Rows : 0\n")


def test_parse_mosfet_id_vds_ngspice_output_file_uses_drain_current_sign() -> None:
    fixture = (
        Path(__file__).parent / "fixtures" / "ngspice" / "mosfet_id_vds_output.txt"
    )

    result = parse_mosfet_id_vds_ngspice_output_file(fixture, fixed_vgs_v=2.0)

    expected = pd.DataFrame(
        {
            "vgs_v": [2.0, 2.0, 2.0, 2.0],
            "vds_v": [0.0, 0.5, 1.0, 2.0],
            "id_a": [0.0, 7.5e-4, 1.0e-3, 1.0e-3],
        }
    )
    pd.testing.assert_frame_equal(result, expected)


def test_parse_mosfet_id_vds_ngspice_output_text_rejects_output_without_rows() -> None:
    with pytest.raises(ValueError, match="No MOSFET Id-Vds ngspice"):
        parse_mosfet_id_vds_ngspice_output_text(
            "No. of Data Rows : 0\n",
            fixed_vgs_v=2.0,
        )
