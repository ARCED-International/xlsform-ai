"""Template management for XLSForm AI projects."""

import json
import os
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import List, Optional
from urllib import request as urlrequest

from .agents import get_agent

TEMPLATE_VERSION = "0.1.0"
DEFAULT_AGENT = "claude"
ODK_VALIDATE_RELEASE_API = "https://api.github.com/repos/getodk/validate/releases/latest"
ODK_VALIDATE_USER_AGENT = "xlsform-ai-cli"
ODK_VALIDATE_TIMEOUT_SECONDS = 30
# Fallback only when release metadata cannot be fetched.
ODK_VALIDATE_FALLBACK_TAG = "v1.20.0"
ODK_VALIDATE_FALLBACK_URL = (
    "https://github.com/getodk/validate/releases/download/v1.20.0/ODK-Validate-v1.20.0.jar"
)
PROJECT_RUNTIME_DEPENDENCIES = [
    "openpyxl>=3.1.0",
    "pyxform>=2.0.0",
    "pdfplumber>=0.11.0",
    "python-docx>=1.1.0",
    "deep-translator>=1.11.4",
]


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

                # Verify activity log template was copied
                template_in_dst = scripts_dst / "activity_log_template.html"
                if template_in_dst.exists():
                    print(f"[OK] Activity log template included")
                else:
                    print(f"[WARNING] Activity log template not found in scripts directory")

            if self._ensure_project_runtime_dependencies():
                print("[OK] Project runtime dependencies ready")
            else:
                print(
                    "[ERROR] Failed to install required runtime dependencies "
                    "(openpyxl, pyxform, pdfplumber, python-docx, deep-translator)."
                )
                print(
                    "[ERROR] Run one of these commands and retry init:\n"
                    "  python -m pip install openpyxl pyxform pdfplumber python-docx deep-translator\n"
                    "  py -3 -m pip install openpyxl pyxform pdfplumber python-docx deep-translator"
                )
                return False

            if self._ensure_odk_validate_jar(project_path, overwrite=overwrite):
                print("[OK] ODK Validate offline engine ready")
            else:
                print(
                    "[WARNING] ODK Validate offline engine not installed. "
                    "Run validation with local checks or install tools/ODK-Validate.jar manually."
                )

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
                                self._copy_text_file_no_bom(cmd_file, dest)

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

                    # Copy shared AGENT_MEMORY_TEMPLATE.md (agent-specific memory file)
                    shared_memory = shared_src / "AGENT_MEMORY_TEMPLATE.md"
                    if shared_memory.exists():
                        memory_file = agent_config.get("memory_file")
                        if memory_file:
                            memory_path = project_path / memory_file
                            if not memory_path.exists() or overwrite:
                                memory_path.parent.mkdir(parents=True, exist_ok=True)
                                self._copy_text_file_no_bom(shared_memory, memory_path)

                    print(f"[OK] Configured {agent} assistant")

            # Create or merge configuration file with multi-agent support
            # IMPORTANT: Never overwrite xlsform-ai.json; merge if it exists.
            config_file = project_path / "xlsform-ai.json"
            try:
                existing_config = {}
                if config_file.exists():
                    try:
                        with open(config_file, 'r', encoding='utf-8') as f:
                            existing_config = json.load(f) or {}
                    except Exception:
                        existing_config = {}

                config_data = self._merge_config_with_defaults(DEFAULT_CONFIG, existing_config)

                config_data["project_name"] = existing_config.get("project_name", project_path.name)
                config_data["created"] = existing_config.get("created", datetime.now().isoformat())

                if existing_config.get("xlsform_file"):
                    config_data["xlsform_file"] = existing_config["xlsform_file"]

                # Auto-detect author for new projects or if not already set
                if not config_data.get("author"):
                    try:
                        import sys
                        scripts_dir = project_path / "scripts"
                        if scripts_dir.exists() and str(scripts_dir) not in sys.path:
                            sys.path.insert(0, str(scripts_dir))
                        from author_utils import get_detected_author

                        detected_author = get_detected_author()
                        if detected_author:
                            config_data["author"] = detected_author
                            config_data["author_updated"] = datetime.now().isoformat()
                    except Exception:
                        pass

                if not config_data.get("location"):
                    try:
                        import sys
                        scripts_dir = project_path / "scripts"
                        if scripts_dir.exists() and str(scripts_dir) not in sys.path:
                            sys.path.insert(0, str(scripts_dir))
                        from author_utils import get_best_location

                        detected_location = get_best_location(project_path, allow_network=True)
                        if detected_location:
                            config_data["location"] = detected_location
                            config_data["location_updated"] = datetime.now().isoformat()
                    except Exception:
                        pass

                existing_agents = config_data.get("enabled_agents") or []
                if not existing_agents:
                    config_data["enabled_agents"] = agents
                else:
                    for agent in agents:
                        if agent not in existing_agents:
                            existing_agents.append(agent)
                    config_data["enabled_agents"] = existing_agents

                if not config_data.get("primary_agent"):
                    config_data["primary_agent"] = agents[0] if agents else DEFAULT_AGENT

                config_data.setdefault("settings", {})
                config_data["settings"].setdefault("parallel_execution", {
                    "enabled": True,
                    "question_threshold": 50,
                    "page_threshold": 10,
                    "size_threshold_mb": 1.0,
                    "user_preference": "auto"
                })

                with open(config_file, 'w', encoding='utf-8') as f:
                    json.dump(config_data, f, indent=2)

                print(f"[OK] Merged xlsform-ai.json configuration")

                if config_data.get("author"):
                    print(f"[INFO] Author detected: {config_data['author']}")
                    print(f"[INFO] You can change this later by editing xlsform-ai.json")
            except Exception as e:
                print(f"Note: Could not update config file: {e}")

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

    def _copy_text_file_no_bom(self, source_path: Path, destination_path: Path) -> None:
        """
        Copy text file using UTF-8 without BOM.

        This prevents markdown frontmatter parsing issues in agent command files.
        """
        try:
            text = source_path.read_text(encoding="utf-8-sig")
            destination_path.parent.mkdir(parents=True, exist_ok=True)
            destination_path.write_text(text, encoding="utf-8")
        except Exception:
            # Fall back to binary copy if text decoding fails.
            shutil.copy2(source_path, destination_path)

    def _merge_config_with_defaults(self, defaults: dict, existing: dict) -> dict:
        """Merge existing config with defaults, preserving existing values."""
        if not isinstance(defaults, dict):
            return existing if existing is not None else defaults

        existing = existing if isinstance(existing, dict) else {}
        merged = {}

        for key, default_val in defaults.items():
            if key in existing:
                existing_val = existing[key]
                if isinstance(default_val, dict) and isinstance(existing_val, dict):
                    merged[key] = self._merge_config_with_defaults(default_val, existing_val)
                else:
                    merged[key] = existing_val
            else:
                merged[key] = default_val

        for key, existing_val in existing.items():
            if key not in merged:
                merged[key] = existing_val

        return merged

    def _fetch_latest_odk_validate_release(self) -> Optional[dict]:
        """Fetch latest ODK Validate release metadata from GitHub."""
        try:
            request = urlrequest.Request(
                ODK_VALIDATE_RELEASE_API,
                headers={
                    "Accept": "application/vnd.github+json",
                    "User-Agent": ODK_VALIDATE_USER_AGENT,
                },
            )
            with urlrequest.urlopen(request, timeout=ODK_VALIDATE_TIMEOUT_SECONDS) as response:
                payload = json.loads(response.read().decode("utf-8"))

            tag = str(payload.get("tag_name", "")).strip()
            assets = payload.get("assets") or []
            jar_asset = None
            for asset in assets:
                name = str(asset.get("name", "")).lower()
                if name.endswith(".jar"):
                    jar_asset = asset
                    break

            if not tag or not jar_asset:
                return None

            return {
                "tag": tag,
                "asset_name": jar_asset.get("name", "ODK-Validate.jar"),
                "download_url": jar_asset.get("browser_download_url"),
                "digest": jar_asset.get("digest"),
                "source": ODK_VALIDATE_RELEASE_API,
            }
        except Exception:
            return None

    def _ensure_odk_validate_jar(self, project_path: Path, overwrite: bool = False) -> bool:
        """Ensure project has an offline ODK Validate jar in tools/."""
        tools_dir = project_path / "tools"
        tools_dir.mkdir(parents=True, exist_ok=True)

        jar_path = tools_dir / "ODK-Validate.jar"
        metadata_path = tools_dir / "ODK-Validate.json"

        release = self._fetch_latest_odk_validate_release()
        if not release:
            release = {
                "tag": ODK_VALIDATE_FALLBACK_TAG,
                "asset_name": "ODK-Validate-v1.20.0.jar",
                "download_url": ODK_VALIDATE_FALLBACK_URL,
                "digest": None,
                "source": "fallback",
            }

        target_tag = str(release.get("tag", "")).strip()
        current_tag = ""
        if metadata_path.exists():
            try:
                with open(metadata_path, "r", encoding="utf-8") as metadata_file:
                    current_tag = str((json.load(metadata_file) or {}).get("tag", "")).strip()
            except Exception:
                current_tag = ""

        if jar_path.exists() and current_tag == target_tag and not overwrite:
            return True

        download_url = str(release.get("download_url", "")).strip()
        if not download_url:
            return jar_path.exists()

        temp_path = tools_dir / ".ODK-Validate.jar.download"
        try:
            request = urlrequest.Request(
                download_url,
                headers={
                    "Accept": "application/octet-stream",
                    "User-Agent": ODK_VALIDATE_USER_AGENT,
                },
            )
            with urlrequest.urlopen(request, timeout=ODK_VALIDATE_TIMEOUT_SECONDS) as response:
                with open(temp_path, "wb") as temp_file:
                    shutil.copyfileobj(response, temp_file)

            with open(temp_path, "rb") as temp_file:
                signature = temp_file.read(2)
            if signature != b"PK":
                raise RuntimeError("Downloaded file is not a valid JAR archive")

            temp_path.replace(jar_path)

            metadata = {
                "tag": target_tag,
                "asset_name": release.get("asset_name"),
                "download_url": download_url,
                "source": release.get("source"),
                "downloaded_at": datetime.now().isoformat(),
            }
            digest = release.get("digest")
            if digest:
                metadata["digest"] = digest
            with open(metadata_path, "w", encoding="utf-8") as metadata_file:
                json.dump(metadata, metadata_file, indent=2)

            return True
        except Exception:
            if temp_path.exists():
                try:
                    temp_path.unlink()
                except Exception:
                    pass
            return jar_path.exists()

    def _candidate_python_commands(self) -> List[List[str]]:
        """Return candidate Python launch commands for dependency bootstrap."""
        candidates: List[List[str]] = []

        # Prefer user-shell python first because project scripts are commonly run as `python scripts/...`.
        candidates.append(["python"])
        if os.name == "nt":
            candidates.append(["py", "-3"])

        # Fallback to current interpreter (e.g., uv tool environment).
        current = str(Path(sys.executable))
        if current:
            candidates.append([current])

        deduped: List[List[str]] = []
        seen = set()
        for cmd in candidates:
            key = tuple(cmd)
            if key not in seen:
                seen.add(key)
                deduped.append(cmd)
        return deduped

    def _run_command(self, command: List[str], timeout_seconds: int = 180) -> bool:
        """Run command and return success/failure."""
        try:
            proc = subprocess.run(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                timeout=timeout_seconds,
                check=False,
            )
            return proc.returncode == 0
        except Exception:
            return False

    def _ensure_project_runtime_dependencies(self) -> bool:
        """
        Ensure required runtime dependencies are installed for project scripts.

        Returns:
            True if dependencies verified in at least one usable Python runtime.
        """
        verify_snippet = (
            "import openpyxl,pyxform,pdfplumber,docx,deep_translator;"
            "print('deps-ok')"
        )

        for launcher in self._candidate_python_commands():
            if not self._run_command(launcher + ["-V"], timeout_seconds=20):
                continue

            # If already installed for this runtime, no-op.
            if self._run_command(launcher + ["-c", verify_snippet], timeout_seconds=30):
                return True

            # Ensure pip exists.
            if not self._run_command(launcher + ["-m", "pip", "--version"], timeout_seconds=30):
                self._run_command(launcher + ["-m", "ensurepip", "--upgrade"], timeout_seconds=120)

            install_cmd = launcher + [
                "-m",
                "pip",
                "install",
                "--disable-pip-version-check",
            ] + PROJECT_RUNTIME_DEPENDENCIES
            installed = self._run_command(install_cmd, timeout_seconds=600)
            if not installed:
                continue

            if self._run_command(launcher + ["-c", verify_snippet], timeout_seconds=30):
                return True

        return False

    def get_template_path(self) -> Path:
        """Get the path to the base template.

        Returns:
            Path to base template directory
        """
        return self.base_template
