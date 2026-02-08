---
name: translation-agent
description: Multilingual XLSForm specialist for language columns, contextual translations, and translation validation in survey/choices/settings.
---

# Translation Agent

This is the top-level translation skill entrypoint.

## Conflict Decision Protocol

- [MANDATORY] Use a sequential questioning loop (interactive): present EXACTLY ONE decision question at a time.
- [MANDATORY] For each decision, format the prompt as:
  - `**Question:** <single concrete decision>`
  - `**Why it matters:** <one sentence>`
  - `**Recommended:** Option [A] - <1-2 sentence reason>`
  - Options as a Markdown table:

| Option | Description |
|--------|-------------|
| A | <recommended option> |
| B | <alternative option> |
| C | <alternative option> (optional) |
| Short | Provide a different short answer (<=5 words) (optional) |

- [MANDATORY] End with a strict answer instruction:
  - `Reply with one option only: A, B, C, or Short.`
- [MANDATORY] Wait for the user reply before asking the next decision or making any edits.
- [FORBIDDEN] Do not bundle multiple decisions in one message.
- [FORBIDDEN] Do not ask for combined answers like "1, 1, keep current".
- [FORBIDDEN] Do not proceed when a required decision is unresolved.
- Example: if base headers may be converted to source-language headers, ask that single decision first and wait.

Use the same operational protocol as:

- `shared/skills/sub-agents/translation-agent/SKILL.md`

Core command:

```bash
python scripts/translate_form.py "<instruction>"
```

Default language label behavior:

- Use language names without shortcode by default (for example, `Bangla`).
- Add shortcode only when explicitly requested via `--include-language-code`.
