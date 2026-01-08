"""Tests for the sim_kernel trajectory runner."""

from __future__ import annotations

import pytest

from meteor_darkflight.physics_core import (
    ExplicitEulerIntegrator,
    RungeKutta4Integrator,
    State,
)
from meteor_darkflight.sim_kernel.environment import (
    AtmosphericLevel,
    AtmosphericProfile,
    DarkflightEnvironment,
)
from meteor_darkflight.sim_kernel.integrator import TerminationReason, run_trajectory


def constant_profile() -> AtmosphericProfile:
    levels = [
        AtmosphericLevel(altitude_m=0.0, density_kg_m3=1.2, wind_u_mps=0.0, wind_v_mps=0.0, temperature_k=288.15),
        AtmosphericLevel(altitude_m=1000.0, density_kg_m3=1.2, wind_u_mps=0.0, wind_v_mps=0.0, temperature_k=288.15),
    ]
    return AtmosphericProfile(levels)


def test_run_trajectory_hits_ground_with_rk4():
    env = DarkflightEnvironment(profile=constant_profile(), gravity_mps2=9.81, drag_coefficient=0.0)
    integrator = RungeKutta4Integrator()
    state = State(t=0.0, x=0.0, y=0.0, z=100.0, vx=30.0, vy=0.0, vz=-20.0, mass=1.0)

    result = run_trajectory(state, integrator, env, dt=0.05, max_steps=10_000)

    assert result.termination_reason is TerminationReason.GROUND
    assert result.impact_state is not None
    assert result.impact_state.z == pytest.approx(0.0, abs=1e-6)
    assert result.flight_time_s == pytest.approx(2.915434405799334, rel=1e-3)
    assert result.terminal_speed_mps == pytest.approx(57.11347264276914, rel=1e-3)
    assert result.terminal_kinetic_energy_j == pytest.approx(1631.4285714285716, rel=1e-3)
    assert result.horizontal_drift_m == pytest.approx(result.impact_state.horizontal_displacement(), rel=1e-7)


def test_run_trajectory_reports_stall_when_speed_small():
    env = DarkflightEnvironment(profile=constant_profile(), gravity_mps2=0.0, drag_coefficient=0.0)
    integrator = ExplicitEulerIntegrator()
    state = State(t=0.0, x=0.0, y=0.0, z=10.0, vx=0.0, vy=0.0, vz=0.0, mass=1.0)

    result = run_trajectory(state, integrator, env, dt=1.0, stall_speed_mps=0.1, max_steps=5)

    assert result.termination_reason is TerminationReason.STALLED
    assert result.impact_state is None
    assert result.flight_time_s == pytest.approx(1.0)
