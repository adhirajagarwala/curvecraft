import numpy as np
import pandas as pd
import pytest

from curvecraft.fitting import fit_mosfet_id_vds
from curvecraft.models import MosfetLevel1Parameters, mosfet_level1_id_vds_current


def test_fit_mosfet_id_vds_recovers_beta_and_lambda_with_fixed_vth() -> None:
    expected = MosfetLevel1Parameters(
        vth_v=1.1,
        beta_a_per_v2=2.2e-3,
        lambda_1_per_v=0.04,
    )
    data = _synthetic_id_vds_data(expected)

    result = fit_mosfet_id_vds(data, fixed_vth_v=expected.vth_v)

    assert result.success
    assert result.fitted_parameters == ("beta_a_per_v2", "lambda_1_per_v")
    assert result.fixed_parameters == ("vth_v",)
    assert result.parameters.vth_v == expected.vth_v
    assert result.parameters.beta_a_per_v2 == pytest.approx(
        expected.beta_a_per_v2,
        rel=0.03,
    )
    assert result.parameters.lambda_1_per_v == pytest.approx(
        expected.lambda_1_per_v,
        abs=0.01,
    )
    assert result.metrics.normalized_rmse_current < 1e-6


def test_fit_mosfet_id_vds_can_fit_vth_jointly_for_synthetic_data() -> None:
    expected = MosfetLevel1Parameters(
        vth_v=1.2,
        beta_a_per_v2=1.8e-3,
        lambda_1_per_v=0.03,
    )
    data = _synthetic_id_vds_data(expected)

    result = fit_mosfet_id_vds(data)

    assert result.fitted_parameters == (
        "vth_v",
        "beta_a_per_v2",
        "lambda_1_per_v",
    )
    assert result.parameters.vth_v == pytest.approx(expected.vth_v, abs=0.08)
    assert result.parameters.beta_a_per_v2 == pytest.approx(
        expected.beta_a_per_v2,
        rel=0.15,
    )
    assert result.parameters.lambda_1_per_v == pytest.approx(
        expected.lambda_1_per_v,
        abs=0.03,
    )
    assert any("vth_v fitted jointly" in note for note in result.notes)


def test_fit_mosfet_id_vds_rejects_insufficient_positive_current_data() -> None:
    data = pd.DataFrame(
        {
            "vgs_v": [0.0, 1.0, 2.0],
            "vds_v": [0.0, 0.5, 1.0],
            "id_a": [0.0, -1e-9, 1e-6],
        }
    )

    with pytest.raises(ValueError, match="positive-current points"):
        fit_mosfet_id_vds(data, fixed_vth_v=1.0)


def test_fit_mosfet_id_vds_rejects_missing_required_columns() -> None:
    data = pd.DataFrame({"vgs_v": [2.0], "id_a": [1e-6]})

    with pytest.raises(ValueError, match="vds_v"):
        fit_mosfet_id_vds(data, fixed_vth_v=1.0)


def test_fit_mosfet_id_vds_notes_negative_current_handling() -> None:
    expected = MosfetLevel1Parameters(
        vth_v=1.1,
        beta_a_per_v2=2e-3,
        lambda_1_per_v=0.02,
    )
    data = _synthetic_id_vds_data(expected)
    data.loc[0, "id_a"] = -1e-9

    result = fit_mosfet_id_vds(data, fixed_vth_v=expected.vth_v)

    assert result.used_points == len(data) - 1
    assert any("negative-current" in note for note in result.notes)


def _synthetic_id_vds_data(parameters: MosfetLevel1Parameters) -> pd.DataFrame:
    vgs_values = np.array([0.5, 1.5, 2.0, 2.5, 3.0])
    vds_values = np.linspace(0.0, 4.0, 41)
    rows: list[tuple[float, float, float]] = []
    for vgs_v in vgs_values:
        current = np.asarray(
            mosfet_level1_id_vds_current(vgs_v, vds_values, parameters)
        )
        rows.extend(
            (float(vgs_v), float(vds_v), float(id_a))
            for vds_v, id_a in zip(vds_values, current, strict=True)
        )
    return pd.DataFrame(rows, columns=["vgs_v", "vds_v", "id_a"])
