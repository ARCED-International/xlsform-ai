"""Add questions to XLSForm survey with best practices."""

import sys
import openpyxl
from pathlib import Path


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


def add_questions(questions_data, survey_file="survey.xlsx"):
    """Add questions to XLSForm with best practices.

    Args:
        questions_data: List of dicts with keys: type, name, label
        survey_file: Path to survey XLSForm file

    Returns:
        dict with success status and details
    """
    try:
        # Load workbook
        wb = openpyxl.load_workbook(survey_file)

        # Get survey sheet
        if "survey" not in wb.sheetnames:
            return {"success": False, "error": "'survey' sheet not found"}

        ws = wb["survey"]

        # Find header row
        header_row = None
        for row_idx in range(1, min(10, ws.max_row + 1)):
            cell_value = ws.cell(row_idx, 1).value
            if cell_value and str(cell_value).strip().lower() == "type":
                header_row = row_idx
                break

        if header_row is None:
            return {"success": False, "error": "Could not find header row with 'type' column"}

        # Find last data row
        last_row = ws.max_row
        for row_idx in range(ws.max_row, header_row, -1):
            if ws.cell(row_idx, 2).value:  # Check if 'name' column has value
                last_row = row_idx
                break

        # Add questions
        added = []
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

            # Insert row
            insert_row = last_row + 1

            # Set values using column mapping
            ws.cell(insert_row, COLUMNS["type"], q_type)
            ws.cell(insert_row, COLUMNS["name"], q_name)
            ws.cell(insert_row, COLUMNS["label"], q_label)

            if constraint:
                ws.cell(insert_row, COLUMNS["constraint"], constraint)
            if constraint_msg:
                ws.cell(insert_row, COLUMNS["constraint_message"], constraint_msg)
            if required:
                ws.cell(insert_row, COLUMNS["required"], required)
            if required_msg:
                ws.cell(insert_row, COLUMNS["required_message"], required_msg)

            added.append({
                "row": insert_row,
                "type": q_type,
                "name": q_name,
                "label": q_label,
                "required": required,
                "constraint": constraint
            })

            last_row = insert_row

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
    if len(sys.argv) < 2:
        print("Usage: python add_questions.py <question_data_json>")
        print("Example: python add_questions.py '{\"type\":\"text\",\"name\":\"first_name\",\"label\":\"First Name\"}'")
        sys.exit(1)

    import json

    # Parse question data from command line argument
    try:
        questions = json.loads(sys.argv[1])
        if not isinstance(questions, list):
            questions = [questions]

        result = add_questions(questions)

        if result["success"]:
            # Structured output
            print(f"SUCCESS: Added {result['total']} question(s)")
            for q in result["added"]:
                print(f"  Row {q['row']}: {q['type']} | {q['name']} | \"{q['label']}\"")
                if q['required']:
                    print(f"    Required: {q['required']}")
                if q['constraint']:
                    print(f"    Constraint: {q['constraint']}")
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
