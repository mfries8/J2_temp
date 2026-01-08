"""Parity checks for lateral displacement slices from the workbook."""
from __future__ import annotations

import json
from pathlib import Path

from meteor_darkflight.validation import ScalarTolerance, compare_nested_scalars
from tests.parity_utils import load_sheet, sheet_rows

FIXTURES = Path(__file__).resolve().parent / "fixtures"
PARITY_FIXTURE = FIXTURES / "parity" / "lateral_displacement_slices.json"


def load_expected_slices() -> dict[str, dict[str, float]]:
    with PARITY_FIXTURE.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    return payload["rows"]


def load_workbook_slices(row_ids: list[int]) -> dict[str, dict[str, float]]:
    sheet_root, strings = load_sheet("lateral displacement")
    rows = sheet_rows(sheet_root, strings)

    result: dict[str, dict[str, float]] = {}
    for idx in row_ids:
        row = rows[idx]
        result[str(idx)] = {
            "altitude_m": float(row["B"]),
            "x_disp_m": float(row["AF"]),
            "y_disp_m": float(row["AH"]),
            "x_rate": float(row["AJ"]),
            "y_rate": float(row["AL"]),
            "cumulative_drift_m": (float(row["AF"]) ** 2 + float(row["AH"]) ** 2) ** 0.5,
        }
    return result


def test_lateral_displacement_slices_match_workbook():
    expected = load_expected_slices()
    row_ids = [int(key) for key in expected]
    actual = load_workbook_slices(row_ids)

    tolerance = ScalarTolerance(absolute=1e-6)
    diffs = list(
        compare_nested_scalars(
            expected,
            actual,
            tolerance,
        )
    )

    assert not diffs, f"Mismatch in lateral displacement slices: {diffs}"
