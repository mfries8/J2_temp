"""Deterministic ensemble execution utilities."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, List, Sequence

import numpy as np


@dataclass(frozen=True)
class EnsembleRun:
    index: int
    seed: int
    sample: Any
    result: Any


@dataclass(frozen=True)
class EnsembleSummary:
    count: int
    mean_east_m: float | None
    mean_north_m: float | None
    std_east_m: float | None
    std_north_m: float | None

    def as_dict(self) -> dict[str, float | int | None]:
        return {
            "count": self.count,
            "mean_east_m": self.mean_east_m,
            "mean_north_m": self.mean_north_m,
            "std_east_m": self.std_east_m,
            "std_north_m": self.std_north_m,
        }


def _default_summary(results: Sequence[Any]) -> EnsembleSummary:
    east: List[float] = []
    north: List[float] = []
    for result in results:
        if isinstance(result, dict):
            east_val = result.get("east_m")
            north_val = result.get("north_m")
        else:
            east_val = getattr(result, "east_m", None)
            north_val = getattr(result, "north_m", None)
        if east_val is None or north_val is None:
            continue
        east.append(float(east_val))
        north.append(float(north_val))

    if not east:
        return EnsembleSummary(count=len(results), mean_east_m=None, mean_north_m=None, std_east_m=None, std_north_m=None)

    east_array = np.array(east)
    north_array = np.array(north)
    return EnsembleSummary(
        count=len(results),
        mean_east_m=float(east_array.mean()),
        mean_north_m=float(north_array.mean()),
        std_east_m=float(east_array.std(ddof=0)),
        std_north_m=float(north_array.std(ddof=0)),
    )


def run_ensemble(
    samples: int,
    sample_generator: Callable[[np.random.Generator, int], Any],
    runner: Callable[[Any], Any],
    *,
    seed: int = 0,
    summary_fn: Callable[[Sequence[Any]], EnsembleSummary] | None = None,
) -> dict[str, Any]:
    """Run an ensemble with deterministic RNG (PCG64) and summarise outputs."""

    if samples <= 0:
        raise ValueError("samples must be positive")

    rng = np.random.Generator(np.random.PCG64(seed))
    runs: List[EnsembleRun] = []
    results: List[Any] = []

    for index in range(samples):
        run_seed = int(rng.bit_generator.state["state"]["state"])
        sample = sample_generator(rng, index)
        result = runner(sample)
        runs.append(EnsembleRun(index=index, seed=run_seed, sample=sample, result=result))
        results.append(result)

    summary = summary_fn(results) if summary_fn else _default_summary(results)

    return {
        "manifest": {
            "generator": "PCG64",
            "seed": seed,
            "samples": samples,
        },
        "runs": runs,
        "summary": summary,
    }
