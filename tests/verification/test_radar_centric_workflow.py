"""Verification test for the Radar-Centric workflow."""

import math
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../src')))

from meteor_darkflight.physics_core import State
from meteor_darkflight.sim_kernel import (
    AtmosphericProfile,
    DarkflightEnvironment,
    calculate_simulated_terminus,
    find_mass_for_flight_time,
    generate_strewn_field,
    run_reverse_trajectory,
)


# Mock Atmosphere (Constant for simplicity in this test, or reuse Park Forest)
def create_mock_atmosphere():
    # Simple isothermal atmosphere
    levels = [
        (0.0, 101325.0, 288.15, 0.0, 0.0),
        (10000.0, 26500.0, 223.15, 10.0, 0.0), # 10 m/s wind East
        (20000.0, 5500.0, 216.65, 20.0, 0.0), # 20 m/s wind East
        (30000.0, 1200.0, 226.50, 0.0, 0.0),
    ]
    return AtmosphericProfile.from_raw_levels(levels)

def test_radar_centric_workflow():
    # 1. Setup Environment
    profile = create_mock_atmosphere()
    env = DarkflightEnvironment(
        profile=profile,
        fragment_density_kg_m3=3000.0,
        drag_model="sphere",
        shape_factor=1.0,
    )

    # 2. Define "Truth" (Terminus)
    # Let's say the fireball terminus was at 25km, falling straight down (for simplicity)
    # But with wind, it will drift.
    # Terminus: 25km, t=0
    terminus_alt = 25000.0

    # 3. Define "Observed" Radar Signature
    # Let's assume we observed a signature at 10km.
    # We need to pick a mass and simulate forward to generate "synthetic observation" first,
    # so we know what the answer should be.

    true_mass = 10.0 # kg

    # Initial state at Terminus
    # Velocity: 3000 m/s, 45 deg angle
    v_mag = 3000.0
    angle_rad = math.radians(45.0)
    vx = v_mag * math.cos(angle_rad) # East
    vy = 0.0
    vz = -v_mag * math.sin(angle_rad) # Down

    terminus_state = State(0.0, 0.0, 0.0, terminus_alt, vx, vy, vz, true_mass)

    # Run forward to 10km to get "Radar Observation"
    # We need a way to stop at 10km.
    # For this test, we can use the mass_finder's internal logic or just run_trajectory and interpolate.
    # Let's use run_trajectory and find the state near 10km.

    from meteor_darkflight.sim_kernel import ExplicitEulerIntegrator, run_trajectory
    integrator = ExplicitEulerIntegrator()
    result = run_trajectory(terminus_state, integrator, env, dt=0.1)

    # Find state closest to 10km and interpolate
    radar_alt = 10000.0
    radar_state = None

    for i in range(len(result.states) - 1):
        s1 = result.states[i]
        s2 = result.states[i+1]

        if s1.z >= radar_alt >= s2.z:
            # Interpolate
            frac = (s1.z - radar_alt) / (s1.z - s2.z)
            t_interp = s1.t + frac * (s2.t - s1.t)
            x_interp = s1.x + frac * (s2.x - s1.x)
            y_interp = s1.y + frac * (s2.y - s1.y)
            z_interp = radar_alt
            vx_interp = s1.vx + frac * (s2.vx - s1.vx)
            vy_interp = s1.vy + frac * (s2.vy - s1.vy)
            vz_interp = s1.vz + frac * (s2.vz - s1.vz)

            radar_state = State(t_interp, x_interp, y_interp, z_interp, vx_interp, vy_interp, vz_interp, s1.mass)
            break

    assert radar_state is not None
    print(f"Synthetic Radar State: z={radar_state.z}, t={radar_state.t}, mass={radar_state.mass}")

    observed_duration = radar_state.t - terminus_state.t
    print(f"Observed Duration: {observed_duration} s")

    # =========================================================================
    # TEST PHASE 1: Mass Finding
    # =========================================================================

    # We forget the true mass and try to recover it using the observed duration.
    # We assume we know the Terminus position/velocity (from the prompt's workflow description).
    # "In the first step... the model knows the altitude and time of the fireball terminus...
    # and the time and altitude of the weather radar signature."

    # Note: The workflow says "Terminus to Radar".
    # We pass the terminus state (with dummy mass) and observed duration.

    dummy_terminus = State(0.0, 0.0, 0.0, terminus_alt, vx, vy, vz, 1.0) # Wrong mass

    found_mass = find_mass_for_flight_time(
        dummy_terminus,
        radar_alt,
        observed_duration,
        env,
        mass_min_kg=0.1,
        mass_max_kg=100.0,
        tolerance_s=0.01
    )

    print(f"Found Mass: {found_mass} kg")
    assert math.isclose(found_mass, true_mass, rel_tol=0.05) # 5% tolerance

    # =========================================================================
    # TEST PHASE 2: Radar to Ground
    # =========================================================================

    # Now we simulate from Radar to Ground using the found mass.
    # We use the radar_state (position/velocity) but update the mass.

    start_state = State(
        radar_state.t,
        radar_state.x,
        radar_state.y,
        radar_state.z,
        radar_state.vx,
        radar_state.vy,
        radar_state.vz,
        found_mass
    )

    ground_result = run_trajectory(start_state, integrator, env)
    print(f"Impact: {ground_result.impact_state.x}, {ground_result.impact_state.y}")

    # =========================================================================
    # TEST PHASE 3: Strewn Field (Reverse Integration)
    # =========================================================================

    # "Back Calculation": Reverse integrate from Radar to Terminus.
    # We should get back close to (0,0, 25km).

    calc_terminus = run_reverse_trajectory(start_state, terminus_alt, env)
    print(f"Calculated Terminus: {calc_terminus.x}, {calc_terminus.y}, {calc_terminus.z}")

    # Verify we are close to 0,0
    # Note: Reverse integration is an approximation, especially with drag.
    # But for a single fragment track, it should be reasonably close.

    dist_error = math.sqrt(calc_terminus.x**2 + calc_terminus.y**2)
    print(f"Terminus Position Error: {dist_error} m")

    # Allow some error due to Euler integration and drag reversibility limits
    assert dist_error < 500.0

    # Centroid (trivial for 1 point)
    centroid = calculate_simulated_terminus([start_state], terminus_alt, env)
    assert math.isclose(centroid[0], calc_terminus.x)
    assert math.isclose(centroid[1], calc_terminus.y)

    # Generate Strewn Field
    masses = [1.0, 10.0, 100.0]
    # We need the velocity at terminus.
    # In the workflow, we use the "Calculated Terminus" location but what velocity?
    # "enter a decadal suite of meteorite masses... and calculate their landing sites"
    # Presumably using the same velocity vector as the fireball?
    # Or the velocity vector from the reverse integration?
    # The reverse integration gives us a velocity vector at terminus.

    term_velocity = (calc_terminus.vx, calc_terminus.vy, calc_terminus.vz)

    field = generate_strewn_field(centroid, terminus_alt, term_velocity, masses, env)

    assert len(field) == 3
    print("Strewn Field Points:")
    for m, x, y in field:
        print(f"Mass {m}kg: ({x}, {y})")

    # Heavier mass -> Less Drag -> Maintains forward velocity -> Travels further.
    # So 100kg should be further East than 1kg.
    assert field[0][1] < field[2][1] # x coordinate
