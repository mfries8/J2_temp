# Test Fixtures

This directory stores canonical inputs used across unit and integration tests.

## Layout
- `events/<event_id>/` — canonical JSON artifacts for a given event.
  - `event.json`
  - `fragments.json`
  - `atmos_profile.json`
  - `radar_metadata.json`
- `formula_coverage_snapshot.json` — regression snapshot for workbook formula coverage used by extractor tests.
- `parity/landing_offsets_workbook.json` — golden landing offsets from the legacy workbook used by ParityGuard tests.

Fixtures originate from the templates under `docs/templates/` and should remain synchronized:

```bash
cp docs/templates/*.json tests/fixtures/events/<event_id>/
```

When updating a schema or template:
1. Adjust the corresponding Pydantic model.
2. Update the template in `docs/templates/`.
3. Refresh the mirrored fixture here.
4. Run `ruff check`, `mypy src`, and `pytest` to ensure compatibility.

These fixtures serve as golden inputs for regression testing and parity validation, so keep modifications reviewed and version-controlled.
