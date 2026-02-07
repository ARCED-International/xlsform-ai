# Agent Capability Audit: Standards-Grade XLSForm (UN/WB/DIME/WHO/FAO)

Date: 2026-02-07
Status: Gap analysis + partial implementation completed (rollback foundation implemented)

## Implementation Update (2026-02-07)

Implemented in this cycle:
- Added rollback backend: `scripts/history_manager.py`
  - Immutable snapshot creation
  - Manifest logging (`.xlsform-ai/history/history.jsonl`)
  - Lock file guard for concurrent edits
  - Restore by revision with pre-restore safety snapshot
- Added rollback CLI helper: `scripts/form_history.py`
  - `list`, `checkpoint`, `restore`, `restore-last`, `undo`
- Integrated pre-change snapshots + lock into write paths:
  - `scripts/add_questions.py`
  - `scripts/add_metadata.py`
  - `scripts/settings_utils.py` (`set_form_settings`)
- Added new slash command spec:
  - `shared/commands/xlsform-revert.md`
  - `.claude/commands/xlsform-revert.md`
- Updated docs:
  - `README.md` (new rollback feature and usage)
  - `AGENT_MEMORY_TEMPLATE.md` command table now includes `/xlsform-revert`

Not yet completed:
- Full open-workbook write-mode with xlwings as default edit engine (current write scripts still use openpyxl).
- Operation-level undo journal (current undo is snapshot-based).
- Snapshot retention policy and cleanup automation.
- Advanced rollback diff visualization (`/xlsform-diff`) command implementation.

## 1) Objective
Assess whether the current multi-agent XLSForm system can reliably produce high-quality, low-error XLSForms that meet practical standards used in UN, World Bank/DIME, WHO, and FAO survey operations, including:
- Complex logic and skip/relevance
- Advanced calculations and dynamic reuse patterns
- Strong validation and quality controls
- Robust imports and repeatable workflows
- Historical protection with safe, fast reversibility of agent edits
- Open-workbook live editing so users can observe changes in real time

## 2) Method
- Local code and template audit of commands, skills, memory template, and scripts.
- Runtime smoke checks of key scripts.
- External standards mapping from primary documentation (XLSForm/ODK + WB/DIME + UN/WHO/FAO references).

## 3) Standards Baseline (What "good" looks like)

### XLSForm/ODK logic baseline
- Rich logic model: relevance, required, constraints, calculations, trigger-based recalculation, repeats, dynamic defaults, randomization, and advanced expressions.
- Critical syntax constraints: valid naming rules, select_multiple value naming constraints, list linking between survey/choices, structured settings.
- External/linked data patterns and dynamic reuse are expected in advanced forms.

Key references:
- XLSForm docs: https://xlsform.org/
- ODK form logic: https://docs.getodk.org/form-logic/
- ODK operators/functions: https://docs.getodk.org/form-operators-functions/
- ODK form design best practices: https://docs.getodk.org/form-design-best-practices/

### WB/DIME quality baseline
- Structured modular design, robust skip logic, validation rules, linked/roster-style question flows, and maintainable form architecture for large studies.
- Emphasis on pretesting and quality checks in CAPI workflows.

Key references:
- Survey Solutions docs (World Bank): https://docs.mysurvey.solutions/
- DIME Wiki (SurveyCTO and coding practices): https://dimewiki.worldbank.org/
- FAO + World Bank survey quality handbook: https://www.fao.org/documents/card/fr/c/ca5801en

### UN/WHO/FAO operations baseline
- Strict questionnaire governance, comparability, quality assurance, and careful skip/consistency handling.
- Strong procedural controls for field operations and metadata quality.

Key references:
- UNSD guidance (automated skips/consistency in CAPI context): https://unstats.un.org/
- UNHCR RMS questionnaire standardization guidance: https://im.unhcr.org/rms-data-collection-workflow/
- WHO STEPS implementation guidance: https://www.who.int/teams/noncommunicable-diseases/surveillance/systems-tools/steps/manuals-and-instruments
- WHO quality checklist (survey/interview process controls): https://www.who.int/publications/m/item/intimate-partner-violence-and-sexual-violence-against-women-survey-checklist
- FAO remote survey quality and planning guidance: https://www.fao.org/statistics/events/events-detail/new-publication--introduction-to-conducting-phone-surveys-and-guidance-on-best-practices/en

## 4) Current System Findings

## 4.1 Overall verdict
The system is **not yet** at reliable "high-quality standards-grade" capability for UN/WB/DIME/WHO/FAO workflows.

It is usable for basic XLSForm edits, but there are critical reliability and validation gaps for complex production forms.

## 4.2 Critical findings

1. Import scripts have runtime blockers
- `parse_pdf.py` and `parse_docx.py` reference `Path`/`sys` before imports (`src/xlsform_ai/templates/base/scripts/parse_pdf.py:11`, `src/xlsform_ai/templates/base/scripts/parse_docx.py:11`).
- Runtime check: both fail immediately with `NameError` on `--help`.
- Impact: PDF/Word import flow is currently broken at entry point.

2. Import command references missing script
- Command docs require `python scripts/parse_xlsx.py` (`src/xlsform_ai/templates/base/shared/commands/xlsform-import.md:125`, mirrored in `.claude` command file).
- `parse_xlsx.py` does not exist under `src/xlsform_ai/templates/base/scripts`.
- Impact: documented Excel import pathway is incomplete.

3. Validator is too shallow for complex logic safety
- Current validator checks mainly: required columns, duplicate question names, duplicate choice names (`src/xlsform_ai/templates/base/scripts/validate_form.py:104`, `src/xlsform_ai/templates/base/scripts/validate_form.py:118`, `src/xlsform_ai/templates/base/scripts/validate_form.py:147`, `src/xlsform_ai/templates/base/scripts/validate_form.py:168`).
- It does **not** validate key production constraints such as:
  - select list existence consistency
  - balanced begin/end group/repeat
  - expression reference integrity
  - choice_filter integrity
  - trigger/read_only/required formula quality
- Runtime check: a workbook with unclosed group + list_name mismatch was marked VALID.
- Impact: high false-negative risk for complex forms.

4. "Advanced" helper modules are mostly disconnected from main flow
- `add_questions.py` imports `QuestionTypeAnalyzer`, `ChoiceListOptimizer`, `OtherSpecifyHandler` (`src/xlsform_ai/templates/base/scripts/add_questions.py:65`), but usage is not wired for full pipeline behavior.
- Choice management in `add_questions.py` is not implemented as a full choices-sheet workflow.
- Impact: advanced logic assistance is documented but not consistently executed.

5. Sub-agent/parallel orchestration is largely declarative, not enforced end-to-end
- `complexity.py` exists, but repository usage is not integrated into actual command execution flow.
- Memory template claims automatic parallel/sub-agent behavior (`src/xlsform_ai/templates/base/shared/AGENT_MEMORY_TEMPLATE.md:388`), but runtime path is not operationally guaranteed.
- Impact: capability expectations exceed proven execution.

6. Dependency packaging is incomplete for key scripts
- Package dependencies in `pyproject.toml` do not include core script requirements like `openpyxl`, `pdfplumber`, `python-docx`.
- Impact: common workflows can fail in fresh installs unless users manually install extra packages.

7. Settings policy is over-opinionated and may conflict with diverse program standards
- `settings_utils.py` enforces a fixed `version` formula (`src/xlsform_ai/templates/base/scripts/settings_utils.py:16`, `src/xlsform_ai/templates/base/scripts/settings_utils.py:239`).
- While useful for some teams, hard enforcement can conflict with program-specific release/version governance.

8. Revertability is not first-class yet
- Mitigated in this cycle: dedicated rollback tooling added (`/xlsform-revert` command spec and `scripts/form_history.py` backend).
- Remaining gap: open-workbook write path is still mostly openpyxl-based and not yet fully xlwings-first.
- Remaining gap: operation-level undo journal and retention automation are still pending.

## 4.3 Capability vs requirement snapshot

| Capability area | Required for standards-grade | Current status |
| --- | --- | --- |
| Basic question add/update | Yes | Partial pass |
| Complex relevance/skip logic safety | Yes | Fail (validation depth gap) |
| Advanced calculations and dynamic reuse | Yes | Partial (possible text insertion, weak verification) |
| Robust import (PDF/Word/Excel) | Yes | Fail (runtime/import coverage gaps) |
| Structural integrity checks (groups/repeats) | Yes | Fail |
| Cross-sheet consistency checks | Yes | Fail |
| Standards alignment evidence (UN/WB/DIME/WHO/FAO) | Yes | Partial docs, weak enforcement |
| Reliable packaging/runtime out-of-box | Yes | Fail |
| Safe historical revert of agent edits | Yes | Fail |

## 5) Priority TODO Plan (No implementation yet)

### Phase 0: Stabilize hard blockers (P0)
1. Repair import script bootstrapping order (`parse_pdf.py`, `parse_docx.py`).
2. Add or remove `parse_xlsx.py` pathway consistently across docs and code.
3. Define and package required runtime dependencies by feature profile.
4. Add a startup self-check command that validates required deps and script entrypoints.

### Phase 0.5: Revert Safety Foundation (P0)
1. Add immutable pre-change snapshots for every XLSForm write operation.
- Store snapshot files under `.xlsform-ai/history/snapshots/`.
- Record metadata in append-only manifest (`history.jsonl`) with timestamp, agent, action, command, source hash, resulting hash.
2. Enforce open-workbook live-edit transaction workflow as the default mode (no temp editing of main file).
- Before edit, create snapshot (`SaveCopyAs` when workbook is open via Excel/xlwings).
- Apply edits directly to the main workbook so user can observe changes in real time.
- Capture per-operation undo journal (sheet, cell/range, old value, new value, formula/format deltas where applicable).
- On failure, auto-rollback from undo journal (fast path) or snapshot (hard rollback).
3. Keep atomic file-replace workflow only as a closed-workbook fallback mode.
- Use temp file + validate + atomic replace when workbook is not open.
- Do not use this path when user is observing a live open workbook session.
4. Add file lock and concurrency guard.
- Prevent two agents from editing the same workbook simultaneously.
- Return clear error and recovery steps when lock exists.
5. Define retention policy.
- Example: keep last 200 snapshots + daily checkpoint snapshots.
- Include configurable cleanup policy in `xlsform-ai.json`.

### Phase 0.6: Revert Commands and Recovery UX (P0/P1)
1. Add `/xlsform-revert <revision_id>` (safe default: dry-run summary first).
2. Add `/xlsform-history [--limit N]` to list revisions with metadata.
3. Add `/xlsform-diff <revision_id>` using normalized sheet-level diff (survey/choices/settings).
4. Add `/xlsform-checkpoint \"label\"` for manual milestones before risky edits.
5. Add `/xlsform-restore-last` fast path for immediate undo.
6. Add `/xlsform-undo` for immediate in-session rollback using operation journal.

### Phase 1: Validation engine for production safety (P0/P1)
1. Extend validator with structural checks:
- begin/end group and repeat balancing
- list_name existence checks for select questions
- select_multiple choice-name space rule
- duplicate policy with `allow_choice_duplicates`
2. Add expression reference checks:
- referenced fields exist
- basic parsing for relevance/constraint/calculation/trigger/read_only/required
3. Add settings checks:
- required fields present
- configurable version policy (not hardcoded only)
4. Add quality categories to output:
- blocking errors
- warnings
- best-practice suggestions

### Phase 2: Complex logic and dynamic reuse support (P1)
1. Implement a proper survey+choices transaction pipeline for select questions.
2. Wire currently isolated helpers (`QuestionTypeAnalyzer`, `ChoiceListOptimizer`, `OtherSpecifyHandler`) into main add/import flows.
3. Add explicit support patterns for:
- `indexed-repeat()`
- `jr:choice-name()`
- `random()` workflows
- external file select patterns and reuse logic
4. Add advanced logic templates (rosters, linked lists, dynamic defaults, trigger-driven calculations).

### Phase 3: Standards profiles and governance (P1/P2)
1. Add profile packs for `UN`, `WB/DIME`, `WHO`, `FAO` with rule presets and warnings.
2. Add profile-aware linting gates (strict mode) before marking form as "ready".
3. Add human review checklist outputs aligned to each profile.

### Phase 4: Verification and trust (P0/P1)
1. Build automated regression tests with fixture XLSForms:
- valid complex forms
- invalid structural/logic forms
- profile-specific edge cases
2. Add end-to-end tests for import -> transform -> validate.
3. Publish capability matrix with confidence levels per feature.

## 6) Reliable Revert Solutions (Recommended Stack)
1. Local immutable snapshot journal (recommended baseline)
- Reliability: High
- Works without git and with binary `.xlsx`.
- Deterministic restore by revision id.

2. Git-assisted checkpoints (recommended optional layer)
- Reliability: High when repo is clean and git is available.
- Auto-commit before/after each slash command when enabled.
- Enables team workflows and remote backup, but still keep local snapshot journal as primary rollback.

3. Canonical sidecar export for diffability
- Reliability: Medium-High
- Export normalized sheet JSON/CSV per revision to enable readable diffs despite binary XLSX.

4. Remote/object-storage backup mirror (optional for enterprise)
- Reliability: High for disaster recovery.
- Not required for local revert, but useful for governance and audit retention.

## 7) Suggested acceptance criteria for next implementation cycle
1. Import scripts run successfully with `--help` and sample files.
2. Validator catches known structural and cross-sheet logic defects.
3. At least one complex roster/dynamic reuse template validated end-to-end.
4. Standards profile checks produce deterministic pass/fail outcomes.
5. CI includes fixture-based tests for all critical logic classes.
6. Every edit creates a restorable immutable snapshot.
7. `/xlsform-revert` supports dry-run, restore, and verification post-restore.
8. Concurrent edit attempts are blocked with clear lock behavior.
9. Revert workflow is tested end-to-end in CI with fixture workbooks.
10. All edit commands work while `survey.xlsx` remains open in Excel.
11. `/xlsform-undo` and `/xlsform-revert` are verified in open-workbook sessions.
12. No command requires temporary editing of the main workbook in open mode.

## 8) Final assessment
Current state supports basic XLSForm work but does not yet meet reliable "high-quality standards-grade" expectations for complex UN/WB/DIME/WHO/FAO survey programming.

The main risk is not only missing features, but false confidence from docs that currently overstate runtime guarantees.
