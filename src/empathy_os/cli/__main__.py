"""Entry point for python -m empathy_os.cli.

Supports both the new Typer-based CLI and legacy CLI.
New commands (profile, etc.) are in the Typer CLI.
Legacy commands fall back to cli.py for compatibility.
"""

import sys
from pathlib import Path

# Commands that are only in the new Typer CLI
NEW_CLI_COMMANDS = {"profile", "memory", "provider"}


def main() -> None:
    """Route to appropriate CLI based on command."""
    # Check if we should use the new Typer CLI
    if len(sys.argv) > 1 and sys.argv[1] in NEW_CLI_COMMANDS:
        # Use the new Typer-based CLI
        from empathy_os.cli import app

        app()
        return

    # Fall back to legacy CLI for backward compatibility
    parent = Path(__file__).parent.parent
    if str(parent) not in sys.path:
        sys.path.insert(0, str(parent))

    import importlib.util

    cli_py_path = parent / "cli.py"
    spec = importlib.util.spec_from_file_location("cli_legacy", cli_py_path)
    cli_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(cli_module)
    cli_module.main()


if __name__ == "__main__":
    main()
