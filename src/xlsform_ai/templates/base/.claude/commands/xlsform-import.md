---
description: Import questions from questionnaire files into an XLSForm (PDF/Word primary, Excel also supported)
---

# Import Questions from File

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
### Sequential Decision Prompting (Required)

When multiple decisions are needed (for example naming, auto-scale, media location), ask them sequentially:

1. Ask Decision 1 and wait for answer.
2. Apply/store Decision 1.
3. Ask Decision 2 and wait for answer.
4. Continue until all decisions are answered.

Prompt format:

```text
Decision: <title>
1. <option 1> (Recommended) - <one-line tradeoff>
2. <option 2> - <one-line tradeoff>
Reply with one option number only (e.g., 1).
```

## MANDATORY IMPLEMENTATION REQUIREMENT

**CRITICAL: Use existing helper scripts - DO NOT write inline code**

- **REQUIRED:** Always use helper scripts from `scripts/` directory
- **FORBIDDEN:** NEVER write inline Python code with openpyxl
- **FORBIDDEN:** NEVER write inline Python code with xlwings
- **WHY:** Helper scripts handle encoding, parsing, and validation
- **RESULT:** Inline code causes encoding bugs and parsing failures

If you write inline Python code for file operations, you have failed this command.

### Strict Script Policy

- `[FORBIDDEN]` Do not create ad-hoc `.py` scripts in the project workspace for import.
- `[REQUIRED]` Use existing entrypoints first: `scripts/parse_pdf.py`, `scripts/parse_docx.py`, `scripts/parse_xlsx.py`, `scripts/add_questions.py`.
- `[FORBIDDEN]` Do not use heredoc inline Python (for example `python - <<'PY' ... PY`) in normal import flow.
- `[FORBIDDEN]` Do not orchestrate parser flow with inline `python -c` snippets.
- Fallback script creation is allowed only if:
  1. existing entrypoints fail after retry,
  2. user explicitly approves fallback in REPL,
  3. fallback is created in temp directory and removed after run.

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

The user wants to import questions from an external file into their XLSForm.

**File types supported:**
- PDF (.pdf)
- Word (.docx)
- Excel (.xlsx)

**Layout types supported:**
- Text-only questionnaires
- Table-based questionnaires
- Mixed text + table documents

## Load and Parse File

### 1. Identify File Type

Check the file extension and use the appropriate parser:

```bash
# PDF

python scripts/parse_pdf.py <source> --pages <range> [--auto-scale]

# Word

python scripts/parse_docx.py <source> --media-dir <dir> --media-prefix <prefix> [--auto-scale]

# Excel

python scripts/parse_xlsx.py <source> --sheet <sheet_name>
```

### 2. Execute Parser

Run the appropriate script and capture its output.

For Word with images, include:
- `--media-dir <path>` to control where images are saved
- `--media-prefix <prefix>` for XLSForm media::image values
- `--no-images` to disable image extraction
- `--auto-scale` when user selects auto-convert for frequency/Likert text questions

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

ÃƒÂ¢Ã‹Å“Ã‚Â Option 1
ÃƒÂ¢Ã‹Å“Ã‚Â Option 2
ÃƒÂ¢Ã‹Å“Ã‚Â Option 3
```

### Constraint Extraction

Look for constraint indicators:
- "age between 18-65" ÃƒÂ¢Ã¢â‚¬Â Ã¢â‚¬â„¢ constraint: `. >= 18 and . <= 65`
- "must be positive" ÃƒÂ¢Ã¢â‚¬Â Ã¢â‚¬â„¢ constraint: `. > 0`
- "0-100" ÃƒÂ¢Ã¢â‚¬Â Ã¢â‚¬â„¢ constraint: `. >= 0 and . <= 100`

### Decision-to-Action Guarantee

If user selects `Auto-convert to select_one` for frequency/Likert text questions:
1. Re-run parser with auto-scale conversion enabled:
   - `python scripts/parse_docx.py <source> --auto-scale ...`
   - `python scripts/parse_pdf.py <source> --auto-scale ...`
2. Apply converted output to XLSForm (survey + choices).
3. Verify conversion by counting imported rows with `type=select_one` that were previously `text`.
4. Report exact counts and sample field names in final response.

Never acknowledge conversion unless step 3 confirms it happened.

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

Ask one decision at a time using the interactive Q/A format.

Example decision prompt:

```text
**Question:** Which naming strategy should we use for imported fields?
**Why it matters:** Numeric and duplicate-style names can create repeat/export ambiguity and harder maintenance.
**Recommended:** Option [A] - Apply semantic renaming for long-term XLSForm clarity.

| Option | Description |
|--------|-------------|
| A | Apply semantic renaming (recommended) |
| B | Keep source names as-is |
| C | Keep source names but only deduplicate collisions |
| Short | Provide a different short answer (<=5 words) |

Reply with one option only: A, B, C, or Short.
```

Then ask the next decision only after answer:
- Frequency/Likert auto-conversion (`--auto-scale`)
- Media destination (`./media/<source_stem>`, beside source, custom, or skip)

Never request combined responses in one message.

### Safe Execution (Use script entrypoints)

- **Do NOT** create ad-hoc scripts in project workspace (e.g., `import_fathers_survey.py`)
- **Do NOT** run heredoc Python blocks such as `python - <<'PY' ... PY`
- **Do NOT** run parser orchestration via `python -c "..."` one-liners
- **Do** call parser scripts directly:

```bash
python scripts/parse_pdf.py <source> --pages <range> [--auto-scale]
python scripts/parse_docx.py <source> --media-dir <dir> --media-prefix <prefix> [--auto-scale]
python scripts/parse_xlsx.py <source> --sheet <sheet_name>
```

### Option 2: Select Questions

```
Available questions:
[[OK]] 1. What is your name? (text)
[[OK]] 2. What is your gender? (select_one)
[ ] 3. How old are you? (integer) ÃƒÂ¢Ã¢â‚¬Â Ã‚Â Skip
[[OK]] 4. Select your favorite fruits (select_multiple)
...

Enter numbers to toggle selection, or 'all'/'none':
```

### Option 3: Review and Edit

For each question:
```
Question 1/15:

Type: [text]
Name: [respondent_name]
Label: What is your name?
Required: [yes]

Accept (A), Edit (E), Skip (S), or Quit (Q)?
```

## Import Process

Once confirmed:

### 1. Generate Question Names

Create unique, descriptive names:
- "What is your name?" ÃƒÂ¢Ã¢â‚¬Â Ã¢â‚¬â„¢ `respondent_name`
- "How old are you?" ÃƒÂ¢Ã¢â‚¬Â Ã¢â‚¬â„¢ `age`
- "What is your gender?" ÃƒÂ¢Ã¢â‚¬Â Ã¢â‚¬â„¢ `gender`

Check for duplicates and resolve with semantic names (avoid numeric suffixes).

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

**With question image:**
```
Row N: text product_photo "Upload/confirm product" media::image="questionnaire/img_0001_ab12cd34.png"
```

Before writing media values, ensure `media::image` header exists in survey row 1.

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

**Add choice images when present:**
```
Row N: list_name=animals name=cat label="Cat" media::image="questionnaire/img_0003_44bb5511.png"
```

Before writing choice media values, ensure `media::image` header exists in choices row 1.

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
[WARNING]  Warning: Similar questions found in current form

Existing: respondent_name "What is your name?"
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
[FAIL] Error: File 'questions.pdf' not found.

Please check:
- File path is correct
- File extension is .pdf, .docx, or .xlsx
- File is in the current directory or provide full path
```

### Unsupported File Type
```
[FAIL] Error: Unsupported file type '.txt'

Supported formats:
- PDF (.pdf)
- Word (.docx)
- Excel (.xlsx)
```

### No Questions Found
```
[WARNING]  Warning: No questions could be detected in the file.

This could be because:
- File format is not supported
- Questions are in an unusual format
- File is scanned images (needs OCR)
- Table headers are non-standard (review manually)

Try:
- Converting to a different format
- Re-running parser with media/table settings
- Using /xlsform-add to manually create questions
```

### Parser Script Failed
```
[FAIL] Error: Failed to parse file

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
  [OK] 1. respondent_name (text)
  [OK] 2. gender (select_one)
  [OK] 3. age (integer)
  [OK] 4. favorite_fruits (select_multiple)
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




