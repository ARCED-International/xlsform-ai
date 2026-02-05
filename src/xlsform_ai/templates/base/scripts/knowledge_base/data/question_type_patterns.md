# Question Type Patterns

Common patterns for detecting XLSForm question types from natural language.

## Integer Question Patterns

### Keywords Indicating Integer Type

**Age and Time:**
- age, how old, years old
- years, months, weeks, days
- duration, period, frequency

**Counts and Numbers:**
- count, number, how many, how much
- children, members, household size
- times, frequency, occurrences
- quantity, amount (when discrete)

**Ratings:**
- rate, scale, score
- rating from 1 to 10
- level from 1 to 5

**Examples:**
- "What is your age?" → integer
- "How many children do you have?" → integer
- "How many times per week?" → integer
- "Rate your satisfaction from 1-10" → integer

## Decimal Question Patterns

### Keywords Indicating Decimal Type

**Measurements:**
- weight, height, length
- distance, area, volume
- size, measurement

**Money and Income:**
- price, cost, income
- salary, wage, payment
- amount, revenue, budget

**Rates and Percentages:**
- percentage, percent, rate
- proportion, ratio
- probability, likelihood

**Physical Quantities:**
- temperature
- pressure
- speed, velocity

**Examples:**
- "What is your weight in kg?" → decimal
- "What is the price?" → decimal
- "Enter temperature" → decimal
- "What percentage?" → decimal

## Text Question Patterns

### Keywords Indicating Text Type

**Names:**
- name, first name, last name
- full name, given name
- respondent name

**Addresses and Locations:**
- address, street, city
- village, town, district
- location description

**Descriptions:**
- describe, description
- explain, explanation
- comments, remarks, notes
- specify, clarification
- details, information

**Open-ended:**
- other specify
- any other (text)
- please specify
- in your own words

**Examples:**
- "What is your name?" → text
- "Describe your main activity" → text
- "Any other comments?" → text
- "Please specify" → text

## Select One Question Patterns

### Keywords Indicating Select One

**Single Choice:**
- select one, choose one
- which one, pick one
- radio button
- single choice

**Mutually Exclusive Options:**
- which [category]
- what type of
- what kind of

**Examples:**
- "What is your gender?" → select_one (with male/female/other)
- "Which crop do you grow?" → select_one
- "Select your education level" → select_one

## Select Multiple Question Patterns

### Keywords Indicating Select Multiple

**Multiple Selection:**
- select all that apply
- check all that apply
- multiple choice
- checkbox
- choose all options

**Plural Indicators:**
- which [plural noun]
- what types of
- select all sources

**Examples:**
- "Select all sources of income" → select_multiple
- "Check all crops grown" → select_multiple
- "Which methods do you use?" → select_multiple

## Date Question Patterns

### Keywords Indicating Date Type

**Time References:**
- date, date of birth
- when, what date
- birthday, birth date
- start date, end date

**Examples:**
- "What is your date of birth?" → date
- "When did you start working?" → date
- "Date of purchase" → date

## Geopoint Question Patterns

### Keywords Indicating Geopoint Type

**Location References:**
- location, GPS, coordinates
- where, place
- latitude, longitude
- map, plot

**Examples:**
- "Record your GPS location" → geopoint
- "What are the coordinates?" → geopoint
- "Locate the plot" → geopoint

## Image Question Patterns

### Keywords Indicating Image Type

**Visual References:**
- photo, photograph, picture
- image, take a photo
- scan, capture

**Examples:**
- "Take a photo of the document" → image
- "Photograph the product" → image
- "Scan the ID card" → image

## Yes/No Question Patterns

### Keywords Indicating Yes/No

**Binary Questions:**
- yes or no, do you
- did you, have you
- will you, can you
- is it, are you

**Examples:**
- "Do you own a phone?" → select_one yes_no
- "Have you attended school?" → select_one yes_no
- "Are you employed?" → select_one yes_no

## Agreements/Ratings Question Patterns

### Likert Scale Items

**Agreement:**
- agree, disagree
- strongly agree, strongly disagree
- satisfied, dissatisfied

**Frequency:**
- always, often, sometimes
- rarely, never

**Examples:**
- "I am satisfied with the service" → select_one agreement
- "How often do you visit?" → select_one frequency

## Numeric Preference Guidelines

### Prefer Numeric for Analysis

**Primary preference:** select_one/select_multiple with numeric codes
- Enables quantitative analysis
- Easier to work with in Stata/R/SPSS
- Consistent with DIME guidelines

**Secondary preference:** integer or decimal
- Use when no discrete options
- Provides quantitative data
- Better than text for analysis

**Text as last resort:** Only when clearly text-only
- Names, addresses
- Open-ended descriptions
- "Other specify" fields

### Decision Tree

```
Question presented
    ↓
Are there discrete options?
    YES → select_one/select_multiple (numeric codes: 1, 2, 3...)
    NO
    ↓
Is it a measurement/count/quantity?
    YES → integer or decimal
    NO
    ↓
Is it clearly text-only (name, address, description)?
    YES → text
    NO
    ↓
Default → text (with warning)
```

## Special Cases

### "Other" Options

When a choice list includes "Other", automatically add an "Other specify" text question:

```xlsx
type: select_one gender
name: gender
label: What is your gender?

type: text
name: gender_other
label: Please specify (Other)
relevant: ${gender} = '99'
```

### cascading Selects

When choices depend on previous selections, use select_one with choice_filter:

```xlsx
type: select_one country
name: country
label: Select country

type: select_one region
name: region
label: Select region
choice_filter: country=${country}
```

### Calculated Fields

For derived values, use calculate type:

```xlsx
type: calculate
name: total_income
calculation: ${income_wage} + ${income_business}
```

### Note Fields

For display-only text, use note type:

```xlsx
type: note
name: instructions
label: Please answer all questions accurately
```

## Special Response Codes

When adding special response options to choice lists, use these consistent negative values:

### Standard Codes
- **-96**: Other (specify)
- **-99**: Don't know
- **-98**: Refused to answer

### Implementation
These codes should be used consistently across ALL choice lists in the form.

**Example with special codes:**
```xlsx
list_name | name | label
gender | 1 | Male
gender | 2 | Female
gender | -96 | Other (specify)
gender | -99 | Don't know
gender | -98 | Refused to answer
```

### "Other Specify" Follow-up
When "-96" (Other) is used, automatically create a follow-up question:

```xlsx
type: text
name: gender_other
label: Please specify (Other)
relevant: ${gender} = '-96'
required: no
```

This ensures that when a respondent selects "Other", they can specify what they mean.

### Benefits
1. **Consistency**: Easy to identify special responses in data analysis
2. **Negative values**: Clearly distinguish from valid positive responses
3. **Standardization**: Same codes across all questions and forms
4. **Data cleaning**: Easy to filter/handle special cases
