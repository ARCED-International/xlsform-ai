# DIME Analytics SurveyCTO Style Guide

Best practices from the DIME Analytics SurveyCTO Style Guide for XLSForm programming. While drafted using SurveyCTO, these practices apply to all ODK-based platforms.

## Design and Development

### Color Coding of Rows

Conditional color coding based on field type makes forms easier to review:

- **Integer questions:** Blue
- **Decimal questions:** Green
- **Text questions:** Yellow
- **Select questions:** Orange
- **Calculate fields:** Gray
- **begin_/end_ fields:** Purple

### Use White Space

Add blank rows between modules for visual separation:

```xlsx
[End of Demographics section]

[blank row]

[Start of Income section]
```

This makes large forms easier to navigate.

### Pre-defined Formula for Form Version

Use automatic versioning:

```xlsx
version: =TEXT(YEAR(NOW())-2000, "00") & TEXT(MONTH(NOW()), "00") & TEXT(DAY(NOW()), "00") & TEXT(HOUR(NOW()), "00") & TEXT(MINUTE(NOW()), "00")
```

This ensures versions are always lexically increasing.

### Matching Names for begin and end Groups

Always name both begin and end groups:

```xlsx
type: begin group
name: household_roster
label: Household Roster

[questions...]

type: end group
name: household_roster
```

This makes it easier to identify groups in complex forms.

## Variable Naming Conventions

### Structure: module_varname_add

Use this 3-part structure:

- **module:** Abbreviated module prefix (e.g., hh_ for household)
- **varname:** Descriptive variable name
- **add:** Additional info (optional)

**Examples:**
- `hh_head_age` (household head age)
- `crop_type_main` (main crop type)
- `income_total` (total income)

### Rules

1. Use only lowercase letters (a-z), digits (0-9), and underscores (_)
2. Always start with a letter
3. Maximum 32 characters (for Stata compatibility)
4. Be descriptive but concise

## User Interface

### Loading Choice-Labels

When questions refer to previous choices, use calculate fields to load labels:

**Without label loading:**
```xlsx
type: select_one crops
name: crop_name
label: Primary crop

type: decimal
name: crop_area
label: How much area is cultivated under 5?
```

**With label loading:**
```xlsx
type: select_one crops
name: crop_name
label: Primary crop

type: calculate
name: crop_label
calculation: jr:choice-name(${crop_name})

type: decimal
name: crop_area
label: How much area is cultivated under ${crop_label}?
```

## Exported Form Dataset

### Numeric Values in Choices

Always use numeric values for choices:

**Recommended:**
```
list_name: gender
name: 1
label: Male

name: 2
label: Female
```

**Not Recommended:**
```
list_name: gender
name: male
label: Male

name: female
label: Female
```

### Standardized Negative Values

Use consistent negative codes (standard across all forms):

- **-96**: Other (specify)
- **-99**: Don't know
- **-98**: Refuse to answer

Apply this consistently across all choice lists with these options.

## Question Type Best Practices

### Age Questions

```xlsx
type: integer
name: age
label: What is your age?
constraint: . >= 0 and . <= 120
constraint_message: Age must be between 0 and 120
required: yes
```

### Name Questions

```xlsx
type: text
name: respondent_name
label: What is your name?
constraint: regex(., '^[a-zA-Z\\s\\-\\.\']+$')
constraint_message: Please enter a valid name (letters only)
required: yes
```

### Percentage Questions

```xlsx
type: decimal
name: satisfaction_pct
label: Satisfaction percentage
constraint: . >= 0 and . <= 100
constraint_message: Value must be between 0 and 100
appearance: percentages
required: yes
```

### Count Questions

```xlsx
type: integer
name: household_size
label: How many people live in your household?
constraint: . >= 1
constraint_message: Household size must be at least 1
required: yes
```

## Relevance and Skip Patterns

### Clear Conditional Logic

Use relevance for skip patterns:

```xlsx
type: select_one yes_no
name: employed
label: Are you employed?
required: yes

type: text
name: occupation
label: What is your occupation?
relevant: ${employed} = '1'
required: yes
```

### Test Skip Patterns

Always test skip patterns thoroughly:
- Verify all paths work
- Check edge cases
- Test with enumerator feedback

## Constraints

### Provide Clear Error Messages

Always include constraint_message:

```xlsx
constraint: . >= 0 and . <= 130
constraint_message: Age must be between 0 and 130 years
```

### Use Appropriate Constraints

Don't over-constrain:
- Age: 0-130 is reasonable
- Height: 0-300 cm is reasonable
- Percentage: 0-100 is required

## Calculations

### Use Calculate for Derived Values

```xlsx
type: calculate
name: total_income
label: Total Income
calculation: ${income_wage} + ${income_self_employment} + ${income_other}
```

### Round Decimal Calculations

```xlsx
type: calculate
name: avg_income
label: Average Income
calculation: round(${total_income} / ${household_size}, 2)
```

## Form Structure

### Organize by Module

Group questions logically:

1. **Introduction** and consent
2. **Demographics**
3. **Main topic questions**
4. **Conclusion** and thank you

### Use Field Lists for Long Forms

For forms with many questions, use field lists:

```xlsx
type: fieldlist
name: demographics_list
label: Demographics
appearance: field-list
```

This reduces scrolling on mobile devices.

## Data Quality

### Required Fields

Make all fields required by default (except notes and calculates):

```xlsx
required: yes
required_message: This field is required
```

### Consistency Checks

Add calculate fields for consistency:

```xlsx
type: calculate
name: total_members_check
calculation: if(${total_members} = count(${household_member}), 'OK', 'CHECK')
```

## Testing

### Test Thoroughly

1. **Pre-load testing:** Test with sample data
2. **Field testing:** Test with real enumerators
3. **Back-check:** Verify data quality

### Use Test Questions

Add practice/real question for testing:

```xlsx
type: select_one test
name: test_question
label: Is this a test submission?
choices: 1=Yes, 2=No
```

This allows filtering test data from production data.
