import numpy as np
import pandas as pd

from curvecraft.plotting import (
    plot_mosfet_id_vds_family,
    plot_mosfet_id_vds_measured_vs_fit,
)


def test_plot_mosfet_id_vds_family_creates_png(tmp_path) -> None:  # type: ignore[no-untyped-def]
    data = _example_id_vds_data()
    output_path = tmp_path / "mosfet-id-vds-family.png"

    result = plot_mosfet_id_vds_family(data, output_path)

    assert result == output_path
    assert output_path.exists()
    assert output_path.stat().st_size > 0


def test_plot_mosfet_id_vds_measured_vs_fit_creates_png(tmp_path) -> None:  # type: ignore[no-untyped-def]
    data = _example_id_vds_data()
    fitted_current = data["id_a"].to_numpy(dtype=float) * 1.02
    output_path = tmp_path / "mosfet-id-vds-fit.png"

    result = plot_mosfet_id_vds_measured_vs_fit(data, fitted_current, output_path)

    assert result == output_path
    assert output_path.exists()
    assert output_path.stat().st_size > 0


def test_plot_mosfet_id_vds_multiple_vgs_groups_without_crashing(
    tmp_path,
) -> None:  # type: ignore[no-untyped-def]
    data = _example_id_vds_data()
    output_path = tmp_path / "multi-vgs.png"

    result = plot_mosfet_id_vds_family(
        data.sample(frac=1.0, random_state=1),
        output_path,
    )

    assert result.exists()


def _example_id_vds_data() -> pd.DataFrame:
    vds = np.array([0.0, 0.5, 1.0])
    rows: list[tuple[float, float, float]] = []
    for vgs_v, scale in [(2.0, 1.0e-3), (3.0, 2.0e-3), (4.0, 3.0e-3)]:
        rows.extend((vgs_v, float(vds_v), float(scale * vds_v)) for vds_v in vds)
    return pd.DataFrame(rows, columns=["vgs_v", "vds_v", "id_a"])
