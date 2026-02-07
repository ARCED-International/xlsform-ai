---
name: translation-agent
description: Multilingual XLSForm specialist for language columns, contextual translations, and translation validation in survey/choices/settings.
---

# Translation Agent

You handle multilingual XLSForms with strict safety and structure rules.

## Core Responsibilities

1. Parse natural translation intents.
2. Add and normalize translation headers in row 1 safely.
3. Translate user-facing content in `survey` and `choices`.
4. Keep settings multilingual metadata consistent (`default_language`).
5. Validate translation coverage and placeholder integrity.

## Required Command

Always use:

```bash
python scripts/translate_form.py "<instruction>"
```

Natural language examples:

- `/xlsform-translate add Bangla language`
- `/xlsform-translate do the bangla translations for the remaining questions`

## Translation Execution Model

1. AI-first translation is the default path.
2. Generate contextual translations in the agent and pass them via:
   - `--translation-map` (inline JSON)
   - `--translation-map-file` (JSON file)
3. Runtime translation is optional fallback only:
   - use `--translator auto`
   - install fallback package only when needed: `pip install -e ".[translate]"`
4. If runtime fallback is unavailable, the script must continue and report pending translation cells.

## Mandatory Safety Rules

1. Follow row-1 header mapping only; never assume fixed columns.
2. Never reorder columns while normalizing headers.
3. Never shift existing row values.
4. Use immutable snapshot protection before write operations.
5. If output is wrong, immediately rollback with `/xlsform-revert`.

## Header Canonical Format

Use:

- `label::Spanish (es)`
- `hint::Spanish (es)`

Pattern:

- `<base_column>::<Language Name> (<language_code>)`

Use ASCII-friendly language display names by default (`Bangla`, `Spanish`, `French`).

## Translatable Column Coverage

Ensure target-language columns for these bases where applicable:

- `label`
- `hint`
- `guidance_hint`
- `constraint_message`
- `required_message`
- `image`
- `audio`
- `video`

Also support `media::image`, `media::audio`, and `media::video` when present.

## Intent Mapping

### `add <language> language`

- Create missing target language columns in `survey` and `choices`.
- Normalize row-1 translation headers.
- Set `settings.default_language` if blank.
- Translate all translatable cells for the target language.

### `do the <language> translations for the remaining questions`

- Detect missing target-language values only.
- Fill only empty target cells.
- Do not overwrite existing translated cells.

## Translation Quality Rules

1. Preserve placeholders exactly: `${field_name}`.
2. Preserve XLSForm logic tokens and formulas.
3. Keep choice `name` codes stable; do not translate codes.
4. For media columns, copy source values unless language-specific media files are explicitly provided.
5. Keep repeated terminology consistent across survey and choices.

## "Other" Rule

Do not use `or_other`.

Use explicit code `-96` plus follow-up text question:

- `select_one`: `${field} = '-96'`
- `select_multiple`: `selected(${field}, '-96')`

## Structured Output Contract

Translation execution must return:

```text
# XLSFORM_TRANSLATION_RESULT
status: completed|completed_with_warnings|dry_run|failed
intent: add_language|translate_remaining|...
mode: add-missing|update-all|header-sync|validate-only
summary:
  headers_added: <count>
  headers_renamed: <count>
  cells_translated: <count>
  cells_pending_translation: <count>
translation_runtime:
  backend: none|same-language|google
  ai_map_entries: <count>
```

## Validation Checklist

Before completion, verify:

1. Target-language headers exist in both `survey` and `choices`.
2. Header normalization did not corrupt any row values.
3. `default_language` handling is explicit (`set`, `updated`, or `no_change`).
4. Missing translation count is acceptable for the requested mode.
5. No translated output changed `choices.name` codes.
6. Placeholder parity is preserved in all translated cells.