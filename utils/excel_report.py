"""Excel reports under ``reports/excel/`` (openpyxl + optional pandas).

CI / local aggregation::

    python -m utils.excel_report

Reads ``reports/junit-pytest.xml``, ``reports/junit-bs-smoke.xml``,
``reports/junit-bs-regression.xml``, and ``reports/junit-newman.xml`` when present,
then writes ``reports/excel/execution_report.xlsx``.
"""

from __future__ import annotations

import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any, Mapping, Sequence

import pandas as pd
from openpyxl import Workbook

from utils.config import project_root


def _excel_dir() -> Path:
    d = project_root() / "reports" / "excel"
    d.mkdir(parents=True, exist_ok=True)
    return d


def generate_report(
    results: Sequence[Mapping[str, Any]],
    *,
    filename: str = "execution_report.xlsx",
) -> Path:
    """
    Build a DataFrame from row dicts and write ``reports/excel/<filename>``.

    Example::

        generate_report(
            [
                {"Test": "Login", "Status": "Pass"},
                {"Test": "Video Play", "Status": "Fail"},
            ]
        )
    """
    path = _excel_dir() / filename
    df = pd.DataFrame(results)
    df.to_excel(path, index=False, engine="openpyxl")
    return path


def write_run_summary(
    rows: list[tuple[str, str]],
    filename: str = "summary.xlsx",
) -> Path:
    """Create a simple two-column workbook (Key, Value) without a DataFrame."""
    path = _excel_dir() / filename
    wb = Workbook()
    ws = wb.active
    ws.title = "Summary"
    ws.append(["Key", "Value"])
    for key, value in rows:
        ws.append([key, value])
    wb.save(path)
    return path


def rows_from_junit(path: Path, source: str) -> list[dict[str, Any]]:
    """Parse a JUnit XML file into table rows (Source, Test, Status, Detail)."""
    if not path.is_file():
        return []
    try:
        tree = ET.parse(path)
        root = tree.getroot()
    except ET.ParseError:
        return [{"Source": source, "Test": path.name, "Status": "Error", "Detail": "Invalid JUnit XML"}]

    rows: list[dict[str, Any]] = []
    for case in root.iter("testcase"):
        classname = case.get("classname") or ""
        name = case.get("name") or ""
        full = f"{classname}::{name}" if classname else name
        failure = case.find("failure")
        error = case.find("error")
        skipped = case.find("skipped")
        if skipped is not None:
            status = "Skip"
        elif failure is not None or error is not None:
            status = "Fail"
        else:
            status = "Pass"
        detail = ""
        for node in (failure, error):
            if node is not None and node.text:
                detail = (node.text or "").strip()[:500]
                break
        rows.append(
            {"Source": source, "Test": full, "Status": status, "Detail": detail}
        )
    return rows


def build_execution_rows() -> list[dict[str, Any]]:
    """Collect rows from known JUnit outputs under ``reports/``."""
    rep = project_root() / "reports"
    rows: list[dict[str, Any]] = []
    rows.extend(rows_from_junit(rep / "junit-pytest.xml", "pytest"))
    rows.extend(rows_from_junit(rep / "junit-bs-smoke.xml", "pytest-bs-smoke"))
    rows.extend(rows_from_junit(rep / "junit-bs-regression.xml", "pytest-bs-regression"))
    rows.extend(rows_from_junit(rep / "junit-newman.xml", "newman"))
    rows.extend(rows_from_junit(rep / "junit-appium.xml", "appium"))
    if not rows:
        rows.append(
            {
                "Source": "n/a",
                "Test": "(no JUnit files found)",
                "Status": "Info",
                "Detail": "Expected reports/junit-pytest.xml and/or reports/junit-newman.xml",
            }
        )
    return rows


def main() -> Path:
    """CLI entry for ``python -m utils.excel_report``."""
    return generate_report(build_execution_rows(), filename="execution_report.xlsx")


if __name__ == "__main__":
    main()
