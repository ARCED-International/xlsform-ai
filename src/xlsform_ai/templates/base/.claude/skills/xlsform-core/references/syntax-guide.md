# XLSForm Syntax Guide

Concise syntax and structure rules aligned with the XLSForm documentation at xlsform.org.

## Sheet Structure

An XLSForm workbook has three main sheets:

1. survey - Contains all questions and form structure
2. choices - Defines answer options for select questions
3. settings - Form metadata and configuration

### Column Order and Blank Rows

- Columns can appear in any order.
- Optional columns can be omitted.
- Data after 20 adjacent blank columns or rows may be ignored by converters.

Keep data contiguous and avoid large blank blocks inside the sheet.

## Survey Sheet

### Required Columns

| Column | Description | Rules |
| --- | --- | --- |
| type | Question type | Must be a valid XLSForm type (text, select_one, etc.) |
| name | Variable name | Unique, starts with a letter or underscore |
| label | Question text | What the user sees |

### Common Optional Columns

| Column | Purpose | Example |
| --- | --- | --- |
| hint | Helper text | Look at the signboard |
| guidance_hint | Training or paper hint | Only shown in special views |
| relevant | Conditional display | ${has_children} = 'yes' |
| required | Required field | yes or ${age} >= 18 |
| required_message | Required error | This field is required |
| constraint | Value restriction | . >= 0 and . <= 120 |
| constraint_message | Constraint error | Age must be 0-120 |
| calculation | Computed value | ${price} * 1.18 |
| trigger | Recalculate when | ${price} |
| read_only | Read-only field | yes or ${role} = 'viewer' |
| default | Pre-filled value | today() |
| appearance | Display style | minimal, field-list, etc. |
| parameters | Type parameters | start=0 end=10 step=1 |
| choice_filter | Cascading select | country=${country} |
| repeat_count | Repeat count | 3 or ${num_children} |

### Formula Syntax

- Reference other fields with ${field_name}.
- Use . to reference the current field in constraints.
- Use selected(${field}, 'choice') for select_multiple conditions.

### Naming Rules (survey sheet name)

- Must start with a letter or underscore.
- Must be short but meaningful (default target <=20, hard cap <=32).
- Allowed characters: letters, digits, hyphens, underscores, periods.
- Case-sensitive.
- Must be unique within the form.
- Recommended: avoid leading numbers and trailing numeric suffixes in base names.
- Recommended: avoid question-code prefixes like `q1_` or `q308_`.

## Choices Sheet

### Required Columns

| Column | Description | Rules |
| --- | --- | --- |
| list_name | Choice list ID | Must match list name in survey type |
| name | Choice value | Unique within list_name |
| label | Choice text | What the user sees |

### Choice Name Rules

- For select_multiple, choice names must not contain spaces.
- Duplicate choice names are normally invalid. If you need duplicates for cascading selects, set allow_choice_duplicates in the settings sheet.

### list_name Consistency

- A type like select_one fruits requires choices with list_name = fruits.
- Multiple questions can reuse the same list_name.

## Settings Sheet

The settings sheet is optional but recommended. If present, include at least:

- form_title
- form_id
- version (common convention: yyyymmddrr)

Other common settings:
- default_language
- public_key
- submission_url
- style
- name
- allow_choice_duplicates

### Settings Layout (Project Standard)

- Row 1 contains headers.
- Row 2 contains values aligned to the headers.
- Read headers before writing values. Do not assume fixed column positions.

## External Choices

For large choice lists, use select_one_from_file or select_multiple_from_file.

In the parameters column you can specify the columns for values and labels:
- value=code
- label=name

## Translations

Add translations by appending ::language_code to label or hint columns:

| type | name | label::en | label::es |
| --- | --- | --- | --- |
| text | name | Name | Nombre |

Set default_language in settings (for example: English (en)).

## or_other Limitations

The or_other modifier is only supported for select_one or select_multiple when:
- There are no label translations.
- There is no choice_filter.

It uses the English label "Specify other".

## Groups and Repeats

- begin group / end group define groups.
- begin repeat / end repeat define repeats.
- Nesting must be properly balanced.
- repeat_count can be a number or a formula.

## Validation Checklist

- Required columns exist in survey and choices.
- All question names are unique and valid.
- list_name matches between survey and choices.
- select_multiple choice names do not contain spaces.
- begin/end group and begin/end repeat are balanced.
- Formulas use ${field_name} and . correctly.
- No large blank blocks (20+ adjacent blank rows or columns).
