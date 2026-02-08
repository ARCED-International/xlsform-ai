#!/usr/bin/env python3
"""Summarize parser JSON output for /xlsform-import workflows."""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter
from pathlib import Path
from typing import Any, Dict, List


_SCALE_HINT_RE = re.compile(
    r"\b("
    r"how often|frequency|agree|disagree|strongly|rarely|never|always|sometimes|"
    r"not at all|several days|more than half the days|nearly every day|"
    r"times in the last|past (day|week|month)|in the last"
    r")\b",
    flags=re.IGNORECASE,
)


def _safe_text(value: Any) -> str:
    if value is None:
        return ""
    text = str(value).strip()
    return re.sub(r"\s+", " ", text)


def _shorten(value: str, width: int = 90) -> str:
    if len(value) <= width:
        return value
    return f"{value[: max(0, width - 3)]}..."


def _looks_like_scale_text(question: Dict[str, Any]) -> bool:
    q_type = _safe_text(question.get("type")).lower()
    if q_type != "text":
        return False
    text = _safe_text(question.get("text"))
    if not text:
        return False
    return bool(_SCALE_HINT_RE.search(text))


def _normalize_questions(payload: Dict[str, Any]) -> List[Dict[str, Any]]:
    raw_questions = payload.get("questions")
    if isinstance(raw_questions, list):
        return [q for q in raw_questions if isinstance(q, dict)]
    if isinstance(payload, list):
        return [q for q in payload if isinstance(q, dict)]
    return []


def _build_summary(payload: Dict[str, Any], path: Path, max_samples: int) -> Dict[str, Any]:
    questions = _normalize_questions(payload)
    type_counts = Counter(_safe_text(q.get("type")).lower() or "unknown" for q in questions)
    type_counts_sorted = dict(sorted(type_counts.items(), key=lambda item: (-item[1], item[0])))

    with_choices = [q for q in questions if isinstance(q.get("choices"), list) and q.get("choices")]
    scale_text = [q for q in questions if _looks_like_scale_text(q)]
    media = payload.get("media") if isinstance(payload.get("media"), dict) else {}

    samples = []
    for idx, question in enumerate(questions[: max(0, max_samples)], start=1):
        samples.append(
            {
                "index": idx,
                "number": _safe_text(question.get("number")),
                "type": _safe_text(question.get("type")) or "unknown",
                "text": _shorten(_safe_text(question.get("text"))),
            }
        )

    scale_samples = []
    for idx, question in enumerate(scale_text[: max(0, max_samples)], start=1):
        scale_samples.append(
            {
                "index": idx,
                "number": _safe_text(question.get("number")),
                "text": _shorten(_safe_text(question.get("text"))),
            }
        )

    return {
        "file": str(path),
        "source": _safe_text(payload.get("source")),
        "auto_scale": bool(payload.get("auto_scale", False)),
        "questions_total": len(questions),
        "question_types": type_counts_sorted,
        "questions_with_choices": len(with_choices),
        "text_questions": type_counts.get("text", 0),
        "select_one_questions": type_counts.get("select_one", 0),
        "select_multiple_questions": type_counts.get("select_multiple", 0),
        "potential_scale_text_questions": len(scale_text),
        "media": {
            "enabled": bool(media.get("enabled", False)),
            "directory": _safe_text(media.get("directory")),
            "prefix": _safe_text(media.get("prefix")),
            "saved_count": int(media.get("saved_count", 0) or 0),
        },
        "samples": samples,
        "potential_scale_text_samples": scale_samples,
    }


def _print_text_summary(summary: Dict[str, Any]) -> None:
    print("# XLSFORM_IMPORT_SUMMARY")
    print(f"file: {summary.get('file', '')}")
    print(f"source: {summary.get('source', '')}")
    print(f"auto_scale: {str(bool(summary.get('auto_scale', False))).lower()}")
    print(f"questions_total: {summary.get('questions_total', 0)}")
    print(f"questions_with_choices: {summary.get('questions_with_choices', 0)}")
    print(f"text_questions: {summary.get('text_questions', 0)}")
    print(f"select_one_questions: {summary.get('select_one_questions', 0)}")
    print(f"select_multiple_questions: {summary.get('select_multiple_questions', 0)}")

    media = summary.get("media", {})
    print(f"media_enabled: {str(bool(media.get('enabled', False))).lower()}")
    print(f"media_directory: {media.get('directory', '')}")
    print(f"media_prefix: {media.get('prefix', '')}")
    print(f"media_saved_count: {media.get('saved_count', 0)}")

    print("question_types:")
    q_types = summary.get("question_types", {})
    if not q_types:
        print("  - none: 0")
    else:
        for q_type, count in q_types.items():
            print(f"  - {q_type}: {count}")

    print("sample_questions:")
    samples = summary.get("samples", [])
    if not samples:
        print("  - none")
    else:
        for sample in samples:
            number = sample.get("number")
            number_fragment = f"#{number} " if number else ""
            print(f"  - {sample.get('index')}. [{sample.get('type')}] {number_fragment}{sample.get('text')}")

    print(f"potential_scale_text_questions: {summary.get('potential_scale_text_questions', 0)}")
    scale_samples = summary.get("potential_scale_text_samples", [])
    if scale_samples:
        print("potential_scale_text_samples:")
        for sample in scale_samples:
            number = sample.get("number")
            number_fragment = f"#{number} " if number else ""
            print(f"  - {sample.get('index')}. {number_fragment}{sample.get('text')}")


def main() -> None:
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

    parser = argparse.ArgumentParser(description="Summarize XLSForm import parser output JSON.")
    parser.add_argument(
        "--file",
        "-f",
        required=True,
        help="Path to parser output JSON (for example .xlsform-ai/tmp/import.json)",
    )
    parser.add_argument(
        "--max-samples",
        type=int,
        default=10,
        help="Maximum number of sample questions to print",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Print machine-readable JSON summary",
    )
    args = parser.parse_args()

    path = Path(args.file).expanduser().resolve()
    if not path.exists():
        print(f"Error: File not found: {path}")
        sys.exit(1)

    try:
        # Accept BOM-prefixed UTF-8 files produced by some shells/editors.
        payload = json.loads(path.read_text(encoding="utf-8-sig"))
    except Exception as exc:
        print(f"Error: Failed to parse JSON file {path}: {exc}")
        sys.exit(1)

    if not isinstance(payload, dict):
        payload = {"questions": payload}

    summary = _build_summary(payload, path=path, max_samples=max(0, args.max_samples))

    if args.json:
        print(json.dumps(summary, ensure_ascii=True, indent=2))
    else:
        _print_text_summary(summary)


if __name__ == "__main__":
    main()
