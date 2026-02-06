# XLSForm Validation Rules

Comprehensive validation checks to ensure XLSForm quality.

## Critical Validation Rules

### 1. Unique Question Names

**Rule:** Every `name` in the survey sheet must be unique.

**Why:** Names are variable names - duplicates cause data conflicts.

**Examples:**
```
[FAIL] Bad:
| type | name | label |
| text | name | Name |
| text | name | Surname |

[OK] Good:
| type | name | label |
| text | first_name | First name |
| text | surname | Surname |
```

**Validation:**
1. Read all values in the `name` column
2. Check for duplicates (case-sensitive)
3. Report duplicates with row numbers

---

### 2. Unique Choice Names Within Lists

**Rule:** Choice `name` values must be unique within each `list_name`.

**Why:** Duplicate choice names are indistinguishable in data analysis.

**Examples:**
```
[FAIL] Bad:
| list_name | name | label |
| gender | male | Male |
| gender | male | Boy |

[OK] Good:
| list_name | name | label |
| gender | male | Male |
| gender | boy | Boy |
```

**Note:** Duplicate choice names across different lists is OK.

---

### 3. list_name Consistency

**Rule:** For `select_one` or `select_multiple`, the list name must exist in choices sheet.

**Examples:**
```
[FAIL] Bad:
Survey: select_one fruits
Choices: list_name = fruit (typo)

[OK] Good:
Survey: select_one fruits
Choices: list_name = fruits (exact match)
```

**Validation:**
1. Extract list names from all `select_one` and `select_multiple` types
2. Verify each exists as a `list_name` in choices sheet
3. Report missing choice lists

---

### 4. Valid Question Types

**Rule:** The `type` column must contain valid XLSForm types.

**Valid Types:**
- Text: `text`, `integer`, `decimal`, `note`
- Select: `select_one`, `select_multiple`, `select_one_from_file`, `select_multiple_from_file`
- Date/Time: `date`, `time`, `dateTime`
- Geo: `geopoint`, `geotrace`, `geoshape`
- Media: `image`, `audio`, `video`, `file`
- Metadata: `start`, `end`, `today`, `deviceid`, `username`, `email`, `audit`, `phonenumber`
- Special: `calculate`, `hidden`, `rank`, `acknowledge`, `barcode`
- Structure: `begin group`, `end group`, `begin repeat`, `end repeat`

**Validation:**
1. Check each type value
2. Report invalid types
3. Suggest corrections for common typos (e.g., `selct_one` → `select_one`)

---

### 5. No Spaces in select_multiple Choice Names

**Rule:** Choice names for `select_multiple` questions must not contain spaces.

**Why:** Selected choices are saved as space-separated values.

**Examples:**
```
[FAIL] Bad:
| list_name | name | label |
| toppings | choice 1 | Cheese |
| toppings | choice 2 | Pepperoni |

[OK] Good:
| list_name | name | label |
| toppings | choice_1 | Cheese |
| toppings | choice_2 | Pepperoni |
```

**Note:** This rule doesn't apply to `select_one`, but it's good practice to avoid spaces in all cases.

---

### 6. Valid Name Syntax

**Rule:** Question names must:
- Start with a letter or underscore
- Contain only: letters, digits, hyphens, underscores, periods
- Be case-sensitive

**Examples:**
```
[FAIL] Invalid:
- 1st_question (starts with digit)
- respondent name (contains space)
- @username (contains @)

[OK] Valid:
- first_question
- _internal
- question-1
- respondent_name
```

---

### 7. Balanced Groups and Repeats

**Rule:** Every `begin group` must have a matching `end group`. Same for repeats.

**Validation:**
1. Track nesting depth
2. Ensure all opened structures are closed
3. Verify proper nesting (can't close outer before inner)

**Examples:**
```
[FAIL] Bad:
begin group A
begin group B
end group A
end group B

[OK] Good:
begin group A
begin group B
end group B
end group A
```

---

### 8. Required Columns Present

**Rule:** Survey sheet must have: `type`, `name`, `label`
**Rule:** Choices sheet must have: `list_name`, `name`, `label`

**Validation:**
1. Check first row for required column names
2. Report missing required columns

---

### 9. No Duplicate Columns

**Rule:** Column names must be unique.

**Why:** Duplicate columns cause ambiguity and errors.

**Example:**
```
[FAIL] Bad:
| type | name | label | audio | audio |
```

---

### 10. Formula Syntax

**Rule:** Formulas in `relevant`, `constraint`, `calculation` must use correct syntax.

**Common Errors:**

**Missing field reference syntax:**
```
[FAIL] Bad: age >= 18
[OK] Good: ${age} >= 18
```

**Wrong current field reference:**
```
[FAIL] In constraint: age >= 18
[OK] In constraint: . >= 18
```

**Mismatched quotes/brackets:**
```
[FAIL] ${country = 'USA'
[OK] ${country} = 'USA'
```

---

## Structural Validation

### 11. Label for begin group

**Rule:** `begin group` and `begin repeat` should have a label.

**Why:** Labels help users understand the form structure.

**Best Practice:**
```
[OK] Good:
| type | name | label |
| begin group | demographics | Demographic Information |

[WARNING] Acceptable but not recommended:
| type | name | label |
| begin group | demographics | |
```

---

### 12. repeat_count Format

**Rule:** `repeat_count` must be a number or a valid formula.

**Valid:**
- `3` (fixed number)
- `${num_children}` (dynamic)
- `count(${household_members})` (calculation)

---

### 13. Settings Sheet Form ID

**Rule:** If `form_id` is provided, it should be:
- URL-friendly (no spaces)
- Unique
- Descriptive

**Examples:**
```
[FAIL] Bad: My Form 2024
[OK] Good: my_form_2024
```

---

## Content Quality Checks

### 14. Constraint Messages

**Best Practice:** When `constraint` is used, provide `constraint_message`.

**Why:** Users need to know why their input was rejected.

**Examples:**
```
[WARNING] Missing:
| constraint |
| . >= 18 |

[OK] Complete:
| constraint | constraint_message |
| . >= 18 | Must be 18 or older |
```

---

### 15. Required Messages

**Best Practice:** When `required = yes`, provide `required_message`.

**Examples:**
```
[WARNING] Missing:
| required |
| yes |

[OK] Complete:
| required | required_message |
| yes | This field is required |
```

---

### 16. Relevant for select_other

**Rule:** If using manual "other" pattern (not `or_other`), add relevance for the text field.

**Example:**
```
[OK] Good:
| type | name | label | relevant |
| select_multiple toppings | favorite | Favorite toppings | |
| text | other_text | Other | selected(${favorite}, 'other') |

Choices sheet must include:
| list_name | name | label |
| toppings | other | Other |
```

---

## Advanced Validation

### 17. Calculation Type Consistency

**Rule:** If the calculation result type matters (date, number), set the type accordingly.

**Examples:**
```
[FAIL] May cause issues:
| type | name | calculation |
| text | today | today() |

[OK] Better:
| type | name | calculation |
| date | today | today() |
```

---

### 18. choice_filter Column Exists

**Rule:** If using `choice_filter`, ensure the filtered field exists.

**Validation:**
1. Parse choice_filter formulas
2. Verify referenced fields exist in survey
3. Check that field types are compatible

---

### 19. Parameters Column Format

**Rule:** Parameters must be space-separated `key=value` pairs.

**Valid:**
```
capture-accuracy=10 warning-accuracy=10
start=0 end=10 step=1
randomize=true
```

---

### 20. External File References

**Rule:** For `select_one_from_file` and `csv-external`, the referenced file must:
- Exist as a form attachment
- Have correct format (CSV, XML, or GeoJSON)
- Have required columns

**Validation:** Check file references if possible, or warn user to verify.

---

## Auto-Fix Suggestions

### Fix Duplicate Names
Suggest unique names by adding suffix:
```
name → name_1, name_2, etc.
```

### Fix list_name Typos
Suggest matching list_name from choices:
```
select_one frut → select_one fruits
```

### Fix Type Typos
Suggest corrections:
```
selct_one → select_one
interger → integer
```

### Fix Constraint Syntax
Add missing syntax:
```
age >= 18 → ${age} >= 18
```

---

## Validation Output Format

Present validation results in three categories:

### Errors
Critical issues that prevent form conversion:
- Duplicate names
- Invalid types
- Missing choice lists
- Unbalanced groups/repeats

### Warnings
Issues that may cause problems:
- Missing constraint messages
- Missing required messages
- Suspicious formulas

### Suggestions
Improvements for best practices:
- Add labels to begin group
- Use snake_case for names
- Add helpful hints

---

## Validation Command Pattern

```bash
# Validate current form
/xlsform-validate

# Validate with auto-fix suggestions
/xlsform-validate --fix

# Validate specific file
/xlsform-validate path/to/form.xlsx
```

---

## Testing Checklist

After validation, test the form:

- [ ] Form converts successfully to XForm
- [ ] All questions appear correctly
- [ ] Choice lists display properly
- [ ] Relevance works as expected
- [ ] Constraints enforce correct values
- [ ] Repeats can be added/removed
- [ ] Form can be filled completely
- [ ] Data exports correctly
