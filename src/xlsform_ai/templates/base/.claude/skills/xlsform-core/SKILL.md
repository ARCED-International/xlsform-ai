---
name: xlsform-core
description: Comprehensive XLSForm creation and editing skill. Use this skill when: (1) Creating XLSForm survey questions or adding new questions to a form, (2) Working with question types (text, select_one, select_multiple, geopoint, integer, decimal, date, etc.), (3) Implementing form logic including relevance, constraints, calculations, and triggers, (4) Validating XLSForm syntax and structure, (5) Converting paper forms, PDFs, or Word documents to XLSForm, (6) Working with advanced features like repeats, groups, cascading selects, choice filters, or external data, (7) Managing choice lists and ensuring list_name consistency between survey and choices sheets
---

# XLSForm Core Skill

## Quick Start

XLSForms are Excel workbooks that define forms for data collection. They have three main sheets:

1. survey - Contains all questions (rows are questions)
2. choices - Defines answer options for select questions
3. settings - Form metadata (optional but recommended)

Columns can appear in any order and optional columns can be omitted. Data after 20 adjacent blank rows or columns may be ignored by converters.

See references/settings-sheet.md for settings guidance.

### Adding a Simple Question

| type | name | label |
| --- | --- | --- |
| text | respondent_name | What is your name? |

### Adding a Select Question

**Survey sheet:**
| type | name | label |
| --- | --- | --- |
| select_one yes_no | likes_pizza | Do you like pizza? |

**Choices sheet:**
| list_name | name | label |
| --- | --- | --- |
| yes_no | yes | Yes |
| yes_no | no | No |

## Critical Rules

### 1. Name Uniqueness
- Every question name must be unique.
- Choice names must be unique within each list_name.
- Use snake_case for names (respondent_age, not Respondent Age).

### 2. list_name Consistency
- For select_one or select_multiple, the list name after the type must match list_name in choices.

### 3. Column Names Are Exact
- Column names are case-sensitive: type, name, label, list_name, constraint, relevant, etc.
- Columns can appear in any order and optional columns can be omitted.

### 4. Blank Row and Column Behavior
- Data after 20 adjacent blank rows or columns may be ignored. Keep data contiguous.

### 5. Settings Sheet (Recommended)
- Include form_title, form_id, version (common convention yyyymmddrr) if the settings sheet is present.
- default_language, submission_url, public_key, style, name, allow_choice_duplicates are optional.

### 6. Question Types (Highlights)
- Text types: text, integer, decimal, note, range
- Select: select_one listname, select_multiple listname, select_one_from_file, select_multiple_from_file
- Date/time: date, time, dateTime
- Geo: geopoint, geotrace, geoshape
- Media: image, audio, video, file, background-audio
- Metadata: start, end, today, deviceid, phonenumber, subscriberid, simserial, username, email, audit
- Special: calculate, hidden, rank, acknowledge, barcode, csv-external, xml-external

## Validation Checklist

Before considering changes complete, verify:

- All question name values are unique
- All choice name values are unique within their list
- list_name in choices matches list name in select questions
- Question types are valid (no typos like selct_one)
- For select_multiple: choice names have no spaces
- relevant formulas use ${field_name} syntax
- constraint formulas use . for the current field
- Column names are exact and case-sensitive
- begin/end group and begin/end repeat are balanced
- No large blank blocks (20+ adjacent blank rows or columns)

## Reference Documents

For detailed information, see:

- references/question-types.md - Complete list of question types
- references/syntax-guide.md - XLSForm structure, column rules, formulas
- references/settings-sheet.md - Settings sheet guidance
- references/validation-rules.md - Validation criteria
- references/common-patterns.md - Reusable patterns for relevance, calculations, repeats

## External Resources

- https://xlsform.org/en/ - Official XLSForm documentation

## Working with Commands

This skill is automatically used by these commands:

- /xlsform-add - Add new questions
- /xlsform-validate - Validate the form
- /xlsform-import - Import from PDF/Word/Excel
- /xlsform-update - Modify existing questions
- /xlsform-remove - Remove questions
- /xlsform-move - Reorder questions

These commands will automatically invoke this skill's knowledge when working with XLSForms.
