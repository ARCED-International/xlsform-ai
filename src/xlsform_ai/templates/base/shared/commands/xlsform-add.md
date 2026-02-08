---
description: Add questions to an XLSForm survey. Use this command to add new questions, specify question types (text, select_one, select_multiple, geopoint, integer, decimal, date, etc.), create choice lists, add multiple questions at once, or add questions with constraints and relevance.
arguments:
  - name: questions
    description: Question description(s) to add - can be a single question, multiple questions, or a file path (PDF/Word/Excel)
    required: true
  - name: type
    description: Question type (auto-detected from context if not specified)
    required: false
  - name: location
    description: Where to add the question (end of form, after specific question, or in a group/repeat)
    required: false
---

# Add XLSForm Questions

## Conflict Decision Protocol

- [MANDATORY] If there is ambiguity, conflict, or multiple valid actions, do not decide silently.
- [MANDATORY] If an interactive question tool is available (`AskUserQuestion`, `request_user_input`, or client-native choice UI), use it.
- [PREFERRED] In interactive-tool mode, ask all pending decisions in one interactive panel as separate questions, each with 2-4 mutually exclusive options.
- [MANDATORY] Once interactive mode is available for a command/session, keep all subsequent required decisions in interactive mode unless the tool fails.
- [MANDATORY] Put the recommended option first and include a one-line tradeoff.
- [MANDATORY] Wait for explicit user selection before applying changes.
- [FALLBACK] If no interactive tool is available, ask in plain REPL text with numbered options.
- [FORBIDDEN] Do not switch from interactive prompts to plain-text follow-up decisions when interactive tools are still available.
- [FORBIDDEN] Do not make silent decisions on required conflicts.
- [FORBIDDEN] Do not ask open-ended combined preference text when structured options are possible.
- Example: if imported names raise warnings (e.g., q308_phq1, fiq_1), collect the required naming decision via interactive options and wait for selection.

## Implementation Protocol

**CRITICAL: Follow this exact protocol when implementing this command:**

### 1. Use the Required Skills

**ALWAYS use these skills before working with XLSForm:**

```
/skill:xlsform-core
```
Provides XLSForm syntax, question types, and best practices.

```
/skill:activity-logging
```
Ensures proper activity logging protocols.

### Knowledge Base Reference

Consult these files for patterns and best practices before writing changes:
- `scripts/knowledge_base/data/use_cases.md`
- `scripts/knowledge_base/data/random_sampling.md`
- `scripts/knowledge_base/data/nested_repeats.md`
- `scripts/knowledge_base/data/settings_sheet.md`

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
from form_structure import build_column_mapping
from add_questions import add_questions
from log_activity import ActivityLogger
```

**NEVER import from other locations.**

**CRITICAL: Column Mapping Rule**

Never assume fixed column positions. Always read headers from row 1 and use `build_column_mapping()`.
This rule applies to survey, choices, and settings; always map headers before writing row 2 values in settings.

**CRITICAL: Standard Metadata**
Always include standard metadata rows (`start`, `end`, `today`, `deviceid`, `phonenumber`, `username`, `email`, `audit`) unless the user explicitly opts out.

### 3. Log the Action

After successfully adding questions:

```python
logger = ActivityLogger()
logger.log_action(
    action_type="add_questions",
    description=f"Added {count} question(s)",
    details=f"Questions: {question_summary}\nRows: {rows}"
)
```

### What NOT To Do

- **NEVER work directly without using skills**
- **NEVER import from other locations** (always use `scripts/`)
- **NEVER skip activity logging** for XLSForm modifications

## Key Principles

1. **Best Practices by Default**: Always add appropriate constraints and required fields
   - Name fields: letters only (regex)
   - Age fields: 0-130 range
   - Integer fields: non-negative
   - Decimal fields: positive
   - All fields: required by default (unless "optional" specified)

2. **Structured Output**: Keep output concise and scannable
   ```
   SUCCESS: Added 2 questions
     Row 2: text | first_name | "First Name"
   ```
   Avoid verbose explanations, use structured lists

3. **Use Helper Script**: Always use `scripts/add_questions.py` to avoid encoding issues

## Understanding Your Request

First, analyze what you're being asked to add:

1. **Single question**: "Add a text question asking for name"
2. **Multiple questions**: "Add questions for age, gender, and occupation"
3. **From file**: "Add all questions from questions.pdf page 1-5"
4. **Select question**: "Add a select_one question for favorite fruits"

## Current Form Structure

Before adding, read the current XLSForm file:

1. Identify which Excel file contains the XLSForm (typically `survey.xlsx`)
2. Read the `survey` sheet to understand existing questions
3. Read the `choices` sheet to see existing choice lists
4. Identify where to insert new questions (by default, add at the end)

**Use xlwings if the file is open, otherwise use openpyxl.**

### Safe Row Inspection (Avoid python -c)

One-line `python -c` commands often break due to quote escaping (especially with f-strings).
Use a heredoc (bash) or here-string (PowerShell) instead.

**PowerShell:**
```powershell
@'
import openpyxl

wb = openpyxl.load_workbook("survey.xlsx")
ws = wb["survey"]

print("Rows 10-14:")
for i in range(10, 15):
    name_val = ws.cell(i, 2).value
    if name_val is not None and str(name_val).strip():
        print(f"Row {i}: {ws.cell(i, 1).value} | {ws.cell(i, 2).value} | {ws.cell(i, 3).value}")

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

print("Rows 10-14:")
for i in range(10, 15):
    name_val = ws.cell(i, 2).value
    if name_val is not None and str(name_val).strip():
        print(f"Row {i}: {ws.cell(i, 1).value} | {ws.cell(i, 2).value} | {ws.cell(i, 3).value}")

print(f"Total rows: {ws.max_row}")
wb.close()
PY
```

## Proposed Changes

Present a clear summary of what will be added, **including best practices that will be applied**:

```
Adding 2 questions to survey sheet:

  Row 2: text | first_name | "First Name"
    Required: yes (best practice)
    Constraint: regex(., '^[a-zA-Z\s\-\.']$') (letters only)

  Row 3: text | last_name | "Last Name"
    Required: yes (best practice)
    Constraint: regex(., '^[a-zA-Z\s\-\.']$') (letters only)

Best practices applied automatically:
- Name fields: letters only, no numbers/special characters
- Age fields: range 0-130 years
- Integer fields: non-negative values
- All questions: required by default (unless optional implied)
```

For select questions, show:
```
Survey Sheet:
  [ ] Row N: select_one gender gender "What is your gender?"

Choices Sheet:
  [ ] gender male "Male"
  [ ] gender female "Female"
  [ ] gender other "Other"
```

## Validation

Before making changes, verify:

- [ ] Question name is unique (no duplicates in existing form)
- [ ] If select question: list_name doesn't conflict or can reuse existing list
- [ ] Question type is valid
- [ ] Name follows conventions (snake_case, starts with letter, no trailing numeric suffix)
- [ ] For select_multiple: choice names have no spaces

If any validation fails:
1. **Stop and explain the issue**
2. **Suggest a semantic fix** (e.g., "Should I use 'respondent_name_primary' instead?")
3. **Wait for user confirmation** before proceeding

## Implementation

### WARNING: IMPORTANT: Use openpyxl Directly, NOT Temporary Files

**NEVER create temporary Python files** (e.g., `add_questions_temp.py`). Always use openpyxl directly in the Bash tool.

### Efficient Implementation Methods

#### Method 1: Simple Questions - Use add_questions.py Helper

For **simple questions without complex escaping**, use the helper script:

```bash
# Single question

python scripts/add_questions.py '[{"type":"text","name":"first_name","label":"First Name"}]'

# Multiple simple questions

python scripts/add_questions.py '[{"type":"text","name":"first_name","label":"First Name"},{"type":"text","name":"last_name","label":"Last Name"}]'
```

#### Method 2: Complex Questions - Use openpyxl Directly (PREFERRED)

For **questions with constraints, regex, or special characters**, use openpyxl directly:

```python
import openpyxl
import sys
from pathlib import Path

scripts_dir = Path("scripts").resolve()
if str(scripts_dir) not in sys.path:
    sys.path.insert(0, str(scripts_dir))

# Load workbook

wb = openpyxl.load_workbook('survey.xlsx')
ws = wb['survey']
ws_choices = wb['choices']

# Find insertion point (after header)

insert_row = 2  # or use ws.max_row + 1 to append

# Add metadata fields

ws.cell(insert_row, 1, 'start')
ws.cell(insert_row, 2, 'start')
ws.cell(insert_row, 3, 'Start Time')
insert_row += 1

ws.cell(insert_row, 1, 'end')
ws.cell(insert_row, 2, 'end')
ws.cell(insert_row, 3, 'End Time')
insert_row += 1

# Add text question with constraint

ws.cell(insert_row, 1, 'text')
ws.cell(insert_row, 2, 'respondent_name')
ws.cell(insert_row, 3, 'What is your name?')
ws.cell(insert_row, 5, 'yes')
ws.cell(insert_row, 8, "regex(., '^[a-zA-Z\\s\\-\\.']+$')")
ws.cell(insert_row, 9, 'Please enter a valid name (letters only)')
insert_row += 1

# Add integer question with constraint

ws.cell(insert_row, 1, 'integer')
ws.cell(insert_row, 2, 'age')
ws.cell(insert_row, 3, 'How old are you?')
ws.cell(insert_row, 5, 'yes')
ws.cell(insert_row, 8, '. >= 0 and . <= 130')
ws.cell(insert_row, 9, 'Age must be between 0 and 130')
insert_row += 1

# Add select_one question

ws.cell(insert_row, 1, 'select_one gender')
ws.cell(insert_row, 2, 'gender')
ws.cell(insert_row, 3, 'What is your gender?')
ws.cell(insert_row, 5, 'yes')
insert_row += 1

# Add choices to choices sheet

# Find last data row in choices sheet (handles pre-formatted templates)

from form_structure import find_last_data_row
choice_start_row = find_last_data_row(ws_choices, 1, [1,2,3]) + 1
for i, (name, label) in enumerate([('-96', 'Other'), ('-99', "Don't know")], 1):
    ws_choices.cell(choice_start_row + i, 1, 'gender')
    ws_choices.cell(choice_start_row + i, 2, name)
    ws_choices.cell(choice_start_row + i, 3, label)

# Save

wb.save('survey.xlsx')
print(f'Added questions. Survey now has {ws.max_row} rows.')
```

### Stop on Errors, Verify Before Logging

- If any exception occurs, stop immediately and fix the script.
- After saving, re-open the workbook and verify expected rows were written before logging.
- Do not claim success or log activity until verification passes.

### Regex Tip

Use raw strings to avoid invalid escape warnings:
```python
constraint = r"regex(., '^[a-zA-Z\\s\\-\\.']+$')"
```

This approach:
- SUCCESS: Works reliably on all platforms (Windows/Mac/Linux)
- SUCCESS: No complex JSON escaping issues
- SUCCESS: Easy to read and debug
- SUCCESS: Supports complex constraints and regex patterns

#### Method 3: Multiple Questions with Choice Lists

When adding many questions with choices, structure your code clearly:

```python
import openpyxl

wb = openpyxl.load_workbook('survey.xlsx')
ws = wb['survey']
ws_choices = wb['choices']

row = 2

# Metadata

for field in ['start', 'end', 'today', 'deviceid']:
    ws.cell(row, 1, field)
    ws.cell(row, 2, field)
    ws.cell(row, 3, field.title())
    row += 1

# Begin group

ws.cell(row, 1, 'begin group')
ws.cell(row, 2, 'demographics')
ws.cell(row, 3, 'Demographics')
row += 1

# Questions

questions = [
    ('text', 'name', 'What is your name?', "regex(., '^[a-zA-Z\\s]+$')", 'Letters only'),
    ('integer', 'age', 'How old are you?', '. >= 0 and . <= 130', 'Age 0-130'),
    ('select_one gender', 'gender', 'What is your gender?', '', ''),
]

for q_type, q_name, q_label, constraint, constraint_msg in questions:
    ws.cell(row, 1, q_type)
    ws.cell(row, 2, q_name)
    ws.cell(row, 3, q_label)
    ws.cell(row, 5, 'yes')
    if constraint:
        ws.cell(row, 8, constraint)
        ws.cell(row, 9, constraint_msg)
    row += 1

# End group

ws.cell(row, 1, 'end group')
ws.cell(row, 2, 'demographics')
row += 1

# Add choices

choices = {'gender': [('1', 'Male'), ('2', 'Female'), ('-96', 'Other')]}
for list_name, options in choices.items():
    # Find last data row and start after it (handles pre-formatted templates)
    from form_structure import find_last_data_row
    choice_start_row = find_last_data_row(ws_choices, 1, [1,2,3]) + 1
    for i, (name, label) in enumerate(options, choice_start_row):
        ws_choices.cell(i, 1, list_name)
        ws_choices.cell(i, 2, name)
        ws_choices.cell(i, 3, label)

wb.save('survey.xlsx')
print(f'Added {len(questions)} questions')
```

### What NOT To Do

ERROR: **DO NOT create temporary Python files:**
```python
# DON'T DO THIS:

Write(add_temp.py)
...
Bash(python add_temp.py)
...
Bash(rm add_temp.py)
```

ERROR: **DO NOT use complex JSON strings with regex in bash:**
```bash
# DON'T DO THIS (fails due to escaping):

python scripts/add_questions.py '[{"type":"text","constraint":"regex(., '\''^[a-zA-Z]+$\'')"}]'
```

### Cross-Platform Compatibility

When creating Python code that runs in bash/PowerShell/Linux:

1. **Avoid Unicode characters** in print statements
   - Use ASCII: `SUCCESS` instead of `SUCCESS:`
   - Use ASCII: `ERROR` instead of `ERROR:`

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
   - Prefer heredocs / here-strings to avoid quoting errors

4. **Always add the scripts path before importing helpers**
   ```python
   import sys
   from pathlib import Path

   scripts_dir = Path("scripts").resolve()
   if str(scripts_dir) not in sys.path:
       sys.path.insert(0, str(scripts_dir))
   ```

5. **Test on multiple platforms**
   - Windows (Git Bash / PowerShell)
   - Linux (bash)
   - macOS (zsh/bash)

### Best Practices

1. **Use openpyxl directly** for complex questions
2. **Use add_questions.py** only for simple questions without special characters
3. **Structure your code clearly** with comments
4. **Add questions in batches** when possible
5. **Always save** the workbook after modifications
6. **Print success messages** to confirm changes

### Adding to Survey Sheet (Using openpyxl)

For each question to add, use direct openpyxl calls:

**Column Reference (COLUMNS dictionary):**
```python
COLUMNS = {
    "type": 1,      # Column A
    "name": 2,      # Column B
    "label": 3,     # Column C
    "hint": 4,      # Column D
    "required": 5,  # Column E
    "calculation": 6,# Column F
    "relevant": 7,  # Column G
    "constraint": 8,# Column H
    "constraint_message": 9,  # Column I
    "required_message": 10,   # Column J
    "appearance": 11,          # Column K
}
```

**Basic pattern:**
```python
ws.cell(row, COLUMNS['type'], 'text')
ws.cell(row, COLUMNS['name'], 'question_name')
ws.cell(row, COLUMNS['label'], 'Question text?')
ws.cell(row, COLUMNS['required'], 'yes')
```

**For select_one/select_multiple with choices:**
```python
# Add the question

ws.cell(row, 1, 'select_one gender')
ws.cell(row, 2, 'q_gender')
ws.cell(row, 3, 'What is your gender?')
ws.cell(row, 5, 'yes')
row += 1

# Add choices separately

choices = [('1', 'Male'), ('2', 'Female'), ('-96', 'Other')]
# Find last data row in choices sheet (handles pre-formatted templates)

from form_structure import find_last_data_row
choice_row = find_last_data_row(ws_choices, 1, [1,2,3]) + 1
for name, label in choices:
    ws_choices.cell(choice_row, 1, 'gender')
    ws_choices.cell(choice_row, 2, name)
    ws_choices.cell(choice_row, 3, label)
    choice_row += 1
```

### Adding to Choices Sheet (Using openpyxl)

If adding a select question with a new list_name:

```python
# Check if list exists

existing_lists = set()
for row in ws_choices.iter_rows(min_row=2, max_row=ws_choices.max_row, values_only=True):
    if row[0]:  # list_name column
        existing_lists.add(row[0])

# Add choices if list doesn't exist

if 'gender' not in existing_lists:
    choices = [
        ('1', 'Male'),
        ('2', 'Female'),
        ('-96', 'Other'),
        ('-99', "Don't know"),
        ('-98', 'Refused'),
    ]

    # Find last data row in choices sheet (handles pre-formatted templates)
    from form_structure import find_last_data_row
    choice_row = find_last_data_row(ws_choices, 1, [1,2,3]) + 1
    for name, label in choices:
        ws_choices.cell(choice_row, 1, 'gender')  # list_name
        ws_choices.cell(choice_row, 2, name)        # name
        ws_choices.cell(choice_row, 3, label)       # label
        choice_row += 1
```

**Basic question (text, integer, decimal, etc.):**
```
type: <question type>
name: <unique snake_case name>
label: <question text>
```

**Select question:**
```
type: select_one <list_name> or select_multiple <list_name>
name: <unique name>
label: <question text>
choice_filter: <optional filter>
```

**With relevance:**
```
type: <type>
name: <name>
label: <label>
relevant: <condition>
```

**With constraint:**
```
type: <type>
name: <name>
label: <label>
constraint: <constraint formula>
constraint_message: <error message>
```

### Adding to Choices Sheet

If adding a select question with a new list_name:

1. **Check if list_name already exists** in choices sheet
   - If yes: add new choices to existing list
   - If no: create new list

2. **For each choice option:**
```
list_name: <list_name>
name: <choice value name, no spaces for select_multiple>
label: <choice display text>
```

### Auto-Detection Rules (AI-Enhanced)

When type is not specified, the system uses intelligent type detection with **aggressive numeric preference**:

**Detection Strategy:**
1. **Choice options provided** -> `select_one`/`select_multiple` (always with numeric codes: 1, 2, 3...)
2. **Numeric keywords detected** -> `integer` or `decimal` (very aggressive)
3. **RAG similarity matching** -> Match against knowledge base of similar questions (if AI available)
4. **Text-only patterns** -> `text` (only for clearly text-only: names, addresses, descriptions)
5. **Yes/No patterns** -> `select_one yes_no`

**Integer Keywords (very aggressive):**
- age, how old, years old, count, number, how many, frequency, children, members, times, quantity

**Decimal Keywords (very aggressive):**
- weight, height, length, price, cost, income, salary, percentage, rate, temperature

**Text-Only Patterns (fallback):**
- name, address, describe, explain, specify, comment, open-ended

**Traditional Pattern Matching (fallback):**
- **"select one" / "choose one" / "radio"** -> `select_one`
- **"select multiple" / "check all that apply" / "checkbox"** -> `select_multiple`
- **"date" / "when"** -> `date`
- **"location" / "GPS" / "coordinates"** -> `geopoint`
- **"photo" / "picture" / "image"** -> `image`
- **"yes/no" / "true or false"** -> `select_one yes_no`

**Example:**
```
Question: "What is your age?"
Detected: integer (confidence: 0.85)
Reasoning: Integer keyword "age" detected

Question: "Enter your weight"
Detected: decimal (confidence: 0.85)
Reasoning: Decimal keyword "weight" detected

Question: "What is your name?"
Detected: text (confidence: 0.85)
Reasoning: Text-only keyword "name" detected
```

### Name Generation

When user doesn't specify a name:

1. Extract key words from question text
2. Convert to snake_case
3. Ensure uniqueness with semantic disambiguation (avoid numeric suffixes)
4. If semantic intent is unclear, ask user for preferred naming

**Examples:**
- "What is your name?" -> `respondent_name`
- "How old are you?" -> `age` or `respondent_age`
- "Do you like pizza?" -> `likes_pizza`
- "What is your gender?" -> `gender`

### Choice List Handling (AI-Enhanced)

The system automatically optimizes choice list reuse and uses **numeric codes by default**:

**Automatic Reuse:**
- `yes_no` - for Yes/No questions (1=Yes, 2=No)
- `gender_simple` - for gender questions (1=Male, 2=Female, 3=Other)
- `agreement` - for 5-point Likert scales (1=Strongly agree to 5=Strongly disagree)
- `frequency` - for frequency questions (1=Always to 5=Never)

**Numeric Codes Always Used:**
All choice lists use numeric codes (1, 2, 3...) for easier analysis in R/Stata/SPSS.

**"Other" Options:**
When "Other" is detected in choices:
- Automatically coded as "-96"
- System creates follow-up "Other specify" text question with relevance logic

**Special Response Codes (consistent negative values):**
- **-96**: Other (specify)
- **-99**: Don't know
- **-98**: Refused to answer

**Example:**
```
Question: Select your gender
Choices: Male, Female, Other (specify), Don't know, Refused

Creates:
1. select_one gender question
   - Choices: 1=Male, 2=Female, -96=Other (specify), -99=Don't know, -98=Refused
2. text question: gender_other
   - Label: "Please specify (Other)"
   - Relevance: ${gender} = '-96'
```

## After Adding

1. **Verify** the changes were applied correctly
2. **Show a concise summary** with this format:
```
SUCCESS: Added 2 questions

  Row 2: text | first_name | "First Name"
    Required: yes
    Constraint: regex(., '^[a-zA-Z\s\-\.']$')
    Constraint Message: Please enter a valid name (letters only)

  Row 3: text | last_name | "Last Name"
    Required: yes
    Constraint: regex(., '^[a-zA-Z\s\-\.']$')
    Constraint Message: Please enter a valid name (letters only)
```

3. **Next step suggestion** (one line):
```
Next: Run /xlsform-validate to check the form
```

**Keep output brief and structured. Avoid verbose explanations.**

## Example Usage

```
User: /xlsform-add Add a question asking for the respondent's name

Your response:
I'll add a text question for the respondent's name.

Current form has 15 questions. I'll add the new question at row 16.

Survey sheet:
  Row 16: text respondent_name "What is your name?"

Added successfully! The question has been added to the end of the survey.
Run /xlsform-validate to check for any issues.
```

```
User: /xlsform-add Add a select_one question for favorite fruits with options: Apple, Banana, Orange

Your response:
I'll add a select_one question for favorite fruits.

Survey sheet:
  Row 16: select_one fruits favorite_fruit "What is your favorite fruit?"

Choices sheet (new list 'fruits'):
  fruits apple "Apple"
  fruits banana "Banana"
  fruits orange "Orange"

Added successfully! Created new choice list 'fruits' with 3 options.
```

```
User: /xlsform-add Add questions for household member name and age in the household repeat

Your response:
I'll add these questions to the household repeat.

Current structure:
  begin repeat household_member (row 20)
    text member_name (row 21)
    ...

I'll add the new questions at row 22:

Survey sheet (within household_member repeat):
  Row 22: text member_name "Household member name"
  Row 23: integer member_age "Household member age"

Added successfully! Both questions are now inside the household_member repeat.
```

## Special Cases

### Adding to a Group or Repeat

When user specifies a location:
- "in the demographics group" -> find begin group, add inside
- "after the name question" -> find name question, add after it
- "in the household repeat" -> find begin repeat, add inside

### Importing from Files

When argument is a file path (questions.pdf, questions.docx, questions.xlsx):

1. **Use the appropriate parsing script:**
   - PDF: `scripts/parse_pdf.py <file> --pages <range>`
   - Word: `scripts/parse_docx.py <file>`
   - Excel: `scripts/parse_xlsx.py <file>`

2. **Parse the file** to extract question structure

3. **Present the extracted questions** to user for confirmation:
```
I found 15 questions in questions.pdf:

1. text: What is your name?
2. integer: How old are you?
3. select_one (gender): What is your gender?
   Choices: male, female, other
...

Should I add all these questions? (You can specify which ones to include)
```

4. **Add the confirmed questions** using the standard process

### Conditional Questions

When user implies conditionality:
- "Add age question if they're 18+" -> add with `relevant: ${previous} >= 18`
- "Only show if they answered yes to previous" -> detect from context

Extract the condition and add to `relevant` column.

### Questions with Constraints

When user mentions limits:
- "Add age question (must be 0-120)" -> add with constraint
- "Enter percentage (0-100)" -> add with constraint

Extract the constraint and:
1. Add to `constraint` column
2. Generate appropriate `constraint_message`

## Error Handling

### File Not Found
```
Error: Could not find survey.xlsx in the current directory.

Please ensure:
- You're in an XLSForm AI project directory
- The Excel file exists
- Or specify the file path explicitly
```

### File Already Open (when using openpyxl)
```
Note: The Excel file is currently open.
I'll use xlwings to make the changes so formatting is preserved.
```

### Duplicate Name Detected
```
Validation issue: A question named 'age' already exists in the form.

Suggested alternatives:
- age_2
- respondent_age
- age_follow_up

Which should I use?
```

### Invalid Type Detected
```
Validation issue: 'selct_one' is not a valid question type.

Did you mean:
- select_one
- select_multiple

Please confirm the correction.
```




