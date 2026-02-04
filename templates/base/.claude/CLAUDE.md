# XLSForm AI Project

This is an XLSForm project with AI-assisted development capabilities using Claude Code.

**An open source project by [ARCED International](https://arced-international.com)**

## Project Overview

This project uses the **xlsform-core** skill to help you create, modify, and validate XLSForms efficiently. The skill provides comprehensive knowledge about XLSForm syntax, question types, and best practices.

## Working with XLSForms

### Key Principles

1. **Always use the xlsform-core skill** for XLSForm operations - it has comprehensive knowledge of XLSForm syntax and features
2. **Use xlwings for open Excel files** to preserve formatting
3. **Use openpyxl for closed files** when formatting is less critical
4. **Reference official documentation** at https://xlsform.org/en/

### Excel File Location

The main XLSForm file is `survey.xlsx` in the project root.

**Important:** Never close the Excel file when using xlwings - let the user close it.

## File Structure

```
.
├── survey.xlsx              # Main XLSForm file (edit this!)
├── package.json             # npm scripts for watch/reload
├── scripts/                 # Utility scripts
│   ├── parse_pdf.py         # PDF question extraction
│   ├── parse_docx.py        # Word question extraction
│   ├── parse_xlsx.py        # Excel question extraction
│   ├── xlwings_helper.py    # Excel editing with xlwings
│   └── validate_form.py     # XLSForm validation
└── .claude/                 # Claude Code configuration
    ├── commands/            # Slash commands
    └── skills/              # XLSForm knowledge
```

## Available Commands

Use these slash commands in Claude Code:

### /xlsform-add
Add new questions to the form.
```
/xlsform-add Add a text question asking for respondent name
/xlsform-add Add a select_one question for favorite fruits with options: Apple, Banana, Orange
```

### /xlsform-import
Import questions from external files.
```
/xlsform-import questions.pdf --pages 1-10
/xlsform-import questionnaire.docx
```

### /xlsform-validate
Validate the form for errors.
```
/xlsform-validate
/xlsform-validate --fix
```

### /xlsform-update
Modify existing questions.
```
/xlsform-update Update the age question to add a constraint
```

### /xlsform-remove
Remove questions or choice lists.
```
/xlsform-remove Remove the question named 'old_question'
```

### /xlsform-move
Reorder questions in the form.
```
/xlsform-move Move the name question to the top
```

## Common Operations

### Adding Questions

1. Use `/xlsform-add` for single questions
2. Use `/xlsform-import` for bulk import from files
3. Claude will automatically detect question types from natural language
4. Choice lists are created automatically when needed

### Editing Excel Files

**When file is OPEN:**
- Use xlwings (via `scripts/xlwings_helper.py`)
- Preserves all formatting
- Real-time preview available

**When file is CLOSED:**
- Use openpyxl (faster for batch operations)
- Formatting may not be preserved perfectly
- Better for automated changes

### Validation

Always validate after making changes:
```
/xlsform-validate
```

This checks for:
- Duplicate names
- Invalid types
- Missing choice lists
- Syntax errors
- Best practices violations

## Best Practices

### Question Names
- Use snake_case: `respondent_age`, not `Respondent Age`
- Be descriptive but concise: `hh_head_age` for household head age
- Always unique - no duplicates

### Choice Lists
- Reuse common lists: `yes_no`, `gender`, `agreement`
- Match list_name exactly between survey type and choices sheet
- Avoid spaces in choice names (especially for select_multiple)

### Form Structure
- Group related questions
- Use begin_group/end_group for organization
- Use begin_repeat/end_repeat for repeated items
- Always close groups and repeats in the right order

### Constraints and Relevance
- Use `${field_name}` to reference other fields
- Use `.` for the current field in constraints
- Test complex relevance logic thoroughly

## Troubleshooting

### "list_name not found" Error

**Cause:** The list name after `select_one` or `select_multiple` doesn't match any `list_name` in the choices sheet.

**Solution:**
1. Check the type column: `select_one fruits`
2. Check choices sheet has: `list_name = fruits`
3. Check for typos (fruit vs fruits)

### Duplicate Name Errors

**Cause:** Two questions have the same name.

**Solution:**
1. Run `/xlsform-validate` to find duplicates
2. Rename one of the questions
3. Use descriptive names: `q1_name`, `q2_name`

### Format Removed

**Cause:** Using openpyxl on a formatted file.

**Solution:**
1. Keep the file open in Excel
2. Use xlwings to make changes
3. Or restore formatting from a backup

### Form Won't Convert

**Common causes:**
- Invalid question type (selct_one vs select_one)
- Unbalanced begin/end groups or repeats
- Missing required columns (type, name, label)

**Solution:**
1. Run `/xlsform-validate`
2. Fix all critical errors
3. Try converting again

### xlwings Can't Find Excel

**Cause:** Excel is not running or file is not open.

**Solution:**
1. Open the Excel file
2. Activate Python environment with xlwings
3. Try again, or use openpyxl for closed files

## ODK Central Integration (Optional)

If using ODK Central for testing:

1. Configure `~/.pyodk_config.toml`:
```toml
central.url = "https://your.central.server"
central.username = "your-username"
central.password = "your-password"
central.project_id = 1
```

2. Use watch mode for automatic upload:
```bash
npm run watch
```

This will:
- Watch for changes to survey.xlsx
- Upload to ODK Central when changes are detected
- Reload the browser preview

## Quick Reference

### Question Types

**Text:** `text`, `integer`, `decimal`, `note`
**Select:** `select_one listname`, `select_multiple listname`
**Date/Time:** `date`, `time`, `dateTime`
**Geo:** `geopoint`, `geotrace`, `geoshape`
**Media:** `image`, `audio`, `video`
**Metadata:** `start`, `end`, `today`, `deviceid`, `audit`

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

**Required:**
```
required: yes
required_message: This field is required
```

**Cascading select:**
```
choice_filter: parent_field=${parent_field}
```

## Getting Help

### XLSForm Resources
- **XLSForm documentation:** https://xlsform.org/en/
- **ODK documentation:** https://docs.getodk.org/
- **Question types:** https://docs.getodk.org/form-question-types/
- **Form logic:** https://docs.getodk.org/form-logic/

### ARCED International Tools

**[XLSForm AI](https://github.com/ARCED-International/xlsform-ai)** - This tool! AI-powered XLSForm creation with Claude Code.

**[FolderManifest](https://www.foldermanifest.com)** - Offline folder audit manifest software for Windows. A lightweight paid desktop tool for generating folder trees, verifying checksum manifests, and cleaning up duplicate files.

**[FolderManifest Free Tools](https://www.foldermanifest.com/free-tools)** - Free online tools:
  - **[Compare Files Online](https://www.foldermanifest.com/free-tools/compare-files)** - Check if files are identical using SHA-256
  - **[Find Duplicate Files](https://www.foldermanifest.com/free-tools/find-duplicates)** - Quickly identify duplicate files
  - **[File Metadata Viewer](https://www.foldermanifest.com/free-tools/metadata-viewer)** - Extract detailed file metadata
  - **[Compare Folders Online](https://www.foldermanifest.com/free-tools/folder-compare)** - Find missing or modified files between folders

These tools are part of ARCED International's commitment to providing high-quality solutions for humanitarian and development work.

## Tips for Success

1. **Start simple** - Add basic questions first, then add complexity
2. **Validate often** - Run `/xlsform-validate` after each change
3. **Test thoroughly** - Fill out the form to check logic works
4. **Keep backups** - Save versions before major changes
5. **Use xlwings** - Keep file open for live preview
6. **Ask for help** - Claude knows XLSForm well, use it!

## Project-Specific Notes

Add any project-specific notes here:

- Form ID: [your-form-id]
- Project: [project-description]
- Last updated: [date]
- Organization: [your-organization]

---

**About ARCED International**

ARCED International is a humanitarian organization committed to serving vulnerable populations worldwide. We develop open-source and commercial tools to support data collection, monitoring and evaluation, and file management in humanitarian contexts.

Learn more at: https://arced-international.com
