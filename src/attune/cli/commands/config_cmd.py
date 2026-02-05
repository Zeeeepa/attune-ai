"""Configuration management CLI commands for Attune AI.

Provides commands for viewing, modifying, and managing configuration.

Copyright 2026 Smart-AI-Memory
Licensed under Fair Source License 0.9
"""

import json
import logging
import sys
from argparse import Namespace

from attune.config import (
    ConfigLoader,
    UnifiedConfig,
    get_loader,
    load_unified_config,
    save_unified_config,
    validate_config,
)

logger = logging.getLogger(__name__)


def cmd_config_show(args: Namespace) -> int:
    """Show current configuration.

    Args:
        args: Parsed arguments with optional --section and --json flags.

    Returns:
        Exit code (0 for success, 1 for error).
    """
    try:
        config = load_unified_config()
    except ValueError as e:
        print(f"Error loading configuration: {e}", file=sys.stderr)
        return 1
    except json.JSONDecodeError as e:
        print(f"Invalid configuration file: {e}", file=sys.stderr)
        return 1

    # Get data to display
    if hasattr(args, "section") and args.section:
        section_name = args.section
        section = getattr(config, section_name, None)
        if section is None:
            print(f"Unknown section: {section_name}", file=sys.stderr)
            print("Available sections: auth, routing, workflows, analysis, "
                  "persistence, telemetry, environment")
            return 1
        data = {section_name: section.to_dict()}
    else:
        data = config.to_dict()

    # Output format
    if hasattr(args, "json") and args.json:
        print(json.dumps(data, indent=2))
    else:
        _print_config_tree(data)

    return 0


def cmd_config_set(args: Namespace) -> int:
    """Set a configuration value.

    Args:
        args: Parsed arguments with key and value.

    Returns:
        Exit code (0 for success, 1 for error).
    """
    key = args.key
    value = args.value

    # Validate key format
    if "." not in key:
        print(f"Invalid key format: {key}", file=sys.stderr)
        print("Use section.setting format (e.g., routing.default_tier)")
        return 1

    try:
        config = load_unified_config()
    except ValueError as e:
        print(f"Error loading configuration: {e}", file=sys.stderr)
        return 1
    except json.JSONDecodeError as e:
        print(f"Invalid configuration file: {e}", file=sys.stderr)
        return 1

    # Get current value to determine type
    try:
        current_value = config.get_value(key)
    except KeyError as e:
        print(f"Unknown setting: {e}", file=sys.stderr)
        print("\nAvailable keys:")
        for available_key in config.get_all_keys():
            print(f"  {available_key}")
        return 1

    # Convert value to appropriate type
    try:
        typed_value = _convert_value(value, current_value)
    except ValueError as e:
        print(f"Invalid value: {e}", file=sys.stderr)
        return 1

    # Set the value
    try:
        config.set_value(key, typed_value)
    except (KeyError, TypeError) as e:
        print(f"Failed to set value: {e}", file=sys.stderr)
        return 1

    # Validate the new configuration
    errors = validate_config(config)
    real_errors = [e for e in errors if e.severity == "error"]
    warnings = [e for e in errors if e.severity == "warning"]

    if real_errors:
        print("Configuration validation failed:", file=sys.stderr)
        for error in real_errors:
            print(f"  {error}", file=sys.stderr)
        return 1

    # Save the configuration
    try:
        saved_path = save_unified_config(config)
        print(f"Set {key} = {typed_value}")
        print(f"Configuration saved to: {saved_path}")

        # Show warnings if any
        if warnings:
            print("\nWarnings:")
            for warning in warnings:
                print(f"  {warning}")
    except (ValueError, PermissionError, OSError) as e:
        print(f"Failed to save configuration: {e}", file=sys.stderr)
        return 1

    return 0


def cmd_config_get(args: Namespace) -> int:
    """Get a configuration value.

    Args:
        args: Parsed arguments with key.

    Returns:
        Exit code (0 for success, 1 for error).
    """
    key = args.key

    # Validate key format
    if "." not in key:
        print(f"Invalid key format: {key}", file=sys.stderr)
        print("Use section.setting format (e.g., routing.default_tier)")
        return 1

    try:
        config = load_unified_config()
    except ValueError as e:
        print(f"Error loading configuration: {e}", file=sys.stderr)
        return 1
    except json.JSONDecodeError as e:
        print(f"Invalid configuration file: {e}", file=sys.stderr)
        return 1

    try:
        value = config.get_value(key)
        print(value)
    except KeyError as e:
        print(f"Unknown setting: {e}", file=sys.stderr)
        print("\nAvailable keys:")
        for available_key in config.get_all_keys():
            print(f"  {available_key}")
        return 1

    return 0


def cmd_config_path(args: Namespace) -> int:
    """Show configuration file path.

    Args:
        args: Parsed arguments (unused).

    Returns:
        Exit code (0 for success).
    """
    loader = get_loader()

    # Try to discover existing config
    discovered = loader.discover_config_path()
    if discovered:
        print(f"Active config: {discovered}")
    else:
        default = loader.get_default_config_path()
        print(f"No config found. Default location: {default}")

    # Show search paths
    print("\nSearch paths (in priority order):")
    for path in ConfigLoader.discover_config_path.__doc__.split("1.")[1:]:
        # Just show the paths from the docstring
        pass

    # Manually list search paths
    from attune.config.loader import CONFIG_SEARCH_PATHS
    for i, path in enumerate(CONFIG_SEARCH_PATHS, 1):
        print(f"  {i}. {path}")

    return 0


def cmd_config_validate(args: Namespace) -> int:
    """Validate the current configuration.

    Args:
        args: Parsed arguments (unused).

    Returns:
        Exit code (0 for valid, 1 for invalid).
    """
    try:
        config = load_unified_config()
    except ValueError as e:
        print(f"Error loading configuration: {e}", file=sys.stderr)
        return 1
    except json.JSONDecodeError as e:
        print(f"Invalid configuration file: {e}", file=sys.stderr)
        return 1

    errors = validate_config(config)

    if not errors:
        print("Configuration is valid.")
        return 0

    # Separate errors and warnings
    real_errors = [e for e in errors if e.severity == "error"]
    warnings = [e for e in errors if e.severity == "warning"]

    if real_errors:
        print("Validation errors:")
        for error in real_errors:
            print(f"  {error}")

    if warnings:
        print("\nWarnings:")
        for warning in warnings:
            print(f"  {warning}")

    return 1 if real_errors else 0


def cmd_config_reset(args: Namespace) -> int:
    """Reset configuration to defaults.

    Args:
        args: Parsed arguments with optional --confirm flag.

    Returns:
        Exit code (0 for success, 1 for error).
    """
    # Check for confirmation
    if not (hasattr(args, "confirm") and args.confirm):
        print("This will reset all configuration to defaults.")
        print("Use --confirm to proceed.")
        return 1

    # Create default config
    config = UnifiedConfig()

    try:
        saved_path = save_unified_config(config)
        print("Configuration reset to defaults.")
        print(f"Saved to: {saved_path}")
    except (ValueError, PermissionError, OSError) as e:
        print(f"Failed to save configuration: {e}", file=sys.stderr)
        return 1

    return 0


def cmd_config_list_keys(args: Namespace) -> int:
    """List all available configuration keys.

    Args:
        args: Parsed arguments (unused).

    Returns:
        Exit code (0 for success).
    """
    config = UnifiedConfig()

    print("Available configuration keys:")
    print()

    current_section = ""
    for key in config.get_all_keys():
        section, setting = key.split(".", 1)
        if section != current_section:
            if current_section:
                print()
            print(f"[{section}]")
            current_section = section
        value = config.get_value(key)
        print(f"  {setting} = {value}")

    return 0


def _convert_value(value_str: str, current_value: object) -> object:
    """Convert string value to appropriate type based on current value.

    Args:
        value_str: String value from command line.
        current_value: Current value to determine target type.

    Returns:
        Converted value.

    Raises:
        ValueError: If conversion fails.
    """
    if isinstance(current_value, bool):
        if value_str.lower() in ("true", "1", "yes", "on"):
            return True
        elif value_str.lower() in ("false", "0", "no", "off"):
            return False
        else:
            raise ValueError(f"Invalid boolean: {value_str}")

    if isinstance(current_value, int):
        try:
            return int(value_str)
        except ValueError:
            raise ValueError(f"Invalid integer: {value_str}")

    if isinstance(current_value, float):
        try:
            return float(value_str)
        except ValueError:
            raise ValueError(f"Invalid float: {value_str}")

    if isinstance(current_value, list):
        # Split by comma for list values
        return [item.strip() for item in value_str.split(",")]

    # Default: return as string
    return value_str


def _print_config_tree(data: dict, indent: int = 0) -> None:
    """Print configuration as a tree structure.

    Args:
        data: Configuration data dict.
        indent: Current indentation level.
    """
    prefix = "  " * indent

    for key, value in data.items():
        if key.startswith("_"):
            # Skip metadata fields in normal display
            continue

        if isinstance(value, dict):
            print(f"{prefix}{key}:")
            _print_config_tree(value, indent + 1)
        elif isinstance(value, list):
            if value:
                print(f"{prefix}{key}:")
                for item in value:
                    print(f"{prefix}  - {item}")
            else:
                print(f"{prefix}{key}: []")
        else:
            print(f"{prefix}{key}: {value}")
