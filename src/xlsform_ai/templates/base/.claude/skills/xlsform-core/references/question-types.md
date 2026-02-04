# XLSForm Question Types Reference

Complete reference of all XLSForm question types with examples.

## Text Input Types

### text
Free text response.

| type | name | label |
| --- | --- | --- |
| text | name | What is your name? |

**Optional appearance:** `multiline` for multi-line input

### integer
Whole number input.

| type | name | label | constraint |
| --- | --- | --- | --- |
| integer | age | What is your age? | . >= 0 and . <= 120 |

### decimal
Decimal number input.

| type | name | label |
| --- | --- | --- |
| decimal | weight | Weight in kg |

### range
Restricted range input with start, end, and step.

| type | name | label | parameters |
| --- | --- | --- | --- |
| range | rating | Rate 1-5 | start=1 end=5 step=1 |

**Optional appearance:** `rating` for star rating widget

## Multiple Choice Types

### select_one
Select one option from a list.

**Syntax:** `select_one listname`

| type | name | label |
| --- | --- | --- |
| select_one gender | gender | What is your gender? |

**Choices sheet:**
| list_name | name | label |
| --- | --- | --- |
| gender | male | Male |
| gender | female | Female |
| gender | other | Other |

### select_multiple
Select multiple options from a list.

**Syntax:** `select_multiple listname`

| type | name | label |
| --- | --- | --- |
| select_multiple fruits | favorite_fruits | Select your favorite fruits |

**Choices sheet:**
| list_name | name | label |
| --- | --- | --- |
| fruits | apple | Apple |
| fruits | banana | Banana |
| fruits | orange | Orange |

**Note:** Choice names for select_multiple must NOT contain spaces (they're space-separated when saved).

### select_one_from_file
Select one option from an external CSV/XML/GeoJSON file.

| type | name | label | parameters |
| --- | --- | --- | --- |
| select_one_from_file countries.csv | country | Select country | value=code label=name |

### select_multiple_from_file
Select multiple options from an external file.

| type | name | label | choice_filter |
| --- | --- | --- | --- |
| select_multiple_from_file items.csv | selected_items | Select items | category='A' |

### or_other
Add an "other" option to select questions (shortcut).

| type | name | label |
| --- | --- | --- |
| select_one fruits or_other | favorite | Favorite fruit |

Adds an "other" choice automatically. For more control, use relevance instead.

## Geolocation Types

### geopoint
Collect GPS coordinates (latitude, longitude, altitude, accuracy).

| type | name | label | parameters |
| --- | --- | --- | --- |
| geopoint | location | Record location | capture-accuracy=10 warning-accuracy=10 |

### geotrace
Record a line of GPS coordinates.

| type | name | label |
| --- | --- | --- |
| geotrace | path | Walk the boundary |

### geoshape
Record a polygon (closed shape).

| type | name | label |
| --- | --- | --- |
| geoshape | area | Mark the area |

## Media Types

### image
Capture or upload an image.

| type | name | label | parameters |
| --- | --- | --- | --- |
| image | photo | Take a photo | max-pixels=1000 |

**Optional appearance:** `signature` for signatures, `draw` for sketches

### audio
Record or upload audio.

| type | name | parameters |
| --- | --- | --- |
| audio | recording | quality=normal |

**Quality options:** `voice-only`, `low`, `normal`, `external`

### video
Record or upload video.

| type | name | label |
| --- | --- | --- |
| video | footage | Record video |

### file
Upload any file (txt, pdf, xls, docx, zip, etc.).

| type | name | label |
| --- | --- | --- |
| file | document | Upload document |

## Date and Time Types

### date
Date input.

| type | name | label | default |
| --- | --- | --- | --- |
| date | survey_date | Survey date | today() |

**Optional appearance:** `no-calendar`, `month-year`, `year`

### time
Time input.

| type | name | label |
| --- | --- | --- |
| time | appointment_time | Appointment time |

### dateTime
Combined date and time input.

| type | name | label |
| --- | --- | --- |
| dateTime | timestamp | Record timestamp |

## Note and Display Types

### note
Display information only (no input). Shorthand for `text` with `readonly=true`.

| type | name | label |
| --- | --- | --- |
| note | instructions | Please read the instructions carefully |

Can embed variables in labels: `Total: ${total_amount}`

### calculate
Perform calculations (hidden field, no label shown).

| type | name | calculation |
| --- | --- | --- |
| calculate | total | ${item1} + ${item2} |

Use a non-text type (integer, decimal, date) if the calculation result type matters for analysis.

### hidden
Hidden field with no UI element, stores a constant.

| type | name | calculation |
| --- | --- | --- |
| hidden | form_version | '1.0' |

## Metadata Types

These collect system information automatically (no user input):

| type | name | Description |
| --- | --- | --- |
| start | start | Form start date/time |
| end | end | Form end date/time |
| today | today | Survey date |
| deviceid | deviceid | Device identifier |
| phonenumber | phonenumber | Phone number (if available) |
| subscriberid | subscriberid | SIM subscriber ID |
| simserial | simserial | SIM serial number |
| username | username | Configured username |
| email | email | Configured email |
| audit | audit | Enumerator behavior log |

**audit metadata** can track location:
| type | name | parameters |
| --- | --- | --- |
| audit | audit | location-priority=high-accuracy location-min-interval=180 location-max-age=300 |

## Special Types

### rank
Order a list of options.

| type | name | label |
| --- | --- | --- |
| rank toppings | rank_toppings | Order toppings from favorite to least |

### acknowledge
Acknowledgment prompt (sets value to "OK").

| type | name | label |
| --- | --- | --- |
| acknowledge | consent | I consent to participate |

### barcode
Scan a barcode (requires barcode scanner app).

| type | name | label |
| --- | --- | --- |
| barcode | product_id | Scan product barcode |

### xml-external
Reference external XML data file.

| type | name | label |
| --- | --- | --- |
| xml-external | houses | External house data |

### csv-external
Reference external CSV data file.

| type | name | label |
| --- | --- | --- |
| csv-external | participants | Participant data |

### begin group / end group
Group related questions together.

| type | name | label | appearance |
| --- | --- | --- | --- |
| begin group | demographics | Demographics | field-list |
| text | name | Name | |
| integer | age | Age | |
| end group | | | |

**field-list appearance** shows all questions in the group on one screen.

### begin repeat / end repeat
Repeatable set of questions.

| type | name | label | repeat_count |
| --- | --- | --- | --- |
| begin repeat | child | Child | |
| text | child_name | Child's name | |
| integer | child_age | Child's age | |
| end repeat | | | |

**repeat_count** can be:
- Fixed number: `3` (exactly 3 repeats)
- Dynamic: `${num_children}` (based on previous answer)
- Omitted: user can add/remove repeats

## Appearance Attributes

Common appearance attributes:

| Appearance | Question Type | Description |
| --- | --- | --- |
| multiline | text | Multi-line text input |
| minimal | select_one/select_multiple | Dropdown menu |
| quick | select_one | Auto-advance after selection |
| compact | select_one/select_multiple | Compact display |
| horizontal | select_one/select_multiple | Horizontal options |
| likert | select_one | Likert scale display |
| newlines | text | Preserve line breaks |
| calendar | date | Show calendar widget |
| spinner | number | Show number spinner |
| signature | image | Signature capture |
| draw | image | Drawing sketch |
| map | select_one_from_file | Show choices on map |

## Parameters Column

Used with specific question types:

### Range parameters
- `start=0` - Minimum value
- `end=10` - Maximum value
- `step=1` - Increment

### Geopoint parameters
- `capture-accuracy=5` - Auto-capture at this accuracy (meters)
- `warning-accuracy=100` - Show warning above this accuracy

### Audio parameters
- `quality=normal` - Audio quality: voice-only, low, normal, external

### Image parameters
- `max-pixels=1000` - Downsize to max pixel dimension

### Select from file parameters
- `value=column_name` - Column for choice value
- `label=column_name` - Column for choice label

### Randomization
- `randomize=true` - Randomize choice order
- `randomize=true, seed=${sd}` - Reproducible randomization

## Tips

1. **Always** use `snake_case` for question names (e.g., `respondent_age`)
2. **Never** use spaces in choice names for `select_multiple`
3. **Always** match the list name exactly between survey type and choices sheet
4. **Use** `calculate` type for computed values that don't need user input
5. **Use** `note` type to display information or embedded calculations
6. **Add** `constraint_message` to explain why a value was rejected
7. **Use** `relevant` to conditionally show questions
8. **Test** complex forms with real data before deployment
