"""CLI parser registration.

This module coordinates parser registration for all CLI commands.

Copyright 2025 Smart-AI-Memory
Licensed under Fair Source License 0.9
"""

from . import help, info, patterns, status, tier


def register_all_parsers(subparsers):
    """Register all command parsers.

    This function is called from the main CLI entry point to set up
    all subcommands and their argument parsers.

    Args:
        subparsers: ArgumentParser subparsers object from main parser

    Note:
        As additional command modules are extracted from cli.py,
        import them here and call their register_parsers() function.
    """
    help.register_parsers(subparsers)
    tier.register_parsers(subparsers)
    info.register_parsers(subparsers)
    patterns.register_parsers(subparsers)
    status.register_parsers(subparsers)
