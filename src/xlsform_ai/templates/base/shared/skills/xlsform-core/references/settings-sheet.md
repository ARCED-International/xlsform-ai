XLSForm settings sheet reference.

## Critical Layout Rules (Non-Negotiable)

1. **Row 1 = column headers, Row 2 = values.**
   - Each header in row 1 must have its value in the same column on row 2.
   - Example: if `form_title` is in column A row 1, its value goes in column A row 2.
2. **Never assume fixed column positions.**
   - Always read row 1 headers to find the correct column before writing row 2.
3. **`version` is always a formula, never blank:**
   - `=TEXT(NOW(), "yyyymmddhhmmss")`

## Required Settings (Row 2 Values)
- `form_title`: Human-readable form title shown in clients.
- `form_id`: Unique identifier used by servers.

## Allowed Settings Headers (Any Order)
- `form_title`: Title shown to users. If missing/blank, pulled from `form_id`.
- `form_id`: Unique identifier. If missing/blank, pulled from XLS file name.
- `version`: `=TEXT(NOW(), "yyyymmddhhmmss")` (must be formula).
- `instance_name`: Expression to name each submission (e.g., `concat(${lname}, '-', ${fname}, '-', uuid())`).
- `default_language`: Default language in localized forms (e.g., `English (en)`).
- `public_key`: Public key for encryption.
- `submission_url`: Override server submission URL.
- `style`: Web form style.
- `name`: XForms root node name (rarely needed).
- `clean_text_values`: `yes` or `no` (defaults to yes).

## Instance Name Best Practices (Suggestion Only)
- Include 1-2 key identifiers + `uuid()` for uniqueness.
- Example: `concat(${cluster_id}, '-', ${hh_id}, '-', uuid())`

## Example (Household Survey)
```xlsform
form_title        form_id               version
Household Survey  household_survey_v1   =TEXT(NOW(), "yyyymmddhhmmss")
```

## Update via Script
```
python scripts/update_settings.py --title "Household Survey" --id "household_survey_v1"
```

If the settings sheet is missing, create it with a header row containing:
`form_title`, `form_id`, and then fill row 2 values.
