"""Tests for the deterministic ensemble driver."""

from __future__ import annotations

import numpy as np
import pytest

from meteor_darkflight.ensemble_driver import run_ensemble


def sample_generator(rng: np.random.Generator, index: int) -> dict[str, float]:
    return {
        "index": index,
        "east_m": float(rng.normal(loc=1000.0, scale=50.0)),
        "north_m": float(rng.normal(loc=-500.0, scale=25.0)),
    }


def runner(sample: dict[str, float]) -> dict[str, float]:
    return {"east_m": sample["east_m"], "north_m": sample["north_m"]}


def test_run_ensemble_is_deterministic():
    first = run_ensemble(5, sample_generator, runner, seed=42)
    second = run_ensemble(5, sample_generator, runner, seed=42)

    assert first["manifest"] == second["manifest"]
    assert [run.seed for run in first["runs"]] == [run.seed for run in second["runs"]]

    first_points = [run.result for run in first["runs"]]
    second_points = [run.result for run in second["runs"]]
    assert first_points == second_points


def test_default_summary_computes_statistics():
    ensemble = run_ensemble(3, sample_generator, runner, seed=0)
    summary = ensemble["summary"]
    assert summary.count == 3
    east_values = [run.result["east_m"] for run in ensemble["runs"]]
    assert summary.mean_east_m == pytest.approx(np.mean(east_values))
    assert summary.std_east_m == pytest.approx(np.std(east_values, ddof=0))
