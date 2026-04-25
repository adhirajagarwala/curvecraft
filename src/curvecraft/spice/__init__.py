"""SPICE integration helpers."""

from curvecraft.spice.netlist_writer import (
    diode_dc_sweep_netlist,
    diode_model_card,
    mosfet_id_vgs_dc_sweep_netlist,
    mosfet_level1_model_card,
    write_diode_netlist,
    write_mosfet_id_vgs_netlist,
)
from curvecraft.spice.ngspice_parser import (
    parse_mosfet_id_vgs_ngspice_output_file,
    parse_mosfet_id_vgs_ngspice_output_text,
    parse_ngspice_dc_output_file,
    parse_ngspice_dc_output_text,
)
from curvecraft.spice.ngspice_runner import (
    NgspiceNotFoundError,
    NgspiceRunError,
    NgspiceRunResult,
    run_ngspice,
)
from curvecraft.spice.validation import (
    SpiceValidationMetrics,
    SpiceValidationResult,
    validate_diode_against_ngspice_results,
    validate_diode_with_ngspice,
    validate_mosfet_id_vgs_against_ngspice_results,
    validate_mosfet_id_vgs_with_ngspice,
)

__all__ = [
    "NgspiceNotFoundError",
    "NgspiceRunError",
    "NgspiceRunResult",
    "SpiceValidationMetrics",
    "SpiceValidationResult",
    "diode_dc_sweep_netlist",
    "diode_model_card",
    "mosfet_id_vgs_dc_sweep_netlist",
    "mosfet_level1_model_card",
    "parse_mosfet_id_vgs_ngspice_output_file",
    "parse_mosfet_id_vgs_ngspice_output_text",
    "parse_ngspice_dc_output_file",
    "parse_ngspice_dc_output_text",
    "run_ngspice",
    "validate_diode_against_ngspice_results",
    "validate_diode_with_ngspice",
    "validate_mosfet_id_vgs_against_ngspice_results",
    "validate_mosfet_id_vgs_with_ngspice",
    "write_diode_netlist",
    "write_mosfet_id_vgs_netlist",
]
