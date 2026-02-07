"""Workflow CLI commands.

Commands for listing, inspecting, and running workflows.

Copyright 2026 Smart-AI-Memory
Licensed under Apache 2.0
"""

from __future__ import annotations

import json
import logging
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from argparse import Namespace

logger = logging.getLogger(__name__)


def cmd_workflow_list(args: Namespace) -> int:
    """List available workflows."""
    from attune.workflows import discover_workflows

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
    print("\nRun a workflow: attune workflow run <name>")
    return 0


def cmd_workflow_info(args: Namespace) -> int:
    """Show workflow details."""
    from attune.workflows import discover_workflows

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

    from attune.config import _validate_file_path
    from attune.workflows import discover_workflows

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
