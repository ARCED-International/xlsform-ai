"""Configuration management for XLSForm AI projects."""

import sys

import json
from datetime import datetime
from pathlib import Path
from typing import Optional
# CRITICAL: Add scripts directory to Python path for sibling imports
# This allows the script to find sibling modules whether run from project root or scripts dir
_scripts_dir = Path(__file__).parent.resolve()
if str(_scripts_dir) not in sys.path:
    sys.path.insert(0, str(_scripts_dir))



DEFAULT_CONFIG = {
    "version": "1.0",
    "project_name": "",
    "xlsform_file": "survey.xlsx",
    "activity_log_file": "activity_log.html",
    "created": None,
    "last_modified": None,
    "author": None,  # Auto-detected on first use
    "author_updated": None,  # Timestamp when author was set
    "collaborators": [],  # List of collaborator names
    "active_collaborator": None,  # Currently active collaborator
    "settings": {
        "auto_validate": True,
        "log_activity": True,
        "backup_before_changes": False
    }
}


class ProjectConfig:
    """Manage project-specific XLSForm AI configuration."""

    def __init__(self, project_dir: Optional[Path] = None):
        """Initialize configuration manager.

        Args:
            project_dir: Project directory. Defaults to current working directory.
        """
        self.project_dir = Path(project_dir) if project_dir else Path.cwd()
        self.config_file = self.project_dir / "xlsform-ai.json"
        self._config = None

    def load(self) -> dict:
        """Load configuration from file with migration support.

        Migrates old configs to include new author-related fields.

        Returns:
            Configuration dictionary
        """
        if self._config is not None:
            return self._config

        if not self.config_file.exists():
            # Create default config
            self._config = DEFAULT_CONFIG.copy()
            self._config["created"] = datetime.now().isoformat()
            self.save()
        else:
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    self._config = json.load(f)

                # Migrate old configs - add new fields if missing
                migrated = False
                if "author" not in self._config:
                    self._config["author"] = None
                    migrated = True
                if "author_updated" not in self._config:
                    self._config["author_updated"] = None
                    migrated = True
                if "collaborators" not in self._config:
                    self._config["collaborators"] = []
                    migrated = True
                if "active_collaborator" not in self._config:
                    self._config["active_collaborator"] = None
                    migrated = True
                if "activity_log_file" not in self._config:
                    self._config["activity_log_file"] = "activity_log.html"
                    migrated = True

                if migrated:
                    self.save()

            except (json.JSONDecodeError, IOError):
                # Fallback to defaults if config is corrupt
                self._config = DEFAULT_CONFIG.copy()

        return self._config

    def save(self):
        """Save configuration to file."""
        self._config["last_modified"] = datetime.now().isoformat()

        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(self._config, f, indent=2)

    def get_xlsform_file(self) -> str:
        """Get the configured XLSForm file name.

        Returns:
            File name (e.g., "survey.xlsx")
        """
        config = self.load()
        return config.get("xlsform_file", "survey.xlsx")

    def set_xlsform_file(self, filename: str):
        """Set the XLSForm file name.

        Args:
            filename: New file name to use
        """
        config = self.load()
        config["xlsform_file"] = filename
        self.save()

    def get_full_xlsform_path(self) -> Path:
        """Get full path to XLSForm file.

        Returns:
            Path object pointing to XLSForm file
        """
        return self.project_dir / self.get_xlsform_file()

    def get_project_name(self) -> str:
        """Get the project name.

        Returns:
            Project name string
        """
        config = self.load()
        return config.get("project_name", self.project_dir.name)

    def set_project_name(self, name: str):
        """Set the project name.

        Args:
            name: New project name
        """
        config = self.load()
        config["project_name"] = name
        self.save()

    def get_author(self) -> Optional[str]:
        """Get the configured author name.

        Returns:
            Author name or None if not configured
        """
        config = self.load()
        return config.get("author")

    def set_author(self, author: str):
        """Set the author name in configuration.

        Args:
            author: Author name to set
        """
        config = self.load()
        config["author"] = author
        config["author_updated"] = datetime.now().isoformat()
        self.save()

    def get_effective_author(self) -> str:
        """Get effective author name with intelligent fallback.

        Priority:
        1. Configured author in xlsform-ai.json
        2. Detected system username (with generic filtering)
        3. Fallback to "User"

        Returns:
            Author name (with intelligent fallback)
        """
        # Try configured author first
        configured = self.get_author()
        if configured:
            return configured

        # Import and use author utilities
        try:
            from author_utils import get_detected_author
            return get_detected_author()
        except ImportError:
            return "User"

    def add_collaborator(self, name: str) -> None:
        """Add a new collaborator to the project.

        Args:
            name: Collaborator name
        """
        config = self.load()
        if "collaborators" not in config:
            config["collaborators"] = []
        if name not in config["collaborators"]:
            config["collaborators"].append(name)
        self.save()

    def get_collaborators(self) -> list:
        """Get list of all collaborators.

        Returns:
            List of collaborator names
        """
        config = self.load()
        return config.get("collaborators", [])

    def set_active_collaborator(self, name: str) -> None:
        """Set the currently active collaborator.

        Args:
            name: Collaborator name
        """
        config = self.load()
        config["active_collaborator"] = name
        self.save()

    def get_active_collaborator(self) -> Optional[str]:
        """Get the currently active collaborator.

        Returns:
            Active collaborator name or None
        """
        config = self.load()
        return config.get("active_collaborator")

    def is_activity_logging_enabled(self) -> bool:
        """Check if activity logging is enabled in configuration.

        Returns:
            True if logging is enabled, False otherwise.
            Defaults to True for backward compatibility.
        """
        config = self.load()
        settings = config.get("settings", {})
        return settings.get("log_activity", True)

    def get_activity_log_file(self) -> str:
        """Get the configured activity log file name.

        Returns:
            Activity log file name (e.g., "activity_log.html")
        """
        config = self.load()
        return config.get("activity_log_file", "activity_log.html")

    def set_activity_log_file(self, filename: str):
        """Set the activity log file name.

        Args:
            filename: New activity log file name to use
        """
        config = self.load()
        config["activity_log_file"] = filename
        self.save()


if __name__ == "__main__":
    # Test configuration management
    import sys

    config = ProjectConfig()

    if len(sys.argv) > 1 and sys.argv[1] == "get":
        # Get current configuration
        print(f"Config file: {config.config_file}")
        print(f"Project name: {config.get_project_name()}")
        print(f"XLSForm file: {config.get_xlsform_file()}")
        print(f"Full path: {config.get_full_xlsform_path()}")
    elif len(sys.argv) > 2 and sys.argv[1] == "set-file":
        # Set XLSForm file name
        config.set_xlsform_file(sys.argv[2])
        print(f"XLSForm file set to: {config.get_xlsform_file()}")
    else:
        # Display all configuration
        data = config.load()
        print(json.dumps(data, indent=2))
