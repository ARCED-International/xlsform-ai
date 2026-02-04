"""Agent configuration for XLSForm AI."""

from typing import Dict, List, Optional
from pathlib import Path

# Agent configuration
# Maps agent names to their specific configurations
AGENTS: Dict[str, Dict] = {
    "claude": {
        "name": "Claude",
        "description": "Anthropic's AI assistant - Best for complex reasoning and natural language understanding",
        "commands_dir": ".claude/commands",
        "skills_dir": ".claude/skills",
        "memory_file": ".claude/CLAUDE.md",
        "command_format": "markdown",
        "supported": True,
        "alias": ["anthropic", "claude-code"],
    },
    "copilot": {
        "name": "GitHub Copilot",
        "description": "GitHub's AI coding assistant - Seamless GitHub integration",
        "commands_dir": ".copilot/instructions",
        "skills_dir": ".copilot/skills",
        "memory_file": ".copilot/MEMORY.md",
        "command_format": "markdown",
        "supported": True,
        "alias": ["github-copilot"],
    },
    "gemini": {
        "name": "Gemini",
        "description": "Google's AI coding assistant - Multimodal capabilities",
        "commands_dir": ".gemini/commands",
        "skills_dir": ".gemini/skills",
        "memory_file": ".gemini/GEMINI.md",
        "command_format": "markdown",
        "supported": True,
        "alias": ["google-gemini"],
    },
    "cursor-agent": {
        "name": "Cursor",
        "description": "AI-first code editor - Excellent for code generation",
        "commands_dir": ".cursor/rules",
        "skills_dir": ".cursor/skills",
        "memory_file": ".cursor/MEMORY.md",
        "command_format": "markdown",
        "supported": True,
        "alias": ["cursor"],
    },
    "qwen": {
        "name": "Qwen Code",
        "description": "Alibaba's AI coding assistant - Strong coding capabilities",
        "commands_dir": ".qwen/commands",
        "skills_dir": ".qwen/skills",
        "memory_file": ".qwen/QWEN.md",
        "command_format": "markdown",
        "supported": True,
    },
    "opencode": {
        "name": "OpenCode",
        "description": "OpenCode AI assistant - Open source focused",
        "commands_dir": ".opencode/commands",
        "skills_dir": ".opencode/skills",
        "memory_file": ".opencode/MEMORY.md",
        "command_format": "markdown",
        "supported": True,
    },
    "codex": {
        "name": "Codex CLI",
        "description": "OpenAI Codex-based CLI - Powerful code generation",
        "commands_dir": ".codex/commands",
        "skills_dir": ".codex/skills",
        "memory_file": ".codex/MEMORY.md",
        "command_format": "markdown",
        "supported": True,
    },
    "windsurf": {
        "name": "Windsurf",
        "description": "Windsurf AI code editor - Next-gen development",
        "commands_dir": ".windsurf/commands",
        "skills_dir": ".windsurf/skills",
        "memory_file": ".windsurf/MEMORY.md",
        "command_format": "markdown",
        "supported": True,
    },
    "kilocode": {
        "name": "Kilo Code",
        "description": "Kilo Code AI assistant - Efficient code handling",
        "commands_dir": ".kilocode/commands",
        "skills_dir": ".kilocode/skills",
        "memory_file": ".kilocode/MEMORY.md",
        "command_format": "markdown",
        "supported": True,
    },
    "auggie": {
        "name": "Auggie",
        "description": "Auggie CLI AI assistant - Lightweight and fast",
        "commands_dir": ".auggie/commands",
        "skills_dir": ".auggie/skills",
        "memory_file": ".auggie/MEMORY.md",
        "command_format": "markdown",
        "supported": True,
    },
    "codebuddy": {
        "name": "CodeBuddy",
        "description": "CodeBuddy CLI assistant - Helpful coding companion",
        "commands_dir": ".codebuddy/commands",
        "skills_dir": ".codebuddy/skills",
        "memory_file": ".codebuddy/MEMORY.md",
        "command_format": "markdown",
        "supported": True,
    },
    "qoder": {
        "name": "Qoder",
        "description": "Qoder CLI AI assistant - Smart code completion",
        "commands_dir": ".qoder/commands",
        "skills_dir": ".qoder/skills",
        "memory_file": ".qoder/MEMORY.md",
        "command_format": "markdown",
        "supported": True,
    },
    "roo": {
        "name": "Roo Code",
        "description": "Roo AI coding assistant - Intelligent code generation",
        "commands_dir": ".roo/commands",
        "skills_dir": ".roo/skills",
        "memory_file": ".roo/MEMORY.md",
        "command_format": "markdown",
        "supported": True,
    },
    "q": {
        "name": "Amazon Q Developer",
        "description": "Amazon's AI coding assistant - AWS integration",
        "commands_dir": ".amazon-q/commands",
        "skills_dir": ".amazon-q/skills",
        "memory_file": ".amazon-q/Q.md",
        "command_format": "markdown",
        "supported": False,  # Limited slash command support
        "alias": ["amazon-q", "q-developer"],
    },
    "amp": {
        "name": "Amp",
        "description": "Amp AI assistant - Amplify your coding",
        "commands_dir": ".amp/commands",
        "skills_dir": ".amp/skills",
        "memory_file": ".amp/MEMORY.md",
        "command_format": "markdown",
        "supported": True,
    },
    "shai": {
        "name": "SHAI",
        "description": "OVHcloud SHAI assistant - European AI solution",
        "commands_dir": ".shai/commands",
        "skills_dir": ".shai/skills",
        "memory_file": ".shai/SHAI.md",
        "command_format": "markdown",
        "supported": True,
    },
    "bob": {
        "name": "IBM Bob",
        "description": "IBM's AI coding assistant - Enterprise focused",
        "commands_dir": ".bob/commands",
        "skills_dir": ".bob/skills",
        "memory_file": ".bob/MEMORY.md",
        "command_format": "markdown",
        "supported": True,
    },
}


def get_agent(agent_name: str) -> Optional[Dict]:
    """Get configuration for a specific agent.

    Args:
        agent_name: Name of the agent (e.g., "claude")

    Returns:
        Agent configuration dict or None if not found
    """
    return AGENTS.get(agent_name.lower())


def get_supported_agents() -> List[str]:
    """Get list of supported agent names.

    Returns:
        List of agent names that are fully supported
    """
    return [name for name, config in AGENTS.items() if config.get("supported", False)]


def get_all_agents() -> List[str]:
    """Get list of all configured agent names.

    Returns:
        List of all agent names (supported and unsupported)
    """
    return list(AGENTS.keys())


def validate_agent(agent_name: str) -> bool:
    """Check if an agent is supported.

    Args:
        agent_name: Name of the agent to validate

    Returns:
        True if agent is supported, False otherwise
    """
    agent = get_agent(agent_name)
    return agent is not None and agent.get("supported", False)


def get_agent_by_alias(alias: str) -> Optional[Dict]:
    """Get agent by alias or name.

    Args:
        alias: Agent alias or name

    Returns:
        Agent configuration dict or None if not found
    """
    alias_lower = alias.lower().replace('-', '').replace('_', '')

    for agent_name, config in AGENTS.items():
        # Check exact name match
        if alias_lower == agent_name.lower().replace('-', '').replace('_', ''):
            return config

        # Check aliases
        if config.get("alias"):
            for a in config["alias"]:
                if alias_lower == a.lower().replace('-', '').replace('_', ''):
                    return config

    return None


def get_agent_directory_structure(agent_name: str) -> Dict[str, Path]:
    """Get all directory paths for an agent.

    Args:
        agent_name: Name of the agent

    Returns:
        Dict with 'commands', 'skills', and 'memory' keys mapping to Path objects
    """
    agent = get_agent(agent_name)
    if not agent:
        return {}

    return {
        "commands": Path(agent["commands_dir"]),
        "skills": Path(agent["skills_dir"]),
        "memory": Path(agent["memory_file"]).parent,
    }
