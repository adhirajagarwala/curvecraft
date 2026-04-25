from curvecraft.fitting.optimizer import DiodeFitMetrics, DiodeFitResult
from curvecraft.models import DiodeParameters
from curvecraft.reports import write_diode_report


def test_write_diode_report_creates_markdown_with_key_sections(tmp_path) -> None:  # type: ignore[no-untyped-def]
    input_csv = tmp_path / "input.csv"
    input_csv.write_text("voltage_v,current_a\n0.1,1e-9\n", encoding="utf-8")
    plot_path = tmp_path / "plots" / "fit.png"
    plot_path.parent.mkdir()
    plot_path.write_bytes(b"png")
    netlist_path = tmp_path / "spice" / "diode.cir"
    netlist_path.parent.mkdir()
    netlist_path.write_text(".end\n", encoding="utf-8")
    report_path = tmp_path / "reports" / "diode_report.md"
    fit_result = DiodeFitResult(
        parameters=DiodeParameters(
            saturation_current_a=1e-12,
            ideality_factor=1.5,
            series_resistance_ohm=2.0,
        ),
        success=True,
        message="synthetic test fit",
        metrics=DiodeFitMetrics(
            rmse_current_a=1e-9,
            rmse_log10_current=0.01,
            max_abs_current_error_a=2e-9,
        ),
        optimizer_cost=0.1,
        optimizer_nfev=12,
        total_points=10,
        positive_current_points=8,
    )

    result = write_diode_report(
        report_path,
        input_csv_path=input_csv,
        fit_result=fit_result,
        plot_paths=[plot_path],
        spice_netlist_path=netlist_path,
    )

    text = result.read_text(encoding="utf-8")
    assert result == report_path
    assert "# M1 Diode I-V Fit Report" in text
    assert "## Fitted Parameters" in text
    assert "Is" in text
    assert "n:" in text
    assert "Rs" in text
    assert "## Limitations" in text
    assert "../plots/fit.png" in text
    assert "../spice/diode.cir" in text
