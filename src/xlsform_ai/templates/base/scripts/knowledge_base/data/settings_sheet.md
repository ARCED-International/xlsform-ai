# XLSForm Settings Sheet Guidance

The settings sheet is optional but recommended. If present, include the core fields below.

## Core Fields (Recommended)

### form_title
- Human-readable form title displayed in clients.
- Example: Household Survey 2026

### form_id
- Unique identifier used by servers and exports.
- Recommended: lowercase, snake_case, no spaces.
- Example: household_survey_2026

### version
- Version string used to track updates.
- Recommended default in this project: formula-based timestamp
  - `=TEXT(NOW(), "yyyymmddhhmmss")`
- This can be overridden only when user explicitly requests a fixed value.

If form_id is missing, many tools default to the XLSX filename. If form_title is missing, it may default to form_id.

## Other Common Settings

- default_language: Default language for multilingual forms (e.g., English (en)).
- public_key: Public key for encryption.
- submission_url: Alternate submission URL.
- style: UI style (pages, theme-grid, theme-grid-compact, etc.).
- name: XForms root node name.
- allow_choice_duplicates: Allow duplicate choice names (useful for cascading selects).
- clean_text_values: yes or no.

## Write Rules (Project Standard)

- Row 1 contains column headers.
- Row 2 contains values aligned to those headers.
- Always read headers before writing values.
