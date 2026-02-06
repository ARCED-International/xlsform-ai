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

        # Store effective author for this session
        self._effective_author = self._get_effective_author()

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
            "author": author or self._effective_author,
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

    def _get_base64_logo(self) -> str:
        """Get ARCED Foundation logo as base64-encoded data URI.

        Returns:
            Base64 data URI string for offline use
        """
        # ARCED Foundation logo - pre-encoded for offline use
        # This ensures the activity log works completely offline
        logo_b64 = """data:image/png;base64,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"""

        return logo_b64

    def _generate_html(self, data: dict) -> str:
        """Generate modern, minimalistic HTML for activity log.

        Design principles:
        - Clean typography with clear hierarchy
        - Purposeful use of color (ARCED brand)
        - No external dependencies (completely offline)
        - Accessible and responsive
        - Subtle interactions

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

        # Get logo as base64
        logo_data_uri = self._get_base64_logo()

        # Generate entries HTML
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
                        <span class="entry-date">📅 {entry["date"]} at {entry["time"]}</span>
                    </div>
                    <div class="entry-description">{entry["description"]}</div>
                    {f'<div class="entry-details">{entry["details"]}</div>' if entry["details"] else ''}
                    <div class="entry-meta">
                        <span>👤 {entry["author"]}</span>
                        {f'<span>📍 {entry["location"]}</span>' if entry.get("location") and entry["location"] != "Unknown" else ''}
                    </div>
                </div>
            """

        # Return complete HTML
        return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Activity Log - {data["project_name"]}</title>
    <style>
        /* CSS Reset & Base */
        *, *::before, *::after {{
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }}

        :root {{
            /* ARCED Foundation Brand Colors */
            --color-primary: #2C5F7D;
            --color-primary-light: #3d7aa0;
            --color-primary-dark: #1e4256;
            --color-secondary: #97C8EB;
            --color-accent: #E8A87C;
            --color-success: #4A9C6D;
            --color-warning: #D9A84B;
            --color-error: #C75B5B;

            /* Neutral Grays */
            --color-gray-50: #FAFAFA;
            --color-gray-100: #F5F5F5;
            --color-gray-200: #EEEEEE;
            --color-gray-300: #E0E0E0;
            --color-gray-400: #BDBDBD;
            --color-gray-500: #9E9E9E;
            --color-gray-600: #757575;
            --color-gray-700: #616161;
            --color-gray-800: #424242;
            --color-gray-900: #212121;

            /* Typography */
            --font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            --font-size-xs: 0.64rem;
            --font-size-sm: 0.80rem;
            --font-size-base: 1.00rem;
            --font-size-md: 1.25rem;
            --font-size-lg: 1.56rem;
            --font-size-xl: 1.95rem;

            /* Spacing */
            --space-4: 1.00rem;
            --space-6: 1.50rem;
            --space-8: 2.00rem;

            /* Shadows */
            --shadow-sm: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
            --shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);

            /* Border Radius */
            --radius-md: 0.375rem;
            --radius-lg: 0.5rem;
        }}

        body {{
            font-family: var(--font-family);
            font-size: var(--font-size-base);
            line-height: 1.5;
            color: var(--color-gray-900);
            background-color: var(--color-gray-50);
            -webkit-font-smoothing: antialiased;
            -moz-osx-font-smoothing: grayscale;
        }}

        /* Layout */
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: var(--color-gray-50);
        }}

        /* Header */
        .header {{
            background: white;
            border-bottom: 1px solid var(--color-gray-200);
            padding: var(--space-8) var(--space-6);
            display: flex;
            align-items: center;
            justify-content: space-between;
            flex-wrap: wrap;
            gap: var(--space-4);
        }}

        .header-branding {{
            display: flex;
            align-items: center;
            gap: var(--space-4);
        }}

        .logo {{
            height: 48px;
            width: auto;
            object-fit: contain;
        }}

        .header-titles {{
            flex: 1;
        }}

        h1 {{
            font-size: var(--font-size-xl);
            font-weight: 700;
            color: var(--color-gray-900);
            margin-bottom: 0.25rem;
            line-height: 1.2;
        }}

        .subtitle {{
            font-size: var(--font-size-base);
            color: var(--color-gray-600);
        }}

        .header-meta {{
            display: flex;
            gap: var(--space-6);
            font-size: var(--font-size-sm);
            color: var(--color-gray-500);
        }}

        .meta-item {{
            display: flex;
            flex-direction: column;
            gap: 0.25rem;
        }}

        .meta-label {{
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            color: var(--color-gray-400);
        }}

        .meta-value {{
            font-weight: 500;
            color: var(--color-gray-700);
        }}

        /* Stats Grid */
        .stats {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: var(--space-4);
            padding: var(--space-6);
            background: white;
            border-bottom: 1px solid var(--color-gray-200);
        }}

        .stat-card {{
            background: var(--color-gray-50);
            padding: var(--space-6);
            border-radius: var(--radius-lg);
            border: 1px solid var(--color-gray-200);
            text-align: center;
            transition: all 0.2s ease;
        }}

        .stat-card:hover {{
            border-color: var(--color-secondary);
            box-shadow: var(--shadow-md);
        }}

        .stat-value {{
            font-size: var(--font-size-xl);
            font-weight: 700;
            color: var(--color-primary);
            margin-bottom: 0.25rem;
        }}

        .stat-label {{
            font-size: var(--font-size-sm);
            color: var(--color-gray-600);
            font-weight: 500;
        }}

        /* Filters */
        .filters {{
            background: white;
            padding: var(--space-6);
            border-bottom: 1px solid var(--color-gray-200);
            display: flex;
            flex-wrap: wrap;
            gap: var(--space-4);
            align-items: end;
        }}

        .filter-group {{
            display: flex;
            flex-direction: column;
            gap: 0.5rem;
        }}

        .filter-group label {{
            font-size: var(--font-size-sm);
            font-weight: 600;
            color: var(--color-gray-700);
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }}

        .filter-group select,
        .filter-group input[type="date"],
        .filter-group input[type="text"] {{
            padding: 0.5rem 0.75rem;
            border: 1px solid var(--color-gray-300);
            border-radius: var(--radius-md);
            font-size: var(--font-size-base);
            background: white;
            min-width: 150px;
            transition: all 0.2s ease;
        }}

        .filter-group select:focus,
        .filter-group input:focus {{
            outline: none;
            border-color: var(--color-primary);
            box-shadow: 0 0 0 3px rgba(44, 95, 125, 0.1);
        }}

        .search-box {{
            flex: 1;
            min-width: 200px;
            padding: 0.5rem 0.75rem;
            border: 1px solid var(--color-gray-300);
            border-radius: var(--radius-md);
            font-size: var(--font-size-base);
        }}

        .results-count {{
            display: inline-flex;
            align-items: center;
            padding: 0.5rem 1rem;
            background: var(--color-primary);
            color: white;
            border-radius: var(--radius-md);
            font-size: var(--font-size-sm);
            font-weight: 600;
        }}

        .btn-clear {{
            padding: 0.5rem 1rem;
            background: var(--color-gray-600);
            color: white;
            border: none;
            border-radius: var(--radius-md);
            font-size: var(--font-size-sm);
            font-weight: 600;
            cursor: pointer;
            transition: all 0.2s ease;
        }}

        .btn-clear:hover {{
            background: var(--color-gray-700);
        }}

        /* Content Area */
        .content {{
            padding: var(--space-6);
        }}

        .section-title {{
            font-size: var(--font-size-lg);
            font-weight: 700;
            color: var(--color-gray-900);
            margin-bottom: var(--space-6);
        }}

        /* Timeline */
        .timeline {{
            position: relative;
        }}

        .entry {{
            background: white;
            border: 1px solid var(--color-gray-200);
            border-left: 4px solid var(--color-primary);
            border-radius: var(--radius-lg);
            padding: var(--space-6);
            margin-bottom: var(--space-4);
            transition: all 0.2s ease;
        }}

        .entry:hover {{
            box-shadow: var(--shadow-md);
            border-left-color: var(--color-secondary);
        }}

        .entry.hidden {{
            display: none;
        }}

        .entry-header {{
            display: flex;
            justify-content: space-between;
            align-items: start;
            margin-bottom: 0.75rem;
            gap: var(--space-4);
            flex-wrap: wrap;
        }}

        .entry-type {{
            display: inline-flex;
            align-items: center;
            padding: 0.25rem 0.75rem;
            background: var(--color-primary);
            color: white;
            border-radius: var(--radius-md);
            font-size: var(--font-size-xs);
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }}

        .entry-date {{
            font-size: var(--font-size-sm);
            color: var(--color-gray-500);
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }}

        .entry-description {{
            font-size: var(--font-size-md);
            font-weight: 600;
            color: var(--color-gray-900);
            margin-bottom: 0.75rem;
        }}

        .entry-details {{
            background: var(--color-gray-50);
            padding: 1rem;
            border-radius: var(--radius-md);
            font-family: 'SF Mono', Monaco, 'Cascadia Code', 'Roboto Mono', Consolas, 'Courier New', monospace;
            font-size: var(--font-size-sm);
            color: var(--color-gray-700);
            white-space: pre-wrap;
            word-break: break-word;
            line-height: 1.6;
        }}

        .entry-meta {{
            display: flex;
            gap: var(--space-6);
            margin-top: 0.75rem;
            padding-top: 0.75rem;
            border-top: 1px solid var(--color-gray-200);
            font-size: var(--font-size-sm);
            color: var(--color-gray-600);
        }}

        .entry-meta span {{
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }}

        /* Empty State */
        .no-results {{
            text-align: center;
            padding: 3rem var(--space-6);
            color: var(--color-gray-500);
            display: none;
        }}

        .no-results-icon {{
            font-size: 4rem;
            margin-bottom: var(--space-4);
            opacity: 0.5;
        }}

        .no-results-text {{
            font-size: var(--font-size-lg);
            color: var(--color-gray-700);
        }}

        /* Footer */
        .footer {{
            background: white;
            border-top: 1px solid var(--color-gray-200);
            padding: var(--space-8) var(--space-6);
            text-align: center;
        }}

        .footer-content {{
            display: flex;
            flex-direction: column;
            gap: 0.75rem;
            align-items: center;
        }}

        .footer-links {{
            display: flex;
            gap: var(--space-6);
            flex-wrap: wrap;
            justify-content: center;
        }}

        .footer-link {{
            color: var(--color-primary);
            text-decoration: none;
            font-weight: 500;
            font-size: var(--font-size-sm);
            transition: color 0.2s ease;
        }}

        .footer-link:hover {{
            color: var(--color-primary-light);
            text-decoration: underline;
        }}

        .footer-notice {{
            font-size: var(--font-size-xs);
            color: var(--color-gray-500);
            max-width: 600px;
        }}

        /* Responsive */
        @media (max-width: 768px) {{
            .header {{
                flex-direction: column;
                align-items: flex-start;
            }}

            .header-branding {{
                width: 100%;
            }}

            .header-meta {{
                width: 100%;
                flex-wrap: wrap;
            }}

            h1 {{
                font-size: var(--font-size-lg);
            }}

            .stats {{
                grid-template-columns: 1fr;
            }}

            .filters {{
                flex-direction: column;
                align-items: stretch;
            }}

            .filter-group {{
                width: 100%;
            }}

            .filter-group select,
            .filter-group input,
            .search-box {{
                width: 100%;
            }}

            .entry-header {{
                flex-direction: column;
            }}
        }}

        /* Print Styles */
        @media print {{
            .filters {{
                display: none;
            }}

            .entry {{
                break-inside: avoid;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <!-- Header -->
        <div class="header">
            <div class="header-branding">
                <img src="{logo_data_uri}" alt="ARCED Foundation Logo" class="logo">
                <div class="header-titles">
                    <h1>Activity Log</h1>
                    <div class="subtitle">{data["project_name"]}</div>
                </div>
            </div>
            <div class="header-meta">
                <div class="meta-item">
                    <span class="meta-label">Total Actions</span>
                    <span class="meta-value">{data["total_actions"]}</span>
                </div>
                <div class="meta-item">
                    <span class="meta-label">Created</span>
                    <span class="meta-value">{datetime.fromisoformat(data["created"]).strftime("%b %d, %Y")}</span>
                </div>
                <div class="meta-item">
                    <span class="meta-label">Last Updated</span>
                    <span class="meta-value">{datetime.fromisoformat(data["last_updated"]).strftime("%b %d, %Y %H:%M")}</span>
                </div>
            </div>
        </div>

        <!-- Stats -->
        <div class="stats">
            <div class="stat-card">
                <div class="stat-value">{data["total_actions"]}</div>
                <div class="stat-label">Total Actions</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{len(action_types)}</div>
                <div class="stat-label">Action Types</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{len(authors)}</div>
                <div class="stat-label">Collaborators</div>
            </div>
        </div>

        <!-- Filters -->
        <div class="filters">
            <div class="filter-group">
                <label for="filter-action-type">Action Type</label>
                <select id="filter-action-type">
                    <option value="">All Types</option>
                    {"".join(f'<option value="{at}">{at}</option>' for at in action_types)}
                </select>
            </div>

            <div class="filter-group">
                <label for="filter-author">Author</label>
                <select id="filter-author">
                    <option value="">All Authors</option>
                    {"".join(f'<option value="{author}">{author}</option>' for author in authors)}
                </select>
            </div>

            <div class="filter-group">
                <label for="filter-date-from">From Date</label>
                <input type="date" id="filter-date-from" min="{min(dates) if dates else ''}">
            </div>

            <div class="filter-group">
                <label for="filter-date-to">To Date</label>
                <input type="date" id="filter-date-to" max="{max(dates) if dates else ''}">
            </div>

            <input type="text" class="search-box" id="filter-search" placeholder="Search activities...">
            <div class="results-count" id="results-count">{len(data["entries"])} shown</div>
            <button class="btn-clear" id="btn-clear">Clear</button>
        </div>

        <!-- Content -->
        <div class="content">
            <h2 class="section-title">Activity Timeline</h2>
            <div class="timeline" id="timeline">
                {entries_html}
            </div>

            <div class="no-results" id="no-results">
                <div class="no-results-icon">🔍</div>
                <div class="no-results-text">No activities match your filters</div>
            </div>
        </div>

        <!-- Footer -->
        <div class="footer">
            <div class="footer-content">
                <div class="footer-links">
                    <a href="https://github.com/ARCED-International/xlsform-ai" target="_blank" class="footer-link">XLSForm AI on GitHub</a>
                    <span style="color: var(--color-gray-300)">•</span>
                    <a href="https://arced-international.com" target="_blank" class="footer-link">ARCED International</a>
                </div>
                <div class="footer-notice">
                    This log is auto-generated by XLSForm AI • Last updated: {datetime.fromisoformat(data["last_updated"]).strftime("%B %d, %Y at %I:%M %p")}
                </div>
            </div>
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

        // Event listeners
        document.getElementById('filter-action-type').addEventListener('change', applyFilters);
        document.getElementById('filter-author').addEventListener('change', applyFilters);
        document.getElementById('filter-date-from').addEventListener('change', applyFilters);
        document.getElementById('filter-date-to').addEventListener('change', applyFilters);
        document.getElementById('filter-search').addEventListener('input', applyFilters);

        document.getElementById('btn-clear').addEventListener('click', () => {{
            document.getElementById('filter-action-type').value = '';
            document.getElementById('filter-author').value = '';
            document.getElementById('filter-date-from').value = '';
            document.getElementById('filter-date-to').value = '';
            document.getElementById('filter-search').value = '';
            applyFilters();
        }});
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
