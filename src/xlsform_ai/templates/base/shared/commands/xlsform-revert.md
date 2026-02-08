---
description: Safely revert XLSForm changes using immutable snapshots. Use this command to view history, create checkpoints, undo the last change, or restore a specific revision.
arguments:
  - name: action
    description: One of history, checkpoint, restore-last, restore, undo
    required: true
  - name: revision
    description: Revision ID for restore action
    required: false
  - name: label
    description: Checkpoint label for checkpoint action
    required: false
  - name: dry_run
    description: Preview restoration without writing changes
    required: false
---

# Revert XLSForm Safely

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

## Implementation Protocol

### 1. Load required skills

```
/skill:xlsform-core
/skill:activity-logging
```

### 2. Use the dedicated history script

Always use:

```bash
python scripts/form_history.py <subcommand> [options]
```

Subcommands:
- `list`
- `checkpoint "<label>"`
- `restore --revision <revision_id>`
- `restore-last`
- `undo`

### 3. Default to dry-run for restore operations

Before any restore:

```bash
python scripts/form_history.py restore --revision <revision_id> --dry-run
```

or

```bash
python scripts/form_history.py restore-last --dry-run
```

Run without `--dry-run` only after confirmation.

## Common Flows

### View history

```bash
python scripts/form_history.py list
```

### Create manual checkpoint

```bash
python scripts/form_history.py checkpoint "Before complex skip logic update"
```

### Undo latest change quickly

```bash
python scripts/form_history.py undo
```

### Restore to latest normal snapshot

```bash
python scripts/form_history.py restore-last
```

### Restore a specific revision

```bash
python scripts/form_history.py restore --revision 20260207121001-ab12cd34
```

## Safety Rules

- Every write command should create an immutable pre-change snapshot.
- Keep the workbook open if the user is observing changes live.
- Never use destructive git commands for XLSForm rollback.
- If restore fails, report error clearly and stop before further edits.




