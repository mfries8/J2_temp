"""Unit tests for physics_core drag and geometry helpers."""

from __future__ import annotations

import math

import pytest

from meteor_darkflight.physics_core import (
    DragParams,
    cross_section_from_mass_density,
    drag_acceleration,
    drag_acceleration_vector,
    drag_force,
    dynamic_pressure,
    radius_from_mass_density,
    relative_velocity,
    speed_magnitude,
)


def test_dynamic_pressure_matches_half_rho_v2():
    assert dynamic_pressure(1.2, 10.0) == pytest.approx(60.0)


def test_drag_force_scales_with_area_and_cd():
    params = DragParams(cd=1.3, area_m2=0.05)
    force = drag_force(20.0, 1.0, params)
    expected = 0.5 * 1.0 * 1.3 * 0.05 * 400.0
    assert force == pytest.approx(expected)


def test_drag_acceleration_vector_aligns_with_relative_velocity():
    params = DragParams(cd=1.0, area_m2=0.01)
    velocity = (50.0, -10.0, -5.0)
    wind = (12.0, -8.0, 0.0)
    rel = relative_velocity(velocity, wind)
    accel = drag_acceleration_vector(velocity, wind, 1.2, 2.0, params)
    # Vector should point opposite relative velocity
    dot = accel[0] * rel[0] + accel[1] * rel[1] + accel[2] * rel[2]
    assert dot <= 0
    speed = speed_magnitude(rel)
    magnitude = math.sqrt(accel[0] ** 2 + accel[1] ** 2 + accel[2] ** 2)
    expected = drag_force(speed, 1.2, params) / 2.0
    assert magnitude == pytest.approx(expected, rel=1e-6)


def test_geometry_helpers_match_known_values():
    mass = 0.001  # kg
    density = 3320.0  # kg/m^3 (3.32 g/cm^3)
    radius = radius_from_mass_density(mass, density)
    area = cross_section_from_mass_density(mass, density)
    assert radius == pytest.approx(0.004158382511244203, rel=1e-9)
    assert area == pytest.approx(math.pi * radius**2)


def test_drag_acceleration_requires_positive_mass():
    with pytest.raises(ValueError):
        drag_acceleration(1.0, 0.0)
