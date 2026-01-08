"""Drag helpers reverse-engineered from the legacy workbook."""

from __future__ import annotations

from dataclasses import dataclass
from math import hypot
from typing import Tuple


@dataclass(frozen=True)
class DragParams:
    """Bundle of drag parameters from workbook particle sheets."""

    cd: float
    area_m2: float


def calculate_sphere_cd(mach: float) -> float:
    """Calculate drag coefficient for a sphere based on Mach number.

    Based on Carter et al. (2009):
    Cd = 0.45 * M^2 + 0.424, for M <= 0.722
    Cd = 2.1 * exp(-1.2 * (M + 0.35)) - 8.9 * exp(-2.2 * (M + 0.35)) + 0.92, for M > 0.722
    """
    if mach <= 0.722:
        return 0.45 * mach**2 + 0.424

    from math import exp
    return 2.1 * exp(-1.2 * (mach + 0.35)) - 8.9 * exp(-2.2 * (mach + 0.35)) + 0.92


def calculate_cube_cd(mach: float) -> float:
    """Calculate drag coefficient for a cube based on Mach number.

    Based on Carter et al. (2009):
    Cd = 0.60 * M^2 + 1.04, for M <= 1.150
    Cd = 2.1 * exp(-1.16 * (M + 0.35)) - 6.5 * exp(-2.23 * (M + 0.35)) + 1.67, for M > 1.150
    """
    if mach <= 1.150:
        return 0.60 * mach**2 + 1.04

    from math import exp
    return 2.1 * exp(-1.16 * (mach + 0.35)) - 6.5 * exp(-2.23 * (mach + 0.35)) + 1.67



def relative_velocity(
    velocity_mps: Tuple[float, float, float],
    wind_mps: Tuple[float, float, float],
) -> Tuple[float, float, float]:
    """Return air-relative velocity components (m/s).

    Workbook logic subtracts the wind field from the fragment velocity before
    applying drag (`docs/methodology.md` §6). This helper keeps that behaviour
    self-contained so both the kernel and tests share the same implementation.
    """

    vx, vy, vz = velocity_mps
    wx, wy, wz = wind_mps
    return (vx - wx, vy - wy, vz - wz)


def speed_magnitude(components: Tuple[float, float, float]) -> float:
    """Return the Euclidean speed for the provided velocity components."""

    return hypot(components[0], components[1], components[2])


def dynamic_pressure(density_kg_m3: float, speed_mps: float) -> float:
    """Return dynamic pressure (Pa) per methodology §7 (½ ρ v²)."""

    return 0.5 * density_kg_m3 * speed_mps**2


def drag_force(speed_mps: float, density_kg_m3: float, params: DragParams) -> float:
    """Compute drag force magnitude (N).

    Mirrors the spreadsheet expression F = ½ ρ C_d A v² used on the
    particle parameters sheet and described in `docs/methodology.md` §7.
    """

    return dynamic_pressure(density_kg_m3, speed_mps) * params.cd * params.area_m2


def drag_acceleration(force_newtons: float, mass_kg: float) -> float:
    """Convert drag force to acceleration (m/s²) along velocity direction."""

    if mass_kg <= 0:
        raise ValueError("mass_kg must be positive to compute acceleration")
    return force_newtons / mass_kg


def drag_acceleration_vector(
    velocity_mps: Tuple[float, float, float],
    wind_mps: Tuple[float, float, float],
    density_kg_m3: float,
    mass_kg: float,
    params: DragParams,
) -> Tuple[float, float, float]:
    """Return drag acceleration vector components in m/s².

    The workbook applies drag opposite the air-relative velocity direction. The
    helper handles the zero-speed edge case gracefully by skipping drag if the
    fragment is effectively stationary relative to the air column.
    """

    rel_v = relative_velocity(velocity_mps, wind_mps)
    speed = speed_magnitude(rel_v)
    if speed == 0.0:
        return (0.0, 0.0, 0.0)

    force = drag_force(speed, density_kg_m3, params)
    accel_mag = drag_acceleration(force, mass_kg)
    scale = -accel_mag / speed
    return (rel_v[0] * scale, rel_v[1] * scale, rel_v[2] * scale)
