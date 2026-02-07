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
PROTECTED_SETTINGS_COLUMNS = {"version"}
_KEY_VALUE_HEADERS = {"column_name", "value"}


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


def _get_header_map_lower(sheet) -> Dict[str, int]:
    headers = [cell.value for cell in sheet[1]]
    header_map = {}
    try:
        from form_structure import normalize_header_name
    except Exception:
        normalize_header_name = None
    for idx, header in enumerate(headers, start=1):
        if header:
            header_name = str(header).strip()
            header_key = normalize_header_name(header_name) if normalize_header_name else header_name.lower()
            header_map[header_key] = idx
    return header_map


def _normalize_settings_sheet(sheet) -> None:
    """Normalize settings sheet to row 1 headers and row 2 values."""
    header_map_lower = _get_header_map_lower(sheet)
    if not _KEY_VALUE_HEADERS.issubset(header_map_lower):
        return

    name_col = header_map_lower["column_name"]
    value_col = header_map_lower["value"]
    settings_pairs = []

    for row_idx in range(2, sheet.max_row + 1):
        key = sheet.cell(row=row_idx, column=name_col).value
        value = sheet.cell(row=row_idx, column=value_col).value
        if key is None:
            continue
        key_str = str(key).strip()
        if not key_str:
            continue
        settings_pairs.append((key_str.lower(), value))

    if not settings_pairs:
        return

    sheet.delete_rows(1, sheet.max_row)

    for col_idx, (key, _) in enumerate(settings_pairs, start=1):
        sheet.cell(row=1, column=col_idx, value=key)

    for col_idx, (key, value) in enumerate(settings_pairs, start=1):
        if key in PROTECTED_SETTINGS_COLUMNS and isinstance(value, str) and value.startswith("="):
            sheet.cell(row=2, column=col_idx, value=value)
        else:
            sheet.cell(row=2, column=col_idx, value=value)


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
    header_map_lower = {k.lower(): v for k, v in header_map.items()}

    if _KEY_VALUE_HEADERS.issubset(header_map_lower):
        name_col = header_map_lower["column_name"]
        value_col = header_map_lower["value"]
        for row_idx in range(2, sheet.max_row + 1):
            key_val = sheet.cell(row=row_idx, column=name_col).value
            value_val = sheet.cell(row=row_idx, column=value_col).value
            if key_val is None:
                continue
            key = str(key_val).strip().lower()
            if key in result and value_val is not None:
                result[key] = str(value_val).strip()
    else:
        row = 2
        for key in REQUIRED_SETTINGS_COLUMNS:
            col = header_map.get(key) or header_map_lower.get(key)
            if col:
                value = sheet.cell(row=row, column=col).value
                if value is not None:
                    result[key] = str(value).strip()
    return result


def ensure_settings_columns(sheet) -> Dict[str, int]:
    """Ensure required settings columns exist; return header map.

    Values are always written to row 2, aligned with row 1 headers.
    """
    _normalize_settings_sheet(sheet)
    header_map = _get_header_map(sheet)
    header_map_lower = {k.lower(): v for k, v in header_map.items()}
    if not header_map:
        # Create header row if missing
        for idx, col in enumerate(REQUIRED_SETTINGS_COLUMNS, start=1):
            sheet.cell(row=1, column=idx, value=col)
        return _get_header_map(sheet)

    next_col = len(header_map) + 1
    for col in REQUIRED_SETTINGS_COLUMNS:
        if col not in header_map and col not in header_map_lower:
            sheet.cell(row=1, column=next_col, value=col)
            header_map[col] = next_col
            next_col += 1

    return header_map


def set_form_settings(xlsx_path: Path, form_title: Optional[str] = None, form_id: Optional[str] = None) -> bool:
    """Create/update settings sheet and set form_title/form_id.

    Values are written to row 2, aligned with headers in row 1.
    """
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
    header_map_lower = {k.lower(): v for k, v in header_map.items()}
    row = 2
    if form_title is not None:
        col = header_map.get("form_title") or header_map_lower.get("form_title")
        if col:
            sheet.cell(row=row, column=col, value=form_title)
    if form_id is not None:
        col = header_map.get("form_id") or header_map_lower.get("form_id")
        if col:
            sheet.cell(row=row, column=col, value=form_id)

    # Never overwrite protected columns like version (often formula-driven)
    for protected in PROTECTED_SETTINGS_COLUMNS:
        if protected in header_map:
            pass

    wb.save(xlsx_path)
    return True


def missing_required_settings(xlsx_path: Path) -> List[str]:
    """Return list of missing required settings fields."""
    settings = read_form_settings(xlsx_path)
    missing = [key for key in REQUIRED_SETTINGS_COLUMNS if not settings.get(key)]
    return missing
