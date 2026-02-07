# ODK Form Best Practices

This document contains best practices from the official ODK documentation for creating high-quality XLSForms.

## Field Naming Conventions

### Use snake_case for field names
- Always use lowercase letters
- Separate words with underscores
- Start with a letter (not a number)
- Avoid ending names with numeric suffixes (e.g., avoid `age_3`, `fruits_1`)
- Be descriptive but concise
- Use semantic variants instead of numbers (`age_child`, `age_spouse`)
- Reason: repeat exports and select_multiple exports commonly generate `_1`, `_2`, etc.

**Good examples:**
- `respondent_age`
- `household_income`
- `crop_type`

**Bad examples:**
- `RespondentAge` (camelCase)
- `respondent-age` (hyphens)
- `1st_question` (starts with number)
- `age_3` (looks like repeat/export-generated field)
- `fruits_1` (collides with select_multiple export pattern)

### Field name length
- Keep under 32 characters for Stata compatibility
- Make names meaningful but not excessively long

## Constraints and Validation

### Age Fields
- **Type:** integer
- **Constraint:** `. >= 0 and . <= 130`
- **Constraint Message:** Age must be between 0 and 130 years
- **Required:** yes (unless explicitly optional)

### Name Fields
- **Type:** text
- **Constraint:** `regex(., '^[a-zA-Z\s\-\.']+$')`
- **Constraint Message:** Please enter a valid name (letters only)
- **Required:** yes

### Percentage Fields
- **Type:** decimal
- **Constraint:** `. >= 0 and . <= 100`
- **Constraint Message:** Percentage must be between 0 and 100
- **Appearance:** percentages

### Integer Count Fields
- **Type:** integer
- **Constraint:** `. >= 0`
- **Constraint Message:** Value must be zero or positive
- **Required:** yes

### Decimal Amount Fields
- **Type:** decimal
- **Constraint:** `. > 0`
- **Constraint Message:** Value must be positive
- **Required:** yes

### Email Fields
- **Type:** text
- **Constraint:** `regex(., '^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$')`
- **Constraint Message:** Please enter a valid email address

### Phone Fields
- **Type:** text
- **Constraint:** `regex(., '^[0-9+\\-\\s]+$')`
- **Constraint Message:** Please enter a valid phone number

### ID Fields
- **Type:** text
- **Constraint:** `regex(., '^[a-zA-Z0-9\\-]+$')`
- **Constraint Message:** ID must contain only letters, numbers, and hyphens

## Choice Lists Best Practices

### Always Use Numeric Choice Values

Numeric codes are easier to work with in analysis tools like R, Stata, and SPSS.

**Good:**
```
list_name | name | label
gender | 1 | Male
gender | 2 | Female
gender | 3 | Other
```

**Bad:**
```
list_name | name | label
gender | male | Male
gender | female | Female
gender | other | Other
```

### Standardize Negative Values

Use standardized negative values for special response options (consistent across all forms):

- **-96**: Other (specify)
- **-99**: Don't know
- **-98**: Refuse to answer

This consistency makes data cleaning easier and is standard practice in survey research.

### Reuse Common Choice Lists

Don't recreate the same lists. Use standard lists:

- **yes_no**: Yes/No questions
- **gender**: Male, Female, Other, Prefer not to say
- **agreement**: Strongly agree, Agree, Neutral, Disagree, Strongly disagree
- **frequency**: Always, Often, Sometimes, Rarely, Never

### Cascading Selects

Use `choice_filter` for cascading selects:

```xlsx
type: select_one country
name: country
label: Select country

type: select_one region
name: region
label: Select region
choice_filter: country=${country}
```

## Relevance and Skip Logic

### Use Field References

Use `${field_name}` to reference other fields:

```xlsx
type: text
name: spouse_name
label: Spouse's name
relevant: ${marital_status} = '2'
```

### Test Complex Logic

Complex relevance logic should be thoroughly tested:

```xlsx
relevant: ${age} >= 18 and ${consent} = 'yes'
```

## Required Fields

### Make Most Fields Required

By default, make fields required to ensure complete data collection:

```xlsx
required: yes
required_message: This field is required
```

### Exceptions

Don't require these field types:
- **calculate** (computed values)
- **hidden** (internal values)
- **note** (display only)
- **metadata** (start, end, today, deviceid, etc.)

## User Interface

### Guidance Text

Use the `hint` field to provide guidance:

```xlsx
label: What is your age?
hint: Enter age in complete years
```

### Field Notes

Use the `guidance` field for detailed instructions (not in label):

```xlsx
label: Household income
guidance: Include income from all sources. Enter 0 if none.
```

### Appearance Settings

Use appearance to improve user experience:

- **numbers**: Show numeric keypad
- **compact**: Show choices in compact view
- **quick**: Show as quick buttons
- **multiline**: Multi-line text input

## Form Structure

### Use Groups for Organization

Group related questions:

```xlsx
type: begin group
name: demographics
label: Demographics

type: text
name: name
label: Name

type: integer
name: age
label: Age

type: end group
name: demographics
```

### Use Repeats for Dynamic Lists

Use `begin repeat` / `end repeat` for repeated items:

```xlsx
type: begin repeat
name: household_member
label: Household Member

type: text
name: member_name
label: Name

type: integer
name: member_age
label: Age

type: end repeat
```

### Name begin and end Groups

Always name both begin and end groups for easier debugging:

```xlsx
type: begin group
name: section1
...

type: end group
name: section1
```

## Metadata Fields

### Standard Metadata

Include these metadata fields in every form:

```xlsx
type: start
name: start
label: Start Time

type: end
name: end
label: End Time

type: today
name: today
label: Date

type: deviceid
name: deviceid
label: Device ID
```

### Form Duration

Calculate form duration:

```xlsx
type: calculate
name: form_duration_minutes
label: Form Duration (minutes)
calculation: round((decimal-time-end() - decimal-time-start()) * 1440)
```

## Repeat Best Practices

### Set Max Limits

Use constraints to limit repeats:

```xlsx
type: begin repeat
name: household_member
label: Household Member
count: ${member_count}

type: end repeat
name: household_member
```

### Count Repeats

Use count() to track repeats:

```xlsx
type: calculate
name: total_members
label: Total Members
calculation: count(${household_member})
```

## Validation

### Always Validate Forms

Use XLSForm validation tools:
- ODK Build
- XLSForm Offline
- pyxform

### Test on Devices

Always test on actual devices:
- Android phones/tablets
- Different screen sizes
- Different ODK Collect versions

## Performance

### Optimize Large Forms

For forms with 100+ questions:
- Use field lists to reduce scrolling
- Minimize complex relevance
- Test performance regularly

### External Choice Lists

For very large choice lists (100+ options):
- Use external selects: `select_one_from_file`
- Improves form loading time

## Security

### Don't Collect Sensitive Data Unnecessarily

- Avoid collecting full ID numbers
- Use partial identifiers when possible
- Consider privacy implications

### Encrypted Forms

Use encrypted forms for sensitive data:
- Set up server encryption
- Use ODK Collect's encryption feature
