XLSForm settings sheet reference.

Required settings (row 2 in `settings` sheet):
- `form_title`: Human-readable form title shown in clients.
- `form_id`: Unique identifier used by servers.

Recommended columns:
- `version`: Version string (e.g., 2025020701).
- `instance_name`: Submission name expression (e.g., concat(${name}, " ", ${date})).
- `default_language`: Language code (e.g., en).

Update via script:
```
python scripts/update_settings.py --title "Household Survey" --id "household_survey_v1"
```

If the settings sheet is missing, create it with a header row containing:
`form_title`, `form_id`.
