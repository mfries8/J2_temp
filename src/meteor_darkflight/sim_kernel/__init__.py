"""Simulation kernel exposing integrators and environment helpers."""

# Re-export Integrator for convenience
from meteor_darkflight.physics_core import ExplicitEulerIntegrator

from .environment import (
    AtmosphericLevel,
    AtmosphericProfile,
    DarkflightEnvironment,
)
from .integrator import (
    TerminationReason,
    TrajectoryResult,
    run_trajectory,
)
from .mass_finder import find_mass_for_flight_time
from .reverse_integration import run_reverse_trajectory
from .strewn_field import calculate_simulated_terminus, generate_strewn_field

__all__ = [
    "AtmosphericLevel",
    "AtmosphericProfile",
    "DarkflightEnvironment",
    "run_trajectory",
    "TrajectoryResult",
    "TerminationReason",
    "find_mass_for_flight_time",
    "run_reverse_trajectory",
    "calculate_simulated_terminus",
    "generate_strewn_field",
    "ExplicitEulerIntegrator",
]
