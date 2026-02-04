"""Template management for XLSForm AI projects."""

import os
import shutil
from pathlib import Path
from typing import Optional

from .agents import get_agent

TEMPLATE_VERSION = "0.1.0"
DEFAULT_AGENT = "claude"


class TemplateManager:
    """Manages project templates for XLSForm AI."""

    def __init__(self, template_dir: Optional[Path] = None):
        """Initialize template manager.

        Args:
            template_dir: Directory containing templates. Defaults to templates/ in package.
        """
        if template_dir is None:
            # Try to find templates in the package installation first
            import importlib.resources as resources

            try:
                # If templates are bundled with the package
                with resources.files("xlsform_ai") as pkg_files:
                    templates_path = pkg_files / "templates"
                    if templates_path.is_dir():
                        template_dir = Path(str(templates_path))
            except Exception:
                pass

            # Fallback to relative path from package root
            if template_dir is None:
                package_root = Path(__file__).parent.parent
                # Try installed package location
                template_dir = package_root / "templates"

                # If not found, try development location (3 levels up)
                if not template_dir.exists():
                    template_dir = Path(__file__).parent.parent.parent / "templates"

        self.template_dir = Path(template_dir)
        self.base_template = self.template_dir / "base"

    def init_project(
        self,
        project_path: Path,
        agent: str = DEFAULT_AGENT,
        overwrite: bool = False,
    ) -> bool:
        """Initialize a new XLSForm AI project.

        Args:
            project_path: Path where project should be initialized
            agent: Agent to configure for (default: claude)
            overwrite: Whether to overwrite existing files

        Returns:
            True if successful, False otherwise
        """
        # Validate agent
        agent_config = get_agent(agent)
        if not agent_config:
            print(f"Error: Agent '{agent}' is not supported.")
            print(f"Supported agents: {', '.join(get_agent.__code__.co_consts[1] or ['claude'])}")
            return False

        # Check if template exists
        if not self.base_template.exists():
            print(f"Error: Template not found at {self.base_template}")
            return False

        # Create project directory if it doesn't exist
        project_path = Path(project_path)
        project_path.mkdir(parents=True, exist_ok=True)

        # Copy template files
        success = self._copy_template_files(
            project_path,
            agent_config,
            overwrite
        )

        return success

    def _copy_template_files(
        self,
        project_path: Path,
        agent_config: dict,
        overwrite: bool,
    ) -> bool:
        """Copy template files to project directory.

        Args:
            project_path: Target project directory
            agent_config: Agent configuration dict
            overwrite: Whether to overwrite existing files

        Returns:
            True if successful
        """
        try:
            # Copy .claude directory
            claude_src = self.base_template / ".claude"
            claude_dst = project_path / ".claude"

            if claude_dst.exists():
                if overwrite:
                    shutil.rmtree(claude_dst)
                else:
                    print(f"Note: .claude directory already exists, skipping...")

            if not claude_dst.exists() or overwrite:
                shutil.copytree(claude_src, claude_dst)
                print(f"✓ Created .claude directory")

            # Copy scripts directory
            scripts_src = self.base_template / "scripts"
            scripts_dst = project_path / "scripts"

            if scripts_dst.exists():
                if overwrite:
                    shutil.rmtree(scripts_dst)
                else:
                    print(f"Note: scripts directory already exists, skipping...")

            if not scripts_dst.exists() or overwrite:
                shutil.copytree(scripts_src, scripts_dst)
                print(f"✓ Created scripts directory")

            # Copy package.json if it exists
            package_json_src = self.base_template / "package.json"
            package_json_dst = project_path / "package.json"

            if package_json_src.exists():
                if package_json_dst.exists() and not overwrite:
                    print(f"Note: package.json already exists, skipping...")
                else:
                    shutil.copy2(package_json_src, package_json_dst)
                    print(f"✓ Created package.json")

            # Create example XLSForm file
            survey_xlsx = project_path / "survey.xlsx"
            if not survey_xlsx.exists() or overwrite:
                # Copy template if it exists, otherwise create a placeholder
                template_xlsx = self.base_template / ".claude" / "skills" / "xlsform-core" / "assets" / "xlsform-template.xlsx"
                if template_xlsx.exists():
                    shutil.copy2(template_xlsx, survey_xlsx)
                else:
                    # Create a placeholder file
                    survey_xlsx.touch()
                print(f"✓ Created survey.xlsx")

            return True

        except Exception as e:
            print(f"Error copying template files: {e}")
            return False

    def get_template_path(self) -> Path:
        """Get the path to the base template.

        Returns:
            Path to base template directory
        """
        return self.base_template
