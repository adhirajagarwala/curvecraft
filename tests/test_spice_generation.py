from curvecraft.models import DiodeParameters, MosfetLevel1Parameters
from curvecraft.spice import (
    diode_dc_sweep_netlist,
    diode_model_card,
    mosfet_id_vgs_dc_sweep_netlist,
    mosfet_level1_model_card,
    write_diode_netlist,
    write_mosfet_id_vgs_netlist,
)


def test_diode_model_card_contains_ngspice_parameter_mapping() -> None:
    parameters = DiodeParameters(
        saturation_current_a=2e-12,
        ideality_factor=1.7,
        series_resistance_ohm=3.5,
    )

    model_card = diode_model_card(parameters, model_name="fit_diode")

    assert model_card == ".model fit_diode D (IS=2e-12 N=1.7 RS=3.5)"


def test_diode_dc_sweep_netlist_contains_expected_lines() -> None:
    parameters = DiodeParameters(
        saturation_current_a=1e-12,
        ideality_factor=1.5,
        series_resistance_ohm=10.0,
    )

    netlist = diode_dc_sweep_netlist(
        parameters,
        start_v=-0.2,
        stop_v=0.7,
        step_v=0.05,
    )

    assert "* CurveCraft diode DC sweep validation" in netlist
    assert "Vin anode 0 0" in netlist
    assert "D1 anode 0 curve_diode" in netlist
    assert ".model curve_diode D (IS=1e-12 N=1.5 RS=10)" in netlist
    assert ".dc Vin -0.2 0.7 0.05" in netlist
    assert ".print dc v(anode) i(Vin)" in netlist
    assert netlist.endswith(".end\n")


def test_diode_dc_sweep_netlist_does_not_include_unrelated_devices() -> None:
    parameters = DiodeParameters(
        saturation_current_a=1e-12,
        ideality_factor=1.5,
        series_resistance_ohm=0.0,
    )

    netlist = diode_dc_sweep_netlist(parameters).lower()

    assert "mos" not in netlist
    assert "nmos" not in netlist
    assert "pmos" not in netlist
    assert "q1" not in netlist


def test_write_diode_netlist_creates_file(tmp_path) -> None:  # type: ignore[no-untyped-def]
    parameters = DiodeParameters(
        saturation_current_a=1e-12,
        ideality_factor=1.5,
        series_resistance_ohm=0.0,
    )
    path = tmp_path / "diode_validation.cir"

    result = write_diode_netlist(path, parameters)

    assert result == path
    assert path.read_text(encoding="utf-8").startswith(
        "* CurveCraft diode DC sweep validation"
    )


def test_mosfet_level1_model_card_contains_ngspice_parameter_mapping() -> None:
    parameters = MosfetLevel1Parameters(
        vth_v=1.2,
        beta_a_per_v2=0.002,
        lambda_1_per_v=0.01,
        vds_v=5.0,
    )

    model_card = mosfet_level1_model_card(parameters, model_name="fit_nmos")

    assert model_card == ".model fit_nmos NMOS (LEVEL=1 VTO=1.2 KP=0.002 LAMBDA=0.01)"


def test_mosfet_id_vgs_dc_sweep_netlist_contains_expected_lines() -> None:
    parameters = MosfetLevel1Parameters(
        vth_v=1.2,
        beta_a_per_v2=0.002,
        lambda_1_per_v=0.0,
        vds_v=5.0,
    )

    netlist = mosfet_id_vgs_dc_sweep_netlist(
        parameters,
        start_v=0.0,
        stop_v=4.0,
        step_v=0.1,
    )

    assert "* CurveCraft MOSFET Id-Vgs DC sweep validation" in netlist
    assert "Vds drain 0 5" in netlist
    assert "Vgs gate 0 0" in netlist
    assert "M1 drain gate 0 0 curve_nmos W=1 L=1" in netlist
    assert ".model curve_nmos NMOS (LEVEL=1 VTO=1.2 KP=0.002 LAMBDA=0)" in netlist
    assert ".dc Vgs 0 4 0.1" in netlist
    assert ".print dc v(gate) i(Vds)" in netlist
    assert netlist.endswith(".end\n")


def test_mosfet_id_vgs_netlist_does_not_include_output_sweep() -> None:
    parameters = MosfetLevel1Parameters(vth_v=1.0, beta_a_per_v2=0.001, vds_v=5.0)

    netlist = mosfet_id_vgs_dc_sweep_netlist(parameters)

    assert ".dc Vgs" in netlist
    assert ".dc Vds" not in netlist


def test_write_mosfet_id_vgs_netlist_creates_file(tmp_path) -> None:  # type: ignore[no-untyped-def]
    parameters = MosfetLevel1Parameters(vth_v=1.0, beta_a_per_v2=0.001, vds_v=5.0)
    path = tmp_path / "mosfet_id_vgs_validation.cir"

    result = write_mosfet_id_vgs_netlist(path, parameters)

    assert result == path
    assert path.read_text(encoding="utf-8").startswith(
        "* CurveCraft MOSFET Id-Vgs DC sweep validation"
    )
