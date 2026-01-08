# Phase 1 Status

_Last updated: 2025-02-14_

## Overview
Phase 1 focuses on extracting the legacy Excel formula graph, reconciling schemas with observed workbook outputs, and establishing parity validation harnesses that prove the Python scaffold matches spreadsheet behaviour for critical calculations.

## Completed
- Phase kickoff: scope, objectives, and acceptance criteria captured in `docs/phases/1/plan.md`.
- Workbook inventory with sheet → module mapping recorded in `docs/phases/1/workbook-mapping.md` (2025-02-14).
- Prototype formula graph extractor (`meteor_darkflight.workbook_extract.extract_formula_graph`) generating per-sheet coverage metrics and cross-sheet dependencies (2025-02-14).
- Vertical-grid ownership documented in `docs/architecture.md` §3 and cross-referenced in the Phase 1 plan (2025-02-14).
- Extractor regression tests hardened with coverage snapshot fixture (`tests/fixtures/formula_coverage_snapshot.json`) and added to PyTest suite (2025-02-14).
- Vertical grid schema/template published (`docs/schemas/vertical_grid.schema.json`, `docs/templates/vertical_grid.json`) to mirror workbook-derived integration slices (2025-02-14).
- Parity harness bootstrapped with landing-offset golden values (1 m absolute tolerance) via `tests/test_parity_landing_offsets.py` and `validation/parity.py` (2025-02-14).
- Parity coverage expanded to include total fall time (±0.5 s), terminal velocity (±1 m/s), and drift magnitude (±2 m / ±0.01 km) sourced from the workbook (2025-02-14).
- Extractor sweep (2025-02-14) confirmed no unresolved workbook formulas for `GA Blacksville 26 June 2025 1624 UTC 01.xlsx` (453,315 formula cells parsed).
- Parity coverage further extended to fragment geometry (density, volume, radius, cross-section, max velocity mph) with implementation guardrail tolerances codified in tests (2025-02-14).
- MODEL_ASSUMPTIONS.md created/updated with Phase 1 workbook observations and pending tolerance notes (2025-02-14).
- `formula_graph.json` exported under `docs/reference/` covering 453,315 formula cells across 16 sheets (2025-02-14).
- Doc confirmed terminal velocity tolerance tightened to ±1 m/s; parity tests updated to enforce the new guardrail (2025-02-14).
- Extractor coverage snapshot recorded in `tests/fixtures/formula_coverage_snapshot.json` (total 453,315 formula cells; key sheets ≥99% coverage for Force graph/P,T/Vmet/position/vertical grid, with RAOB Used for Calcs 52.1% driven by value cells) (2025-02-14).
- Intermediate drift parity captured via `tests/test_parity_lateral_displacement.py` validating lateral displacement slices (rows 3–7) against the workbook to guard cumulative drift rates (2025-02-14).

## In Progress
- None (Phase 1 scope delivered).
## Next Up
- Transition to Phase 2 (physics implementation parity) per roadmap; capture further parity candidates (terminal energy, ensemble stats) in the Phase 2 backlog.
- Coordinate with DevTools to wire `scripts/run_parity.sh` into CI as part of the Phase 2 kickoff.

### Parity Harness To-Do (Dev/AI)
- Automation: `scripts/run_parity.sh` (ruff, mypy, parity pytest) ready; next step is wiring into CI once Phase 2 begins.
- Candidate metrics: terminal kinetic energy, per-slice drift accumulation, ensemble summary stats (pending Doc priorities).

### Parity Tolerance Record (Doc-approved 2025-02-14)
- Landing offsets: ±1.0 m (absolute) — matches workbook displacement summary (`tests/fixtures/parity/landing_offsets_workbook.json`).
- Total fall time: ±0.5 s (absolute) — protects against timestep drift while tolerating spreadsheet rounding.
- Terminal fall velocity: ±1 m/s (absolute) — tightened per Doc sign-off to guard terminal speed parity more aggressively.
- Horizontal drift magnitude: ±2 m absolute / ±0.01 km back-calculated — keeps metre-level precision while allowing workbook rounding differences.

## Blockers / Risks
- None – workbook ranges accessible for current extracts; revisit if new events introduce protected sheets.

## Notes
- Update this status after each milestone; move items between sections as work progresses.
- Record coverage metrics (cells parsed vs target) here once extraction reports are available.
- Coverage snapshot highlights: Force graph 13501/13518 (99.9%), P,T 22500/22514 (99.9%), Vmet graph 22500/22518 (99.9%), position 13502/13515 (99.9%), vertical grid 22504/22522 (99.9%), RAOB Used for Calcs 45282/86904 (52.1% formula vs data inputs).
- Parity suite reproducible via `scripts/run_parity.sh` (ruff + mypy + parity tests) executed 2025-02-14.
