"""CLI parser registration.

This module coordinates parser registration for all CLI commands.
Parser modules are imported lazily -- only when register_all_parsers()
is called -- so that importing this package does not trigger loading
every parser up front.

Copyright 2025 Smart-AI-Memory
Licensed under the Apache License, Version 2.0
"""

import importlib

# Registry of parser modules and their registration order.
# Each entry is (module_name, comment) -- the module must expose
# a ``register_parsers(subparsers)`` function.
_PARSER_MODULES: list[str] = [
    # Core commands
    "help",
    "tier",
    "info",
    # Pattern and state management
    "patterns",
    "status",
    # Workflow and execution
    "workflow",
    "inspect",
    # Provider configuration
    "provider",
    # Orchestration and sync
    "orchestrate",
    "sync",
    # Metrics and state
    "metrics",
    "cache",
    "batch",
    "routing",
    # Setup and initialization
    "setup",
]


def register_all_parsers(subparsers) -> None:
    """Register all command parsers.

    Parser modules are imported on demand so that the top-level package
    import remains lightweight.

    This function is called from the main CLI entry point to set up
    all subcommands and their argument parsers.

    Args:
        subparsers: ArgumentParser subparsers object from main parser

    Note:
        All 30 commands have been extracted from the monolithic cli.py
        and organized into focused modules.
    """
    for module_name in _PARSER_MODULES:
        module = importlib.import_module(f".{module_name}", package=__name__)
        module.register_parsers(subparsers)
