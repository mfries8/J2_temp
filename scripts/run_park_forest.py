"""Run Park Forest simulation and export KML."""

import math
import os
import sys

import pandas as pd
from pyproj import Transformer

# Ensure src is in path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from meteor_darkflight.geospatial_export.export import export_kml
from meteor_darkflight.physics_core import ExplicitEulerIntegrator, State
from meteor_darkflight.sim_kernel import (
    AtmosphericProfile,
    DarkflightEnvironment,
    run_trajectory,
)


def load_park_forest_atmosphere():
    """Load atmospheric profile from extracted CSV."""
    # Path relative to repo root
    csv_path = 'tests/verification/data/park_forest_wind.csv'
    if not os.path.exists(csv_path):
        # Try relative to script if running from scripts dir
        csv_path = '../tests/verification/data/park_forest_wind.csv'

    df = pd.read_csv(csv_path)

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

def main():
    print("Setting up Park Forest simulation...")

    # 1. Setup Parameters
    mass_kg = 1000.0
    density_kg_m3 = 3320.0

    # Initial State
#    lat_start = 41.3468
#    lon_start = -87.7878
    lat_start = 41.46
    lon_start = -87.73
    alt_start = 17000.0
    velocity = 3000.0
    angle_deg = 61.0
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
    print("Loading atmosphere...")
    profile = load_park_forest_atmosphere()

    env = DarkflightEnvironment(
        profile=profile,
        fragment_density_kg_m3=density_kg_m3,
        drag_model="sphere",
        shape_factor=1.0,
    )

    # 3. Run Simulation
    print("Running simulation...")
    integrator = ExplicitEulerIntegrator()
    result = run_trajectory(initial_state, integrator, env, dt=0.1, max_steps=100_000)

    print(f"Simulation complete. Flight time: {result.flight_time_s:.2f} s")
    print(f"Impact Location (UTM): {result.impact_state.x:.2f}, {result.impact_state.y:.2f}")

    # 4. Export KML
    out_file = "park_forest.kml"
    print(f"Exporting KML to {out_file}...")
    export_kml([result], out_file)

    abs_path = os.path.abspath(out_file)
    print(f"KML exported successfully to: {abs_path}")

if __name__ == "__main__":
    main()
