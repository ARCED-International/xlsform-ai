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
  - name: file
    description: Override XLSForm file name (default: use xlsform-ai.json config or survey.xlsx)
    required: false
---

# Add XLSForm Questions

## Key Principles

1. **Best Practices by Default**: Always add appropriate constraints and required fields
   - Name fields: letters only (regex)
   - Age fields: 0-130 range
   - Integer fields: non-negative
   - Decimal fields: positive
   - All fields: required by default (unless "optional" specified)

2. **Structured Output**: Keep output concise and scannable
   ```
   ✓ Added 2 questions
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
- [ ] Name follows conventions (snake_case, starts with letter)
- [ ] For select_multiple: choice names have no spaces

If any validation fails:
1. **Stop and explain the issue**
2. **Suggest a fix** (e.g., "Should I use 'respondent_name_1' instead?")
3. **Wait for user confirmation** before proceeding

## Implementation

### Use Helper Script for Adding Questions

Instead of inline Python commands that may have encoding issues on Windows, use the `scripts/add_questions.py` helper:

**For simple text questions:**
```bash
python scripts/add_questions.py '[{"type":"text","name":"first_name","label":"First Name"}]'
```

**For multiple questions:**
```bash
python scripts/add_questions.py '[{"type":"text","name":"first_name","label":"First Name"},{"type":"text","name":"last_name","label":"Last Name"}]'
```

**For questions with constraints:**
```bash
python scripts/add_questions.py '[{"type":"integer","name":"age","label":"Age","constraint":".>=0 and .<=120","constraint_message":"Age must be between 0 and 120"}]'
```

**For select questions, you need to manually add choices to the choices sheet:**
1. Add the question using the helper script
2. Manually add the choice list to the choices sheet using openpyxl or xlwings

### Adding to Survey Sheet

For each question to add:

1. **Determine the row** to insert (end of form, or after specified location)
2. **Map columns** based on question type:

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

### Auto-Detection Rules

When type is not specified, detect from description:

- **"select one" / "choose one" / "radio"** → `select_one`
- **"select multiple" / "check all that apply" / "checkbox"** → `select_multiple`
- **"enter name" / "write" / "text"** → `text`
- **"age" / "number" / "how many"** → `integer`
- **"weight" / "height" / "price"** → `decimal`
- **"date" / "when"** → `date`
- **"location" / "GPS" / "coordinates"** → `geopoint`
- **"photo" / "picture" / "image"** → `image`
- **"yes/no" / "true or false"** → `select_one yes_no` (reuse if exists)

### Name Generation

When user doesn't specify a name:

1. Extract key words from question text
2. Convert to snake_case
3. Ensure uniqueness by adding number suffix if needed

**Examples:**
- "What is your name?" → `respondent_name`
- "How old are you?" → `age` or `respondent_age`
- "Do you like pizza?" → `likes_pizza`
- "What is your gender?" → `gender`

### Choice List Handling

**When to reuse existing lists:**
- `yes_no` - for yes/no questions
- `gender` - for gender questions
- Any list that has the exact same choices needed

**When to create new lists:**
- Custom choices specific to the question
- Different labels for the same values
- Need for additional data columns

**Default choices for common types:**

For yes/no:
```
list_name: yes_no
choices: yes, no
```

For gender:
```
list_name: gender
choices: male, female, other, prefer_not_to_say
```

For agreement:
```
list_name: agreement
choices: strongly_agree, agree, neutral, disagree, strongly_disagree
```

## After Adding

1. **Verify** the changes were applied correctly
2. **Show a concise summary** with this format:
```
✓ Added 2 questions

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
- "in the demographics group" → find begin group, add inside
- "after the name question" → find name question, add after it
- "in the household repeat" → find begin repeat, add inside

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
- "Add age question if they're 18+" → add with `relevant: ${previous} >= 18`
- "Only show if they answered yes to previous" → detect from context

Extract the condition and add to `relevant` column.

### Questions with Constraints

When user mentions limits:
- "Add age question (must be 0-120)" → add with constraint
- "Enter percentage (0-100)" → add with constraint

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
