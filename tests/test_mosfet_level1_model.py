import numpy as np

from curvecraft.models import (
    MosfetLevel1Parameters,
    mosfet_level1_current,
    mosfet_level1_id_vds_current,
)


def test_mosfet_level1_current_is_zero_below_threshold() -> None:
    parameters = MosfetLevel1Parameters(vth_v=1.5, beta_a_per_v2=1e-3, vds_v=5.0)
    vgs = np.array([0.0, 1.0, 1.5])

    current = mosfet_level1_current(vgs, parameters)

    np.testing.assert_allclose(current, np.zeros_like(vgs))


def test_mosfet_level1_current_increases_above_threshold() -> None:
    parameters = MosfetLevel1Parameters(vth_v=1.0, beta_a_per_v2=1e-3, vds_v=5.0)
    vgs = np.array([1.1, 1.5, 2.0, 2.5])

    current = mosfet_level1_current(vgs, parameters)

    assert np.all(np.diff(current) > 0)


def test_mosfet_level1_higher_beta_increases_current() -> None:
    low_beta = MosfetLevel1Parameters(vth_v=1.0, beta_a_per_v2=1e-3, vds_v=5.0)
    high_beta = MosfetLevel1Parameters(vth_v=1.0, beta_a_per_v2=2e-3, vds_v=5.0)

    assert mosfet_level1_current(2.0, high_beta) > mosfet_level1_current(
        2.0,
        low_beta,
    )


def test_mosfet_level1_higher_vth_reduces_current_at_fixed_vgs() -> None:
    low_vth = MosfetLevel1Parameters(vth_v=1.0, beta_a_per_v2=1e-3, vds_v=5.0)
    high_vth = MosfetLevel1Parameters(vth_v=1.5, beta_a_per_v2=1e-3, vds_v=5.0)

    assert mosfet_level1_current(2.5, high_vth) < mosfet_level1_current(
        2.5,
        low_vth,
    )


def test_mosfet_level1_positive_lambda_increases_current() -> None:
    no_modulation = MosfetLevel1Parameters(
        vth_v=1.0,
        beta_a_per_v2=1e-3,
        lambda_1_per_v=0.0,
        vds_v=5.0,
    )
    with_modulation = MosfetLevel1Parameters(
        vth_v=1.0,
        beta_a_per_v2=1e-3,
        lambda_1_per_v=0.02,
        vds_v=5.0,
    )

    assert mosfet_level1_current(2.0, with_modulation) > mosfet_level1_current(
        2.0,
        no_modulation,
    )


def test_mosfet_level1_vectorized_input_matches_expected_values() -> None:
    parameters = MosfetLevel1Parameters(vth_v=1.0, beta_a_per_v2=2e-3, vds_v=5.0)
    vgs = np.array([0.5, 1.0, 2.0, 3.0])

    current = mosfet_level1_current(vgs, parameters)

    expected = np.array([0.0, 0.0, 1e-3, 4e-3])
    np.testing.assert_allclose(current, expected)


def test_mosfet_level1_uses_triode_region_when_vds_is_below_overdrive() -> None:
    parameters = MosfetLevel1Parameters(vth_v=1.0, beta_a_per_v2=1e-3, vds_v=0.5)

    current = mosfet_level1_current(2.0, parameters)

    np.testing.assert_allclose(current, 3.75e-4)


def test_mosfet_level1_id_vds_current_is_zero_below_threshold() -> None:
    parameters = MosfetLevel1Parameters(vth_v=1.5, beta_a_per_v2=1e-3)

    current = mosfet_level1_id_vds_current(1.0, 2.0, parameters)

    assert current == 0.0


def test_mosfet_level1_id_vds_current_increases_in_triode_region() -> None:
    parameters = MosfetLevel1Parameters(vth_v=1.0, beta_a_per_v2=1e-3)
    vds = np.array([0.1, 0.2, 0.3])

    current = mosfet_level1_id_vds_current(2.0, vds, parameters)

    assert np.all(np.diff(current) > 0)


def test_mosfet_level1_id_vds_current_shows_saturation_behavior() -> None:
    parameters = MosfetLevel1Parameters(vth_v=1.0, beta_a_per_v2=2e-3)
    vds = np.array([0.5, 1.0, 2.0, 4.0])

    current = mosfet_level1_id_vds_current(2.0, vds, parameters)

    np.testing.assert_allclose(current[-1], current[-2])
    assert current[-1] == current[-3]


def test_mosfet_level1_id_vds_positive_lambda_increases_saturation_current() -> None:
    no_modulation = MosfetLevel1Parameters(
        vth_v=1.0,
        beta_a_per_v2=2e-3,
        lambda_1_per_v=0.0,
    )
    with_modulation = MosfetLevel1Parameters(
        vth_v=1.0,
        beta_a_per_v2=2e-3,
        lambda_1_per_v=0.02,
    )

    assert mosfet_level1_id_vds_current(
        2.0,
        4.0,
        with_modulation,
    ) > mosfet_level1_id_vds_current(2.0, 4.0, no_modulation)


def test_mosfet_level1_id_vds_higher_vgs_increases_current_at_fixed_vds() -> None:
    parameters = MosfetLevel1Parameters(vth_v=1.0, beta_a_per_v2=1e-3)

    low_vgs_current = mosfet_level1_id_vds_current(2.0, 0.5, parameters)
    high_vgs_current = mosfet_level1_id_vds_current(3.0, 0.5, parameters)

    assert high_vgs_current > low_vgs_current


def test_mosfet_level1_id_vds_vectorized_paired_inputs_match_expected_values() -> None:
    parameters = MosfetLevel1Parameters(vth_v=1.0, beta_a_per_v2=2e-3)
    vgs = np.array([0.5, 2.0, 2.0, 3.0])
    vds = np.array([1.0, 0.5, 2.0, 1.0])

    current = mosfet_level1_id_vds_current(vgs, vds, parameters)

    expected = np.array([0.0, 7.5e-4, 1.0e-3, 3.0e-3])
    np.testing.assert_allclose(current, expected)
