---
name: xlsform-core
description: Comprehensive XLSForm creation and editing skill. Use this skill when: (1) Creating XLSForm survey questions or adding new questions to a form, (2) Working with question types (text, select_one, select_multiple, geopoint, integer, decimal, date, etc.), (3) Implementing form logic including relevance conditions, constraints, calculations, and triggers, (4) Validating XLSForm syntax and structure, (5) Converting paper forms, PDFs, or Word documents to XLSForm, (6) Working with advanced features like repeats, groups, cascading selects, choice filters, or external data, (7) Managing choice lists and ensuring list_name consistency between survey and choices sheets
---

# XLSForm Core Skill

## Quick Start

XLSForms are Excel workbooks that define forms for data collection. They have three main sheets:

1. **survey** - Contains all questions (rows are questions)
2. **choices** - Defines answer options for select questions
3. **settings** - Form metadata (form title, ID, version)

### Adding a Simple Question

To add a question to the survey sheet:

| type | name | label |
| --- | --- | --- |
| text | respondent_name | What is your name? |

### Adding a Select Question

For select_one or select_multiple, you need both sheets:

**survey sheet:**
| type | name | label |
| --- | --- | --- |
| select_one yes_no | likes_pizza | Do you like pizza? |

**choices sheet:**
| list_name | name | label |
| --- | --- | --- |
| yes_no | yes | Yes |
| yes_no | no | No |

## Critical Rules

### 1. Name Uniqueness
- Every question (in the `name` column) must be **unique**
- Every choice name (in the `name` column of choices) must be **unique within a list**
- Use snake_case for names (e.g., `respondent_age`, not `Respondent Age`)

### 2. list_name Consistency
- For `select_one` or `select_multiple` types, the list name after the type MUST match the `list_name` in the choices sheet
- Example: `select_one fruits` requires choices with `list_name` = `fruits`

### 3. Column Names Are Exact
- Column names must be exact: `type`, `name`, `label`, `list_name`, `constraint`, `relevant`, etc.
- `Choices` or `choice` will NOT work - must be `choices`

### 4. Question Types
- Text types: `text`, `integer`, `decimal`, `note`
- Select: `select_one listname`, `select_multiple listname`
- Date/time: `date`, `time`, `dateTime`
- Geo: `geopoint`, `geotrace`, `geoshape`
- Media: `image`, `audio`, `video`
- Metadata: `start`, `end`, `today`, `deviceid`, `username`, `audit`

## When to Use xlwings vs openpyxl

### Use xlwings when:
- Excel file is currently OPEN
- You need to preserve formatting (colors, fonts, borders)
- You want real-time preview as changes are made

### Use openpyxl when:
- Excel file is closed
- Formatting preservation is less critical
- You need faster file operations

**Always** save changes after editing. **Never** close the file when using xlwings (let the user close it).

## Validation Checklist

Before considering changes complete, verify:

- [ ] All question `name` values are unique
- [ ] All choice `name` values are unique within their list
- [ ] `list_name` in choices sheet matches the list name in select questions
- [ ] Question types are valid (no typos like `selct_one`)
- [ ] For `select_one`/`select_multiple`: list name is specified and exists in choices
- [ ] `relevant` formulas use `${variable_name}` syntax
- [ ] `constraint` formulas use `.` for the current field
- [ ] Column names are exact (type, name, label, list_name, etc.)
- [ ] No duplicate columns (e.g., two "audio" columns)

## Common Patterns

### Conditional Questions (Relevance)

Show a question only when a condition is met:

| type | name | label | relevant |
| --- | --- | --- | --- |
| select_one yes_no | has_children | Do you have children? | |
| integer | num_children | How many children? | ${has_children} = 'yes' |

### Cascading Selects (Choice Filter)

Filter choices based on previous answers:

| type | name | label | choice_filter |
| --- | --- | --- | --- |
| select_one countries | country | Which country? | |
| select_one cities | city | Which city? | country=${country} |

### Constraints

Limit acceptable values:

| type | name | label | constraint | constraint_message |
| --- | --- | --- | --- | --- |
| integer | age | Age? | . >= 0 and . <= 120 | Age must be between 0 and 120 |

### Calculations

Perform calculations:

| type | name | label | calculation |
| --- | --- | --- | --- |
| decimal | price | Price? | |
| decimal | tax | | ${price} * 0.18 |
| note | total | Total with tax: ${tax} | |

## Reference Documents

For detailed information, see:

- **[question-types.md](question-types.md)** - Complete list of all question types with examples
- **[syntax-guide.md](syntax-guide.md)** - XLSForm syntax rules and sheet structure
- **[validation-rules.md](validation-rules.md)** - Comprehensive validation rules and checks
- **[common-patterns.md](common-patterns.md)** - Reusable patterns for relevance, calculations, repeats, etc.

## External Resources

- [XLSForm.org](https://xlsform.org/en/) - Official XLSForm documentation
- [ODK Form Question Types](https://docs.getodk.org/form-question-types/)
- [ODK Form Logic](https://docs.getodk.org/form-logic/)
- [ODK Operators and Functions](https://docs.getodk.org/form-operators-functions/)

## Troubleshooting

### "list_name not found" Error
- Check that the list name after `select_one` or `select_multiple` exactly matches a `list_name` in the choices sheet
- Check for typos in the list name

### Duplicate Name Errors
- Every question must have a unique name
- Check the entire `name` column for duplicates
- Names are case-sensitive

### Form Not Converting
- Verify all column names are exact (case-sensitive)
- Check for mismatched begin_group/end_group or begin_repeat/end_repeat
- Ensure list_name consistency between survey and choices sheets

### Format Removed
- Use xlwings for open Excel files to preserve formatting
- Avoid operations that clear formatting when using openpyxl
- Keep a backup of the original formatted template

## Working with Commands

This skill is automatically used by these commands:

- `/xlsform-add` - Add new questions
- `/xlsform-validate` - Validate the form
- `/xlsform-import` - Import from PDF/Word/Excel
- `/xlsform-update` - Modify existing questions
- `/xlsform-remove` - Remove questions
- `/xlsform-move` - Reorder questions

These commands will automatically invoke this skill's knowledge when working with XLSForms.
