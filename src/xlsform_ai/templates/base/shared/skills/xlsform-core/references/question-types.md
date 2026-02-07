# XLSForm Question Types Reference

Concise list of XLSForm question types with minimal examples.

## Text and Number

### text
| type | name | label |
| --- | --- | --- |
| text | respondent_name | What is your name? |

### integer
| type | name | label | constraint |
| --- | --- | --- | --- |
| integer | age | Age | . >= 0 and . <= 120 |

### decimal
| type | name | label |
| --- | --- | --- |
| decimal | weight | Weight (kg) |

### range
| type | name | label | parameters |
| --- | --- | --- | --- |
| range | rating | Rate 1-5 | start=1 end=5 step=1 |

## Select Questions

### select_one
Syntax: select_one list_name

| type | name | label |
| --- | --- | --- |
| select_one gender | gender | Gender |

### select_multiple
Syntax: select_multiple list_name

| type | name | label |
| --- | --- | --- |
| select_multiple fruits | favorite_fruits | Favorite fruits |

Note: select_multiple choice names must not contain spaces.

### select_one_from_file
| type | name | label | parameters |
| --- | --- | --- | --- |
| select_one_from_file countries.csv | country | Country | value=code label=name |

### select_multiple_from_file
| type | name | label | parameters |
| --- | --- | --- | --- |
| select_multiple_from_file items.csv | items | Select items | value=id label=label |

### or_other (modifier)
Adds an "other" option to select_one or select_multiple.
Only supported without translations and without choice_filter.

Example: select_one fruits or_other

## Geo

### geopoint
| type | name | label |
| --- | --- | --- |
| geopoint | location | Record location |

### geotrace
| type | name | label |
| --- | --- | --- |
| geotrace | route | Walk the route |

### geoshape
| type | name | label |
| --- | --- | --- |
| geoshape | area | Mark the area |

## Media

### image
| type | name | label |
| --- | --- | --- |
| image | photo | Take a photo |

### audio
| type | name | label |
| --- | --- | --- |
| audio | recording | Record audio |

### video
| type | name | label |
| --- | --- | --- |
| video | footage | Record video |

### file
| type | name | label |
| --- | --- | --- |
| file | document | Upload document |

### background-audio
| type | name | label |
| --- | --- | --- |
| background-audio | bg_audio | Play background audio |

## Date and Time

### date
| type | name | label |
| --- | --- | --- |
| date | survey_date | Survey date |

### time
| type | name | label |
| --- | --- | --- |
| time | appointment_time | Appointment time |

### dateTime
| type | name | label |
| --- | --- | --- |
| dateTime | timestamp | Record timestamp |

## Display and Calculation

### note
| type | name | label |
| --- | --- | --- |
| note | instructions | Read these instructions |

### calculate
| type | name | calculation |
| --- | --- | --- |
| calculate | total | ${a} + ${b} |

### acknowledge
| type | name | label |
| --- | --- | --- |
| acknowledge | consent | I agree |

### hidden
| type | name | calculation |
| --- | --- | --- |
| hidden | form_version | '1.0' |

## Ranking and Barcode

### rank
| type | name | label |
| --- | --- | --- |
| rank toppings | rank_toppings | Rank toppings |

### barcode
| type | name | label |
| --- | --- | --- |
| barcode | product_id | Scan barcode |

## External Data

### csv-external
| type | name | label |
| --- | --- | --- |
| csv-external | participants | Participant data |

### xml-external
| type | name | label |
| --- | --- | --- |
| xml-external | houses | External data |

## Metadata (auto-collected)

| type | name | Description |
| --- | --- | --- |
| start | start | Form start time |
| end | end | Form end time |
| today | today | Survey date |
| deviceid | deviceid | Device identifier |
| phonenumber | phonenumber | Phone number |
| subscriberid | subscriberid | SIM subscriber ID |
| simserial | simserial | SIM serial |
| username | username | Username |
| email | email | Email |
| audit | audit | Audit log |

## Structure

### begin group / end group
| type | name | label |
| --- | --- | --- |
| begin group | demographics | Demographics |
| text | name | Name |
| end group | | |

### begin repeat / end repeat
| type | name | label | repeat_count |
| --- | --- | --- | --- |
| begin repeat | child | Child | ${num_children} |
| text | child_name | Child name | |
| end repeat | | | |

## Useful Columns

- relevant for conditional display
- constraint and constraint_message for validation
- required and required_message for mandatory fields
- choice_filter for cascading selects
- appearance and parameters for UI and type options
