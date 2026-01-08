"""Pydantic schemas for atmospheric and radar inputs."""

from __future__ import annotations

import math
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field, model_validator
from typing_extensions import Self


class AtmosLevel(BaseModel):
    model_config = ConfigDict(populate_by_name=True, extra="allow")

    altitude_m: float
    pressure_pa: float = Field(alias="pressure_Pa")
    temperature_k: float = Field(alias="temperature_K")
    wind_u_mps: float
    wind_v_mps: float
    wind_w_mps: Optional[float] = None

    @classmethod
    @model_validator(mode="before")
    def _normalize_units(cls, values: Dict[str, Any]) -> Dict[str, Any]:
        data = dict(values)
        if "pressure_Pa" not in data and "pressure_hPa" in data:
            data["pressure_Pa"] = float(data["pressure_hPa"]) * 100.0
        if "temperature_K" not in data and "temperature_C" in data:
            data["temperature_K"] = float(data["temperature_C"]) + 273.15
        if "wind_u_mps" not in data or "wind_v_mps" not in data:
            if "wind_speed_mps" in data and "wind_dir_deg" in data:
                speed = float(data["wind_speed_mps"])
                # Meteorological convention: direction wind is *from*
                angle = math.radians(float(data["wind_dir_deg"]))
                data.setdefault("wind_u_mps", -speed * math.sin(angle))
                data.setdefault("wind_v_mps", -speed * math.cos(angle))
        return data


class AtmosProfile(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    meta: Optional[Dict[str, Any]] = None
    levels: List[AtmosLevel]

    @model_validator(mode="after")
    def _ensure_sorted(self) -> Self:
        levels = self.levels or []
        if levels and any(
            earlier.altitude_m > later.altitude_m
            for earlier, later in zip(levels, levels[1:])
        ):
            raise ValueError("Atmospheric levels must be sorted by altitude_m ascending.")
        return self


class RadarMetadata(BaseModel):
    radar_site_id: str
    volume_time_utc: str
    level2_files: List[str]
    notes: Optional[str] = None
