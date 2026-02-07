---
description: Import questions from external files (PDF, Word, Excel) into an XLSForm. Use this command to parse questionnaires, surveys, or forms and convert them to XLSForm format with intelligent question type detection.
arguments:
  - name: source
    description: Path to file containing questions (PDF, .docx, or .xlsx)
    required: true
  - name: pages
    description: Page range for PDF files (e.g., 1-10, 5-15)
    required: false
  - name: sheet
    description: Sheet name for Excel files
    required: false
---

# Import Questions from File

## Implementation Protocol

**CRITICAL: Follow this exact protocol when implementing this command:**

### 1. Use the Required Skills

```
/skill:xlsform-core
/skill:activity-logging
```

**Why these skills?**
- `xlsform-core` provides XLSForm syntax, question types, and best practices
- `activity-logging` ensures proper activity logging protocols

### Knowledge Base Reference

Consult these files for patterns and best practices before writing changes:
- `scripts/knowledge_base/data/use_cases.md`
- `scripts/knowledge_base/data/nested_repeats.md`

### XLSForm.org Rules Snapshot

- Columns can be in any order; optional columns can be omitted.
- Data after 20 adjacent blank rows or columns may be ignored.
- Survey requires type/name/label; choices requires list_name/name/label.
- Question names: start with letter/underscore; allowed letters, digits, hyphen, underscore, period.
- select_multiple choice names must not contain spaces.
- For cascading selects with duplicate choice names, set allow_choice_duplicates in settings.
- or_other only works without translations and without choice_filter; it uses English "Specify other".
- Settings sheet is optional but recommended; include form_title, form_id, version (yyyymmddrr).

### 2. Import from Scripts Directory

**CRITICAL: Always import from the `scripts/` directory:**

```python
import sys
from pathlib import Path
sys.path.insert(0, str(Path('scripts')))

from form_structure import FormStructure
from add_questions import add_questions
from log_activity import ActivityLogger
```

**NEVER import from other locations.**

**CRITICAL: Column Mapping Rule**

Never assume fixed column positions. Always read headers from row 1 and use `build_column_mapping()` before writing.

### 3. Log the Action

After successfully importing questions:

```python
from scripts.log_activity import ActivityLogger

logger = ActivityLogger()

# Determine action type based on file type
if file_ext == '.pdf':
    action_type = "import_pdf"
elif file_ext == '.docx':
    action_type = "import_docx"
elif file_ext == '.xlsx':
    action_type = "import_xlsx"

logger.log_action(
    action_type=action_type,
    description=f"Imported {count} questions from {file_type}",
    details=f"Source: {source_path}\nPages: {page_range}\nQuestions: {question_summary}"
)
```

### What NOT To Do

- **NEVER work directly without using skills**
- **NEVER import from other locations** (always use `scripts/`)
- **NEVER skip activity logging** for XLSForm modifications
- **NEVER modify the XLSForm without logging the action**

---

## Understanding Your Request

The user wants to import questions from an external file into their XLSForm.

**File types supported:**
- PDF (.pdf)
- Word (.docx)
- Excel (.xlsx)

## Load and Parse File

### 1. Identify File Type

Check the file extension and use the appropriate parser:

```bash
# PDF
python scripts/parse_pdf.py <source> --pages <range>

# Word
python scripts/parse_docx.py <source>

# Excel
python scripts/parse_xlsx.py <source> --sheet <sheet_name>
```

### 2. Execute Parser

Run the appropriate script and capture its output.

### Safe Execution (No temp files, no python -c)

- **Do NOT** create temporary scripts (e.g., `temp_import.py`)
- **Do NOT** use `python -c` (quote escaping is brittle)
- **Do** use heredocs / here-strings

**PowerShell:**
```powershell
@'
import openpyxl

wb = openpyxl.load_workbook("survey.xlsx")
ws = wb["survey"]
print(f"Total rows: {ws.max_row}")
wb.close()
'@ | python -
```

**bash/zsh:**
```bash
python - <<'PY'
import openpyxl

wb = openpyxl.load_workbook("survey.xlsx")
ws = wb["survey"]
print(f"Total rows: {ws.max_row}")
wb.close()
PY
```

### Cross-Platform Compatibility

When creating Python code for file parsing that runs on bash/PowerShell/Linux:

1. **Avoid Unicode characters** in print statements
   - Use ASCII: `SUCCESS` instead of checkmark symbols
   - Use ASCII: `ERROR` instead of X symbols

2. **Handle encoding explicitly** at script start
   ```python
   import sys
   if sys.platform == 'win32':
       sys.stdout.reconfigure(encoding='utf-8', errors='replace')
   ```

3. **Use proper file paths** for cross-platform compatibility
   - Use `pathlib.Path` instead of string paths
   - Use forward slashes or `os.path.join()`

4. **Always add the scripts path before importing helpers**
   ```python
   import sys
   from pathlib import Path

   scripts_dir = Path("scripts").resolve()
   if str(scripts_dir) not in sys.path:
       sys.path.insert(0, str(scripts_dir))
   ```

### Stop on Errors, Verify Before Logging

- If any exception occurs, stop immediately and fix the script.
- After saving, re-open the workbook and verify rows were written before logging.

## Question Type Detection

**Expected output format:** JSON with extracted question structure:

```json
{
  "questions": [
    {
      "number": "1",
      "text": "What is your name?",
      "type": "text",
      "choices": null,
      "constraint": null,
      "required": true
    },
    {
      "number": "2",
      "text": "What is your gender?",
      "type": "select_one",
      "choices": [
        {"value": "male", "label": "Male"},
        {"value": "female", "label": "Female"},
        {"value": "other", "label": "Other"}
      ],
      "constraint": null,
      "required": true
    },
    {
      "number": "3",
      "text": "How old are you?",
      "type": "integer",
      "choices": null,
      "constraint": "0-120",
      "required": true
    }
  ]
}
```

## Question Type Detection

The parser should intelligently detect question types:

### Detection Rules

| Pattern | Question Type | Example |
| --- | --- | --- |
| "select one", "choose", "radio button" | select_one | "Select your gender" |
| "select all that apply", "checkbox", "choose multiple" | select_multiple | "Select all that apply" |
| "yes/no", "true or false" | select_one yes_no | "Do you agree?" |
| "age", "how old", "years" | integer | "How old are you?" |
| "date", "when" | date | "Date of birth" |
| "name", "describe", "explain" | text | "What is your name?" |
| a), b), c) or 1., 2., 3. lists | select_one/select_multiple | Detect from options |
| "location", "GPS", "coordinates" | geopoint | "Record your location" |

### Choice Detection

Look for patterns like:
```
a) Option 1
b) Option 2
c) Option 3

Or:

1. Option 1
2. Option 2
3. Option 3

Or:

☐ Option 1
☐ Option 2
☐ Option 3
```

### Constraint Extraction

Look for constraint indicators:
- "age between 18-65" -> constraint: `. >= 18 and . <= 65`
- "must be positive" -> constraint: `. > 0`
- "0-100" -> constraint: `. >= 0 and . <= 100`

## Present Findings

Show the user what was found before adding:

```
# Import Results from questions.pdf

I found 15 questions on pages 1-5:

## Questions to Import

1. [text] What is your name?
2. [select_one: gender] What is your gender?
   Choices: Male, Female, Other
3. [integer] How old are you?
   Constraint: 0-120
4. [select_multiple: fruits] Select your favorite fruits:
   Choices: Apple, Banana, Orange, Other
5. [date] What is your date of birth?
... (10 more questions)

## Choice Lists to Create

- gender (3 choices)
- fruits (4 choices)

## Import Summary

- New questions: 15
- New choice lists: 2
- Questions with constraints: 3
- Estimated rows to add: 15 (survey) + 7 (choices) = 22 total

---

Do you want to import all questions, or would you like to:
- Select specific questions to import
- Modify question types
- Review and edit before importing
```

## Interactive Confirmation

Give the user options:

```
Import options:
1. Import all questions as-is
2. Select specific questions to import
3. Review and edit each question
4. Cancel import

Choose option (1-4):
```

### Option 2: Select Questions

```
Available questions:
[SUCCESS:] 1. What is your name? (text)
[SUCCESS:] 2. What is your gender? (select_one)
[ ] 3. How old are you? (integer) ← Skip
[SUCCESS:] 4. Select your favorite fruits (select_multiple)
...

Enter numbers to toggle selection, or 'all'/'none':
```

### Option 3: Review and Edit

For each question:
```
Question 1/15:

Type: [text]
Name: [q1_name]
Label: What is your name?
Required: [yes]

Accept (A), Edit (E), Skip (S), or Quit (Q)?
```

## Import Process

Once confirmed:

### 1. Generate Question Names

Create unique, descriptive names:
- "What is your name?" -> `respondent_name`
- "How old are you?" -> `age`
- "What is your gender?" -> `gender`

Check for duplicates and append numbers if needed.

### 2. Load Current Form

Read the existing XLSForm:
- Find last row in survey sheet
- Check existing choice lists
- Identify potential list reuse

### 3. Add to Survey Sheet

For each question:

**Basic question:**
```
Row N: text respondent_name "What is your name?"
```

**Select question:**
```
Row N: select_one gender gender "What is your gender?"
```

**With constraint:**
```
Row N: integer age "How old are you?" constraint=". >= 0 and . <= 120" constraint_message="Age must be 0-120"
```

**With required:**
```
Row N: text respondent_name "What is your name?" required="yes"
```

### 4. Add to Choices Sheet

For each select question:

**Check if list exists:**
- If yes: add to existing list
- If no: create new list

**Add choices:**
```
Row N: list_name=gender name=male label="Male"
Row N+1: list_name=gender name=female label="Female"
Row N+2: list_name=gender name=other label="Other"
```

### 5. Validate

After adding:
1. Check for duplicate names
2. Verify list_name consistency
3. Validate all constraints
4. Run `/xlsform-validate` to check for issues

## Special Cases

### PDF Page Ranges

```
User: /xlsform-import questionnaire.pdf --pages 1-10

Your response:
Parsing pages 1-10 of questionnaire.pdf...

[Proceed with import process]
```

### Excel Sheet Selection

```
User: /xlsform-import workbook.xlsx --sheet "Survey Questions"

Your response:
Reading sheet 'Survey Questions' from workbook.xlsx...

[Proceed with import process]
```

### Overwrite Detection

If questions with similar names exist:
```
WARNING:  Warning: Similar questions found in current form

Existing: q1_name "What is your name?"
Importing: respondent_name "What is your name?"

This may create duplicate content.

Options:
1. Skip duplicate questions
2. Rename imported questions
3. Import anyway (may cause duplicates)

Choose option:
```

### Merging Choice Lists

When importing choices that could reuse existing lists:

```
Detected potential choice list reuse:

Existing list 'yes_no' has choices: yes, no
Importing list 'yes_no' has choices: Yes, No

Options:
1. Reuse existing 'yes_no' list (recommended)
2. Create new list with different name
3. Merge choices

Recommendation: Reuse existing list for consistency
```

## Error Handling

### File Not Found
```
ERROR: Error: File 'questions.pdf' not found.

Please check:
- File path is correct
- File extension is .pdf, .docx, or .xlsx
- File is in the current directory or provide full path
```

### Unsupported File Type
```
ERROR: Error: Unsupported file type '.txt'

Supported formats:
- PDF (.pdf)
- Word (.docx)
- Excel (.xlsx)
```

### No Questions Found
```
WARNING:  Warning: No questions could be detected in the file.

This could be because:
- File format is not supported
- Questions are in an unusual format
- File is scanned images (needs OCR)

Try:
- Converting to a different format
- Using /xlsform-add to manually create questions
```

### Parser Script Failed
```
ERROR: Error: Failed to parse file

Parser output:
[error details from script]

Troubleshooting:
- Check file is not corrupted
- Ensure file has actual text (not scanned images)
- Try opening and re-saving the file
```

## After Import

Show summary:

```
# Import Complete!

Successfully imported 15 questions to survey.xlsx

Survey sheet:
  - Added 15 questions (rows 16-30)
  - Questions with constraints: 3
  - Questions marked as required: 12

Choices sheet:
  - Created 2 new choice lists
  - Added 7 choice options

Next steps:
1. Review the imported questions in Excel
2. Run /xlsform-validate to check for issues
3. Use /xlsform-add to add any missing questions
4. Use /xlsform-update to modify imported questions

Questions imported:
  SUCCESS: 1. respondent_name (text)
  SUCCESS: 2. gender (select_one)
  SUCCESS: 3. age (integer)
  SUCCESS: 4. favorite_fruits (select_multiple)
  ... (11 more)

Run /xlsform-validate now to check the form.
```

## Integration with Other Commands

- "Use /xlsform-validate to check imported questions"
- "Use /xlsform-update to modify question types or labels"
- "Use /xlsform-remove to delete any unwanted imports"
- "Use /xlsform-add to add additional questions manually"

## Best Practices for Import

1. **Always review** before confirming import
2. **Check for duplicates** in existing form
3. **Reuse choice lists** when possible (yes_no, gender, etc.)
4. **Validate after import** to catch any issues
5. **Preserve original file** for reference
