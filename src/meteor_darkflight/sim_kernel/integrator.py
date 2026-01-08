"""Trajectory orchestration utilities for the darkflight simulation kernel."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import List, Sequence

from meteor_darkflight.physics_core import Integrator, State
from meteor_darkflight.physics_core.trajectory import IntegrationEnvironment


class TerminationReason(str, Enum):
    GROUND = "ground"
    MAX_STEPS = "max_steps"
    STALLED = "stalled"


@dataclass(frozen=True)
class TrajectoryResult:
    """Bundle simulation output and derived metrics."""

    states: Sequence[State]
    termination_reason: TerminationReason
    impact_state: State | None
    flight_time_s: float
    max_speed_mps: float
    horizontal_drift_m: float
    terminal_speed_mps: float
    terminal_kinetic_energy_j: float | None

    def as_dict(self) -> dict[str, float]:
        """Return summary metrics for downstream parity comparisons."""

        return {
            "flight_time_s": self.flight_time_s,
            "max_speed_mps": self.max_speed_mps,
            "horizontal_drift_m": self.horizontal_drift_m,
            "terminal_speed_mps": self.terminal_speed_mps,
            "terminal_kinetic_energy_j": self.terminal_kinetic_energy_j or 0.0,
        }


def _interpolate_state(prev_state: State, next_state: State) -> State:
    """Interpolate linearly in time to locate the ground-touch state."""

    if prev_state.z <= 0 <= next_state.z:
        # Already straddled ground but previous state is underground; swap.
        prev_state, next_state = next_state, prev_state

    if prev_state.z <= 0 and next_state.z <= 0:
        return next_state.with_updates(z=0.0)

    denominator = prev_state.z - next_state.z
    if denominator == 0:
        return next_state.with_updates(z=0.0)

    alpha = max(0.0, min(1.0, prev_state.z / denominator))

    def lerp(a: float, b: float) -> float:
        return a + (b - a) * alpha

    return prev_state.with_updates(
        t=lerp(prev_state.t, next_state.t),
        x=lerp(prev_state.x, next_state.x),
        y=lerp(prev_state.y, next_state.y),
        z=0.0,
        vx=lerp(prev_state.vx, next_state.vx),
        vy=lerp(prev_state.vy, next_state.vy),
        vz=lerp(prev_state.vz, next_state.vz),
        mass=lerp(prev_state.mass, next_state.mass),
    )


def run_trajectory(
    initial_state: State,
    integrator: Integrator,
    env: IntegrationEnvironment,
    *,
    dt: float = 0.5,
    max_steps: int = 100_000,
    stall_speed_mps: float = 1e-3,
) -> TrajectoryResult:
    """Integrate trajectory steps until ground intersection or timeout."""

    states: List[State] = [initial_state]
    current = initial_state
    max_speed = initial_state.speed()

    for _ in range(max_steps):
        next_state = integrator.step(current, dt, env)
        max_speed = max(max_speed, next_state.speed())

        if next_state.z <= 0.0:
            impact_state = _interpolate_state(current, next_state)
            states.append(impact_state)
            return TrajectoryResult(
                states=tuple(states),
                termination_reason=TerminationReason.GROUND,
                impact_state=impact_state,
                flight_time_s=impact_state.t - initial_state.t,
                max_speed_mps=max_speed,
                horizontal_drift_m=impact_state.horizontal_displacement(),
                terminal_speed_mps=impact_state.speed(),
                terminal_kinetic_energy_j=0.5
                * impact_state.mass
                * impact_state.speed() ** 2,
            )

        states.append(next_state)
        current = next_state

        if next_state.speed() <= stall_speed_mps:
            return TrajectoryResult(
                states=tuple(states),
                termination_reason=TerminationReason.STALLED,
                impact_state=None,
                flight_time_s=current.t - initial_state.t,
                max_speed_mps=max_speed,
                horizontal_drift_m=current.horizontal_displacement(),
                terminal_speed_mps=current.speed(),
                terminal_kinetic_energy_j=None,
            )

    return TrajectoryResult(
        states=tuple(states),
        termination_reason=TerminationReason.MAX_STEPS,
        impact_state=None,
        flight_time_s=current.t - initial_state.t,
        max_speed_mps=max_speed,
        horizontal_drift_m=current.horizontal_displacement(),
        terminal_speed_mps=current.speed(),
        terminal_kinetic_energy_j=None,
    )
