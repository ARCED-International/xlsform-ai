# XLSForm AI

[![Python](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![GitHub](https://img.shields.io/badge/github-ARCED--International-blue.svg)](https://github.com/ARCED-International/xlsform-ai)

**AI-powered XLSForm creation tool with multi-agent coding support.**
**Includes standardized survey modules and knowledge base patterns.**

<img src="https://www.arced-international.com/_next/image?url=%2F_next%2Fstatic%2Fmedia%2Farced-int_logo.5040257d.png&w=3840&q=75" alt="ARCED International Logo" width="200">

**An Open Source Project by [ARCED International](https://arced-international.com)**

XLSForm AI helps you create, modify, and validate XLSForms intelligently. Parse forms from PDF/Word/Excel, auto-detect question types, and manage complex form logic with ease.

## What is XLSForm AI?

XLSForm AI is a CLI tool that sets up projects with specialized skills and commands for XLSForm development, compatible with multiple AI coding agents. It combines:

- **Comprehensive XLSForm knowledge** integrated with your AI coding agent
- **Smart file parsing** to import questions from PDFs, Word docs, and Excel files
- **Intelligent question type detection** from natural language
- **xlwings integration** for live Excel editing with format preservation
- **Validation** to catch errors before deployment
- **Standardized survey modules** and best-practice patterns from the built-in knowledge base

## Features

### ✨ Smart Question Creation
- Add questions from natural language descriptions
- Auto-detect question types (text, select_one, geopoint, etc.)
- Automatic choice list creation
- Intelligent name generation

### 📄 File Import
- Import questions from PDF files
- Import from Word documents (.docx)
- Import from existing Excel forms
- Parse question structure automatically

### ✅ Validation
- Check for duplicate names
- Validate question types
- Verify choice list consistency
- Enforce XLSForm syntax rules
- Run offline `ODK-Validate.jar` checks with structured REPL output

### 🔄 Live Editing
- xlwings integration for open Excel files
- Format preservation
- Real-time preview support

### Safe Rollback
- Immutable pre-change snapshots for write operations
- Revision history listing and manual checkpoints
- Fast undo/restore workflows for agent edits
- Designed for open workbook workflows where users observe changes live

### 📋 Slash Commands
- `/xlsform-add` - Add questions
- `/xlsform-import` - Import from files
- `/xlsform-validate` - Validate form
- `/xlsform-update` - Modify questions
- `/xlsform-remove` - Delete questions
- `/xlsform-move` - Reorder questions
- `/xlsform-translate` - Add/complete multilingual translations
- `/xlsform-revert` - Restore from history safely

### Standardized Modules
- Crop production, livestock, aquaculture DNA
- Household roster, child education, education access
- Food security (FCS, rCSI), nutrition (MUAC)
- WASH, housing, energy access
- Health (basic, biomarkers, immunization, ANC)
- Migration, market access, shocks and coping
- Labor rights, workplace violence, protection/GBV (safety-first templates)

## Installation

### Prerequisites

- Python 3.10 or higher
- Node.js 18+ (for watch/reload features)
- Java 8+ (for offline ODK Validate jar)
- An AI coding assistant (Claude Code recommended, but other agents supported)
- Excel (optional, for xlwings features)

### Install CLI Tool

```bash
# Using uv (recommended)
uv tool install xlsform-ai-cli --from git+https://github.com/ARCED-International/xlsform-ai.git

# Or with pip
pip install git+https://github.com/ARCED-International/xlsform-ai.git
```

If `uv` is not installed, use the `pip` command above or install `uv` first:
```bash
pip install uv
```

### Verify Installation

```bash
xlsform-ai check
```

If you run project scripts directly (for example, `python scripts/validate_form.py`),
ensure runtime dependencies are installed in that Python environment:

```bash
python -m pip install openpyxl pyxform pdfplumber python-docx deep-translator
```

## Quick Start

### Create a New Project

```bash
# Option 1: Create new project directory
xlsform-ai init my-survey
cd my-survey

# Option 2: Initialize existing directory
mkdir my-survey && cd my-survey
xlsform-ai init .    # or: xlsform-ai init --here
```

This creates:
```
my-survey/
├── survey.xlsx              # Your XLSForm file
├── .claude/                 # Claude Code configuration
│   ├── commands/            # Slash commands
│   ├── skills/              # XLSForm knowledge
│   └── AGENT_MEMORY_TEMPLATE.md  # Project memory
├── scripts/                 # Utility scripts
└── package.json             # npm scripts
```

### Start Creating Forms

`xlsform-ai init` also prepares offline validation tooling at `tools/ODK-Validate.jar` (latest release when network is available).

1. **Open the project in your preferred AI coding environment:**
```bash
cd my-survey

# Using Claude Code (recommended)
claude

# Or use with other AI coding agents that support local file access
```

2. **Add questions using natural language:**
```
/xlsform-add Add a text question asking for respondent name
```

3. **Import from a PDF:**
```
/xlsform-import questionnaire.pdf --pages 1-10
```

4. **Validate your form:**
```
/xlsform-validate
```

## Available Commands

### `/xlsform-add`

Add new questions to your form.

```bash
# Add a single question
/xlsform-add Add a text question asking for name

# Add a select question
/xlsform-add Add a select_one question for favorite fruits with options: Apple, Banana, Orange

# Add with constraints
/xlsform-add Add an age question (must be 18-120)
```

### `/xlsform-import`

Import questions from external files.

```bash
# Import from PDF
/xlsform-import questions.pdf --pages 1-10

# Import from Word
/xlsform-import questionnaire.docx

# Import from Excel
/xlsform-import existing_form.xlsx --sheet "Survey Questions"
```

### `/xlsform-validate`

Validate your form for errors.

```bash
# Basic validation
/xlsform-validate

# Auto-fix simple issues
/xlsform-validate --fix

# Validate specific file
/xlsform-validate backup.xlsx
```

Validation output is structured in REPL via `scripts/validate_form.py`:

```text
# XLSFORM_VALIDATION_RESULT
valid: true|false
summary:
  errors: <count>
  warnings: <count>
  suggestions: <count>
engines:
  local.status: passed|failed
  odk_validate.status: completed|jar_not_found|java_not_found|pyxform_not_found|xform_conversion_failed|disabled
```

For JSON output:

```bash
python scripts/validate_form.py survey.xlsx --json
```

Validation pipeline: XLSForm local checks -> XLSForm to XForm conversion (pyxform) -> offline ODK Validate jar.

### `/xlsform-update`

Modify existing questions.

```bash
/xlsform-update Update the age question to add a constraint message
/xlsform-update Change the name question to include a hint
```

### `/xlsform-remove`

Remove questions or choice lists.

```bash
/xlsform-remove Remove the question named 'old_question'
/xlsform-remove Remove the choice list 'unused_list'
```

### `/xlsform-move`

Reorder questions in the form.

```bash
/xlsform-move Move the name question to the beginning of the form
/xlsform-move Move the age question after the name question
```

### `/xlsform-translate`

Add and complete multilingual translations in `survey` and `choices`.

```bash
# Add Bangla language columns and translate full content
/xlsform-translate add Bangla language

# Fill only missing Bangla translations
/xlsform-translate do the bangla translations for the remaining questions
```

Script entrypoint:

```bash
python scripts/translate_form.py "add Bangla language"
python scripts/translate_form.py "do the bangla translations for the remaining questions"

# AI-first contextual translation map (recommended)
python scripts/translate_form.py "add Bangla language" --translation-map-file .xlsform-ai/translation/bn.json

# Optional runtime fallback
python scripts/translate_form.py "add Bangla language" --translator auto

# Optional: convert base columns to source-language headers (after confirmation)
python scripts/translate_form.py "add Bangla language" --base-language-mode english

# Optional: include language shortcode in headers/settings values
python scripts/translate_form.py "add Bangla language" --include-language-code
```

Default behavior is AI-first: the agent can provide contextual translations via `--translation-map` or `--translation-map-file`.
`deep-translator` is optional fallback only (install with `pip install -e ".[translate]"`).
Language display labels are normalized to ASCII-friendly names by default (for example, `Bangla`, `Spanish`). Use `--include-language-code` to emit `Bangla (bn)`.

Structured output marker:

```text
# XLSFORM_TRANSLATION_RESULT
status: completed|completed_with_warnings|dry_run|failed
```

### `/xlsform-revert`

Safely revert XLSForm changes from immutable snapshots.

```bash
# Show revision history
/xlsform-revert history

# Create a manual checkpoint
/xlsform-revert checkpoint "Before roster update"

# Undo latest change
/xlsform-revert undo

# Restore latest normal snapshot
/xlsform-revert restore-last

# Restore specific revision
/xlsform-revert restore --revision 20260207121001-ab12cd34
```

## Examples

### Creating a Survey from Scratch

```
# Start with metadata
/xlsform-add Add form metadata (start, end, today)

# Add demographics questions
/xlsform-add Add text question for respondent name
/xlsform-add Add integer question for age (0-120)
/xlsform-add Add select_one question for gender with options: Male, Female, Other

# Add a conditional question
/xlsform-add Add a text question for occupation that only shows if age >= 18

# Validate
/xlsform-validate
```

### Importing from a PDF Questionnaire

```
# Import all questions from pages 1-10
/xlsform-import household_survey.pdf --pages 1-10

# Review and confirm
# Claude will show what it found and ask for confirmation

# Validate after import
/xlsform-validate
```

### Creating a Cascading Select

```
/xlsform-add Add a select_one question for country with options: USA, Canada, Mexico
/xlsform-add Add a select_one question for city with choice_filter matching the country
```

### Working with Repeats

```
/xlsform-add Add a repeat group for household members
/xlsform-add Add text and age questions inside the household repeat
```

## Configuration

### ODK Central (Optional)

For automatic upload and preview:

1. Create `~/.pyodk_config.toml`:

```toml
central.url = "https://your.central.server"
central.username = "your-username"
central.password = "your-password"
central.project_id = 1
```

2. Enable watch mode:

```bash
npm run watch
```

This will:
- Watch `survey.xlsx` for changes
- Upload to ODK Central when changes are detected
- Reload the browser preview

## Previewing Your Form

### Option 1: Excel in VSCode (Recommended)

**Built-in Excel viewing:**

1. **Open your survey.xlsx in VSCode**
   - Just right-click the file and "Open with... → Excel"
   - Or use VSCode's built-in Excel viewer

2. **Edit while viewing**
   - Make changes with Claude Code commands
   - See updates in Excel preview instantly
   - No extensions needed!

**Benefits:**
- Works offline
- No extensions required
- Fast and lightweight
- Direct Excel file viewing

### Option 2: Database Client Extension

**For advanced preview:**

1. **Install Database Client** for VSCode:
   ```
   ext install cweijan.vscode-database-client
   ```
   Visit: [database-client.com](https://database-client.com)

2. **Open and preview your Excel files**
   - Handles large datasets well
   - Query and filter capabilities
   - Professional database tools

### Option 3: ODK Central Online

**For full testing with submissions:**

1. Set up ODK Central (see Configuration section)
2. Upload your form
3. Preview in web browser
4. Test submissions on mobile devices

### Option 4: Enketo Express

**For quick online preview:**

1. Go to [https://enketoeexpress.preview.app](https://enketoeexpress.preview.app)
2. Upload your `survey.xlsx`
3. Test your form immediately

### xlwings Setup (Optional)

For live Excel editing:

1. Install xlwings:
```bash
pip install xlwings
```

2. Activate Excel add-in (see [xlwings docs](https://docs.xlwings.org/en/stable/addin.html))

3. Keep your Excel file open while making changes

## Project Structure

Important runtime artifact:
- `tools/ODK-Validate.jar` is installed by `xlsform-ai init` for offline form validation.

```
.
├── survey.xlsx              # Main XLSForm file (your work output)
├── activity_log_*.html      # Activity log (auto-generated)
├── .claude/                 # Claude Code configuration
│   ├── commands/            # Slash commands (.md files)
│   │   ├── xlsform-add.md
│   │   ├── xlsform-validate.md
│   │   ├── xlsform-import.md
│   │   └── ...
│   ├── skills/              # XLSForm knowledge
│   │   └── xlsform-core/
│   │       ├── SKILL.md     # Main skill file
│   │       ├── references/  # Detailed documentation
│   │       └── assets/      # Templates
│   └── AGENT_MEMORY_TEMPLATE.md  # Project memory
├── scripts/                 # Utility scripts
│   ├── parse_pdf.py         # PDF parser
│   ├── parse_docx.py        # Word parser
│   ├── parse_xlsx.py        # Excel parser
│   ├── add_questions.py     # Add questions with best practices
│   ├── translate_form.py    # Multilingual translation workflow
│   ├── log_activity.py      # Activity logger
│   ├── cleanup.py           # Cleanup utility
│   ├── xlwings_helper.py    # Excel editing
│   └── validate_form.py     # Validation
└── package.json             # npm scripts
```

## Activity Logging

**All actions are automatically logged to a beautiful HTML file!**

Every time you use XLSForm AI commands (add, update, validate, import, translate), the activity is logged with:
- Date and time
- Action type
- Description and details
- Changes made
- Row numbers affected

**View your activity log:**
- Open `activity_log_*.html` in your browser
- Beautiful timeline UI with ARCED International branding
- Shows complete history of all changes
- Useful for auditing and tracking progress

**Log file features:**
- Auto-created on first action
- Persistent across sessions
- Survives cleanup (keeps your work history)
- Can be renamed - XLSForm AI will find it by tag

## Rollback and History

XLSForm write operations now create immutable pre-change snapshots for safe recovery.

- History root: `.xlsform-ai/history/`
- Snapshot files: `.xlsform-ai/history/snapshots/`
- Manifest: `.xlsform-ai/history/history.jsonl`

You can manage revisions using:

```bash
python scripts/form_history.py list
python scripts/form_history.py checkpoint "Before major logic changes"
python scripts/form_history.py restore --revision <revision_id>
python scripts/form_history.py restore-last
python scripts/form_history.py undo
```

## CLI Reference

### `xlsform-ai init`

Initialize a new XLSForm AI project.

```bash
xlsform-ai init <PROJECT_NAME>     # Create new project directory
xlsform-ai init .                   # Initialize in current directory
xlsform-ai init --here              # Same as "init ."
xlsform-ai init . --ai claude       # Specify AI agent
```

**Quick start in current directory:**
```bash
mkdir my-survey && cd my-survey
xlsform-ai init .   # Initialize current directory
# Now you can use /xlsform-add commands
```

### `xlsform-ai check`

Check CLI installation.

```bash
xlsform-ai check
```

### `xlsform-ai info`

Show installation information.

```bash
xlsform-ai info
```

### `xlsform-ai cleanup`

Clean up XLSForm AI files from a project, keeping only your work outputs.

```bash
xlsform-ai cleanup              # Remove .claude/, scripts/, tools/, package.json
xlsform-ai cleanup --dry-run    # Preview what would be removed
```

**What gets removed:**
- `.claude/` - Claude Code configuration
- `scripts/` - Helper scripts
- `tools/` - Offline validator binaries
- `package.json` - npm configuration

**What gets kept:**
- `survey.xlsx` - Your form (output)
- `*.xlsx` - Any Excel files
- `activity_log_*.html` - Your activity history

**Use cases:**
- Clean up a completed project
- Prepare project for handoff
- Free up space while keeping outputs
- Reinstall XLSForm AI fresh (log will be reused)

## Documentation

### XLSForm Resources

- [XLSForm.org](https://xlsform.org/en/) - Official XLSForm documentation
- [ODK Form Question Types](https://docs.getodk.org/form-question-types/)
- [ODK Form Logic](https://docs.getodk.org/form-logic/)
- [ODK Operators and Functions](https://docs.getodk.org/form-operators-functions/)

### Knowledge Base

The template ships with a curated knowledge base for common patterns and best practices:

- `src/xlsform_ai/templates/base/scripts/knowledge_base/data/settings_sheet.md`
- `src/xlsform_ai/templates/base/scripts/knowledge_base/data/random_sampling.md`
- `src/xlsform_ai/templates/base/scripts/knowledge_base/data/nested_repeats.md`
- `src/xlsform_ai/templates/base/scripts/knowledge_base/data/use_cases.md`
- `src/xlsform_ai/templates/base/scripts/knowledge_base/data/multilingual_translation.md`

### Project-Specific Docs

- Agent memory file (copied from template) and quick reference
- `.claude/skills/xlsform-core/SKILL.md` - XLSForm knowledge
- `.claude/skills/xlsform-core/references/` - Detailed guides

## Troubleshooting

### "list_name not found" Error

**Cause:** The list name in `select_one` doesn't match any `list_name` in the choices sheet.

**Solution:**
1. Check the type column: `select_one fruits`
2. Check choices sheet has: `list_name = fruits`
3. Look for typos (fruit vs fruits)

### Duplicate Name Errors

**Cause:** Two questions have the same name.

**Solution:**
```bash
# Run validation to find duplicates
/xlsform-validate

# Rename duplicates
/xlsform-update Rename the duplicate age question
```

### xlwings Can't Find Excel

**Cause:** Excel is not running or file is not open.

**Solution:**
1. Open the Excel file
2. Make sure xlwings is installed
3. Try again, or close the file and use openpyxl

### Form Won't Convert

**Common causes:**
- Invalid question type (selct_one vs select_one)
- Unbalanced begin/end groups or repeats
- Missing required columns

**Solution:**
```bash
/xlsform-validate --fix
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## Development

### Setup Development Environment

```bash
# Clone repository
git clone https://github.com/ARCED-International/xlsform-ai.git
cd xlsform-ai

# Install in development mode
pip install -e .

# Install development dependencies
pip install -e ".[dev]"

# Run tests
pytest
```

### Project Structure for Development

```
xlsform-ai/
├── src/xlsform_ai/          # CLI source code
│   ├── cli.py               # Main entry point
│   ├── agents.py            # Agent configuration
│   ├── config.py            # Configuration management
│   └── templates.py         # Template management
├── templates/               # Project templates
│   └── base/               # Base template
├── scripts/                # Installation scripts
├── pyproject.toml          # Package configuration
└── README.md
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## About ARCED International

[ARCED International](https://arced-international.com) is a Global Research & Learning Studio. We partner with institutions, governments, and growth-stage ventures to design and implement research, and build technical products that deliver lasting impact across emerging markets.

With 12+ years of evidence-led execution, serving 40+ countries, and impacting 5M+ lives, we develop purpose-built platforms that deliver clarity to research and learning teams.

### Other ARCED International Tools

**[FolderManifest](https://www.foldermanifest.com)** - Offline folder audit manifest software for Windows. Generate folder trees, verify checksum manifests, and clean up duplicate files. A lightweight paid desktop tool for professionals who need robust file auditing capabilities.

<img src="https://www.foldermanifest.com/assets/logo-D_p3Ev9M.svg" alt="FolderManifest Logo" width="100">

**[FolderManifest Free Tools](https://www.foldermanifest.com/free-tools)** - Free online tools for everyone:

- **[Compare Files Online](https://www.foldermanifest.com/free-tools/compare-files)** - Upload 2 files to instantly check if they are identical using SHA-256 checksums
- **[Find Duplicate Files](https://www.foldermanifest.com/free-tools/find-duplicates)** - Upload up to 10 files to quickly identify duplicates
- **[File Metadata Viewer](https://www.foldermanifest.com/free-tools/metadata-viewer)** - Extract detailed metadata from your files
- **[Compare Folders Online](https://www.foldermanifest.com/free-tools/folder-compare)** - Upload 2 folders to find missing, modified, or duplicate files

These tools are part of ARCED International's commitment to providing high-quality solutions for research, learning, and development work.

## Acknowledgments

- [XLSForm](https://xlsform.org/) for the form specification
- [ODK](https://odk.org/) for the XForm standard
- [Claude Code](https://claude.ai/code) for the AI-powered development environment (recommended)
- Compatible with other AI coding agents that support local file system access

## Support

- 📖 [Documentation](https://github.com/ARCED-International/xlsform-ai/wiki)
- 🐛 [Issues](https://github.com/ARCED-International/xlsform-ai/issues)
- 💬 [Discussions](https://github.com/ARCED-International/xlsform-ai/discussions)
- 🌐 [ARCED International](https://arced-international.com)

---

Made with ❤️ by [ARCED International](https://arced-international.com)
