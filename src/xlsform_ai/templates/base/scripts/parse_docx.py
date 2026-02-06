#!/usr/bin/env python3
"""
Word Question Parser for XLSForm AI

Extracts questions from Word (.docx) files and converts them to structured JSON format.
Usage: python parse_docx.py <file.docx>
"""

import sys
import json
import argparse
from pathlib import Path

try:
    from docx import Document
except ImportError:
    print("Error: python-docx is required. Install with: pip install python-docx")
    sys.exit(1)


def extract_questions_from_docx(docx_path):
    """Extract questions from Word document."""
    doc = Document(docx_path)
    questions = []

    current_question = None
    choice_list = []
    question_num = 0

    for para in doc.paragraphs:
        text = para.text.strip()
        if not text:
            continue

        # Detect numbered questions
        if text[0].isdigit() and (text[1] == '.' or text[1:3] == '. '):
            question_num += 1

            # Save previous question
            if current_question:
                if choice_list:
                    current_question['choices'] = choice_list
                questions.append(current_question)

            # Start new question
            question_text = text.split('.', 1)[1].strip()
            current_question = {
                'number': str(question_num),
                'text': question_text,
                'type': 'text',
                'choices': None
            }
            choice_list = []

        # Detect choice options
        elif text and text[0] in ('a', 'b', 'c', 'd', 'e', '•', '-'):
            if ')' in text:
                choice_text = text.split(')', 1)[1].strip()
            else:
                choice_text = text[1:].strip()

            choice_list.append({
                'value': choice_text.lower().replace(' ', '_'),
                'label': choice_text
            })

            if current_question and len(choice_list) > 1:
                current_question['type'] = 'select_multiple'

    # Save last question
    if current_question:
        if choice_list:
            current_question['choices'] = choice_list
        questions.append(current_question)

    return questions


def main():
    parser = argparse.ArgumentParser(
        description='Extract questions from Word document for XLSForm import'
    )
    parser.add_argument('docx_file', help='Path to Word (.docx) file')
    parser.add_argument('--output', help='Output JSON file', default=None)

    args = parser.parse_args()

    # Extract questions
    print(f"Parsing {args.docx_file}...")
    questions = extract_questions_from_docx(args.docx_file)

    # Log import activity
    try:
        from log_activity import ActivityLogger
        logger = ActivityLogger()
        question_summary = ", ".join([f"{q.get('text', 'Unknown')[:30]} ({q.get('type', 'unknown')})" for q in questions[:5]])
        if len(questions) > 5:
            question_summary += f"... and {len(questions) - 5} more"

        logger.log_action(
            action_type="import_docx",
            description=f"Imported {len(questions)} questions from Word document",
            details=f"Source: {args.docx_file}\nQuestions: {question_summary}"
        )
    except Exception:
        # Silently fail if logging is not available
        pass

    # Output
    output = {
        'source': args.docx_file,
        'count': len(questions),
        'questions': questions
    }

    json_output = json.dumps(output, indent=2)

    if args.output:
        with open(args.output, 'w') as f:
            f.write(json_output)
        print(f"Saved {len(questions)} questions to {args.output}")
    else:
        print(json_output)


if __name__ == '__main__':
    main()
