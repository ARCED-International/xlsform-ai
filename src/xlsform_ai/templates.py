"""Template management for XLSForm AI projects."""

import json
import os
import shutil
from datetime import datetime
from pathlib import Path
from typing import List, Optional

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
            # Templates should be inside the xlsform_ai package
            import importlib.resources as resources

            try:
                # Try to find templates in the installed package
                with resources.files("xlsform_ai") as pkg_files:
                    templates_path = pkg_files / "templates"
                    if templates_path.is_dir():
                        template_dir = Path(str(templates_path))
            except Exception:
                # Fallback to relative path for development
                template_dir = Path(__file__).parent / "templates"

        self.template_dir = Path(template_dir)
        self.base_template = self.template_dir / "base"

    def init_project(
        self,
        project_path: Path,
        agents: List[str] = None,
        overwrite: bool = False,
    ) -> bool:
        """Initialize a new XLSForm AI project.

        Args:
            project_path: Path where project should be initialized
            agents: List of agents to configure for (default: [claude])
            overwrite: Whether to overwrite existing files

        Returns:
            True if successful, False otherwise
        """
        # Default to claude if no agents specified
        if agents is None:
            agents = [DEFAULT_AGENT]

        # Validate all agents
        for agent in agents:
            agent_config = get_agent(agent)
            if not agent_config:
                print(f"Error: Agent '{agent}' is not supported.")
                from .agents import get_supported_agents
                print(f"Supported agents: {', '.join(get_supported_agents())}")
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
            agents,
            overwrite
        )

        return success

    def _copy_template_files(
        self,
        project_path: Path,
        agents: List[str],
        overwrite: bool,
    ) -> bool:
        """Copy template files to project directory.

        Args:
            project_path: Target project directory
            agents: List of agent names to configure for
            overwrite: Whether to overwrite existing files

        IMPORTANT: Never overwrite survey file and activity log files during re-init,
        even if overwrite=True. These files contain user data.

        Returns:
            True if successful
        """
        try:
            # Detect existing survey file (from config or default)
            try:
                # Import config module from scripts
                import sys
                scripts_dir = self.base_template / "scripts"
                if str(scripts_dir) not in sys.path:
                    sys.path.insert(0, str(scripts_dir))
                from config import ProjectConfig, DEFAULT_CONFIG

                # Check if config exists in project
                config_file = project_path / "xlsform-ai.json"
                if config_file.exists():
                    config = ProjectConfig(project_path)
                    survey_file_name = config.get_xlsform_file()
                else:
                    survey_file_name = "survey.xlsx"
            except Exception:
                survey_file_name = "survey.xlsx"

            survey_xlsx = project_path / survey_file_name

            # Find existing activity log files
            existing_activity_logs = list(project_path.glob("activity_log_*.html"))

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
                print(f"[OK] Created scripts directory")

            # Copy package.json if it exists
            package_json_src = self.base_template / "package.json"
            package_json_dst = project_path / "package.json"

            if package_json_src.exists():
                if package_json_dst.exists() and not overwrite:
                    print(f"Note: package.json already exists, skipping...")
                else:
                    shutil.copy2(package_json_src, package_json_dst)
                    print(f"[OK] Created package.json")

            # Copy shared/ directory resources to each agent's directory
            shared_src = self.base_template / "shared"
            if shared_src.exists():
                for agent in agents:
                    agent_config = get_agent(agent)
                    if not agent_config:
                        continue

                    # Get agent-specific directory paths
                    agent_dir = project_path / agent_config.get("skills_dir", "").rstrip("/skills")
                    agent_commands_dir = project_path / agent_config.get("commands_dir", "")
                    agent_skills_dir = agent_dir / "skills"

                    # Create agent directories
                    agent_commands_dir.mkdir(parents=True, exist_ok=True)
                    agent_skills_dir.mkdir(parents=True, exist_ok=True)

                    # Copy shared commands
                    shared_commands = shared_src / "commands"
                    if shared_commands.exists():
                        for cmd_file in shared_commands.glob("*.md"):
                            dest = agent_commands_dir / cmd_file.name
                            if not dest.exists() or overwrite:
                                shutil.copy2(cmd_file, dest)

                    # Copy shared skills (including xlsform-core and sub-agents)
                    shared_skills = shared_src / "skills"
                    if shared_skills.exists():
                        for skill_dir in shared_skills.iterdir():
                            if skill_dir.is_dir():
                                dest = agent_skills_dir / skill_dir.name
                                if dest.exists():
                                    if overwrite:
                                        shutil.rmtree(dest)
                                    else:
                                        continue
                                shutil.copytree(skill_dir, dest)

                    # Copy shared CLAUDE.md (agent-specific memory file)
                    shared_claude = shared_src / "CLAUDE.md"
                    if shared_claude.exists():
                        memory_file = agent_config.get("memory_file")
                        if memory_file:
                            memory_path = project_path / memory_file
                            if not memory_path.exists() or overwrite:
                                memory_path.parent.mkdir(parents=True, exist_ok=True)
                                shutil.copy2(shared_claude, memory_path)

                    print(f"[OK] Configured {agent} assistant")

            # Create configuration file with multi-agent support
            config_file = project_path / "xlsform-ai.json"
            if not config_file.exists() or overwrite:
                try:
                    config_data = DEFAULT_CONFIG.copy()
                    config_data["project_name"] = project_path.name
                    config_data["created"] = datetime.now().isoformat()

                    # Add multi-agent configuration
                    config_data["enabled_agents"] = agents
                    config_data["primary_agent"] = agents[0] if agents else "claude"
                    config_data["settings"]["parallel_execution"] = {
                        "enabled": True,
                        "question_threshold": 50,
                        "page_threshold": 10,
                        "size_threshold_mb": 1.0,
                        "user_preference": "auto"
                    }

                    with open(config_file, 'w', encoding='utf-8') as f:
                        json.dump(config_data, f, indent=2)

                    print(f"[OK] Created xlsform-ai.json configuration")
                except Exception as e:
                    print(f"Note: Could not create config file: {e}")

            # Create example XLSForm file - NEVER overwrite if it exists
            if not survey_xlsx.exists():
                template_xlsx = self.base_template / "shared" / "skills" / "xlsform-core" / "assets" / "xlsform-template.xlsx"
                if template_xlsx.exists():
                    shutil.copy2(template_xlsx, survey_xlsx)
                    # Note: Template sourced from Google Sheets
                    # https://docs.google.com/spreadsheets/d/1v9Bumt3R0vCOGEKQI6ExUf2-8T72-XXp_CbKKTACuko/edit?gid=1068911091
                    # To update: Download as XLSX and replace both template files:
                    #   - src/xlsform_ai/templates/base/shared/skills/xlsform-core/assets/xlsform-template.xlsx
                    #   - src/xlsform_ai/templates/base/.claude/skills/xlsform-core/assets/xlsform-template.xlsx
                    # Template has freeze panes pre-set - we don't modify with openpyxl to avoid corruption
                else:
                    survey_xlsx.touch()
                print(f"[OK] Created {survey_file_name}")
            else:
                print(f"Note: {survey_file_name} already exists, preserving data...")

            # NEVER delete activity log files during re-init
            if existing_activity_logs:
                print(f"Note: Preserving {len(existing_activity_logs)} existing activity log file(s)")

            return True

        except Exception as e:
            print(f"Error copying template files: {e}")
            return False

    def _merge_agent_config(
        self,
        target_dir: Path,
        agent_template_dir: Path,
    ):
        """Merge agent-specific configuration into target directory.

        Args:
            target_dir: Target .claude directory
            agent_template_dir: Agent-specific template directory
        """
        # Copy agent-specific files, overwriting base files if they exist
        for item in agent_template_dir.iterdir():
            target = target_dir / item.name

            if item.is_dir():
                if target.exists():
                    shutil.rmtree(target)
                shutil.copytree(item, target)
            else:
                shutil.copy2(item, target)

    def get_template_path(self) -> Path:
        """Get the path to the base template.

        Returns:
            Path to base template directory
        """
        return self.base_template
