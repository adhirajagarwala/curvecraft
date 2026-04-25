import numpy as np
import pandas as pd
import pytest

from curvecraft.fitting import fit_mosfet_id_vgs
from curvecraft.models import MosfetLevel1Parameters, mosfet_level1_current


def test_fit_mosfet_id_vgs_recovers_synthetic_parameters() -> None:
    expected = MosfetLevel1Parameters(vth_v=1.25, beta_a_per_v2=2.2e-3, vds_v=5.0)
    vgs = np.linspace(0.0, 3.5, 80)
    current = mosfet_level1_current(vgs, expected)
    data = pd.DataFrame({"vgs_v": vgs, "id_a": current, "vds_v": 5.0})

    result = fit_mosfet_id_vgs(data)

    assert result.success
    assert result.fixed_vds_v == 5.0
    assert result.used_points == result.positive_current_points
    assert result.parameters.lambda_1_per_v == 0.0
    assert result.parameters.vth_v == pytest.approx(expected.vth_v, abs=0.02)
    assert result.parameters.beta_a_per_v2 == pytest.approx(
        expected.beta_a_per_v2,
        rel=0.08,
    )
    assert result.metrics.rmse_log10_current is not None


def test_fit_mosfet_id_vgs_accepts_explicit_fixed_vds_without_vds_column() -> None:
    expected = MosfetLevel1Parameters(vth_v=1.0, beta_a_per_v2=1.5e-3, vds_v=3.3)
    vgs = np.linspace(0.0, 3.0, 70)
    current = mosfet_level1_current(vgs, expected)
    data = pd.DataFrame({"vgs_v": vgs, "id_a": current})

    result = fit_mosfet_id_vgs(data, fixed_vds_v=3.3)

    assert result.fixed_vds_v == 3.3
    assert result.parameters.vds_v == 3.3


def test_fit_mosfet_id_vgs_rejects_insufficient_positive_current_points() -> None:
    data = pd.DataFrame(
        {
            "vgs_v": [0.0, 1.0, 2.0, 3.0],
            "id_a": [0.0, -1e-9, 0.0, 1e-6],
            "vds_v": [5.0, 5.0, 5.0, 5.0],
        }
    )

    with pytest.raises(ValueError, match="positive-current points"):
        fit_mosfet_id_vgs(data)


def test_fit_mosfet_id_vgs_rejects_invalid_fixed_vds() -> None:
    data = pd.DataFrame(
        {
            "vgs_v": [0.0, 1.0, 2.0, 3.0],
            "id_a": [0.0, 1e-8, 1e-6, 1e-4],
        }
    )

    with pytest.raises(ValueError, match="fixed Vds"):
        fit_mosfet_id_vgs(data, fixed_vds_v=0.0)


def test_fit_mosfet_id_vgs_rejects_nonconstant_vds_column() -> None:
    data = pd.DataFrame(
        {
            "vgs_v": [0.0, 1.0, 2.0, 3.0],
            "id_a": [0.0, 1e-8, 1e-6, 1e-4],
            "vds_v": [5.0, 5.0, 4.5, 5.0],
        }
    )

    with pytest.raises(ValueError, match="fixed Vds"):
        fit_mosfet_id_vgs(data)


def test_fit_mosfet_id_vgs_notes_nonpositive_current_handling() -> None:
    expected = MosfetLevel1Parameters(vth_v=1.2, beta_a_per_v2=2e-3, vds_v=5.0)
    vgs = np.linspace(0.0, 3.0, 80)
    current = np.asarray(mosfet_level1_current(vgs, expected))
    current[0] = -1e-9
    data = pd.DataFrame({"vgs_v": vgs, "id_a": current, "vds_v": 5.0})

    result = fit_mosfet_id_vgs(data)

    assert result.total_points == len(data)
    assert result.positive_current_points < result.total_points
    assert any("nonpositive-current" in note for note in result.notes)
