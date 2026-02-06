"""Utilities for reading and updating XLSForm settings sheet."""

import sys
from pathlib import Path
from typing import Dict, List, Optional

try:
    import openpyxl
except ImportError as exc:
    raise ImportError("openpyxl is required for settings utilities") from exc


SETTINGS_SHEET_NAME = "settings"
REQUIRED_SETTINGS_COLUMNS = ["form_title", "form_id"]


def _get_settings_sheet(wb):
    if SETTINGS_SHEET_NAME in wb.sheetnames:
        return wb[SETTINGS_SHEET_NAME]
    return None


def _get_header_map(sheet) -> Dict[str, int]:
    headers = [cell.value for cell in sheet[1]]
    header_map = {}
    for idx, header in enumerate(headers, start=1):
        if header:
            header_map[str(header).strip()] = idx
    return header_map


def read_form_settings(xlsx_path: Path) -> Dict[str, str]:
    """Read form_title and form_id from settings sheet."""
    result = {"form_title": "", "form_id": ""}
    if not xlsx_path or not Path(xlsx_path).exists():
        return result

    wb = openpyxl.load_workbook(xlsx_path)
    sheet = _get_settings_sheet(wb)
    if sheet is None:
        return result

    header_map = _get_header_map(sheet)
    row = 2
    for key in REQUIRED_SETTINGS_COLUMNS:
        col = header_map.get(key)
        if col:
            value = sheet.cell(row=row, column=col).value
            if value is not None:
                result[key] = str(value).strip()
    return result


def ensure_settings_columns(sheet) -> Dict[str, int]:
    """Ensure required settings columns exist; return header map."""
    header_map = _get_header_map(sheet)
    if not header_map:
        # Create header row if missing
        for idx, col in enumerate(REQUIRED_SETTINGS_COLUMNS, start=1):
            sheet.cell(row=1, column=idx, value=col)
        return _get_header_map(sheet)

    next_col = len(header_map) + 1
    for col in REQUIRED_SETTINGS_COLUMNS:
        if col not in header_map:
            sheet.cell(row=1, column=next_col, value=col)
            header_map[col] = next_col
            next_col += 1

    return header_map


def set_form_settings(xlsx_path: Path, form_title: Optional[str] = None, form_id: Optional[str] = None) -> bool:
    """Create/update settings sheet and set form_title/form_id."""
    if not xlsx_path:
        return False

    xlsx_path = Path(xlsx_path)
    if not xlsx_path.exists():
        return False

    wb = openpyxl.load_workbook(xlsx_path)
    sheet = _get_settings_sheet(wb)
    if sheet is None:
        sheet = wb.create_sheet(SETTINGS_SHEET_NAME)

    header_map = ensure_settings_columns(sheet)
    row = 2
    if form_title is not None:
        sheet.cell(row=row, column=header_map["form_title"], value=form_title)
    if form_id is not None:
        sheet.cell(row=row, column=header_map["form_id"], value=form_id)

    wb.save(xlsx_path)
    return True


def missing_required_settings(xlsx_path: Path) -> List[str]:
    """Return list of missing required settings fields."""
    settings = read_form_settings(xlsx_path)
    missing = [key for key in REQUIRED_SETTINGS_COLUMNS if not settings.get(key)]
    return missing
