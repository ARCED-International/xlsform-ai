#!/usr/bin/env python3
"""
PDF Question Parser for XLSForm AI.

Extracts questions from PDF files and converts them to structured JSON.
Supports text blocks, tables, and mixed layouts.

Usage:
  python parse_pdf.py <file.pdf> --pages 1-10
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# Add scripts directory to Python path for sibling imports.
_scripts_dir = Path(__file__).parent.resolve()
if str(_scripts_dir) not in sys.path:
    sys.path.insert(0, str(_scripts_dir))

try:
    import pdfplumber as _pdfplumber
except ImportError:
    _pdfplumber = None


QUESTION_RE = re.compile(r"^\s*(?:Q(?:uestion)?\s*)?(\d+[A-Za-z]?)\s*[\.\):\-]\s*(.+)$")
CHOICE_RE = re.compile(r"^\s*(?:\(?[A-Za-z]\)|[A-Za-z][\.\)]|\(?\d+\)|\d+[\.\)]|[-*+])\s+(.+)$")
QUESTION_WORD_RE = re.compile(
    r"^(who|what|when|where|why|how|which|do|does|did|is|are|was|were|can|could|will|would)\b"
)
HEADER_QUESTION_TOKENS = ("question", "item", "prompt", "label")
HEADER_RESPONSE_TOKENS = ("response", "option", "choice", "answer")
HEADER_VARIABLE_TOKENS = ("variable", "var", "name", "code")


def _clean_text(value: str) -> str:
    return re.sub(r"\s+", " ", value or "").strip()


def _choice_value(label: str) -> str:
    value = re.sub(r"\s+", "_", label.strip().lower())
    value = re.sub(r"[^a-z0-9_]", "", value)
    return value[:48] or "option"


def _strip_choice_prefix(text: str) -> str:
    return _clean_text(re.sub(r"^\s*(?:\(?[A-Za-z]\)|[A-Za-z][\.\)]|\(?\d+\)|\d+[\.\)]|[-*+])\s+", "", text))


def _looks_like_question(text: str) -> bool:
    normalized = _clean_text(text)
    if not normalized:
        return False
    if QUESTION_RE.match(normalized):
        return True
    if normalized.endswith("?"):
        return True
    return bool(QUESTION_WORD_RE.match(normalized.lower()))


def _parse_option_blob(raw_text: str) -> List[str]:
    text = _clean_text(raw_text)
    if not text:
        return []

    lowered = text.lower()
    if "yes/no" in lowered or "yes / no" in lowered:
        return ["Yes", "No"]

    if "\n" in raw_text:
        candidates = [_strip_choice_prefix(item) for item in raw_text.splitlines() if _clean_text(item)]
    elif ";" in text:
        candidates = [_strip_choice_prefix(item) for item in raw_text.split(";") if _clean_text(item)]
    elif "|" in text:
        candidates = [_strip_choice_prefix(item) for item in raw_text.split("|") if _clean_text(item)]
    elif text.count(",") >= 2:
        candidates = [_strip_choice_prefix(item) for item in raw_text.split(",") if _clean_text(item)]
    elif re.search(r"\b\d{1,2}\b", text):
        candidates = _extract_numbered_inline_options(raw_text)
    elif CHOICE_RE.match(text):
        candidates = [_strip_choice_prefix(text)]
    else:
        candidates = []

    return [item for item in (_clean_text(x) for x in candidates) if item]


def _infer_non_select_type(question_text: str, response_hint: str = "") -> str:
    text = f"{question_text} {response_hint}".lower()
    if any(token in text for token in ["how old", "age", "how many", "count", "number of", "integer"]):
        return "integer"
    if any(token in text for token in ["decimal", "percentage", "percent", "amount", "price", "rate"]):
        return "decimal"
    if any(token in text for token in ["date", "when", "dd/mm", "mm/dd", "yyyy"]):
        return "date"
    if any(token in text for token in ["location", "gps", "coordinate"]):
        return "geopoint"
    return "text"


def _infer_select_mode(question_text: str, response_hint: str = "") -> str:
    text = f"{question_text} {response_hint}".lower()
    if any(token in text for token in ["select all", "all that apply", "multiple", "check all"]):
        return "select_multiple"
    return "select_one"


def _extract_numbered_inline_options(raw_text: str) -> List[str]:
    # Handles patterns like: "1 Always 2 Often 3 Sometimes 4 Rarely 5 Never"
    matches = re.findall(
        r"(?:^|\s)\(?\d{1,2}\)?[\.\:\-]?\s*([A-Za-z][A-Za-z/&\-\s]{1,60}?)(?=(?:\s+\(?\d{1,2}\)?[\.\:\-]?\s+)|$)",
        raw_text,
    )
    cleaned = [_clean_text(m) for m in matches if _clean_text(m)]
    return cleaned if len(cleaned) >= 2 else []


def _infer_standard_scale_options(question_text: str) -> List[str]:
    text = _clean_text(question_text).lower()
    if not text:
        return []

    if any(token in text for token in ["how often", "frequency", "frequently", "often do you"]):
        return ["Always", "Often", "Sometimes", "Rarely", "Never"]

    if "agree" in text and "disagree" in text:
        return ["Strongly agree", "Agree", "Neutral", "Disagree", "Strongly disagree"]

    if any(token in text for token in ["satisfied", "satisfaction"]):
        return [
            "Very satisfied",
            "Satisfied",
            "Neither satisfied nor dissatisfied",
            "Dissatisfied",
            "Very dissatisfied",
        ]

    return []


def _parse_page_range(page_arg: Optional[str]) -> Optional[Tuple[int, int]]:
    if not page_arg:
        return None
    value = page_arg.strip()
    if not value:
        return None
    if "-" in value:
        start_s, end_s = value.split("-", 1)
        start = int(start_s.strip())
        end = int(end_s.strip())
    else:
        start = int(value)
        end = int(value)
    if start <= 0 or end <= 0 or end < start:
        raise ValueError(f"Invalid page range: {page_arg}")
    return start, end


def parse_questions_from_lines(lines: List[str], page_num: int, auto_scale: bool = False) -> List[Dict[str, object]]:
    questions: List[Dict[str, object]] = []
    current_question: Optional[Dict[str, object]] = None
    current_choices: List[Dict[str, str]] = []
    auto_question_number = 0

    def finalize_current() -> None:
        nonlocal current_question, current_choices
        if current_question is None:
            return

        question_text = str(current_question.get("text", ""))
        if current_choices:
            current_question["choices"] = current_choices
            current_question["type"] = _infer_select_mode(question_text)
        else:
            if auto_scale:
                inferred_scale = _infer_standard_scale_options(question_text)
                if inferred_scale:
                    current_question["type"] = "select_one"
                    current_question["choices"] = [
                        {"value": _choice_value(label), "label": label} for label in inferred_scale
                    ]
                else:
                    current_question["choices"] = None
                    current_question["type"] = _infer_non_select_type(question_text)
            else:
                current_question["choices"] = None
                current_question["type"] = _infer_non_select_type(question_text)

        questions.append(current_question)
        current_question = None
        current_choices = []

    def start_question(text: str, number: Optional[str] = None) -> None:
        nonlocal current_question, current_choices, auto_question_number
        finalize_current()
        auto_question_number += 1
        current_question = {
            "number": str(number or auto_question_number),
            "text": _clean_text(text),
            "type": "text",
            "choices": None,
            "page": page_num,
        }
        current_choices = []

    def add_choice(label: str) -> None:
        if current_question is None:
            return
        cleaned = _clean_text(label)
        if not cleaned:
            return
        current_choices.append({"value": _choice_value(cleaned), "label": cleaned})

    for raw_line in lines:
        line = _clean_text(raw_line)
        if not line:
            continue

        qmatch = QUESTION_RE.match(line)
        if qmatch:
            start_question(qmatch.group(2), number=qmatch.group(1))
            continue

        if current_question is not None:
            cmatch = CHOICE_RE.match(line)
            if cmatch:
                add_choice(_strip_choice_prefix(line))
                continue

            options = _parse_option_blob(line)
            if len(options) >= 2:
                for option in options:
                    add_choice(option)
                continue

            if not current_choices and not _looks_like_question(line):
                current_question["text"] = _clean_text(f"{current_question['text']} {line}")
                continue

        if _looks_like_question(line):
            start_question(line)

    finalize_current()
    return questions


def _detect_header_index(row: List[str], tokens: Tuple[str, ...]) -> Optional[int]:
    for idx, value in enumerate(row):
        lowered = value.lower()
        if any(token in lowered for token in tokens):
            return idx
    return None


def parse_questions_from_table(table_rows: List[List[str]], page_num: int, auto_scale: bool = False) -> List[Dict[str, object]]:
    rows = [[_clean_text(str(cell)) for cell in row] for row in table_rows]
    rows = [row for row in rows if any(cell for cell in row)]
    if not rows:
        return []

    header_row_index = None
    question_col = None
    response_col = None
    variable_col = None

    for idx, row in enumerate(rows[:3]):
        maybe_question_col = _detect_header_index(row, HEADER_QUESTION_TOKENS)
        if maybe_question_col is None:
            continue
        question_col = maybe_question_col
        response_col = _detect_header_index(row, HEADER_RESPONSE_TOKENS)
        variable_col = _detect_header_index(row, HEADER_VARIABLE_TOKENS)
        header_row_index = idx
        break

    if header_row_index is None or question_col is None:
        flattened_lines: List[str] = []
        for row in rows:
            for cell in row:
                if cell:
                    flattened_lines.append(cell)
        return parse_questions_from_lines(flattened_lines, page_num, auto_scale=auto_scale)

    questions: List[Dict[str, object]] = []
    active_question: Optional[Dict[str, object]] = None

    def finalize_active() -> None:
        nonlocal active_question
        if active_question is None:
            return
        choices = active_question.get("choices") or []
        if choices:
            active_question["type"] = _infer_select_mode(str(active_question.get("text", "")))
        else:
            question_text = str(active_question.get("text", ""))
            if auto_scale:
                inferred_scale = _infer_standard_scale_options(question_text)
                if inferred_scale:
                    active_question["type"] = "select_one"
                    active_question["choices"] = [
                        {"value": _choice_value(label), "label": label} for label in inferred_scale
                    ]
                else:
                    active_question["type"] = _infer_non_select_type(question_text)
                    active_question["choices"] = None
            else:
                active_question["type"] = _infer_non_select_type(question_text)
                active_question["choices"] = None
        questions.append(active_question)
        active_question = None

    for row in rows[header_row_index + 1 :]:
        q_text = row[question_col] if question_col < len(row) else ""
        response_text = row[response_col] if response_col is not None and response_col < len(row) else ""
        variable_value = row[variable_col] if variable_col is not None and variable_col < len(row) else ""

        if q_text:
            finalize_active()
            parsed = QUESTION_RE.match(q_text)
            q_number = parsed.group(1) if parsed else None
            q_body = parsed.group(2) if parsed else q_text
            active_question = {
                "number": str(q_number or len(questions) + 1),
                "text": _clean_text(q_body),
                "type": "text",
                "choices": [],
                "page": page_num,
            }
            if variable_value:
                active_question["name"] = variable_value

            options = _parse_option_blob(response_text)
            if options:
                for item in options:
                    active_question["choices"].append({"value": _choice_value(item), "label": item})
            continue

        # Continuation rows for options in response column
        if active_question is not None and response_text:
            options = _parse_option_blob(response_text)
            if options:
                for item in options:
                    active_question["choices"].append({"value": _choice_value(item), "label": item})

    finalize_active()
    return questions


def _dedupe_questions(questions: List[Dict[str, object]]) -> List[Dict[str, object]]:
    seen = set()
    deduped: List[Dict[str, object]] = []
    for question in questions:
        key = (_clean_text(str(question.get("text", ""))).lower(), str(question.get("page", "")))
        if key in seen:
            continue
        seen.add(key)
        deduped.append(question)
    return deduped


def extract_text_from_pdf(
    pdf_path: str | Path,
    page_range: Optional[Tuple[int, int]] = None,
    auto_scale: bool = False,
) -> List[Dict[str, object]]:
    questions: List[Dict[str, object]] = []
    source = Path(pdf_path).resolve()
    if _pdfplumber is None:
        raise RuntimeError("pdfplumber is required. Install with: pip install pdfplumber")

    with _pdfplumber.open(str(source)) as pdf:
        start_idx = 0
        end_idx = len(pdf.pages)
        if page_range:
            start_idx = page_range[0] - 1
            end_idx = page_range[1]

        for page_idx in range(start_idx, min(end_idx, len(pdf.pages))):
            page_num = page_idx + 1
            page = pdf.pages[page_idx]

            # 1) Parse text blocks
            text = page.extract_text() or ""
            if text.strip():
                questions.extend(parse_questions_from_lines(text.splitlines(), page_num, auto_scale=auto_scale))

            # 2) Parse table blocks
            try:
                tables = page.extract_tables() or []
            except Exception:
                tables = []

            for table in tables:
                if table:
                    questions.extend(parse_questions_from_table(table, page_num, auto_scale=auto_scale))

    return _dedupe_questions(questions)


def extract_questions(pdf_path: str | Path, pages: Optional[str] = None, auto_scale: bool = False) -> List[Dict[str, object]]:
    """Compatibility alias used in older command protocols."""
    page_range = _parse_page_range(pages)
    return extract_text_from_pdf(pdf_path, page_range=page_range, auto_scale=auto_scale)


def main() -> None:
    parser = argparse.ArgumentParser(description="Extract questions from PDF file for XLSForm import")
    parser.add_argument("pdf_file", help="Path to PDF file")
    parser.add_argument("--pages", help="Page range (e.g., 1-10)", default=None)
    parser.add_argument(
        "--auto-scale",
        action="store_true",
        help="Auto-convert frequency/Likert text questions to select_one with standard choices",
    )
    parser.add_argument("--output", help="Output JSON file", default=None)
    args = parser.parse_args()

    source_path = Path(args.pdf_file).resolve()
    if not source_path.exists():
        print(f"Error: File not found: {source_path}")
        sys.exit(1)
    if _pdfplumber is None:
        print("Error: pdfplumber is required. Install with: pip install pdfplumber")
        sys.exit(1)

    try:
        page_range = _parse_page_range(args.pages)
    except ValueError as exc:
        print(f"Error: {exc}")
        sys.exit(1)

    print(f"Parsing {source_path}...")
    questions = extract_text_from_pdf(source_path, page_range=page_range, auto_scale=args.auto_scale)

    try:
        from log_activity import ActivityLogger

        logger = ActivityLogger()
        question_summary = ", ".join(
            [f"{q.get('text', 'Unknown')[:30]} ({q.get('type', 'unknown')})" for q in questions[:5]]
        )
        if len(questions) > 5:
            question_summary += f"... and {len(questions) - 5} more"

        logger.log_action(
            action_type="import_pdf",
            description=f"Imported {len(questions)} questions from PDF",
            details=f"Source: {source_path}\nPages: {args.pages or 'all'}\nQuestions: {question_summary}",
        )
    except Exception:
        pass

    output = {
        "source": str(source_path),
        "pages": args.pages,
        "auto_scale": bool(args.auto_scale),
        "count": len(questions),
        "questions": questions,
    }
    json_output = json.dumps(output, ensure_ascii=False, indent=2)

    if args.output:
        output_path = Path(args.output).resolve()
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(json_output, encoding="utf-8")
        print(f"Saved {len(questions)} questions to {output_path}")
    else:
        print(json_output)


if __name__ == "__main__":
    main()
