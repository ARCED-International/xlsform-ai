#!/usr/bin/env python3
"""
PDF Question Parser for XLSForm AI.

Extracts questions from PDF files and converts them to structured JSON.
Usage: python parse_pdf.py <file.pdf> --pages 1-10
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


QUESTION_RE = re.compile(r"^\s*(\d+)[\.\)]\s+(.+)$")
CHOICE_RE = re.compile(r"^\s*(?:[a-zA-Z][\)\.]|[-*•])\s+(.+)$")


def _choice_value(label: str) -> str:
    value = re.sub(r"\s+", "_", label.strip().lower())
    value = re.sub(r"[^a-z0-9_]", "", value)
    return value[:48] or "option"


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


def parse_questions_from_text(text: str, page_num: int) -> List[Dict[str, object]]:
    questions: List[Dict[str, object]] = []
    current_question: Optional[Dict[str, object]] = None
    current_choices: List[Dict[str, str]] = []

    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line:
            continue

        qmatch = QUESTION_RE.match(line)
        if qmatch:
            if current_question is not None:
                if current_choices:
                    current_question["choices"] = current_choices
                    current_question["type"] = (
                        "select_multiple" if len(current_choices) > 1 else "select_one"
                    )
                questions.append(current_question)

            current_question = {
                "number": qmatch.group(1),
                "text": qmatch.group(2).strip(),
                "type": "text",
                "choices": None,
                "page": page_num,
            }
            current_choices = []
            continue

        cmatch = CHOICE_RE.match(line)
        if cmatch and current_question is not None:
            choice_text = cmatch.group(1).strip()
            current_choices.append({"value": _choice_value(choice_text), "label": choice_text})

    if current_question is not None:
        if current_choices:
            current_question["choices"] = current_choices
            current_question["type"] = "select_multiple" if len(current_choices) > 1 else "select_one"
        questions.append(current_question)

    return questions


def detect_question_types(questions: List[Dict[str, object]]) -> None:
    """Refine question types for non-choice questions using simple keyword rules."""
    type_keywords = {
        "integer": ["age", "how many", "how old", "number of", "count"],
        "decimal": ["weight", "height", "price", "rate", "percentage"],
        "date": ["date of birth", "when", "date"],
        "geopoint": ["location", "gps", "coordinates", "where"],
        "select_one": ["which", "select one", "choose"],
        "select_multiple": ["select all", "check all", "multiple"],
    }

    for question in questions:
        if question.get("choices"):
            continue
        text = str(question.get("text", "")).lower()
        for q_type, keywords in type_keywords.items():
            if any(keyword in text for keyword in keywords):
                question["type"] = q_type
                break


def extract_text_from_pdf(
    pdf_path: str | Path,
    page_range: Optional[Tuple[int, int]] = None,
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
            text = pdf.pages[page_idx].extract_text() or ""
            if not text.strip():
                continue
            questions.extend(parse_questions_from_text(text, page_num))

    detect_question_types(questions)
    return questions


def extract_questions(pdf_path: str | Path, pages: Optional[str] = None) -> List[Dict[str, object]]:
    """Compatibility alias used in older command protocols."""
    page_range = _parse_page_range(pages)
    return extract_text_from_pdf(pdf_path, page_range=page_range)


def main() -> None:
    parser = argparse.ArgumentParser(description="Extract questions from PDF file for XLSForm import")
    parser.add_argument("pdf_file", help="Path to PDF file")
    parser.add_argument("--pages", help="Page range (e.g., 1-10)", default=None)
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
    questions = extract_text_from_pdf(source_path, page_range=page_range)

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
        "count": len(questions),
        "questions": questions,
    }
    json_output = json.dumps(output, ensure_ascii=False, indent=2)

    if args.output:
        output_path = Path(args.output).resolve()
        output_path.write_text(json_output, encoding="utf-8")
        print(f"Saved {len(questions)} questions to {output_path}")
    else:
        print(json_output)


if __name__ == "__main__":
    main()
