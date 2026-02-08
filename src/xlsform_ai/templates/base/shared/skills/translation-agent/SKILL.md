---
name: translation-agent
description: Multilingual XLSForm specialist for language columns, contextual translations, and translation validation in survey/choices/settings.
---

# Translation Agent

This is the top-level translation skill entrypoint.

Use the same operational protocol as:

- `shared/skills/sub-agents/translation-agent/SKILL.md`

Core command:

```bash
python scripts/translate_form.py "<instruction>"
```

Default language label behavior:

- Use language names without shortcode by default (for example, `Bangla`).
- Add shortcode only when explicitly requested via `--include-language-code`.
