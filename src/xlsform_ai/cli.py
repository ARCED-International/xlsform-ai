"""XLSForm AI CLI - Main entry point."""

import sys
from pathlib import Path

import questionary
import requests
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table

from . import __version__
from .agents import get_supported_agents, validate_agent
from .templates import TemplateManager

console = Console()


def print_banner():
    """Print welcome banner."""
    banner = """
[bold cyan]╔══════════════════════════════════════════╗
║     [white]XLSForm AI [dim]v{version}[/dim]            [bold cyan]║
║     [white]AI-Powered XLSForm Creation        [bold cyan]║
╚══════════════════════════════════════════╝
""".format(version=__version__)
    console.print(banner)


def print_success(message: str):
    """Print success message."""
    console.print(f"[green]✓[/green] {message}")


def print_error(message: str):
    """Print error message."""
    console.print(f"[red]✗[/red] {message}")


def print_warning(message: str):
    """Print warning message."""
    console.print(f"[yellow]⚠[/yellow] {message}")


def check_cli_installation() -> bool:
    """Check if CLI is properly installed.

    Returns:
        True if all components are available
    """
    from .templates import TemplateManager

    try:
        tm = TemplateManager()
        template_path = tm.get_template_path()

        if not template_path.exists():
            print_warning("Template files not found")
            return False

        # Check for key template components
        required = [
            template_path / ".claude" / "skills" / "xlsform-core" / "SKILL.md",
            template_path / ".claude" / "CLAUDE.md",
        ]

        missing = [f for f in required if not f.exists()]
        if missing:
            print_warning("Some template files are missing:")
            for f in missing:
                console.print(f"  - {f.relative_to(template_path)}")
            return False

        print_success("XLSForm AI CLI is properly installed")
        print_success(f"Template version: {tm.get_template_path().name}")
        return True

    except Exception as e:
        print_error(f"Error checking installation: {e}")
        return False


def init_project(
    project_name: str,
    here: bool = False,
    ai: str = "claude",
    force: bool = False,
):
    """Initialize a new XLSForm AI project.

    Args:
        project_name: Name of the project (or . for --here)
        here: Initialize in current directory
        ai: AI agent to configure for
        force: Overwrite existing files
    """
    # Validate agent
    if not validate_agent(ai):
        print_error(f"Agent '{ai}' is not supported")
        console.print(f"\nSupported agents: {', '.join(get_supported_agents())}")
        sys.exit(1)

    # Determine project path
    if here:
        project_path = Path.cwd()
    else:
        project_path = Path.cwd() / project_name

    # Check if directory exists
    if project_path.exists() and not here:
        response = questionary.confirm(
            f"Directory '{project_name}' already exists. Continue?",
            default=False,
        ).ask()

        if not response:
            print_warning("Initialization cancelled")
            return

    console.print(f"\n[bold]Initializing XLSForm AI project...[/bold]\n")

    # Initialize project
    tm = TemplateManager()

    try:
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("Creating project structure...", total=None)

            success = tm.init_project(
                project_path=project_path,
                agent=ai,
                overwrite=force,
            )

            progress.remove_task(task)

        if success:
            console.print(Panel.fit(
                f"[bold green]Project initialized successfully![/bold green]\n\n"
                f"Location: [cyan]{project_path}[/cyan]\n\n"
                f"[bold]Next steps:[/bold]\n"
                f"1. cd {project_path.relative_to(Path.cwd()) if not here else '.'}\n"
                f"2. Open survey.xlsx in Excel\n"
                f"3. Use Claude Code with /xlsform-add commands\n"
                f"4. Or use /xlsform-import to import from PDF/Word",
                title="✓ Success",
                border_style="green",
            ))
        else:
            print_error("Failed to initialize project")
            sys.exit(1)

    except KeyboardInterrupt:
        print_warning("\nInitialization cancelled")
        sys.exit(1)
    except Exception as e:
        print_error(f"Error: {e}")
        sys.exit(1)


def show_info():
    """Show installation and configuration information."""
    print_banner()

    # Installation check
    console.print("\n[bold]Installation Status[/bold]\n")
    check_cli_installation()

    # Supported agents
    console.print(f"\n[bold]Supported Agents[/bold]\n")
    for agent in get_supported_agents():
        console.print(f"  • [cyan]{agent}[/cyan]")

    # Configuration
    console.print(f"\n[bold]Configuration[/bold]\n")
    from .config import Config
    config = Config()
    console.print(f"  Config directory: [cyan]{config.config_dir}[/cyan]")

    pyodk_config = config.get_pyodk_config()
    if pyodk_config:
        console.print(f"  ODK config: [green]{pyodk_config}[/green]")
    else:
        console.print(f"  ODK config: [dim]Not configured[/dim]")

    console.print(f"\n[bold]Documentation[/bold]\n")
    console.print(f"  GitHub: https://github.com/yourusername/xlsform-ai")
    console.print(f"  XLSForm: https://xlsform.org")


# Note: We're using a stub function here since we can't import typer in plan mode
# In actual implementation, this would be the Typer app
def app():
    """Main CLI application entry point."""
    import argparse

    parser = argparse.ArgumentParser(
        description="XLSForm AI - AI-powered XLSForm creation tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  xlsform-ai init my-survey           Create new project
  xlsform-ai init --here               Initialize in current directory
  xlsform-ai init . --ai claude        Specify AI agent
  xlsform-ai check                     Check installation
  xlsform-ai info                      Show information
        """,
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Init command
    init_parser = subparsers.add_parser("init", help="Initialize a new XLSForm AI project")
    init_parser.add_argument(
        "project_name",
        nargs="?",
        help="Name of the project (use '.' with --here)",
    )
    init_parser.add_argument(
        "--here",
        action="store_true",
        help="Initialize in current directory",
    )
    init_parser.add_argument(
        "--ai",
        default="claude",
        help="AI agent to configure for (default: claude)",
    )
    init_parser.add_argument(
        "--force",
        action="store_true",
        help="Overwrite existing files",
    )

    # Check command
    subparsers.add_parser("check", help="Check CLI installation")

    # Info command
    subparsers.add_parser("info", help="Show installation information")

    # Version
    parser.add_argument("--version", action="version", version=f"%(prog)s v{__version__}")

    args = parser.parse_args()

    # Execute command
    if args.command == "init":
        if not args.project_name and not args.here:
            print_error("Please specify a project name or use --here")
            sys.exit(1)

        init_project(
            project_name=args.project_name or ".",
            here=args.here,
            ai=args.ai,
            force=args.force,
        )
    elif args.command == "check":
        check_cli_installation()
    elif args.command == "info":
        show_info()
    else:
        parser.print_help()


if __name__ == "__main__":
    app()
