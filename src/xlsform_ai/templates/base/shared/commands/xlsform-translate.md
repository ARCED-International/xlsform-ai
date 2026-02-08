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
- [MANDATORY] If an interactive question tool is available (`AskUserQuestion`, `request_user_input`, or client-native choice UI), use it.
- [PREFERRED] In interactive-tool mode, ask all pending decisions in one interactive panel as separate questions, each with 2-4 mutually exclusive options.
- [MANDATORY] Once interactive mode is available for a command/session, keep all subsequent required decisions in interactive mode unless the tool fails.
- [MANDATORY] Put the recommended option first and include a one-line tradeoff.
- [MANDATORY] Wait for explicit user selection before applying changes.
- [FALLBACK] If no interactive tool is available, ask in plain REPL text with numbered options.
- [FORBIDDEN] Do not switch from interactive prompts to plain-text follow-up decisions when interactive tools are still available.
- [FORBIDDEN] Do not make silent decisions on required conflicts.
- [FORBIDDEN] Do not ask open-ended combined preference text when structured options are possible.
- Example: if imported names raise warnings (e.g., q308_phq1, fiq_1), collect the required naming decision via interactive options and wait for selection.

## Implementation Protocol

### 1. Load Required Skills

```
/skill:xlsform-core
/skill:activity-logging
/skill:translation-agent
```

### Strict Script Policy

- `[REQUIRED]` Use existing entrypoint only: `scripts/translate_form.py`.
- `[REQUIRED]` For inspection/pre-checks, use `--dry-run --json` (never ad-hoc workbook probing).
- `[FORBIDDEN]` Do not use inline `python -c` for translation diagnostics.
- `[FORBIDDEN]` Do not create temporary `.py` scripts in workspace for translation tasks.
- `[FORBIDDEN]` Do not use `Workbook.get(...)`; when direct workbook access is unavoidable in maintained scripts, use `workbook["sheet_name"]` with existence checks.

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

When user explicitly wants shortcode in headers/settings values:

```bash
python scripts/translate_form.py "add Bangla language" --include-language-code
```

Preflight inspection (required before applying large translation changes):

```bash
python scripts/translate_form.py "<instruction>" --dry-run --json
```

### 3. Translation Mode Rules

- AI-first translation is the default approach:
  - generate contextual translations in the agent
  - pass them using `--translation-map` or `--translation-map-file`
- Runtime translation is optional fallback:
  - default is AI-only (`--translator none`)
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

### 4.1 Base Header Decision (Mandatory Prompt)

If source columns are unlabeled base columns (for example `label`, `hint`) ask user before writing:

1. Keep base columns as-is (recommended)
2. Convert base columns to source language form (for example `label` -> `label::English`)

Then run with:

- Preserve mode: `--base-language-mode preserve`
- Convert mode: `--base-language-mode english`

### 5. Row-1 Header Safety Rules

- Use row-1 header mapping for all reads/writes.
- Never rely on fixed column indexes.
- Never reorder existing columns.
- Never shift existing data values while adding/normalizing headers.
- If duplicate language columns exist, merge safely and report conflicts.
- Keep translation columns grouped after their base columns (for example `label`, then `label::Bangla`).

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

Choices sheet must include translation columns for:

- `label`
- `image`
- `audio`
- `video`

Header format:

- Default: `label::Bangla`, `hint::Bangla`
- Optional shortcode mode: `label::Bangla (bn)`, `hint::Bangla (bn)`

Use ASCII-friendly language display names by default (for example, `Bangla`, `Spanish`) and do not append shortcodes unless explicitly requested.

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



