---
description: Remove questions or choice lists from XLSForm. Use this to delete questions from the survey sheet, remove choice lists from the choices sheet, or clean up unused items.
arguments:
  - name: target
    description: Question name or choice list name to remove
    required: true
  - name: scope
    description: What to remove (question, choice_list, or both)
    required: false
---

# Remove XLSForm Questions or Choice Lists

## Conflict Decision Protocol

- [MANDATORY] Use a sequential questioning loop (interactive): present EXACTLY ONE decision question at a time.
- [MANDATORY] For each decision, format the prompt as:
  - `**Question:** <single concrete decision>`
  - `**Why it matters:** <one sentence>`
  - `**Recommended:** Option [A] - <1-2 sentence reason>`
  - Options as a Markdown table:

| Option | Description |
|--------|-------------|
| A | <recommended option> |
| B | <alternative option> |
| C | <alternative option> (optional) |
| Short | Provide a different short answer (<=5 words) (optional) |

- [MANDATORY] End with a strict answer instruction:
  - `Reply with one option only: A, B, C, or Short.`
- [MANDATORY] Wait for the user reply before asking the next decision or making any edits.
- [FORBIDDEN] Do not bundle multiple decisions in one message.
- [FORBIDDEN] Do not ask for combined answers like "1, 1, keep current".
- [FORBIDDEN] Do not proceed when a required decision is unresolved.
- Example: if imported names raise warnings (e.g., q308_phq1, fiq_1), ask naming decision first and wait for reply.
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
- `scripts/knowledge_base/data/nested_repeats.md`
- `scripts/knowledge_base/data/use_cases.md`

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
from log_activity import ActivityLogger
```

**NEVER import from other locations.**

**CRITICAL: Column Mapping Rule**

Never assume fixed column positions. Always read headers from row 1 and use `build_column_mapping()` before writing.

### 3. Log the Action

After successfully removing questions or choice lists:

```python
from scripts.log_activity import ActivityLogger

logger = ActivityLogger()
logger.log_action(
    action_type="remove_questions",
    description=f"Removed {count} item(s)",
    details=f"Questions removed: {question_names}\nChoice lists removed: {choice_list_names}\nRows: {row_numbers}"
)
```

### What NOT To Do

- **NEVER work directly without using skills**
- **NEVER import from other locations** (always use `scripts/`)
- **NEVER skip activity logging** for XLSForm modifications

---

## Key Principles

1. **Safety first**: Check dependencies before removing
2. **Confirm intent**: Show what will be affected
3. **Clean up**: Remove orphaned choice lists
4. **Log activity**: All removals are logged to activity log

## Understanding Your Request

Identify what's being removed:

1. **Remove question**: "Remove the question named 'old_question'"
2. **Remove choice list**: "Remove the choice list 'fruits'"
3. **Remove both**: "Remove the gender question and its choice list"

## Current Form Structure

1. Read the survey.xlsx file
2. Locate the target question(s) or choice list(s)
3. Check for dependencies
4. Show what will be affected

### Safe Execution (No temp files, no python -c)

- **Do NOT** create temporary scripts (e.g., `temp_remove.py`)
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

When creating Python code for removal that runs on bash/PowerShell/Linux:

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
- After saving, re-open the workbook and verify removals before logging.

## Dependency Checking

Before removing, check:

### Question Dependencies
- **Relevance**: Do other questions reference this question?
- **Calculations**: Is this question used in calculations?
- **Choice filters**: Does any select question filter based on this?

### Choice List Dependencies
- **Survey questions**: Does any question use this list_name?
- **Cascading selects**: Is this list used in choice_filter expressions?

## Proposed Changes

Show what will be removed:

```
Removing: old_question

Found: Row 10 - text old_question "Old Question"

Dependencies found:
  - Question 'follow_up' uses ${old_question} in relevant
  - This will break the relevance condition

Action: Remove row 10
Warning: Question 'follow_up' relevance will be invalid

Choice lists to remove: none
```

For choice lists:
```
Removing Choice List: fruits

Used by:
  - favorite_fruit (select_one fruits)

Action: Remove choice list 'fruits'
Warning: favorite_fruit will have invalid list_name

Suggestion: Remove favorite_fruit question too?
```

## Validation

Before removing, verify:

- [ ] Target exists (question name or choice list name)
- [ ] Dependencies have been checked
- [ ] User is aware of impacts
- [ ] Confirmation received for destructive changes

## Implementation

### Removing a Question

1. **Find the question row** in survey sheet
2. **Remove the entire row**
3. **Update row references** (not needed for XLSForm, but good practice)
4. **Check for orphaned choice lists** (if question was select type)

Example:
```python
# Find row with name = target in column 2

# Delete that row

# Check if question type was select_one/select_multiple

# If yes, check if choice list is now unused

# If unused, offer to remove choice list

```

### Removing a Choice List

1. **Find all rows** with list_name = target in choices sheet
2. **Remove all those rows**
3. **Check for orphaned questions** that reference this list

Example:
```python
# Find all rows in choices sheet where list_name = target

# Delete all those rows

# Check survey sheet for questions using this list_name

# Warn about invalid questions

```

### Safe Removal Pattern

**With dependencies:**
```
Question 'age' is used in:
  - Question 'occupation' relevance: ${age} >= 18
  - Question 'senior' calculation: ${age} >= 65

Recommendation:
  1. Update or remove dependent questions first
  2. Then remove 'age'

Or, remove all related questions:
  - age
  - occupation (depends on age)
  - senior (depends on age)

Shall I remove all dependent questions too?
```

**Without dependencies:**
```
Question 'temp_question' has no dependencies.
Safe to remove.

Removing row 15...
```

## After Removing

1. **Verify** the removal was successful
2. **Show structured output:**
```
SUCCESS: Removed: old_question

  Removed from: Row 10
  Type: text
  Label: Old Question

  Choice lists affected: none
  Dependent questions: none
```

3. **Log the activity** to activity log
4. **Suggest validation:** "Next: Run /xlsform-validate to check for issues"

## Example Usage

```
User: /xlsform-remove Remove the question named 'old_question'

Your response:
I'll remove the question 'old_question'.

Found: Row 10 - text old_question "Old Question"

Checking dependencies...
No dependencies found. Safe to remove.

SUCCESS: Removed: old_question
  Removed from: Row 10
```

```
User: /xlsform-remove Remove the choice list 'unused_fruits'

Your response:
I'll remove the choice list 'unused_fruits'.

Found: 5 choices in list 'unused_fruits'
Checking if any questions use this list...

No questions use this list. Safe to remove.

SUCCESS: Removed: unused_fruits choice list
  Choices removed: 5
```

```
User: /xlsform-remove Remove age question

Your response:
I'll remove the age question.

Found: Row 5 - integer age "Age"

Checking dependencies...
Warning: age is used in:
  - occupation relevance: ${age} >= 18
  - is_senior calculation: ${age} >= 65

Recommendations:
  1. Remove dependent questions too (occupation, is_senior)
  2. Or update dependent questions first

Which approach would you like?
```

## Error Handling

### Question Not Found
```
Error: Could not find question 'xyz' in the form.

Existing questions:
- first_name (row 2)
- last_name (row 3)
- age (row 4)

Did you mean one of these?
```

### Choice List Not Found
```
Error: Could not find choice list 'xyz' in choices sheet.

Existing choice lists:
- gender
- yes_no
- agreement
```

### Cannot Remove Begin Group
```
Error: Cannot remove 'begin_group demographics'.

To remove a group:
1. Remove all questions inside the group
2. Remove the end_group row
3. Then remove the begin_group row

Or use: /xlsform-remove Remove entire demographics group
```

### Choice List Still in Use
```
Error: Cannot remove choice list 'gender'.

Still used by:
  - gender_question (select_one gender)
  - respondent_gender (select_one gender)

Remove those questions first, or specify: remove all
```

## Special Cases

### Removing a Group or Repeat

When user asks to remove a group/repeat:

1. Find the begin_group or begin_repeat row
2. Find the matching end_group or end_repeat row
3. Remove all rows between begin and end
4. Remove both begin and end rows
5. Verify no broken references

```
Removing: household_repeat

Found:
  begin repeat household_member (row 20)
  text member_name (row 21)
  integer member_age (row 22)
  end repeat household_member (row 23)

Removing rows 20-23...

SUCCESS: Removed: household_member repeat
  Questions removed: 3
  Rows removed: 20-23
```

### Bulk Removal

When user wants to remove multiple questions:

```
User: /xlsform-remove Remove questions q1, q2, and q3

Your response:
I'll remove 3 questions.

Found:
  - q1 (row 10) - text
  - q2 (row 11) - integer
  - q3 (row 12) - select_one options

Checking dependencies...
No dependencies found for any questions.

Removing from bottom up (to preserve row numbers)...
  Removed q3 (row 12)
  Removed q2 (row 11)
  Removed q1 (row 10)

SUCCESS: Removed: 3 questions
  Total rows removed: 3
  Choice lists removed: options (5 choices)
```




