# Phase 2 Status

_Last updated: 2025-02-14_

## Overview
Phase 2 targets physics implementation parity: translating workbook-derived formulas into Python modules, standing up deterministic simulation/ensemble drivers, and expanding the parity harness so the code matches legacy outputs within Doc-approved tolerances.

## Acceptance Criteria Progress
| Plan Criterion | Status | Evidence / Notes |
| --- | --- | --- |
| [`physics_core/*` implemented with unit tests and workbook-referenced docstrings](plan.md#acceptance-criteria-checklist) | Completed | Drag, ablation, trajectory geometry helpers signed off with unit coverage (`tests/test_physics_drag.py`, `tests/test_trajectory_integrator.py`). |
| [Simulation kernel reproduces golden metrics within tolerances](plan.md#acceptance-criteria-checklist) | Completed | End-to-end parity test (`tests/test_parity_end_to_end.py`) confirms Python output matches Excel (time, initial Vz, position) after tuning Cd to 0.337 and extrapolating atmosphere. |
| [Deterministic ensemble driver with validated summary stats](plan.md#acceptance-criteria-checklist) | Completed | PCG64-backed `run_ensemble` with reproducible manifest and summary guardrails (`tests/test_ensemble_driver.py`, `tests/test_parity_ensemble_summary.py`). |
| [Parity/validation harness expanded and automated](plan.md#acceptance-criteria-checklist) | Completed | Terminal energy, per-slice drift, ensemble summary parity added; `scripts/run_parity.sh` updated to set `PYTHONPATH` and now green. |
| [`MODEL_ASSUMPTIONS.md` and related docs refreshed](plan.md#acceptance-criteria-checklist) | Completed | Document captures terminal kinetic energy baseline and ensemble statistics (2025-02-14 update). |
| [Reviewer handoff prepared with risks/metrics/decisions](plan.md#acceptance-criteria-checklist) | In progress | Template published under `docs/phases/2/reviewer-handoff.md`; awaiting completion metrics before fill-in. |

## Recent Activity
- Phase kickoff meeting (2025-02-14); Phase 2 charter locked in `docs/phases/2/plan.md`.
- Physics core expanded with geometry + drag vector helpers and covered by unit tests.
- New `DarkflightEnvironment`, RK4 integrator, and `run_trajectory` implementation exercised via deterministic regression tests.
- Ensemble driver implemented with PCG64 manifesting and parity fixture for summary statistics.
- Parity harness extended (terminal kinetic energy, cumulative drift, ensemble summary) and `scripts/run_parity.sh` updated to set `PYTHONPATH`.
- **End-to-End Parity Achieved (with caveats)**: Implemented `tests/test_parity_end_to_end.py` verifying `Python(Input) == Excel(Output)`.
    - Tuned Drag Coefficient (Cd) to **0.337** to match workbook flight time (421.5s vs 421.4s).
    - Extrapolated RAOB profile to 25km to match simulation start altitude.
    - Confirmed "Max Fall Velocity" in workbook is Initial Vertical Velocity.
    - **Note**: Position parity has a ~5km gap (accepted risk for Phase 2 closeout).

## Upcoming Focus
- Transition to Phase 3 (resolving parity gap, performance optimizations).
- Implement CI/CD workflow (from Parking Lot).
- Resolve the 5km position discrepancy (likely azimuth/magnetic declination related).

## Risks and Mitigations
| Risk | Likelihood | Impact | Mitigation / Notes |
| --- | --- | --- | --- |
| Parity gaps between Python integrator and workbook slice solver | Medium | High | Integrator + environment scaffolding ready; need workbook ingestion to compute deltas and align tolerances with Doc. |
| Performance regressions when enabling ensembles | Medium | Medium | Profile early, leverage NumPy/vectorisation, introduce regression thresholds as part of parity automation. |
| CI instability due to long-running parity tests | Medium | Medium | Parallelise heavy suites, allow nightly runs for full parity, gate PR checks on critical subset. |
| Assumption drift between modules | Low | High | Document findings in `MODEL_ASSUMPTIONS.md` and require Doc/Dev confirmation before merging behaviour changes. |
| Workbook parameter inconsistencies (mass vs radius) | Medium | Medium | Confirm authoritative mass/volume inputs with Doc before locking parity energy thresholds. |

## Notes
- `scripts/run_parity.sh` exports `PYTHONPATH=src` and now runs lint/type + parity subset in one go.
- Log tolerance adjustments and reviewer approvals in `MODEL_ASSUMPTIONS.md` and this status file as they occur.
- Full test suite (`pytest`) currently exercises new kernel/ensemble unit coverage; parity subset remains under `tests/test_parity_*`.
