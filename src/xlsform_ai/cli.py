"""XLSForm AI CLI - Main entry point."""

import sys
from pathlib import Path
from typing import List, Optional

import questionary
import requests
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table

from . import __version__
from .agents import get_supported_agents, validate_agent
from .templates import TemplateManager
from .display import (
    print_main_banner,
    print_init_success,
    print_info_panel,
    print_cleanup_results,
    print_error as display_error,
    print_warning as display_warning,
)

console = Console()


def print_banner():
    """Print welcome banner."""
    print_main_banner()


def print_success(message: str):
    """Print success message."""
    console.print(f"[green][OK] {message}[/green]")


def print_error(message: str):
    """Print error message."""
    console.print(f"[red][X] {message}[/red]")


def print_warning(message: str):
    """Print warning message."""
    console.print(f"[yellow][!] {message}[/yellow]")


def check_cli_installation() -> bool:
    """Check if CLI is properly installed.

    Returns:
        True if all components are available
    """
    from .templates import TemplateManager

    try:
        tm = TemplateManager()
        template_path = tm.get_template_path()

        # Debug: Show where we're looking for templates
        print(f"Looking for templates at: {template_path}")
        print(f"Templates exist: {template_path.exists()}")

        if not template_path.exists():
            print_warning("Template files not found")
            print_warning("This may be because templates weren't included in the package build")
            print_warning("Try reinstalling with: uv tool install xlsform-ai-cli --from git+https://github.com/ARCED-International/xlsform-ai.git --reinstall")
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


def prompt_agent_selection() -> list:
    """Prompt user to select AI agent(s) interactively.

    Returns:
        List of selected agent names
    """
    from .agents import get_supported_agents, get_agent

    agents = get_supported_agents()

    # Build choices for questionary - ALWAYS prompt
    choices = []
    for agent_key in agents:
        agent_info = get_agent(agent_key)
        name = agent_info['name']
        description = agent_info.get('description', 'AI assistant')
        choices.append(questionary.Choice(
            title=f"{name} - {description}",
            value=agent_key,
            checked=(agent_key == agents[0])  # First agent checked by default
        ))

    # Always prompt - even for single agent
    if len(agents) == 1:
        # Single agent: use confirm instead of checkbox
        agent_info = get_agent(agents[0])
        response = questionary.confirm(
            f"Use {agent_info['name']} ({agent_info.get('description', 'AI assistant')})?",
            default=True,
        ).ask()
        if response:
            return agents
        else:
            print_warning("Agent selection cancelled. Using default: claude")
            return ["claude"]
    else:
        # Multiple agents: use checkbox
        selections = questionary.checkbox(
            "Which AI agent(s) would you like to use?",
            choices=choices,
            validate=lambda x: len(x) > 0 or "You must select at least one agent"
        ).ask()

        if not selections or len(selections) == 0:
            print_warning("No agent selected. Using default: claude")
            return ["claude"]

        # Remove duplicates while preserving order
        seen = set()
        unique_selections = []
        for agent in selections:
            if agent not in seen:
                seen.add(agent)
                unique_selections.append(agent)

        return unique_selections


def init_project(
    project_name: str,
    here: bool = False,
    ai: Optional[str] = None,
    force: bool = False,
):
    """Initialize a new XLSForm AI project.

    Args:
        project_name: Name of the project (or . for --here)
        here: Initialize in current directory
        ai: AI agent(s) to configure for (comma-separated list)
        force: Overwrite existing files
    """
    # Show the beautiful banner at the start
    print_banner()

    # Determine which agents to use
    if ai is None:
        # Prompt for agent selection
        selected_agents = prompt_agent_selection()
    else:
        # Parse comma-separated agents
        selected_agents = [a.strip() for a in ai.split(',')]
        # Remove duplicates while preserving order
        seen = set()
        unique_agents = []
        for agent in selected_agents:
            if agent not in seen:
                seen.add(agent)
                unique_agents.append(agent)
        selected_agents = unique_agents

    # Validate all selected agents
    for agent in selected_agents:
        if not validate_agent(agent):
            print_error(f"Agent '{agent}' is not supported")
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
                agents=selected_agents,
                overwrite=force,
            )

            progress.remove_task(task)

        if success:
            # Calculate relative path for display
            if here:
                relative_path = "."
            else:
                relative_path = str(project_path.relative_to(Path.cwd()))

            print_init_success(
                location=str(project_path),
                relative_path=relative_path
            )
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

    # Gather information for display
    info = {
        "installed": check_cli_installation(),
        "agents": get_supported_agents(),
    }

    # Configuration
    from .config import Config
    config = Config()
    info["config_dir"] = str(config.config_dir)

    # Display the info panel
    print_info_panel(info)


def cleanup_project(dry_run: bool = False):
    """Clean up XLSForm AI files from current directory.

    Args:
        dry_run: Show what would be removed without actually removing
    """
    import sys
    sys.path.insert(0, Path.cwd())

    try:
        from scripts.cleanup import cleanup_project as cp
    except ImportError:
        print_error("Cleanup script not found. Are you in an XLSForm AI project?")
        sys.exit(1)

    console.print("\n[bold]Cleaning up XLSForm AI files...[/bold]\n")

    if dry_run:
        console.print("[yellow]Dry run mode - showing what would be removed:[/yellow]\n")

    result = cp(dry_run=dry_run)

    # Use the beautiful display module for results
    print_cleanup_results(result, dry_run=dry_run)


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
  xlsform-ai init my-survey           Create new project (prompts for agent selection)
  xlsform-ai init . --ai claude       Skip prompt, use single agent
  xlsform-ai init . --ai claude,cursor Use multiple agents
  xlsform-ai init --here              Same as 'init .' (initialize in current directory)
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
        help="Name of the project (use '.' for current directory)",
    )
    init_parser.add_argument(
        "--here",
        action="store_true",
        help="Initialize in current directory (same as using '.')",
    )
    init_parser.add_argument(
        "--ai",
        default=None,
        help="AI agent(s) to configure for (comma-separated, prompts if not specified)",
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

    # Cleanup command
    cleanup_parser = subparsers.add_parser("cleanup", help="Remove XLSForm AI files, keeping outputs")
    cleanup_parser.add_argument(
        "--dry-run",
        "-n",
        action="store_true",
        help="Show what would be removed without actually removing"
    )

    # Version
    parser.add_argument("--version", action="version", version=f"%(prog)s v{__version__}")

    args = parser.parse_args()

    # Execute command
    if args.command == "init":
        # Support both "init ." and "init --here" for current directory
        here = args.here or args.project_name == "."

        if not args.project_name and not here:
            print_error("Please specify a project name or use --here")
            sys.exit(1)

        init_project(
            project_name=args.project_name or ".",
            here=here,
            ai=args.ai,
            force=args.force,
        )
    elif args.command == "check":
        check_cli_installation()
    elif args.command == "info":
        show_info()
    elif args.command == "cleanup":
        cleanup_project(dry_run=args.dry_run)
    else:
        parser.print_help()


if __name__ == "__main__":
    app()
