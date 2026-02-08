# XLSForm Validation Rules

Validation checks aligned with XLSForm rules and common converter behavior.

## Structural Rules

1. Required columns exist
- survey: type, name, label
- choices: list_name, name, label

2. Column names are exact and case-sensitive
- type is not Type, choices is not Choices

3. Names are valid
- start with a letter or underscore
- allowed characters: letters, digits, hyphens, underscores, periods

4. Names are unique
- survey name values must be unique
- choices name values must be unique within each list_name

5. Naming quality checks (best practice)
- avoid leading numeric names like 1st_age
- avoid trailing numeric base names like age_3 or fruits_2
- avoid question-code prefixes like q1_ or q308_
- prefer short semantic names (target <=20 chars; hard cap <=32)

6. list_name matches
- select_one list_name and select_multiple list_name must exist in choices

7. select_multiple choice names contain no spaces

8. begin/end group and begin/end repeat are balanced and properly nested

9. Avoid large blank blocks
- data after 20 adjacent blank rows or columns may be ignored

## Formula Rules

10. relevant, constraint, calculation use correct syntax
- use ${field_name} for other fields
- use . for current field in constraints
- selected(${field}, 'value') for select_multiple

11. required and read_only are yes/no or valid formulas

12. constraint_message and required_message provided when possible

## Settings Sheet Rules (If Present)

13. Recommended fields exist
- form_title
- form_id
- version (commonly yyyymmddrr)

14. allow_choice_duplicates enabled if cascading selects require duplicate choice names

## Output Categories

- Errors: invalid types, missing required columns, duplicate names, missing choice lists, unbalanced groups
- Warnings: missing messages, suspicious formulas, large blank blocks
- Suggestions: improve naming, add labels to groups, reduce deeply nested groups
