# Multilingual Translation Guide

This guide defines project standards for XLSForm multilingual work.

## Header Format

Use this pattern for translated columns:

- `<base_column>::<Language Name> (<language_code>)`

Examples:

- `label::Spanish (es)`
- `hint::Bangla (bn)`
- `constraint_message::French (fr)`

Use ASCII-friendly language labels by default (`Bangla`, `Spanish`, `French`).

## Translation Source Strategy

1. Preferred: AI-generated contextual translation maps (`--translation-map` or `--translation-map-file`).
2. Optional fallback: runtime translator via `--translator auto` when `deep-translator` is installed.
3. If no fallback is available, keep pending cells explicit in output and do not fail silently.

## Required Translation Coverage

When adding a language, add translated columns for:

- `label`
- `hint`
- `guidance_hint`
- `constraint_message`
- `required_message`
- `image`
- `audio`
- `video`

If `media::image`, `media::audio`, or `media::video` are used, apply the same language suffix pattern.

## Safety Rules

1. Read column positions from row 1 headers.
2. Never assume fixed column indexes.
3. Never reorder columns while normalizing headers.
4. Never shift or overwrite unrelated values.

## Translation Integrity

1. Keep placeholders unchanged (`${field}`).
2. Keep formulas and logic syntax unchanged.
3. Keep `choices.name` stable (never translate codes).
4. Keep translation terminology consistent across survey and choices.

## "Other" Standard

Avoid `or_other`.

Use:

1. explicit `-96` choice code in `choices`
2. follow-up `text` question in `survey`
3. relevance:
   - `select_one`: `${field} = '-96'`
   - `select_multiple`: `selected(${field}, '-96')`