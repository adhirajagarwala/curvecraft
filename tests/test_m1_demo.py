from curvecraft.cli import main, run_diode_demo


def test_run_diode_demo_creates_core_outputs_without_ngspice(tmp_path) -> None:  # type: ignore[no-untyped-def]
    result = run_diode_demo(
        output_dir=tmp_path,
        run_ngspice_if_available=False,
    )

    assert result.fit_plot_path.exists()
    assert result.semilog_plot_path.exists()
    assert result.netlist_path.exists()
    assert result.report_path.exists()
    assert result.validation_result is None
    assert result.validation_skipped_reason is not None


def test_cli_diode_demo_accepts_temp_output_dir(tmp_path, capsys) -> None:  # type: ignore[no-untyped-def]
    exit_code = main(
        [
            "diode-demo",
            "--output-dir",
            str(tmp_path),
            "--skip-ngspice",
        ]
    )

    output = capsys.readouterr().out
    assert exit_code == 0
    assert "SPICE netlist:" in output
    assert "Report:" in output
    assert (tmp_path / "diode_validation.cir").exists()
    assert (tmp_path / "diode_m1_fit_report.md").exists()
