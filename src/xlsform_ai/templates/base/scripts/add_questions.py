"""Add questions to XLSForm survey with best practices."""

import sys
import openpyxl
from pathlib import Path

# Try to import logger, fail gracefully if not available
try:
    from log_activity import ActivityLogger
    LOGGING_AVAILABLE = True
except ImportError:
    LOGGING_AVAILABLE = False

# Try to import config, fail gracefully if not available
try:
    from config import ProjectConfig
    CONFIG_AVAILABLE = True
except ImportError:
    CONFIG_AVAILABLE = False

# Try to import form structure, fail gracefully if not available
try:
    from form_structure import find_insertion_point, freeze_top_row, find_header_row
    FORM_STRUCTURE_AVAILABLE = True
except ImportError:
    FORM_STRUCTURE_AVAILABLE = False


# Column mapping for XLSForm survey sheet
COLUMNS = {
    "type": 1,
    "name": 2,
    "label": 3,
    "hint": 4,
    "required": 5,
    "relevant": 6,
    "constraint": 9,
    "constraint_message": 10,
    "required_message": 11,
}


def get_best_practices(question_type, question_name):
    """Apply best practices based on question type and name.

    Args:
        question_type: XLSForm question type
        question_name: Question name/variable

    Returns:
        dict with constraint, constraint_message, required, required_message
    """
    result = {
        "constraint": "",
        "constraint_message": "",
        "required": "yes",
        "required_message": "This field is required"
    }

    # Name fields: no numbers, special chars
    if any(keyword in question_name.lower() for keyword in ["name", "first", "last", "full"]):
        result.update({
            "constraint": "regex(., '^[a-zA-Z\\\\s\\\\-\\\\\\\\.']$)",
            "constraint_message": "Please enter a valid name (letters only)",
            "required": "yes",
            "required_message": "Name is required"
        })

    # Age fields: reasonable range
    elif question_type == "integer" and "age" in question_name.lower():
        result.update({
            "constraint": ". >= 0 and . <= 130",
            "constraint_message": "Age must be between 0 and 130",
            "required": "yes",
            "required_message": "Age is required"
        })

    # Integer fields: non-negative by default
    elif question_type == "integer":
        result.update({
            "constraint": ". >= 0",
            "constraint_message": "Value must be zero or positive",
            "required": "yes",
            "required_message": "This field is required"
        })

    # Decimal fields: positive by default
    elif question_type == "decimal":
        result.update({
            "constraint": ". > 0",
            "constraint_message": "Value must be positive",
            "required": "yes",
            "required_message": "This field is required"
        })

    # Text fields: required by default
    elif question_type == "text":
        result.update({
            "required": "yes",
            "required_message": "This field is required"
        })

    # Select questions: always required
    elif question_type.startswith("select_"):
        result.update({
            "required": "yes",
            "required_message": "Please select an option"
        })

    return result


def add_questions(questions_data, survey_file=None):
    """Add questions to XLSForm with best practices.

    Args:
        questions_data: List of dicts with keys: type, name, label
        survey_file: Path to survey XLSForm file (optional, uses config if not specified)

    Returns:
        dict with success status and details
    """
    try:
        # Determine file to use
        if survey_file is None:
            if CONFIG_AVAILABLE:
                config = ProjectConfig()
                survey_file = config.get_full_xlsform_path()
            else:
                survey_file = Path("survey.xlsx")
        else:
            survey_file = Path(survey_file)

        # Load workbook
        wb = openpyxl.load_workbook(survey_file)

        # Get survey sheet
        if "survey" not in wb.sheetnames:
            return {"success": False, "error": "'survey' sheet not found"}

        ws = wb["survey"]

        # Find header row
        if FORM_STRUCTURE_AVAILABLE:
            header_row = find_header_row(ws)
        else:
            header_row = None
            for row_idx in range(1, min(10, ws.max_row + 1)):
                cell_value = ws.cell(row_idx, 1).value
                if cell_value and str(cell_value).strip().lower() == "type":
                    header_row = row_idx
                    break

        if header_row is None:
            return {"success": False, "error": "Could not find header row with 'type' column"}

        # Find insertion point using smart logic (or fallback to simple logic)
        if FORM_STRUCTURE_AVAILABLE:
            insertion_row = find_insertion_point(ws, header_row, questions_data)
        else:
            # Fallback: find last data row
            insertion_row = ws.max_row
            for row_idx in range(ws.max_row, header_row, -1):
                if ws.cell(row_idx, 2).value:  # Check if 'name' column has value
                    insertion_row = row_idx
                    break
            insertion_row += 1

        # Add questions
        added = []
        current_row = insertion_row
        for q in questions_data:
            q_type = q.get("type", "text")
            q_name = q.get("name", "")
            q_label = q.get("label", "")

            # Apply best practices
            practices = get_best_practices(q_type, q_name)

            # Allow override if user specified constraints/required
            constraint = q.get("constraint", practices["constraint"])
            constraint_msg = q.get("constraint_message", practices["constraint_message"])
            required = q.get("required", practices["required"])
            required_msg = q.get("required_message", practices["required_message"])

            # Set values using column mapping
            ws.cell(current_row, COLUMNS["type"], q_type)
            ws.cell(current_row, COLUMNS["name"], q_name)
            ws.cell(current_row, COLUMNS["label"], q_label)

            if constraint:
                ws.cell(current_row, COLUMNS["constraint"], constraint)
            if constraint_msg:
                ws.cell(current_row, COLUMNS["constraint_message"], constraint_msg)
            if required:
                ws.cell(current_row, COLUMNS["required"], required)
            if required_msg:
                ws.cell(current_row, COLUMNS["required_message"], required_msg)

            added.append({
                "row": current_row,
                "type": q_type,
                "name": q_name,
                "label": q_label,
                "required": required,
                "constraint": constraint
            })

            current_row += 1

        # Freeze the header row for better usability
        if FORM_STRUCTURE_AVAILABLE:
            try:
                freeze_top_row(ws, header_row)
            except Exception as e:
                # Fail gracefully if freeze panes doesn't work
                pass

        # Save workbook
        wb.save(survey_file)

        return {
            "success": True,
            "added": added,
            "total": len(added)
        }

    except Exception as e:
        return {"success": False, "error": str(e)}


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description='Add questions to XLSForm')
    parser.add_argument('questions', help='JSON string of questions to add')
    parser.add_argument('--file', '-f',
                       help='Override XLSForm file name (default: use config or survey.xlsx)')

    args = parser.parse_args()

    # Parse question data from command line argument
    import json
    try:
        questions = json.loads(args.questions)
        if not isinstance(questions, list):
            questions = [questions]

        result = add_questions(questions, survey_file=args.file)

        if result["success"]:
            # Structured output
            print(f"SUCCESS: Added {result['total']} question(s)")
            for q in result["added"]:
                print(f"  Row {q['row']}: {q['type']} | {q['name']} | \"{q['label']}\"")
                if q['required']:
                    print(f"    Required: {q['required']}")
                if q['constraint']:
                    print(f"    Constraint: {q['constraint']}")

            # Log activity
            if LOGGING_AVAILABLE:
                try:
                    logger = ActivityLogger()
                    questions_summary = ", ".join([f"{q['name']} ({q['type']})" for q in result["added"]])
                    logger.log_action(
                        action_type="add_questions",
                        description=f"Added {result['total']} question(s)",
                        details=f"Questions: {questions_summary}\nRows: {', '.join([str(q['row']) for q in result['added']])}",
                        author="Claude Code"
                    )
                    log_file = logger.log_file
                    print(f"\nActivity logged to: {log_file.name}")
                except Exception as e:
                    print(f"\nNote: Could not log activity: {e}")

            sys.exit(0)
        else:
            print(f"ERROR: {result['error']}")
            sys.exit(1)

    except json.JSONDecodeError:
        print("ERROR: Invalid JSON format for question data")
        sys.exit(1)
    except Exception as e:
        print(f"ERROR: {str(e)}")
        sys.exit(1)
