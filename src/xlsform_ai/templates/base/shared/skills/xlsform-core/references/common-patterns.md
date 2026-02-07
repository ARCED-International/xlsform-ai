# XLSForm Common Patterns

Reusable patterns aligned with XLSForm documentation and common practice.

## Relevance (Conditional Display)

Show a question only if a condition is met:

| type | name | label | relevant |
| --- | --- | --- | --- |
| select_one yes_no | has_children | Do you have children? | |
| integer | num_children | How many children? | ${has_children} = 'yes' |

For select_multiple, use selected():

| type | name | label | relevant |
| --- | --- | --- | --- |
| select_multiple fruits | favorite_fruits | Favorite fruits | |
| text | other_fruit | Specify other | selected(${favorite_fruits}, 'other') |

## Cascading Selects (choice_filter)

Filter a choice list based on a previous answer:

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
| cities | toronto | Toronto | canada |

If cascading selects require duplicate choice names, set allow_choice_duplicates in the settings sheet.

## Constraints

| type | name | label | constraint | constraint_message |
| --- | --- | --- | --- | --- |
| integer | age | Age | . >= 0 and . <= 120 | Age must be 0-120 |

Use . for the current field in constraints.

## Calculations and Triggers

| type | name | label | calculation |
| --- | --- | --- | --- |
| decimal | price | Price | |
| calculate | tax | | ${price} * 0.18 |

Trigger recalculation on a specific change:

| type | name | calculation | trigger |
| --- | --- | --- | --- |
| dateTime | temp_timestamp | now() | ${temperature} |

## Repeats

| type | name | label | repeat_count |
| --- | --- | --- | --- |
| begin repeat | child | Child | ${num_children} |
| text | child_name | Child name | |
| end repeat | | | |

repeat_count can be a number or a formula.

## Groups

| type | name | label | appearance |
| --- | --- | --- | --- |
| begin group | demographics | Demographics | field-list |
| text | name | Name | |
| integer | age | Age | |
| end group | | | |

## Required and Read-Only

| type | name | label | required | required_message |
| --- | --- | --- | --- | --- |
| text | name | Name | yes | This field is required |

| type | name | label | read_only | calculation |
| --- | --- | --- | --- | --- |
| decimal | total | Total | yes | ${a} + ${b} |

## Defaults

| type | name | label | default |
| --- | --- | --- | --- |
| date | survey_date | Survey date | today() |

## or_other (Use Carefully)

or_other is only supported for select_one or select_multiple when there are no label translations and no choice_filter. It uses the English label "Specify other".

If you need translations or choice_filter, use a manual "other" pattern with a separate text question and selected().

## Randomize Choice Order

| type | name | label | parameters |
| --- | --- | --- | --- |
| select_one options | choice | Choose | randomize=true |

For reproducible randomization, set a seed calculation and include seed=${seed} in parameters.
