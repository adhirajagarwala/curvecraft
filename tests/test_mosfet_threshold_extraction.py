import numpy as np
import pytest

from curvecraft.fitting import (
    estimate_initial_mosfet_params,
    estimate_threshold_by_constant_current,
    estimate_threshold_by_sqrt_id_linear_fit,
)
from curvecraft.models import MosfetLevel1Parameters, mosfet_level1_current


def test_constant_current_threshold_recovers_synthetic_vth_approximately() -> None:
    parameters = MosfetLevel1Parameters(vth_v=1.2, beta_a_per_v2=2e-3, vds_v=5.0)
    vgs = np.linspace(0.0, 3.0, 121)
    current = mosfet_level1_current(vgs, parameters)

    estimate = estimate_threshold_by_constant_current(vgs, current, 2e-6)

    assert estimate == pytest.approx(1.244, abs=0.01)


def test_constant_current_threshold_raises_when_target_is_not_crossed() -> None:
    vgs = np.array([0.0, 1.0, 2.0])
    current = np.array([0.0, 1e-6, 2e-6])

    with pytest.raises(ValueError, match="not crossed"):
        estimate_threshold_by_constant_current(vgs, current, 1e-3)


def test_sqrt_id_threshold_recovers_synthetic_vth_approximately() -> None:
    parameters = MosfetLevel1Parameters(vth_v=1.2, beta_a_per_v2=2e-3, vds_v=5.0)
    vgs = np.linspace(0.0, 3.0, 121)
    current = mosfet_level1_current(vgs, parameters)

    result = estimate_threshold_by_sqrt_id_linear_fit(vgs, current)

    assert result.vth_v == pytest.approx(1.2, abs=1e-12)
    assert result.slope_sqrt_a_per_v > 0
    assert result.selected_point_count >= 3


def test_sqrt_id_threshold_rejects_insufficient_positive_current_data() -> None:
    vgs = np.array([0.0, 1.0, 2.0])
    current = np.array([0.0, 0.0, 1e-6])

    with pytest.raises(ValueError, match="positive-current points"):
        estimate_threshold_by_sqrt_id_linear_fit(vgs, current)


def test_sqrt_id_threshold_handles_noisy_synthetic_data_reasonably() -> None:
    rng = np.random.default_rng(123)
    parameters = MosfetLevel1Parameters(vth_v=1.4, beta_a_per_v2=1.5e-3, vds_v=5.0)
    vgs = np.linspace(0.0, 3.5, 160)
    clean_current = np.asarray(mosfet_level1_current(vgs, parameters))
    noise_scale = np.where(clean_current > 0, 0.03 * clean_current, 0.0)
    noisy_current = np.maximum(clean_current + rng.normal(0.0, noise_scale), 0.0)

    result = estimate_threshold_by_sqrt_id_linear_fit(vgs, noisy_current)

    assert result.vth_v == pytest.approx(1.4, abs=0.08)


def test_initial_mosfet_params_estimates_vth_and_beta() -> None:
    parameters = MosfetLevel1Parameters(vth_v=1.1, beta_a_per_v2=2.4e-3, vds_v=5.0)
    vgs = np.linspace(0.0, 3.0, 120)
    current = mosfet_level1_current(vgs, parameters)

    estimate = estimate_initial_mosfet_params(vgs, current)

    assert estimate.vth_v == pytest.approx(parameters.vth_v, abs=1e-12)
    assert estimate.beta_a_per_v2 == pytest.approx(
        parameters.beta_a_per_v2,
        rel=1e-12,
    )
    assert estimate.method == "sqrt_id_linear_fit"
