"""Reverse integration utility for Terminus estimation."""

from __future__ import annotations

from meteor_darkflight.physics_core import State
from meteor_darkflight.sim_kernel import DarkflightEnvironment


def run_reverse_trajectory(
    radar_state: State,
    target_altitude_m: float,
    env: DarkflightEnvironment,
    dt: float = -0.1, # Negative time step for reverse integration
    max_steps: int = 100_000,
) -> State:
    """Run a reverse trajectory simulation from Radar state to Terminus altitude.

    Args:
        radar_state: State at the radar signature (t, x, y, z, vx, vy, vz, mass).
        target_altitude_m: The altitude of the fireball terminus (higher than radar).
        env: Simulation environment.
        dt: Time step (should be negative).
        max_steps: Maximum steps to prevent infinite loops.

    Returns:
        The estimated State at the Terminus.
    """

    if dt > 0:
        dt = -dt # Ensure negative time step

    state = radar_state

    for _ in range(max_steps):
        if state.z >= target_altitude_m:
            return state

        # In reverse integration:
        # We are solving: dX/dt = V, dV/dt = A
        # But we are moving backwards in time.
        # X_{n-1} = X_n - V_n * dt ?
        # Or simply use the same Euler step with negative dt?
        # V_{t+dt} = V_t + a(V_t) * dt
        # If dt is negative, we are effectively subtracting.

        # However, drag opposes velocity.
        # In forward flight: a_drag = -C * v^2 * v_hat
        # In reverse flight: We are tracing back where it came from.
        # The velocity vector points DOWN (mostly).
        # We are moving UP.
        # The physical forces (Gravity, Drag) still act in their usual directions based on the state.
        # Gravity points DOWN. Drag points OPPOSITE to Velocity.

        # If we just use negative dt:
        # V_{prev} = V_{curr} + a(V_{curr}) * (-dt)
        # X_{prev} = X_{curr} + V_{curr} * (-dt)

        # Let's check the logic:
        # V_{curr} = V_{prev} + a(V_{prev}) * dt_pos
        # V_{prev} = V_{curr} - a(V_{prev}) * dt_pos
        # We approximate a(V_{prev}) with a(V_{curr}).
        # So V_{prev} approx V_{curr} - a(V_{curr}) * dt\_pos
        # Which is V_{curr} + a(V_{curr}) * dt_neg.

        # So yes, standard Euler with negative dt works for simple reversibility
        # (ignoring chaotic divergence for now, which is fine for short ballistic segments).

        acc = env.acceleration(state)
        # Mass change?
        # If we assume constant mass for this segment (dark flight), mdot = 0.
        # If ablation happened, we'd need to add mass back.
        # For now, assume constant mass in dark flight.
        # mdot = 0.0

        vx_new = state.vx + acc[0] * dt
        vy_new = state.vy + acc[1] * dt
        vz_new = state.vz + acc[2] * dt

        x_new = state.x + state.vx * dt
        y_new = state.y + state.vy * dt
        z_new = state.z + state.vz * dt

        m_new = state.mass # Constant mass
        t_new = state.t + dt

        state = State(t_new, x_new, y_new, z_new, vx_new, vy_new, vz_new, m_new)

    return state # Return last state if max_steps reached (warn user?)
