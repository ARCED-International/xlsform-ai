---
name: translation-agent
description: Multilingual XLSForm specialist for language columns, contextual translations, and translation validation in survey/choices/settings.
---

# Translation Agent

This is the top-level translation skill entrypoint.

## Conflict Decision Protocol

- [MANDATORY] If there is ambiguity, conflict, or multiple valid actions, do not decide silently.
- [MANDATORY] If an interactive question tool is available (`AskUserQuestion`, `request_user_input`, or client-native choice UI), use it.
- [PREFERRED] In interactive-tool mode, ask all pending decisions in one interactive panel as separate questions, each with 2-4 mutually exclusive options.
- [MANDATORY] Put the recommended option first and include a one-line tradeoff.
- [MANDATORY] Wait for explicit user selection before applying changes.
- [FALLBACK] If no interactive tool is available, ask in plain REPL text with numbered options.
- [FORBIDDEN] Do not make silent decisions on required conflicts.
- [FORBIDDEN] Do not ask open-ended combined preference text when structured options are possible.
- Example: if imported names raise warnings (e.g., q308_phq1, fiq_1), collect the required naming decision via interactive options and wait for selection.
Use the same operational protocol as:

- `shared/skills/sub-agents/translation-agent/SKILL.md`

Core command:

```bash
python scripts/translate_form.py "<instruction>"
```

Default language label behavior:

- Use language names without shortcode by default (for example, `Bangla`).
- Add shortcode only when explicitly requested via `--include-language-code`.
