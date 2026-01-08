"""Parity checks for landing-offset metrics sourced from the workbook."""
from __future__ import annotations

import json
from dataclasses import dataclass
from math import sqrt
from pathlib import Path

from meteor_darkflight.validation import ScalarTolerance, compare_nested_scalars
from tests.parity_utils import cell_value, load_sheet

FIXTURES = Path(__file__).resolve().parent / "fixtures"
PARITY_FIXTURE = FIXTURES / "parity" / "landing_offsets_workbook.json"


@dataclass(frozen=True)
class WorkbookLandingOffsets:
    starting_position_utm: dict[str, float]
    landing_site_utm: dict[str, float]
    offset_from_start_m: dict[str, float]
    back_calculated_offset_km: dict[str, float]
    total_fall_time_s: float
    max_fall_velocity_mps: float
    horizontal_drift_m: float
    horizontal_drift_km: float
    fragment_properties: dict[str, float]
    terminal_kinetic_energy_j: float

    def as_dict(self) -> dict[str, dict[str, float]]:
        return {
            "starting_position_utm": self.starting_position_utm,
            "landing_site_utm": self.landing_site_utm,
            "offset_from_start_m": self.offset_from_start_m,
            "back_calculated_offset_km": self.back_calculated_offset_km,
            "total_fall_time_s": self.total_fall_time_s,
            "max_fall_velocity_mps": self.max_fall_velocity_mps,
            "horizontal_drift_m": self.horizontal_drift_m,
            "horizontal_drift_km": self.horizontal_drift_km,
            "fragment_properties": self.fragment_properties,
            "terminal_kinetic_energy_j": self.terminal_kinetic_energy_j,
        }


def load_workbook_offsets() -> WorkbookLandingOffsets:
    sheet_root, strings = load_sheet("particle parameters")

    def value(ref: str) -> float:
        raw = cell_value(sheet_root, strings, ref)
        if raw is None:
            raise ValueError(f"Cell {ref} did not contain a numeric value")
        if isinstance(raw, str):
            raise TypeError(f"Expected numeric cell {ref}, found string '{raw}'")
        return float(raw)

    volume_cm3 = value("D12")
    mass_kg = value("B21") * 1e-3
    max_velocity_mps = value("B13")

    fragment_properties = {
        "density_g_cm3": value("B16"),
        "volume_cm3": volume_cm3,
        "max_velocity_mph": value("B14"),
        "radius_cm": value("F15"),
        "radius_m": value("F17"),
        "cross_section_m2": value("F19"),
        "mass_kg": mass_kg,
    }

    return WorkbookLandingOffsets(
        starting_position_utm={
            "east_m": value("B6"),
            "north_m": value("C6"),
        },
        landing_site_utm={
            "east_m": value("B8"),
            "north_m": value("C8"),
        },
        offset_from_start_m={
            "east": value("E7"),
            "north": value("F7"),
        },
        back_calculated_offset_km={
            "east": value("E9"),
            "north": value("F9"),
        },
        total_fall_time_s=value("B12"),
        max_fall_velocity_mps=max_velocity_mps,
        horizontal_drift_m=sqrt(value("E7") ** 2 + value("F7") ** 2),
        horizontal_drift_km=sqrt(value("E9") ** 2 + value("F9") ** 2),
        fragment_properties=fragment_properties,
        terminal_kinetic_energy_j=0.5 * mass_kg * max_velocity_mps**2,
    )


def load_expected_offsets() -> dict[str, dict[str, float]]:
    with PARITY_FIXTURE.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    payload.pop("metadata", None)
    return payload


def test_landing_offsets_within_meter_tolerance():
    expected = load_expected_offsets()
    workbook_offsets = load_workbook_offsets().as_dict()

    tolerance = ScalarTolerance(absolute=1.0)
    per_metric = {
        "total_fall_time_s": ScalarTolerance(absolute=0.5),
        "max_fall_velocity_mps": ScalarTolerance(absolute=1.0),
        "horizontal_drift_m": ScalarTolerance(absolute=2.0),
        "horizontal_drift_km": ScalarTolerance(absolute=0.01),
        "fragment_properties.density_g_cm3": ScalarTolerance(absolute=0.01),
        "fragment_properties.volume_cm3": ScalarTolerance(absolute=0.5),
        "fragment_properties.max_velocity_mph": ScalarTolerance(absolute=0.5),
        "fragment_properties.radius_cm": ScalarTolerance(absolute=1e-4),
        "fragment_properties.radius_m": ScalarTolerance(absolute=1e-6),
        "fragment_properties.cross_section_m2": ScalarTolerance(absolute=1e-8),
        "fragment_properties.mass_kg": ScalarTolerance(absolute=1e-6),
        "terminal_kinetic_energy_j": ScalarTolerance(relative=1e-3),
    }
    diffs = list(
        compare_nested_scalars(
            expected,
            workbook_offsets,
            tolerance,
            per_metric_tolerance=per_metric,
        )
    )

    assert diffs == []


def test_landing_offsets_fail_when_outside_tolerance():
    expected = load_expected_offsets()
    candidate = load_workbook_offsets().as_dict()
    candidate["offset_from_start_m"]["east"] += 2.0  # exceed 1 m tolerance

    tolerance = ScalarTolerance(absolute=1.0)
    diffs = list(compare_nested_scalars(expected, candidate, tolerance))

    assert diffs, "Expected a diff when perturbing the east offset by >1 m"
    assert diffs[0].name == "offset_from_start_m.east"
