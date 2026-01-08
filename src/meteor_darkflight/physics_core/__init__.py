"""Physics core exports for drag, ablation, and trajectory helpers."""

from .ablation import (
    ClassicalAblationParams,
    SimpleAblationParams,
    classical_ablation_rate,
    simple_ablation_rate,
)
from .drag import (
    DragParams,
    calculate_cube_cd,
    calculate_sphere_cd,
    drag_acceleration,
    drag_acceleration_vector,
    drag_force,
    dynamic_pressure,
    relative_velocity,
    speed_magnitude,
)
from .geometry import cross_section_from_mass_density, radius_from_mass_density
from .trajectory import (
    ExplicitEulerIntegrator,
    IntegrationEnvironment,
    Integrator,
    RungeKutta4Integrator,
    State,
)

__all__ = [
    "DragParams",
    "dynamic_pressure",
    "drag_force",
    "drag_acceleration",
    "drag_acceleration_vector",
    "relative_velocity",
    "speed_magnitude",
    "calculate_sphere_cd",
    "calculate_cube_cd",
    "SimpleAblationParams",
    "ClassicalAblationParams",
    "simple_ablation_rate",
    "classical_ablation_rate",
    "radius_from_mass_density",
    "cross_section_from_mass_density",
    "State",
    "IntegrationEnvironment",
    "Integrator",
    "ExplicitEulerIntegrator",
    "RungeKutta4Integrator",
]
