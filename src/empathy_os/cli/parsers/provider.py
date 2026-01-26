"""Parser definitions for provider commands.

Copyright 2025 Smart-AI-Memory
Licensed under Fair Source License 0.9
"""

from ..commands import provider


def register_parsers(subparsers):
    """Register provider command parsers.

    Args:
        subparsers: ArgumentParser subparsers object from main parser
    """
    # Provider parent command
    parser_provider = subparsers.add_parser(
        "provider",
        help="Configure model providers and hybrid mode",
    )
    provider_sub = parser_provider.add_subparsers(dest="provider_command", required=True)

    # Provider hybrid command
    p_hybrid = provider_sub.add_parser(
        "hybrid",
        help="Configure hybrid mode (pick best models for each tier)",
    )
    p_hybrid.set_defaults(func=provider.cmd_provider_hybrid)

    # Provider show command
    p_show = provider_sub.add_parser(
        "show",
        help="Show current provider configuration",
    )
    p_show.set_defaults(func=provider.cmd_provider_show)

    # Provider set command
    p_set = provider_sub.add_parser(
        "set",
        help="Set default provider",
    )
    p_set.add_argument(
        "name",
        choices=["anthropic", "openai", "google", "ollama", "hybrid"],
        help="Provider name",
    )
    p_set.set_defaults(func=provider.cmd_provider_set)
