"""Agent configuration for XLSForm AI."""

from typing import Dict, List, Optional

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
    },
    # Future agents can be added here
    # "cursor": {
    #     "name": "Cursor",
    #     "description": "AI code editor - Great for code generation and refactoring",
    #     "commands_dir": ".cursor/rules",
    #     "skills_dir": ".cursor/skills",
    #     "memory_file": ".cursor/MEMORY.md",
    #     "command_format": "markdown",
    #     "supported": False,
    # },
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
