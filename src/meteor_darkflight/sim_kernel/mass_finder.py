"""Mass finding utility for Radar-Centric workflow."""

from __future__ import annotations

from meteor_darkflight.physics_core import ExplicitEulerIntegrator, State
from meteor_darkflight.sim_kernel import DarkflightEnvironment


def find_mass_for_flight_time(
    terminus_state: State,
    radar_altitude_m: float,
    observed_duration_s: float,
    env: DarkflightEnvironment,
    mass_min_kg: float = 0.001,
    mass_max_kg: float = 10000.0,
    tolerance_s: float = 0.1,
    max_iterations: int = 50,
) -> float:
    """Find the mass that results in the observed flight time from Terminus to Radar.

    Uses a bisection method to find the mass.
    Assumes flight time is monotonic with mass (heavier = faster = shorter time).

    Args:
        terminus_state: State at the fireball terminus (mass is ignored/overwritten).
        radar_altitude_m: Target altitude of the radar signature.
        observed_duration_s: Observed time difference (t_radar - t_terminus).
        env: Simulation environment.
        mass_min_kg: Minimum mass to search.
        mass_max_kg: Maximum mass to search.
        tolerance_s: Convergence tolerance in seconds.
        max_iterations: Maximum bisection iterations.

    Returns:
        The estimated mass in kg.

    Raises:
        ValueError: If a solution cannot be found within the bounds.
    """

    def simulate_flight_time(mass: float) -> float:
        # Create a new state with the trial mass
        # Note: State is frozen, so we create a new one
        trial_state = State(
            t=terminus_state.t,
            x=terminus_state.x,
            y=terminus_state.y,
            z=terminus_state.z,
            vx=terminus_state.vx,
            vy=terminus_state.vy,
            vz=terminus_state.vz,
            mass=mass
        )

        integrator = ExplicitEulerIntegrator()

        state = trial_state
        dt = 0.1

        for _ in range(100_000):
            # Store previous state for interpolation
            prev_state = state

            # Step
            state = integrator.step(state, dt, env)

            if state.z <= radar_altitude_m:
                 # Interpolate
                 # z_prev > radar_alt >= z_curr
                 if prev_state.z == state.z:
                     return state.t - terminus_state.t

                 fraction = (prev_state.z - radar_altitude_m) / (prev_state.z - state.z)
                 t_interp = prev_state.t + fraction * dt
                 return t_interp - terminus_state.t

        return float('inf') # Did not reach altitude

    # Define the objective function for root finding
    def time_error(mass: float) -> float:
        flight_time = simulate_flight_time(mass)
        if flight_time == float('inf'):
            # If it didn't reach altitude, return a large error
            # But which direction?
            # If it didn't reach, it likely stopped too high (too light? or too much drag?)
            # Light mass -> high drag -> stops early.
            # So we need heavier mass.
            # Error should be positive (time_sim - time_obs) where time_sim is effectively infinite?
            # Or just return a large number.
            return 1e6
        return flight_time - observed_duration_s

    # Use scipy.optimize.brentq
    from scipy.optimize import brentq  # type: ignore

    try:
        # Check bounds first to ensure sign change
        err_min = time_error(mass_min_kg)
        err_max = time_error(mass_max_kg)

        if err_min * err_max > 0:
            raise ValueError(f"No solution in mass range [{mass_min_kg}, {mass_max_kg}]. Errors: {err_min:.2f}, {err_max:.2f}")

        optimal_mass = brentq(time_error, mass_min_kg, mass_max_kg, xtol=1e-3, maxiter=max_iterations)
        return float(optimal_mass)

    except Exception as e:
        raise ValueError(f"Optimization failed: {e}")

