---
description: Translate XLSForm content into additional languages using natural language commands. Adds missing language columns, normalizes row-1 translation headers safely, updates settings.default_language, and fills full or remaining translations in survey/choices.
arguments:
  - name: instruction
    description: Natural language translation instruction (e.g., "add Bangla language")
    required: true
---

# Translate XLSForm

## Conflict Decision Protocol

- [MANDATORY] If there is ambiguity, conflict, or multiple valid actions, do not decide silently.
- Present 2-4 REPL options and ask the user to choose before proceeding.
- Put the recommended option first and include a one-line tradeoff for each option.
- Wait for explicit user selection before applying changes.
- Only auto-decide when the user explicitly asked for automatic decisions.
- Example: if imported names raise warnings (e.g., q308_phq1, fiq_1), ask user whether to keep source names or apply semantic renaming.


## Implementation Protocol

### 1. Load Required Skills

```
/skill:xlsform-core
/skill:activity-logging
/skill:translation-agent
```

### 2. Use the Translation Script

Always execute translation through:

```bash
python scripts/translate_form.py "<instruction>"
```

Examples:

```bash
python scripts/translate_form.py "add Bangla language"
python scripts/translate_form.py "do the bangla translations for the remaining questions"

# AI-driven contextual translations (recommended)

python scripts/translate_form.py "add Bangla language" --translation-map-file .xlsform-ai/translation/bn.json

# Optional runtime fallback (uses deep-translator if installed)

python scripts/translate_form.py "add Bangla language" --translator auto
```

### 3. Translation Mode Rules

- AI-first translation is the default approach:
  - generate contextual translations in the agent
  - pass them using `--translation-map` or `--translation-map-file`
- Runtime translation is optional fallback:
  - `--translator auto` tries Google translation only if `deep-translator` is installed
  - if runtime translator is unavailable, the script reports pending cells instead of failing
- Optional fallback install:
  - `pip install -e ".[translate]"`

### 4. Natural Language Intent Rules

- `add <language> language`
  - add missing translation columns in `survey` and `choices`
  - normalize row-1 translation headers to canonical format
  - set `settings.default_language` if missing
  - translate all translatable cells for the target language
- `do the <language> translations for the remaining questions`
  - detect missing translations only
  - fill only missing target-language cells
  - preserve existing target-language values

### 5. Row-1 Header Safety Rules

- Use row-1 header mapping for all reads/writes.
- Never rely on fixed column indexes.
- Never reorder existing columns.
- Never shift existing data values while adding/normalizing headers.
- If duplicate language columns exist, merge safely and report conflicts.

### 6. Required Translatable Column Coverage

For each requested language, ensure translated columns for these bases (where applicable):

- `label`
- `hint`
- `guidance_hint`
- `constraint_message`
- `required_message`
- `image`
- `audio`
- `video`

Header format:

- `label::Spanish (es)`
- `hint::Spanish (es)`

Use ASCII-friendly language display names by default (for example, `Bangla`, `Spanish`).

### 7. "Other" Pattern Rule

Do not introduce `or_other` in translated workflows.
Use explicit `-96` option and follow-up text question with relevance:

- `select_one`: `${field} = '-96'`
- `select_multiple`: `selected(${field}, '-96')`

### 8. Structured Output Requirement

The script must produce:

```text
# XLSFORM_TRANSLATION_RESULT

status: ...
intent: ...
mode: ...
summary:
  headers_added: ...
  headers_renamed: ...
  cells_translated: ...
  cells_pending_translation: ...
translation_runtime:
  backend: none|same-language|google
  ai_map_entries: ...
```

When needed:

```bash
python scripts/translate_form.py "<instruction>" --json
```

### 9. Rollback Safety

- Translation writes must be snapshot-protected.
- If translation output is wrong, immediately use:

```bash
/xlsform-revert undo
```

or

```bash
/xlsform-revert restore-last
```


