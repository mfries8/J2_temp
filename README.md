# JORMUNGANDR - Meteorite Darkflight Modeling

This repository is a modular Python darkflight modeler and strewn-field predictor. Each module contains placeholders and simple function/class stubs to be implemented.

See `docs/architecture.md` for full architecture and `docs/methodology.md` for physics methodology.

## Project Status
- Phase 1 (Extraction & Parity Foundations) complete; Phase 2 (Physics Parity & Validation Harness) kickoff in progress. See `docs/phases/1/status.md` for the wrap-up and `docs/phases/2/plan.md` (coming online) for next-phase details.
- Phase roadmap with upcoming milestones lives in `docs/roadmap.md` (open issue updates flow there).

## Getting Started (Python 3.12)

### 1. Install Python
Ensure Python 3.12 is installed. On Linux/macOS you can check with `python3 --version`; on Windows use `py --version`.

### 2. Create and Activate a Virtual Environment
Using a virtual environment keeps project dependencies isolated.

Linux / macOS:

```bash
python3.12 -m venv .venv
source .venv/bin/activate
```

Windows (PowerShell):

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Your prompt should now show `(.venv)` indicating the environment is active. Run `deactivate` to exit later.

### 3. Install Project + Development Tools

```bash
python -m pip install --upgrade pip
python -m pip install -e .[dev]
```

The `dev` extras install pytest, ruff, mypy, and related tooling.

### 4. Run Quality Checks

- Lint: `ruff check`
- Type check: `mypy src`
- Tests: `pytest`
- Parity bundle: `scripts/run_parity.sh` (ruff + mypy + parity pytest in one go)

Run these commands before committing to ensure the scaffold stays healthy.

### 5. Explore the CLI

The Typer CLI lives at `src/meteor_darkflight/cli_api/cli.py`. Example validation run using the bundled templates:

```bash
python -m meteor_darkflight.cli_api.cli validate \
  --event docs/templates/event.json \
  --dir docs/templates
```

### 6. Sample Data & Schemas

- Canonical templates: `docs/templates/`
- JSON Schemas: `docs/schemas/`
- Test fixtures: `tests/fixtures/`

Keep templates and fixtures in sync when updating schemas.

### 7. Further Reading

- Architecture overview: `docs/architecture.md`
- Methodology & physics notes: `docs/methodology.md`
- Phase roadmap and status: `docs/phases/`

For questions or contributions, open an issue or start a discussion in the repository.
