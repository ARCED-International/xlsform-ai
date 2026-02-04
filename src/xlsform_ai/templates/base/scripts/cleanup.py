"""Cleanup script to remove XLSForm AI files, keeping only outputs."""

import sys
from pathlib import Path


def cleanup_project(project_dir=None, dry_run=False):
    """Remove XLSForm AI configuration files, keeping output files.

    Args:
        project_dir: Project directory (default: current directory)
        dry_run: If True, show what would be deleted without deleting

    Returns:
        dict with cleanup results
    """
    project_dir = Path(project_dir) if project_dir else Path.cwd()

    # Files and directories to remove
    to_remove = [
        ".claude",           # Claude Code configuration
        "scripts",           # Helper scripts
        "package.json",      # npm scripts
    ]

    # Files to keep (output files)
    to_keep = [
        "survey.xlsx",      # Main output file
        "*.xlsx",           # Any Excel files
        "*.html",           # Activity log files
    ]

    removed = []
    kept = []
    errors = []

    for item in to_remove:
        item_path = project_dir / item

        if item_path.exists():
            if dry_run:
                removed.append(str(item_path))
            else:
                try:
                    if item_path.is_dir():
                        import shutil
                        shutil.rmtree(item_path)
                    else:
                        item_path.unlink()
                    removed.append(str(item_path))
                except Exception as e:
                    errors.append(f"{item}: {e}")

    # List output files that are kept
    for pattern in to_keep:
        if "*" in pattern:
            matching = list(project_dir.glob(pattern))
            for f in matching:
                kept.append(str(f.name))
        else:
            f = project_dir / pattern
            if f.exists():
                kept.append(str(f.name))

    # Check for log files specifically
    log_files = []
    for f in project_dir.glob("*.html"):
        try:
            with open(f, 'r', encoding='utf-8') as file:
                content = file.read(1000)
                if "XLSFORM_AI_ACTIVITY_LOG" in content:
                    log_files.append(f.name)
                    if f.name not in kept:
                        kept.append(f.name)
        except:
            pass

    return {
        "removed": removed,
        "kept": kept,
        "log_files": log_files,
        "errors": errors,
        "dry_run": dry_run
    }


if __name__ == "__main__":
    dry_run = "--dry-run" in sys.argv or "-n" in sys.argv

    if dry_run:
        print("DRY RUN - Showing what would be removed:\n")

    result = cleanup_project(dry_run=dry_run)

    if dry_run:
        print("Would remove:")
        for item in result["removed"]:
            print(f"  - {item}")

        if result["errors"]:
            print("\nWould have errors:")
            for error in result["errors"]:
                print(f"  - {error}")
    else:
        if result["removed"]:
            print("Removed:")
            for item in result["removed"]:
                print(f"  - {item}")

        if result["errors"]:
            print("\nErrors:")
            for error in result["errors"]:
                print(f"  - {error}")

    print("\nKept (output files):")
    for item in result["kept"]:
        print(f"  - {item}")

    if result["log_files"]:
        print("\nLog files (preserved):")
        for log in result["log_files"]:
            print(f"  - {log}")
        print("\nNote: Your activity log will be reused if you reinstall XLSForm AI.")

    if not dry_run and not result["errors"] and result["removed"]:
        print("\nCleanup complete!")
        print("To reinstall XLSForm AI in this directory, run:")
        print("  xlsform-ai init --here")
