# XLSForm AI

[![Python](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![GitHub](https://img.shields.io/badge/github-ARCED--International-blue.svg)](https://github.com/ARCED-International/xlsform-ai)

**AI-powered XLSForm creation tool with Claude Code integration.**

[An Open Source Project by ARCED International](https://arced-international.com)

XLSForm AI helps you create, modify, and validate XLSForms intelligently. Parse forms from PDF/Word/Excel, auto-detect question types, and manage complex form logic with ease.

## What is XLSForm AI?

XLSForm AI is a CLI tool that sets up projects with specialized Claude Code skills and commands for XLSForm development. It combines:

- **Comprehensive XLSForm knowledge** built into Claude Code
- **Smart file parsing** to import questions from PDFs, Word docs, and Excel files
- **Intelligent question type detection** from natural language
- **xlwings integration** for live Excel editing with format preservation
- **Validation** to catch errors before deployment

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

### 🔄 Live Editing
- xlwings integration for open Excel files
- Format preservation
- Real-time preview support

### 📋 Slash Commands
- `/xlsform-add` - Add questions
- `/xlsform-import` - Import from files
- `/xlsform-validate` - Validate form
- `/xlsform-update` - Modify questions
- `/xlsform-remove` - Delete questions
- `/xlsform-move` - Reorder questions

## Installation

### Prerequisites

- Python 3.10 or higher
- Node.js 18+ (for watch/reload features)
- Claude Code with CLI access
- Excel (optional, for xlwings features)

### Install CLI Tool

```bash
# Using uv (recommended)
uv tool install xlsform-ai-cli --from git+https://github.com/ARCED-International/xlsform-ai.git

# Or with pip
pip install git+https://github.com/ARCED-International/xlsform-ai.git
```

### Verify Installation

```bash
xlsform-ai check
```

## Quick Start

### Create a New Project

```bash
# Create new project
xlsform-ai init my-survey

# Or initialize in existing directory
cd my-survey
xlsform-ai init --here
```

This creates:
```
my-survey/
├── survey.xlsx              # Your XLSForm file
├── .claude/                 # Claude Code configuration
│   ├── commands/            # Slash commands
│   ├── skills/              # XLSForm knowledge
│   └── CLAUDE.md            # Project memory
├── scripts/                 # Utility scripts
└── package.json             # npm scripts
```

### Start Creating Forms

1. **Open the project in Claude Code:**
```bash
cd my-survey
claude
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

### xlwings Setup (Optional)

For live Excel editing:

1. Install xlwings:
```bash
pip install xlwings
```

2. Activate Excel add-in (see [xlwings docs](https://docs.xlwings.org/en/stable/addin.html))

3. Keep your Excel file open while making changes

## Project Structure

```
.
├── survey.xlsx              # Main XLSForm file
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
│   └── CLAUDE.md            # Project memory
├── scripts/                 # Utility scripts
│   ├── parse_pdf.py         # PDF parser
│   ├── parse_docx.py        # Word parser
│   ├── parse_xlsx.py        # Excel parser
│   ├── xlwings_helper.py    # Excel editing
│   └── validate_form.py     # Validation
└── package.json             # npm scripts
```

## CLI Reference

### `xlsform-ai init`

Initialize a new XLSForm AI project.

```bash
xlsform-ai init <PROJECT_NAME>    # Create new project
xlsform-ai init --here              # Initialize in current directory
xlsform-ai init . --ai claude      # Specify AI agent
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

## Documentation

### XLSForm Resources

- [XLSForm.org](https://xlsform.org/en/) - Official XLSForm documentation
- [ODK Form Question Types](https://docs.getodk.org/form-question-types/)
- [ODK Form Logic](https://docs.getodk.org/form-logic/)
- [ODK Operators and Functions](https://docs.getodk.org/form-operators-functions/)

### Project-Specific Docs

- `.claude/CLAUDE.md` - Project memory and quick reference
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

**[FolderManifest Free Tools](https://www.foldermanifest.com/free-tools)** - Free online tools for everyone:

- **[Compare Files Online](https://www.foldermanifest.com/free-tools/compare-files)** - Upload 2 files to instantly check if they are identical using SHA-256 checksums
- **[Find Duplicate Files](https://www.foldermanifest.com/free-tools/find-duplicates)** - Upload up to 10 files to quickly identify duplicates
- **[File Metadata Viewer](https://www.foldermanifest.com/free-tools/metadata-viewer)** - Extract detailed metadata from your files
- **[Compare Folders Online](https://www.foldermanifest.com/free-tools/folder-compare)** - Upload 2 folders to find missing, modified, or duplicate files

These tools are part of ARCED International's commitment to providing high-quality solutions for research, learning, and development work.

## Acknowledgments

- [XLSForm](https://xlsform.org/) for the form specification
- [ODK](https://odk.org/) for the XForm standard
- [Claude Code](https://claude.ai/code) for the AI-powered development environment

## Support

- 📖 [Documentation](https://github.com/ARCED-International/xlsform-ai/wiki)
- 🐛 [Issues](https://github.com/ARCED-International/xlsform-ai/issues)
- 💬 [Discussions](https://github.com/ARCED-International/xlsform-ai/discussions)
- 🌐 [ARCED International](https://arced-international.com)

---

Made with ❤️ by [ARCED International](https://arced-international.com)
