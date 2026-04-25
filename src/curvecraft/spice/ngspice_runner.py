"""Run ngspice in batch mode."""

import shutil
import subprocess
from dataclasses import dataclass
from os import PathLike
from pathlib import Path


class NgspiceNotFoundError(RuntimeError):
    """Raised when ngspice is not available on PATH."""


class NgspiceRunError(RuntimeError):
    """Raised when ngspice exits with a nonzero status."""


@dataclass(frozen=True)
class NgspiceRunResult:
    """Paths and process status from an ngspice batch run."""

    netlist_path: Path
    output_path: Path
    returncode: int
    command: tuple[str, ...]


def run_ngspice(
    netlist_path: str | PathLike[str],
    output_path: str | PathLike[str] | None = None,
    *,
    executable: str = "ngspice",
) -> NgspiceRunResult:
    """Run ngspice in batch mode and write its text output to a known file."""
    executable_path = shutil.which(executable)
    if executable_path is None:
        raise NgspiceNotFoundError(
            f"ngspice executable '{executable}' was not found on PATH."
        )

    netlist = Path(netlist_path)
    if output_path is None:
        output = netlist.with_suffix(".out")
    else:
        output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)

    command = (executable_path, "-b", "-o", str(output), str(netlist))
    completed = subprocess.run(command, check=False)
    result = NgspiceRunResult(
        netlist_path=netlist,
        output_path=output,
        returncode=int(completed.returncode),
        command=command,
    )
    if completed.returncode != 0:
        raise NgspiceRunError(
            f"ngspice failed with exit code {completed.returncode}. "
            f"See output file: {output}"
        )
    return result
