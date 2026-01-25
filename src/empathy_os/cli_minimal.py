#!/usr/bin/env python3
"""Empathy Framework Minimal CLI.

A streamlined CLI for automation and CI/CD workflows.
Interactive features are available via Claude Code skills.

Commands:
    empathy workflow list              List available workflows
    empathy workflow run <name>        Execute a workflow
    empathy workflow info <name>       Show workflow details

    empathy telemetry show             Display usage summary
    empathy telemetry savings          Show cost savings
    empathy telemetry export           Export to CSV/JSON

    empathy provider show              Show current provider config
    empathy provider set <name>        Set provider (anthropic, openai, hybrid)

    empathy validate                   Validate configuration
    empathy version                    Show version

For interactive features, use Claude Code skills:
    /dev        Developer tools (debug, commit, PR, review)
    /testing    Run tests, coverage, benchmarks
    /docs       Documentation generation
    /release    Release preparation
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from argparse import Namespace

logger = logging.getLogger(__name__)


def get_version() -> str:
    """Get package version."""
    try:
        from importlib.metadata import version

        return version("empathy-framework")
    except Exception:  # noqa: BLE001
        # INTENTIONAL: Fallback for dev installs without metadata
        return "dev"


# =============================================================================
# Workflow Commands
# =============================================================================


def cmd_workflow_list(args: Namespace) -> int:
    """List available workflows."""
    from empathy_os.workflows import discover_workflows

    workflows = discover_workflows()

    print("\n📋 Available Workflows\n")
    print("-" * 60)

    if not workflows:
        print("No workflows registered.")
        return 0

    for name, workflow_cls in sorted(workflows.items()):
        doc = workflow_cls.__doc__ or "No description"
        # Get first line of docstring
        description = doc.split("\n")[0].strip()
        print(f"  {name:25} {description}")

    print("-" * 60)
    print(f"\nTotal: {len(workflows)} workflows")
    print("\nRun a workflow: empathy workflow run <name>")
    return 0


def cmd_workflow_info(args: Namespace) -> int:
    """Show workflow details."""
    from empathy_os.workflows import discover_workflows

    workflows = discover_workflows()
    name = args.name
    if name not in workflows:
        print(f"❌ Workflow not found: {name}")
        print("\nAvailable workflows:")
        for wf_name in sorted(workflows.keys()):
            print(f"  - {wf_name}")
        return 1

    workflow_cls = workflows[name]
    print(f"\n📋 Workflow: {name}\n")
    print("-" * 60)

    # Show docstring
    if workflow_cls.__doc__:
        print(workflow_cls.__doc__)

    # Show input schema if available
    if hasattr(workflow_cls, "input_schema"):
        print("\nInput Schema:")
        print(json.dumps(workflow_cls.input_schema, indent=2))

    print("-" * 60)
    return 0


def cmd_workflow_run(args: Namespace) -> int:
    """Execute a workflow."""
    import asyncio

    from empathy_os.config import _validate_file_path
    from empathy_os.workflows import discover_workflows

    workflows = discover_workflows()
    name = args.name
    if name not in workflows:
        print(f"❌ Workflow not found: {name}")
        return 1

    # Parse input if provided
    input_data = {}
    if args.input:
        try:
            input_data = json.loads(args.input)
        except json.JSONDecodeError as e:
            print(f"❌ Invalid JSON input: {e}")
            return 1

    # Add common options with validation
    if args.path:
        try:
            # Validate path to prevent path traversal attacks
            validated_path = _validate_file_path(args.path)
            input_data["path"] = str(validated_path)
        except ValueError as e:
            print(f"❌ Invalid path: {e}")
            return 1
    if args.target:
        input_data["target"] = args.target

    print(f"\n🚀 Running workflow: {name}\n")

    try:
        workflow_cls = workflows[name]
        workflow = workflow_cls()

        # Run the workflow
        if asyncio.iscoroutinefunction(workflow.execute):
            result = asyncio.run(workflow.execute(**input_data))
        else:
            result = workflow.execute(**input_data)

        # Output result
        if args.json:
            print(json.dumps(result, indent=2, default=str))
        else:
            if isinstance(result, dict):
                print("\n✅ Workflow completed\n")
                for key, value in result.items():
                    print(f"  {key}: {value}")
            else:
                print(f"\n✅ Result: {result}")

        return 0

    except Exception as e:  # noqa: BLE001
        # INTENTIONAL: CLI commands should catch all errors and report gracefully
        logger.exception(f"Workflow failed: {e}")
        print(f"\n❌ Workflow failed: {e}")
        return 1


# =============================================================================
# Telemetry Commands
# =============================================================================


def cmd_telemetry_show(args: Namespace) -> int:
    """Display usage summary."""
    try:
        from empathy_os.models.telemetry import TelemetryStore

        store = TelemetryStore()

        print("\n📊 Telemetry Summary\n")
        print("-" * 60)
        print(f"  Period:         Last {args.days} days")

        # Get workflow records from store
        # TODO: Consider adding aggregate methods to TelemetryStore for better performance
        # with large datasets (e.g., store.get_total_cost(), store.get_token_counts())
        workflows = store.get_workflows(limit=1000)
        calls = store.get_calls(limit=1000)

        if workflows:
            total_cost = sum(r.total_cost for r in workflows)
            total_tokens = sum(r.total_input_tokens + r.total_output_tokens for r in workflows)
            print(f"  Workflow runs:  {len(workflows):,}")
            print(f"  Total tokens:   {total_tokens:,}")
            print(f"  Total cost:     ${total_cost:.2f}")
        elif calls:
            total_cost = sum(c.estimated_cost for c in calls)
            total_tokens = sum(c.input_tokens + c.output_tokens for c in calls)
            print(f"  API calls:      {len(calls):,}")
            print(f"  Total tokens:   {total_tokens:,}")
            print(f"  Total cost:     ${total_cost:.2f}")
        else:
            print("  No telemetry data found.")

        print("-" * 60)
        return 0

    except ImportError:
        print("❌ Telemetry module not available")
        return 1
    except Exception as e:  # noqa: BLE001
        # INTENTIONAL: CLI commands should catch all errors and report gracefully
        logger.exception(f"Telemetry error: {e}")
        print(f"❌ Error: {e}")
        return 1


def cmd_telemetry_savings(args: Namespace) -> int:
    """Show cost savings from tier routing."""
    try:
        from empathy_os.models.telemetry import TelemetryStore

        store = TelemetryStore()

        print("\n💰 Cost Savings Report\n")
        print("-" * 60)
        print(f"  Period:              Last {args.days} days")

        # Calculate savings from workflow runs
        records = store.get_workflows(limit=1000)
        if records:
            actual_cost = sum(r.total_cost for r in records)
            total_tokens = sum(r.total_input_tokens + r.total_output_tokens for r in records)

            # Calculate what premium-only pricing would cost
            # Using Claude Opus pricing as premium baseline: ~$15/1M input, ~$75/1M output
            # Simplified: ~$45/1M tokens average (blended input/output)
            premium_rate_per_token = 45.0 / 1_000_000
            baseline_cost = total_tokens * premium_rate_per_token

            # Only show savings if we actually routed to cheaper models
            if baseline_cost > actual_cost:
                savings = baseline_cost - actual_cost
                savings_pct = (savings / baseline_cost * 100) if baseline_cost > 0 else 0

                print(f"  Actual cost:         ${actual_cost:.2f}")
                print(f"  Premium-only cost:   ${baseline_cost:.2f} (estimated)")
                print(f"  Savings:             ${savings:.2f}")
                print(f"  Savings percentage:  {savings_pct:.1f}%")
            else:
                print(f"  Total cost:          ${actual_cost:.2f}")
                print(f"  Total tokens:        {total_tokens:,}")
                print("\n  Note: No savings detected (may already be optimized)")

            print("\n  * Premium baseline assumes Claude Opus pricing (~$45/1M tokens)")
        else:
            print("  No telemetry data found.")

        print("-" * 60)
        return 0

    except ImportError:
        print("❌ Telemetry module not available")
        return 1
    except Exception as e:  # noqa: BLE001
        # INTENTIONAL: CLI commands should catch all errors and report gracefully
        logger.exception(f"Telemetry error: {e}")
        print(f"❌ Error: {e}")
        return 1


def cmd_telemetry_export(args: Namespace) -> int:
    """Export telemetry data to file."""
    from empathy_os.config import _validate_file_path

    try:
        from empathy_os.models.telemetry import TelemetryStore

        store = TelemetryStore()
        records = store.get_workflows(limit=10000)

        # Convert to exportable format
        data = [
            {
                "run_id": r.run_id,
                "workflow_name": r.workflow_name,
                "timestamp": r.started_at,
                "total_cost": r.total_cost,
                "input_tokens": r.total_input_tokens,
                "output_tokens": r.total_output_tokens,
                "success": r.success,
            }
            for r in records
        ]

        # Validate output path
        output_path = _validate_file_path(args.output)

        if args.format == "csv":
            import csv

            with output_path.open("w", newline="") as f:
                if data:
                    writer = csv.DictWriter(f, fieldnames=data[0].keys())
                    writer.writeheader()
                    writer.writerows(data)
            print(f"✅ Exported {len(data)} entries to {output_path}")

        elif args.format == "json":
            with output_path.open("w") as f:
                json.dump(data, f, indent=2, default=str)
            print(f"✅ Exported {len(data)} entries to {output_path}")

        return 0

    except ImportError:
        print("❌ Telemetry module not available")
        return 1
    except ValueError as e:
        print(f"❌ Invalid path: {e}")
        return 1
    except Exception as e:  # noqa: BLE001
        # INTENTIONAL: CLI commands should catch all errors and report gracefully
        logger.exception(f"Export error: {e}")
        print(f"❌ Error: {e}")
        return 1


# =============================================================================
# Provider Commands
# =============================================================================


def cmd_provider_show(args: Namespace) -> int:
    """Show current provider configuration."""
    try:
        from empathy_os.models.provider_config import get_provider_config

        config = get_provider_config()

        print("\n🔧 Provider Configuration\n")
        print("-" * 60)
        print(f"  Mode:            {config.mode.value}")
        print(f"  Primary provider: {config.primary_provider}")
        print(f"  Cost optimization: {'✅ Enabled' if config.cost_optimization else '❌ Disabled'}")

        if config.available_providers:
            print("\n  Available providers:")
            for provider in config.available_providers:
                status = "✓" if provider == config.primary_provider else " "
                print(f"    [{status}] {provider}")
        else:
            print("\n  ⚠️  No API keys detected")
            print("  Set ANTHROPIC_API_KEY, OPENAI_API_KEY, or GOOGLE_API_KEY")

        print("-" * 60)
        return 0

    except ImportError:
        print("❌ Provider module not available")
        return 1
    except Exception as e:  # noqa: BLE001
        # INTENTIONAL: CLI commands should catch all errors and report gracefully
        logger.exception(f"Provider error: {e}")
        print(f"❌ Error: {e}")
        return 1


def cmd_provider_set(args: Namespace) -> int:
    """Set the LLM provider."""
    try:
        from empathy_os.models.provider_config import (
            ProviderMode,
            get_provider_config,
            set_provider_config,
        )

        # Get current config and update
        config = get_provider_config()

        if args.name == "hybrid":
            config.mode = ProviderMode.HYBRID
            print("✅ Provider mode set to: hybrid (multi-provider)")
        else:
            config.mode = ProviderMode.SINGLE
            config.primary_provider = args.name
            print(f"✅ Provider set to: {args.name}")

        set_provider_config(config)
        return 0

    except ImportError:
        print("❌ Provider module not available")
        return 1
    except Exception as e:  # noqa: BLE001
        # INTENTIONAL: CLI commands should catch all errors and report gracefully
        logger.exception(f"Provider error: {e}")
        print(f"❌ Error: {e}")
        return 1


# =============================================================================
# Utility Commands
# =============================================================================


def cmd_validate(args: Namespace) -> int:
    """Validate configuration."""
    print("\n🔍 Validating configuration...\n")

    errors = []
    warnings = []

    # Check config file
    config_paths = [
        Path("empathy.config.json"),
        Path("empathy.config.yml"),
        Path("empathy.config.yaml"),
    ]

    config_found = False
    for config_path in config_paths:
        if config_path.exists():
            config_found = True
            print(f"  ✅ Config file: {config_path}")
            break

    if not config_found:
        warnings.append("No empathy.config file found (using defaults)")

    # Check for API keys
    import os

    api_keys = {
        "ANTHROPIC_API_KEY": "Anthropic (Claude)",
        "OPENAI_API_KEY": "OpenAI (GPT)",
        "GOOGLE_API_KEY": "Google (Gemini)",
    }

    keys_found = 0
    for key, name in api_keys.items():
        if os.environ.get(key):
            print(f"  ✅ {name} API key set")
            keys_found += 1

    if keys_found == 0:
        errors.append(
            "No API keys found. Set at least one: ANTHROPIC_API_KEY, OPENAI_API_KEY, or GOOGLE_API_KEY"
        )

    # Check workflows directory
    try:
        from empathy_os.workflows import WORKFLOW_REGISTRY

        print(f"  ✅ {len(WORKFLOW_REGISTRY)} workflows registered")
    except ImportError as e:
        warnings.append(f"Could not load workflows: {e}")

    # Summary
    print("\n" + "-" * 60)

    if errors:
        print("\n❌ Validation failed:")
        for error in errors:
            print(f"   - {error}")
        return 1

    if warnings:
        print("\n⚠️  Warnings:")
        for warning in warnings:
            print(f"   - {warning}")

    print("\n✅ Configuration is valid")
    return 0


def cmd_version(args: Namespace) -> int:
    """Show version information."""
    version = get_version()
    print(f"empathy-framework {version}")

    if args.verbose:
        print(f"\nPython: {sys.version}")
        print(f"Platform: {sys.platform}")

        # Show installed extras
        try:
            from importlib.metadata import requires

            reqs = requires("empathy-framework") or []
            print(f"\nDependencies: {len(reqs)}")
        except Exception:  # noqa: BLE001
            pass

    return 0


# =============================================================================
# Main Entry Point
# =============================================================================


def create_parser() -> argparse.ArgumentParser:
    """Create the argument parser."""
    parser = argparse.ArgumentParser(
        prog="empathy",
        description="Empathy Framework CLI - AI-powered developer workflows",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
For interactive features, use Claude Code skills:
    /dev        Developer tools (debug, commit, PR, review)
    /testing    Run tests, coverage, benchmarks
    /docs       Documentation generation
    /release    Release preparation

Documentation: https://smartaimemory.com/framework-docs/
        """,
    )

    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Enable verbose output",
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # --- Workflow commands ---
    workflow_parser = subparsers.add_parser("workflow", help="Workflow management")
    workflow_sub = workflow_parser.add_subparsers(dest="workflow_command")

    # workflow list
    workflow_sub.add_parser("list", help="List available workflows")

    # workflow info
    info_parser = workflow_sub.add_parser("info", help="Show workflow details")
    info_parser.add_argument("name", help="Workflow name")

    # workflow run
    run_parser = workflow_sub.add_parser("run", help="Run a workflow")
    run_parser.add_argument("name", help="Workflow name")
    run_parser.add_argument("--input", "-i", help="JSON input data")
    run_parser.add_argument("--path", "-p", help="Target path")
    run_parser.add_argument("--target", "-t", help="Target value (e.g., coverage target)")
    run_parser.add_argument("--json", "-j", action="store_true", help="Output as JSON")

    # --- Telemetry commands ---
    telemetry_parser = subparsers.add_parser("telemetry", help="Usage telemetry")
    telemetry_sub = telemetry_parser.add_subparsers(dest="telemetry_command")

    # telemetry show
    show_parser = telemetry_sub.add_parser("show", help="Display usage summary")
    show_parser.add_argument(
        "--days", "-d", type=int, default=30, help="Number of days (default: 30)"
    )

    # telemetry savings
    savings_parser = telemetry_sub.add_parser("savings", help="Show cost savings")
    savings_parser.add_argument(
        "--days", "-d", type=int, default=30, help="Number of days (default: 30)"
    )

    # telemetry export
    export_parser = telemetry_sub.add_parser("export", help="Export telemetry data")
    export_parser.add_argument("--output", "-o", required=True, help="Output file path")
    export_parser.add_argument(
        "--format", "-f", choices=["csv", "json"], default="json", help="Output format"
    )
    export_parser.add_argument(
        "--days", "-d", type=int, default=30, help="Number of days (default: 30)"
    )

    # --- Provider commands ---
    provider_parser = subparsers.add_parser("provider", help="LLM provider configuration")
    provider_sub = provider_parser.add_subparsers(dest="provider_command")

    # provider show
    provider_sub.add_parser("show", help="Show current provider")

    # provider set
    set_parser = provider_sub.add_parser("set", help="Set provider")
    set_parser.add_argument("name", choices=["anthropic", "openai", "hybrid"], help="Provider name")

    # --- Utility commands ---
    subparsers.add_parser("validate", help="Validate configuration")

    version_parser = subparsers.add_parser("version", help="Show version")
    version_parser.add_argument("-v", "--verbose", action="store_true", help="Show detailed info")

    return parser


def main(argv: list[str] | None = None) -> int:
    """Main entry point."""
    parser = create_parser()
    args = parser.parse_args(argv)

    # Configure logging
    if args.verbose:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.WARNING)

    # Route to command handlers
    if args.command == "workflow":
        if args.workflow_command == "list":
            return cmd_workflow_list(args)
        elif args.workflow_command == "info":
            return cmd_workflow_info(args)
        elif args.workflow_command == "run":
            return cmd_workflow_run(args)
        else:
            print("Usage: empathy workflow {list|info|run}")
            return 1

    elif args.command == "telemetry":
        if args.telemetry_command == "show":
            return cmd_telemetry_show(args)
        elif args.telemetry_command == "savings":
            return cmd_telemetry_savings(args)
        elif args.telemetry_command == "export":
            return cmd_telemetry_export(args)
        else:
            print("Usage: empathy telemetry {show|savings|export}")
            return 1

    elif args.command == "provider":
        if args.provider_command == "show":
            return cmd_provider_show(args)
        elif args.provider_command == "set":
            return cmd_provider_set(args)
        else:
            print("Usage: empathy provider {show|set}")
            return 1

    elif args.command == "validate":
        return cmd_validate(args)

    elif args.command == "version":
        return cmd_version(args)

    else:
        parser.print_help()
        return 0


if __name__ == "__main__":
    sys.exit(main())
