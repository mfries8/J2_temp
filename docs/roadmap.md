# Project Roadmap

This roadmap expands the phase outline introduced in `docs/phases/0/plan.md`. Phase 0 (Bootstrap) is complete; phases 1 and beyond describe the staged evolution toward full Excel parity, uncertainty quantification, and automation.

## Phase 1 – Extraction & Parity Foundations
**Focus:** Reverse-engineer the legacy Excel workbook and align Python data contracts with real formulas.

**Key Deliverables**
- Automated extraction of Excel formula graph (`formula_graph.json`) with coverage >95% of non-UI cells.
- Mapping of workbook regions to domain concepts (drag, ablation, wind drift) documented in `MODEL_ASSUMPTIONS.md`.
- Updated Pydantic models / JSON Schemas refined from extracted formulas.
- Integration tests comparing extracted calculations to Excel outputs for representative cells.

**Exit Criteria**
- Formula graph topologically sortable with documented unresolved nodes.
- Schemas and templates validated against real workbook-derived data.
- Validation harness demonstrates parity for core derived quantities (e.g., terminal velocity, drift estimates).

## Phase 2 – Physics Parity & Validation Harness
**Focus:** Implement Python physics modules to achieve numerical parity with the spreadsheet on golden scenarios.

**Key Deliverables**
- Implemented drag/trajectory/ablation modules in `physics_core/` with unit tests and assumption annotations.
- `sim_kernel` running deterministic darkflight for baseline cases; fixtures for golden scenarios.
- Parity guardrails: `validation_report.md` including centroid/point deltas, runtime metrics.
- CI-ready test suite exercising golden scenarios (even if CI enablement is deferred).

**Exit Criteria**
- >=95% of golden case metrics within agreed tolerances (centroid delta, landing points, runtime).
- `pytest` suite includes parity comparisons; documentation updated with measured tolerances.
- Reviewer sign-off that Python results replicate Excel within allowed error bands.

## Phase 3 – Enhancement (UQ, Optimisation, Performance)
**Focus:** Expand the simulation to cover ensembles, uncertainty quantification, and performance hardening.

**Key Deliverables**
- Ensemble execution (Monte Carlo / Latin Hypercube) with reproducible sampling.
- Uncertainty outputs: `uncertainty_ellipses.geojson`, probability heatmaps.
- Optimisation routines for parameter calibration (`calibrated_params.json`).
- Performance profiling and regression guards (baseline runtime targets).

**Exit Criteria**
- Ensemble runs complete within target runtime (<60 s for 10k particles or agreed benchmark).
- Uncertainty products validated against historical recoveries where available.
- Performance reports (profiling output) checked into repo; thresholds documented.

## Phase 4 – Automation & Provenance
**Focus:** Orchestrate the full pipeline with caching, provenance, and reproducible builds.

**Key Deliverables**
- Coordinator/orchestration layer capable of running end-to-end with content-hash caching.
- Provenance graph (`provenance_graph.json`) linking inputs, code versions, and outputs.
- Automated build scripts or CI pipelines executing lint/type/test (and parity when feasible).
- Reporting artifacts: HTML/Markdown run summaries with embedded provenance and geospatial outputs.

**Exit Criteria**
- Single command (or CI job) can rebuild the entire pipeline for a fixture event.
- Provenance output audited to ensure traceability from raw inputs to final artifacts.
- Automation documentation (operations or runbook) updated and reviewed.

## Phase 5 – Advanced Enhancements / ML Assist (Future)
**Focus:** Incorporate advanced techniques once baseline parity and automation are stable.

**Potential Deliverables**
- Machine-learning assisted parameter estimation based on recovered meteorite datasets.
- Adaptive atmospheric ingestion (e.g., automatic HRRR/ECMWF fetch).
- Advanced visualisation agents (interactive 3D, recovery planning overlays).

**Exit Criteria**
- Demonstrated reduction in prediction error versus Phase 2 baseline.
- Clear rollback plan for ML-assisted features; documentation covering new assumptions.

---

_Phase numbering may evolve as new requirements emerge. Update this roadmap and the associated phase directories (`docs/phases/<n>/`) when scope or deliverables change._
