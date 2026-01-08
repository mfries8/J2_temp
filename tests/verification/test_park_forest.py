import math
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../src')))

import pandas as pd
from pyproj import Transformer

from meteor_darkflight.physics_core import ExplicitEulerIntegrator, State
from meteor_darkflight.sim_kernel import (
    AtmosphericProfile,
    DarkflightEnvironment,
    run_trajectory,
)


def load_park_forest_atmosphere():
    """Load atmospheric profile from extracted CSV."""
    df = pd.read_csv('tests/verification/data/park_forest_wind.csv')

    levels = []
    for _, row in df.iterrows():
        alt_m = row['altitude']
        speed_mps = row['speed']
        direction_deg = row['direction']
        pressure_pa = row['pressure']
        temp_k = row['temperature']

        # Wind components
        # u = -speed * sin(dir)
        # v = -speed * cos(dir)
        rad = math.radians(direction_deg)
        u = -speed_mps * math.sin(rad)
        v = -speed_mps * math.cos(rad)

        levels.append((alt_m, pressure_pa, temp_k, u, v))

    return AtmosphericProfile.from_raw_levels(levels)

def test_park_forest_simulation():
    # 1. Setup Parameters
    mass_kg = 1000.0
    density_kg_m3 = 3320.0
    # cd = 0.47 # Sphere

    # Initial State
    # User correction: Moving SSW to NNE (Heading 21).
    # This means Start is the Southern point, End is the Northern point.

    # South Point (Previously Expected Landing)
    lat_start = 41.3468
    lon_start = -87.7878

    # User correction: Start Altitude 17km
    alt_start = 17000.0

    velocity = 3000.0
    angle_deg = 51.0 # Fitted to match range with Mach-dependent drag

    # User correction: Heading 21 degrees
    azimuth_deg = 21.0

    # Convert Lat/Lon to UTM
    transformer = Transformer.from_crs("epsg:4326", "epsg:32616") # WGS84 to UTM Zone 16N
    x_start, y_start = transformer.transform(lat_start, lon_start)

    # Velocity components
    el_rad = math.radians(angle_deg)
    az_rad = math.radians(azimuth_deg)

    vz = -velocity * math.sin(el_rad)
    v_horiz = velocity * math.cos(el_rad)

    vx = v_horiz * math.sin(az_rad)
    vy = v_horiz * math.cos(az_rad)

    initial_state = State(
        t=0.0,
        x=x_start,
        y=y_start,
        z=alt_start,
        vx=vx,
        vy=vy,
        vz=vz,
        mass=mass_kg
    )

    # 2. Setup Environment
    profile = load_park_forest_atmosphere()

    env = DarkflightEnvironment(
        profile=profile,
        fragment_density_kg_m3=density_kg_m3,
        drag_model="sphere",
        shape_factor=1.0,
    )

    # 3. Run Simulation
    integrator = ExplicitEulerIntegrator()
    result = run_trajectory(initial_state, integrator, env, dt=0.1, max_steps=100_000)

    # 4. Verify Landing
    # Expected Landing: North Point (Previously Start)
    lat_expected = 41.46
    lon_expected = -87.73
    x_expected, y_expected = transformer.transform(lat_expected, lon_expected)

    print(f"Expected UTM: {x_expected}, {y_expected}")
    print(f"Actual UTM: {result.impact_state.x}, {result.impact_state.y}")
    print(f"Flight Time: {result.flight_time_s} s")

    dist = math.sqrt((result.impact_state.x - x_expected)**2 + (result.impact_state.y - y_expected)**2)
    print(f"Distance Error: {dist} meters")

    # Assert within 1km
    assert dist < 1000.0
