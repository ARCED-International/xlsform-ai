# XLSForm Common Patterns

Reusable patterns for common XLSForm features.

## Conditional Questions (Relevance)

Show questions based on previous answers using the `relevant` column.

### Basic Yes/No Condition

Show a follow-up question only when user answers "yes":

| type | name | label | relevant |
| --- | --- | --- | --- |
| select_one yes_no | has_children | Do you have children? | |
| integer | num_children | How many children? | ${has_children} = 'yes' |

**Choices for yes_no:**
| list_name | name | label |
| --- | --- | --- |
| yes_no | yes | Yes |
| yes_no | no | No |

### Multiple Conditions

Combine conditions with `and`/`or`:

| type | name | label | relevant |
| --- | --- | --- | --- |
| select_one gender | gender | Gender | |
| integer | age | Age | |
| text | pregnancy_note | Note | ${gender} = 'female' and ${age} >= 18 |

### Numeric Comparisons

| type | name | label | relevant |
| --- | --- | --- | --- |
| integer | household_size | Household size | |
| text | large_hh_note | Note | ${household_size} > 10 |

### select_multiple with selected()

Check if a specific option was selected in a select_multiple:

| type | name | label | relevant |
| --- | --- | --- | --- |
| select_multiple fruits | favorite_fruits | Favorite fruits | |
| text | other_fruit | Specify other | selected(${favorite_fruits}, 'other') |

**Note:** For select_multiple, use `selected(${field}, 'value')` not `${field} = 'value'`.

---

## Cascading Selects (Choice Filters)

Filter choice lists based on previous selections.

### Two-Level Cascade

Country → City:

**Survey:**
| type | name | label | choice_filter |
| --- | --- | --- | --- |
| select_one countries | country | Country | |
| select_one cities | city | City | country=${country} |

**Choices:**
| list_name | name | label | country |
| --- | --- | --- | --- |
| countries | usa | United States | |
| countries | canada | Canada | |
| cities | nyc | New York | usa |
| cities | la | Los Angeles | usa |
| cities | toronto | Toronto | canada |

### Three-Level Cascade

Country → State → City:

**Survey:**
| type | name | label | choice_filter |
| --- | --- | --- | --- |
| select_one countries | country | Country | |
| select_one states | state | State/Province | country=${country} |
| select_one cities | city | City | state=${state} |

**Choices:**
| list_name | name | label | country | state |
| --- | --- | --- | --- | --- |
| states | ca | California | usa | |
| states | ny | New York | usa | |
| cities | la | Los Angeles | usa | ca |
| cities | nyc | New York City | usa | ny |

---

## Constraints

Restrict what values users can enter.

### Range Constraint

| type | name | label | constraint | constraint_message |
| --- | --- | --- | --- | --- |
| integer | age | Age | . >= 0 and . <= 120 | Age must be 0-120 |

### Not Empty

| type | name | label | constraint | constraint_message |
| --- | --- | --- | --- | --- |
| text | name | Name | . != '' | Name is required |

### Pattern Matching (Advanced)

For phone numbers, emails (requires regex support):

| type | name | label | constraint | constraint_message |
| --- | --- | --- | --- | --- |
| text | phone | Phone | regex(., '^[0-9]{10}$') | Must be 10 digits |

---

## Calculations

Compute values from other fields.

### Simple Calculation

| type | name | label | calculation |
| --- | --- | --- | --- |
| decimal | price | Price | |
| decimal | tax_rate | | 0.18 |
| calculate | tax | | ${price} * ${tax_rate} |
| note | total | Total: ${tax} | |

### Date Calculation

| type | name | label | calculation |
| --- | --- | --- | --- |
| date | start_date | Start date | |
| date | end_date | End date | |
| calculate | days | | floor(decimal-date-time(${end_date}) - decimal-date-time(${start_date})) |

### Counting in Repeats

Count items in a repeat:

| type | name | label | calculation |
| --- | --- | --- | --- |
| begin repeat | household_member | | |
| text | member_name | Name | |
| end repeat | | | |
| calculate | total_members | | count(${household_member}) |

---

## Triggered Calculations

Recalculate only when a specific field changes.

### Timestamp on Entry

Record when a value is entered:

| type | name | label | calculation | trigger |
| --- | --- | --- | --- | --- |
| integer | temp | Temperature | | |
| dateTime | temp_timestamp | | now() | ${temp} |

### Clear Value on Trigger

Clear a calculated field when trigger changes:

| type | name | label | calculation | trigger |
| --- | --- | --- | --- | --- |
| text | person_name | Name | | |
| integer | person_age | Age | | ${person_name} |

When `person_name` changes, `person_age` is cleared.

---

## Repeats

Allow users to add multiple sets of questions.

### Basic Repeat

| type | name | label | repeat_count |
| --- | --- | --- | --- |
| begin repeat | child | Child | |
| text | child_name | Child's name | |
| integer | child_age | Child's age | |
| end repeat | | | |

### Fixed Count Repeat

Exactly 3 children:

| type | name | label | repeat_count |
| --- | --- | --- | --- |
| begin repeat | child | Child | 3 |
| text | child_name | Child's name | |
| end repeat | | | |

### Dynamic Count Repeat

Based on previous answer:

| type | name | label | |
| --- | --- | --- | --- |
| integer | num_children | Number of children | |
| begin repeat | child | Child | ${num_children} |
| text | child_name | Child's name | |
| end repeat | | | |

### Conditional Repeat

Only show repeat if condition is met:

| type | name | label | relevant |
| --- | --- | --- | --- |
| select_one yes_no | has_children | Has children? | |
| begin repeat | child | Child | ${has_children} = 'yes' |
| text | child_name | Child's name | |
| end repeat | | | |

---

## Groups

Organize related questions.

### Basic Group

| type | name | label |
| --- | --- | --- |
| begin group | demographics | Demographics |
| text | name | Name |
| integer | age | Age |
| end group | | |

### Field-List Group (Single Screen)

Show all questions on one screen:

| type | name | label | appearance |
| --- | --- | --- | --- |
| begin group | info | Information | field-list |
| text | name | Name |
| integer | age | Age |
| select_one gender | gender | Gender |
| end group | | |

### Nested Groups

| type | name | label |
| --- | --- | --- |
| begin group | section1 | Section 1 |
| begin group | subsection1a | Subsection 1A |
| text | q1 | Question 1 |
| end group | | |
| end group | | |

---

## Required Fields

Make fields mandatory.

### Basic Required

| type | name | label | required |
| --- | --- | --- | --- |
| text | name | Name | yes |

### Required with Message

| type | name | label | required | required_message |
| --- | --- | --- | --- | --- |
| text | name | Name | yes | Please enter your name |

---

## Default Values

Pre-fill fields.

### Static Default

| type | name | label | default |
| --- | --- | --- | --- |
| date | survey_date | Date | 2024-12-15 |

### Dynamic Default (Today)

| type | name | label | default |
| --- | --- | --- | --- |
| date | today | Today | today() |

---

## Read-Only Fields

Display calculated values that users can't edit.

| type | name | label | readonly | calculation |
| --- | --- | --- | --- | --- |
| decimal | amount | Amount | | |
| decimal | tax | Tax (18%) | yes | ${amount} * 0.18 |

---

## Hidden Fields

Store values without showing them to users.

| type | name | calculation |
| --- | --- | --- |
| hidden | form_version | '2024.12.15' |
| hidden | enumerator_id | '12345' |

---

## Metadata

Automatically collected information.

| type | name | label |
| --- | --- | --- |
| start | start | |
| end | end | |
| today | today | |
| deviceid | deviceid | |
| username | username | |
| audit | audit | |

### Audit with Location Tracking

| type | name | parameters |
| --- | --- | --- |
| audit | audit | location-priority=high-accuracy location-min-interval=180 location-max-age=300 |

---

## Appearance Attributes

Change how questions display.

### Multiline Text

| type | name | label | appearance |
| --- | --- | --- | --- |
| text | comments | Comments | multiline |

### Compact Choices

| type | name | label | appearance |
| --- | --- | --- | --- |
| select_one yes_no | ready | Ready? | compact |

### Likert Scale

| type | name | label | appearance |
| --- | --- | --- | --- |
| select_one agreement | agree | Agreement | likert |

### Quick (Auto-Advance)

| type | name | label | appearance |
| --- | --- | --- | --- |
| select_one next | continue | Continue? | quick |

---

## Specify Other (Manual Pattern)

Instead of `or_other`, use manual pattern for more control.

| type | name | label | relevant |
| --- | --- | --- | --- |
| select_multiple fruits | favorite | Favorite fruits | |
| text | fruit_other | Specify other | selected(${favorite}, 'other') |

**Choices must include 'other':**
| list_name | name | label |
| --- | --- | --- |
| fruits | apple | Apple |
| fruits | banana | Banana |
| fruits | other | Other |

---

## Instance Lookups

Look up values from choice lists or external files.

### Lookup from Choices

| type | name | label | calculation |
| --- | --- | --- | --- |
| select_one products | product | Product | |
| calculate | product_price | | instance('products')/root/item[name=${product}]/price |

**Choices with data column:**
| list_name | name | label | price |
| --- | --- | --- | --- |
| products | item1 | Item 1 | 10.50 |
| products | item2 | Item 2 | 15.00 |

---

## Calculated Instance Name

Give each submission a unique name based on fields.

**Settings sheet:**
| form_id | instance_name |
| --- | --- |
| my_form | concat(${first_name}, '_', ${last_name}) |

---

## Randomization

Randomize choice order.

### Simple Randomization

| type | name | label | parameters |
| --- | --- | --- | --- |
| select_one options | choice | Choose | randomize=true |

### Reproducible Randomization

| type | name | label | calculation | parameters |
| --- | --- | --- | --- | --- |
| calculate | seed | | once(decimal-date-time(now())) | |
| select_one options | choice | Choose | | randomize=true seed=${seed} |

---

## Multiple Languages

Add translations using language code suffix.

### Labels

| type | name | label::English | label::Français |
| --- | --- | --- | --- |
| text | name | Name | Nom |

### Settings

| form_id | default_language |
| --- | --- |
| my_form | English (en) |

---

## Media in Choices

Add images/audio to choices.

| list_name | name | label | image |
| --- | --- | --- | --- |
| fruits | apple | Apple | apple.jpg |
| fruits | banana | Banana | banana.png |

---

## Form Design Best Practices

### Question Ordering

1. Start with metadata (start, today)
2. Simple questions first
3. Complex/sensitive questions later
4. Demographics at the end

### Grouping Logic

- Group related questions
- Use field-list for short related questions
- Label groups meaningfully
- Don't nest more than 3 levels deep

### Naming Conventions

- Use snake_case: `respondent_age`
- Be descriptive but concise: `hh_head_age`
- Avoid abbreviations unless obvious
- Use consistent prefixes: `hh_` for household

### Choice Lists

- Reuse choice lists when possible (yes_no, gender)
- Use consistent naming: list name in type matches list_name in choices
- Avoid spaces in choice names (especially for select_multiple)

### Relevance

- Keep conditions simple
- Use parentheses for complex logic: `${a} and (${b} or ${c})`
- Test thoroughly with all combinations

### Performance

- Avoid very long choice lists (>1000 options)
- Use select_one_from_file for large lists
- Minimize calculations in repeat counts
- Test on target devices
