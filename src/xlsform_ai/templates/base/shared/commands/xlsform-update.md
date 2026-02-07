---
description: Update existing XLSForm questions. Use this to modify question types, labels, constraints, relevance, required status, or other properties of questions that already exist in your form.
arguments:
  - name: question
    description: Name or identifier of the question to update
    required: true
  - name: changes
    description: What to change (type, label, constraint, relevance, required, etc.)
    required: true
---

# Update XLSForm Question

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

from form_structure import FormStructure
from log_activity import ActivityLogger
```

**NEVER import from other locations.**

### 3. Log the Action

After successfully updating the question:

```python
from scripts.log_activity import ActivityLogger

logger = ActivityLogger()
logger.log_action(
    action_type="update_questions",
    description=f"Updated question: {question_name}",
    details=f"Question: {question_name}\nChanges: {changes_summary}\nRow: {row_number}"
)
```

### What NOT To Do

- **NEVER work directly without using skills**
- **NEVER import from other locations** (always use `scripts/`)
- **NEVER skip activity logging** for XLSForm modifications

---

## Key Principles

1. **Identify the question**: Find by name or description
2. **Understand the change**: What property to modify (type, label, constraint, etc.)
3. **Preserve data**: Don't break existing data relationships
4. **Log activity**: All updates are logged to activity log

## Understanding Your Request

Identify what's being updated:

1. **Change type**: "Update age question from text to integer"
2. **Add constraint**: "Update age to add constraint (0-120)"
3. **Modify label**: "Update the name question label to be more specific"
4. **Add relevance**: "Update occupation question to only show if age >= 18"
5. **Make required**: "Update email question to be required"

## Current Form Structure

1. Read the survey.xlsx file
2. Locate the target question by name
3. Show current properties
4. Confirm the change

### Safe Execution (No temp files, no python -c)

- **Do NOT** create temporary scripts (e.g., `temp_update.py`)
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

When creating Python code for updates that runs on bash/PowerShell/Linux:

1. **Avoid Unicode characters** in print statements
   - Use ASCII: `SUCCESS` instead of checkmark symbols
   - Use ASCII: `ERROR` instead of X symbols

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

## Proposed Changes

Present what will change:

```
Updating: first_name

Current:
  type: text
  label: First Name
  required: no
  constraint: none

Changes to:
  type: text
  label: Respondent First Name
  required: yes
  constraint: regex(., '^[a-zA-Z\s\-\.']$')
```

## Validation

Before updating, verify:

- [ ] Question name exists in the form
- [ ] New type is valid (if changing type)
- [ ] New constraint syntax is correct
- [ ] Relevance formula references valid fields
- [ ] Label is not empty

## Implementation

### Use openpyxl to update the question

**Find the question row:**
```python
# Search for question by name in column 2 (name column)
# Get the row number
```

**Update the cells:**
```python
# Update specific columns based on what's changing
# type: column 1
# name: column 2
# label: column 3
# required: column 5
# constraint: column 9
# constraint_message: column 10
# relevant: column 6
```

### Update Patterns

**Change type:**
```
Old: text
New: select_one gender
Action: Update type column, verify choice list exists
```

**Add constraint:**
```
Old: (no constraint)
New: constraint: . >= 0 and . <= 120
     constraint_message: Age must be between 0 and 120
Action: Add constraint and constraint_message columns
```

**Add relevance:**
```
Old: (no relevance)
New: relevant: ${age} >= 18
Action: Add relevant column
```

**Make required:**
```
Old: required: no
New: required: yes
     required_message: This field is required
Action: Update required and required_message columns
```

**Update label:**
```
Old: label: Name
New: label: Respondent's Full Name
Action: Update label column
```

## After Updating

1. **Verify** the changes were applied correctly
2. **Show structured output:**
```
SUCCESS: Updated question: first_name

  Changes:
    - label: "First Name" -> "Respondent First Name"
    - required: no -> yes
    - constraint: none -> regex(., '^[a-zA-Z\s\-\.']$')

  Row 2 updated
```

3. **Log the activity** to activity log
4. **Suggest validation:** "Next: Run /xlsform-validate to check for issues"

## Example Usage

```
User: /xlsform-update Update the age question to add a constraint (0-120)

Your response:
I'll update the age question to add a constraint.

Found: age (integer) on row 5

Proposed change:
  Add constraint: . >= 0 and . <= 120
  Add constraint_message: Age must be between 0 and 120

Confirming update...

SUCCESS: Updated question: age
  Changes:
    - constraint: added (. >= 0 and . <= 120)
    - constraint_message: added
```

```
User: /xlsform-update Change name question to be required

Your response:
I'll make the name question required.

Found: first_name (text) on row 2

Proposed change:
  required: no -> yes
  required_message: "This field is required"

SUCCESS: Updated question: first_name
  Changes:
    - required: no -> yes
    - required_message: added
```

## Error Handling

### Question Not Found
```
Error: Could not find question 'age' in the form.

Existing questions:
- first_name (row 2)
- last_name (row 3)
- gender (row 4)

Did you mean one of these?
```

### Invalid Type Change
```
Error: Cannot change 'household_members' from repeat to text.

Removing a repeat group will lose all repeat functionality.
If you want to remove questions inside the repeat, use /xlsform-remove first.
```

### Invalid Constraint
```
Error: Invalid constraint syntax: ". >= 0 and =< 120"

Did you mean: ". >= 0 and . <= 120"

Please confirm the correction.
```

### Circular Relevance
```
Warning: Relevance "${occupation} = 'Engineer'" may create circular dependency.

Question 'occupation' comes after this question. This could cause issues.
Consider reordering or using a different field.
```
