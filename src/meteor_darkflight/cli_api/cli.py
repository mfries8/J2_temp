"""Typer-based CLI scaffold."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Mapping, Optional

import typer
from pydantic import ValidationError

from meteor_darkflight.atmos_source import AtmosProfile, RadarMetadata
from meteor_darkflight.event_ingest import (
    EventIngestError,
    parse_event,
    parse_fragments,
)

app = typer.Typer()


def _load_json(path: Path) -> object:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


@app.command()
def validate(
    event: Path = typer.Option(..., exists=True, dir_okay=False, file_okay=True),
    directory: Optional[Path] = typer.Option(
        None, "--dir", exists=True, file_okay=False, dir_okay=True
    ),
):
    """Validate input files for an event."""

    base_dir = directory or event.parent
    errors: list[str] = []

    try:
        parse_event(event)
    except EventIngestError as exc:
        errors.append(str(exc))

    fragments_path = base_dir / "fragments.json"
    try:
        parse_fragments(fragments_path)
    except EventIngestError as exc:
        errors.append(str(exc))

    atmos_path = base_dir / "atmos_profile.json"
    try:
        atmos_payload = _load_json(atmos_path)
        if not isinstance(atmos_payload, Mapping):
            errors.append("Atmospheric profile must be a JSON object")
        else:
            AtmosProfile(**dict(atmos_payload))
    except FileNotFoundError:
        errors.append(f"Missing required file: {atmos_path}")
    except json.JSONDecodeError as exc:
        errors.append(f"Invalid JSON in {atmos_path}: {exc}")
    except ValidationError as exc:
        errors.append(f"Atmospheric profile validation failed: {exc}")

    radar_path = base_dir / "radar_metadata.json"
    if radar_path.exists():
        try:
            radar_payload = _load_json(radar_path)
            if not isinstance(radar_payload, Mapping):
                errors.append("Radar metadata must be a JSON object")
            else:
                RadarMetadata(**dict(radar_payload))
        except json.JSONDecodeError as exc:
            errors.append(f"Invalid JSON in {radar_path}: {exc}")
        except ValidationError as exc:
            errors.append(f"Radar metadata validation failed: {exc}")

    if errors:
        for message in errors:
            typer.secho(message, fg=typer.colors.RED)
        raise typer.Exit(code=1)

    typer.secho(
        "Validation passed for event inputs",
        fg=typer.colors.GREEN,
    )


@app.command()
def run(event: str):
    """Run full pipeline (validate -> preprocess -> simulate -> export)."""
    typer.echo(f"Run pipeline for {event} (not implemented)")


if __name__ == "__main__":
    app()
