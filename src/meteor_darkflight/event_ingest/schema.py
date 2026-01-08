"""Pydantic schemas for event input."""

from typing import List, Optional

from pydantic import BaseModel


class Location(BaseModel):
    lat: float
    lon: float
    altitude_m: float

class LuminousEnd(BaseModel):
    time_utc: str
    lat: float
    lon: float
    altitude_m: float
    speed_mps: float
    azimuth_deg: float
    elevation_deg: float

class FragmentHypothesis(BaseModel):
    id: str
    mass_kg: float
    density_kgm3: float
    cd: float
    shape_factor: Optional[float]

class EventModel(BaseModel):
    event_id: str
    luminous_end: LuminousEnd
    fragments: Optional[List[FragmentHypothesis]] = None
