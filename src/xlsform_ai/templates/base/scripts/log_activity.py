"""Activity logger for XLSForm AI projects."""

import base64
import io
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional
# CRITICAL: Add scripts directory to Python path for sibling imports
# This allows the script to find sibling modules whether run from project root or scripts dir
_scripts_dir = Path(__file__).parent.resolve()
if str(_scripts_dir) not in sys.path:
    sys.path.insert(0, str(_scripts_dir))



LOG_FILE_TAG = "XLSFORM_AI_ACTIVITY_LOG"
LOG_VERSION = "1.0"


class ActivityLogger:
    """Logger for tracking XLSForm AI activities."""

    def __init__(self, project_dir: Optional[Path] = None):
        """Initialize logger.

        Args:
            project_dir: Project directory. Defaults to current working directory.
        """
        self.project_dir = Path(project_dir) if project_dir else Path.cwd()

        # Try to load project name from config
        try:
            from config import ProjectConfig
            config = ProjectConfig(self.project_dir)
            self.project_name = config.get_project_name()
        except:
            self.project_name = self.project_dir.name

        self.log_file = self._find_log_file()

        # Store effective author for this session
        self._effective_author = self._get_effective_author()
        self._effective_location = self._get_effective_location()
        self._xlsform_path = self._get_xlsform_path()

    def _get_xlsform_path(self) -> Optional[Path]:
        """Get XLSForm file path for reading settings metadata."""
        try:
            from config import ProjectConfig
            config = ProjectConfig(self.project_dir)
            return config.get_full_xlsform_path()
        except Exception:
            default_path = self.project_dir / "survey.xlsx"
            return default_path if default_path.exists() else None

    def _get_effective_author(self) -> str:
        """Get effective author name with intelligent fallback.

        Priority:
        1. Configured author in xlsform-ai.json
        2. Detected system username (with generic filtering)
        3. Fallback to "User"

        Returns:
            Author name string
        """
        # Try to get from project config first
        try:
            from config import ProjectConfig
            config = ProjectConfig(self.project_dir)
            author = config.get_effective_author()
            if author:
                return author
        except Exception:
            pass

        # Fall back to detection utilities
        try:
            from author_utils import get_detected_author
            return get_detected_author()
        except Exception:
            return "User"

    def _find_log_file(self) -> Path:
        """Find existing log file or determine new log file path.

        Ensures only ONE activity log file exists per project.
        If multiple are found, keeps the most recent and deletes the others.

        Returns:
            Path to log file
        """
        # Get the configured log file name
        try:
            from config import ProjectConfig
            config = ProjectConfig(self.project_dir)
            log_filename = config.get_activity_log_file()
        except Exception:
            # Fallback to default if config is not available
            log_filename = "activity_log.html"

        log_path = self.project_dir / log_filename

        # Find all existing activity log files (including old ones with different names)
        existing_logs = []
        for file in self.project_dir.glob("*.html"):
            try:
                with open(file, 'r', encoding='utf-8') as f:
                    # Check first 1000 chars for tag
                    content = f.read(1000)
                    if LOG_FILE_TAG in content:
                        existing_logs.append(file)
            except:
                pass

        if not existing_logs:
            # No existing log found, return the new file path
            return log_path

        # Sort existing logs by modification time (most recent first)
        existing_logs.sort(key=lambda f: f.stat().st_mtime, reverse=True)

        # Keep the most recent log file
        most_recent_log = existing_logs[0]

        # If the most recent log is not named according to config, rename it
        if most_recent_log.name != log_filename:
            try:
                most_recent_log.rename(log_path)
                return log_path
            except Exception:
                # If rename fails, use the most recent log as-is
                return most_recent_log

        # Delete any older log files (there should only be one now)
        for old_log in existing_logs[1:]:
            try:
                if old_log != log_path and old_log.exists():
                    old_log.unlink()
            except Exception:
                pass  # Ignore errors when cleaning up old logs

        return log_path

    def _get_effective_location(self) -> str:
        """Get effective location label for activity logging."""
        try:
            from config import ProjectConfig
            config = ProjectConfig(self.project_dir)
            location = config.get_location()
            if location:
                return location
        except Exception:
            pass

        try:
            from author_utils import get_effective_location
            return get_effective_location(self.project_dir)
        except Exception:
            return "Unknown"

    def log_action(self, action_type: str, description: str, details: str = "",
                   author: Optional[str] = None, location: Optional[str] = None):
        """Log an action to the activity log.

        Args:
            action_type: Type of action (e.g., "add_questions", "validate", "import")
            description: Brief description of the action
            details: Detailed information about the action
            author: Author name (optional)
            location: Author location (optional)
        """
        # Load existing data
        data = self._load_log_data()
        self._update_form_settings_metadata(data)
        self._warn_if_missing_settings()

        # Add new entry
        entry = {
            "timestamp": datetime.now().isoformat(),
            "date": datetime.now().strftime("%Y-%m-%d"),
            "time": datetime.now().strftime("%H:%M:%S"),
            "action_type": action_type,
            "description": description,
            "details": details,
            "author": author or self._effective_author,
            "location": location or self._effective_location or "Unknown"
        }

        data["entries"].append(entry)
        data["total_actions"] += 1
        data["last_updated"] = datetime.now().isoformat()

        # Save updated log
        self._save_log(data)

        return self.log_file

    def _warn_if_missing_settings(self) -> None:
        """Warn once per session if required settings are missing."""
        try:
            from settings_utils import missing_required_settings
        except Exception:
            return

        if not self._xlsform_path or not self._xlsform_path.exists():
            return

        missing = missing_required_settings(self._xlsform_path)
        if missing:
            missing_list = ", ".join(missing)
            try:
                from rich.console import Console
                console = Console()
                console.print("")
                console.print(f"[bold white on red] ACTION REQUIRED [/bold white on red] Missing required settings: {missing_list}")
                console.print("[bold yellow]Set them in the settings sheet (row 2) or run:[/bold yellow] `xlsform-ai update-settings --title \"...\" --id \"...\"`")
                console.print("")
            except Exception:
                print(f"\n[ACTION REQUIRED] Missing required settings: {missing_list}")
                print("Set them in the settings sheet (row 2) or run: xlsform-ai update-settings --title \"...\" --id \"...\"")
                print("")

    def _update_form_settings_metadata(self, data: dict) -> None:
        """Update log metadata with current form title and ID."""
        try:
            from settings_utils import read_form_settings
        except Exception:
            return

        if not self._xlsform_path or not self._xlsform_path.exists():
            return

        settings = read_form_settings(self._xlsform_path)
        data["form_title"] = settings.get("form_title", "")
        data["form_id"] = settings.get("form_id", "")

    def _load_log_data(self) -> dict:
        """Load existing log data or create new structure.

        Returns:
            dict with log data
        """
        default_data = {
            "version": LOG_VERSION,
            "tag": LOG_FILE_TAG,
            "project_name": self.project_name,
            "form_title": "",
            "form_id": "",
            "created": datetime.now().isoformat(),
            "last_updated": datetime.now().isoformat(),
            "total_actions": 0,
            "entries": []
        }

        if not self.log_file.exists():
            return default_data

        try:
            # Try to extract JSON data from existing HTML
            with open(self.log_file, 'r', encoding='utf-8') as f:
                content = f.read()
                # Find JSON data between specific markers
                start_marker = "<!-- XLSFORM_AI_DATA_START -->"
                end_marker = "<!-- XLSFORM_AI_DATA_END -->"

                start_idx = content.find(start_marker)
                if start_idx > 0:
                    start_idx += len(start_marker)
                    end_idx = content.find(end_marker, start_idx)
                    if end_idx > start_idx:
                        json_str = content[start_idx:end_idx].strip()
                        return json.loads(json_str)
        except:
            pass

        return default_data

    def _save_log(self, data: dict):
        """Save log data as formatted HTML file.

        Args:
            data: Log data dictionary
        """
        html = self._generate_html(data)

        with open(self.log_file, 'w', encoding='utf-8') as f:
            f.write(html)

    def _get_base64_logo(self) -> str:
        """Get ARCED Foundation logo as base64-encoded data URI.

        Returns:
            Base64 data URI string for offline use
        """
        # Try to load logo from branding folder
        logo_paths = [
            Path("J:/My Drive/ARCED International/Branding/arced-int.png"),
            Path(__file__).parent.parent / "arced-int.png",
            self.project_dir / "arced-int.png",
        ]

        for logo_path in logo_paths:
            try:
                if logo_path.exists():
                    # Import PIL here to avoid dependency if not available
                    try:
                        from PIL import Image
                        img = Image.open(logo_path)

                        # Resize to reasonable header size (max height 96px)
                        max_height = 96
                        aspect_ratio = img.width / img.height
                        new_height = max_height
                        new_width = int(new_height * aspect_ratio)

                        img_resized = img.resize((new_width, new_height), Image.Resampling.LANCZOS)

                        # Save to buffer and encode
                        buffer = io.BytesIO()
                        img_resized.save(buffer, format='PNG', optimize=True)
                        buffer.seek(0)

                        logo_data = buffer.read()
                        logo_b64 = base64.b64encode(logo_data).decode('utf-8')
                        return f"data:image/png;base64,{logo_b64}"
                    except ImportError:
                        # PIL not available, use raw file
                        with open(logo_path, 'rb') as f:
                            logo_data = f.read()
                            logo_b64 = base64.b64encode(logo_data).decode('utf-8')
                            return f"data:image/png;base64,{logo_b64}"
            except Exception:
                continue

        # Fallback to a simple colored rectangle if no logo found
        # This ensures the activity log always works
        return "data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iNDgiIGhlaWdodD0iNDgiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyI+PHJlY3Qgd2lkdGg9IjQ4IiBoZWlnaHQ9IjQ4IiBmaWxsPSIjMkM1RjdEIi8+PC9zdmc+"
    def _generate_html(self, data: dict) -> str:
        """Generate modern, professional HTML for activity log.

        Features:
        - Hybrid table view with expandable rows
        - Column resizing, sorting, visibility toggle
        - Export to CSV/JSON
        - Pagination
        - Filtering (action type, author, date range, search)
        - Completely offline compatible

        Args:
            data: Log data dictionary

        Returns:
            HTML string
        """
        # Get logo as base64 data URI
        logo_data_uri = self._get_base64_logo()

        # Try to read the template file
        template_path = Path(__file__).parent / 'activity_log_template.html'

        # Fallback: use built-in template if file doesn't exist
        if not template_path.exists():
            return self._generate_html_fallback(data, logo_data_uri)

        with open(template_path, 'r', encoding='utf-8') as f:
            template = f.read()

        # Embed the data
        json_data = json.dumps(data, indent=2)

        # Replace placeholders in template
        html = template.replace('{DATA}', json_data)

        return html

    def _generate_html_fallback(self, data: dict, logo_data_uri: str) -> str:
        """Fallback HTML generation if template file is not found.

        Args:
            data: Log data dictionary
            logo_data_uri: Base64 encoded logo

        Returns:
            HTML string
        """
        # This is a simplified version - in production, the template should always exist
        entries = list(reversed(data.get("entries", [])))

        return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Activity Log - {data.get("project_name", "XLSForm")}</title>
    <style>
        body {{ font-family: -apple-system, sans-serif; line-height: 1.6; padding: 2rem; }}
        .entry {{ border: 1px solid #ddd; padding: 1rem; margin-bottom: 1rem; border-radius: 8px; }}
        .entry-type {{ background: #2C5F7D; color: white; padding: 0.25rem 0.75rem; border-radius: 4px; font-size: 0.75rem; text-transform: uppercase; }}
        .details {{ background: #f5f5f5; padding: 1rem; border-radius: 4px; font-family: monospace; white-space: pre-wrap; margin-top: 0.5rem; }}
    </style>
</head>
<body>
    <h1>Activity Log - {data.get("project_name", "XLSForm")}</h1>
    <p><strong>Template file not found. Please ensure activity_log_template.html exists.</strong></p>
    {"".join(f'<div class="entry"><span class="entry-type">{e.get("action_type", "")}</span><h3>{e.get("description", "")}</h3><div class="details">{e.get("details", "")}</div></div>' for e in entries)}
    <div style="display:none;">
        <!-- XLSFORM_AI_DATA_START -->
        {json.dumps(data, indent=2)}
        <!-- XLSFORM_AI_DATA_END -->
    </div>
</body>
</html>"""

    def get_summary(self) -> dict:
        """Get summary of logged activities.

        Returns:
            dict with summary statistics
        """
        data = self._load_log_data()
        return {
            "log_file": str(self.log_file),
            "total_actions": data["total_actions"],
            "created": data["created"],
            "last_updated": data["last_updated"],
            "recent_actions": list(reversed(data["entries"]))[-5:]  # Last 5 actions
        }


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python log_activity.py <action_type> <description> [details] [author] [location]")
        print("Example: python log_activity.py add_questions 'Added 2 questions' 'first_name, last_name'")
        sys.exit(1)

    action_type = sys.argv[1]
    description = sys.argv[2]
    details = sys.argv[3] if len(sys.argv) > 3 else ""
    author = sys.argv[4] if len(sys.argv) > 4 else None
    location = sys.argv[5] if len(sys.argv) > 5 else None

    logger = ActivityLogger()
    log_file = logger.log_action(action_type, description, details, author, location)

    print(f"Activity logged to: {log_file.name}")
    summary = logger.get_summary()
    print(f"Total actions: {summary['total_actions']}")
