import shutil

import pytest

from curvecraft.models import DiodeParameters
from curvecraft.spice import (
    NgspiceNotFoundError,
    run_ngspice,
    write_diode_netlist,
)


def test_run_ngspice_missing_executable_has_clear_error(tmp_path) -> None:  # type: ignore[no-untyped-def]
    netlist = tmp_path / "diode.cir"
    netlist.write_text(".end\n", encoding="utf-8")

    with pytest.raises(NgspiceNotFoundError, match="not found on PATH"):
        run_ngspice(netlist, executable="definitely-not-ngspice")


@pytest.mark.skipif(shutil.which("ngspice") is None, reason="ngspice is not installed")
def test_run_ngspice_integration_when_available(tmp_path) -> None:  # type: ignore[no-untyped-def]
    netlist = write_diode_netlist(
        tmp_path / "diode.cir",
        DiodeParameters(
            saturation_current_a=1e-12,
            ideality_factor=1.5,
            series_resistance_ohm=0.0,
        ),
    )
    output = tmp_path / "diode.out"

    result = run_ngspice(netlist, output)

    assert result.returncode == 0
    assert result.output_path.exists()
    assert result.output_path == output
