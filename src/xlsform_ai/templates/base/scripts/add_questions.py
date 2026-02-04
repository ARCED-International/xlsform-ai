"""Add questions to XLSForm survey."""

import sys
import openpyxl
from pathlib import Path


def add_questions(questions_data, survey_file="survey.xlsx"):
    """Add questions to XLSForm.

    Args:
        questions_data: List of dicts with keys: type, name, label
        survey_file: Path to survey XLSForm file

    Returns:
        True if successful
    """
    try:
        # Load workbook
        wb = openpyxl.load_workbook(survey_file)

        # Get survey sheet
        if "survey" not in wb.sheetnames:
            print("Error: 'survey' sheet not found in workbook")
            return False

        ws = wb["survey"]

        # Find first empty row
        max_row = ws.max_row

        # Check if we need to skip header rows
        # Find where actual data starts (look for 'type' in column 1)
        header_row = None
        for row_idx in range(1, min(10, max_row + 1)):
            cell_value = ws.cell(row_idx, 1).value
            if cell_value and str(cell_value).strip() == "type":
                header_row = row_idx
                break

        if header_row is None:
            # No header found, assume row 1 is header
            header_row = 1
            # Add header if missing
            if ws.cell(1, 1).value is None:
                headers = ["type", "name", "label", "constraint", "relevant",
                          "constraint_message", "required", "required_message"]
                for col_idx, header in enumerate(headers, 1):
                    ws.cell(1, col_idx, header)
                max_row = 1
            else:
                # Find actual last data row
                for row_idx in range(max_row, 0, -1):
                    if ws.cell(row_idx, 1).value:
                        max_row = row_idx
                        break

        # Add questions
        added_count = 0
        for q in questions_data:
            row_data = [
                q.get("type", "text"),
                q.get("name", ""),
                q.get("label", ""),
                q.get("constraint", ""),
                q.get("relevant", ""),
                q.get("constraint_message", ""),
                q.get("required", ""),
                q.get("required_message", "")
            ]
            ws.append(row_data)
            added_count += 1

        # Save workbook
        wb.save(survey_file)
        print(f"Successfully added {added_count} question(s)")
        return True

    except Exception as e:
        print(f"Error: {str(e)}")
        return False


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

        success = add_questions(questions)
        sys.exit(0 if success else 1)

    except json.JSONDecodeError:
        print("Error: Invalid JSON format for question data")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {str(e)}")
        sys.exit(1)
