"""Add questions to XLSForm survey with best practices."""

import sys
import openpyxl
from pathlib import Path

# Ensure UTF-8 encoding for Windows console output
if sys.platform == 'win32':
    import locale
    import codecs
    # Try to set stdout/stderr encoding to UTF-8
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')
    except AttributeError:
        # Python < 3.7 doesn't have reconfigure, use environment variable approach
        import os
        os.environ['PYTHONIOENCODING'] = 'utf-8'

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

        # Build dynamic column mapping from actual header row
        # This maps column names to their actual positions (e.g., {"type": 1, "name": 3})
        if FORM_STRUCTURE_AVAILABLE:
            column_map = build_column_mapping(ws, header_row)
        else:
            # Fallback: assume standard column positions
            column_map = {
                "type": 1, "name": 2, "label": 3, "hint": 4, "required": 5,
                "calculation": 6, "relevant": 7, "constraint": 8,
                "constraint_message": 9, "required_message": 10, "appearance": 11,
                "default": 12, "media::image": 13, "media::audio": 14, "media::video": 15
            }

        # Validate required columns exist
        required_columns = ["type", "name", "label"]
        missing_columns = [col for col in required_columns if col not in column_map]
        if missing_columns:
            return {"success": False, "error": f"Missing required columns in header row: {', '.join(missing_columns)}"}

        # Check for duplicate question names (prevent adding existing questions)
        name_col = column_map.get("name", 2)
        existing_names = set()
        for row_idx in range(header_row + 1, ws.max_row + 1):
            name_val = ws.cell(row_idx, name_col).value
            if name_val:
                existing_names.add(str(name_val).strip())

        # Filter out questions that already exist
        duplicates = []
        filtered_questions = []
        for q in questions_data:
            q_name = q.get("name", "")
            if q_name in existing_names:
                duplicates.append(q_name)
            else:
                filtered_questions.append(q)

        if duplicates:
            print(f"Note: Skipping {len(duplicates)} question(s) that already exist: {', '.join(duplicates)}")

        if not filtered_questions:
            return {
                "success": True,
                "added": [],
                "total": 0,
                "skipped": duplicates,
                "message": "All questions already exist in the form"
            }

        # Use filtered list for actual addition
        questions_data = filtered_questions

        # Find insertion point using smart logic (or fallback to simple logic)
        if FORM_STRUCTURE_AVAILABLE:
            insertion_row = find_insertion_point(ws, header_row, questions_data, column_map)
        else:
            # Fallback: find last data row
            insertion_row = ws.max_row
            name_col = column_map.get("name", 2)  # Use dynamic mapping or fallback to column 2
            for row_idx in range(ws.max_row, header_row, -1):
                if ws.cell(row_idx, name_col).value:  # Check if 'name' column has value
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

            # Allow override if user specified constraints/required
            constraint = q.get("constraint", practices["constraint"])
            constraint_msg = q.get("constraint_message", practices["constraint_message"])
            required = q.get("required", practices["required"])
            required_msg = q.get("required_message", practices["required_message"])
            appearance = q.get("appearance", practices.get("appearance", ""))

            # Set core values (required columns always exist due to validation above)
            ws.cell(current_row, column_map["type"], q_type)
            ws.cell(current_row, column_map["name"], q_name)
            ws.cell(current_row, column_map["label"], q_label)

            # Set constraint fields (optional - check if column exists)
            if constraint and "constraint" in column_map:
                ws.cell(current_row, column_map["constraint"], constraint)
            if constraint_msg and "constraint_message" in column_map:
                ws.cell(current_row, column_map["constraint_message"], constraint_msg)
            if required and "required" in column_map:
                ws.cell(current_row, column_map["required"], required)
            if required_msg and "required_message" in column_map:
                ws.cell(current_row, column_map["required_message"], required_msg)
            # Set appearance from best practices if not overridden by user
            if appearance and "appearance" not in q and "appearance" in column_map:
                ws.cell(current_row, column_map["appearance"], appearance)

            # Handle additional fields dynamically from question data
            # This supports: hint, calculation, relevant, appearance, default, media::image, media::audio, media::video, etc.
            for key, value in q.items():
                if key not in ["type", "name", "label", "constraint", "constraint_message", "required", "required_message"]:
                    # Normalize key to lowercase for case-insensitive matching
                    key_lower = key.lower()
                    # Check if we have a column mapping for this key
                    if key_lower in column_map:
                        ws.cell(current_row, column_map[key_lower], value)

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
            if LOGGING_AVAILABLE and CONFIG_AVAILABLE:
                try:
                    # Check if activity logging is enabled in config
                    config = ProjectConfig()
                    if config.is_activity_logging_enabled():
                        logger = ActivityLogger()
                        questions_summary = ", ".join([f"{q['name']} ({q['type']})" for q in result["added"]])
                        logger.log_action(
                            action_type="add_questions",
                            description=f"Added {result['total']} question(s)",
                            details=f"Questions: {questions_summary}\nRows: {', '.join([str(q['row']) for q in result['added']])}"
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
