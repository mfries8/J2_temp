"""Tests for trajectory integrators with simple environments."""

from __future__ import annotations

import pytest

from meteor_darkflight.physics_core import ExplicitEulerIntegrator, RungeKutta4Integrator, State
from meteor_darkflight.physics_core.trajectory import IntegrationEnvironment


class ConstantAccelerationEnv(IntegrationEnvironment):
    def __init__(self, ax: float = 0.0, ay: float = 0.0, az: float = -9.81):
        self._accel = (ax, ay, az)

    def acceleration(self, state: State):
        return self._accel

    def mass_derivative(self, state: State) -> float:
        return 0.0


@pytest.mark.parametrize("integrator_cls", [ExplicitEulerIntegrator, RungeKutta4Integrator])
def test_integrators_update_position_and_velocity(integrator_cls):
    integrator = integrator_cls()
    env = ConstantAccelerationEnv()
    state = State(t=0.0, x=0.0, y=0.0, z=100.0, vx=0.0, vy=0.0, vz=0.0, mass=1.0)

    next_state = integrator.step(state, 1.0, env)
    assert next_state.vz == pytest.approx(-9.81, rel=1e-6)
    expected_z = 90.19 if integrator_cls is ExplicitEulerIntegrator else 95.095
    assert next_state.z == pytest.approx(expected_z, rel=1e-3)

    two_step = integrator.step(next_state, 1.0, env)
    assert two_step.vz == pytest.approx(-19.62, rel=1e-6)
    assert two_step.z < next_state.z


def test_runge_kutta_matches_analytic_solution():
    integrator = RungeKutta4Integrator()
    env = ConstantAccelerationEnv()
    state = State(t=0.0, x=0.0, y=0.0, z=100.0, vx=10.0, vy=0.0, vz=-20.0, mass=1.0)
    dt = 0.5

    total_time = 5.0
    steps = int(total_time / dt)
    current = state
    for _ in range(steps):
        current = integrator.step(current, dt, env)

    expected_z = state.z + state.vz * total_time + 0.5 * env._accel[2] * total_time**2
    expected_vz = state.vz + env._accel[2] * total_time
    expected_x = state.x + state.vx * total_time

    assert current.z == pytest.approx(expected_z, rel=1e-5)
    assert current.vz == pytest.approx(expected_vz, rel=1e-5)
    assert current.x == pytest.approx(expected_x, rel=1e-5)
