"""Excel formula graph extraction utilities."""
from __future__ import annotations

import re
import zipfile
from dataclasses import dataclass
from typing import Dict, Iterable, List
from xml.etree import ElementTree as ET

NAMESPACE = "http://schemas.openxmlformats.org/spreadsheetml/2006/main"
REL_NAMESPACE = "http://schemas.openxmlformats.org/package/2006/relationships"
OFFICE_REL_NAMESPACE = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"

CELL_REF_PATTERN = re.compile(
    r"(?P<sheet>(?:'[^']+'|[A-Za-z0-9_\.]+)!)?"
    r"\$?[A-Za-z]{1,3}\$?[0-9]{1,7}"
)


@dataclass
class SheetCoverage:
    """Summary of cell counts for a single worksheet."""

    total_cells: int
    formula_cells: int
    value_cells: int

    def to_dict(self) -> Dict[str, int]:
        return {
            "total_cells": self.total_cells,
            "formula_cells": self.formula_cells,
            "value_cells": self.value_cells,
        }


@dataclass
class FormulaCell:
    """A single formula cell and its dependencies."""

    sheet: str
    cell: str
    formula: str
    references: List[str]

    def to_dict(self) -> Dict[str, object]:
        return {
            "sheet": self.sheet,
            "cell": self.cell,
            "formula": self.formula,
            "references": self.references,
        }


@dataclass
class FormulaGraph:
    """Collection of workbook formulas with coverage metadata."""

    cells: List[FormulaCell]
    coverage: Dict[str, SheetCoverage]

    def to_dict(self) -> Dict[str, object]:
        return {
            "cells": [cell.to_dict() for cell in self.cells],
            "coverage": {sheet: cov.to_dict() for sheet, cov in self.coverage.items()},
        }


def extract_formula_graph(workbook_path: str) -> FormulaGraph:
    """Parse an Excel workbook and construct a lightweight formula graph.

    This prototype focuses on enumerating formula locations, extracting cell
    references, and producing coverage metrics per worksheet so the
    FormulaGraph agent can identify remaining gaps.
    """

    with zipfile.ZipFile(workbook_path) as archive:
        sheet_targets = _sheet_targets(archive)
        cells: List[FormulaCell] = []
        coverage: Dict[str, SheetCoverage] = {}

        for sheet_name, target in sheet_targets:
            sheet_xml = archive.read(f"xl/{target}")
            sheet_cells, sheet_cov = _parse_sheet(sheet_name, sheet_xml)
            cells.extend(sheet_cells)
            coverage[sheet_name] = sheet_cov

    return FormulaGraph(cells=cells, coverage=coverage)


def _sheet_targets(archive: zipfile.ZipFile) -> List[tuple[str, str]]:
    workbook = ET.fromstring(archive.read("xl/workbook.xml"))
    rels = ET.fromstring(archive.read("xl/_rels/workbook.xml.rels"))

    rel_lookup = {
        rel.get("Id"): rel.get("Target")
        for rel in rels.findall(f"{{{REL_NAMESPACE}}}Relationship")
    }

    sheets: List[tuple[str, str]] = []
    for sheet in workbook.findall(f"{{{NAMESPACE}}}sheets/{{{NAMESPACE}}}sheet"):
        rel_id = sheet.get(f"{{{OFFICE_REL_NAMESPACE}}}id")
        target = rel_lookup.get(rel_id)
        if not target:
            continue
        sheets.append((sheet.get("name", "Unnamed"), target))

    return sheets


def _parse_sheet(sheet_name: str, sheet_xml: bytes) -> tuple[List[FormulaCell], SheetCoverage]:
    root = ET.fromstring(sheet_xml)
    cells: List[FormulaCell] = []
    total_cells = 0
    formula_cells = 0

    for cell in root.findall(f".//{{{NAMESPACE}}}c"):
        total_cells += 1
        formula_element = cell.find(f"{{{NAMESPACE}}}f")
        if formula_element is None:
            continue

        formula_cells += 1
        cell_ref = cell.get("r", "")
        formula_text = (formula_element.text or "").strip()
        references = sorted(set(_extract_references(formula_text)))
        cells.append(
            FormulaCell(
                sheet=sheet_name,
                cell=cell_ref,
                formula=formula_text,
                references=references,
            )
        )

    value_cells = total_cells - formula_cells
    coverage = SheetCoverage(
        total_cells=total_cells,
        formula_cells=formula_cells,
        value_cells=value_cells,
    )
    return cells, coverage


def _extract_references(formula: str) -> Iterable[str]:
    for match in CELL_REF_PATTERN.finditer(formula):
        yield match.group().replace("'", "")
