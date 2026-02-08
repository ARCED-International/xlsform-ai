---
description: Alias for xlsform-translate. Translate XLSForm content into additional languages using natural language instructions.
arguments:
  - name: instruction
    description: Natural language translation instruction (e.g., "add Bangla language")
    required: true
---

# Translation Agent (Alias)

This command is an alias for `/xlsform-translate`.

Use the same translation workflow and safety rules:

1. Parse the natural-language instruction and detect target language.
2. Ensure translation headers exist in `survey` and `choices` for translatable columns.
3. Preserve row-1 header mapping and column order.
4. Update `settings.default_language` safely.
5. Fill translations for missing/all rows based on instruction mode.
6. Validate and report structured results.

Run:

```bash
python scripts/translate_form.py --file survey.xlsx --translator auto --language "<TargetLanguage>" "<instruction>"
```

Fallback if runtime translator is unavailable:

```bash
python scripts/translate_form.py --file survey.xlsx --translator none --language "<TargetLanguage>" "<instruction>"
```
