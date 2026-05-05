import numpy as np
import pandas as pd
import pytest

from curvecraft.fitting import extract_rdson_by_vgs, extract_rdson_for_curve


def test_extract_rdson_for_curve_recovers_known_linear_resistance() -> None:
    vds = np.array([0.0, 0.05, 0.1, 0.15])
    current = vds / 10.0

    result = extract_rdson_for_curve(vds, current, max_vds_v=0.1)

    assert result.rds_on_ohm == pytest.approx(10.0)
    assert result.conductance_siemens == pytest.approx(0.1)
    assert result.selected_point_count == 3
    assert abs(result.fit_intercept_a) < 1e-15


def test_extract_rdson_by_vgs_returns_one_estimate_per_vgs() -> None:
    data = pd.DataFrame(
        {
            "vgs_v": [2.0, 2.0, 2.0, 3.0, 3.0, 3.0],
            "vds_v": [0.0, 0.05, 0.1, 0.0, 0.05, 0.1],
            "id_a": [0.0, 0.005, 0.01, 0.0, 0.01, 0.02],
        }
    )

    results = extract_rdson_by_vgs(data, max_vds_v=0.1)

    assert [estimate.vgs_v for estimate in results] == [2.0, 3.0]
    assert results[0].rds_on_ohm == pytest.approx(10.0)
    assert results[1].rds_on_ohm == pytest.approx(5.0)


def test_extract_rdson_for_curve_rejects_insufficient_low_vds_points() -> None:
    vds = np.array([0.0, 0.5, 1.0])
    current = np.array([0.0, 0.05, 0.1])

    with pytest.raises(ValueError, match="too few low-Vds points"):
        extract_rdson_for_curve(vds, current, max_vds_v=0.0)


def test_extract_rdson_for_curve_rejects_nonpositive_conductance() -> None:
    vds = np.array([0.0, 0.05, 0.1])
    current = np.array([0.0, -0.01, -0.02])

    with pytest.raises(ValueError, match="positive low-Vds conductance"):
        extract_rdson_for_curve(vds, current, max_vds_v=0.1)


def test_extract_rdson_for_curve_rejects_duplicate_low_vds_only() -> None:
    vds = np.array([0.05, 0.05, 0.05])
    current = np.array([0.001, 0.002, 0.003])

    with pytest.raises(ValueError, match="two distinct low-Vds voltages"):
        extract_rdson_for_curve(vds, current, max_vds_v=0.05)


def test_extract_rdson_for_curve_handles_noisy_synthetic_data_reasonably() -> None:
    rng = np.random.default_rng(123)
    vds = np.linspace(0.0, 0.2, 12)
    clean_current = vds / 8.0
    noisy_current = clean_current + rng.normal(0.0, 2e-4, size=vds.shape)

    result = extract_rdson_for_curve(vds, noisy_current, max_vds_v=0.2)

    assert result.rds_on_ohm == pytest.approx(8.0, rel=0.08)
    assert result.rmse_current_a > 0
