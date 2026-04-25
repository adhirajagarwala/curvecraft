import numpy as np

from curvecraft.plotting import plot_iv_linear, plot_iv_semilog_y


def test_plot_iv_linear_creates_png(tmp_path) -> None:  # type: ignore[no-untyped-def]
    voltage = np.array([-0.1, 0.0, 0.1, 0.2])
    measured = np.array([-1e-12, 0.0, 1e-10, 1e-8])
    model = np.array([-1e-12, 0.0, 1.1e-10, 0.9e-8])
    output_path = tmp_path / "linear.png"

    result = plot_iv_linear(voltage, measured, model, output_path)

    assert result == output_path
    assert output_path.exists()
    assert output_path.stat().st_size > 0


def test_plot_iv_semilog_masks_nonpositive_currents_and_creates_png(
    tmp_path,
) -> None:  # type: ignore[no-untyped-def]
    voltage = np.array([-0.1, 0.0, 0.1, 0.2])
    measured = np.array([-1e-12, 0.0, 1e-10, 1e-8])
    model = np.array([-1e-12, 0.0, 1.1e-10, 0.9e-8])
    output_path = tmp_path / "semilog.png"

    result = plot_iv_semilog_y(voltage, measured, model, output_path)

    assert result == output_path
    assert output_path.exists()
    assert output_path.stat().st_size > 0
