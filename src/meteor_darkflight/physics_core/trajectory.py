"""Trajectory integrators and state definitions (Phase 2 scaffolding)."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, replace
from math import sqrt
from typing import Protocol, Tuple


@dataclass(frozen=True)
class State:
    t: float
    x: float
    y: float
    z: float
    vx: float
    vy: float
    vz: float
    mass: float

    def speed(self) -> float:
        """Return total speed magnitude (m/s)."""

        return sqrt(self.vx**2 + self.vy**2 + self.vz**2)

    def horizontal_displacement(self) -> float:
        """Return horizontal drift magnitude (m)."""

        return sqrt(self.x**2 + self.y**2)

    def with_updates(
        self,
        *,
        t: float | None = None,
        x: float | None = None,
        y: float | None = None,
        z: float | None = None,
        vx: float | None = None,
        vy: float | None = None,
        vz: float | None = None,
        mass: float | None = None,
    ) -> "State":
        """Return a new state with updated components."""

        return replace(
            self,
            t=self.t if t is None else t,
            x=self.x if x is None else x,
            y=self.y if y is None else y,
            z=self.z if z is None else z,
            vx=self.vx if vx is None else vx,
            vy=self.vy if vy is None else vy,
            vz=self.vz if vz is None else vz,
            mass=self.mass if mass is None else mass,
        )


class IntegrationEnvironment(Protocol):
    """Minimal hooks the integrator expects from the simulation context."""

    def acceleration(self, state: State) -> Tuple[float, float, float]:
        """Return acceleration components (ax, ay, az) in m/s²."""

    def mass_derivative(self, state: State) -> float:
        """Return dm/dt (kg/s) accounting for ablation and fragmentation."""


class Integrator(ABC):
    @abstractmethod
    def step(self, state: State, dt: float, env: IntegrationEnvironment) -> State:
        """Advance state by ``dt`` using the supplied environment."""


class ExplicitEulerIntegrator(Integrator):
    """Simple explicit Euler integrator mirroring workbook slice stepping."""

    def step(self, state: State, dt: float, env: IntegrationEnvironment) -> State:
        ax, ay, az = env.acceleration(state)
        dm_dt = env.mass_derivative(state)

        vx = state.vx + ax * dt
        vy = state.vy + ay * dt
        vz = state.vz + az * dt
        x = state.x + vx * dt
        y = state.y + vy * dt
        z = state.z + vz * dt
        mass = max(state.mass + dm_dt * dt, 0.0)

        return state.with_updates(t=state.t + dt, x=x, y=y, z=z, vx=vx, vy=vy, vz=vz, mass=mass)


class RungeKutta4Integrator(Integrator):
    """Classical 4th-order Runge–Kutta integrator for trajectory evolution."""

    def step(self, state: State, dt: float, env: IntegrationEnvironment) -> State:
        def derivative(s: State) -> Tuple[float, float, float, float, float, float, float]:
            ax, ay, az = env.acceleration(s)
            dm_dt = env.mass_derivative(s)
            return (s.vx, s.vy, s.vz, ax, ay, az, dm_dt)

        def combine(
            base: State,
            k: Tuple[float, float, float, float, float, float, float],
            scale: float,
        ) -> State:
            return base.with_updates(
                t=base.t + dt * scale,
                x=base.x + k[0] * dt * scale,
                y=base.y + k[1] * dt * scale,
                z=base.z + k[2] * dt * scale,
                vx=base.vx + k[3] * dt * scale,
                vy=base.vy + k[4] * dt * scale,
                vz=base.vz + k[5] * dt * scale,
                mass=max(base.mass + k[6] * dt * scale, 0.0),
            )

        k1 = derivative(state)
        k2 = derivative(combine(state, k1, 0.5))
        k3 = derivative(combine(state, k2, 0.5))
        k4 = derivative(combine(state, k3, 1.0))

        def rk4_component(index: int) -> float:
            return k1[index] + 2.0 * k2[index] + 2.0 * k3[index] + k4[index]

        x = state.x + (dt / 6.0) * rk4_component(0)
        y = state.y + (dt / 6.0) * rk4_component(1)
        z = state.z + (dt / 6.0) * rk4_component(2)
        vx = state.vx + (dt / 6.0) * rk4_component(3)
        vy = state.vy + (dt / 6.0) * rk4_component(4)
        vz = state.vz + (dt / 6.0) * rk4_component(5)
        mass = max(state.mass + (dt / 6.0) * rk4_component(6), 0.0)

        return state.with_updates(t=state.t + dt, x=x, y=y, z=z, vx=vx, vy=vy, vz=vz, mass=mass)
