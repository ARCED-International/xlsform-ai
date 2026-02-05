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
    from form_structure import find_insertion_point, freeze_top_row, find_header_row, build_column_mapping
    FORM_STRUCTURE_AVAILABLE = True
except ImportError:
    FORM_STRUCTURE_AVAILABLE = False
    build_column_mapping = None

# Try to import display module, fail gracefully if not available
try:
    from display import print_questions_added
    DISPLAY_AVAILABLE = True
except ImportError:
    DISPLAY_AVAILABLE = False

# Try to import AI components, fail gracefully if not available
try:
    from knowledge_base.rag_engine import RAGEngine
    from question_type_analyzer import QuestionTypeAnalyzer
    from constraint_generator import SmartConstraintGenerator, Question
    from choice_optimizer import ChoiceListOptimizer
    from other_specify_handler import OtherSpecifyHandler, Question as OSQuestion
    AI_COMPONENTS_AVAILABLE = True
except ImportError:
    AI_COMPONENTS_AVAILABLE = False
    RAGEngine = None
    QuestionTypeAnalyzer = None
    SmartConstraintGenerator = None
    Question = None
    ChoiceListOptimizer = None
    OtherSpecifyHandler = None
    OSQuestion = None


# Column mapping for XLSForm survey sheet
# Note: Column numbers may vary based on your XLSForm template
COLUMNS = {
    "type": 1,
    "name": 2,
    "label": 3,
    "hint": 4,
    "required": 5,
    "calculation": 6,
    "relevant": 7,
    "constraint": 8,
    "constraint_message": 9,
    "required_message": 10,
    "appearance": 11,
    "default": 12,          # For default values in select/select_one
    "media::image": 13,     # For image filenames
    "media::audio": 14,     # For audio filenames
    "media::video": 15,     # For video filenames
}


def get_best_practices(question_type, question_name, question_label=""):
    """Apply best practices based on question type and name.

    Uses AI-powered SmartConstraintGenerator if available, otherwise
    falls back to rule-based logic.

    Args:
        question_type: XLSForm question type
        question_name: Question name/variable
        question_label: Question label text (for AI analysis)

    Returns:
        dict with constraint, constraint_message, required, required_message, appearance
    """
    # Use AI-powered constraint generator if available
    if AI_COMPONENTS_AVAILABLE and SmartConstraintGenerator:
        try:
            generator = SmartConstraintGenerator()
            question_obj = Question(question_type, question_name, question_label)
            constraints = generator.generate_constraints(question_obj)

            return {
                "constraint": constraints.constraint,
                "constraint_message": constraints.constraint_message,
                "required": constraints.required,
                "required_message": constraints.required_message,
                "appearance": constraints.appearance
            }
        except Exception as e:
            # Fall back to simple rules on error
            pass

    # Fallback to simple rule-based logic
    # Field types that should NOT be required (computed/read-only fields)
    non_input_types = {
        'calculate', 'hidden', 'note', 'imei', 'deviceid', 'subscriberid',
        'simserial', 'phonenumber', 'username', 'start', 'end', 'today',
        'audit', 'barcode', 'qrcode', 'image', 'audio', 'video', 'file'
    }

    is_non_input = question_type.lower() in non_input_types

    result = {
        "constraint": "",
        "constraint_message": "",
        "required": "" if is_non_input else "yes",
        "required_message": "" if is_non_input else "This field is required",
        "appearance": ""
    }

    # Name fields: no numbers, special chars
    if any(keyword in question_name.lower() for keyword in ["name", "first", "last", "full"]):
        result.update({
            "constraint": "regex(., '^[a-zA-Z\\\\s\\\\-\\\\\\\\.']$')",
            "constraint_message": "Please enter a valid name (letters only)",
            "required": "" if is_non_input else "yes",
            "required_message": "" if is_non_input else "Name is required"
        })

    # Age fields: reasonable range
    elif question_type == "integer" and "age" in question_name.lower():
        result.update({
            "constraint": ". >= 0 and . <= 130",
            "constraint_message": "Age must be between 0 and 130",
            "required": "" if is_non_input else "yes",
            "required_message": "" if is_non_input else "Age is required"
        })

    # Integer fields: non-negative by default
    elif question_type == "integer":
        result.update({
            "constraint": ". >= 0",
            "constraint_message": "Value must be zero or positive",
            "required": "" if is_non_input else "yes",
            "required_message": "" if is_non_input else "This field is required"
        })

    # Decimal fields: positive by default
    elif question_type == "decimal":
        result.update({
            "constraint": ". > 0",
            "constraint_message": "Value must be positive",
            "required": "" if is_non_input else "yes",
            "required_message": "" if is_non_input else "This field is required"
        })

    # Text fields: required by default (unless non-input type)
    elif question_type == "text":
        if not is_non_input:
            result.update({
                "required": "yes",
                "required_message": "This field is required"
            })

    # Select questions: always required (unless non-input type)
    elif question_type.startswith("select_"):
        if not is_non_input:
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

        # NEW: Build dynamic column mapping to fix wrong column bug
        try:
            if FORM_STRUCTURE_AVAILABLE and build_column_mapping:
                column_mapping = build_column_mapping(ws, header_row)
            else:
                # Fallback to COLUMNS dict
                column_mapping = COLUMNS
        except ValueError as e:
            return {"success": False, "error": str(e)}
        except Exception as e:
            # Fallback to COLUMNS dict on any error
            column_mapping = COLUMNS

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

            # Apply best practices (with AI enhancement if available)
            practices = get_best_practices(q_type, q_name, q_label)

            # NEW: Check for "Other" choice in select questions
            choices = q.get("choices", [])
            has_other = False
            other_choice_name = None

            if q_type.startswith("select_") and choices and AI_COMPONENTS_AVAILABLE and OtherSpecifyHandler:
                handler = OtherSpecifyHandler()
                if handler.detect_other_choice(choices):
                    has_other = True
                    # Find the "Other" choice name
                    for choice in choices:
                        choice_name = choice.get("name", "")
                        if choice_name == "-96" or "other" in str(choice.get("label", "")).lower():
                            other_choice_name = choice_name
                            break
                    if not other_choice_name:
                        other_choice_name = "-96"

            # Allow override if user specified constraints/required
            constraint = q.get("constraint", practices["constraint"])
            constraint_msg = q.get("constraint_message", practices["constraint_message"])
            required = q.get("required", practices["required"])
            required_msg = q.get("required_message", practices["required_message"])
            appearance = q.get("appearance", practices.get("appearance", ""))

            # Set core values using dynamic column mapping
            ws.cell(current_row, column_mapping["type"], q_type)
            ws.cell(current_row, column_mapping["name"], q_name)
            ws.cell(current_row, column_mapping["label"], q_label)

            # Set constraint fields only if columns exist
            if "constraint" in column_mapping and constraint:
                ws.cell(current_row, column_mapping["constraint"], constraint)
            if "constraint_message" in column_mapping and constraint_msg:
                ws.cell(current_row, column_mapping["constraint_message"], constraint_msg)
            if "required" in column_mapping and required:
                ws.cell(current_row, column_mapping["required"], required)
            if "required_message" in column_mapping and required_msg:
                ws.cell(current_row, column_mapping["required_message"], required_msg)
            if "appearance" in column_mapping and appearance and "appearance" not in q:
                ws.cell(current_row, column_mapping["appearance"], appearance)

            # Handle additional fields dynamically
            # This supports: hint, calculation, relevant, appearance, default, media::image, media::audio, media::video, etc.
            for key, value in q.items():
                if key not in ["type", "name", "label", "constraint", "constraint_message", "required", "required_message", "appearance"]:
                    # Use dynamic column mapping
                    if key in column_mapping:
                        ws.cell(current_row, column_mapping[key], value)
                    elif key == "hint" and "hint" in column_mapping:
                        ws.cell(current_row, column_mapping["hint"], value)
                    elif key == "calculation" and "calculation" in column_mapping:
                        ws.cell(current_row, column_mapping["calculation"], value)
                    elif key == "relevant" and "relevant" in column_mapping:
                        ws.cell(current_row, column_mapping["relevant"], value)
                    elif key == "default" and "default" in column_mapping:
                        ws.cell(current_row, column_mapping["default"], value)
                    elif key.startswith("media::"):
                        media_type = key.split("::")[1]  # e.g., "image" from "media::image"
                        media_column = f"media::{media_type}"
                        if media_column in column_mapping:
                            ws.cell(current_row, column_mapping[media_column], value)

            added.append({
                "row": current_row,
                "type": q_type,
                "name": q_name,
                "label": q_label,
                "required": required,
                "constraint": constraint
            })

            current_row += 1

            # NEW: Add "Other specify" follow-up if detected
            if has_other and other_choice_name:
                other_question_name = f"{q_name}_other"
                other_label = "Please specify (Other)"

                # Create the follow-up question
                ws.cell(current_row, column_mapping["type"], "text")
                ws.cell(current_row, column_mapping["name"], other_question_name)
                ws.cell(current_row, column_mapping["label"], other_label)

                # Add relevance to show only when "Other" selected
                if "relevant" in column_mapping:
                    relevance = f"${{{q_name}}} = '{other_choice_name}'"
                    ws.cell(current_row, column_mapping["relevant"], relevance)

                added.append({
                    "row": current_row,
                    "type": "text",
                    "name": other_question_name,
                    "label": other_label,
                    "note": "Auto-created 'Other specify' follow-up",
                    "parent": q_name
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
            # Use beautiful display if available
            if DISPLAY_AVAILABLE:
                print_questions_added(result['total'], result['added'])
            else:
                # Fallback to simple text output
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
