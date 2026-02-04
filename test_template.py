#!/usr/bin/env python
"""Test multi-agent template initialization."""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from xlsform_ai.templates import TemplateManager

def test_multi_agent_init():
    """Test initializing a project with multiple agents."""

    print("Testing multi-agent template initialization...")

    # Create template manager
    tm = TemplateManager()

    # Test with multiple agents
    test_project = Path(__file__).parent / "test_multi_agent_project"

    print(f"\nInitializing project at: {test_project}")
    print(f"Agents: claude, cursor-agent, copilot")

    success = tm.init_project(
        project_path=test_project,
        agents=["claude", "cursor-agent", "copilot"],
        overwrite=True
    )

    if success:
        print("\n[OK] Multi-agent initialization successful!")

        # Check that agent directories were created
        for agent in ["claude", "cursor-agent", "copilot"]:
            agent_dir = test_project / f".{agent}"
            if agent_dir.exists():
                print(f"[OK] {agent} directory created")
                # Check for skills
                skills_dir = agent_dir / "skills"
                if skills_dir.exists():
                    print(f"  -> skills/ directory exists")
                    xlsform_core = skills_dir / "xlsform-core"
                    if xlsform_core.exists():
                        print(f"  -> xlsform-core skill exists")
                    sub_agents = skills_dir / "sub-agents"
                    if sub_agents.exists():
                        print(f"  -> sub-agents directory exists")
            else:
                print(f"[X] {agent} directory NOT created")

        # Check for shared resources
        claude_skills = test_project / ".claude" / "skills"
        if claude_skills.exists():
            print("\n[OK] Claude skills directory has content:")
            for item in claude_skills.iterdir():
                print(f"  - {item.name}")

        # Check config
        config_file = test_project / "xlsform-ai.json"
        if config_file.exists():
            import json
            with open(config_file) as f:
                config = json.load(f)
                print(f"\n[OK] Configuration file created")
                print(f"  enabled_agents: {config.get('enabled_agents', [])}")
                print(f"  primary_agent: {config.get('primary_agent', 'N/A')}")
    else:
        print("\n[X] Multi-agent initialization failed!")

    return success

if __name__ == "__main__":
    test_multi_agent_init()
