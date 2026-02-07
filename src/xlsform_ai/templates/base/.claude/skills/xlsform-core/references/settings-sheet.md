# XLSForm Settings Sheet Reference

The settings sheet is optional but recommended. If you include it, add the core fields below.

## Core Settings (Recommended)

- form_title: Human-readable title shown in clients.
- form_id: Unique identifier used by servers and exports.
- version: Version string. Common convention is yyyymmddrr (year, month, day, revision).

If form_id is missing, many tools default to the XLSX file name. If form_title is missing, it may default to form_id.

## Other Common Settings

- default_language: Default language for multilingual forms.
- public_key: Public key for encryption.
- submission_url: Alternate submission URL.
- style: UI style (for compatible clients).
- name: XForms root node name.
- allow_choice_duplicates: Allow duplicate choice names in choices (used for cascading selects).
- clean_text_values: yes or no.

## Layout Rules (Project Standard)

- Row 1 contains column headers.
- Row 2 contains values aligned to those headers.
- Always read headers before writing values. Do not assume fixed column positions.

## Example

```xlsform
form_title        form_id               version
Household Survey  household_survey_v1   2026020701
```

## Scripted Update

```bash
python scripts/update_settings.py --title "Household Survey" --id "household_survey_v1"
```
