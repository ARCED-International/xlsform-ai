# Random Sampling and Selection Patterns

These patterns use ODK/XLSForm functions like `random()` and `indexed-repeat()`.
They assume the repeat name and question names are consistent.

## Randomly Select One Household Member

Assumes a repeat named `person` with `person_name` and `person_age`.

```xlsx
type        name                label                   calculation
calculate   hh_count                                   count(${person_name})
calculate   hh_random_index                            int(random() * ${hh_count}) + 1
calculate   hh_random_name                             indexed-repeat(${person_name}, ${person}, ${hh_random_index})
```

Best practices:
- Make `person_name` required so it is always available.
- Use `count(${person_name})` to ensure only filled names are counted.

## Randomly Select Two Members (Allow Repeats)

This picks two random indices. They can be the same if the random values match.

```xlsx
type        name                    calculation
calculate   hh_random_index_1        int(random() * ${hh_count}) + 1
calculate   hh_random_index_2        int(random() * ${hh_count}) + 1
calculate   hh_random_name_1         indexed-repeat(${person_name}, ${person}, ${hh_random_index_1})
calculate   hh_random_name_2         indexed-repeat(${person_name}, ${person}, ${hh_random_index_2})
```

If you need unique selections, add a constraint or ask the user to re-run.

## Randomly Select Two Members (Force Unique)

Use a constraint to ensure unique picks. If it fails, prompt a re-run.

```xlsx
type        name                    calculation                              constraint                         constraint_message
calculate   hh_random_index_1        int(random() * ${hh_count}) + 1
calculate   hh_random_index_2        int(random() * ${hh_count}) + 1          . != ${hh_random_index_1}          Random picks matched. Please re-run.
```

## Randomly Select N Members (Custom Number)

You cannot loop in XLSForm. For small N, repeat the pattern and enforce uniqueness.
For large N, ask the enumerator to use a rank question after randomizing choices.

## Randomize Choice Order

Use `randomize()` to shuffle choices for a select question:
```xlsx
type            name           label                         appearance
select_one yes_no  consent     Do you consent?               randomize()
```

Note: Randomization changes display order, not stored values.

## Select From a Custom List Based on Repeat Condition

Generate a select list from repeat values and filter by a condition:

```xlsx
type                        name            label
begin_repeat                person          Person
text                        person_name     Name
integer                     person_age      Age
end_repeat                  person

select_one ${person_name}   adult_choice    Select an adult
choice_filter                               ${person_age} >= 18
```

Best practices:
- Require `person_name` in the repeat.
- Use `choice_filter` to limit by age or other conditions.

