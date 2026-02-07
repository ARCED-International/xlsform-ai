#!/usr/bin/env python3
"""
Word Question Parser for XLSForm AI.

Extracts questions from Word (.docx) files and emits JSON.
Supports:
- paragraph-based questionnaires
- table-based questionnaires (e.g., Variable / Item / Response)
- mixed paragraph + table documents
- embedded images mapped to media::image for questions and choices

Usage:
  python parse_docx.py <file.docx>
  python parse_docx.py <file.docx> --media-dir media/forms --media-prefix media/forms
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Tuple

# Add scripts directory to Python path for sibling imports.
_scripts_dir = Path(__file__).parent.resolve()
if str(_scripts_dir) not in sys.path:
    sys.path.insert(0, str(_scripts_dir))

try:
    from docx import Document as _Document
    from docx.oxml.table import CT_Tbl
    from docx.oxml.text.paragraph import CT_P
    from docx.table import Table as _Table
    from docx.text.paragraph import Paragraph as _Paragraph
except ImportError:
    _Document = None
    CT_Tbl = None
    CT_P = None
    _Table = None
    _Paragraph = None


QUESTION_RE = re.compile(r"^\s*(?:Q(?:uestion)?\s*)?(\d+[A-Za-z]?)\s*[\.\):\-]\s*(.+)$")
CHOICE_RE = re.compile(r"^\s*(?:\(?[A-Za-z]\)|[A-Za-z][\.\)]|\(?\d+\)|\d+[\.\)]|[-*+])\s+(.+)$")
QUESTION_WORD_RE = re.compile(
    r"^(who|what|when|where|why|how|which|do|does|did|is|are|was|were|can|could|will|would)\b"
)
SPLIT_OPTIONS_RE = re.compile(r"\s*[;\|\n]\s*")
HEADER_QUESTION_TOKENS = ("question", "item", "prompt", "label")
HEADER_RESPONSE_TOKENS = ("response", "option", "choice", "answer")
HEADER_VARIABLE_TOKENS = ("variable", "var", "name", "code")
HEADER_TYPE_TOKENS = ("type", "question_type")


def _clean_text(value: str) -> str:
    return re.sub(r"\s+", " ", value or "").strip()


def _choice_value(label: str) -> str:
    value = re.sub(r"\s+", "_", label.strip().lower())
    value = re.sub(r"[^a-z0-9_]", "", value)
    return value[:48] or "option"


def _normalize_variable_name(raw_value: str) -> str:
    text = _clean_text(raw_value).lower()
    text = re.sub(r"[^a-z0-9_]", "_", text)
    text = re.sub(r"_+", "_", text).strip("_")
    if not text:
        return ""
    if text[0].isdigit():
        text = f"q_{text}"
    if text[-1].isdigit():
        text = f"{text}_field"
    return text[:64]


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


def _infer_non_select_type(question_text: str, response_hint: str = "") -> str:
    text = f"{question_text} {response_hint}".lower()
    if any(token in text for token in ["how old", "age", "how many", "count", "number of", "integer", "whole number"]):
        return "integer"
    if any(token in text for token in ["decimal", "percentage", "percent", "weight", "height", "amount", "price", "rate"]):
        return "decimal"
    if any(token in text for token in ["date", "when", "dd/mm", "mm/dd", "yyyy"]):
        return "date"
    if any(token in text for token in ["location", "gps", "coordinate"]):
        return "geopoint"
    return "text"


def _infer_select_mode(question_text: str, response_hint: str = "") -> str:
    text = f"{question_text} {response_hint}".lower()
    if any(token in text for token in ["select all", "all that apply", "multiple", "check all", "tick all"]):
        return "select_multiple"
    return "select_one"


def _parse_option_blob(raw_text: str) -> List[str]:
    text = _clean_text(raw_text)
    if not text:
        return []

    lowered = text.lower()
    if "yes/no" in lowered or "yes / no" in lowered:
        return ["Yes", "No"]

    tokens: List[str] = []
    if "\n" in raw_text:
        tokens = [_strip_choice_prefix(piece) for piece in raw_text.splitlines() if _clean_text(piece)]
    elif ";" in text or "|" in text:
        tokens = [_strip_choice_prefix(piece) for piece in SPLIT_OPTIONS_RE.split(raw_text) if _clean_text(piece)]
    elif text.count(",") >= 2:
        tokens = [_strip_choice_prefix(piece) for piece in raw_text.split(",") if _clean_text(piece)]
    elif CHOICE_RE.match(text):
        tokens = [_strip_choice_prefix(text)]

    cleaned: List[str] = []
    for token in tokens:
        candidate = _clean_text(token)
        if not candidate:
            continue
        if candidate.lower() in {"select one", "select all that apply", "response", "responses"}:
            continue
        cleaned.append(candidate)
    return cleaned


def _detect_header_index(row: List[str], tokens: Tuple[str, ...]) -> Optional[int]:
    for idx, value in enumerate(row):
        lowered = value.lower()
        if any(token in lowered for token in tokens):
            return idx
    return None


def _extract_relationship_ids(paragraph) -> List[str]:
    rid_values: List[str] = []
    if paragraph is None:
        return rid_values

    try:
        blips = paragraph._p.xpath(".//*[local-name()='blip']")
    except Exception:
        return rid_values

    for blip in blips:
        rid = ""
        for attr_name, attr_value in blip.attrib.items():
            if attr_name.endswith("}embed") or attr_name == "r:embed":
                rid = str(attr_value).strip()
                break
        if rid:
            rid_values.append(rid)
    return rid_values


def _guess_extension(image_part) -> str:
    filename = getattr(image_part, "filename", "") or ""
    suffix = Path(filename).suffix.lower()
    if suffix in {".png", ".jpg", ".jpeg", ".gif", ".bmp", ".tif", ".tiff", ".webp"}:
        return ".jpg" if suffix == ".jpeg" else suffix

    content_type = getattr(image_part, "content_type", "") or ""
    if "/" in content_type:
        guessed = content_type.split("/", 1)[1].lower().strip()
        if guessed == "jpeg":
            guessed = "jpg"
        guessed = guessed.replace("+xml", "").replace("svg+xml", "svg")
        if guessed:
            return f".{guessed}"

    return ".png"


@dataclass
class MediaContext:
    extract_images: bool
    media_dir: Optional[Path]
    media_prefix: str
    digest_to_ref: Dict[str, str] = field(default_factory=dict)
    saved_files: List[str] = field(default_factory=list)
    counter: int = 0

    def save_part(self, image_part) -> Optional[str]:
        if not self.extract_images or self.media_dir is None:
            return None

        blob = getattr(image_part, "blob", None)
        if not blob:
            return None

        digest = hashlib.sha1(blob).hexdigest()
        if digest in self.digest_to_ref:
            return self.digest_to_ref[digest]

        self.media_dir.mkdir(parents=True, exist_ok=True)

        ext = _guess_extension(image_part)
        self.counter += 1
        filename = f"img_{self.counter:04d}_{digest[:8]}{ext}"
        output_path = self.media_dir / filename
        output_path.write_bytes(blob)

        reference = filename
        if self.media_prefix:
            prefix = self.media_prefix.replace("\\", "/").strip().strip("/")
            if prefix:
                reference = f"{prefix}/{filename}"

        self.digest_to_ref[digest] = reference
        self.saved_files.append(str(output_path))
        return reference


def _extract_paragraph_media_refs(paragraph, media_context: MediaContext) -> List[str]:
    if not media_context.extract_images:
        return []

    references: List[str] = []
    rid_values = _extract_relationship_ids(paragraph)
    if not rid_values:
        return references

    related_parts = getattr(paragraph.part, "related_parts", {})
    for rid in rid_values:
        image_part = related_parts.get(rid)
        if image_part is None:
            continue
        reference = media_context.save_part(image_part)
        if reference and reference not in references:
            references.append(reference)
    return references


def _extract_cell_media_refs(cell, media_context: MediaContext) -> List[str]:
    references: List[str] = []
    for paragraph in cell.paragraphs:
        for ref in _extract_paragraph_media_refs(paragraph, media_context):
            if ref not in references:
                references.append(ref)
    return references


def _iter_doc_blocks(doc) -> Iterable[Tuple[str, object]]:
    if CT_P is None or CT_Tbl is None or _Paragraph is None or _Table is None:
        return []

    body = doc.element.body
    for child in body.iterchildren():
        if isinstance(child, CT_P):
            yield "paragraph", _Paragraph(child, doc)
        elif isinstance(child, CT_Tbl):
            yield "table", _Table(child, doc)


def _build_media_context(
    source_path: Path,
    media_dir: Optional[str | Path],
    media_prefix: Optional[str],
    extract_images: bool,
) -> MediaContext:
    if not extract_images:
        return MediaContext(extract_images=False, media_dir=None, media_prefix="")

    if media_dir is None:
        resolved_media_dir = Path.cwd() / "media" / source_path.stem
    else:
        resolved_media_dir = Path(media_dir).expanduser().resolve()

    prefix = media_prefix.strip() if media_prefix is not None else resolved_media_dir.name
    return MediaContext(
        extract_images=True,
        media_dir=resolved_media_dir,
        media_prefix=prefix,
    )


def extract_questions_from_docx(
    docx_path: str | Path,
    media_dir: Optional[str | Path] = None,
    media_prefix: Optional[str] = None,
    extract_images: bool = True,
    _media_context: Optional[MediaContext] = None,
) -> List[Dict[str, object]]:
    """Extract a list of question objects from a Word document."""
    if _Document is None:
        raise RuntimeError("python-docx is required. Install with: pip install python-docx")

    source_path = Path(docx_path).resolve()
    doc = _Document(str(source_path))
    media_context = _media_context or _build_media_context(source_path, media_dir, media_prefix, extract_images)

    questions: List[Dict[str, object]] = []
    current_question: Optional[Dict[str, object]] = None
    current_choices: List[Dict[str, object]] = []
    auto_question_number = 0

    def finalize_current_question() -> None:
        nonlocal current_question, current_choices
        if current_question is None:
            return

        question_text = str(current_question.get("text", ""))
        if current_choices:
            current_question["choices"] = current_choices
            if not str(current_question.get("type", "")).startswith("select_"):
                current_question["type"] = _infer_select_mode(question_text)
        else:
            current_question["choices"] = None
            if str(current_question.get("type", "")).startswith("select_"):
                current_question["type"] = _infer_non_select_type(question_text)

        if not current_question.get("name"):
            current_question.pop("name", None)
        if not current_question.get("media::image"):
            current_question.pop("media::image", None)

        questions.append(current_question)
        current_question = None
        current_choices = []

    def start_question(
        question_text: str,
        number: Optional[str] = None,
        variable_name: Optional[str] = None,
        image_refs: Optional[List[str]] = None,
    ) -> None:
        nonlocal auto_question_number, current_question, current_choices
        finalize_current_question()

        auto_question_number += 1
        normalized_text = _clean_text(question_text)
        if not normalized_text:
            normalized_text = f"Question {auto_question_number}"

        current_question = {
            "number": str(number or auto_question_number),
            "text": normalized_text,
            "type": "text",
            "choices": None,
        }
        current_choices = []

        normalized_name = _normalize_variable_name(variable_name or "")
        if normalized_name:
            current_question["name"] = normalized_name

        if image_refs:
            current_question["media::image"] = image_refs[0]

    def add_choice(label: str, image_ref: Optional[str] = None) -> None:
        nonlocal current_choices
        if current_question is None:
            return

        cleaned_label = _clean_text(label)
        if not cleaned_label:
            return

        choice: Dict[str, object] = {
            "value": _choice_value(cleaned_label),
            "label": cleaned_label,
        }
        if image_ref:
            choice["media::image"] = image_ref
        current_choices.append(choice)

    def apply_response_definition(response_text: str, response_images: Optional[List[str]] = None) -> None:
        if current_question is None:
            return

        raw_response = (response_text or "").strip()
        parsed_options = _parse_option_blob(raw_response)
        if parsed_options:
            current_question["type"] = _infer_select_mode(
                str(current_question.get("text", "")),
                raw_response,
            )
            for idx, label in enumerate(parsed_options):
                image_ref = None
                if response_images and idx < len(response_images):
                    image_ref = response_images[idx]
                add_choice(label, image_ref=image_ref)
            return

        lowered = raw_response.lower()
        if any(token in lowered for token in ["select one", "single choice", "choose one"]):
            current_question["type"] = "select_one"
            return
        if any(token in lowered for token in ["select all", "all that apply", "multiple choice", "choose all"]):
            current_question["type"] = "select_multiple"
            return
        if any(token in lowered for token in ["integer", "whole number", "numeric", "number"]):
            current_question["type"] = "integer"
            return
        if any(token in lowered for token in ["decimal", "percentage", "percent", "amount"]):
            current_question["type"] = "decimal"
            return
        if "date" in lowered:
            current_question["type"] = "date"
            return

        if response_images:
            if current_choices:
                for idx, image_ref in enumerate(response_images):
                    if idx < len(current_choices) and "media::image" not in current_choices[idx]:
                        current_choices[idx]["media::image"] = image_ref
            elif "media::image" not in current_question:
                current_question["media::image"] = response_images[0]

    def process_text_line(line_text: str, line_images: Optional[List[str]] = None) -> bool:
        nonlocal current_question
        normalized_line = _clean_text(line_text)
        if not normalized_line:
            return False

        question_match = QUESTION_RE.match(normalized_line)
        if question_match:
            start_question(
                question_text=question_match.group(2),
                number=question_match.group(1),
                image_refs=line_images,
            )
            return True

        if current_question is not None:
            choice_match = CHOICE_RE.match(normalized_line)
            if choice_match:
                add_choice(_strip_choice_prefix(normalized_line), image_ref=(line_images or [None])[0])
                return True

            split_options = _parse_option_blob(normalized_line)
            if len(split_options) >= 2:
                current_question["type"] = _infer_select_mode(str(current_question.get("text", "")), normalized_line)
                for idx, item in enumerate(split_options):
                    image_ref = None
                    if line_images and idx < len(line_images):
                        image_ref = line_images[idx]
                    add_choice(item, image_ref=image_ref)
                return True

            if not current_choices and not _looks_like_question(normalized_line):
                current_question["text"] = _clean_text(f"{current_question.get('text', '')} {normalized_line}")
                if line_images and "media::image" not in current_question:
                    current_question["media::image"] = line_images[0]
                return True

        if _looks_like_question(normalized_line):
            start_question(question_text=normalized_line, image_refs=line_images)
            return True

        return False

    def parse_structured_table(table) -> bool:
        rows: List[Dict[str, object]] = []
        for row in table.rows:
            row_texts: List[str] = []
            row_images: List[List[str]] = []
            for cell in row.cells:
                row_texts.append(_clean_text(cell.text))
                row_images.append(_extract_cell_media_refs(cell, media_context))
            rows.append({"texts": row_texts, "images": row_images})

        if not rows:
            return False

        header_row_index = None
        question_col = None
        response_col = None
        variable_col = None
        type_col = None

        for idx, row in enumerate(rows[:3]):
            cells = [str(item) for item in row["texts"]]
            maybe_question_col = _detect_header_index(cells, HEADER_QUESTION_TOKENS)
            if maybe_question_col is None:
                continue

            question_col = maybe_question_col
            response_col = _detect_header_index(cells, HEADER_RESPONSE_TOKENS)
            variable_col = _detect_header_index(cells, HEADER_VARIABLE_TOKENS)
            type_col = _detect_header_index(cells, HEADER_TYPE_TOKENS)
            header_row_index = idx
            break

        if header_row_index is None or question_col is None:
            return False

        for row in rows[header_row_index + 1 :]:
            texts = row["texts"]
            images = row["images"]

            if all(not _clean_text(str(text)) for text in texts) and all(not img for img in images):
                continue

            question_text = texts[question_col] if question_col < len(texts) else ""
            question_images = images[question_col] if question_col < len(images) else []
            response_text = texts[response_col] if response_col is not None and response_col < len(texts) else ""
            response_images = images[response_col] if response_col is not None and response_col < len(images) else []
            variable_name = texts[variable_col] if variable_col is not None and variable_col < len(texts) else ""
            explicit_type = texts[type_col] if type_col is not None and type_col < len(texts) else ""

            if question_text:
                parsed_question = QUESTION_RE.match(question_text)
                question_number = parsed_question.group(1) if parsed_question else None
                question_body = parsed_question.group(2) if parsed_question else question_text
                start_question(
                    question_text=question_body,
                    number=question_number,
                    variable_name=variable_name,
                    image_refs=question_images,
                )
                if explicit_type:
                    current_question["type"] = _clean_text(explicit_type).lower().replace(" ", "_")
                apply_response_definition(response_text, response_images=response_images)
                continue

            # Continuation rows for options or response details.
            continuation_text = response_text
            if not continuation_text:
                for col_idx, value in enumerate(texts):
                    if col_idx == question_col:
                        continue
                    if _clean_text(value):
                        continuation_text = value
                        if col_idx < len(images):
                            response_images = images[col_idx]
                        break

            if continuation_text and current_question is not None:
                apply_response_definition(continuation_text, response_images=response_images)
            elif response_images and current_question is not None:
                if current_choices:
                    if "media::image" not in current_choices[-1]:
                        current_choices[-1]["media::image"] = response_images[0]
                elif "media::image" not in current_question:
                    current_question["media::image"] = response_images[0]

        return True

    for block_type, block in _iter_doc_blocks(doc):
        if block_type == "paragraph":
            paragraph_text = block.text or ""
            paragraph_lines = [_clean_text(part) for part in paragraph_text.splitlines() if _clean_text(part)]
            paragraph_images = _extract_paragraph_media_refs(block, media_context)

            if not paragraph_lines:
                if paragraph_images and current_question is not None and "media::image" not in current_question:
                    current_question["media::image"] = paragraph_images[0]
                continue

            for line_index, line in enumerate(paragraph_lines):
                line_images = paragraph_images if line_index == 0 else None
                process_text_line(line, line_images=line_images)

            continue

        if block_type == "table":
            handled_structured = parse_structured_table(block)
            if handled_structured:
                continue

            # Fallback: parse table cell text in reading order for mixed/unstyled tables.
            for row in block.rows:
                for cell in row.cells:
                    cell_images = _extract_cell_media_refs(cell, media_context)
                    cell_lines = [_clean_text(part) for part in cell.text.splitlines() if _clean_text(part)]
                    if not cell_lines:
                        if cell_images and current_question is not None and "media::image" not in current_question:
                            current_question["media::image"] = cell_images[0]
                        continue

                    for idx, line in enumerate(cell_lines):
                        line_images = cell_images if idx == 0 else None
                        consumed = process_text_line(line, line_images=line_images)
                        if not consumed and line_images and current_question is not None:
                            if current_choices and "media::image" not in current_choices[-1]:
                                current_choices[-1]["media::image"] = line_images[0]
                            elif "media::image" not in current_question:
                                current_question["media::image"] = line_images[0]

    finalize_current_question()

    # Final cleanup: normalize types for question objects that have choices.
    for question in questions:
        choices = question.get("choices")
        text = str(question.get("text", ""))
        if choices:
            if not str(question.get("type", "")).startswith("select_"):
                question["type"] = _infer_select_mode(text)
        else:
            question["choices"] = None
            if str(question.get("type", "")).startswith("select_"):
                question["type"] = _infer_non_select_type(text)

    return questions


def extract_questions(
    docx_path: str | Path,
    pages: Optional[str] = None,
    media_dir: Optional[str | Path] = None,
    media_prefix: Optional[str] = None,
    extract_images: bool = True,
) -> List[Dict[str, object]]:
    """
    Compatibility alias used in older command protocols.
    `pages` is accepted for interface parity but ignored for DOCX.
    """
    _ = pages
    return extract_questions_from_docx(
        docx_path,
        media_dir=media_dir,
        media_prefix=media_prefix,
        extract_images=extract_images,
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Extract questions from Word document for XLSForm import")
    parser.add_argument("docx_file", help="Path to Word (.docx) file")
    parser.add_argument("--output", help="Output JSON file", default=None)
    parser.add_argument(
        "--media-dir",
        help="Directory to save extracted images (default: ./media/<docx_stem>)",
        default=None,
    )
    parser.add_argument(
        "--media-prefix",
        help="Prefix used in media::image values (default: media directory name)",
        default=None,
    )
    parser.add_argument(
        "--no-images",
        action="store_true",
        help="Disable image extraction",
    )

    args = parser.parse_args()
    source_path = Path(args.docx_file).resolve()
    if not source_path.exists():
        print(f"Error: File not found: {source_path}")
        sys.exit(1)

    if _Document is None:
        print("Error: python-docx is required. Install with: pip install python-docx")
        sys.exit(1)

    extract_images = not args.no_images
    media_context = _build_media_context(
        source_path=source_path,
        media_dir=args.media_dir,
        media_prefix=args.media_prefix,
        extract_images=extract_images,
    )

    print(f"Parsing {source_path}...")
    questions = extract_questions_from_docx(
        source_path,
        media_dir=media_context.media_dir,
        media_prefix=media_context.media_prefix,
        extract_images=extract_images,
        _media_context=media_context,
    )

    saved_files: List[str] = []
    media_dir_path: Optional[Path] = media_context.media_dir
    if extract_images:
        saved_files = [str(Path(path).resolve()) for path in media_context.saved_files]

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
            details=(
                f"Source: {source_path}\n"
                f"Questions: {question_summary}\n"
                f"Images exported: {len(saved_files)}"
            ),
        )
    except Exception:
        pass

    output = {
        "source": str(source_path),
        "count": len(questions),
        "questions": questions,
        "media": {
            "enabled": extract_images,
            "directory": str(media_dir_path) if media_dir_path else None,
            "prefix": media_context.media_prefix if extract_images else "",
            "saved_count": len(saved_files),
            "files": saved_files,
        },
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
