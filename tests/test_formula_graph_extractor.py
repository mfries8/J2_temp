import json
from pathlib import Path

from meteor_darkflight.workbook_extract import extract_formula_graph

FIXTURES = Path(__file__).resolve().parent / "fixtures"
SNAPSHOT_PATH = FIXTURES / "formula_coverage_snapshot.json"


with SNAPSHOT_PATH.open("r", encoding="utf-8") as snapshot_file:
    SNAPSHOT = json.load(snapshot_file)

WORKBOOK_PATH = Path(__file__).resolve().parent.parent / SNAPSHOT["workbook"]


def test_extractor_reports_sheet_coverage():
    graph = extract_formula_graph(str(WORKBOOK_PATH))

    # Prototype should enumerate all worksheets and capture formulas
    assert len(graph.coverage) == 16

    lateral = graph.coverage["lateral displacement"]
    assert lateral.formula_cells > 0
    assert lateral.total_cells >= lateral.formula_cells


def test_extractor_traces_cross_sheet_references():
    graph = extract_formula_graph(str(WORKBOOK_PATH))

    dependencies = {
        tuple((cell.sheet, cell.cell))
        for cell in graph.cells
        if "RAOB Used for Calcs!C1" in cell.references
    }

    assert ("lateral displacement", "B1") in dependencies


def test_extractor_matches_coverage_snapshot():
    graph = extract_formula_graph(str(WORKBOOK_PATH))

    observed = {
        sheet: {
            "total_cells": cov.total_cells,
            "formula_cells": cov.formula_cells,
            "value_cells": cov.value_cells,
        }
        for sheet, cov in graph.coverage.items()
    }

    assert observed == SNAPSHOT["coverage"]

    total_formulas = sum(cov["formula_cells"] for cov in observed.values())
    assert total_formulas == SNAPSHOT["total_formula_cells"]
