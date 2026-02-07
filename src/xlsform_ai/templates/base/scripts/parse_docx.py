#!/usr/bin/env python3
"""
Word Question Parser for XLSForm AI.

Extracts questions from Word (.docx) files and emits JSON.
Usage: python parse_docx.py <file.docx>
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Dict, List, Optional

# Add scripts directory to Python path for sibling imports.
_scripts_dir = Path(__file__).parent.resolve()
if str(_scripts_dir) not in sys.path:
    sys.path.insert(0, str(_scripts_dir))

try:
    from docx import Document as _Document
except ImportError:
    _Document = None


QUESTION_RE = re.compile(r"^\s*(\d+)[\.\)]\s+(.+)$")
CHOICE_RE = re.compile(r"^\s*(?:[a-zA-Z][\)\.]|[-*•])\s+(.+)$")


def _choice_value(label: str) -> str:
    value = re.sub(r"\s+", "_", label.strip().lower())
    value = re.sub(r"[^a-z0-9_]", "", value)
    return value[:48] or "option"


def _build_choice(choice_text: str) -> Dict[str, str]:
    label = choice_text.strip()
    return {"value": _choice_value(label), "label": label}


def extract_questions_from_docx(docx_path: str | Path) -> List[Dict[str, object]]:
    """Extract a list of question objects from a Word document."""
    if _Document is None:
        raise RuntimeError("python-docx is required. Install with: pip install python-docx")

    doc = _Document(str(docx_path))
    questions: List[Dict[str, object]] = []

    current_question: Optional[Dict[str, object]] = None
    current_choices: List[Dict[str, str]] = []
    question_num = 0

    for para in doc.paragraphs:
        text = para.text.strip()
        if not text:
            continue

        qmatch = QUESTION_RE.match(text)
        if qmatch:
            if current_question is not None:
                if current_choices:
                    current_question["choices"] = current_choices
                    current_question["type"] = (
                        "select_multiple" if len(current_choices) > 1 else "select_one"
                    )
                questions.append(current_question)

            question_num += 1
            current_question = {
                "number": qmatch.group(1) or str(question_num),
                "text": qmatch.group(2).strip(),
                "type": "text",
                "choices": None,
            }
            current_choices = []
            continue

        cmatch = CHOICE_RE.match(text)
        if cmatch and current_question is not None:
            current_choices.append(_build_choice(cmatch.group(1)))

    if current_question is not None:
        if current_choices:
            current_question["choices"] = current_choices
            current_question["type"] = "select_multiple" if len(current_choices) > 1 else "select_one"
        questions.append(current_question)

    return questions


def extract_questions(docx_path: str | Path, pages: Optional[str] = None) -> List[Dict[str, object]]:
    """
    Compatibility alias used in older command protocols.
    `pages` is accepted for interface parity but ignored for DOCX.
    """
    _ = pages
    return extract_questions_from_docx(docx_path)


def main() -> None:
    parser = argparse.ArgumentParser(description="Extract questions from Word document for XLSForm import")
    parser.add_argument("docx_file", help="Path to Word (.docx) file")
    parser.add_argument("--output", help="Output JSON file", default=None)

    args = parser.parse_args()
    source_path = Path(args.docx_file).resolve()
    if not source_path.exists():
        print(f"Error: File not found: {source_path}")
        sys.exit(1)

    if _Document is None:
        print("Error: python-docx is required. Install with: pip install python-docx")
        sys.exit(1)

    print(f"Parsing {source_path}...")
    questions = extract_questions_from_docx(source_path)

    try:
        from log_activity import ActivityLogger

        logger = ActivityLogger()
        question_summary = ", ".join(
            [f"{q.get('text', 'Unknown')[:30]} ({q.get('type', 'unknown')})" for q in questions[:5]]
        )
        if len(questions) > 5:
            question_summary += f"... and {len(questions) - 5} more"

        logger.log_action(
            action_type="import_docx",
            description=f"Imported {len(questions)} questions from Word document",
            details=f"Source: {source_path}\nQuestions: {question_summary}",
        )
    except Exception:
        pass

    output = {
        "source": str(source_path),
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
