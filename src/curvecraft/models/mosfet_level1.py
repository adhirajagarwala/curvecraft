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
    scalar_input = np.isscalar(vgs_v)
    vgs = np.asarray(vgs_v, dtype=float)
    overdrive = vgs - parameters.vth_v
    current = np.zeros_like(vgs, dtype=float)

    conducting = overdrive > 0
    if np.any(conducting):
        vds = parameters.vds_v
        beta = parameters.beta_a_per_v2
        modulation = 1.0 + parameters.lambda_1_per_v * vds
        triode = conducting & (vds < overdrive)
        saturation = conducting & ~triode

        current[triode] = (
            beta
            * (overdrive[triode] * vds - 0.5 * vds**2)
            * modulation
        )
        current[saturation] = (
            0.5 * beta * overdrive[saturation] ** 2 * modulation
        )

    if scalar_input:
        return float(current)
    return current
