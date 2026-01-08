# Phase 0 Workplan - Bootstrap

## Purpose
Establish the foundational project scaffolding so future phases can focus on physics parity without reworking tooling. This plan assumes a single developer working in VSCode with OpenAI Codex assistance and occasional check-ins from a PhD domain reviewer.

## Objectives
- Stand up the Python package skeleton aligned with the architecture (module folders, `__init__.py`, docstrings).
- Configure tooling: dependency management, linting, type checking, formatting, and pytest.
- Add an initial event fixture plus placeholder data contracts to unblock early integration tests.
- Ensure CI basics (GitHub Actions or equivalent) run lint + type + unit stubs.
- Document setup and developer workflow for quick onboarding.

## Deliverables
- `pyproject.toml` with project metadata, runtime deps, and development extras.
- Ruff + mypy configuration (`ruff.toml`, `mypy.ini`) documented for local execution.
- `tests/` scaffolding with at least one smoke/CLI validation test.
- Sample data in `tests/fixtures/events/` and `docs/templates/` synced with JSON Schemas under `docs/schemas/`.
- Updated `README.md` covering environment setup, quality commands, and CLI usage.
- Reviewer handoff note summarizing Phase 0 completion (`docs/phases/0/reviewer-handoff.md`).
- _Deferred:_ CI workflow & VSCode automation tracked in `docs/phases/parking-lot/`.

## Constraints & Assumptions
- Single developer capacity - timebox tasks; prioritize automation that reduces manual toil later.
- Limited reviewer time - provide concise PR notes, automated validation outputs, and doc diffs for scientific oversight.
- Tooling must support Windows (developer) and Linux (CI) environments.
- No production-grade physics expected; placeholder implementations acceptable if tested and clearly marked.

## Work Breakdown

### 1. Repository & Environment Setup
- Confirm Python 3.12 baseline; configure virtual env via Poetry/PDM.
- Generate `pyproject.toml` with project metadata, core deps (`numpy`, `pydantic`, `typer`) and dev deps (`pytest`, `ruff`, `mypy`).
- Create `.python-version` or VSCode `.vscode/settings.json` pointing to interpreter for reproducible local runs.

### 2. Source Tree Alignment
- Ensure module directories under `src/meteor_darkflight/` all contain `__init__.py` and skeletal docstrings.
- Add placeholder implementations (return `NotImplementedError`) where missing to maintain importability.
- Document module responsibilities in-line with AGENTS architecture (brief comment header per module).

### 3. Tooling Configuration
- Add `ruff.toml` with target Python, selected rules, per-module ignores if needed.
- Configure `mypy.ini` with strict settings for physics modules, relaxed defaults elsewhere.
- Document manual quality checks in README (automation tasks deferred to parking lot).
- Optional: `.editorconfig` / VSCode recommendations (_deferred_).

### 4. Testing Scaffold
- Create `tests/conftest.py` with fixture for loading sample event JSON.
- Add `tests/test_imports.py` validating key modules import successfully and expose expected symbols.
- Include placeholder unit test for `event_ingest.parse_event` once implemented to read template fixture.

### 5. Sample Data & Schemas
- Sync `docs/templates/*.json` with Pydantic models; ensure they include `$schema`, `meta.units`, and `provenance` placeholders.
- Place fixture copies under `tests/fixtures/` and write README describing update process.
- Draft initial JSON Schema stubs (can be TODO-marked) for event and atmosphere artifacts.

### 6. Continuous Integration (Deferred)
- CI workflow, coverage publishing, and automation notes captured in parking lot for future phase.

### 7. Documentation & Knowledge Base
- Extend root `README.md` with setup, lint/type/test commands, and CLI quickstart.
- Add `docs/phases/0/status.md` to snapshot completion checklist and outstanding risks.
- Cross-reference AGENTS roles with implemented tooling (e.g., DevTools agent responsibilities).

### 8. Sign-off Preparation
- Prepare summary note for PhD reviewer highlighting:
  - Toolchain readiness and reproducibility proof (hash or command transcript).
  - Any physics-affecting placeholders explicitly deferred to Phase 1.
- Capture open questions or dependencies (e.g., CI secrets, data storage paths).

## Timeline (2 weeks target)
- **Day 1-2:** Environment + pyproject + base module cleanup.
- **Day 3-5:** Tooling configs, optional IDE settings, smoke tests.
- **Day 6-8:** Fixtures, schema alignment, CLI scaffolding update.
- **Day 9-10:** Documentation updates, reviewer package, backlog grooming for Phase 1 (CI moved to parking lot).
- **Day 11-12:** Buffer for feedback, polish, and issue tracking.
- **Day 13-14:** Reserve for deferred tasks planning / adjustments.

## Acceptance Criteria Checklist
- [x] `python -m pip install -e .[dev]` succeeds on clean clone.
- [x] `ruff check` passes locally (CI deferred).
- [x] `mypy src` passes (with documented suppressions if necessary).
- [x] `pytest` succeeds with sample fixtures.
- [ ] CI pipeline green on default branch (_deferred to parking lot_).
- [x] README + docs reflect actual commands and directory layout.
- [x] Reviewer handoff recorded with follow-up items tracked.

## Risk Log (Phase 0)
| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Tooling drift between local and CI environments | Medium | Medium | Lock dependency versions; document install steps; use consistent Python version. |
| Limited reviewer time delays feedback | Medium | Low | Provide concise status notes and automate validation outputs to reduce review load. |
| Placeholder physics misused downstream | Low | High | Clearly mark NotImplemented sections, guard with tests raising informative errors. |
| VSCode-specific configs break other IDEs | Low | Low | Keep optional under `.vscode/` and document alternatives. |

## Coordination Notes
- Use GitHub Projects or Issues to track tasks per work breakdown section.
- After each milestone, capture a short Loom/notes summary for the PhD reviewer.
- Coordinate with DevTools agent responsibilities by tagging tooling-related commits with `chore:` per Conventional Commits.
