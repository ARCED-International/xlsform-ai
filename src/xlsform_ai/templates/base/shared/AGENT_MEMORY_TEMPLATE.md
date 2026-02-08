# XLSForm AI Project

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

This is an XLSForm project with AI-assisted development capabilities using multi-agent architecture.

**An open source project by [ARCED International](https://arced-international.com)**

---

# [WARNING] CRITICAL: MANDATORY LOGGING REQUIREMENT [WARNING]


## **EVERY XLSForm Modification MUST Be Logged - NO EXCEPTIONS**

**This is NOT optional. This is NOT a suggestion. This is MANDATORY.**

### When MUST You Log Activity?

**You MUST log activity AFTER EVERY modification to `survey.xlsx`:**

[OK] **AFTER adding questions** - Use `add_questions()` ÃƒÂ¢Ã¢â‚¬Â Ã¢â‚¬â„¢ **MUST LOG**
[OK] **AFTER updating questions** - Modify any field ÃƒÂ¢Ã¢â‚¬Â Ã¢â‚¬â„¢ **MUST LOG**
[OK] **AFTER removing questions** - Delete any row ÃƒÂ¢Ã¢â‚¬Â Ã¢â‚¬â„¢ **MUST LOG**
[OK] **AFTER moving questions** - Reorder anything ÃƒÂ¢Ã¢â‚¬Â Ã¢â‚¬â„¢ **MUST LOG**
[OK] **AFTER importing** - From PDF/Word/Excel ÃƒÂ¢Ã¢â‚¬Â Ã¢â‚¬â„¢ **MUST LOG**
[OK] **AFTER validating** - Even validation ÃƒÂ¢Ã¢â‚¬Â Ã¢â‚¬â„¢ **MUST LOG**

### How to Log (REQUIRED)

**Step 1:** Import the logger (DO THIS EVERY TIME):
```python
import sys
from pathlib import Path
sys.path.insert(0, str(Path('scripts')))

from log_activity import ActivityLogger
```

**Step 2:** Create logger and log (DO THIS AFTER EVERY CHANGE):
```python
logger = ActivityLogger()
logger.log_action(
    action_type="add_questions",  # or update_questions, remove_questions, etc.
    description="Added 3 question(s)",
    details="Questions: q1, q2, q3\nRows: 10, 11, 12"
)
```

### What Happens If You Don't Log?

[FAIL] **No audit trail** - Can't track who changed what
[FAIL] **Broken collaboration** - Team can't see changes
[FAIL] **Project management fails** - Can't review history
[FAIL] **Violates protocol** - Breaks the universal implementation protocol

### Simple Rule to Follow

**[CRITICAL] RED RULE: If survey.xlsx was modified, YOU MUST LOG IT.**

**No excuses. No exceptions. No skipping.**

**Before marking task complete, ask yourself: "Did I log this activity?"**
- If YES ÃƒÂ¢Ã¢â‚¬Â Ã¢â‚¬â„¢ Task complete [OK]
- If NO ÃƒÂ¢Ã¢â‚¬Â Ã¢â‚¬â„¢ LOG FIRST, then complete [OK]

---

# Table of Contents


1. [Executive Summary](#executive-summary) - Quick start guide
2. [Core Architecture](#core-architecture) - Multi-agent system, skills, sub-agents
3. [Implementation Protocols](#implementation-protocols) - Step-by-step workflows
4. [Reference Documentation](#reference-documentation) - Lookup information
5. [Advanced Patterns](#advanced-patterns) - Complex use cases
6. [Appendices](#appendices) - Supporting reference materials

---

# Executive Summary


## What is XLSForm AI?

XLSForm AI is an AI-powered toolkit for creating, modifying, and validating XLSForm surveys. It supports **17 different AI assistants** (Claude, Copilot, Gemini, Cursor, etc.) with equal capability, using a sophisticated multi-agent architecture that automatically scales from simple tasks to complex, parallel processing workflows.

## Quick Start

1. **Initialize project**: `xlsform-ai init --here`
2. **Use your preferred AI assistant**: Claude, Copilot, Cursor, Gemini, etc.
3. **Add questions**: `/xlsform-add Add a text question asking for name`
4. **Import from PDF**: `/xlsform-import questionnaire.pdf --pages 1-10`
5. **Validate**: `/xlsform-validate` (always validate after changes)

## Key Capabilities

- [OK] **17 AI assistants supported** - Use whichever you prefer
- [OK] **Automatic question type detection** - From natural language
- [OK] **PDF/Word/Excel import** - Parse existing questionnaires
- [OK] **Smart form validation** - Catch errors before deployment
- [OK] **Automatic parallel processing** - For large tasks (50+ questions, 10+ pages)
- [OK] **Activity logging** - Track all changes with audit trail
- [OK] **Multi-language support** - Built-in translation workflows
- [OK] **Knowledge base integration** - XLSForm best practices at your fingertips

## Quick Reference Card

| Category | Item | Description |
|----------|------|-------------|
| **Main File** | `survey.xlsx` | Primary XLSForm file in project root |
| **Config** | `xlsform-ai.json` | Project settings and agent configuration |
| **Scripts** | `scripts/*.py` | Utility modules for form manipulation |
| **Activity Log** | `activity_log.html` | Browser-based audit trail |

### Slash Commands

| Command | Purpose | Example |
|---------|---------|---------|
| `/xlsform-add` | Add questions | `/xlsform-add Add age question` |
| `/xlsform-import` | Import from files | `/xlsform-import survey.pdf` |
| `/xlsform-validate` | Validate form | `/xlsform-validate --fix` |
| `/xlsform-update` | Modify questions | `/xlsform-update Add constraint to age` |
| `/xlsform-remove` | Delete questions | `/xlsform-remove Remove q1` |
| `/xlsform-move` | Reorder questions | `/xlsform-move Move name to top` |
| `/xlsform-translate` | Translate multilingual columns (AI-first, optional runtime fallback) | `/xlsform-translate add Bangla language` |
| `/xlsform-revert` | Restore previous revisions | `/xlsform-revert restore-last` |

### Essential Skills

| Skill | Purpose | Usage |
|-------|---------|-------|
| `xlsform-core` | XLSForm syntax & best practices | **Always use before XLSForm work** |
| `activity-logging` | Activity tracking protocols | **Always use before XLSForm work** |

### File Paths

```
Project Root/
ÃƒÂ¢Ã¢â‚¬ÂÃ…â€œÃƒÂ¢Ã¢â‚¬ÂÃ¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬ÂÃ¢â€šÂ¬ survey.xlsx              # Main XLSForm file
ÃƒÂ¢Ã¢â‚¬ÂÃ…â€œÃƒÂ¢Ã¢â‚¬ÂÃ¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬ÂÃ¢â€šÂ¬ xlsform-ai.json          # Configuration
ÃƒÂ¢Ã¢â‚¬ÂÃ…â€œÃƒÂ¢Ã¢â‚¬ÂÃ¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬ÂÃ¢â€šÂ¬ activity_log.html        # Activity audit trail
ÃƒÂ¢Ã¢â‚¬ÂÃ…â€œÃƒÂ¢Ã¢â‚¬ÂÃ¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬ÂÃ¢â€šÂ¬ scripts/                 # Python utility modules
ÃƒÂ¢Ã¢â‚¬ÂÃ¢â‚¬ÂÃƒÂ¢Ã¢â‚¬ÂÃ¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬ÂÃ¢â€šÂ¬ {agent}/                 # Agent-specific config
    ÃƒÂ¢Ã¢â‚¬ÂÃ…â€œÃƒÂ¢Ã¢â‚¬ÂÃ¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬ÂÃ¢â€šÂ¬ commands/            # Slash commands
    ÃƒÂ¢Ã¢â‚¬ÂÃ¢â‚¬ÂÃƒÂ¢Ã¢â‚¬ÂÃ¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬ÂÃ¢â€šÂ¬ skills/              # Knowledge packages
```

---

# Core Architecture


## Multi-Agent System

XLSForm AI supports **17 AI assistants with equal capability**. The system is agent-agnostic - all assistants have access to the same features, skills, and sub-agents.

### Supported Agents

**Core Agents (Production-Ready):**
- Claude (`.claude/`) - Anthropic's AI assistant
- GitHub Copilot (`.copilot/`) - GitHub's coding assistant
- Gemini (`.gemini/`) - Google's AI assistant
- Cursor (`.cursor/`) - AI-first code editor
- Qwen (`.qwen/`) - Alibaba's AI assistant
- OpenCode (`.opencode/`) - Open source focused
- Codex (`.codex/`) - OpenAI Codex-based CLI
- Windsurf (`.windsurf/`) - Next-gen development
- KiloCode (`.kilocode/`) - Efficient code handling
- Auggie (`.auggie/`) - Lightweight and fast
- CodeBuddy (`.codebuddy/`) - Helpful companion
- Qoder (`.qoder/`) - Smart code completion
- Roo Code (`.roo/`) - Intelligent generation
- Amp (`.amp/`) - Amplify your coding
- Shai (`.shai/`) - European AI solution

**Community Agents (Supported):**
- Amazon Q Developer (`.amazon-q/`) - AWS integration (limited command support)
- IBM Bob (`.bob/`) - Enterprise focused

### What Each Agent Gets During Init

When you run `xlsform-ai init`, each agent receives:

1. **Custom directory structure** - e.g., `.claude/`, `.copilot/`, `.gemini/`
2. **Shared skills** - `xlsform-core`, `activity-logging` (same for all agents)
3. **Shared commands** - All 8 slash commands (same for all agents)
4. **Agent-specific memory file** - Copied from shared template:
   - Claude ÃƒÂ¢Ã¢â‚¬Â Ã¢â‚¬â„¢ `.claude/CLAUDE.md`
   - Copilot ÃƒÂ¢Ã¢â‚¬Â Ã¢â‚¬â„¢ `.copilot/MEMORY.md`
   - Gemini ÃƒÂ¢Ã¢â‚¬Â Ã¢â‚¬â„¢ `.gemini/GEMINI.md`
   - Cursor ÃƒÂ¢Ã¢â‚¬Â Ã¢â‚¬â„¢ `.cursor/MEMORY.md`
   - And so on...
5. **Full sub-agent access** - All agents can use validation-agent, import-agent, etc.

### Agent-Agnostic Design

The system ensures **feature parity** across all agents:
- [OK] All agents can add questions
- [OK] All agents can import from PDF/Word/Excel
- [OK] All agents can validate forms
- [OK] All agents can use sub-agents for parallel processing
- [OK] All agents log activities automatically

## Skill System

Skills are reusable knowledge packages that provide specialized information to AI assistants.

### Main Skills

**Two critical skills that MUST be used before any XLSForm operation:**

#### 1. xlsform-core

**Purpose:** Comprehensive XLSForm knowledge

**Provides:**
- XLSForm syntax and structure
- All question types with examples
- Constraint and relevance patterns
- Choice list management
- Validation rules
- Best practices

**Usage (varies by agent):**
- Claude: `/skill:xlsform-core`
- Cursor: `Use skill xlsform-core`
- Copilot: `@skill xlsform-core`

**Knowledge sources:**
- `xlsform-core/references/question-types.md` - Complete type reference
- `xlsform-core/references/syntax-guide.md` - XLSForm structure
- `xlsform-core/references/settings-sheet.md` - Settings sheet rules
- `xlsform-core/references/validation-rules.md` - Validation criteria
- `xlsform-core/references/common-patterns.md` - Reusable patterns

#### 2. activity-logging

**Purpose:** Activity tracking protocols

**Provides:**
- When to log activities
- How to log activities
- Action type reference
- Log viewing instructions

**Usage:**
- Claude: `/skill:activity-logging`
- Cursor: `Use skill activity-logging`
- Copilot: `@skill activity-logging`

**Knowledge sources:**
- `activity-logging/SKILL.md` - Complete logging guide

### How Skills Work

1. **Agent loads skill** - Agent reads skill file to gain knowledge
2. **Knowledge auto-loads** - Skill references additional documentation
3. **Context-aware** - Skills provide relevant information based on task
4. **Reusable** - Same skill works across all 17 agents

### When to Use Skills

**MANDATORY:** Always load both skills before XLSForm operations:
```
/skill:xlsform-core
/skill:activity-logging
```

**Optional:** Load specialist skills for specific tasks:
```
/skill:translation-agent  # For multi-language forms
```

## Sub-Agent Architecture

Sub-agents are specialist agents that handle specific tasks. They automatically activate for large tasks or can be manually invoked.

### The 5 Specialist Sub-Agents

#### 1. validation-agent

**Specialty:** XLSForm syntax and structure validation

**Capabilities:**
- Detect duplicate names
- Validate question types
- Check choice list references
- Verify constraint syntax
- Identify best practices violations

**Auto-activates:** 100+ questions

**Used in:**
- After form modifications
- During import workflows
- Before deployment

#### 2. import-agent

**Specialty:** PDF, Word, Excel parsing

**Capabilities:**
- Extract questions from PDF
- Parse Word documents
- Read Excel spreadsheets
- Auto-detect question types
- Identify choice lists

**Auto-activates:** 10+ pages or 1MB+ file size

**Used in:**
- `/xlsform-import` command
- Large document processing

#### 3. export-agent

**Specialty:** Format conversion

**Capabilities:**
- Convert to XForm XML
- Convert to PyXForm JSON
- ODK-specific formats
- KoboToolbox formats
- CommCare formats

**Auto-activates:** Manual activation only

**Used in:**
- Deployment workflows
- Platform migration

#### 4. schema-agent

**Specialty:** Form structure analysis

**Capabilities:**
- Analyze question dependencies
- Identify optimization opportunities
- Detect circular references
- Suggest improvements
- Map form structure

**Auto-activates:** 50+ questions

**Used in:**
- Complex form design
- Structure optimization
- Import workflows

#### 5. translation-agent

**Specialty:** Multi-language management

**Capabilities:**
- Manage translations
- Cultural adaptation
- Language validation
- Translation workflows

**Auto-activates:** Manual activation only

**Used in:**
- Multi-language form creation
- Translation management

### Sub-Agent Coordination

Sub-agents work together in workflows:

**Import Workflow:**
```
import-agent (parallel chunks)
    ÃƒÂ¢Ã¢â‚¬Â Ã¢â‚¬Å“
schema-agent (analyze structure)
    ÃƒÂ¢Ã¢â‚¬Â Ã¢â‚¬Å“
validation-agent (validate all)
```

**Export Workflow:**
```
schema-agent (analyze)
    ÃƒÂ¢Ã¢â‚¬Â Ã¢â‚¬Å“
export-agent (convert)
```

**Translation Workflow:**
```
translation-agent (translate)
    ÃƒÂ¢Ã¢â‚¬Â Ã¢â‚¬Å“
validation-agent (validate)
```

## Parallel Processing

For large tasks, XLSForm AI automatically uses parallel processing with sub-agents.

### Automatic Activation Thresholds

| Task Type | Threshold | Parallel Strategy |
|-----------|-----------|-------------------|
| Question validation | 100+ questions | Chunk validation, merge results |
| PDF import | 10+ pages | Split by page ranges |
| Word import | 1MB+ file | Split by sections |
| Excel import | 1MB+ file | Split by row count |
| Form analysis | 50+ questions | Analyze sections in parallel |

### Parallel Processing Workflow

**Example:** Import 100 questions from 25-page PDF

```
Task: Import 100 questions from PDF

[Analysis] 100 questions, 25 pages ÃƒÂ¢Ã¢â‚¬Â Ã¢â‚¬â„¢ High complexity
[Decision] Using parallel import (5 chunks)

[PARALLEL PHASE]
  ÃƒÂ¢Ã¢â‚¬ÂÃ…â€œÃƒÂ¢Ã¢â‚¬ÂÃ¢â€šÂ¬ [Chunk 1] import-agent: Pages 1-5 ÃƒÂ¢Ã¢â‚¬Â Ã¢â‚¬â„¢ 20 questions
  ÃƒÂ¢Ã¢â‚¬ÂÃ…â€œÃƒÂ¢Ã¢â‚¬ÂÃ¢â€šÂ¬ [Chunk 2] import-agent: Pages 6-10 ÃƒÂ¢Ã¢â‚¬Â Ã¢â‚¬â„¢ 18 questions
  ÃƒÂ¢Ã¢â‚¬ÂÃ…â€œÃƒÂ¢Ã¢â‚¬ÂÃ¢â€šÂ¬ [Chunk 3] import-agent: Pages 11-15 ÃƒÂ¢Ã¢â‚¬Â Ã¢â‚¬â„¢ 22 questions
  ÃƒÂ¢Ã¢â‚¬ÂÃ…â€œÃƒÂ¢Ã¢â‚¬ÂÃ¢â€šÂ¬ [Chunk 4] import-agent: Pages 16-20 ÃƒÂ¢Ã¢â‚¬Â Ã¢â‚¬â„¢ 19 questions
  ÃƒÂ¢Ã¢â‚¬ÂÃ¢â‚¬ÂÃƒÂ¢Ã¢â‚¬ÂÃ¢â€šÂ¬ [Chunk 5] import-agent: Pages 21-25 ÃƒÂ¢Ã¢â‚¬Â Ã¢â‚¬â„¢ 21 questions

[SEQUENTIAL PHASE]
  ÃƒÂ¢Ã¢â‚¬ÂÃ…â€œÃƒÂ¢Ã¢â‚¬ÂÃ¢â€šÂ¬ schema-agent: Analyze form structure
  ÃƒÂ¢Ã¢â‚¬ÂÃ¢â‚¬ÂÃƒÂ¢Ã¢â‚¬ÂÃ¢â€šÂ¬ validation-agent: Validate all questions

[FINAL] Apply to survey.xlsx
```

### Manual Override

Force parallel processing:
```python
# Use command-level parallel workflows (import-agent/validation-agent).
# Do not pass parallel=True to add_questions; that argument is unsupported.
# Example command:
/xlsform-import large_file.pdf
```

Force sequential processing:
```
# Use --sequential flag

/xlsform-import large_file.pdf --sequential
```

## File Structure

```
.
ÃƒÂ¢Ã¢â‚¬ÂÃ…â€œÃƒÂ¢Ã¢â‚¬ÂÃ¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬ÂÃ¢â€šÂ¬ survey.xlsx                  # Main XLSForm file (edit this!)
ÃƒÂ¢Ã¢â‚¬ÂÃ…â€œÃƒÂ¢Ã¢â‚¬ÂÃ¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬ÂÃ¢â€šÂ¬ xlsform-ai.json              # Project configuration
ÃƒÂ¢Ã¢â‚¬ÂÃ…â€œÃƒÂ¢Ã¢â‚¬ÂÃ¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬ÂÃ¢â€šÂ¬ activity_log.html            # Activity audit trail
ÃƒÂ¢Ã¢â‚¬ÂÃ…â€œÃƒÂ¢Ã¢â‚¬ÂÃ¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬ÂÃ¢â€šÂ¬ package.json                 # npm scripts for watch/reload
ÃƒÂ¢Ã¢â‚¬ÂÃ¢â‚¬Å¡
ÃƒÂ¢Ã¢â‚¬ÂÃ…â€œÃƒÂ¢Ã¢â‚¬ÂÃ¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬ÂÃ¢â€šÂ¬ scripts/                     # Utility scripts
ÃƒÂ¢Ã¢â‚¬ÂÃ¢â‚¬Å¡   ÃƒÂ¢Ã¢â‚¬ÂÃ…â€œÃƒÂ¢Ã¢â‚¬ÂÃ¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬ÂÃ¢â€šÂ¬ config.py                # Configuration management
ÃƒÂ¢Ã¢â‚¬ÂÃ¢â‚¬Å¡   ÃƒÂ¢Ã¢â‚¬ÂÃ…â€œÃƒÂ¢Ã¢â‚¬ÂÃ¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬ÂÃ¢â€šÂ¬ form_structure.py        # Form parsing and smart insertion
ÃƒÂ¢Ã¢â‚¬ÂÃ¢â‚¬Å¡   ÃƒÂ¢Ã¢â‚¬ÂÃ…â€œÃƒÂ¢Ã¢â‚¬ÂÃ¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬ÂÃ¢â€šÂ¬ add_questions.py         # Question addition (with smart insertion)
ÃƒÂ¢Ã¢â‚¬ÂÃ¢â‚¬Å¡   ÃƒÂ¢Ã¢â‚¬ÂÃ…â€œÃƒÂ¢Ã¢â‚¬ÂÃ¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬ÂÃ¢â€šÂ¬ log_activity.py          # Activity logging (with filterable UI)
ÃƒÂ¢Ã¢â‚¬ÂÃ¢â‚¬Å¡   ÃƒÂ¢Ã¢â‚¬ÂÃ…â€œÃƒÂ¢Ã¢â‚¬ÂÃ¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬ÂÃ¢â€šÂ¬ validate_form.py         # XLSForm validation
ÃƒÂ¢Ã¢â‚¬ÂÃ¢â‚¬Å¡   ÃƒÂ¢Ã¢â‚¬ÂÃ…â€œÃƒÂ¢Ã¢â‚¬ÂÃ¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬ÂÃ¢â€šÂ¬ parse_pdf.py             # PDF question extraction
ÃƒÂ¢Ã¢â‚¬ÂÃ¢â‚¬Å¡   ÃƒÂ¢Ã¢â‚¬ÂÃ…â€œÃƒÂ¢Ã¢â‚¬ÂÃ¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬ÂÃ¢â€šÂ¬ parse_docx.py            # Word question extraction
ÃƒÂ¢Ã¢â‚¬ÂÃ¢â‚¬Å¡   ÃƒÂ¢Ã¢â‚¬ÂÃ…â€œÃƒÂ¢Ã¢â‚¬ÂÃ¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬ÂÃ¢â€šÂ¬ parse_xlsx.py            # Excel question extraction
ÃƒÂ¢Ã¢â‚¬ÂÃ¢â‚¬Å¡   ÃƒÂ¢Ã¢â‚¬ÂÃ…â€œÃƒÂ¢Ã¢â‚¬ÂÃ¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬ÂÃ¢â€šÂ¬ xlwings_helper.py        # Excel editing with xlwings
ÃƒÂ¢Ã¢â‚¬ÂÃ¢â‚¬Å¡   ÃƒÂ¢Ã¢â‚¬ÂÃ¢â‚¬ÂÃƒÂ¢Ã¢â‚¬ÂÃ¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬ÂÃ¢â€šÂ¬ knowledge_base/          # Best practices and patterns
ÃƒÂ¢Ã¢â‚¬ÂÃ¢â‚¬Å¡       ÃƒÂ¢Ã¢â‚¬ÂÃ¢â‚¬ÂÃƒÂ¢Ã¢â‚¬ÂÃ¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬ÂÃ¢â€šÂ¬ data/                # Knowledge base documents
ÃƒÂ¢Ã¢â‚¬ÂÃ¢â‚¬Å¡
ÃƒÂ¢Ã¢â‚¬ÂÃ…â€œÃƒÂ¢Ã¢â‚¬ÂÃ¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬ÂÃ¢â€šÂ¬ {agent-specific}/            # AI assistant configuration
ÃƒÂ¢Ã¢â‚¬ÂÃ¢â‚¬Å¡   ÃƒÂ¢Ã¢â‚¬ÂÃ…â€œÃƒÂ¢Ã¢â‚¬ÂÃ¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬ÂÃ¢â€šÂ¬ commands/                # Slash commands
ÃƒÂ¢Ã¢â‚¬ÂÃ¢â‚¬Å¡   ÃƒÂ¢Ã¢â‚¬ÂÃ¢â‚¬Å¡   ÃƒÂ¢Ã¢â‚¬ÂÃ…â€œÃƒÂ¢Ã¢â‚¬ÂÃ¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬ÂÃ¢â€šÂ¬ xlsform-add.md       # Add questions
ÃƒÂ¢Ã¢â‚¬ÂÃ¢â‚¬Å¡   ÃƒÂ¢Ã¢â‚¬ÂÃ¢â‚¬Å¡   ÃƒÂ¢Ã¢â‚¬ÂÃ…â€œÃƒÂ¢Ã¢â‚¬ÂÃ¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬ÂÃ¢â€šÂ¬ xlsform-import.md    # Import from files
ÃƒÂ¢Ã¢â‚¬ÂÃ¢â‚¬Å¡   ÃƒÂ¢Ã¢â‚¬ÂÃ¢â‚¬Å¡   ÃƒÂ¢Ã¢â‚¬ÂÃ…â€œÃƒÂ¢Ã¢â‚¬ÂÃ¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬ÂÃ¢â€šÂ¬ xlsform-validate.md  # Validate form
ÃƒÂ¢Ã¢â‚¬ÂÃ¢â‚¬Å¡   ÃƒÂ¢Ã¢â‚¬ÂÃ¢â‚¬Å¡   ÃƒÂ¢Ã¢â‚¬ÂÃ…â€œÃƒÂ¢Ã¢â‚¬ÂÃ¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬ÂÃ¢â€šÂ¬ xlsform-update.md    # Modify questions
ÃƒÂ¢Ã¢â‚¬ÂÃ¢â‚¬Å¡   ÃƒÂ¢Ã¢â‚¬ÂÃ¢â‚¬Å¡   ÃƒÂ¢Ã¢â‚¬ÂÃ…â€œÃƒÂ¢Ã¢â‚¬ÂÃ¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬ÂÃ¢â€šÂ¬ xlsform-remove.md    # Delete questions
ÃƒÂ¢Ã¢â‚¬ÂÃ¢â‚¬Å¡   ÃƒÂ¢Ã¢â‚¬ÂÃ¢â‚¬Å¡   ÃƒÂ¢Ã¢â‚¬ÂÃ…â€œÃƒÂ¢Ã¢â‚¬ÂÃ¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬ÂÃ¢â€šÂ¬ xlsform-move.md      # Reorder questions
ÃƒÂ¢Ã¢â‚¬ÂÃ¢â‚¬Å¡   ÃƒÂ¢Ã¢â‚¬ÂÃ¢â‚¬Å¡   ÃƒÂ¢Ã¢â‚¬ÂÃ¢â‚¬ÂÃƒÂ¢Ã¢â‚¬ÂÃ¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬ÂÃ¢â€šÂ¬ xlsform-translate.md # Translate multilingual columns
ÃƒÂ¢Ã¢â‚¬ÂÃ¢â‚¬Å¡   ÃƒÂ¢Ã¢â‚¬ÂÃ¢â‚¬Å¡
ÃƒÂ¢Ã¢â‚¬ÂÃ¢â‚¬Å¡   ÃƒÂ¢Ã¢â‚¬ÂÃ¢â‚¬ÂÃƒÂ¢Ã¢â‚¬ÂÃ¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬ÂÃ¢â€šÂ¬ skills/                  # XLSForm knowledge
ÃƒÂ¢Ã¢â‚¬ÂÃ¢â‚¬Å¡       ÃƒÂ¢Ã¢â‚¬ÂÃ…â€œÃƒÂ¢Ã¢â‚¬ÂÃ¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬ÂÃ¢â€šÂ¬ xlsform-core/        # Core XLSForm skill
ÃƒÂ¢Ã¢â‚¬ÂÃ¢â‚¬Å¡       ÃƒÂ¢Ã¢â‚¬ÂÃ¢â‚¬Å¡   ÃƒÂ¢Ã¢â‚¬ÂÃ¢â‚¬ÂÃƒÂ¢Ã¢â‚¬ÂÃ¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬ÂÃ¢â€šÂ¬ references/      # XLSForm reference docs
ÃƒÂ¢Ã¢â‚¬ÂÃ¢â‚¬Å¡       ÃƒÂ¢Ã¢â‚¬ÂÃ¢â‚¬ÂÃƒÂ¢Ã¢â‚¬ÂÃ¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬ÂÃ¢â€šÂ¬ activity-logging/    # Activity logging skill
ÃƒÂ¢Ã¢â‚¬ÂÃ¢â‚¬Å¡
ÃƒÂ¢Ã¢â‚¬ÂÃ¢â‚¬ÂÃƒÂ¢Ã¢â‚¬ÂÃ¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬ÂÃ¢â€šÂ¬ {agent-specific}/            # Other configured agents
    ÃƒÂ¢Ã¢â‚¬ÂÃ…â€œÃƒÂ¢Ã¢â‚¬ÂÃ¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬ÂÃ¢â€šÂ¬ commands/                # (same commands, copied to each agent)
    ÃƒÂ¢Ã¢â‚¬ÂÃ¢â‚¬ÂÃƒÂ¢Ã¢â‚¬ÂÃ¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬ÂÃ¢â€šÂ¬ skills/                  # (same skills, copied to each agent)
```

**Note:** All configured agents receive the same commands and skills. The system ensures consistency across all agents.

Offline validator location:
- `tools/ODK-Validate.jar` (installed/updated during `xlsform-ai init`)

---

# Implementation Protocols


## Universal Implementation Protocol

**CRITICAL: All agents MUST follow this protocol for ALL XLSForm operations**

This protocol ensures consistency, prevents errors, and maintains activity logs.

### Phase 1: Preparation

**Step 1: Load Required Skills**

```bash
/skill:xlsform-core
/skill:activity-logging
```

**Why:** Skills provide essential knowledge about XLSForm syntax and logging protocols.

**Step 2: Check Configuration**

```python
from scripts.config import ProjectConfig

config = ProjectConfig()
xlsform_file = config.get_xlsform_file()  # Get configured file name
log_enabled = config.is_activity_logging_enabled()
```

**Why:** Ensures you're working with the correct file and settings.

**Step 3: Verify File State**

```python
from pathlib import Path

xlsx_path = Path(xlsform_file)
if not xlsx_path.exists():
    raise FileNotFoundError(f"{xlsform_file} not found")

# Check if file is open (for xlwings vs openpyxl decision)

```

**Why:** Determines whether to use xlwings (open file) or openpyxl (closed file).

### Phase 2: Execution

**Step 4: Import from Scripts Directory ONLY**

```python
import sys
from pathlib import Path
sys.path.insert(0, str(Path('scripts')))

from form_structure import FormStructure
from add_questions import add_questions
from log_activity import ActivityLogger
```

**CRITICAL:** NEVER import from other locations. ALWAYS use `scripts/` directory.

**Why:** Ensures consistent access to utility modules and prevents import errors.

**Step 5: Use Appropriate Helper Functions**

```python
# Example: Adding questions

questions = [
    {
        'type': 'text',
        'name': 'respondent_name',
        'label': 'What is your name?'
    }
]

add_questions(questions, survey_file=xlsx_path)
```

**Why:** Helper functions handle smart insertion, validation, and formatting.

**CRITICAL: Column Mapping Rule**

**Never assume fixed column positions.** Always read headers from row 1 and build a column map before writing.
Use `build_column_mapping()` from `form_structure` to locate columns like `constraint`, `relevant`, etc.

**Applies to ALL sheets** (`survey`, `choices`, `settings`). For `settings`, always locate the header in row 1, then write the value to row 2 in the same column.

**Settings Sheet Rules (Project Standard):**
- Row 1 headers, Row 2 values (single values row).
- Settings sheet is optional but recommended. If present, include `form_title`, `form_id`, `version`.
- `version` is a string; common convention is `yyyymmddrr`.
- Columns can appear in any order. Always map headers before writing.
- Common headers: `instance_name`, `default_language`, `public_key`, `submission_url`, `style`,
  `name`, `clean_text_values`, `allow_choice_duplicates`.
- Instance name suggestions are allowed (e.g., include key IDs + `uuid()`), but still written in row 2.

**Standard Metadata (Default Include Unless User Opts Out):**
- Always include standard metadata fields in the **survey** sheet unless the user says not to.
- Metadata types: `start`, `end`, `today`, `deviceid`, `phonenumber`, `username`, `email`, `audit`.
- Always include **labels** for readability; metadata is still auto-captured.
- Audit note: location tracking only in ODK Collect (not Enketo webforms) and configured via `parameters`.
- GPS for a location should use a normal `geopoint` question (not metadata).

**Step 6: Apply Changes with Error Handling**

```python
try:
    # Make changes to XLSForm
    add_questions(questions, survey_file=xlsx_path)
    print(f"SUCCESS: Added {len(questions)} questions")
except Exception as e:
    print(f"ERROR: {e}")
    # Provide actionable error message
    raise
```

**Why:** Graceful error handling prevents data corruption and provides helpful feedback.

**CRITICAL: Missing Settings Reminder (Agent Output, Not Console)**

If `form_title` or `form_id` are missing after any XLSForm operation, the agent MUST explicitly remind the user in a highly noticeable format (e.g., bold banner or "ACTION REQUIRED" line). This reminder is part of the agent's response text, not a console print. It must appear every time until both are set, and should include how to set them (settings sheet row 2 or `xlsform-ai update-settings --title ... --id ...`).

### Phase 3: Finalization

**Step 7: [WARNING] LOG ACTIVITY (MANDATORY - NON-NEGOTIABLE) [WARNING]**

**[ALERT] THIS STEP IS NOT OPTIONAL. YOU MUST LOG EVERY XLSFORM MODIFICATION.**

```python
# Import these EVERY TIME (add to top of your script)

import sys
from pathlib import Path
sys.path.insert(0, str(Path('scripts')))

from log_activity import ActivityLogger

# After making changes to survey.xlsx, YOU MUST LOG:

logger = ActivityLogger()
logger.log_action(
    action_type="add_questions",  # Be specific: add_questions, update_questions, remove_questions, etc.
    description=f"Added {len(questions)} question(s)",  # Brief summary
    details=f"Questions: {', '.join([q['name'] for q in questions])}\nRows: {row_numbers}"  # Full details
)

# Verify logging worked

print(f"[OK] Activity logged to: activity_log.html")
```

**[CRITICAL] CRITICAL - NON-NEGOTIABLE REQUIREMENTS:**

1. **MUST import from `scripts/` directory** - Use `sys.path.insert(0, str(Path('scripts')))`
2. **MUST create ActivityLogger instance** - `logger = ActivityLogger()`
3. **MUST call log_action()** - With action_type, description, and details
4. **MUST confirm logging worked** - Print success message
5. **MUST do this AFTER EVERY modification** - No exceptions, no skipping

**IF YOU SKIP LOGGING, YOU HAVE FAILED THE TASK.**

**Why:** Provides audit trail, enables change tracking, supports collaboration, and is REQUIRED by the universal protocol.

**Verification:** Before completing any task, confirm:
- [OK] `logger.log_action()` was called
- [OK] Success message was printed
- [OK] `activity_log.html` was updated

**Step 8: Validate Changes**

```python
import json
import subprocess
import sys

result = subprocess.run(
    [sys.executable, "scripts/validate_form.py", str(xlsx_path), "--json"],
    capture_output=True,
    text=True,
    check=False
)
report = json.loads(result.stdout)
odk_raw = report["details"]["odk_validate"].get("raw_output") or "none"

print("Validation summary:", report["summary"])
print("ODK status:", report["engines"]["odk_validate"]["status"])
print("Exact ODK validator output (verbatim):")
print(odk_raw)

if result.returncode != 0:
    print("WARNING: validation reported blocking errors")
else:
    print("SUCCESS: Form validated successfully")
```

**Why:** Catches errors before deployment.

**Step 9: Report Results with Specific Row Numbers**

```python
print(f"SUCCESS: Added {len(questions)} questions")
print(f"  Questions added to rows: {', '.join(map(str, row_numbers))}")
print(f"  File: {xlsx_path}")
```

**Why:** Specific row numbers help users locate changes in Excel.

### What NOT To Do

[FAIL] **NEVER skip skill loading** - Always use `/skill:xlsform-core` and `/skill:activity-logging`
[FAIL] **NEVER import from other locations** - Always use `scripts/` directory
[FAIL] **[ALERT] NEVER SKIP ACTIVITY LOGGING - THIS IS MANDATORY FOR EVERY XLSFORM MODIFICATION [ALERT]**
[FAIL] **NEVER skip validation** - Always validate after changes
[FAIL] **NEVER work directly without helper functions** - Always use scripts modules

### [WARNING] REMEMBER: THE RED RULE [WARNING]

**[CRITICAL] If survey.xlsx was modified, YOU MUST LOG IT. NO EXCEPTIONS.**

**Before completing ANY task, verify:**
1. [OK] Did I import `ActivityLogger` from `scripts/log_activity`?
2. [OK] Did I call `logger.log_action()` with full details?
3. [OK] Did I print the success message?
4. [OK] Did I verify `activity_log.html` was updated?

**If answer to ANY is NO ÃƒÂ¢Ã¢â‚¬Â Ã¢â‚¬â„¢ LOG FIRST, then complete.**

## Command-Specific Protocols

### /xlsform-add Protocol

**Purpose:** Add new questions to the form

**When to use:**
- Adding single questions
- Adding small batches of questions (< 50)
- Quick form modifications

**Protocol:**

1. Load skills: `/skill:xlsform-core`, `/skill:activity-logging`
2. Import: `from scripts.add_questions import add_questions`
3. Prepare questions list with type, name, label
4. Add to form: `add_questions(questions)`
5. Log action: `logger.log_action(action_type="add_questions", ...)`
6. Validate: `/xlsform-validate`

**Example:**

```python
import sys
from pathlib import Path
sys.path.insert(0, str(Path('scripts')))

from add_questions import add_questions
from log_activity import ActivityLogger

questions = [
    {
        'type': 'text',
        'name': 'respondent_name',
        'label': 'What is your name?',
        'required': True
    },
    {
        'type': 'integer',
        'name': 'age',
        'label': 'How old are you?',
        'constraint': '. >= 0 and . <= 120',
        'constraint_message': 'Age must be 0-120'
    }
]

add_questions(questions, survey_file='survey.xlsx')

logger = ActivityLogger()
logger.log_action(
    action_type="add_questions",
    description=f"Added {len(questions)} question(s)",
    details=f"Questions: {', '.join([q['name'] for q in questions])}"
)
```

**Parallel threshold:** 50+ questions (auto-activates parallel add)

**Common mistakes:**
- Forgetting to load skills first
- Not providing unique question names
- Skipping validation after adding
- Not logging the action

### /xlsform-import Protocol

**Purpose:** Import questions from PDF, Word, or Excel files

**When to use:**
- Importing questionnaire from PDF
- Converting Word form to XLSForm
- Migrating Excel spreadsheet to XLSForm

**Protocol:**

1. Load skills: `/skill:xlsform-core`, `/skill:activity-logging`
2. Do not create ad-hoc import scripts in project workspace. Use existing scripts first.
3. Run parser entrypoints directly (preferred, avoids import-path bugs):
   - PDF: `python scripts/parse_pdf.py <source> --pages <range> [--auto-scale] --output <json>`
   - Word: `python scripts/parse_docx.py <source> [--media-dir <dir> --media-prefix <prefix> --auto-scale] --output <json>`
   - Excel: `python scripts/parse_xlsx.py <source> [--sheet <name>] --output <json>`
4. For Word with images, ask user media destination in REPL (recommended: `./media/<source_stem>`)
5. If user chooses auto-convert for frequency/Likert, pass `--auto-scale`.
6. Load parser JSON output and map payload to `add_questions` input format.
7. Detect large file: If 10+ pages or 1MB+, auto-activate import-agent (parallel)
8. Add survey rows via `add_questions(questions, survey_file='survey.xlsx')` (ensure media headers are present)
9. Add choices rows, including `media::image` for choice images when available
10. Verify user-selected transforms were applied (for auto-convert, report converted count + sample names)
11. Log action: `logger.log_action(action_type=\"import_pdf\"|\"import_docx\"|\"import_xlsx\", ...)`
12. Validate: `/xlsform-validate`

**FORBIDDEN in normal flow:**
- `python - <<'PY' ... PY` (heredoc inline Python)
- `python -c "..."` for parser orchestration
- creating ad-hoc import scripts in project root

Use parser script entrypoints directly unless explicit user-approved fallback is required.

**Example:**

```python
import sys
import json
import subprocess
from pathlib import Path
sys.path.insert(0, str(Path('scripts')))

from add_questions import add_questions
from log_activity import ActivityLogger

# Extract questions from PDF via script entrypoint
subprocess.run(
    [
        sys.executable,
        'scripts/parse_pdf.py',
        'questionnaire.pdf',
        '--pages',
        '1-10',
        '--output',
        'tmp_import.json',
    ],
    check=True,
)
with open('tmp_import.json', 'r', encoding='utf-8') as fh:
    payload = json.load(fh)
questions = payload.get('questions', [])

# Add to form

add_questions(questions, survey_file='survey.xlsx')

# Log activity

logger = ActivityLogger()
logger.log_action(
    action_type="import_pdf",
    description=f"Imported {len(questions)} questions from PDF",
    details=f"Source: questionnaire.pdf\nPages: 1-10\nQuestions: {len(questions)}"
)
```

DOCX with images example:
```python
from parse_docx import extract_questions

questions = extract_questions(
    'questionnaire.docx',
    media_dir='media/questionnaire',
    media_prefix='questionnaire',
    auto_scale=True,
)
```

**Parallel threshold:** 10+ pages or 1MB+ file size

**Sub-agents used:**
- import-agent (parallel chunks)
- schema-agent (analyze structure)
- validation-agent (validate all)

**File type considerations:**
- **PDF:** Supports text and table extraction; scanned-image PDFs still require OCR
- **Word:** Supports text, tables, mixed layouts, and embedded image extraction to media files
- **Excel:** Best for structured data, requires column mapping

### /xlsform-validate Protocol

**Purpose:** Validate form for errors and best practices

**When to use:**
- After any form modification
- Before deployment
- When investigating errors
- As part of CI/CD pipeline

**Protocol:**

1. Load skills: `/skill:xlsform-core`, `/skill:activity-logging`
2. Run: `python scripts/validate_form.py survey.xlsx --json`
3. Parse JSON report, especially:
   - `summary`
   - `engines.local`
   - `engines.odk_validate`
   - `details.odk_validate.raw_output`
4. Report results:
   - Structured summary table with status tags: `[PASS]`, `[WARN]`, `[FAIL]`
   - Engine status table (local + ODK)
   - Exact ODK validator output in a verbatim `text` block
5. Log action: `logger.log_action(action_type="validate", ...)`

**Required final response shape:**
- `Validation Summary` table (errors/warnings/suggestions)
- `Engine Status` table (local + odk_validate)
- `Exact ODK Validator Output` fenced `text` block with exact text from `details.odk_validate.raw_output` (or `none`)

**Example:**

```python
import sys
from pathlib import Path
import json
sys.path.insert(0, str(Path('scripts')))

from log_activity import ActivityLogger
import subprocess
import sys

result = subprocess.run(
    [sys.executable, "scripts/validate_form.py", "survey.xlsx", "--json"],
    capture_output=True,
    text=True,
    check=False
)

# Parse and report

report = json.loads(result.stdout)
odk_raw = report["details"]["odk_validate"].get("raw_output") or "none"
print("summary:", report["summary"])
print("engines:", report["engines"])
print("Exact ODK validator output:")
print(odk_raw)

# Log activity

logger = ActivityLogger()
logger.log_action(
    action_type="validate",
    description=f"Form validation {'passed' if result.returncode == 0 else 'failed'}",
    details="See structured validator output in console"
)
```

**Error categories:**
1. **Critical Errors** (must fix):
   - Duplicate question names
   - Invalid question types
   - Missing choice lists
   - Unbalanced groups/repeats
   - Invalid name syntax

2. **Warnings** (should fix):
   - Missing constraint messages
   - Missing required messages
   - Labels missing for begin_group
   - Suspicious formulas

3. **Suggestions** (nice to have):
   - Naming convention improvements
   - Reusable choice list opportunities
   - Helpful hints for complex questions

**Auto-fix capabilities:**
- `/xlsform-validate --fix` - Automatically fix simple issues:
  - Correct obvious typos in type (selct_one ÃƒÂ¢Ã¢â‚¬Â Ã¢â‚¬â„¢ select_one)
  - Add missing constraint_message with generic text
  - Remove duplicate columns

**Parallel threshold:** 100+ questions

### /xlsform-update Protocol

**Purpose:** Modify existing questions

**When to use:**
- Updating question labels
- Adding constraints
- Modifying question types
- Changing required status
- Adding relevance logic

**Protocol:**

1. Load skills: `/skill:xlsform-core`, `/skill:activity-logging`
2. Import: `from scripts.form_structure import FormStructure`
3. Find question: Search by name or row number
4. Read current values: `form_structure.get_question(question_name)`
5. Apply changes: Update specific cells
6. Log action: `logger.log_action(action_type="update_questions", ...)`
7. Validate: `/xlsform-validate`

**Example:**

```python
import sys
from pathlib import Path
sys.path.insert(0, str(Path('scripts')))

from form_structure import FormStructure
from log_activity import ActivityLogger

# Find question

form = FormStructure(worksheet, header_row)
question = form.get_question('age')

# Update constraint

question['constraint'] = '. >= 18 and . <= 100'
question['constraint_message'] = 'Age must be 18-100'

# Save changes

# ... implementation depends on openpyxl/xlwings ...


# Log activity

logger = ActivityLogger()
logger.log_action(
    action_type="update_questions",
    description=f"Updated question: age",
    details=f"Changes: Added constraint (. >= 18 and . <= 100)\nRow: {question['row']}"
)
```

**Search strategies:**
1. **By name:** Exact match on question name
2. **By label:** Partial match on label text
3. **By row:** Direct row number access
4. **By type:** All questions of a specific type

### /xlsform-remove Protocol

**Purpose:** Delete questions or choice lists

**When to use:**
- Removing unused questions
- Cleaning up test data
- Deleting deprecated fields
- Removing entire choice lists

**Protocol:**

1. Load skills: `/skill:xlsform-core`, `/skill:activity-logging`
2. Import: `from scripts.form_structure import FormStructure`
3. Find question: Locate target question or list
4. **Check dependencies:**
   - Is question referenced in relevance?
   - Is question used in calculations?
   - Is choice list used by any question?
5. Confirm intent: Show what will be affected
6. Remove: Delete row(s)
7. Log action: `logger.log_action(action_type="remove_questions", ...)`
8. Validate: `/xlsform-validate`

**Example:**

```python
import sys
from pathlib import Path
sys.path.insert(0, str(Path('scripts')))

from form_structure import FormStructure
from log_activity import ActivityLogger

# Find question

form = FormStructure(worksheet, header_row)
question = form.get_question('old_question')

# Check dependencies

dependencies = form.find_dependencies('old_question')
if dependencies:
    print(f"WARNING: Question is used in:")
    for dep in dependencies:
        print(f"  - {dep}")
    # Get user confirmation

# Remove question

worksheet.delete_rows(question['row'])

# Log activity

logger = ActivityLogger()
logger.log_action(
    action_type="remove_questions",
    description=f"Removed question: old_question",
    details=f"Row: {question['row']}\nType: {question['type']}"
)
```

**Safety checks:**
1. Check for dependent questions (relevance, calculations)
2. Check if choice list is in use
3. Warn about unbalanced groups/repeats
4. Confirm before destructive changes

**What NOT to remove:**
- begin_group/end_group without removing contents first
- Questions used in other questions' relevance
- Choice lists still referenced by select questions

### /xlsform-move Protocol

**Purpose:** Reorder questions in the form

**When to use:**
- Reorganizing question flow
- Grouping related questions
- Moving questions to different sections
- Fixing question order

**Protocol:**

1. Load skills: `/skill:xlsform-core`, `/skill:activity-logging`
2. Import: `from scripts.form_structure import FormStructure`
3. Find question: Locate question to move
4. Determine new location:
   - Insertion point (after which row?)
   - Smart insertion (after metadata, after group, etc.)
5. Move question: Cut and insert at new location
6. Log action: `logger.log_action(action_type="move_questions", ...)`
7. Validate: `/xlsform-validate`

**Example:**

```python
import sys
from pathlib import Path
sys.path.insert(0, str(Path('scripts')))

from form_structure import FormStructure, find_insertion_row
from log_activity import ActivityLogger

# Find question

form = FormStructure(worksheet, header_row)
question = form.get_question('name')

# Find new location

insert_after_row = find_insertion_row(worksheet, 'demographics_end')
worksheet.move_row(question['row'], insert_after_row)

# Log activity

logger = ActivityLogger()
logger.log_action(
    action_type="move_questions",
    description=f"Moved question: name",
    details=f"From row: {old_row}\nTo row: {new_row}\nAfter: demographics section"
)
```

**Insertion strategies:**
1. **After metadata** - Insert after start/end/deviceid fields
2. **After group** - Insert at end of specific group
3. **Before question** - Insert immediately before specified question
4. **At position** - Insert at specific row number

**Caution:** Moving questions can break relevance logic if not careful. Always validate after moving.

## Error Handling Protocol

Systematic approach to handling errors in XLSForm operations.

### Error Categories

#### 1. Configuration Errors

**Examples:**
- `xlsform-ai.json` missing or corrupted
- Invalid agent configuration
- Missing file path configuration

**Detection:**
```python
from scripts.config import ProjectConfig

try:
    config = ProjectConfig()
except Exception as e:
    print(f"ERROR: Configuration error: {e}")
    print("Solution: Re-initialize project with 'xlsform-ai init'")
```

**Recovery:**
- Re-initialize project: `xlsform-ai init --here`
- Manually fix `xlsform-ai.json`
- Restore from backup if available

**Prevention:**
- Validate config on startup
- Check for required fields
- Use default values for missing options

#### 2. File Access Errors

**Examples:**
- `survey.xlsx` not found
- File is locked by another process
- Insufficient permissions

**Detection:**
```python
from pathlib import Path

xlsx_path = Path('survey.xlsx')
if not xlsx_path.exists():
    raise FileNotFoundError(f"{xlsx_path} not found")

if not xlsx_path.is_file():
    raise ValueError(f"{xlsx_path} is not a file")

# Check file permissions

if not os.access(xlsx_path, os.R_OK | os.W_OK):
    raise PermissionError(f"Cannot read/write {xlsx_path}")
```

**Recovery:**
- Check file path is correct
- Close file in Excel if open
- Check file permissions
- Use alternative file (openpyxl vs xlwings)

**Prevention:**
- Always check file exists before operations
- Verify file state (open/closed)
- Check read/write permissions

#### 3. Validation Errors

**Examples:**
- Duplicate question names
- Invalid question types
- Missing choice lists
- Syntax errors in constraints/relevance

**Detection:**
```python
import json
import subprocess
import sys

result = subprocess.run(
    [sys.executable, "scripts/validate_form.py", "survey.xlsx", "--json"],
    capture_output=True,
    text=True,
    check=False
)

report = json.loads(result.stdout)
print(report["summary"])
print("Exact ODK validator output:")
print(report["details"]["odk_validate"].get("raw_output") or "none")
if result.returncode != 0:
    print("CRITICAL ERRORS FOUND")
    # Do not proceed with deployment
```

**Recovery:**
1. Run `/xlsform-validate` to get full error report
2. Fix errors manually or with `/xlsform-validate --fix`
3. Re-validate after fixes
4. Only deploy when no critical errors remain

**Prevention:**
- Always validate after changes
- Use unique question names
- Test constraints and relevance logic
- Verify choice lists exist before using

#### 4. Import Errors

**Examples:**
- PDF file is scanned images (needs OCR)
- Word document has unexpected structure
- Excel file has no headers
- File format not supported

**Detection:**
```python
try:
    questions = extract_questions(source_path)
except Exception as e:
    print(f"ERROR: Failed to import: {e}")
    print("Solution: Check file format and structure")
```

**Recovery:**
- Verify file format (PDF, Word, Excel)
- Check file is not corrupted
- Try alternative parser
- Manual entry if automatic fails
- OCR for scanned PDFs

**Prevention:**
- Validate file format before import
- Check file size and page count
- Preview file structure
- Use appropriate parser for file type

#### 5. Activity Log Errors

**Examples:**
- Log file permissions error
- Template file missing
- Log file corrupted

**Detection:**
```python
try:
    logger = ActivityLogger()
    logger.log_action(...)
except Exception as e:
    print(f"WARNING: Could not log activity: {e}")
    print("Continuing without logging...")
```

**Recovery:**
- Check file permissions
- Recreate log file
- Disable logging in config if needed
- Continue with operation (non-critical)

**Prevention:**
- Check permissions on startup
- Verify template exists
- Handle logging gracefully (don't fail operation)

### Error Handling Best Practices

1. **Try-except wrappers:** Wrap all file operations
2. **Specific exceptions:** Catch specific exceptions, not generic Exception
3. **Helpful messages:** Provide actionable error messages
4. **Graceful degradation:** Continue if non-critical error
5. **Log errors:** Log error details for debugging
6. **User communication:** Report errors clearly to user
7. **Recovery suggestions:** Suggest how to fix the error

### Example Error Handling Pattern

```python
def safe_operation(xlsx_path):
    """Pattern for safe XLSForm operations"""
    try:
        # Check configuration
        config = ProjectConfig()

        # Check file exists
        if not Path(xlsx_path).exists():
            raise FileNotFoundError(f"File not found: {xlsx_path}")

        # Perform operation
        result = perform_operation(xlsx_path)

        # Validate result
        errors = validate_operation(result)
        if errors:
            raise ValueError(f"Validation failed: {errors}")

        # Log success
        logger.log_action(action_type="operation", ...)

        return result

    except FileNotFoundError as e:
        print(f"ERROR: {e}")
        print("Solution: Check file path and try again")
        return None

    except PermissionError as e:
        print(f"ERROR: Permission denied: {e}")
        print("Solution: Close file in Excel or check permissions")
        return None

    except Exception as e:
        print(f"ERROR: Unexpected error: {e}")
        print("Solution: Contact support with error details")
        # Log error for debugging
        logger.log_action(action_type="error", details=str(e))
        return None
```

## Activity Logging Protocol

**CRITICAL: ALL XLSForm modifications MUST be logged to the activity log**

### Why Log Activities?

- Tracks collaboration and changes over time
- Provides audit trail for project management
- Essential for multi-user projects
- Helps review and undo changes
- Enables change analysis and reporting

### Step-by-Step Logging

**Step 1: Check if Logging is Enabled**

```python
from scripts.config import ProjectConfig

config = ProjectConfig()
if config.is_activity_logging_enabled():
    # Proceed with logging
```

**Step 2: Import Activity Logger**

```python
from scripts.log_activity import ActivityLogger

logger = ActivityLogger()  # Uses current directory
```

**Step 3: Log the Action**

```python
logger.log_action(
    action_type="add_questions",  # See table below
    description="Brief description of what changed",
    details="Full details with question names, row numbers, etc."
)
```

**Step 4: View the Log**

Open `activity_log.html` in your browser to see:
- Complete activity history
- Filter by action type, author, date range
- Search across descriptions and details
- Export to CSV or JSON
- Sort by any column
- Pagination for large logs

### Action Types

Use these specific `action_type` values:

| Action Type | When to Use | Example Description |
|-------------|-------------|-------------------|
| `add_questions` | Adding new questions | "Added 3 question(s)" |
| `update_questions` | Modifying existing questions | "Updated question: age" |
| `remove_questions` | Deleting questions | "Removed 2 question(s)" |
| `validate` | Running form validation | "Form validation completed" |
| `import_pdf` | Importing from PDF | "Imported 15 questions from PDF" |
| `import_docx` | Importing from Word | "Imported 10 questions from Word" |
| `import_xlsx` | Importing from Excel | "Imported 20 questions from Excel" |
| `analyze_structure` | Analyzing form structure | "Analyzed form structure" |
| `cleanup` | Cleaning up unused items | "Cleaned up 5 unused lists" |

### Logging Examples

**Adding Questions:**

```python
logger = ActivityLogger()
logger.log_action(
    action_type="add_questions",
    description=f"Added {len(questions)} question(s)",
    details=f"Questions: {', '.join([q['name'] for q in questions])}\nRows: {', '.join(map(str, row_numbers))}"
)
```

**Updating Questions:**

```python
logger = ActivityLogger()
logger.log_action(
    action_type="update_questions",
    description=f"Updated question: {question_name}",
    details=f"Question: {question_name}\nChanges: Added constraint (. >= 0 and . <= 120)\nRow: {row_number}"
)
```

**Removing Questions:**

```python
logger = ActivityLogger()
logger.log_action(
    action_type="remove_questions",
    description=f"Removed {count} question(s)",
    details=f"Questions: {', '.join(question_names)}\nRows: {', '.join(map(str, row_numbers))}"
)
```

**Validating Form:**

```python
logger = ActivityLogger()
logger.log_action(
    action_type="validate",
    description=f"Form validation {'passed' if is_valid else 'failed'}",
    details=f"Errors: {error_count}\nWarnings: {warning_count}\nSuggestions: {suggestion_count}"
)
```

**Importing from PDF:**

```python
logger = ActivityLogger()
logger.log_action(
    action_type="import_pdf",
    description=f"Imported {count} questions from PDF",
    details=f"Source: {pdf_path}\nPages: {pages}\nQuestions: {question_summary}"
)
```

### Important Reminders

- **NEVER skip activity logging** for XLSForm modifications
- **ALWAYS import from** `scripts/` directory
- **ALWAYS use the skills** (`xlsform-core`, `activity-logging`)
- Users can disable logging in `xlsform-ai.json` if needed
- Activity log is preserved across re-initializations

---

# Reference Documentation


## Configuration Reference

Project settings are stored in `xlsform-ai.json` in the project root.

### Complete Configuration Options

```json
{
  "version": "1.0",
  "project_name": "My Survey Project",
  "xlsform_file": "survey.xlsx",
  "created": "2025-02-04T10:30:00",
  "last_modified": "2025-02-04T14:15:00",
  "author": "Your Name",
  "author_location": "Your Location",
  "enabled_agents": ["claude", "cursor", "copilot"],
  "primary_agent": "claude",
  "settings": {
    "auto_validate": true,
    "log_activity": true,
    "backup_before_changes": false,
    "parallel_execution": {
      "enabled": true,
      "question_threshold": 50,
      "page_threshold": 10,
      "size_threshold_mb": 1.0,
      "user_preference": "auto"
    }
  }
}
```

### Configuration Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `version` | string | "1.0" | Config file version |
| `project_name` | string | Required | Project identifier for activity logs |
| `xlsform_file` | string | "survey.xlsx" | Main XLSForm file name |
| `created` | datetime | Auto-set | Project creation timestamp |
| `last_modified` | datetime | Auto-set | Last modification timestamp |
| `author` | string | Auto-detected | Author name |
| `author_location` | string | Auto-detected | Author location |
| `enabled_agents` | array | ["claude"] | Configured AI assistants |
| `primary_agent` | string | First agent | Default AI assistant |

### Settings Options

| Setting | Type | Default | Description |
|---------|------|---------|-------------|
| `auto_validate` | boolean | true | Automatically validate after changes |
| `log_activity` | boolean | true | Enable activity logging |
| `backup_before_changes` | boolean | false | Create backups before modifications |

### Parallel Execution Settings

| Setting | Type | Default | Description |
|---------|------|---------|-------------|
| `enabled` | boolean | true | Enable parallel processing |
| `question_threshold` | integer | 50 | Questions threshold for parallel |
| `page_threshold` | integer | 10 | PDF pages threshold for parallel |
| `size_threshold_mb` | float | 1.0 | File size threshold (MB) |
| `user_preference` | string | "auto" | "auto", "always", or "never" |

### Changing Configuration

**Check current configuration:**
```bash
cat xlsform-ai.json
```

**Change XLSForm file name:**
```bash
python scripts/config.py set-file my_custom_form.xlsx
```

**Disable activity logging:**
```bash
python scripts/config.py set-setting log_activity false
```

**Re-initialize protection:**
When re-initializing a project, these files are **never overwritten**:
- XLSForm survey file (e.g., survey.xlsx)
- Activity log files (activity_log_*.html)

## Script Module Reference

**Available Script Modules (import from scripts/ directory ONLY):**

### Core Modules

#### form_structure.py

**Purpose:** Parse and analyze XLSForm structure

**Key Classes/Functions:**
- `FormStructure` class - Parse and analyze form
- `find_insertion_row()` - Smart row placement for new questions
- `is_metadata_field()` - Check if field type is metadata
- `find_header_row()` - Locate header row in sheet
- `build_column_map()` - Map column names to positions

**Usage:**
```python
from scripts.form_structure import FormStructure

form = FormStructure(worksheet, header_row)
structure = form.structure  # Get parsed structure
```

#### add_questions.py

**Purpose:** Add questions to XLSForm

**Key Functions:**
- `add_questions()` - Main function to add questions
- `get_best_practices()` - Suggest constraints/required flags from type/name/label

**Usage:**
```python
from scripts.add_questions import add_questions

questions = [{'type': 'text', 'name': 'q1', 'label': 'Name'}]
add_questions(questions, survey_file='survey.xlsx')
```

#### validate_form.py

**Purpose:** Validate XLSForm for errors

**Primary Interface:**
- `python scripts/validate_form.py survey.xlsx`
- Structured output marker: `# XLSFORM_VALIDATION_RESULT`
- JSON output option: `python scripts/validate_form.py survey.xlsx --json`
- Offline path: XLSForm -> XForm (pyxform) -> `tools/ODK-Validate.jar`
- Common engine statuses: `completed`, `jar_not_found`, `java_not_found`, `pyxform_not_found`, `xform_conversion_failed`
- Exact ODK output path in JSON: `details.odk_validate.raw_output`
- For user-facing responses, present summary and engine tables plus verbatim ODK output block

**Programmatic Function:**
- `validate_xlsxform()` returns `(errors, warnings, suggestions)` for local checks

**Usage:**
```python
from scripts.validate_form import validate_xlsxform

errors, warnings, suggestions = validate_xlsxform('survey.xlsx')
```

#### log_activity.py

**Purpose:** Activity tracking and logging

**Key Classes:**
- `ActivityLogger` - Logging interface
  - `log_action()` - Record activity
  - `get_log_html()` - Generate HTML log

**Usage:**
```python
from scripts.log_activity import ActivityLogger

logger = ActivityLogger()
logger.log_action(
    action_type="add_questions",
    description="Added 3 questions",
    details="Questions: q1, q2, q3"
)
```

#### config.py

**Purpose:** Configuration management

**Key Classes:**
- `ProjectConfig` - Configuration interface
  - `get_xlsform_file()` - Get XLSForm file path
  - `is_activity_logging_enabled()` - Check logging status
  - `get_setting()` - Get specific setting

**Usage:**
```python
from scripts.config import ProjectConfig

config = ProjectConfig()
xlsx_file = config.get_xlsform_file()
```

#### xlwings_helper.py

**Purpose:** Excel editing with xlwings (for open files)

**Key Functions:**
- `get_workbook()` - Get Excel workbook
- `set_cell_value()` - Set cell value with formatting
- `save_workbook()` - Save changes

**Usage:**
```python
from scripts.xlwings_helper import get_workbook, set_cell_value

wb = get_workbook('survey.xlsx')
set_cell_value(wb.sheets['survey'], row, col, value)
```

### Import Modules

#### parse_pdf.py

**Purpose:** Extract questions from PDF files

**Key Functions:**
- `extract_questions()` - Parse PDF and extract questions
- `parse_questions_from_lines()` - Parse text lines into questions
- `parse_questions_from_table()` - Parse table rows into questions

**Usage:**
```python
from scripts.parse_pdf import extract_questions

questions = extract_questions('questionnaire.pdf', pages='1-10')
```

#### parse_docx.py

**Purpose:** Extract questions from Word documents

**Key Functions:**
- `extract_questions_from_docx()` - Parse text, tables, and mixed layouts
- `extract_questions()` - Compatibility wrapper with media options
- `--media-dir/--media-prefix` - Control exported image path and XLSForm media reference prefix

**Usage:**
```python
from scripts.parse_docx import extract_questions_from_docx

questions = extract_questions_from_docx(
    'questionnaire.docx',
    media_dir='media/questionnaire',
    media_prefix='questionnaire',
)
```

#### parse_xlsx.py

**Purpose:** Extract questions from Excel spreadsheets

**Key Functions:**
- `extract_questions_from_xlsx()` - Parse Excel
- `read_sheet()` - Read specific sheet

**Usage:**
```python
from scripts.parse_xlsx import extract_questions_from_xlsx

questions = extract_questions_from_xlsx('workbook.xlsx', sheet='Questions')
```

### Import Best Practices

**ALWAYS import from scripts/ directory:**
```python
import sys
from pathlib import Path
sys.path.insert(0, str(Path('scripts')))

from form_structure import FormStructure
from add_questions import add_questions
```

**NEVER import from other locations.**

## XLSForm Syntax Quick Reference

### Question Types

**Text Input:**
- `text` - Short text input
- `integer` - Whole numbers
- `decimal` - Decimal numbers
- `note` - Display-only text

**Select:**
- `select_one listname` - Single choice
- `select_multiple listname` - Multiple choices

**Date/Time:**
- `date` - Date picker
- `time` - Time picker
- `dateTime` - Date and time picker

**Geo:**
- `geopoint` - GPS coordinates
- `geotrace` - GPS path/line
- `geoshape` - GPS polygon/area

**Media:**
- `image` - Photo capture
- `audio` - Audio recording
- `video` - Video recording

**Metadata:**
- `start` - Form start timestamp
- `end` - Form end timestamp
- `today` - Current date
- `deviceid` - Device identifier
- `audit` - Audit trail metadata

### Common Patterns

**Conditional question:**
```
relevant: ${previous_question} = 'yes'
```

**Constraint:**
```
constraint: . >= 0 and . <= 120
constraint_message: Value must be 0-120
```

**Required field:**
```
required: yes
required_message: This field is required
```

**Cascading select:**
```
choice_filter: parent_field=${parent_field}
```

**Calculation:**
```
calculate: ${field1} + ${field2}
```

**Dynamic label:**
```
label: Age of ${respondent_name}
```

**For more details:** Use `/skill:xlsform-core` for comprehensive syntax reference

## Sub-Agent Capabilities Matrix

| Sub-Agent | Auto-Activate Threshold | Capabilities | Coordination |
|-----------|------------------------|--------------|--------------|
| **validation-agent** | 100+ questions | - Duplicate detection<br>- Type validation<br>- Choice list verification<br>- Best practices check | Used after all modifications<br>- Part of import/export workflows |
| **import-agent** | 10+ pages or 1MB+ | - PDF parsing<br>- Word extraction<br>- Excel reading<br>- Type detection | Parallel chunks ÃƒÂ¢Ã¢â‚¬Â Ã¢â‚¬â„¢ schema-agent ÃƒÂ¢Ã¢â‚¬Â Ã¢â‚¬â„¢ validation-agent |
| **export-agent** | Manual only | - XForm XML<br>- PyXForm JSON<br>- ODK format<br>- Kobo format<br>- CommCare format | schema-agent ÃƒÂ¢Ã¢â‚¬Â Ã¢â‚¬â„¢ export-agent |
| **schema-agent** | 50+ questions | - Structure analysis<br>- Dependency mapping<br>- Optimization suggestions<br>- Circular reference detection | Analyzes before/after modifications<br>- Validates structure integrity |
| **translation-agent** | Manual only | - Multi-language support<br>- Cultural adaptation<br>- Translation validation<br>- Language workflows | translation-agent ÃƒÂ¢Ã¢â‚¬Â Ã¢â‚¬â„¢ validation-agent |

### Coordination Patterns

**Import Workflow:**
```
import-agent (parallel chunks)
    ÃƒÂ¢Ã¢â‚¬Â Ã¢â‚¬Å“
schema-agent (analyze structure)
    ÃƒÂ¢Ã¢â‚¬Â Ã¢â‚¬Å“
validation-agent (validate all)
```

**Export Workflow:**
```
schema-agent (analyze)
    ÃƒÂ¢Ã¢â‚¬Â Ã¢â‚¬Å“
export-agent (convert)
```

**Large Edit Workflow:**
```
validation-agent (parallel chunks)
    ÃƒÂ¢Ã¢â‚¬Â Ã¢â‚¬Å“
merge results
    ÃƒÂ¢Ã¢â‚¬Â Ã¢â‚¬Å“
validation-agent (final validation)
```

**Translation Workflow:**
```
translation-agent (translate)
    ÃƒÂ¢Ã¢â‚¬Â Ã¢â‚¬Å“
validation-agent (validate all languages)
```

## Best Practices Encyclopedia

### Question Design

**Naming Conventions:**
- Use snake_case: `respondent_age`, not `Respondent Age`
- Be descriptive but concise: `hh_head_age` for household head age
- Always unique: No duplicate names
- Do not start or end names with numbers: avoid `1st_visit` and `age_3`
- Use semantic disambiguation instead of numeric suffixes: `age_child`, `age_spouse`
- This avoids confusion with repeat exports (`age_1`, `age_2`) and select_multiple exports (`fruits_1`, `fruits_2`)

**Type Selection:**
- Use `integer` for whole numbers (age, count)
- Use `decimal` for measurements (weight, height)
- Use `text` for short free-form input
- Use `select_one` for mutually exclusive options
- Use `select_multiple` for multiple selections

**Label Clarity:**
- Be descriptive: "What is your full name?" not "Name"
- Be concise: Avoid long labels (>100 characters)
- Use consistent language: Match respondent's dialect
- Avoid technical jargon: Use simple, clear language

**Required vs Optional:**
- Default to required for key questions
- Use `required: yes` sparingly
- Provide helpful required_message
- Make only truly critical fields required

### Form Structure

**Grouping:**
- Group related questions with `begin_group`/`end_group`
- Use descriptive group labels
- Keep groups focused (5-15 questions)
- Avoid deep nesting (max 3 levels)

**Question Order:**
- Start with easy questions (name, age)
- Group related questions together
- Put sensitive questions later
- Use logical flow (demographics ÃƒÂ¢Ã¢â‚¬Â Ã¢â‚¬â„¢ main questions ÃƒÂ¢Ã¢â‚¬Â Ã¢â‚¬â„¢ wrap-up)

**Repeats:**
- Use `begin_repeat`/`end_repeat` for repeated items
- Always close repeats in proper order
- Add count question to control repeat
- Keep repeat sections focused

**Metadata:**
- Place metadata at top (start, today, deviceid)
- Use `audit` for compliance tracking
- Don't overuse metadata (only what's needed)
- Consider user experience (deviceid can be intrusive)

### Data Quality

**Constraints:**
- Add constraints to all numeric fields
- Use helpful constraint_message
- Test constraint logic thoroughly
- Use realistic ranges (0-120 for age)

**Validation:**
- Use regex for text validation when needed
- Add validation messages for clarity
- Test edge cases (negative numbers, decimals)
- Consider offline data collection

**Relevance:**
- Use `${field_name}` to reference other fields
- Test complex relevance logic
- Use parentheses for complex expressions
- Document relevance logic in comments

**Calculations:**
- Test calculations thoroughly
- Handle division by zero
- Use parentheses for order of operations
- Round decimals appropriately

### Performance

**Minimize Complexity:**
- Simplify relevance logic when possible
- Avoid deeply nested expressions
- Use choice_filter instead of complex relevance
- Limit number of calculations

**Optimize Validation:**
- Use incremental validation for large forms
- Skip validation during rapid prototyping
- Use parallel validation for 100+ questions
- Cache validation results when appropriate

**Reduce File Size:**
- Minimize total questions (< 200 recommended)
- Remove unused questions
- Consolidate redundant questions
- Use external selects for large choice lists

---

# Advanced Patterns


## Complex Form Patterns

### Pattern 1: Cascading Select

**Use case:** Country ÃƒÂ¢Ã¢â‚¬Â Ã¢â‚¬â„¢ State ÃƒÂ¢Ã¢â‚¬Â Ã¢â‚¬â„¢ City selection

**Implementation:**
```xlsform
type                    name        label                   choice_filter
select_one countries   country     Select country
select_one states       state       Select state           country=${country}
select_one cities        city        Select city             state=${state}
```

**Choices sheet:**
```xlsform
list_name  name        label
countries usa         United States
countries can         Canada
countries uk          United Kingdom

states    usa_wa      Washington     usa
states    usa_or      Oregon         usa
states    can_bc      British Columbia  can

cities    usa_wa_se   Seattle         usa_wa
cities    usa_or_por  Portland        usa_or
```

**Reference:** `/skill:xlsform-core` section 7, `question-types.md` line 245

### Pattern 2: Conditional Repeats

**Use case:** Household members only if household exists

**Implementation:**
```xlsform
type         name              label                       relevant
select_one   has_household     Does this household exist?
begin_repeat household_member  Household Member           ${has_household} = 'yes'
text         member_name       Member Name
integer      member_age        Member Age
end_repeat   household_member
```

**Key points:**
- `relevant` on `begin_repeat` controls entire repeat
- Can use any condition (select_one, calculate, etc.)
- Test with has_household = 'no' to verify repeat is hidden

**Reference:** `syntax-guide.md` section 4

### Pattern 3: Dynamic Labels

**Use case:** Label shows answer from previous question

**Implementation:**
```xlsform
type      name        label
text      name        What is your name?
text      age_label   Age

# In the label column for age_label:

# Use: Age of ${name}

```

**Advanced: Multiple variables**
```xlsform
# label: Age of ${name} (${relationship_to_head})

```

**Key points:**
- Use `${field_name}` syntax
- Works in label, hint, constraint_message
- Shows live answer from referenced field

**Reference:** `question-types.md` section 3

### Pattern 4: Multi-Language Form

**Use case:** Survey in English and Spanish

**Implementation:**
```xlsform
type           name      label::English      label::Spanish      label::French
text           name      What is your name?  Como te llamas?     Quel est votre nom?
select_one     gender    What is your gender? Cual es tu genero? Quel est votre genre?
```

**Settings sheet:**
```xlsform
form_title        form_id            default_language
Household Survey  household_survey   English
```

**Translation workflow:**
1. Use `/skill:translation-agent`
2. Ask user whether to keep base headers as-is or convert base headers to English
3. Add language columns after each base column (for example `label`, then `label::Bangla`)
4. Add translated labels and choices
5. Validate all translations

**Base header decision options (mandatory prompt):**
1. Keep base headers as-is (recommended)
2. Convert base headers to source language (for example `label` -> `label::English`)

Default language label format:
- Use names without shortcode (for example `Bangla`, `English`)
- Include shortcode only when explicitly requested

**Reference:** `/skill:translation-agent`

### Pattern 5: Calculated Fields

**Use case:** BMI calculation from height and weight

**Implementation:**
```xlsform
type       name       label                    calculation
decimal    height     Height (cm)
decimal    weight     Weight (kg)
decimal    bmi        BMI                      ${weight} / ((${height} / 100) * (${height} / 100))
```

**Advanced: Rounding**
```xlsform
type       name       label                    calculation
decimal    bmi_rounded BMI (rounded)           round(${bmi}, 1)
```

**Key points:**
- Use `${field_name}` to reference fields
- Use standard math operators: +, -, *, /
- Use `round()` for decimal places
- Test calculations thoroughly

**Reference:** `syntax-guide.md` section 6

### Pattern 6: External Selects

**Use case:** Large choice lists from external file

**Implementation:**
```xlsform
type           name          label
select_one     country       Select country    countries.csv
```

**In choices sheet, reference external file:**
```xlsform
list_name  name
country    *file_name=countries.csv*
```

**Benefits:**
- Reduces form file size
- Enables centralized choice management
- Updates don't require form redeployment

**Reference:** `syntax-guide.md` section 8

## Parallel Processing Strategies

### Decision Tree: Parallel vs Sequential

```
Is task size ÃƒÂ¢Ã¢â‚¬Â°Ã‚Â¥ threshold?
ÃƒÂ¢Ã¢â‚¬ÂÃ…â€œÃƒÂ¢Ã¢â‚¬ÂÃ¢â€šÂ¬ Yes ÃƒÂ¢Ã¢â‚¬Â Ã¢â‚¬â„¢ Use automatic parallel processing
ÃƒÂ¢Ã¢â‚¬ÂÃ¢â‚¬Å¡   ÃƒÂ¢Ã¢â‚¬ÂÃ…â€œÃƒÂ¢Ã¢â‚¬ÂÃ¢â€šÂ¬ 100+ questions ÃƒÂ¢Ã¢â‚¬Â Ã¢â‚¬â„¢ Parallel validation
ÃƒÂ¢Ã¢â‚¬ÂÃ¢â‚¬Å¡   ÃƒÂ¢Ã¢â‚¬ÂÃ…â€œÃƒÂ¢Ã¢â‚¬ÂÃ¢â€šÂ¬ 10+ pages ÃƒÂ¢Ã¢â‚¬Â Ã¢â‚¬â„¢ Parallel import
ÃƒÂ¢Ã¢â‚¬ÂÃ¢â‚¬Å¡   ÃƒÂ¢Ã¢â‚¬ÂÃ¢â‚¬ÂÃƒÂ¢Ã¢â‚¬ÂÃ¢â€šÂ¬ 1MB+ file ÃƒÂ¢Ã¢â‚¬Â Ã¢â‚¬â„¢ Parallel parsing
ÃƒÂ¢Ã¢â‚¬ÂÃ¢â‚¬Å¡
ÃƒÂ¢Ã¢â‚¬ÂÃ¢â‚¬ÂÃƒÂ¢Ã¢â‚¬ÂÃ¢â€šÂ¬ No ÃƒÂ¢Ã¢â‚¬Â Ã¢â‚¬â„¢ Use sequential processing (faster startup)
```

### Manual Override

**Force parallel:**
```python
# Use command-level parallel workflows only.
# Example:
/xlsform-import large_file.pdf
```

**Force sequential:**
```
/xlsform-import large_file.pdf --sequential
```

### Chunking Strategies

**PDF:**
- By page count: 10-20 pages per chunk
- Balanced: Similar question counts per chunk
- Adaptive: Adjust based on parsing speed

**Word:**
- By section headers
- By page count
- By question count (50 per chunk)

**Excel:**
- By row count: 50-100 rows per chunk
- By sheet (if multiple sheets)
- By section headers

### Error Handling in Parallel Mode

**If chunk fails:**
1. Log error for that chunk
2. Continue processing other chunks
3. Report errors at end
4. Don't apply changes if critical errors

**If merge fails:**
1. Retry sequentially
2. Log error details
3. Ask user for manual intervention

**Performance tips:**
- Small tasks: Use sequential (faster startup)
- Large tasks: Let system auto-detect
- Very large tasks: Force parallel
- Testing/debugging: Use sequential

## Integration Workflows

### Git Workflow

**Initial setup:**
```bash
git init
echo "*.xlsx" >> .gitignore
echo "activity_log.html" >> .gitignore
git add .
git commit -m "Initial XLSForm project"
```

**.gitignore:**
```
*.xlsx
activity_log.html
!*.template.xlsx
```

**Commit strategy:**
- Commit after each feature/section
- Use descriptive commit messages
- Commit activity log with form changes
- Include row numbers in commit messages

**Example commit:**
```bash
git add survey.xlsx activity_log.html
git commit -m "Add demographic questions

Added 5 questions to demographics section:
- name, age, gender, education, occupation
Rows: 10-14

Activity log: 1 entry logged"
```

### ODK Central Integration

**Setup:**
1. Install pyodk: `pip install pyodk`
2. Configure `~/.pyodk_config.toml`:
```toml
central.url = "https://your.central.server"
central.username = "your-username"
central.password = "your-password"
central.project_id = 1
```

**Upload:**
```bash
# Manual upload

python scripts/deploy_odk.py survey.xlsx

# Auto-upload with watch mode

npm run watch
```

**Versioning:**
- Ensure `version` exists in the settings sheet
- Use the common convention `yyyymmddrr` (year, month, day, revision)
- Track version updates in the activity log

### Multi-User Collaboration

**Activity log for change review:**
- Open `activity_log.html`
- Filter by author/date
- Review changes before merging
- Export to CSV for analysis

**Conflict resolution:**
- Last write wins (with warnings)
- Use activity log to identify conflicts
- Communicate through log comments
- Backup before major changes

**Best practices:**
- Pull before making changes
- Review activity log before committing
- Communicate large changes in advance
- Use descriptive log entries

### CI/CD Pipeline

**Pre-commit hook:**
```bash
#!/bin/bash
# .git/hooks/pre-commit


python scripts/validate_form.py survey.xlsx
if [ $? -ne 0 ]; then
    echo "Validation failed. Commit aborted."
    exit 1
fi
```

**GitHub Actions workflow:**
```yaml
name: Validate XLSForm
on: [push, pull_request]
jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
      - name: Install dependencies
        run: pip install -r requirements.txt
      - name: Validate form
        run: python scripts/validate_form.py survey.xlsx
```

**Automated deployment:**
- Validate on commit
- Auto-test with ODK Build
- Deploy to staging on success
- Monitor activity log for errors

## Troubleshooting Guide

### Diagnostic Approach

**Step 1: Check Configuration**
```bash
cat xlsform-ai.json
```
- Verify project settings
- Check file paths
- Confirm agents are enabled

**Step 2: Verify File State**
```bash
ls -la survey.xlsx
```
- Check file exists
- Verify file permissions
- Check file size (corruption?)

**Step 3: Run Validation**
```bash
/xlsform-validate
```
- Get detailed error report
- Identify specific issues
- Follow recommended fixes

**Step 4: Check Activity Log**
```bash
# Open activity_log.html in browser

```
- Review recent changes
- Identify what caused issue
- Check for failed operations

**Step 5: Review Error Messages**
- Read full error stack trace
- Check line numbers
- Look for specific error types

### Common Issues

**Configuration Errors:**
- **Issue:** `xlsform-ai.json` not found
- **Solution:** Re-init project: `xlsform-ai init --here`
- **Issue:** Invalid agent configuration
- **Solution:** Check `enabled_agents` list, verify agent names

**File Access Errors:**
- **Issue:** File not found
- **Solution:** Check file path, verify file exists
- **Issue:** Permission denied
- **Solution:** Close file in Excel, check permissions
- **Issue:** File locked
- **Solution:** Close Excel, use openpyxl instead

**Validation Errors:**
- **Issue:** Duplicate names
- **Solution:** Rename duplicates with descriptive names
- **Issue:** Invalid types
- **Solution:** Fix typos (selct_one ÃƒÂ¢Ã¢â‚¬Â Ã¢â‚¬â„¢ select_one)
- **Issue:** Missing choice lists
- **Solution:** Create choice list or fix list_name typo

**Import Errors:**
- **Issue:** PDF parsing failed
- **Solution:** Check if PDF is scanned images (needs OCR)
- **Issue:** Word extraction failed
- **Solution:** Check file format, try different parser
- **Issue:** Excel reading failed
- **Solution:** Verify headers, check sheet names

**Performance Issues:**
- **Issue:** Slow validation
- **Solution:** Use parallel mode for 100+ questions
- **Issue:** Memory errors
- **Solution:** Close large files, process in chunks
- **Issue:** Long import times
- **Solution:** Reduce page range, use parallel mode

### Debug Mode

**Enable debug mode:**
```json
// In xlsform-ai.json
{
  "settings": {
    "debug": true
  }
}
```

**Debug output:**
- Detailed logs to console
- Stack traces for errors
- Progress indicators
- Performance timing

**Logs saved to:** `debug_log.txt`

**Remember:** Disable debug mode after troubleshooting!

### Getting Help

**Check activity log** - Review recent changes
**Run validation** - `/xlsform-validate`
**Review knowledge base** - `scripts/knowledge_base/data/`
**Check GitHub issues** - https://github.com/ARCED-International/xlsform-ai/issues
**Contact support** - support@arced-international.com

## Performance Optimization

### Form Design

**Minimize total questions:**
- Target < 200 questions per form
- Remove unnecessary questions
- Consolidate redundant questions
- Split large forms into multiple forms

**Simplify relevance logic:**
- Avoid deeply nested expressions
- Use choice_filter instead of complex relevance
- Test relevance logic thoroughly
- Use intermediate calculate fields

**Optimize choice lists:**
- Use external selects for large lists
- Reuse common choice lists
- Remove unused choices
- Avoid spaces in choice names (select_multiple)

### Validation Performance

**Incremental validation:**
- Validate sections instead of entire form
- Use validation after major changes only
- Skip validation during rapid prototyping
- Cache validation results

**Parallel validation:**
- Automatically activates for 100+ questions
- Manual activation: use command-level import/validation workflows; `add_questions` has no `parallel` argument
- Reduces validation time by ~50%

### Import/Export Performance

**Chunk large files:**
- Automatic for 10+ pages or 1MB+
- Manual: `parse_pdf(source, chunk_size=20)`
- Process in parallel when possible
- Use appropriate chunk sizes

**Use openpyxl for closed files:**
- Faster than xlwings for batch operations
- Better for automated changes
- May not preserve formatting perfectly

**Disable formatting:**
- Use openpyxl to skip formatting
- Reduces file size and processing time
- Acceptable for closed files

### Memory Management

**Close large files:**
- Close Excel files after operations
- Release file handles explicitly
- Use context managers where possible

**Use generators:**
- For large datasets, use generators instead of lists
- Reduces memory footprint
- Better for iterative processing

**Clear cache:**
- Clear validation cache periodically
- Restart Python session if needed
- Monitor memory usage during operations

---

# Appendices


## Appendix A: Command Syntax Reference

### All Commands

| Command | Purpose | Example | Claude | Cursor | Copilot |
|---------|---------|---------|--------|--------|---------|
| `/xlsform-add` | Add questions | `/xlsform-add Add text question` | /xlsform-add | Use command xlsform-add | @xlsform-add |
| `/xlsform-import` | Import from files | `/xlsform-import survey.pdf` | /xlsform-import | Use command xlsform-import | @xlsform-import |
| `/xlsform-validate` | Validate form | `/xlsform-validate --fix` | /xlsform-validate | Use command xlsform-validate | @xlsform-validate |
| `/xlsform-update` | Modify questions | `/xlsform-update Add constraint` | /xlsform-update | Use command xlsform-update | @xlsform-update |
| `/xlsform-remove` | Delete questions | `/xlsform-remove Remove q1` | /xlsform-remove | Use command xlsform-remove | @xlsform-remove |
| `/xlsform-move` | Reorder questions | `/xlsform-move Move name to top` | /xlsform-move | Use command xlsform-move | @xlsform-move |
| `/xlsform-translate` | Translate multilingual content (AI-first, optional runtime fallback) | `/xlsform-translate add Bangla language` | /xlsform-translate | Use command xlsform-translate | @xlsform-translate |
| `/xlsform-revert` | Revert safely | `/xlsform-revert restore --revision <id>` | /xlsform-revert | Use command xlsform-revert | @xlsform-revert |

### Skill Syntax

| Skill | Claude | Cursor | Copilot |
|-------|--------|--------|---------|
| xlsform-core | `/skill:xlsform-core` | `Use skill xlsform-core` | `@skill xlsform-core` |
| activity-logging | `/skill:activity-logging` | `Use skill activity-logging` | `@skill activity-logging` |
| translation-agent | `/skill:translation-agent` | `Use skill translation-agent` | `@skill translation-agent` |

## Appendix B: Knowledge Base Index

### Available Knowledge Base Documents

**Location:** `scripts/knowledge_base/data/`

| Document | Purpose | Topics Covered |
|----------|---------|----------------|
| `odk_best_practices.md` | ODK-specific guidelines | Field naming, constraints, validation |
| `dime_style_guide.md` | Question design guide | Question phrasing, form structure |
| `constraint_rules.md` | Constraint patterns | Constraints by field type, examples |
| `question_type_patterns.md` | Type selection guide | Decision trees for type selection |
| `settings_sheet.md` | Settings rules | form_title, form_id, version convention, layout |
| `random_sampling.md` | Randomization patterns | random(), randomize(), indexed-repeat() |
| `nested_repeats.md` | Nested repeat guidance | Hierarchy design, pitfalls |
| `use_cases.md` | Common survey modules | Sector patterns and examples |
| `multilingual_translation.md` | Translation standards | language headers, placeholder safety, multilingual coverage |

### How to Access

**Direct access:**
```bash
cat scripts/knowledge_base/data/odk_best_practices.md
```

**Via skill:**
```bash
/skill:xlsform-core  # References knowledge base automatically
```

**Via RAG retrieval:**
- Automatic for complex queries
- Context-aware retrieval
- Cross-references to relevant sections

## Appendix C: Agent Compatibility Matrix

### Feature Support by Agent

All 17 agents have full feature parity. Every agent can:

- [OK] Add, update, remove, move questions
- [OK] Import from PDF, Word, Excel
- [OK] Validate forms
- [OK] Use all 8 slash commands
- [OK] Access xlsform-core skill
- [OK] Access activity-logging skill
- [OK] Log activities automatically
- [OK] Use sub-agents for parallel processing
- [OK] View and filter activity logs

### Agent-Specific Details

| Agent | Commands | Skills | Memory File | Command Format |
|-------|----------|--------|-------------|----------------|
| Claude | [OK] | [OK] | `.claude/CLAUDE.md` | `/command` |
| Copilot | [OK] | [OK] | `.copilot/MEMORY.md` | `/command` |
| Gemini | [OK] | [OK] | `.gemini/GEMINI.md` | `/command` |
| Cursor | [OK] | [OK] | `.cursor/MEMORY.md` | `Use command` |
| Qwen | [OK] | [OK] | `.qwen/QWEN.md` | `/command` |
| OpenCode | [OK] | [OK] | `.opencode/MEMORY.md` | `/command` |
| Codex | [OK] | [OK] | `.codex/MEMORY.md` | `/command` |
| Windsurf | [OK] | [OK] | `.windsurf/MEMORY.md` | `/command` |
| KiloCode | [OK] | [OK] | `.kilocode/MEMORY.md` | `/command` |
| Auggie | [OK] | [OK] | `.auggie/MEMORY.md` | `/command` |
| CodeBuddy | [OK] | [OK] | `.codebuddy/MEMORY.md` | `/command` |
| Qoder | [OK] | [OK] | `.qoder/MEMORY.md` | `/command` |
| Roo | [OK] | [OK] | `.roo/MEMORY.md` | `/command` |
| Amazon Q | [OK] | [OK] | `.amazon-q/Q.md` | `/command` |
| Amp | [OK] | [OK] | `.amp/MEMORY.md` | `/command` |
| Shai | [OK] | [OK] | `.shai/SHAI.md` | `/command` |
| Bob | [OK] | [OK] | `.bob/MEMORY.md` | `/command` |

**Note:** Amazon Q has limited slash command support (configuration-dependent).

### Agent Directory Structure

All agents receive the same structure during init:

```
{agent}/
ÃƒÂ¢Ã¢â‚¬ÂÃ…â€œÃƒÂ¢Ã¢â‚¬ÂÃ¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬ÂÃ¢â€šÂ¬ commands/           # Slash commands (same for all agents)
ÃƒÂ¢Ã¢â‚¬ÂÃ¢â‚¬Å¡   ÃƒÂ¢Ã¢â‚¬ÂÃ…â€œÃƒÂ¢Ã¢â‚¬ÂÃ¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬ÂÃ¢â€šÂ¬ xlsform-add.md
ÃƒÂ¢Ã¢â‚¬ÂÃ¢â‚¬Å¡   ÃƒÂ¢Ã¢â‚¬ÂÃ…â€œÃƒÂ¢Ã¢â‚¬ÂÃ¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬ÂÃ¢â€šÂ¬ xlsform-import.md
ÃƒÂ¢Ã¢â‚¬ÂÃ¢â‚¬Å¡   ÃƒÂ¢Ã¢â‚¬ÂÃ…â€œÃƒÂ¢Ã¢â‚¬ÂÃ¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬ÂÃ¢â€šÂ¬ xlsform-validate.md
ÃƒÂ¢Ã¢â‚¬ÂÃ¢â‚¬Å¡   ÃƒÂ¢Ã¢â‚¬ÂÃ…â€œÃƒÂ¢Ã¢â‚¬ÂÃ¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬ÂÃ¢â€šÂ¬ xlsform-update.md
ÃƒÂ¢Ã¢â‚¬ÂÃ¢â‚¬Å¡   ÃƒÂ¢Ã¢â‚¬ÂÃ…â€œÃƒÂ¢Ã¢â‚¬ÂÃ¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬ÂÃ¢â€šÂ¬ xlsform-remove.md
ÃƒÂ¢Ã¢â‚¬ÂÃ¢â‚¬Å¡   ÃƒÂ¢Ã¢â‚¬ÂÃ…â€œÃƒÂ¢Ã¢â‚¬ÂÃ¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬ÂÃ¢â€šÂ¬ xlsform-move.md
ÃƒÂ¢Ã¢â‚¬ÂÃ¢â‚¬Å¡   ÃƒÂ¢Ã¢â‚¬ÂÃ¢â‚¬ÂÃƒÂ¢Ã¢â‚¬ÂÃ¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬ÂÃ¢â€šÂ¬ xlsform-translate.md
ÃƒÂ¢Ã¢â‚¬ÂÃ¢â‚¬Å¡
ÃƒÂ¢Ã¢â‚¬ÂÃ¢â‚¬ÂÃƒÂ¢Ã¢â‚¬ÂÃ¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬ÂÃ¢â€šÂ¬ skills/             # Knowledge packages (same for all agents)
    ÃƒÂ¢Ã¢â‚¬ÂÃ…â€œÃƒÂ¢Ã¢â‚¬ÂÃ¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬ÂÃ¢â€šÂ¬ xlsform-core/
    ÃƒÂ¢Ã¢â‚¬ÂÃ¢â‚¬Å¡   ÃƒÂ¢Ã¢â‚¬ÂÃ¢â‚¬ÂÃƒÂ¢Ã¢â‚¬ÂÃ¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬ÂÃ¢â€šÂ¬ SKILL.md
    ÃƒÂ¢Ã¢â‚¬ÂÃ¢â‚¬ÂÃƒÂ¢Ã¢â‚¬ÂÃ¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬ÂÃ¢â€šÂ¬ activity-logging/
        ÃƒÂ¢Ã¢â‚¬ÂÃ¢â‚¬ÂÃƒÂ¢Ã¢â‚¬ÂÃ¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬ÂÃ¢â€šÂ¬ SKILL.md
```

## Appendix D: Glossary

**Agent:** AI assistant (Claude, Copilot, Gemini, etc.)

**Choice List:** Predefined options for select_one/select_multiple questions

**Dependency:** When one question's visibility/value depends on another question

**Form Structure:** Organization of questions (groups, repeats, metadata)

**Knowledge Base:** Collection of best practices and patterns

**Metadata:** Special fields that capture form information (start, end, deviceid)

**Parallel Processing:** Using multiple sub-agents simultaneously to process large tasks

**Question Type:** Defines what kind of input the question accepts (text, integer, select_one, etc.)

**Relevance:** Conditional logic that shows/hides questions based on previous answers

**Skill:** Reusable knowledge package that provides specialized information to agents

**Sub-Agent:** Specialist agent that handles specific tasks (validation, import, export, schema, translation)

**Validation:** Checking form for errors, warnings, and best practices violations

**XLSForm:** Standard format for designing forms that can be used with ODK, KoboToolbox, CommCare, etc.

---

# Project-Specific Notes


Add any project-specific notes here:

- Form ID: [your-form-id]
- Project: [project-description]
- Last updated: [date]
- Organization: [your-organization]

---

**About ARCED International**

ARCED International is a Global Research & Learning Studio. We partner with institutions, governments, and growth-stage ventures to design and implement research, and build technical products that deliver lasting impact across emerging markets.

With 12+ years of evidence-led execution, serving 40+ countries, and impacting 5M+ lives, we develop purpose-built platforms that deliver clarity to research and learning teams.

Learn more at: https://arced-international.com




