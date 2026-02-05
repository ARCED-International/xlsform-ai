# Constraint Rules

Standard constraint patterns for XLSForm question types.

## Special Response Codes

Consistent negative values for special response options (used across all forms):
- **-96**: Other (specify)
- **-99**: Don't know
- **-98**: Refused to answer

These codes should be used consistently across all choice lists.

## Pattern: age

### Type: integer
### Constraint: . >= 0 and . <= 130
### Message: Age must be between 0 and 130 years
### Required: yes
### Required Message: Age is required

**Usage:**
```xlsx
type: integer
name: age
label: What is your age?
constraint: . >= 0 and . <= 130
constraint_message: Age must be between 0 and 130 years
required: yes
required_message: Age is required
```

## Pattern: count

### Type: integer
### Constraint: . >= 0
### Message: Value must be zero or positive
### Required: yes
### Required Message: This field is required

**Usage:**
For counting people, items, occurrences.

```xlsx
type: integer
name: household_size
label: How many people live in your household?
constraint: . >= 0
constraint_message: Value must be zero or positive
required: yes
required_message: Household size is required
```

## Pattern: percentage

### Type: decimal
### Constraint: . >= 0 and . <= 100
### Message: Value must be between 0 and 100
### Required: yes
### Required Message: This field is required
### Appearance: percentages

**Usage:**
For percentage questions.

```xlsx
type: decimal
name: satisfaction_pct
label: What percentage are you satisfied?
constraint: . >= 0 and . <= 100
constraint_message: Value must be between 0 and 100
required: yes
required_message: This field is required
appearance: percentages
```

## Pattern: positive_integer

### Type: integer
### Constraint: . > 0
### Message: Value must be positive (greater than zero)
### Required: yes
### Required Message: This field is required

**Usage:**
For counts where zero is not valid.

```xlsx
type: integer
name: household_size
label: How many people live in your household? (must be at least 1)
constraint: . > 0
constraint_message: Household size must be at least 1
required: yes
required_message: Household size is required
```

## Pattern: name

### Type: text
### Constraint: regex(., '^[a-zA-Z\s\-\.']+$')
### Message: Please enter a valid name (letters only)
### Required: yes
### Required Message: Name is required

**Usage:**
For name fields (first name, last name, full name).

```xlsx
type: text
name: respondent_name
label: What is your name?
constraint: regex(., '^[a-zA-Z\s\-\.']+$')
constraint_message: Please enter a valid name (letters only, no numbers)
required: yes
required_message: Name is required
```

## Pattern: email

### Type: text
### Constraint: regex(., '^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
### Message: Please enter a valid email address
### Required: yes
### Required Message: Email is required

**Usage:**
For email fields.

```xlsx
type: text
name: email
label: What is your email address?
constraint: regex(., '^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
constraint_message: Please enter a valid email address
required: yes
required_message: Email is required
```

## Pattern: phone

### Type: text
### Constraint: regex(., '^[0-9+\-\s]+$')
### Message: Please enter a valid phone number
### Required: yes
### Required Message: Phone number is required

**Usage:**
For phone number fields.

```xlsx
type: text
name: phone
label: What is your phone number?
constraint: regex(., '^[0-9+\-\s]+$')
constraint_message: Please enter a valid phone number (digits, +, -, spaces only)
required: yes
required_message: Phone number is required
```

## Pattern: id_code

### Type: text
### Constraint: regex(., '^[a-zA-Z0-9\-]+$')
### Message: ID must contain only letters, numbers, and hyphens
### Required: yes
### Required Message: ID is required

**Usage:**
For ID fields (participant ID, household ID, etc.).

```xlsx
type: text
name: household_id
label: Enter the household ID
constraint: regex(., '^[a-zA-Z0-9\-]+$')
constraint_message: ID must contain only letters, numbers, and hyphens
required: yes
required_message: Household ID is required
```

## Pattern: decimal_positive

### Type: decimal
### Constraint: . > 0
### Message: Value must be positive
### Required: yes
### Required Message: This field is required

**Usage:**
For decimal measurements where zero is not valid.

```xlsx
type: decimal
name: weight
label: What is your weight in kg?
constraint: . > 0
constraint_message: Weight must be positive
required: yes
required_message: Weight is required
```

## Pattern: decimal_non_negative

### Type: decimal
### Constraint: . >= 0
### Message: Value must be zero or positive
### Required: yes
### Required Message: This field is required

**Usage:**
For decimal measurements where zero is valid.

```xlsx
type: decimal
name: height
label: What is your height in cm?
constraint: . >= 0
constraint_message: Height must be zero or positive
required: yes
required_message: Height is required
```

## Pattern: decimal_range_0_1

### Type: decimal
### Constraint: . >= 0 and . <= 1
### Message: Value must be between 0 and 1
### Required: yes
### Required Message: This field is required

**Usage:**
For proportions and probabilities.

```xlsx
type: decimal
name: probability
label: What is the probability? (0 to 1)
constraint: . >= 0 and . <= 1
constraint_message: Value must be between 0 and 1
required: yes
required_message: This field is required
```

## Pattern: year

### Type: integer
### Constraint: . >= 1900 and . <= 2100
### Message: Please enter a valid year
### Required: yes
### Required Message: Year is required

**Usage:**
For year fields.

```xlsx
type: integer
name: birth_year
label: What year were you born?
constraint: . >= 1900 and . <= 2100
constraint_message: Please enter a valid year (1900-2100)
required: yes
required_message: Birth year is required
```

## Pattern: month

### Type: integer
### Constraint: . >= 1 and . <= 12
### Message: Month must be between 1 and 12
### Required: yes
### Required Message: Month is required

**Usage:**
For month fields (when not using date type).

```xlsx
type: integer
name: interview_month
label: Month of interview (1-12)
constraint: . >= 1 and . <= 12
constraint_message: Month must be between 1 and 12
required: yes
required_message: Month is required
```

## Pattern: rating_1_5

### Type: integer
### Constraint: . >= 1 and . <= 5
### Message: Please select a rating from 1 to 5
### Required: yes
### Required Message: Rating is required

**Usage:**
For 5-point rating scales.

```xlsx
type: integer
name: satisfaction_rating
label: Rate your satisfaction (1=Very Dissatisfied, 5=Very Satisfied)
constraint: . >= 1 and . <= 5
constraint_message: Please select a rating from 1 to 5
required: yes
required_message: Rating is required
```

## Pattern: rating_1_10

### Type: integer
### Constraint: . >= 1 and . <= 10
### Message: Please select a rating from 1 to 10
### Required: yes
### Required Message: Rating is required

**Usage:**
For 10-point rating scales.

```xlsx
type: integer
name: nps_score
label: How likely are you to recommend us? (1-10)
constraint: . >= 1 and . <= 10
constraint_message: Please select a rating from 1 to 10
required: yes
required_message: Rating is required
```

## Pattern: text_length_limit

### Type: text
### Constraint: string-length(.) <= 250
### Message: Response must be 250 characters or less
### Required: yes
### Required Message: This field is required

**Usage:**
For text fields with character limits.

```xlsx
type: text
name: comments
label: Any comments?
constraint: string-length(.) <= 250
constraint_message: Please keep your response under 250 characters
required: no
```

## Pattern: integer_small

### Type: integer
### Constraint: . >= 0 and . <= 999
### Message: Value must be between 0 and 999
### Required: yes
### Required Message: This field is required

**Usage:**
For small counts (number of rooms, etc.).

```xlsx
type: integer
name: num_rooms
label: How many rooms?
constraint: . >= 0 and . <= 999
constraint_message: Number of rooms must be between 0 and 999
required: yes
required_message: Number of rooms is required
```
