---
description: Validate an XLSForm for errors, warnings, and best practices. Use this command to check for duplicate names, missing choice lists, invalid types, syntax errors, structural issues, and get suggestions for improvements.
arguments:
  - name: fix
    description: Automatically fix simple issues (optional)
    required: false
---

# Validate XLSForm

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

### 2. Import from Scripts Directory

**CRITICAL: Always import from the `scripts/` directory:**

```python
import sys
from pathlib import Path
sys.path.insert(0, str(Path('scripts')))

from validate_form import validate_form
from log_activity import ActivityLogger
```

**NEVER import from other locations.**

### 3. Log the Action

After completing validation:

```python
from scripts.log_activity import ActivityLogger

logger = ActivityLogger()
logger.log_action(
    action_type="validate",
    description=f"Form validation {'passed' if is_valid else 'failed'}",
    details=f"Errors: {error_count}\nWarnings: {warning_count}\nSuggestions: {suggestion_count}"
)
```

### What NOT To Do

- **NEVER work directly without using skills**
- **NEVER import from other locations** (always use `scripts/`)
- **NEVER skip activity logging** for XLSForm modifications

---

## Understanding the Request

The user wants to validate their XLSForm to ensure:
- No critical errors that prevent conversion
- No warnings that might cause issues
- Following best practices

## Load the Form

1. **Identify the file:**
   - Default: `survey.xlsx` in current directory
   - Or use specified file path

2. **Read all sheets:**
   - survey sheet
   - choices sheet
   - settings sheet (optional)

3. **Check file accessibility:**
   - If file is open in Excel, note it (might see live changes)
   - Use openpyxl for closed files
   - Use xlwings if file is open and changes need to be made

### Safe Execution (No temp files, no python -c)

- **Do NOT** create temporary scripts (e.g., `temp_validate.py`)
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

When creating Python code for validation that runs on bash/PowerShell/Linux:

1. **Avoid Unicode characters** in print statements
   - Use ASCII: `SUCCESS` instead of checkmark symbols
   - Use ASCII: `ERROR` instead of X symbols
   - Use ASCII: `INFO` for suggestion hints

2. **Handle encoding explicitly** at script start
   ```python
   import sys
   if sys.platform == 'win32':
       sys.stdout.reconfigure(encoding='utf-8', errors='replace')
   ```

3. **Escape quotes properly** for bash
   - Use double quotes outside: `"..."`
   - Escape inner quotes: `'...\'...'`
   - Or use raw strings: `r"..."`

## Validation Checks

Perform these checks systematically:

### 1. Critical Errors

These MUST be fixed for the form to work:

#### A. Duplicate Question Names
```python
# Check survey sheet 'name' column for duplicates
# Report: Row numbers and duplicate names
# Severity: ERROR
```

Example output:
```
ERROR: ERROR: Duplicate question names found
  - Row 5, Row 23: name = 'age'
  - Row 12, Row 34: name = 'location'

Impact: These names must be unique. Duplicates will cause form conversion to fail.
Fix: Rename the duplicates (e.g., age -> age_2, location -> household_location)
```

#### B. Duplicate Choice Names in Same List
```python
# Check choices sheet for duplicate name values within same list_name
# Report: list_name and duplicate choice names
# Severity: ERROR
```

Example output:
```
ERROR: ERROR: Duplicate choice names in same list
  - List 'gender': Row 3, Row 7 both have name = 'male'

Impact: Duplicate choices are indistinguishable in data export.
Fix: Rename one of the duplicates
```

#### C. Missing Choice Lists
```python
# For each select_one/select_multiple, verify list_name exists in choices
# Report: Question row and missing list_name
# Severity: ERROR
```

Example output:
```
ERROR: ERROR: Referenced choice lists don't exist
  - Row 15: select_one fruits (list 'fruits' not found in choices sheet)
  - Row 28: select_multiple colors (list 'colors' not found)

Impact: These questions will have no options to select.
Fix: Create the missing choice lists or fix the list_name typo
```

#### D. Invalid Question Types
```python
# Check all type values against valid XLSForm types
# Report: Invalid types and row numbers
# Severity: ERROR
```

Example output:
```
ERROR: ERROR: Invalid question types
  - Row 8: 'selct_one' (did you mean 'select_one'?)
  - Row 19: 'interger' (did you mean 'integer'?)

Impact: Form conversion will fail with unknown types.
Fix: Correct the typos in the type column
```

#### E. Invalid Name Syntax
```python
# Check name column starts with letter/underscore
# Check for invalid characters
# Severity: ERROR
```

Example output:
```
ERROR: ERROR: Invalid question names
  - Row 3: '1st_question' (starts with digit)
  - Row 10: 'respondent name' (contains space)

Impact: Invalid names will cause conversion errors.
Fix: Use 'first_question' and 'respondent_name' instead
```

#### F. Unbalanced Groups/Repeats
```python
# Count begin_group vs end_group
# Count begin_repeat vs end_repeat
# Check proper nesting
# Severity: ERROR
```

Example output:
```
ERROR: ERROR: Unbalanced structures
  - begin_group at Row 5 missing matching end_group
  - begin_repeat at Row 15 missing matching end_repeat

Impact: Form structure is invalid.
Fix: Add the missing end_group and end_repeat rows
```

#### G. Spaces in select_multiple Choice Names
```python
# For select_multiple questions, check choice names for spaces
# Severity: ERROR
```

Example output:
```
ERROR: ERROR: Spaces in select_multiple choice names
  - List 'toppings' has choice 'choice 1' (contains space)

Impact: Selected values will be corrupted (space-separated).
Fix: Use 'choice_1' instead
```

### 2. Warnings

These SHOULD be fixed to avoid issues:

#### A. Missing Constraint Messages
```python
# Check for constraints without constraint_message
# Severity: WARNING
```

Example output:
```
WARNING:  WARNING: Constraints without error messages
  - Row 12: constraint '. >= 18' has no constraint_message

Impact: Users won't know why their input was rejected.
Recommendation: Add "Must be 18 or older" as constraint_message
```

#### B. Missing Required Messages
```python
# Check for required=yes without required_message
# Severity: WARNING
```

#### C. Labels Missing for begin group
```python
# Check for begin_group without labels
# Severity: WARNING
```

Example output:
```
WARNING:  WARNING: begin group without label
  - Row 8: begin_group demographics has empty label

Impact: Users won't see a group header.
Recommendation: Add a descriptive label like "Demographic Information"
```

#### D. Suspicious Formulas
```python
# Check for common formula errors
# - Missing ${} in relevant/constraint
# - Wrong syntax in calculations
# Severity: WARNING
```

Example output:
```
WARNING:  WARNING: Possible formula syntax errors
  - Row 14: relevant 'age >= 18' (missing ${}, should be '${age} >= 18')
  - Row 20: calculation 'price * 0.18' (missing ${}, should be '${price} * 0.18')
```

### 3. Suggestions

Best practice improvements:

#### A. Naming Conventions
```
INFO: SUGGESTION: Use snake_case for question names
  - Row 5: 'RespondentName' -> consider 'respondent_name'
  - Row 12: 'Household Size' -> consider 'household_size'

Benefits: Consistent, easier to work with, follows conventions
```

#### B. Reusable Choice Lists
```
INFO: SUGGESTION: Reuse existing choice lists
  - You have 3 questions using identical 'yes_no' choices
  - Consider creating a single 'yes_no' list and reusing it

Benefits: Easier to maintain, consistent data
```

#### C. Helpful Hints
```
INFO: SUGGESTION: Add hint text for complex questions
  - Row 25: Complex calculation question could use a hint

Example hint: "This will be calculated automatically from previous answers"
```

## Validation Report

Present results in this format:

```
# XLSForm Validation Report

File: survey.xlsx
Last modified: [timestamp]

## Summary
ERROR: 3 Critical Errors
WARNING:  5 Warnings
INFO: 2 Suggestions

## Critical Errors (Must Fix)

[List all errors as shown above]

## Warnings (Recommended Fixes)

[List all warnings as shown above]

## Suggestions (Best Practices)

[List all suggestions as shown above]

---

## Next Steps

1. Fix all critical errors first
2. Address warnings to improve user experience
3. Consider implementing suggestions for best practices

Run this validation again after making changes to verify fixes.
```

## Auto-Fix Mode

When user provides `--fix` flag or asks to fix issues:

1. **Fix only safe, unambiguous issues:**
   - Correct obvious typos in type (selct_one -> select_one)
   - Add missing constraint_message with generic text
   - Remove duplicate columns

2. **Ask for confirmation on ambiguous fixes:**
   - Duplicate names: suggest alternatives
   - Invalid names: ask what to use
   - Missing choice lists: ask to create or fix typo

3. **Don't auto-fix:**
   - Relevance/constraint formulas (too complex)
   - Group/repeat structure (needs manual review)
   - Choice list decisions (needs user input)

## Example Usage

```
User: /xlsform-validate

Your response:
# XLSForm Validation Report

File: survey.xlsx
SUCCESS: All checks passed! No errors found.

Your form is ready for use. Consider running validation again after making changes.

---

User: /xlsform-validate

Your response:
# XLSForm Validation Report

File: survey.xlsx

ERROR: 2 Critical Errors
WARNING:  1 Warning

## Critical Errors

ERROR: ERROR: Duplicate question names
  - Row 8, Row 25: name = 'age'

Fix options:
1. Rename row 25 to 'age_follow_up'
2. Rename row 8 to 'initial_age'
3. Enter custom name

Which would you like?

ERROR: ERROR: Missing choice list
  - Row 15: select_one fruits (list 'fruits' not found)

Fix options:
1. Create 'fruits' choice list now
2. Fix typo (did you mean 'fruit'?)
3. I'll fix it manually

## Warnings

WARNING:  WARNING: Constraint without message
  - Row 12: constraint '. >= 18' needs constraint_message

Recommendation: Add "Age must be 18 or older"

---

Run /xlsform-validate --fix to automatically fix safe issues.
```

## Special Cases

### Multiple Files
```
User: /xlsform-validate survey.xlsx backup_survey.xlsx

Your response:
Validating 2 files...

## File 1: survey.xlsx
ERROR: 1 Error
WARNING:  2 Warnings

[details...]

## File 2: backup_survey.xlsx
SUCCESS: All checks passed!

[details...]
```

### Specific Sheet Only
```
User: /xlsform-validate --sheet choices

Your response:
Validating choices sheet only...

SUCCESS: Choice sheet is valid:
  - 5 choice lists
  - 47 total choices
  - No duplicate names within lists
  - All list_names are referenced in survey
```

## After Validation

Always end with:

1. **If errors found:** Provide clear next steps to fix them
2. **If warnings found:** Explain impact and recommend fixes
3. **If all clear:** Confirm form is ready to use/test
4. **Suggest:** Run validation again after making changes

## Integration with Other Commands

Mention related commands:

- "After fixing validation errors, use /xlsform-add to add missing questions"
- "Use /xlsform-update to fix invalid types"
- "Use /xlsform-remove to delete duplicate questions"
