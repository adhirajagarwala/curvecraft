"""Educational Level-1 MOSFET Id-Vgs equations."""

from dataclasses import dataclass

import numpy as np


@dataclass(frozen=True)
class MosfetLevel1Parameters:
    """Parameters for a simple n-channel enhancement MOSFET transfer model.

    Attributes:
        vth_v: Threshold voltage, Vth, in volts.
        beta_a_per_v2: Effective transconductance parameter, beta, in A/V^2.
        lambda_1_per_v: Channel-length modulation parameter, lambda, in 1/V.
        vds_v: Fixed drain-source voltage for Id-Vgs evaluation, in volts.
    """

    vth_v: float
    beta_a_per_v2: float
    lambda_1_per_v: float = 0.0
    vds_v: float = 5.0

    def __post_init__(self) -> None:
        if self.beta_a_per_v2 <= 0:
            raise ValueError("beta_a_per_v2 must be positive.")
        if self.lambda_1_per_v < 0:
            raise ValueError("lambda_1_per_v must be nonnegative.")
        if self.vds_v < 0:
            raise ValueError("vds_v must be nonnegative.")


def mosfet_level1_current(
    vgs_v: np.ndarray | float,
    parameters: MosfetLevel1Parameters,
) -> np.ndarray | float:
    """Evaluate n-channel enhancement MOSFET drain current for Id-Vgs data.

    This is a simple Level-1 / square-law educational model at fixed Vds. It
    ignores subthreshold conduction, so current is clamped to zero when
    ``vgs_v - vth_v <= 0``. It also ignores body effect, capacitance,
    temperature dependence, velocity saturation, and other effects captured by
    production compact models such as BSIM.
    """
    return mosfet_level1_id_vds_current(vgs_v, parameters.vds_v, parameters)


def mosfet_level1_id_vds_current(
    vgs_v: np.ndarray | float,
    vds_v: np.ndarray | float,
    parameters: MosfetLevel1Parameters,
) -> np.ndarray | float:
    """Evaluate n-channel enhancement MOSFET drain current for Id-Vds data.

    This paired-input evaluator uses the same educational Level-1 / square-law
    equations as the M2 Id-Vgs helper, but accepts both ``vgs_v`` and ``vds_v``.
    It models only nonnegative-drain-voltage nMOS output curves. It ignores
    subthreshold conduction, body effect, capacitance, gate charge, temperature
    dependence, velocity saturation, self-heating, and BSIM-level behavior.
    """
    scalar_input = np.isscalar(vgs_v) and np.isscalar(vds_v)
    vgs, vds = np.broadcast_arrays(
        np.asarray(vgs_v, dtype=float),
        np.asarray(vds_v, dtype=float),
    )
    if np.any(~np.isfinite(vgs)) or np.any(~np.isfinite(vds)):
        raise ValueError("vgs_v and vds_v must contain only finite values.")
    if np.any(vds < 0):
        raise ValueError("vds_v must be nonnegative for this n-channel model.")

    overdrive = vgs - parameters.vth_v
    current = np.zeros_like(overdrive, dtype=float)

    conducting = overdrive > 0
    if np.any(conducting):
        beta = parameters.beta_a_per_v2
        modulation = 1.0 + parameters.lambda_1_per_v * vds
        triode = conducting & (vds < overdrive)
        saturation = conducting & ~triode

        current[triode] = (
            beta
            * (overdrive[triode] * vds[triode] - 0.5 * vds[triode] ** 2)
            * modulation[triode]
        )
        current[saturation] = (
            0.5
            * beta
            * overdrive[saturation] ** 2
            * modulation[saturation]
        )

    current = np.maximum(current, 0.0)
    if scalar_input:
        return float(current)
    return current
