"""ngspice netlist generation for diode validation."""

from os import PathLike
from pathlib import Path

from curvecraft.models import DiodeParameters


def diode_model_card(
    parameters: DiodeParameters,
    *,
    model_name: str = "curve_diode",
) -> str:
    """Return an ngspice diode ``.model`` card for fitted diode parameters."""
    return (
        f".model {model_name} D "
        f"(IS={_format_spice_number(parameters.saturation_current_a)} "
        f"N={_format_spice_number(parameters.ideality_factor)} "
        f"RS={_format_spice_number(parameters.series_resistance_ohm)})"
    )


def diode_dc_sweep_netlist(
    parameters: DiodeParameters,
    *,
    model_name: str = "curve_diode",
    source_name: str = "Vin",
    diode_name: str = "D1",
    start_v: float = -0.1,
    stop_v: float = 0.8,
    step_v: float = 0.01,
) -> str:
    """Return a deterministic ngspice DC sweep netlist for diode I-V validation."""
    if step_v <= 0:
        raise ValueError("step_v must be positive.")
    if stop_v <= start_v:
        raise ValueError("stop_v must be greater than start_v.")

    lines = [
        "* CurveCraft diode DC sweep validation",
        f"{source_name} anode 0 0",
        f"{diode_name} anode 0 {model_name}",
        diode_model_card(parameters, model_name=model_name),
        (
            f".dc {source_name} {_format_spice_number(start_v)} "
            f"{_format_spice_number(stop_v)} {_format_spice_number(step_v)}"
        ),
        f".print dc v(anode) i({source_name})",
        ".end",
        "",
    ]
    return "\n".join(lines)


def write_diode_netlist(
    path: str | PathLike[str],
    parameters: DiodeParameters,
    *,
    model_name: str = "curve_diode",
    start_v: float = -0.1,
    stop_v: float = 0.8,
    step_v: float = 0.01,
) -> Path:
    """Write a diode DC sweep netlist and return the output path."""
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    netlist = diode_dc_sweep_netlist(
        parameters,
        model_name=model_name,
        start_v=start_v,
        stop_v=stop_v,
        step_v=step_v,
    )
    output_path.write_text(netlist, encoding="utf-8")
    return output_path


def _format_spice_number(value: float) -> str:
    """Format numbers deterministically for snapshot-friendly netlists."""
    formatted = f"{value:.12g}"
    if formatted == "-0":
        return "0"
    return formatted
