"""Parity check for deterministic ensemble summary statistics."""

from __future__ import annotations

import json
from pathlib import Path

from meteor_darkflight.ensemble_driver import run_ensemble
from meteor_darkflight.validation import ScalarTolerance, compare_nested_scalars

FIXTURES = Path(__file__).resolve().parent / "fixtures"
PARITY_FIXTURE = FIXTURES / "parity" / "ensemble_summary.json"
OFFSET_FIXTURE = FIXTURES / "parity" / "landing_offsets_workbook.json"


def _load_baseline_offsets() -> tuple[float, float]:
    with OFFSET_FIXTURE.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    landing = payload["landing_site_utm"]
    return float(landing["east_m"]), float(landing["north_m"])


def _sample_generator(rng, index: int):
    base_east, base_north = _load_baseline_offsets()
    return {
        "east_m": float(rng.normal(loc=base_east, scale=150.0)),
        "north_m": float(rng.normal(loc=base_north, scale=150.0)),
    }


def _runner(sample):
    return sample


def _load_expected_summary() -> dict[str, float | int | None]:
    with PARITY_FIXTURE.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    payload.pop("metadata", None)
    return payload


def test_ensemble_summary_matches_fixture():
    expected = _load_expected_summary()
    run_payload = run_ensemble(32, _sample_generator, _runner, seed=314)
    summary = run_payload["summary"].as_dict()

    tolerance = ScalarTolerance(relative=1e-6, absolute=1e-6)
    diffs = list(compare_nested_scalars(expected, summary, tolerance))
    assert diffs == []
