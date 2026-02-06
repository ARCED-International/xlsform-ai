"""Cleanup script to remove XLSForm AI files, keeping only outputs."""

import sys
from pathlib import Path

# Try to import rich for beautiful formatting
try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.text import Text
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False

if RICH_AVAILABLE:
    console = Console()


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
        "xlsform-ai.json",   # Project configuration
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
                if f.name not in kept:
                    kept.append(str(f.name))
        else:
            f = project_dir / pattern
            if f.exists() and pattern not in kept:
                kept.append(pattern)

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


def print_cleanup_results(result):
    """Print cleanup results with beautiful formatting.

    Args:
        result: Dict from cleanup_project()
    """
    if RICH_AVAILABLE:
        print_cleanup_rich(result)
    else:
        print_cleanup_simple(result)


def print_cleanup_rich(result):
    """Print results using rich formatting."""
    from rich.tree import Tree
    from rich import box

    # Create main tree
    tree = Tree("🧹 Cleanup Summary", style="bold cyan")

    # Removed files branch
    if result["removed"]:
        removed_branch = tree.add("📦 Removed Files/Directories", style="green")
        for item in result["removed"]:
            item_name = Path(item).name
            removed_branch.add(f"[OK] {item_name}", style="green")
    else:
        tree.add("📦 No files to remove", style="yellow")

    # Kept files branch
    if result["kept"]:
        kept_branch = tree.add("💾 Kept Files (Your Work)", style="cyan")

        # Group files by type
        excel_files = [f for f in result["kept"] if f.endswith('.xlsx')]
        log_files = [f for f in result["kept"] if f.endswith('.html')]

        if excel_files:
            excel_branch = kept_branch.add("📊 Excel Files", style="blue")
            for f in excel_files:
                excel_branch.add(f"  {f}", style="blue")

        if log_files:
            log_branch = kept_branch.add("📋 Activity Logs", style="blue")
            for f in log_files:
                log_branch.add(f"  {f}", style="blue")

    # Errors branch
    if result["errors"]:
        error_branch = tree.add("[WARNING]  Errors", style="red")
        for error in result["errors"]:
            error_branch.add(f"✗ {error}", style="red")

    # Print tree
    console.print(tree)

    # Print informational panel
    if result["dry_run"]:
        console.print("\n[yellow][WARNING]  DRY RUN MODE[/yellow]")
        console.print("[yellow]No files were actually removed.[/yellow]")
        console.print("[yellow]Run without --dry-run to perform actual cleanup.[/yellow]\n")
    else:
        if result["removed"] and not result["errors"]:
            console.print("\n[green][OK] Cleanup completed successfully![/green]")

            # Next steps panel
            console.print(Panel(
                f"[bold cyan]🔄 Reinstall XLSForm AI:[/bold cyan]\n"
                f"  [cyan]xlsform-ai init --here[/cyan] [dim](to reuse same directory)[/dim]\n"
                f"  [cyan]xlsform-ai init <new-project>[/cyan] [dim](to create new project)[/dim]\n\n"
                f"[bold cyan][INFO] Note:[/bold cyan]\n"
                f"  [dim]Your activity logs were preserved and will be reused on reinstall.[/dim]\n"
                f"  [dim]Your XLSForm files (*.xlsx) are safe and ready to use.[/dim]",
                title="[bold green]Next Steps[/bold green]",
                border_style="green",
                padding=(1, 2),
            ))
        elif result["errors"]:
            console.print("\n[red]✗ Cleanup completed with errors[/red]")
            console.print("[yellow]Some files could not be removed. Check the errors above.[/yellow]\n")
        else:
            console.print("\n[yellow][WARNING]  No XLSForm AI files found[/yellow]")
            console.print("[yellow]This directory doesn't appear to be an XLSForm AI project.[/yellow]\n")


def print_cleanup_simple(result):
    """Print results with simple formatting (fallback)."""
    mode = "DRY RUN - " if result["dry_run"] else ""

    print(f"\n{mode}Cleanup Summary")
    print("=" * 50)

    if result["removed"]:
        print("\n[OK] Removed Files/Directories:")
        for item in result["removed"]:
            print(f"  [OK] {item}")
    else:
        print("\n[!] No files to remove")

    if result["kept"]:
        print("\n[OK] Kept Files (Your Work):")
        for item in result["kept"]:
            print(f"  • {item}")

    if result["errors"]:
        print("\n[X] Errors:")
        for error in result["errors"]:
            print(f"  ✗ {error}")

    print("\n" + "=" * 50)

    if result["dry_run"]:
        print("\n[!] DRY RUN MODE - No files were actually removed")
        print("Run without --dry-run to perform actual cleanup.")
    elif result["removed"] and not result["errors"]:
        print("\n[OK] Cleanup completed successfully!")
        print("\nTo reinstall XLSForm AI:")
        print("  xlsform-ai init --here")


if __name__ == "__main__":
    dry_run = "--dry-run" in sys.argv or "-n" in sys.argv

    if not RICH_AVAILABLE:
        print("Note: Install 'rich' for beautiful formatting")
        print("  pip install rich\n")

    result = cleanup_project(dry_run=dry_run)

    # Use beautiful formatting
    print_cleanup_results(result)
