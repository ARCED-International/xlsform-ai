"""Activity logger for XLSForm AI projects."""

import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional


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

    def _find_log_file(self) -> Path:
        """Find existing log file or determine new log file path.

        Ensures only ONE activity log file exists per project.
        If multiple are found, keeps the most recent and deletes the others.

        Returns:
            Path to log file
        """
        # Use a fixed filename - no timestamps
        log_filename = "activity_log.html"
        log_path = self.project_dir / log_filename

        # Find all existing activity log files (including old timestamped ones)
        existing_logs = []
        for file in self.project_dir.glob("activity_log*.html"):
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

        # If the most recent log is not named "activity_log.html", rename it
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

        # Add new entry
        entry = {
            "timestamp": datetime.now().isoformat(),
            "date": datetime.now().strftime("%Y-%m-%d"),
            "time": datetime.now().strftime("%H:%M:%S"),
            "action_type": action_type,
            "description": description,
            "details": details,
            "author": author or "Claude Code",
            "location": location or "Unknown"
        }

        data["entries"].append(entry)
        data["total_actions"] += 1
        data["last_updated"] = datetime.now().isoformat()

        # Save updated log
        self._save_log(data)

        return self.log_file

    def _load_log_data(self) -> dict:
        """Load existing log data or create new structure.

        Returns:
            dict with log data
        """
        default_data = {
            "version": LOG_VERSION,
            "tag": LOG_FILE_TAG,
            "project_name": self.project_name,
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

    def _generate_html(self, data: dict) -> str:
        """Generate HTML content for activity log with filtering.

        Args:
            data: Log data dictionary

        Returns:
            HTML string
        """
        # Reverse entries for newest-first display
        entries = list(reversed(data["entries"]))

        # Extract unique values for filters
        action_types = sorted(set(entry.get("action_type", "") for entry in data["entries"]))
        authors = sorted(set(entry.get("author", "") for entry in data["entries"]))
        dates = sorted(set(entry.get("date", "") for entry in data["entries"]), reverse=True)

        return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>XLSForm AI Activity Log - {data["project_name"]}</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 20px;
            line-height: 1.6;
        }}

        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 12px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            overflow: hidden;
        }}

        .header {{
            background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
            color: white;
            padding: 40px;
            text-align: center;
        }}

        .logo {{
            max-width: 200px;
            height: auto;
            margin-bottom: 20px;
            filter: brightness(0) invert(1);
        }}

        h1 {{
            font-size: 2.5em;
            margin-bottom: 10px;
            font-weight: 700;
        }}

        .subtitle {{
            font-size: 1.1em;
            opacity: 0.9;
        }}

        .stats {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            padding: 30px 40px;
            background: #f8f9fa;
        }}

        .stat-card {{
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            text-align: center;
        }}

        .stat-value {{
            font-size: 2em;
            font-weight: 700;
            color: #2a5298;
        }}

        .stat-label {{
            color: #6c757d;
            font-size: 0.9em;
            margin-top: 5px;
        }}

        .filters {{
            background: #f8f9fa;
            padding: 20px 40px;
            border-bottom: 2px solid #e9ecef;
        }}

        .filter-group {{
            display: inline-block;
            margin-right: 20px;
            margin-bottom: 10px;
        }}

        .filter-group label {{
            display: block;
            font-weight: 600;
            color: #2a5298;
            margin-bottom: 5px;
            font-size: 0.9em;
        }}

        .filter-group select, .filter-group input[type="date"], .filter-group input[type="text"] {{
            padding: 8px 12px;
            border: 2px solid #dee2e6;
            border-radius: 6px;
            font-size: 0.9em;
            background: white;
            min-width: 150px;
            cursor: pointer;
        }}

        .filter-group select:focus, .filter-group input:focus {{
            outline: none;
            border-color: #667eea;
        }}

        .search-box {{
            width: 300px;
            padding: 10px 15px;
            border: 2px solid #dee2e6;
            border-radius: 25px;
            font-size: 0.95em;
            margin-left: 20px;
        }}

        .search-box:focus {{
            outline: none;
            border-color: #667eea;
        }}

        .results-count {{
            background: #667eea;
            color: white;
            padding: 5px 15px;
            border-radius: 20px;
            font-weight: 600;
            margin-left: 20px;
        }}

        .content {{
            padding: 40px;
        }}

        .timeline {{
            position: relative;
            padding-left: 30px;
        }}

        .timeline::before {{
            content: '';
            position: absolute;
            left: 0;
            top: 0;
            bottom: 0;
            width: 3px;
            background: linear-gradient(to bottom, #667eea, #764ba2);
        }}

        .entry {{
            position: relative;
            margin-bottom: 30px;
            padding: 20px;
            background: #f8f9fa;
            border-radius: 8px;
            border-left: 4px solid #667eea;
        }}

        .entry.hidden {{
            display: none;
        }}

        .entry::before {{
            content: '';
            position: absolute;
            left: -36px;
            top: 25px;
            width: 12px;
            height: 12px;
            border-radius: 50%;
            background: #667eea;
            border: 3px solid white;
            box-shadow: 0 0 0 3px #667eea;
        }}

        .entry-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 10px;
            flex-wrap: wrap;
            gap: 10px;
        }}

        .entry-type {{
            display: inline-block;
            padding: 5px 15px;
            background: linear-gradient(135deg, #667eea, #764ba2);
            color: white;
            border-radius: 20px;
            font-size: 0.85em;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}

        .entry-date {{
            color: #6c757d;
            font-size: 0.9em;
        }}

        .entry-description {{
            font-size: 1.2em;
            font-weight: 600;
            color: #2a5298;
            margin-bottom: 10px;
        }}

        .entry-details {{
            background: white;
            padding: 15px;
            border-radius: 6px;
            font-family: 'Courier New', monospace;
            font-size: 0.9em;
            color: #495057;
            white-space: pre-wrap;
            word-break: break-word;
        }}

        .entry-meta {{
            display: flex;
            gap: 20px;
            margin-top: 10px;
            font-size: 0.85em;
            color: #6c757d;
        }}

        .entry-meta span {{
            display: flex;
            align-items: center;
            gap: 5px;
        }}

        .no-results {{
            text-align: center;
            padding: 60px 20px;
            color: #6c757d;
            font-size: 1.2em;
            display: none;
        }}

        .no-results::before {{
            content: "🔍";
            display: block;
            font-size: 4em;
            margin-bottom: 20px;
        }}

        .footer {{
            background: #2a5298;
            color: white;
            text-align: center;
            padding: 30px;
        }}

        .footer a {{
            color: white;
            text-decoration: underline;
        }}

        @media (max-width: 768px) {{
            .stats {{
                grid-template-columns: 1fr;
            }}

            .entry-header {{
                flex-direction: column;
                align-items: flex-start;
            }}

            h1 {{
                font-size: 1.8em;
            }}

            .search-box {{
                width: 100%;
                margin-left: 0;
                margin-top: 10px;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <img src="https://www.arced-international.com/_next/image?url=%2F_next%2Fstatic%2Fmedia%2Farced-int_logo.5040257d.png&w=3840&q=75" alt="ARCED International Logo" class="logo">
            <h1>XLSForm AI Activity Log</h1>
            <p class="subtitle">Project: {data["project_name"]}</p>
        </div>

        <div class="stats">
            <div class="stat-card">
                <div class="stat-value">{data["total_actions"]}</div>
                <div class="stat-label">Total Actions</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{datetime.fromisoformat(data["created"]).strftime("%b %d, %Y")}</div>
                <div class="stat-label">Project Created</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{datetime.fromisoformat(data["last_updated"]).strftime("%b %d, %Y")}</div>
                <div class="stat-label">Last Updated</div>
            </div>
        </div>

        <div class="filters">
            <div class="filter-group">
                <label>Action Type</label>
                <select id="filter-action-type">
                    <option value="">All Types</option>
                    {"".join(f'<option value="{at}">{at}</option>' for at in action_types)}
                </select>
            </div>

            <div class="filter-group">
                <label>Author</label>
                <select id="filter-author">
                    <option value="">All Authors</option>
                    {"".join(f'<option value="{author}">{author}</option>' for author in authors)}
                </select>
            </div>

            <div class="filter-group">
                <label>From Date</label>
                <input type="date" id="filter-date-from" min="{min(dates) if dates else ''}">
            </div>

            <div class="filter-group">
                <label>To Date</label>
                <input type="date" id="filter-date-to" max="{max(dates) if dates else ''}">
            </div>

            <input type="text" class="search-box" id="filter-search" placeholder="Search descriptions and details...">
            <div class="results-count" id="results-count">{len(data["entries"])} shown</div>
        </div>

        <div class="content">
            <h2 style="margin-bottom: 20px; color: #2a5298;">Activity Timeline</h2>
            <div class="timeline" id="timeline">
"""

        # Add entries with data attributes for filtering
        entries_html = ""
        for entry in entries:
            entries_html += f"""
                <div class="entry"
                     data-action-type="{entry.get('action_type', '')}"
                     data-author="{entry.get('author', '')}"
                     data-date="{entry.get('date', '')}"
                     data-description="{entry.get('description', '').lower()}"
                     data-details="{entry.get('details', '').lower()}">
                    <div class="entry-header">
                        <span class="entry-type">{entry["action_type"]}</span>
                        <span class="entry-date">{entry["date"]} at {entry["time"]}</span>
                    </div>
                    <div class="entry-description">{entry["description"]}</div>
                    {f'<div class="entry-details">{entry["details"]}</div>' if entry["details"] else ''}
                    <div class="entry-meta">
                        <span>👤 {entry["author"]}</span>
                        {f'<span>📍 {entry["location"]}</span>' if entry.get("location") and entry["location"] != "Unknown" else ''}
                    </div>
                </div>
            """

        # Complete the HTML
        html += f"""
            </div>
            <div class="no-results" id="no-results">
                No entries match your filters
            </div>
        </div>

        <div class="footer">
            <p>Powered by <a href="https://github.com/ARCED-International/xlsform-ai" target="_blank">XLSForm AI</a> by ARCED International</p>
            <p style="margin-top: 10px; font-size: 0.9em; opacity: 0.8;">
                An open source project by <a href="https://arced-international.com" target="_blank">ARCED International</a>
            </p>
        </div>
    </div>

    <script>
        // Filter functionality
        const entries = document.querySelectorAll('.entry');
        const resultsCount = document.getElementById('results-count');
        const noResults = document.getElementById('no-results');

        function applyFilters() {{
            const actionType = document.getElementById('filter-action-type').value.toLowerCase();
            const author = document.getElementById('filter-author').value.toLowerCase();
            const dateFrom = document.getElementById('filter-date-from').value;
            const dateTo = document.getElementById('filter-date-to').value;
            const searchText = document.getElementById('filter-search').value.toLowerCase();

            let visibleCount = 0;

            entries.forEach(entry => {{
                const entryActionType = entry.dataset.actionType.toLowerCase();
                const entryAuthor = entry.dataset.author.toLowerCase();
                const entryDate = entry.dataset.date;
                const entryDescription = entry.dataset.description;
                const entryDetails = entry.dataset.details;

                // Check each filter
                const matchesActionType = !actionType || entryActionType === actionType;
                const matchesAuthor = !author || entryAuthor === author;
                const matchesDateFrom = !dateFrom || entryDate >= dateFrom;
                const matchesDateTo = !dateTo || entryDate <= dateTo;
                const matchesSearch = !searchText ||
                    entryDescription.includes(searchText) ||
                    entryDetails.includes(searchText);

                const isVisible = matchesActionType && matchesAuthor && matchesDateFrom && matchesDateTo && matchesSearch;

                entry.classList.toggle('hidden', !isVisible);
                if (isVisible) visibleCount++;
            }});

            // Update UI
            resultsCount.textContent = `${{visibleCount}} shown`;
            noResults.style.display = visibleCount === 0 ? 'block' : 'none';
        }}

        // Add event listeners
        document.getElementById('filter-action-type').addEventListener('change', applyFilters);
        document.getElementById('filter-author').addEventListener('change', applyFilters);
        document.getElementById('filter-date-from').addEventListener('change', applyFilters);
        document.getElementById('filter-date-to').addEventListener('change', applyFilters);
        document.getElementById('filter-search').addEventListener('input', applyFilters);

        // Clear filters button
        const clearBtn = document.createElement('button');
        clearBtn.textContent = 'Clear Filters';
        clearBtn.style.cssText = 'margin-left: 10px; padding: 8px 15px; background: #6c757d; color: white; border: none; border-radius: 6px; cursor: pointer;';
        clearBtn.onclick = () => {{
            document.getElementById('filter-action-type').value = '';
            document.getElementById('filter-author').value = '';
            document.getElementById('filter-date-from').value = '';
            document.getElementById('filter-date-to').value = '';
            document.getElementById('filter-search').value = '';
            applyFilters();
        }};
        document.querySelector('.filters').appendChild(clearBtn);
    </script>

    <!-- XLSFORM_AI_DATA_START -->
    {json.dumps(data, indent=2)}
    <!-- XLSFORM_AI_DATA_END -->
</body>
</html>
"""

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
