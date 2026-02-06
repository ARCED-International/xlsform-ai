#!/usr/bin/env python3
"""
PDF Question Parser for XLSForm AI

Extracts questions from PDF files and converts them to structured JSON format.
Usage: python parse_pdf.py <file.pdf> --pages 1-10
"""

import sys
import json
import argparse
from pathlib import Path

try:
    import pdfplumber
except ImportError:
    print("Error: pdfplumber is required. Install with: pip install pdfplumber")
    sys.exit(1)


def extract_text_from_pdf(pdf_path, page_range=None):
    """Extract text from PDF file."""
    questions = []

    with pdfplumber.open(pdf_path) as pdf:
        pages = pdf.pages

        # Apply page range if specified
        if page_range:
            start, end = page_range
            pages = pdf.pages[start-1:end]

        for page_num, page in enumerate(pages, start=1):
            text = page.extract_text()
            if text:
                # Parse questions from text
                page_questions = parse_questions_from_text(text, page_num)
                questions.extend(page_questions)

    return questions


def parse_questions_from_text(text, page_num):
    """
    Parse questions from extracted text.

    This is a simplified implementation. In production, you would use
    more sophisticated NLP or pattern matching.
    """
    questions = []
    lines = text.split('\n')

    current_question = None
    in_choices = False
    choice_list = []

    for line in lines:
        line = line.strip()
        if not line:
            continue

        # Detect question numbering (1., 2., etc.)
        if line[0].isdigit() and (line[1] == '.' or line[1:3] == '. '):
            # Save previous question
            if current_question:
                if choice_list:
                    current_question['choices'] = choice_list
                questions.append(current_question)

            # Start new question
            question_text = line.split('.', 1)[1].strip()
            current_question = {
                'number': line.split('.')[0],
                'text': question_text,
                'type': 'text',  # Default, will be refined
                'choices': None,
                'page': page_num
            }
            choice_list = []
            in_choices = False

        # Detect choice options (a), b), c) or bullets)
        elif line and line[0] in ('a', 'b', 'c', 'd', 'e', '•', '-'):
            choice_text = line.split(')', 1)[1].strip() if ')' in line else line[1:].strip()
            choice_list.append({
                'value': choice_text.lower().replace(' ', '_'),
                'label': choice_text
            })
            in_choices = True

            # If we have choices, mark as select type
            if current_question:
                if len(choice_list) > 1:
                    current_question['type'] = 'select_multiple'
                else:
                    current_question['type'] = 'select_one'

    # Don't forget the last question
    if current_question:
        if choice_list:
            current_question['choices'] = choice_list
        questions.append(current_question)

    return questions


def detect_question_types(questions):
    """Refine question types based on patterns."""
    type_keywords = {
        'integer': ['age', 'how many', 'how old', 'number of', 'count'],
        'decimal': ['weight', 'height', 'price', 'rate', 'percentage'],
        'date': ['date of birth', 'when', 'date'],
        'geopoint': ['location', 'gps', 'coordinates', 'where'],
        'select_one': ['which', 'select one', 'choose'],
        'select_multiple': ['select all', 'check all', 'multiple'],
    }

    for q in questions:
        text_lower = q['text'].lower()

        # Skip if already has choices (type detected from choices)
        if q.get('choices'):
            continue

        # Detect from keywords
        for q_type, keywords in type_keywords.items():
            if any(kw in text_lower for kw in keywords):
                q['type'] = q_type
                break


def main():
    parser = argparse.ArgumentParser(
        description='Extract questions from PDF file for XLSForm import'
    )
    parser.add_argument('pdf_file', help='Path to PDF file')
    parser.add_argument('--pages', help='Page range (e.g., 1-10)', default=None)
    parser.add_argument('--output', help='Output JSON file', default=None)

    args = parser.parse_args()

    # Parse page range
    page_range = None
    if args.pages:
        if '-' in args.pages:
            start, end = map(int, args.pages.split('-'))
            page_range = (start, end)
        else:
            page_range = (int(args.pages), int(args.pages))

    # Extract questions
    print(f"Parsing {args.pdf_file}...")
    questions = extract_text_from_pdf(args.pdf_file, page_range)

    # Refine question types
    detect_question_types(questions)

    # Log import activity
    try:
        from log_activity import ActivityLogger
        logger = ActivityLogger()
        question_summary = ", ".join([f"{q.get('text', 'Unknown')[:30]} ({q.get('type', 'unknown')})" for q in questions[:5]])
        if len(questions) > 5:
            question_summary += f"... and {len(questions) - 5} more"

        logger.log_action(
            action_type="import_pdf",
            description=f"Imported {len(questions)} questions from PDF",
            details=f"Source: {args.pdf_file}\nPages: {args.pages or 'all'}\nQuestions: {question_summary}"
        )
    except Exception:
        # Silently fail if logging is not available
        pass

    # Output
    output = {
        'source': args.pdf_file,
        'pages': args.pages,
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
