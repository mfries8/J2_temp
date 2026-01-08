# Phase 1 Workplan - Extraction & Parity Foundations

## Purpose
Reverse-engineer the legacy Excel workbook, formalise the resulting data contracts, and establish the baseline tests that prove Python scaffolding can reproduce spreadsheet behaviour for core calculations.

## Objectives
- Automate extraction of the workbook formula graph with high coverage and traceability to module responsibilities.
- Align JSON Schemas, Pydantic models, and templates with real workbook outputs and known physics assumptions.
- Stand up parity validation harnesses comparing Python calculations against Excel-derived values for benchmark scenarios.
- Document assumptions, unresolved formulas, and risks so PhysicsSynth and downstream agents have authoritative references.

## Deliverables
- `formula_graph.json` covering ≥95% of non-UI cells, with unresolved nodes captured in an issues log.
- Updated schema/model definitions reflecting workbook realities (`docs/schemas/`, `docs/templates/`, `tests/fixtures/`).
- Parity comparison tests and harnesses (`tests/parity/`) exercising key quantities (terminal velocity, drift, impact metrics).
- Maintained `MODEL_ASSUMPTIONS.md` entries describing extracted physics relationships and outstanding questions.
- Reviewer packet noting coverage metrics, unresolved formulas, and data-contract adjustments.
- Deferred automation/items tracked in parking lot when out of scope for Phase 1.

## Constraints & Assumptions
- Workbook structure remains stable; significant changes trigger revisit of extraction tooling.
- Excel automation may require manual seed ranges; document all manual interventions.
- Numerical tolerances for parity derived from methodology doc; coordinate with PhysicsSynth before relaxing them.
- Tooling must run cross-platform (Windows dev machines, Linux CI).

## Work Breakdown

### 1. Workbook Intake & Mapping
- Inventory workbook sheets/tabs; map to domain concepts per `docs/architecture.md` §3.
- Annotate source ranges → module responsibilities (`workbook_extract`, `physics_core`).
- Produce initial coverage report (cells parsed vs total target cells).

### 2. Formula Graph Extraction
- Implement/extend extraction script to emit `formula_graph.json` with dependency edges and cell metadata.
- Flag unsupported functions or references; log in `docs/reference/formula_issues.md` (new file if needed).
- Add regression test ensuring extraction tool emits deterministic graph for reference workbook fixture.

### 3. Data Contract Alignment
- Diff extracted output against existing schemas/templates; update JSON Schemas and Pydantic models accordingly.
- Sync `docs/templates/` and `tests/fixtures/` with new fields, units, and provenance requirements.
- Ensure CLI validation and fixtures remain green (`ruff check`, `mypy src`, `pytest`).
- Publish intermediate artifact schemas when workbook sheets expose new contracts (e.g., `vertical_grid.json`).

### 4. Parity Harness Construction
- Identify benchmark cells/outputs (terminal velocity, drift, impact energy) and capture expected values from Excel.
- Build parity tests comparing Python implementations (or interim notebook calculations) against golden values (landing offsets, total fall time, terminal velocity, drift magnitude, fragment geometry in Phase 1).
- Introduce configuration for tolerances, referencing `docs/methodology.md` assumptions (baseline physics tolerances captured in `validation/parity.py`: 1 m offsets, 0.5 s fall time, 1 m/s terminal velocity, 2 m / 0.01 km drift magnitude with Doc approval recorded 2025-02-14).

### 5. Assumptions & Documentation
- Update `MODEL_ASSUMPTIONS.md` with findings, including any approximations or inferred constants.
- Document extraction procedure and manual steps in `docs/architecture.md` appendix or dedicated doc.
- Keep AGENTS mapping current; note responsibilities for FormulaGraph and PhysicsSynth agents.

### 6. Deferred Automation & CI Coordination (as needed)
- Capture backlog items (e.g., full CI enablement, advanced extraction heuristics) in parking lot.
- Coordinate with DevTools agent if automation is required earlier.

## Timeline (target 3–4 weeks)
- **Week 1:** Workbook mapping, initial extraction prototype, coverage metrics.
- **Week 2:** Schema/template alignment, fixture updates, CLI validation kept passing.
- **Week 3:** Parity harness implementation, tolerance calibration, documentation updates.
- **Week 4 (buffer):** Reviewer feedback incorporation, backlog grooming, polish.

## Acceptance Criteria Checklist
- [x] `formula_graph.json` committed with coverage stats ≥95% of target cells.
- [x] Extraction tooling deterministic; regression tests cover key sheets.
- [x] Schemas/templates/fixtures remain mutually consistent and validated via CLI test suite.
- [x] Parity tests capture agreed-upon metrics and pass within documented tolerances.
- [x] `MODEL_ASSUMPTIONS.md` updated with new findings and TODOs for PhysicsSynth.
- [x] Reviewer handoff completed with outstanding risks and follow-ups noted.

## Risk Log (Phase 1)
| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Extraction misses hidden/indirect references | Medium | High | Iterate coverage reports, involve domain reviewer for workbook nuances. |
| Divergence between schema updates and fixtures | Medium | Medium | Pair changes with automated schema validation; run CLI tests after each update. |
| Parity tolerances unclear or disputed | Medium | High | Align tolerances with `docs/methodology.md`; schedule sign-off with PhysicsSynth reviewer. |
| Tooling brittleness across platforms | Low | Medium | Use cross-platform libraries (openpyxl/xlrd); run tests on Windows and Linux. |

## Coordination Notes
- Track tasks via issues/Projects board, tagging FormulaGraph & PhysicsSynth ownership where relevant.
- Share extraction coverage snapshots with reviewers weekly.
- Ensure documentation updates accompany schema or physics assumption changes, per AGENTS playbook.
- AtmoFusion ⇄ DarkflightSim vertical-grid contract captured in `docs/architecture.md` §3 (see module responsibilities for `atmos_fusion` and `sim_kernel`); reference that spec for future changes.
