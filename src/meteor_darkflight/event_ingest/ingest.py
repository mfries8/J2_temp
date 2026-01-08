"""Utilities to parse and normalize event inputs."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Iterable, List, Mapping

from pydantic import ValidationError

from .schema import EventModel, FragmentHypothesis


class EventIngestError(RuntimeError):
    """Raised when event-related input files are invalid."""


def _load_json(path: Path) -> object:
    try:
        with path.open("r", encoding="utf-8") as handle:
            return json.load(handle)
    except FileNotFoundError as exc:  # pragma: no cover - safety guard
        raise EventIngestError(f"Missing required file: {path}") from exc
    except json.JSONDecodeError as exc:
        raise EventIngestError(f"Invalid JSON in {path}: {exc}") from exc


def parse_event(path: str | Path) -> EventModel:
    """Load and validate an event JSON file."""

    event_path = Path(path)
    payload = _load_json(event_path)
    if not isinstance(payload, Mapping):
        raise EventIngestError(f"Event file {event_path} must contain a JSON object.")
    try:
        return EventModel(**payload)
    except ValidationError as exc:
        raise EventIngestError(f"Event schema validation failed for {event_path}: {exc}") from exc


def parse_fragments(path: str | Path) -> List[FragmentHypothesis]:
    """Load and validate fragment hypotheses list."""

    fragments_path = Path(path)
    payload = _load_json(fragments_path)
    if not isinstance(payload, Iterable):
        raise EventIngestError("Fragments file must contain an array of objects.")

    result: List[FragmentHypothesis] = []
    for index, fragment in enumerate(payload):
        if not isinstance(fragment, Mapping):
            raise EventIngestError(
                f"Fragment entry {index} in {fragments_path} must be a JSON object."
            )
        try:
            result.append(FragmentHypothesis(**fragment))
        except ValidationError as exc:
            raise EventIngestError(
                f"Fragment entry {index} in {fragments_path} failed validation: {exc}"
            ) from exc
    return result
