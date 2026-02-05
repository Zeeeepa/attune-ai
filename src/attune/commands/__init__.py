"""Attune slash commands for Claude Code.

This package contains the markdown command files that define
slash commands for use in Claude Code (VSCode, Claude Desktop).

To install these commands, run:
    attune setup

This will copy the command files to ~/.claude/commands/
"""

from pathlib import Path

# Path to the commands directory
COMMANDS_DIR = Path(__file__).parent


def get_command_files() -> list[Path]:
    """Get all command markdown files."""
    return list(COMMANDS_DIR.glob("*.md"))
