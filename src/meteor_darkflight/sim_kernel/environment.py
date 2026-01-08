"""Simulation environment implementation for darkflight integration."""

from __future__ import annotations

from dataclasses import dataclass
from math import exp, log
from typing import Callable, Iterable, List, Tuple

from meteor_darkflight.physics_core import (
    DragParams,
    SimpleAblationParams,
    calculate_cube_cd,
    calculate_sphere_cd,
    cross_section_from_mass_density,
    drag_acceleration_vector,
    relative_velocity,
    simple_ablation_rate,
    speed_magnitude,
)
from meteor_darkflight.physics_core.trajectory import IntegrationEnvironment, State

_R_SPECIFIC_DRY_AIR = 287.05  # J / (kg·K)


@dataclass(frozen=True)
class AtmosphericLevel:
    altitude_m: float
    density_kg_m3: float
    temperature_k: float
    wind_u_mps: float
    wind_v_mps: float


@dataclass
class AtmosphericProfile:
    """Atmospheric lookup with log-linear density interpolation."""

    levels: List[AtmosphericLevel]

    @classmethod
    def from_raw_levels(
        cls,
        raw_levels: Iterable[Tuple[float, float, float, float, float]]
    ) -> "AtmosphericProfile":
        """Build from (altitude, pressure_Pa, temperature_K, wind_u, wind_v)."""

        levels: List[AtmosphericLevel] = []
        for altitude_m, pressure_pa, temperature_k, wind_u, wind_v in raw_levels:
            density = pressure_pa / (_R_SPECIFIC_DRY_AIR * temperature_k)
            levels.append(
                AtmosphericLevel(
                    altitude_m=float(altitude_m),
                    density_kg_m3=density,
                    temperature_k=float(temperature_k),
                    wind_u_mps=float(wind_u),
                    wind_v_mps=float(wind_v),
                )
            )
        levels.sort(key=lambda level: level.altitude_m)
        return cls(levels)

    def _bracket(self, altitude_m: float) -> Tuple[AtmosphericLevel, AtmosphericLevel]:
        if altitude_m <= self.levels[0].altitude_m:
            return self.levels[0], self.levels[0]
        if altitude_m >= self.levels[-1].altitude_m:
            return self.levels[-1], self.levels[-1]
        for lower, upper in zip(self.levels, self.levels[1:]):
            if lower.altitude_m <= altitude_m <= upper.altitude_m:
                return lower, upper
        return self.levels[-1], self.levels[-1]

    def density(self, altitude_m: float) -> float:
        lower, upper = self._bracket(altitude_m)
        if lower.altitude_m == upper.altitude_m:
            return lower.density_kg_m3
        frac = (altitude_m - lower.altitude_m) / (upper.altitude_m - lower.altitude_m)
        if lower.density_kg_m3 <= 0 or upper.density_kg_m3 <= 0:
            return lower.density_kg_m3 + frac * (upper.density_kg_m3 - lower.density_kg_m3)
        log_interp = exp((1 - frac) * log(lower.density_kg_m3) + frac * log(upper.density_kg_m3))
        return log_interp

    def wind(self, altitude_m: float) -> Tuple[float, float, float]:
        lower, upper = self._bracket(altitude_m)
        if lower.altitude_m == upper.altitude_m:
            return (lower.wind_u_mps, lower.wind_v_mps, 0.0)
        frac = (altitude_m - lower.altitude_m) / (upper.altitude_m - lower.altitude_m)
        u = lower.wind_u_mps + frac * (upper.wind_u_mps - lower.wind_u_mps)
        v = lower.wind_v_mps + frac * (upper.wind_v_mps - lower.wind_v_mps)
        return (u, v, 0.0)

    def temperature(self, altitude_m: float) -> float:
        lower, upper = self._bracket(altitude_m)
        if lower.altitude_m == upper.altitude_m:
            return lower.temperature_k
        frac = (altitude_m - lower.altitude_m) / (upper.altitude_m - lower.altitude_m)
        return lower.temperature_k + frac * (upper.temperature_k - lower.temperature_k)

    def speed_of_sound(self, altitude_m: float) -> float:
        """Calculate speed of sound (m/s) at altitude."""
        temp_k = self.temperature(altitude_m)
        # a = sqrt(gamma * R * T)
        # gamma = 1.4 (adiabatic index for air)
        # R = 287.05 (specific gas constant for dry air)
        return float((1.4 * _R_SPECIFIC_DRY_AIR * temp_k) ** 0.5)


@dataclass
class DarkflightEnvironment(IntegrationEnvironment):
    """Environment bridging physics helpers with the integrator."""

    profile: AtmosphericProfile
    latitude_deg: float = 0.0
    magnetic_declination_deg: float = 0.0
    gravity_mps2: float = 9.80665
    fragment_density_kg_m3: float = 3400.0
    drag_coefficient: float = 1.0
    shape_factor: float = 1.0
    drag_model: str = "constant" # "constant", "sphere", "cube"
    ablation: SimpleAblationParams | None = None
    wind_model: Callable[[float], Tuple[float, float, float]] | None = None

    def _drag_params(self, mass_kg: float, cd: float) -> DragParams:
        area = cross_section_from_mass_density(mass_kg, self.fragment_density_kg_m3)
        return DragParams(cd=cd * self.shape_factor, area_m2=area)

    def acceleration(self, state: State) -> Tuple[float, float, float]:
        altitude = max(state.z, 0.0)
        density = self.profile.density(altitude)
        wind = self.wind_model(state.z) if self.wind_model else self.profile.wind(altitude)

        # Calculate Mach number
        speed_sound = self.profile.speed_of_sound(altitude)
        rel_v = relative_velocity((state.vx, state.vy, state.vz), wind)
        speed = speed_magnitude(rel_v)
        mach = speed / speed_sound if speed_sound > 0 else 0.0

        # Determine Cd
        if self.drag_model == "sphere":
            cd = calculate_sphere_cd(mach)
        elif self.drag_model == "cube":
            cd = calculate_cube_cd(mach)
        else:
            cd = self.drag_coefficient

        drag = drag_acceleration_vector(
            (state.vx, state.vy, state.vz),
            wind,
            density,
            max(state.mass, 1e-9),
            self._drag_params(max(state.mass, 0.0), cd),
        )

        # Coriolis Effect
        # a_c = -2 * Omega x v
        # Omega = [0, Omega * cos(lat), Omega * sin(lat)] (North-Up-East frame? No.)
        # Standard ENU (East-North-Up):
        # Omega vector at latitude phi:
        # Omega_x = 0 (East)
        # Omega_y = Omega * cos(phi) (North)
        # Omega_z = Omega * sin(phi) (Up)
        # v = [vx, vy, vz]
        # Cross product:
        # ax = -2 (Wy*vz - Wz*vy)
        # ay = -2 (Wz*vx - Wx*vz)
        # az = -2 (Wx*vy - Wy*vx)

        ax = drag[0]
        ay = drag[1]
        az = drag[2] - self.gravity_mps2

        if self.latitude_deg != 0.0:
            from math import cos, radians, sin
            omega = 7.2921159e-5  # Earth rotation rate rad/s
            lat_rad = radians(self.latitude_deg)

            # Omega vector in ENU
            wy = omega * cos(lat_rad)
            wz = omega * sin(lat_rad)

            # Coriolis acceleration
            # a_cor = -2 * (Omega x v)
            # x component: -2 * (wy*vz - wz*vy)
            # y component: -2 * (wz*vx - 0)
            # z component: -2 * (0 - wy*vx)

            ac_x = -2.0 * (wy * state.vz - wz * state.vy)
            ac_y = -2.0 * (wz * state.vx)
            ac_z = -2.0 * (-wy * state.vx)

            # print(f"DEBUG: Coriolis ax={ac_x:.4f}, ay={ac_y:.4f}, az={ac_z:.4f}")

            ax += ac_x
            ay += ac_y
            az += ac_z

        return (ax, ay, az)

    def mass_derivative(self, state: State) -> float:
        if not self.ablation:
            return 0.0
        altitude = max(state.z, 0.0)
        density = self.profile.density(altitude)
        wind = self.wind_model(state.z) if self.wind_model else self.profile.wind(altitude)
        rel_v = relative_velocity((state.vx, state.vy, state.vz), wind)
        speed_sq = rel_v[0] ** 2 + rel_v[1] ** 2 + rel_v[2] ** 2
        if speed_sq == 0.0:
            return 0.0
        speed = speed_sq ** 0.5
        return simple_ablation_rate(density, speed, self.ablation)
