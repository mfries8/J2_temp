#!/usr/bin/env pwsh
$ErrorActionPreference = "Stop"

# Run lint, type check, and parity-focused tests.
ruff check
mypy src

$originalPyPath = $env:PYTHONPATH
$pathSeparator = [System.IO.Path]::PathSeparator
if ([string]::IsNullOrWhiteSpace($originalPyPath)) {
    $env:PYTHONPATH = "src"
} else {
    $env:PYTHONPATH = "src$pathSeparator$originalPyPath"
}
try {
    pytest "tests/test_parity_*" @args
}
finally {
    $env:PYTHONPATH = $originalPyPath
}
