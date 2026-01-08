# Phase 2 Workplan – Physics Parity & Validation Harness

> **Change control:** This charter remains stable after kickoff. Capture ongoing progress and risk updates in `docs/phases/2/status.md` and only amend the plan if Phase 2 scope changes.

## Purpose
Implement the Python physics modules and simulation kernels so the repository reproduces the legacy workbook numerically, while hardening validation tooling for automated regression checks.

## Objectives
- Translate extracted formula segments into production-ready physics modules (`physics_core/`, `sim_kernel/`).
- Achieve metric-level parity with the Phase 1 golden workbook across trajectory, velocity, and drift outputs within Doc-approved tolerances.
- Expand parity/validation harnesses (terminal energy, per-slice drift, ensemble stats) and wire them into repeatable automation.
- Document assumptions, reviewer sign-offs, and outstanding risks for Dev/Doc collaborators.

## Deliverables
- Implemented drag, trajectory integration, and ablation modules with unit tests and typed APIs.
- Updated simulation kernel (`sim_kernel`) capable of running single fragment and ensemble scenarios deterministically.
- Parity reports covering landing offsets, fall time, terminal velocity, drift magnitude, intermediate drift slices, and terminal kinetic energy; ensemble summary parity plan documented.
- CI-ready script or workflow invoking `scripts/run_parity.sh` (ruff + mypy + parity tests) and any new parity suites.
- Refreshed documentation (`MODEL_ASSUMPTIONS.md`, `docs/methodology.md` annotations, README status) reflecting physics implementation and tolerances.

## Constraints & Assumptions
- Phase 1 extraction artifacts (`formula_graph.json`, parity fixtures) remain the authoritative source for physics logic.
- Any tolerance adjustments require Doc review; record decisions in Phase 2 status and assumptions log.
- Implementation must preserve deterministic behaviour (fixed seeds, reproducible integrator outputs).
- Tooling should continue to pass `ruff`, `mypy src`, and the parity pytest bundle on Linux/macOS.

## Work Breakdown

### 1. Physics Module Implementation
- Derive drag, ablation, and state update functions from the formula graph with explicit units and docstrings.
- Introduce integration strategy abstractions (e.g., RK4, semi-implicit) per architecture guidance.
- Add targeted unit tests validating physics computations against workbook-derived constants.

### 2. Simulation Kernel & Ensemble Execution
- Wire physics modules into `sim_kernel` to run single-fragment trajectories end-to-end.
- Implement ensemble driver using deterministic RNG (PCG64) and ensure reproducible manifests.
- Capture intermediate state outputs required for later parity checks (per-slice drift, velocity decay).

### 3. Parity Harness Expansion
- Extend parity tests to include terminal kinetic energy, per-slice drift accumulation, and ensemble summary statistics.
- Update fixtures/expected values sourced from the workbook; document provenance in `tests/fixtures/parity/`.
- Ensure `scripts/run_parity.sh` (or successor) executes the expanded suite locally and in CI.

### 4. Validation & Documentation
- Update `MODEL_ASSUMPTIONS.md` with any new constants or approximations introduced by Python implementations.
- Note reviewer approvals and parity results in `docs/phases/2/status.md`.
- Add methodology cross-references where behaviour diverges or is clarified.

### 5. Automation & CI Integration
- Collaborate with DevTools to connect the parity bundle into GitHub Actions or preferred CI system.
- Publish parity/validation reports as artifacts for reviewer consumption.
- Track flaky tests or long-running suites; propose mitigations in the Phase 2 status log.

## Acceptance Criteria Checklist
- [ ] Physics modules (`physics_core/*`) implemented with unit tests and docstrings referencing workbook origins.
- [ ] Simulation kernel reproduces golden workbook metrics (landing offsets, fall time, terminal velocity, drift magnitude, terminal energy) within tolerances.
- [ ] Ensemble driver produces deterministic manifests and summary stats validated against workbook-derived expectations.
- [ ] Parity/validation harness updated and automated via `scripts/run_parity.sh` (or CI workflow); all checks pass.
- [ ] `MODEL_ASSUMPTIONS.md` and related docs reflect new physics behaviours and reviewer approvals.
- [ ] Reviewer handoff (`docs/phases/2/reviewer-handoff.md`) prepared with risks, metrics, and outstanding decisions.

## Risk Log (Phase 2)

Refer to the live risk register in `docs/phases/2/status.md#risks-and-mitigations`.

## Coordination Notes
- Continue referencing `docs/architecture.md` §3 for module responsibilities and data contracts.
- Align with DevTools on CI timelines and automation blockers; log any open items in the parking lot if deferred.
- Keep DocSmith informed of methodology updates to maintain consistent documentation.
- Surface parity deltas promptly to Doc/PhysicsSynth reviewers with reproduction steps and workbook references.
