"""Beautiful display helpers for XLSForm AI CLI."""

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from . import __version__

console = Console(force_terminal=True, legacy_windows=False)


def _get_banner():
    """Get the XLSForm AI banner - Speckit-inspired professional design."""
    # XLSFORM ASCII art
    xlsform_art = """[bold cyan]
 █████ █████ █████        █████████  ███████████                                         █████████   █████
░░███ ░░███ ░░███        ███░░░░░███░░███░░░░░░█                                        ███░░░░░███ ░░███
 ░░███ ███   ░███       ░███    ░░░  ░███   █ ░   ██████  ████████  █████████████      ░███    ░███  ░███
  ░░█████    ░███       ░░█████████  ░███████    ███░░███░░███░░███░░███░░███░░███     ░███████████  ░███
   ███░███   ░███        ░░░░░░░░███ ░███░░░█   ░███ ░███ ░███ ░░░  ░███ ░███ ░███     ░███░░░░░███  ░███
  ███ ░░███  ░███      █ ███    ░███ ░███  ░    ░███ ░███ ░███      ░███ ░███ ░███     ░███    ░███  ░███
 █████ █████ ███████████░░█████████  █████      ░░██████  █████     █████░███ █████    █████   █████ █████
░░░░░ ░░░░░ ░░░░░░░░░░░  ░░░░░░░░░  ░░░░░        ░░░░░░  ░░░░░     ░░░░░ ░░░ ░░░░░    ░░░░░   ░░░░░ ░░░░░[/bold cyan]"""

    return f"""{xlsform_art}

[dim]                    AI-Powered Survey & Form Creation Toolkit[/dim]
[dim]                            by ARCED International[/dim]
[dim]                                Version {__version__}[/dim]

"""


# Main banner
BANNER = _get_banner()


def _get_header(title: str, color: str = "cyan") -> str:
    """Generate a formatted header.

    Args:
        title: Header title text
        color: Rich color name

    Returns:
        Formatted header string
    """
    border = "+" + "=" * 78 + "+"
    return f"[bold {color}]{border}\n|                                                                      |\n|                          [{color}]{title}[/{color}]                            |\n|                                                                      |\n{border}[/{color}]"


# Clean headers using simple ASCII borders
def get_init_success_header():
    return _get_header("[OK] PROJECT INITIALIZED", "green")

def get_add_questions_header():
    return _get_header("ADD QUESTIONS", "yellow")

def get_validate_header():
    return _get_header("VALIDATE FORM", "magenta")

def get_import_header():
    return _get_header("IMPORT QUESTIONS", "blue")

def get_cleanup_header():
    return _get_header("CLEANUP PROJECT", "red")

def get_info_header():
    return _get_header("PROJECT INFORMATION", "white")

def get_error_header():
    return _get_header("ERROR OCCURRED", "red")

def get_warning_header():
    return _get_header("WARNING NOTICE", "yellow")


def print_main_banner():
    """Print the main XLSForm AI banner."""
    import sys
    import io

    # Force UTF-8 encoding for Windows console compatibility
    if hasattr(sys.stdout, 'buffer'):
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

    console.print(BANNER)


def print_init_success(location: str, relative_path: str = "."):
    """Print beautiful initialization success message.

    Args:
        location: Full path to the project
        relative_path: Relative path from current directory
    """
    console.print(get_init_success_header())

    console.print(Panel.fit(
        f"[bold green][OK] Project initialized successfully![/bold green]\n\n"
        f"[bold]Location:[/bold] [cyan]{location}[/cyan]\n\n"
        f"[bold]Next steps:[/bold]\n"
        f"  [cyan]1.[/cyan] cd {relative_path}\n"
        f"  [cyan]2.[/cyan] Open [yellow]survey.xlsx[/yellow] in Excel\n"
        f"  [cyan]3.[/cyan] Use Claude Code with [yellow]/xlsform-add[/yellow] commands\n"
        f"  [cyan]4.[/cyan] Or use [yellow]/xlsform-import[/yellow] to import from PDF/Word/Excel\n\n"
        f"[dim]Your activity log will be preserved across re-installations.[/dim]",
        title="[green][OK] SUCCESS[/green]",
        border_style="green",
        padding=(1, 2),
    ))


def print_questions_added(count: int, questions: list):
    """Print beautiful questions added message.

    Args:
        count: Number of questions added
        questions: List of added question info
    """
    console.print(get_add_questions_header())

    # Create a table for the questions
    table = Table(show_header=True, header_style="bold cyan", border_style="cyan")
    table.add_column("Row", style="dim", width=6)
    table.add_column("Type", style="yellow", width=15)
    table.add_column("Name", style="green", width=25)
    table.add_column("Label", style="white")

    for q in questions:
        table.add_row(
            str(q.get("row", "")),
            q.get("type", ""),
            q.get("name", ""),
            q.get("label", "")[:40] + ("..." if len(q.get("label", "")) > 40 else "")
        )

    console.print(table)
    console.print(f"\n[bold green][OK] Added {count} question(s)[/bold green]")


def print_validation_results(results: dict):
    """Print beautiful validation results.

    Args:
        results: Validation results dictionary
    """
    console.print(get_validate_header())

    if results.get("valid"):
        console.print(Panel(
            f"[bold green][OK] Form is valid![/bold green]\n\n"
            f"[dim]No critical errors or warnings found.[/dim]",
            title="[green][OK] VALID[/green]",
            border_style="green",
        ))
    else:
        # Show errors
        if results.get("errors"):
            console.print("\n[bold red]Critical Errors:[/bold red]")
            for error in results.get("errors", []):
                console.print(f"  [red][X][/red] {error}")

        if results.get("warnings"):
            console.print("\n[bold yellow]Warnings:[/bold yellow]")
            for warning in results.get("warnings", []):
                console.print(f"  [yellow][!][/yellow] {warning}")


def print_import_results(results: dict):
    """Print beautiful import results.

    Args:
        results: Import results dictionary
    """
    console.print(get_import_header())

    if results.get("success"):
        count = results.get("count", 0)
        console.print(Panel(
            f"[bold green][OK] Imported {count} question(s)[/bold green]\n\n"
            f"[dim]Questions have been added to your XLSForm.[/dim]",
            title="[green][OK] IMPORTED[/green]",
            border_style="green",
        ))

        # Show imported questions summary
        if results.get("questions"):
            console.print("\n[bold]Imported Questions:[/bold]")
            table = Table(show_header=True, header_style="bold cyan", border_style="cyan")
            table.add_column("Type", style="yellow", width=15)
            table.add_column("Name", style="green", width=25)
            table.add_column("Label", style="white")

            for q in results["questions"][:10]:  # Show first 10
                table.add_row(
                    q.get("type", ""),
                    q.get("name", ""),
                    q.get("label", "")[:40] + ("..." if len(q.get("label", "")) > 40 else "")
                )

            console.print(table)

            if len(results["questions"]) > 10:
                console.print(f"[dim]... and {len(results['questions']) - 10} more[/dim]")
    else:
        console.print(Panel(
            f"[bold red][X] Import failed[/bold red]\n\n"
            f"[dim]{results.get('error', 'Unknown error')}[/dim]",
            title="[red][X] ERROR[/red]",
            border_style="red",
        ))


def print_cleanup_results(results: dict, dry_run: bool = False):
    """Print beautiful cleanup results.

    Args:
        results: Cleanup results dictionary
        dry_run: Whether this was a dry run
    """
    console.print(get_cleanup_header())

    if dry_run:
        console.print("[yellow]Dry run mode - showing what would be removed:[/yellow]\n")

    # Show what would be/was removed
    if results.get("removed"):
        console.print(f"[bold]{'Would remove:' if dry_run else 'Removed:'}[/bold]")
        for item in results.get("removed", []):
            console.print(f"  [red][-][/red] {item}")

    # Show errors
    if results.get("errors"):
        console.print(f"\n[bold red]{'Would have errors:' if dry_run else 'Errors:'}[/bold]")
        for error in results.get("errors", []):
            console.print(f"  [red][X][/red] {error}")

    # Show preserved files
    console.print(f"\n[bold green]Kept (output files):[/bold green]")
    for item in results.get("kept", []):
        console.print(f"  [green][OK][/green] {item}")

    # Show preserved logs
    if results.get("log_files"):
        console.print(f"\n[bold cyan]Activity Log (preserved):[/bold cyan]")
        for log in results.get("log_files", []):
            console.print(f"  [cyan]->[/cyan] {log}")

    if not dry_run and not results.get("errors"):
        console.print(Panel(
            "[bold green][OK] Cleanup complete![/bold green]\n\n"
            "Your output files (survey.xlsx, activity logs) are safe.\n\n"
            "[bold]To reinstall XLSForm AI:[/bold]\n"
            "  [cyan]xlsform-ai init --here[/cyan]",
            border_style="green",
        ))


def print_info_panel(info: dict):
    """Print beautiful information panel.

    Args:
        info: Information dictionary
    """
    console.print(get_info_header())

    # Version
    console.print(f"\n[bold]Version[/bold]")
    console.print(f"  XLSForm AI: [cyan]{__version__}[/cyan]")

    # Installation status
    console.print(f"\n[bold]Installation Status[/bold]")
    if info.get("installed"):
        console.print("  [green][OK][/green] XLSForm AI CLI is properly installed")
    else:
        console.print("  [red][X][/red] Installation issues detected")

    # Supported agents
    console.print(f"\n[bold]Supported Agents[/bold]")
    for agent in info.get("agents", []):
        console.print(f"  [cyan]->[/cyan] {agent}")

    # Configuration
    console.print(f"\n[bold]Configuration[/bold]")
    console.print(f"  Config directory: [cyan]{info.get('config_dir', 'N/A')}[/cyan]")

    # Links
    console.print(f"\n[bold]Documentation & Resources[/bold]")
    console.print("  GitHub: [cyan]https://github.com/ARCED-International/xlsform-ai[/cyan]")
    console.print("  XLSForm: [cyan]https://xlsform.org[/cyan]")


def print_error(message: str, details: str = ""):
    """Print beautiful error message.

    Args:
        message: Error message
        details: Additional error details
    """
    console.print(get_error_header())

    content = f"[bold red][X] {message}[/bold red]"
    if details:
        content += f"\n\n[dim]{details}[/dim]"

    console.print(Panel(
        content,
        title="[red][X] ERROR[/red]",
        border_style="red",
    ))


def print_warning(message: str):
    """Print beautiful warning message.

    Args:
        message: Warning message
    """
    console.print(get_warning_header())
    console.print(f"[bold yellow][!] {message}[/bold yellow]")
