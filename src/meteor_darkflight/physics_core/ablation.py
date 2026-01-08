"""Ablation and mass-loss helpers derived from workbook logic."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class SimpleAblationParams:
    """Parameters for the simplified workbook-style ablation model."""

    k_ab: float  # empirical coefficient (kg·m³·s³)


@dataclass(frozen=True)
class ClassicalAblationParams:
    """Parameters for the classical single-body ablation model."""

    sigma: float  # heat transfer coefficient
    q_star_j_per_kg: float  # heat of ablation


def simple_ablation_rate(
    density_kg_m3: float,
    rel_speed_mps: float,
    params: SimpleAblationParams,
) -> float:
    """Return dm/dt (kg/s) using the simplified workbook formulation.

    Matches the `dm/dt = -k_ab * ρ * |V_rel|³` placeholder noted in
    `docs/methodology.md` §8 when ablation remains active into darkflight.
    """

    return -params.k_ab * density_kg_m3 * rel_speed_mps**3


def classical_ablation_rate(
    area_m2: float,
    density_kg_m3: float,
    rel_speed_mps: float,
    params: ClassicalAblationParams,
) -> float:
    """Return dm/dt (kg/s) using the classical single-body approximation."""

    convective_term = 0.5 * density_kg_m3 * rel_speed_mps**3
    return -(params.sigma * area_m2 * convective_term) / params.q_star_j_per_kg
