---
description: Update existing XLSForm questions. Use this to modify question types, labels, constraints, relevance, required status, or other properties of questions that already exist in your form.
arguments:
  - name: question
    description: Name or identifier of the question to update
    required: true
  - name: changes
    description: What to change (type, label, constraint, relevance, required, etc.)
    required: true
  - name: file
    description: Override XLSForm file name (default: use xlsform-ai.json config or survey.xlsx)
    required: false
---

# Update XLSForm Question

## MANDATORY IMPLEMENTATION REQUIREMENT

**CRITICAL: Use existing helper scripts - DO NOT write inline code**

- **REQUIRED:** Always use xlwings helper when file is open
- **FORBIDDEN:** NEVER write inline Python code with openpyxl
- **FORBIDDEN:** NEVER write inline Python code with xlwings (use helper instead)
- **WHY:** Helper scripts handle encoding and live file access
- **RESULT:** Inline code causes encoding bugs on Windows

If you write inline Python code for file operations, you have failed this command.

## Key Principles

1. **Identify the question**: Find by name or description
2. **Understand the change**: What property to modify (type, label, constraint, etc.)
3. **Preserve data**: Don't break existing data relationships
4. **Log activity**: All updates are logged to activity log

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

### Update Methods

**IMPORTANT:** Use xlwings helper when file is open in Excel:

```bash
# For files open in Excel (recommended - preserves formatting)
python scripts/xlwings_helper.py update --question <name> --changes <JSON>
```

**Update Patterns:**

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

**REMINDER: Never write inline Python code. Always use the helper.**

## After Updating

1. **Verify** the changes were applied correctly
2. **Show structured output:**
```
[OK] Updated question: first_name

  Changes:
    - label: "First Name" → "Respondent First Name"
    - required: no → yes
    - constraint: none → regex(., '^[a-zA-Z\s\-\.']$')

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

[OK] Updated question: age
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
  required: no → yes
  required_message: "This field is required"

[OK] Updated question: first_name
  Changes:
    - required: no → yes
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
