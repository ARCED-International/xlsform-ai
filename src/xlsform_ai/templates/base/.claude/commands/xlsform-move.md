---
description: Move or reorder XLSForm questions. Use this to move questions to different positions, move questions into/out of groups or repeats, or reorder questions within a form.
arguments:
  - name: question
    description: Name of the question to move
    required: true
  - name: location
    description: Where to move it (position, after/before another question, into group/repeat)
    required: true
  - name: file
    description: Override XLSForm file name (default: use xlsform-ai.json config or survey.xlsx)
    required: false
---

# Move XLSForm Questions

## MANDATORY IMPLEMENTATION REQUIREMENT

**CRITICAL: Use existing helper scripts - DO NOT write inline code**

- **REQUIRED:** Always use xlwings helper when file is open
- **FORBIDDEN:** NEVER write inline Python code with openpyxl
- **FORBIDDEN:** NEVER write inline Python code with xlwings (use helper instead)
- **WHY:** Helper scripts handle encoding and live file access
- **RESULT:** Inline code causes encoding bugs on Windows

If you write inline Python code for file operations, you have failed this command.

## Key Principles

1. **Preserve structure**: Keep groups/repeats intact
2. **Validate placement**: Don't break begin/end pairs
3. **Update references**: Maintain row relationships
4. **Log activity**: All moves are logged to activity log

## Understanding Your Request

Identify the move operation:

1. **To position**: "Move name question to the top/beginning"
2. **After question**: "Move age question after name question"
3. **Before question**: "Move occupation before age"
4. **Into group**: "Move income question into demographics group"
5. **Out of group**: "Move phone question out of contact group"

## Current Form Structure

1. Read the survey.xlsx file
2. Locate the source question
3. Locate the target position
4. Check for structural issues (groups, repeats)

## Proposed Changes

Show the move operation:

```
Moving: phone_question

From: Row 15 (inside contact_info group)
To: After name question (Row 3, outside group)

Action:
  1. Extract row 15 (phone_question)
  2. Insert at new position (row 4)
  3. Shift other questions down

Warning: This will move phone_question out of contact_info group.
```

For moving into groups:
```
Moving: income_question

From: Row 10 (outside groups)
To: Into demographics group (after age question)

Group structure:
  begin group demographics (row 5)
    text name (row 6)
    integer age (row 7)
    ← income_question will go here
  end group demographics (row 8)

Action: Insert at row 8, shift end_group down
```

## Validation

Before moving, verify:

- [ ] Source question exists
- [ ] Target position exists (or is valid like "top", "bottom")
- [ ] Group/repeat structure remains valid
- [ ] No orphaned questions outside groups
- [ ] begin/end pairs remain balanced

## Implementation

### Move Methods

**IMPORTANT:** Use xlwings helper when file is open in Excel:

```bash
# For files open in Excel (recommended - preserves formatting)
python scripts/xlwings_helper.py move --question <name> --location <target>
```

### Move Strategies

**Strategy 1: Cut and Insert (Simple)**
1. Copy entire source row
2. Delete source row
3. Insert at target position
4. Good for simple moves within same level

**Strategy 2: Row-by-Row (Safe)**
1. Read source row data
2. Delete source row
3. Find new target row number
4. Insert at new position
5. Verify structure

**Strategy 3: Group-Aware (Complex)**
1. Extract source with dependencies
2. Delete from source
3. Insert at target maintaining hierarchy
4. Validate begin/end pairs

### Move Patterns

**To beginning (top):**
```
Source: Row 15
Target: Row 2 (after header, before first question)

Action:
  - Copy row 15 data
  - Delete row 15
  - Insert at row 2
  - All other rows shift down
```

**To end (bottom):**
```
Source: Row 3
Target: After last question (row 20)

Action:
  - Copy row 3 data
  - Delete row 3
  - Append at end
```

**After specific question:**
```
Source: age (row 5)
Target: After name (row 4)

Action:
  - Copy age row (row 5)
  - Delete row 5
  - Insert after name (new row 5)
  - Rows shift accordingly
```

**Into group:**
```
Source: income (row 10)
Target: Into demographics group (after age)

Group before:
  begin group (row 5)
    name (row 6)
    age (row 7)
  end group (row 8)

Action:
  - Copy income row (row 10)
  - Delete row 10
  - Insert at row 8 (inside group, after age)
  - end_group shifts to row 9

Group after:
  begin group (row 5)
    name (row 6)
    age (row 7)
    income (row 8) ← moved here
  end group (row 9)
```

**Out of group:**
```
Source: phone (row 7, inside contact_info group)
Target: Outside groups, after demographics

Current structure:
  begin group demographics (row 5)
    name (row 6)
  end group (row 7)
  begin group contact_info (row 8)
    phone (row 9)
  end group (row 10)

Action:
  - Copy phone row (row 9)
  - Delete row 9
  - Insert at row 8 (between groups)
  - contact_info group shifts

Result:
  begin group demographics (row 5)
    name (row 6)
  end group (row 7)
  phone (row 8) ← moved here, outside groups
  begin group contact_info (row 9)
    (empty or shifts)
  end group (row 10)
```

### Validation Checks

**Before move:**
- Check source exists
- Check target is valid
- Check if moving into/out of groups
- Verify group structure remains valid

**After move:**
- Verify source removed correctly
- Verify question inserted at target
- Check no orphaned questions
- Validate begin/end pairs balanced

## After Moving

1. **Verify** the move was successful
2. **Show structured output:**
```
✓ Moved: age_question

  From: Row 15
  To: Row 3 (top of form)

  New order:
    Row 2: first_name
    Row 3: age_question ← moved here
    Row 4: last_name
    ...
```

3. **Log the activity** to activity log
4. **Suggest validation:** "Next: Run /xlsform-validate to check structure"

## Example Usage

```
User: /xlsform-move Move the name question to the top

Your response:
I'll move the name question to the top of the form.

Found: first_name (text) on row 10

Moving to row 2 (top of form, after header)...

✓ Moved: first_name
  From: Row 10
  To: Row 2
```

```
User: /xlsform-move Move age after name

Your response:
I'll move the age question to after the name question.

Found:
  - name on row 2
  - age on row 5

Moving age to row 3 (after name)...

✓ Moved: age
  From: Row 5
  To: Row 3
```

```
User: /xlsform-move Move income into demographics group

Your response:
I'll move the income question into the demographics group.

Found:
  - income on row 10 (outside groups)
  - demographics group: rows 5-8

Moving into demographics group...

Current group structure:
  begin group demographics (row 5)
    text name (row 6)
    integer age (row 7)
  end group (row 8)

Moving to row 8 (inside group, after age)...

✓ Moved: income
  From: Row 10
  To: Row 8 (inside demographics group)

New group structure:
  begin group demographics (row 5)
    text name (row 6)
    integer age (row 7)
    text income (row 8) ← moved here
  end group (row 9)
```

## Error Handling

### Question Not Found
```
Error: Could not find question 'xyz' to move.

Available questions:
- first_name (row 2)
- last_name (row 3)
- age (row 4)

Which question do you want to move?
```

### Target Not Found
```
Error: Could not find 'target_question' to move after.

Available questions:
- first_name (row 2)
- last_name (row 3)

Where should I move it?
```

### Would Break Group Structure
```
Error: Cannot move 'begin_group' out of position.

Groups must have matching begin/end pairs.
To move a group, move all questions inside it first,
then use /xlsform-remove to remove the empty group.
```

### Moving Into Repeat With Count
```
Warning: Moving into 'household' repeat which has repeat_count.

This may affect repeat calculations if repeat_count refers to
specific question positions.

Continue anyway? (y/n)
```

### Orphaned Questions
```
Warning: Moving 'name' out of demographics group would leave
the group empty.

Options:
  1. Remove the empty demographics group
  2. Leave the group empty
  3. Keep name in the group

Which would you prefer?
```

## Special Cases

### Reordering Multiple Questions

```
User: /xlsform-move Move name and age to the top, in that order

Your response:
I'll move name and age questions to the top.

Found:
  - name on row 10
  - age on row 12

Moving in reverse order (to maintain positions)...

Step 1: Move age to row 3
Step 2: Move name to row 2

✓ Moved: 2 questions
  New order:
    Row 2: name
    Row 3: age
    (other questions shifted down)
```

### Reversing Order

```
User: /xlsform-move Reverse the order of all questions

Current order:
  1. q1
  2. q2
  3. q3

Reversing...

✓ Reordered: 3 questions
  New order:
    1. q3
    2. q2
    3. q1
```

### Moving Between Groups

```
User: /xlsform-move Move phone from contact_info to demographics group

Found:
  - phone in contact_info group (row 9)
  - demographics group (rows 5-8)

Moving from contact_info to demographics...

Warning: contact_info group will be empty after this move.
Action: Removing empty contact_info group.

✓ Moved: phone
  From: contact_info group
  To: demographics group (after age question)

  Empty group removed: contact_info
```
