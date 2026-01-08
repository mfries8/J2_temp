# Phase 1 Reviewer Handoff

_Last updated: 2025-02-14_

## Scope Overview
Phase 1 delivers workbook formula extraction, schema alignment, and parity validation harnesses that demonstrate the Python implementation mirrors the legacy Excel workbook for key metrics.

## Key Artifacts (to provide at phase close)
- `formula_graph.json` with coverage summary and unresolved-node log.
- `docs/reference/formula_graph.json` now available (453,315 formulas parsed across 16 worksheets).
- Updated schemas/templates/fixtures reflecting extracted data contracts.
- Parity test suite outputs (e.g., `tests/parity/` reports, tolerance configs).
- `MODEL_ASSUMPTIONS.md` updates highlighting inferred constants or simplifications.
- Extraction tooling documentation and runbook notes.

## Current Status Snapshot
- Extraction prototype and schema alignment work underway (see `docs/phases/1/status.md`).
- Parity suite covers landing offsets, fall time, terminal velocity, and drift magnitude (terminal velocity tolerance tightened to ±1 m/s with Doc sign-off) plus fragment geometry guardrails for regression.
- Extractor coverage snapshot (`tests/fixtures/formula_coverage_snapshot.json`) shows 453,315 formula cells parsed overall with ≥99% coverage on Force graph / P,T / Vmet / position / vertical grid sheets and 52.1% formula coverage on `RAOB Used for Calcs` reflecting value-driven inputs.
- New parity harness `tests/test_parity_lateral_displacement.py` locks lateral displacement slices (rows 3–7) to workbook values, providing intermediate drift parity coverage.
- Parity bundle reproducible via `scripts/run_parity.sh` (ruff + mypy + parity tests); last run 2025-02-14 with all checks passing.

- Unresolved formulas: _None for `GA Blacksville 26 June 2025 1624 UTC 01.xlsx` (extractor sweep 2025-02-14 parsed 453,315 formula cells); keep logging list here for future workbooks if gaps appear._
- Deferred automation tasks: parity script in `scripts/run_parity.sh` ready; CI integration targeted for Phase 2 kickoff per roadmap.
- Physics-driven parity tolerances (1 m offsets, 0.5 s fall time, 1 m/s terminal velocity, 2 m / 0.01 km drift magnitude) endorsed by Doc reviewer (feedback received 2025-02-14).

## Risks & Assumptions
- Parity tolerances derive from methodology doc; deviations require sign-off.
- Workbook updates or alternate event sheets may necessitate re-extraction; document version/hash used for reference.
- Extraction tooling should remain deterministic; note environment requirements (Python version, libraries).

## Next Steps for Reviewer
- Review coverage metrics and unresolved formula list once available.
- Validate schema/template changes against methodology expectations.
- Confirm parity test tolerances and approve or flag discrepancies (Doc sign-off received for current thresholds; note future adjustments in Phase 2 backlog if required).

Please append decision notes, approvals, and follow-up actions when Phase 1 artifacts are ready for handoff.
