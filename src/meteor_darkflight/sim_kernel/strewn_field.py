"""Strewn field generation utility for Radar-Centric workflow."""

from __future__ import annotations

from typing import List, Tuple

from meteor_darkflight.physics_core import ExplicitEulerIntegrator, State
from meteor_darkflight.sim_kernel import DarkflightEnvironment, run_trajectory
from meteor_darkflight.sim_kernel.reverse_integration import run_reverse_trajectory


def calculate_simulated_terminus(
    radar_states: List[State],
    terminus_altitude_m: float,
    env: DarkflightEnvironment,
) -> Tuple[float, float]:
    """Calculate the centroid of back-calculated terminus points.

    Args:
        radar_states: List of States at the radar signatures.
        terminus_altitude_m: The target terminus altitude.
        env: Simulation environment.

    Returns:
        Tuple of (Centroid X, Centroid Y) in the simulation coordinate frame.
    """

    terminus_points = []

    for state in radar_states:
        # Reverse integrate to terminus altitude
        term_state = run_reverse_trajectory(state, terminus_altitude_m, env)
        terminus_points.append((term_state.x, term_state.y))

    # Calculate Centroid
    if not terminus_points:
        return (0.0, 0.0)

    sum_x = sum(p[0] for p in terminus_points)
    sum_y = sum(p[1] for p in terminus_points)
    count = len(terminus_points)

    return (sum_x / count, sum_y / count)


def generate_strewn_field(
    terminus_centroid: Tuple[float, float],
    terminus_altitude_m: float,
    terminus_velocity: Tuple[float, float, float], # (vx, vy, vz)
    masses_kg: List[float],
    env: DarkflightEnvironment,
) -> List[Tuple[float, float, float]]: # (mass, impact_x, impact_y)
    """Generate strewn field impact points for a suite of masses.

    Args:
        terminus_centroid: (x, y) of the simulated terminus.
        terminus_altitude_m: Altitude of the terminus.
        terminus_velocity: Velocity vector at the terminus.
        masses_kg: List of masses to simulate.
        env: Simulation environment.

    Returns:
        List of tuples (mass, impact_x, impact_y).
    """

    results = []
    integrator = ExplicitEulerIntegrator()

    for mass in masses_kg:
        initial_state = State(
            t=0.0, # Relative time
            x=terminus_centroid[0],
            y=terminus_centroid[1],
            z=terminus_altitude_m,
            vx=terminus_velocity[0],
            vy=terminus_velocity[1],
            vz=terminus_velocity[2],
            mass=mass
        )

        result = run_trajectory(initial_state, integrator, env, dt=0.1, max_steps=100_000)
        if result.impact_state:
            results.append((mass, result.impact_state.x, result.impact_state.y))

    return results
