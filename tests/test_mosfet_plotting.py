import numpy as np

from curvecraft.plotting import (
    plot_mosfet_id_vgs_linear,
    plot_mosfet_id_vgs_semilog_y,
)


def test_plot_mosfet_id_vgs_linear_creates_png(tmp_path) -> None:  # type: ignore[no-untyped-def]
    vgs = np.array([0.0, 1.0, 2.0, 3.0])
    measured = np.array([0.0, 0.0, 1e-4, 8e-4])
    model = np.array([0.0, 0.0, 1.1e-4, 7.8e-4])
    output_path = tmp_path / "mosfet-linear.png"

    result = plot_mosfet_id_vgs_linear(vgs, measured, model, output_path)

    assert result == output_path
    assert output_path.exists()
    assert output_path.stat().st_size > 0


def test_plot_mosfet_id_vgs_semilog_creates_png(tmp_path) -> None:  # type: ignore[no-untyped-def]
    vgs = np.array([0.0, 1.0, 2.0, 3.0])
    measured = np.array([0.0, 1e-9, 1e-4, 8e-4])
    model = np.array([0.0, 1.2e-9, 1.1e-4, 7.8e-4])
    output_path = tmp_path / "mosfet-semilog.png"

    result = plot_mosfet_id_vgs_semilog_y(vgs, measured, model, output_path)

    assert result == output_path
    assert output_path.exists()
    assert output_path.stat().st_size > 0


def test_plot_mosfet_id_vgs_semilog_masks_nonpositive_currents(
    tmp_path,
) -> None:  # type: ignore[no-untyped-def]
    vgs = np.array([0.0, 1.0, 2.0, 3.0])
    measured = np.array([-1e-9, 0.0, 1e-4, 8e-4])
    model = np.array([0.0, 0.0, 1.1e-4, 7.8e-4])
    output_path = tmp_path / "mosfet-semilog-nonpositive.png"

    result = plot_mosfet_id_vgs_semilog_y(vgs, measured, model, output_path)

    assert result == output_path
    assert output_path.exists()
    assert output_path.stat().st_size > 0
