"""Geometry helpers for spherical fragments derived from workbook logic."""

from __future__ import annotations

import math


def radius_from_mass_density(mass_kg: float, density_kg_m3: float) -> float:
    """Return fragment radius (m) assuming a sphere.

    Workbook sheets derive radius from volume using the same relationship; see
    `docs/methodology.md` §5.
    """

    if density_kg_m3 <= 0:
        raise ValueError("density_kg_m3 must be positive")
    if mass_kg < 0:
        raise ValueError("mass_kg cannot be negative")

    volume_m3: float = mass_kg / density_kg_m3
    return math.pow((3.0 * volume_m3) / (4.0 * math.pi), 1.0 / 3.0)


def cross_section_from_mass_density(mass_kg: float, density_kg_m3: float) -> float:
    """Return cross-sectional area (m²) for a spherical fragment."""

    radius_m = radius_from_mass_density(mass_kg, density_kg_m3)
    return math.pi * radius_m**2
