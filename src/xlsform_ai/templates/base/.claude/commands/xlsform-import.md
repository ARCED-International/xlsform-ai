---
description: Import questions from questionnaire files into an XLSForm (PDF/Word primary, Excel also supported)
---

# Import Questions from File

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
- [MANDATORY] Missing settings decisions (`form_title`/`form_id`/`version`) must follow the same interactive protocol and may not be asked as plain numbered text when interactive tools are available.

### Interactive Decision Prompting (Preferred)

When multiple decisions are pending (for example naming, auto-scale, media location), use one interactive panel when the client supports it.

- Include one structured choice question per decision.
- Keep options mutually exclusive (2-4 options per question).
- Put the recommended option first with a one-line tradeoff.
- Apply changes only after explicit selections.

Fallback when no interactive panel tool exists:
- Ask the same decisions in plain REPL text with numbered options.
- Ask one decision at a time and wait for the answer.

### Settings Bootstrap Decision (Mandatory)

Before importing, check row-2 values in `settings` for `form_title`, `form_id`, and `version`.

- If `form_title` or `form_id` is empty, ask a structured interactive question to set them before import.
- Always suggest values:
  - Suggested `form_title`: derived from source file stem in title case.
  - Suggested `form_id`: snake_case from source stem.
- `version` should default to formula (not a fixed literal):
  - `=TEXT(NOW(), "yyyymmddhhmmss")`
- If `version` is blank, propose setting formula immediately.

Interactive options must include:
- `Set all now (Recommended)` - set suggested `form_title`, `form_id`, and formula `version`.
- `Set version only` - keep title/id empty for now, set formula `version`.
- `Continue without setting` - proceed and keep warning visible.

Settings write safety:
- Only write columns the user approved in the decision.
- Do not overwrite existing non-empty `version` unless the user explicitly asks to replace it.
- Do not modify unrelated settings columns/values.

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
- `[REQUIRED]` Use parser output JSON + `scripts/add_questions.py --from-json-file ...` instead of temporary transformation scripts.
- `[FORBIDDEN]` Do not use heredoc inline Python (for example `python - <<'PY' ... PY`) in normal import flow.
- `[FORBIDDEN]` Do not orchestrate parser flow with inline `python -c` snippets.
- `[FORBIDDEN]` Do not use ad-hoc `python -c` snippets for settings checks, JSON inspection, or workbook diagnostics during import.
- `[FORBIDDEN]` Do not create temporary scripts in project root/current directory (for example `temp_import_processor.py`).
- Fallback script creation is allowed only if:
  1. existing entrypoints fail after retry,
  2. user explicitly approves fallback in interactive panel,
  3. fallback script is created outside project workspace in OS temp directory,
  4. fallback script is removed after run.

### XLSForm.org Rules Snapshot

- Columns can be in any order; optional columns can be omitted.
- Data after 20 adjacent blank rows or columns may be ignored.
- Survey requires type/name/label; choices requires list_name/name/label.
- Question names: start with letter/underscore; allowed letters, digits, hyphen, underscore, period.
- Keep imported semantic question names concise (target <=32 chars) while still descriptive.
- Keep generated choice list names concise (target <=24 chars, e.g., `phq_freq_opts` not long sentence fragments).
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

- Option 1
- Option 2
- Option 3
```

### Constraint Extraction

Look for constraint indicators:
- "age between 18-65" -> constraint: `. >= 18 and . <= 65`
- "must be positive" -> constraint: `. > 0`
- "0-100" -> constraint: `. >= 0 and . <= 100`

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

Use the interactive question panel when available and include all pending decisions in the same panel.

Example decision prompt:

```text
[Interactive Panel]
Q1. Naming strategy for imported fields
- A: Apply semantic renaming (Recommended) - concise descriptive names (<=32 chars) and compact list names (<=24 chars)
- B: Keep source names as-is - fastest, but may keep risky names
- C: Keep source names and only deduplicate collisions - balanced compromise

Q2. Frequency/Likert conversion
- A: Auto-convert to select_one (Recommended) - cleaner coded analysis
- B: Keep as text - no automatic type inference risk

Q3. Media destination
- A: Save to ./media/<source_stem> (Recommended) - portable project layout
- B: Save beside source file - easy local review
- C: Use custom path - user-controlled location
- D: Skip image extraction - no media files added
```

Fallback REPL format (only if interactive panel is unavailable):

```text
Decision: <title>
1. <option 1> (Recommended) - <one-line tradeoff>
2. <option 2> - <one-line tradeoff>
Reply with one option number only (e.g., 1).
```

### Safe Execution (Use script entrypoints)

- **Do NOT** create ad-hoc scripts in project workspace (e.g., `import_fathers_survey.py`)
- **Do NOT** run heredoc Python blocks such as `python - <<'PY' ... PY`
- **Do NOT** run parser orchestration via `python -c "..."` one-liners
- **Do** map parser JSON directly using `add_questions.py --from-json-file` (no temporary transformation script)
- **Do** call parser scripts directly:

```bash
python scripts/parse_pdf.py <source> --pages <range> [--auto-scale] --output .xlsform-ai/tmp/import.json
python scripts/parse_docx.py <source> --media-dir <dir> --media-prefix <prefix> [--auto-scale] --output .xlsform-ai/tmp/import.json
python scripts/parse_xlsx.py <source> --sheet <sheet_name> --output .xlsform-ai/tmp/import.json
python scripts/add_questions.py --from-json-file .xlsform-ai/tmp/import.json --name-strategy <preserve|semantic>
```

### Option 2: Select Questions

```
Available questions:
[[OK]] 1. What is your name? (text)
[[OK]] 2. What is your gender? (select_one)
[ ] 3. How old are you? (integer) -> Skip
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
- "What is your name?" -> `respondent_name`
- "How old are you?" -> `age`
- "What is your gender?" -> `gender`
- Keep names concise (prefer <=32 chars) and avoid long sentence-like identifiers.
- Keep select list names concise (prefer <=24 chars; e.g., `phq_freq_opts`, `gender_opts`).

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




