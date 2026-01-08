"""Validation and parity checks against golden outputs."""

from .parity import MetricDiff, ScalarTolerance, compare_nested_scalars, within_tolerance
from .validate import run_validation

__all__ = [
    "run_validation",
    "MetricDiff",
    "ScalarTolerance",
    "compare_nested_scalars",
    "within_tolerance",
]
