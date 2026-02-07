# XLSForm Settings Sheet Guidance

The `settings` sheet uses a single header row (row 1) and a single values row (row 2).
Only row 2 should contain values. Do not insert extra rows.

## Column Behavior and Best Practices

### form_title
- Purpose: Human-readable form title displayed in tools.
- Recommended: Clear, concise, unique per project.
- Example: `Household Survey 2026`.

### form_id
- Purpose: Unique form identifier used by servers and analytics.
- Rules: Must be unique, lowercase, start with a letter, no spaces.
- Recommended: Use snake_case.
- Example: `household_survey_2026`.

### version
- Purpose: Form version for deployment updates.
- Rule: Must always be this formula (do not leave blank or replace with a literal):
  `=TEXT(NOW(), "yyyymmddhhmmss")`

### instance_name
- Purpose: Defines the default instance name shown for submissions.
- Best practice: Use a short, meaningful name that references key identifiers.
- Example: `concat('HH-', ${household_id})` or `concat(${respondent_name}, ' - ', ${today})`.

### default_language
- Purpose: Default language for labels in multilingual forms.
- Rules: Use ISO language codes (e.g., `en`, `fr`, `es`).
- Example: `en`.

### style
- Purpose: Controls form appearance in some platforms.
- Common values: `pages`, `theme-grid`, `theme-grid-compact`.
- Best practice: Only set if you need a specific style.

## Write Rules

- Read column names from row 1.
- Write values to row 2 only.
- Do not create new rows for settings.
- Ensure `version` is present and set to `=TEXT(NOW(), "yyyymmddhhmmss")`.
