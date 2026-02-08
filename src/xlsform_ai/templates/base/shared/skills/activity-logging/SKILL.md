# Activity Logging Skill

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
- Example: if imported names raise warnings (e.g., q308_phq1, fiq_1), ask naming decision first and wait for reply.
Track all XLSForm project activities automatically.

## When to Use

**ALWAYS** log activities when working with XLSForm:
- Adding, modifying, or removing questions
- Validating the form
- Importing from external files (PDF, Word, Excel)
- Analyzing or modifying form structure
- **ANY other XLSForm modifications**

## How to Log

### Step 1: Check if logging is enabled

```python
from scripts.config import ProjectConfig

config = ProjectConfig()
if config.is_activity_logging_enabled():
    # Proceed with logging
```

### Step 2: Log the action

```python
from scripts.log_activity import ActivityLogger

logger = ActivityLogger()
logger.log_action(
    action_type="add_questions",
    description="Added 3 questions",
    details="Questions: respondent_name, respondent_age, respondent_gender\nRows: 5, 10, 15"
)
```

## Action Types

Use these specific `action_type` values:

| Action Type | When to Use |
|-------------|-------------|
| `add_questions` | Adding new questions |
| `update_questions` | Modifying existing questions |
| `remove_questions` | Deleting questions |
| `validate` | Running form validation |
| `import_pdf` | Importing from PDF |
| `import_docx` | Importing from Word document |
| `import_xlsx` | Importing from Excel |
| `analyze_structure` | Analyzing form structure |
| `cleanup` | Cleaning up unused items |

## Parameters

- `action_type` (required): Type of action (see table above)
- `description` (required): Brief human-readable description
- `details` (optional): Detailed information about the action
- `author` (optional): Author name (auto-detected if not provided)
- `location` (optional): Author location (auto-detected if not provided)

## View Activity Log

The activity log is saved as `activity_log.html` in your project directory.

**Open it in a browser to see:**
- Complete activity history
- Filter by action type, author, date range
- Search across descriptions and details
- Export to CSV or JSON
- Sort by any column
- Pagination for large logs

## Examples

### Adding Questions

```python
from scripts.log_activity import ActivityLogger

logger = ActivityLogger()
logger.log_action(
    action_type="add_questions",
    description="Added 5 questions about demographics",
    details="Questions: respondent_name, respondent_age, respondent_gender, respondent_education, respondent_occupation\nRows: 5, 10, 15, 20, 25"
)
```

### Validating Form

```python
from scripts.log_activity import ActivityLogger

logger = ActivityLogger()
logger.log_action(
    action_type="validate",
    description="Form validation completed",
    details="Errors: 0\nWarnings: 2\n- Missing label for q5\n- Invalid constraint in q10"
)
```

### Importing from PDF

```python
from scripts.log_activity import ActivityLogger

logger = ActivityLogger()
logger.log_action(
    action_type="import_pdf",
    description=f"Imported 15 questions from PDF",
    details=f"Source: questionnaire.pdf\nPages: 1-5\nQuestions extracted: 15"
)
```

## Important Notes

- **NEVER skip activity logging** for XLSForm modifications
- **ALWAYS import from** `scripts/` directory
- The log tracks **collaboration and changes** over time
- Essential for **audit trails** and **project management**
- Users can **disable logging** in `xlsform-ai.json` if needed
- Activity log is **preserved** across re-initializations

## Troubleshooting

**Activity log not being created?**
- Check if `log_activity: true` in `xlsform-ai.json`
- Verify `activity_log_template.html` exists in `scripts/` directory
- Ensure you're importing from `scripts/`, not other locations

**Need to view log without browser?**
- The log data is embedded in the HTML between `<!-- XLSFORM_AI_DATA_START -->` and `<!-- XLSFORM_AI_DATA_END -->` markers
- You can extract the JSON data programmatically




