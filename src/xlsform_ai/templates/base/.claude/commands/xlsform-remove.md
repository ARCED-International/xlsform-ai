---
description: Remove questions or choice lists from XLSForm. Use this to delete questions from the survey sheet, remove choice lists from the choices sheet, or clean up unused items.
arguments:
  - name: target
    description: Question name or choice list name to remove
    required: true
  - name: scope
    description: What to remove (question, choice_list, or both)
    required: false
  - name: file
    description: Override XLSForm file name (default: use xlsform-ai.json config or survey.xlsx)
    required: false
---

# Remove XLSForm Questions or Choice Lists

## MANDATORY IMPLEMENTATION REQUIREMENT

**CRITICAL: Use existing helper scripts - DO NOT write inline code**

- **REQUIRED:** Always use xlwings helper when file is open
- **FORBIDDEN:** NEVER write inline Python code with openpyxl
- **FORBIDDEN:** NEVER write inline Python code with xlwings (use helper instead)
- **WHY:** Helper scripts handle encoding and live file access
- **RESULT:** Inline code causes encoding bugs on Windows

If you write inline Python code for file operations, you have failed this command.

## Key Principles

1. **Safety first**: Check dependencies before removing
2. **Confirm intent**: Show what will be affected
3. **Clean up**: Remove orphaned choice lists
4. **Log activity**: All removals are logged to activity log

### XLSForm.org Rules Snapshot

- Columns can be in any order; optional columns can be omitted.
- Data after 20 adjacent blank rows or columns may be ignored.
- Survey requires type/name/label; choices requires list_name/name/label.
- Question names: start with letter/underscore; allowed letters, digits, hyphen, underscore, period.
- select_multiple choice names must not contain spaces.
- For cascading selects with duplicate choice names, set allow_choice_duplicates in settings.
- or_other only works without translations and without choice_filter; it uses English "Specify other".
- Settings sheet is optional but recommended; include form_title, form_id, version (yyyymmddrr).

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

### Removal Methods

**IMPORTANT:** Use xlwings helper when file is open in Excel:

```bash
# For files open in Excel (recommended - preserves formatting)
python scripts/xlwings_helper.py remove --target <name>
```

### Removing a Question

1. **Find the question row** in survey sheet
2. **Remove the entire row**
3. **Check for orphaned choice lists** (if question was select type)

### Removing a Choice List

1. **Find all rows** with list_name = target in choices sheet
2. **Remove all those rows**
3. **Check for orphaned questions** that reference this list

**REMINDER: Never write inline Python code. Always use the helper.**

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
[OK] Removed: old_question

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

[OK] Removed: old_question
  Removed from: Row 10
```

```
User: /xlsform-remove Remove the choice list 'unused_fruits'

Your response:
I'll remove the choice list 'unused_fruits'.

Found: 5 choices in list 'unused_fruits'
Checking if any questions use this list...

No questions use this list. Safe to remove.

[OK] Removed: unused_fruits choice list
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

[OK] Removed: household_member repeat
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

[OK] Removed: 3 questions
  Total rows removed: 3
  Choice lists removed: options (5 choices)
```
