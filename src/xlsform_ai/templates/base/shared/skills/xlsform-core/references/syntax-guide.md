# XLSForm Syntax Guide

Complete guide to XLSForm syntax and structure.

## Sheet Structure

An XLSForm workbook has three main sheets:

1. **survey** - Contains all questions and form structure
2. **choices** - Defines answer options for select questions
3. **settings** - Form metadata and configuration

## Survey Sheet

### Required Columns

| Column | Description | Rules |
| --- | --- | --- |
| **type** | Question type | Must be valid XLSForm type (e.g., text, select_one) |
| **name** | Unique variable name | Must be unique, start with letter/underscore, snake_case recommended |
| **label** | Question text | What the user sees |

### Common Optional Columns

| Column | Description | Example |
| --- | --- | --- |
| **hint** | Helper text | Look on the signboard |
| **guidance_hint** | Training/paper hint | Shown only in special views |
| **relevant** | Conditional display | ${previous_question} = 'yes' |
| **constraint** | Value restriction | . >= 0 and . <= 120 |
| **constraint_message** | Error message | Age must be 0-120 |
| **required** | Required field | yes |
| **required_message** | Required error | This field is required |
| **default** | Pre-filled value | today() |
| **calculation** | Computed value | ${price} * 1.18 |
| **trigger** | When to recalculate | ${price} |
| **appearance** | Display style | multiline, compact, etc. |
| **parameters** | Type-specific config | start=0 end=10 step=1 |
| **repeat_count** | Number of repeats | 3 or ${num_children} |

### Column Naming Rules

1. **Case-sensitive:** `type`, `Type`, and `TYPE` are different
2. **Exact spelling:** `Choices` or `choice` will NOT work - must be `choices`
3. **No spaces in column names:** Use underscores (e.g., `constraint_message`)
4. **Optional columns can be omitted** if not needed

## Metadata Question Types

Standard metadata types (auto-captured; labels should still be included for readability):
`start`, `end`, `today`, `deviceid`, `phonenumber`, `username`, `email`, `audit`

Notes:
- Always include labels; metadata is still auto-captured.
- Metadata rows typically appear near the top of the survey but can be placed anywhere.
- Audit logging with location tracking is supported in ODK Collect, not Enketo webforms.
- To capture a specific location (e.g., a store GPS), add a normal `geopoint` question with a label.

## Choices Sheet

### Required Columns

| Column | Description | Rules |
| --- | --- | --- |
| **list_name** | Group identifier for choices | Links to select_one/select_multiple type |
| **name** | Choice value name | Unique within list_name |
| **label** | Choice display text | What user sees |

### Common Optional Columns

| Column | Description | Example |
| --- | --- | --- |
| **image** | Associated image file | choice1.png |
| **audio** | Associated audio file | choice1.wav |
| **video** | Associated video file | choice1.mp4 |

### list_name Rules

- The `list_name` must match the list name in the survey sheet's type column
- Example: `select_one fruits` requires choices with `list_name = fruits`
- Multiple questions can use the same `list_name` (reusable choice lists)

## Settings Sheet

### Common Settings Columns

| Column | Description | Example |
| --- | --- | --- |
| **form_title** | Form display title | Household Survey |
| **form_id** | Unique form identifier | household_survey_v1 |
| **version** | Form version string | 2024121501 |
| **instance_name** | Submission naming | concat(${first_name}, ' ', ${last_name}) |
| **default_language** | Default language | English (en) |
| **public_key** | Encryption key | (base64 RSA key) |
| **submission_url** | Alternate submission URL | https://example.com/submit |
| **style** | Form style | pages, theme-grid |

**Strict settings layout:** Row 1 contains headers, Row 2 contains values in the same columns. Never assume column positions; always map headers before writing.
**Version requirement:** `version` must be the formula `=TEXT(NOW(), "yyyymmddhhmmss")`.

## Naming Conventions

### Question Names (survey sheet `name` column)

**Rules:**
1. Must start with a letter or underscore
2. Can contain: letters, digits, hyphens, underscores, periods
3. Case-sensitive (Name and name are different)
4. Must be **unique** within the form

**Recommended:** snake_case
```
Good: respondent_name, household_size, _internal
Bad: Respondent Name, 1st_question, respondent-name (use underscore)
```

### Choice Names (choices sheet `name` column)

**Rules:**
1. For `select_one`: can contain spaces
2. For `select_multiple`: must NOT contain spaces
3. Must be unique within a single `list_name`

**Recommended:** Avoid spaces in all cases (easier to convert to select_multiple later)
```
Good: yes, no, option_a, option_1
Bad for select_multiple: choice 1, option B (has spaces)
```

### list_name

**Rules:**
1. Matches list name in type column to choices sheet
2. Case-sensitive
3. Can contain letters, digits, underscores

## Formula Syntax

### Referencing Fields

Use `${field_name}` to reference other fields:
```
${age} >= 18
${total_price} * 0.18
${country} = 'USA'
```

### Current Field Reference

Use `.` to reference the current field (mostly in constraints):
```
. >= 0 and . <= 120
. != ''
```

### Operators

**Comparison:** `=`, `!=`, `<`, `>`, `<=`, `>=`
**Logical:** `and`, `or`
**Arithmetic:** `+`, `-`, `*`, `div`, `mod`
**String:** `starts-with()`, `contains()`, `substr()`

### Functions

Common functions:
```
today() - Current date
now() - Current date/time
count() - Count items in repeat
selected() - Check if choice selected (for select_multiple)
concat() - Join strings
round() - Round numbers
int() - Convert to integer
number() - Convert to number
string() - Convert to string
```

## Sheet Structure Rules

### Row Order

- Rows are processed top to bottom
- You can leave blank rows for readability (but not >20 consecutive blank rows)
- Group/repeat structures must be properly nested

### begin group / end group

```
begin group
  ...questions...
end group
```

- `begin group` has name and label
- `end group` has empty name and label
- Groups can be nested

### begin repeat / end repeat

```
begin repeat
  ...questions...
end repeat
```

- `begin repeat` has name (and optional label)
- `end repeat` has empty name and label
- Repeats can contain groups

### Nesting Rules

Groups and repeats can be nested:
```
begin repeat household
  begin group member
    ...questions...
  end group
end repeat
```

**Always** close the most recent structure first:
```
[OK] Correct:
begin repeat
  begin group
  end group
end repeat

✗ Wrong:
begin repeat
  begin group
end repeat
  end group
```

## Language Translations

Add translations using `::language_code` suffix:

| type | name | label::English | label::Français |
| --- | --- | --- | --- |
| text | name | Name | Nom |

**Settings sheet:**
| form_title | default_language |
| --- | --- |
| My Form | English (en) |

**Media can also be translated:**
| image::English | image::Français |
| --- | --- |
| en.png | fr.png |

## Appearance Column Values

### For select questions
- `minimal` - Dropdown menu
- `compact` - Compact display
- `horizontal` - Horizontal layout
- `quick` - Auto-advance after selection

### For text questions
- `multiline` - Multi-line input
- `newlines` - Preserve line breaks

### For date questions
- `no-calendar` - Suppress calendar
- `month-year` - Month and year only
- `year` - Year only

### For groups
- `field-list` - All questions on one screen

## Common Pitfalls

### 1. Column Name Typos
```
[FAIL] Choices, choice, Type, Name
[OK] choices, type, name
```

### 2. list_name Mismatch
```
[FAIL] Survey: select_one fruit
   Choices: list_name = fruits

[OK] Survey: select_one fruits
   Choices: list_name = fruits
```

### 3. Duplicate Names
```
[FAIL] Multiple questions with name = "question1"
[OK] Each question has unique name
```

### 4. Invalid Name Characters
```
[FAIL] name starts with digit: 1st_question
[FAIL] name has spaces: respondent name
[OK] name: first_question, respondent_name
```

### 5. Spaces in select_multiple Choice Names
```
[FAIL] select_multiple with choice name = "choice 1"
[OK] choice name = "choice_1" or "choice1"
```

### 6. Unmatched begin/end
```
[FAIL] begin group without end group
[FAIL] Nested groups closed in wrong order
[OK] Every begin has matching end, properly nested
```

### 7. Formula Syntax Errors
```
[FAIL] ${age > 18} (missing closing brace)
[FAIL] age >= 18 (missing ${)
[OK] ${age} >= 18
```

## Formatting Notes

- **Cell formatting is ignored** by XLSForm converters
- Use formatting (bold, colors, borders) for human readability
- Background colors beyond column 20 are not processed
- Merged cells should be avoided
- Keep data in the first ~20 columns and ~1000 rows for safety

## Validation Checklist

Before finalizing:

- [ ] All column names are exact and correctly spelled
- [ ] All question names are unique
- [ ] All choice names are unique within their list
- [ ] list_name matches between survey and choices
- [ ] All begin_group/end_group pairs match
- [ ] All begin_repeat/end_repeat pairs match
- [ ] Formulas use correct syntax (${field_name})
- [ ] Constraints use `.` for current field
- [ ] No spaces in select_multiple choice names
- [ ] Names start with letter or underscore
