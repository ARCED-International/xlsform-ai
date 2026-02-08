#!/usr/bin/env python3
"""Read-only settings status helper for import/validation flows."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Dict

# Add scripts directory for sibling imports.
_scripts_dir = Path(__file__).parent.resolve()
if str(_scripts_dir) not in sys.path:
    sys.path.insert(0, str(_scripts_dir))

from settings_utils import VERSION_FORMULA, read_form_settings  # noqa: E402


def _derive_suggestions(source_hint: str) -> Dict[str, str]:
    stem = Path(source_hint).stem if source_hint else "survey"
    cleaned = re.sub(r"[_\-]+", " ", stem).strip()
    cleaned = re.sub(r"\s+", " ", cleaned)
    title = cleaned.title() if cleaned else "Survey"

    form_id = re.sub(r"[^a-z0-9]+", "_", stem.lower())
    form_id = re.sub(r"_+", "_", form_id).strip("_")
    if not form_id:
        form_id = "survey_form"
    if form_id[0].isdigit():
        form_id = f"form_{form_id}"
    return {"form_title": title, "form_id": form_id}


def _print_text_status(status: Dict[str, object]) -> None:
    print("# XLSFORM_SETTINGS_STATUS")
    print(f"file: {status['file']}")
    print(f"form_title: {status['current']['form_title']}")
    print(f"form_id: {status['current']['form_id']}")
    print(f"version: {status['current']['version']}")
    print(f"version_is_formula: {str(status['version_is_formula']).lower()}")
    missing = status["missing"]
    print(f"missing_required: {', '.join(missing) if missing else 'none'}")
    print(f"suggested_form_title: {status['suggested']['form_title']}")
    print(f"suggested_form_id: {status['suggested']['form_id']}")
    print(f"recommended_command: {status['recommended_command']}")


def main() -> None:
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

    parser = argparse.ArgumentParser(description="Inspect settings row safely without modifying workbook.")
    parser.add_argument(
        "--file",
        "-f",
        default="survey.xlsx",
        help="Path to XLSForm workbook (default: survey.xlsx)",
    )
    parser.add_argument(
        "--source",
        default="",
        help="Source questionnaire path/name used to derive suggested title/id",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Print machine-readable JSON output",
    )
    args = parser.parse_args()

    xlsx_path = Path(args.file).expanduser().resolve()
    if not xlsx_path.exists():
        print(f"Error: XLSForm file not found: {xlsx_path}")
        sys.exit(1)

    current = read_form_settings(xlsx_path)
    current = {
        "form_title": str(current.get("form_title", "") or "").strip(),
        "form_id": str(current.get("form_id", "") or "").strip(),
        "version": str(current.get("version", "") or "").strip(),
    }
    missing = [key for key in ("form_title", "form_id", "version") if not current.get(key)]
    source_hint = args.source or xlsx_path.stem
    suggested = _derive_suggestions(source_hint)

    if current["form_title"] and current["form_id"]:
        command = (
            f'python scripts/update_settings.py --ensure-version-formula --file "{xlsx_path}"'
        )
    else:
        command = (
            "python scripts/update_settings.py "
            f'--title "{suggested["form_title"]}" '
            f'--id "{suggested["form_id"]}" '
            f'--ensure-version-formula --file "{xlsx_path}"'
        )

    status = {
        "file": str(xlsx_path),
        "current": current,
        "missing": missing,
        "version_is_formula": current["version"] == VERSION_FORMULA,
        "version_formula": VERSION_FORMULA,
        "suggested": suggested,
        "recommended_command": command,
    }

    if args.json:
        print(json.dumps(status, ensure_ascii=True, indent=2))
    else:
        _print_text_status(status)


if __name__ == "__main__":
    main()

