"""Parity comparison helpers for legacy Excel golden values."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Iterable, Mapping


@dataclass(frozen=True)
class ScalarTolerance:
    """Absolute/relative tolerance guardrails for a scalar comparison."""

    absolute: float = 0.0
    relative: float = 0.0


@dataclass(frozen=True)
class MetricDiff:
    """Difference record when parity comparisons fall outside tolerance."""

    name: str
    expected: float
    actual: float
    difference: float
    tolerance: ScalarTolerance


def within_tolerance(expected: float, actual: float, tolerance: ScalarTolerance) -> bool:
    """Return True when the scalar comparison is within tolerance."""

    difference = abs(actual - expected)
    if tolerance.relative > 0 and expected != 0:
        allowed = max(tolerance.absolute, tolerance.relative * abs(expected))
    else:
        allowed = tolerance.absolute
    return difference <= allowed


def compare_nested_scalars(
    expected: Dict[str, float],
    actual: Dict[str, float],
    default_tolerance: ScalarTolerance,
    per_metric_tolerance: Dict[str, ScalarTolerance] | None = None,
) -> Iterable[MetricDiff]:
    """Compare nested dicts of scalars and yield diffs outside tolerance."""

    per_metric_tolerance = per_metric_tolerance or {}

    def flatten(prefix: str, node: Mapping[str, Any], out: Dict[str, float]) -> None:
        for key, value in node.items():
            name = f"{prefix}.{key}" if prefix else key
            if isinstance(value, Mapping):
                flatten(name, value, out)
            else:
                out[name] = _to_float(value)

    expected_flat: Dict[str, float] = {}
    actual_flat: Dict[str, float] = {}
    flatten("", expected, expected_flat)
    flatten("", actual, actual_flat)

    for metric, expected_value in expected_flat.items():
        if metric not in actual_flat:
            yield MetricDiff(
                name=metric,
                expected=expected_value,
                actual=float("nan"),
                difference=float("inf"),
                tolerance=per_metric_tolerance.get(metric, default_tolerance),
            )
            continue

        actual_value = actual_flat[metric]
        tolerance = per_metric_tolerance.get(metric, default_tolerance)
        if within_tolerance(expected_value, actual_value, tolerance):
            continue

        yield MetricDiff(
            name=metric,
            expected=expected_value,
            actual=actual_value,
            difference=abs(actual_value - expected_value),
            tolerance=tolerance,
        )


def _to_float(value: Any) -> float:
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, str):
        return float(value)
    raise TypeError(f"Expected numeric-compatible value, received {type(value)!r}")
