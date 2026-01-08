#!/usr/bin/env bash
set -euo pipefail

# Run lint, type check, and parity-focused tests.
ruff check
mypy src
export PYTHONPATH="src${PYTHONPATH:+:$PYTHONPATH}"
pytest tests/test_parity_* "$@"
