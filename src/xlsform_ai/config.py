"""Configuration management for XLSForm AI."""

import os
from pathlib import Path
from typing import Optional


class Config:
    """Configuration settings for XLSForm AI."""

    def __init__(self):
        """Initialize configuration with defaults."""
        self.home = Path.home()
        self.config_dir = self.home / ".xlsform-ai"
        self.templates_dir = self.config_dir / "templates"

    def ensure_config_dir(self) -> Path:
        """Ensure configuration directory exists.

        Returns:
            Path to configuration directory
        """
        self.config_dir.mkdir(parents=True, exist_ok=True)
        return self.config_dir

    def get_template_version(self) -> Optional[str]:
        """Get the currently installed template version.

        Returns:
            Version string or None if not found
        """
        version_file = self.config_dir / "template_version.txt"
        if version_file.exists():
            return version_file.read_text().strip()
        return None

    def set_template_version(self, version: str) -> None:
        """Set the installed template version.

        Args:
            version: Version string to store
        """
        self.ensure_config_dir()
        version_file = self.config_dir / "template_version.txt"
        version_file.write_text(version)

    def get_pyodk_config(self) -> Optional[Path]:
        """Get path to pyodk configuration file.

        Returns:
            Path to .pyodk_config.toml or None if not found
        """
        config_path = self.home / ".pyodk_config.toml"
        if config_path.exists():
            return config_path
        return None
