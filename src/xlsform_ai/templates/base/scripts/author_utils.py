"""Author detection and management utilities for XLSForm AI activity logging.

This module provides cross-platform username detection with intelligent filtering
for generic usernames, and integration with project configuration.
"""

import getpass
import os
import platform
from pathlib import Path
from typing import Optional


# Generic usernames to filter out (case-insensitive)
GENERIC_USERNAMES = {
    'user', 'administrator', 'admin', 'root', 'guest',
    'asus', 'dell', 'hp', 'user1', 'user2', 'test',
    'owner', 'desktop', 'laptop', 'pc', 'macuser',
    'ubuntu', 'debian', 'fedora'
}


def detect_system_username() -> str:
    """Detect the current system username across platforms.

    Tries multiple methods in order of reliability:
    1. Environment variables (USERNAME on Windows, USER on Unix)
    2. getpass module
    3. Platform-specific fallbacks

    Returns:
        Username string, or "Unknown User" if detection fails
    """
    # Try environment variables first (most reliable)
    username = os.getenv('USERNAME') or os.getenv('USER') or os.getenv('LOGNAME')

    # Fallback to getpass
    if not username:
        try:
            username = getpass.getuser()
        except Exception:
            pass

    # Final fallback
    if not username:
        username = "Unknown User"

    return username


def is_generic_username(username: str) -> bool:
    """Check if username is too generic to be meaningful.

    Generic usernames like "user", "admin", "asus" don't provide
    useful identification and should trigger fallback behavior.

    Args:
        username: Username to check

    Returns:
        True if username is generic/common
    """
    return username.lower().strip() in GENERIC_USERNAMES


def get_detected_author() -> str:
    """Get detected author name with intelligent fallback handling.

    If the detected username is generic (e.g., "user", "admin"), this
    function generates a more descriptive fallback using the hostname.

    Returns:
        Author name string with proper capitalization
    """
    detected = detect_system_username()

    if is_generic_username(detected):
        # Generate a more descriptive fallback
        hostname = platform.node().split('.')[0]
        # Capitalize hostname
        hostname = hostname.capitalize() if hostname else 'Local'
        return f"User ({hostname})"

    # Capitalize first letter of each word for proper display
    # Handle both space-separated and dot-separated usernames
    return ' '.join(word.capitalize() for word in detected.split('.'))


def load_author_from_config(project_dir: Optional[Path] = None) -> Optional[str]:
    """Load author name from project configuration file.

    Args:
        project_dir: Project directory (defaults to current working directory)

    Returns:
        Author name if configured, None otherwise
    """
    if project_dir is None:
        project_dir = Path.cwd()

    config_file = project_dir / "xlsform-ai.json"

    if not config_file.exists():
        return None

    try:
        import json
        with open(config_file, 'r', encoding='utf-8') as f:
            config = json.load(f)
            return config.get('author')
    except Exception:
        return None


def save_author_to_config(author: str, project_dir: Optional[Path] = None) -> bool:
    """Save author name to project configuration file.

    Creates the config file if it doesn't exist, or updates the existing one.

    Args:
        author: Author name to save
        project_dir: Project directory (defaults to current working directory)

    Returns:
        True if successful, False otherwise
    """
    if project_dir is None:
        project_dir = Path.cwd()

    config_file = project_dir / "xlsform-ai.json"

    try:
        import json
        from datetime import datetime

        # Load existing config or create new
        if config_file.exists():
            with open(config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
        else:
            config = {}

        # Set author and timestamp
        config['author'] = author
        config['author_updated'] = datetime.now().isoformat()

        # Save back to file
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2)

        return True
    except Exception:
        return False


def get_effective_author(project_dir: Optional[Path] = None) -> str:
    """Get the effective author name for activity logging.

    Priority order:
    1. Configured author in xlsform-ai.json
    2. Detected system username (with generic filtering)
    3. Fallback to "User"

    Args:
        project_dir: Project directory

    Returns:
        Author name to use for logging
    """
    # Try config first
    config_author = load_author_from_config(project_dir)
    if config_author:
        return config_author

    # Fall back to detection
    return get_detected_author()


if __name__ == "__main__":
    # Test the author detection
    print("=== Author Detection Test ===")
    print(f"Detected username: {detect_system_username()}")
    print(f"Is generic: {is_generic_username(detect_system_username())}")
    print(f"Effective author: {get_detected_author()}")
    print(f"Config author: {load_author_from_config()}")
    print(f"Final author: {get_effective_author()}")
