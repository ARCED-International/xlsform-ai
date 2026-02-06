#!/usr/bin/env python3
"""
XLSForm Validator

Validates XLSForm structure and syntax.
Usage: python validate_form.py <survey.xlsx>
"""

import sys
import argparse
from pathlib import Path

# Ensure UTF-8 encoding for Windows console output
if sys.platform == 'win32':
    # Try to set stdout/stderr encoding to UTF-8
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')
    except AttributeError:
        # Python < 3.7 doesn't have reconfigure
        pass

# CRITICAL: Add scripts directory to Python path for sibling imports
# This allows the script to find sibling modules whether run from project root or scripts dir
_scripts_dir = Path(__file__).parent.resolve()
if str(_scripts_dir) not in sys.path:
    sys.path.insert(0, str(_scripts_dir))

try:
    import openpyxl
except ImportError:
    print("Error: openpyxl is required. Install with: pip install openpyxl")
    sys.exit(1)

# Try to import display module, fail gracefully if not available
try:
    from display import print_validation_results
    DISPLAY_AVAILABLE = True
except ImportError:
    DISPLAY_AVAILABLE = False


def validate_xlsxform(xlsx_path):
    """Validate XLSForm Excel file."""
    errors = []
    warnings = []
    suggestions = []

    try:
        wb = openpyxl.load_workbook(xlsx_path)

        # Check for required sheets
        if 'survey' not in wb.sheetnames:
            errors.append("Missing required sheet: 'survey'")
        if 'choices' not in wb.sheetnames:
            warnings.append("Missing optional sheet: 'choices'")

        # Validate survey sheet
        if 'survey' in wb.sheetnames:
            survey = wb['survey']
            survey_errors, survey_warnings = validate_survey_sheet(survey)
            errors.extend(survey_errors)
            warnings.extend(survey_warnings)

        # Validate choices sheet
        if 'choices' in wb.sheetnames:
            choices = wb['choices']
            choices_errors = validate_choices_sheet(choices)
            errors.extend(choices_errors)

    except Exception as e:
        errors.append(f"Failed to load workbook: {str(e)}")

    return errors, warnings, suggestions


def validate_survey_sheet(sheet):
    """Validate survey sheet structure."""
    errors = []
    warnings = []

    # Get headers
    headers = [cell.value for cell in sheet[1]]
    headers = [h for h in headers if h]

    # Check required columns
    required = ['type', 'name', 'label']
    for col in required:
        if col not in headers:
            errors.append(f"Missing required column in survey sheet: '{col}'")

    # Check for duplicate names
    if 'name' in headers:
        name_col = headers.index('name')
        names = {}
        for row_idx, row in enumerate(sheet.iter_rows(min_row=2, values_only=True), start=2):
            if row[name_col]:
                name = row[name_col]
                if name in names:
                    errors.append(f"Duplicate question name '{name}' at rows {names[name]} and {row_idx}")
                else:
                    names[name] = row_idx

    return errors, warnings


def validate_choices_sheet(sheet):
    """Validate choices sheet structure."""
    errors = []

    # Get headers
    headers = [cell.value for cell in sheet[1]]
    headers = [h for h in headers if h]

    # Check required columns
    required = ['list_name', 'name', 'label']
    for col in required:
        if col not in headers:
            errors.append(f"Missing required column in choices sheet: '{col}'")

    # Check for duplicate names within same list
    if 'list_name' in headers and 'name' in headers:
        list_name_col = headers.index('list_name')
        name_col = headers.index('name')

        choice_names = {}
        for row in sheet.iter_rows(min_row=2, values_only=True):
            if row[list_name_col] and row[name_col]:
                list_name = row[list_name_col]
                name = row[name_col]

                if list_name not in choice_names:
                    choice_names[list_name] = set()

                if name in choice_names[list_name]:
                    errors.append(f"Duplicate choice name '{name}' in list '{list_name}'")
                else:
                    choice_names[list_name].add(name)

    return errors


def main():
    parser = argparse.ArgumentParser(
        description='Validate XLSForm Excel file'
    )
    parser.add_argument('xlsx_file', help='Path to XLSForm Excel file')

    args = parser.parse_args()

    # Validate
    print(f"Validating {args.xlsx_file}...\n")
    errors, warnings, suggestions = validate_xlsxform(args.xlsx_file)

    # Build results dict
    results = {
        "valid": len(errors) == 0,
        "errors": errors,
        "warnings": warnings
    }

    # Log validation activity
    try:
        from log_activity import ActivityLogger
        logger = ActivityLogger()
        logger.log_action(
            action_type="validate",
            description=f"Form validation {'passed' if results['valid'] else 'failed'}",
            details=f"Errors: {len(errors)}\nWarnings: {len(warnings)}\nSuggestions: {len(suggestions)}"
        )
    except Exception:
        # Silently fail if logging is not available
        pass

    # Use beautiful display if available
    if DISPLAY_AVAILABLE:
        print_validation_results(results)
    else:
        # Fallback to simple text output
        print(f"# Validation Report\n")

        if errors:
            print(f"❌ {len(errors)} Critical Error(s):\n")
            for error in errors:
                print(f"  - {error}")
            print()

        if warnings:
            print(f"⚠️  {len(warnings)} Warning(s):\n")
            for warning in warnings:
                print(f"  - {warning}")
            print()

        if not errors and not warnings:
            print("✓ All checks passed! No errors found.\n")

    # Exit code
    sys.exit(1 if errors else 0)


if __name__ == '__main__':
    main()
