"""Helpers for extracting values from the legacy workbook in parity tests."""

from __future__ import annotations

from pathlib import Path
from typing import Dict, Tuple
from xml.etree import ElementTree as ET
from zipfile import ZipFile

from meteor_darkflight.workbook_extract.extractor import NAMESPACE, _sheet_targets

WORKBOOK_PATH = (
    Path(__file__).resolve().parent.parent
    / "docs"
    / "reference"
    / "GA Blacksville 26 June 2025 1624 UTC 01.xlsx"
)

_NS = "{" + NAMESPACE + "}"
_ERROR_VALUES = {"#DIV/0!", "#VALUE!", "#N/A", "#REF!", "#NAME?"}


def _shared_strings(archive: ZipFile) -> list[str]:
    root = ET.fromstring(archive.read("xl/sharedStrings.xml"))
    strings: list[str] = []
    for si in root.findall(f"{_NS}si"):
        text = si.find(f"{_NS}t")
        if text is not None and text.text is not None:
            strings.append(text.text)
            continue

        parts: list[str] = []
        for rich in si.findall(f"{_NS}r"):
            node = rich.find(f"{_NS}t")
            if node is not None and node.text is not None:
                parts.append(node.text)
        strings.append("".join(parts))
    return strings


def load_sheet(sheet_name: str) -> Tuple[ET.Element, list[str]]:
    """Return the XML root and shared strings for a workbook sheet."""

    with ZipFile(WORKBOOK_PATH) as archive:
        strings = _shared_strings(archive)
        sheet_map = dict(_sheet_targets(archive))
        sheet_xml = archive.read(f"xl/{sheet_map[sheet_name]}")

    return ET.fromstring(sheet_xml), strings


def cell_value(
    sheet_root: ET.Element,
    shared_strings: list[str],
    reference: str,
) -> float | str | None:
    """Fetch a cell value from the sheet (converts numeric and shared strings)."""

    cell = sheet_root.find(f".//{_NS}c[@r='{reference}']")
    if cell is None:
        raise KeyError(reference)

    value_node = cell.find(f"{_NS}v")
    if value_node is None or value_node.text is None:
        return None

    raw = value_node.text
    if raw in _ERROR_VALUES:
        return None
    if cell.get("t") == "s":
        return shared_strings[int(raw)]
    return float(raw)


def sheet_rows(
    sheet_root: ET.Element,
    shared_strings: list[str],
    *,
    skip_errors: bool = True,
) -> Dict[int, Dict[str, float | str]]:
    """Return a row/column mapping of the sheet values."""

    rows: Dict[int, Dict[str, float | str]] = {}
    for cell in sheet_root.findall(f".//{_NS}c"):
        reference = cell.get("r")
        if reference is None:
            continue
        column_part = "".join(filter(str.isalpha, reference))
        row_part = "".join(filter(str.isdigit, reference))
        if not row_part:
            continue

        row_index = int(row_part)
        value_node = cell.find(f"{_NS}v")
        if value_node is None or value_node.text is None:
            continue

        raw = value_node.text
        if raw in _ERROR_VALUES:
            if skip_errors:
                continue
            value: float | str = raw
        elif cell.get("t") == "s":
            value = shared_strings[int(raw)]
        else:
            value = float(raw)

        rows.setdefault(row_index, {})[column_part] = value

    return rows
