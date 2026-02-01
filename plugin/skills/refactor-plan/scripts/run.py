#!/usr/bin/env python3
"""
Refactor Plan Runner

Analyzes code and generates refactoring roadmaps.
Uses attune-ai package if installed, otherwise falls back to bundled core.
"""

import argparse
import asyncio
import sys
from pathlib import Path


def get_workflow():
    """Get the RefactorPlanWorkflow, preferring installed package."""
    try:
        from attune.workflows import RefactorPlanWorkflow
        return RefactorPlanWorkflow()
    except ImportError:
        try:
            from ...core.workflows import RefactorPlanWorkflow
            return RefactorPlanWorkflow()
        except ImportError:
            print("Error: attune-ai not installed and bundled core not found.")
            print("Install with: pip install attune-ai")
            sys.exit(1)


async def main():
    parser = argparse.ArgumentParser(
        description="Generate refactoring plan for code",
        epilog="For more info: https://attune-ai.org/docs/refactor-plan"
    )
    parser.add_argument(
        "--path", "-p",
        type=str,
        default=".",
        help="Path to analyze"
    )
    parser.add_argument(
        "--output", "-o",
        type=str,
        help="Output file for plan"
    )
    parser.add_argument(
        "--focus",
        type=str,
        nargs="+",
        choices=["complexity", "duplication", "coupling", "naming", "all"],
        default=["all"],
        help="Focus areas"
    )
    parser.add_argument(
        "--format",
        type=str,
        choices=["json", "text", "markdown"],
        default="markdown",
        help="Output format"
    )

    args = parser.parse_args()

    target_path = Path(args.path)
    if not target_path.exists():
        print(f"Error: Path '{args.path}' does not exist")
        sys.exit(1)

    workflow = get_workflow()

    print(f"🔧 Analyzing for refactoring: {target_path}")
    print("-" * 50)

    try:
        result = await workflow.execute(
            target_path=str(target_path),
            focus_areas=args.focus
        )

        if args.output:
            with open(args.output, "w") as f:
                f.write(result.format(args.format))
            print(f"Plan saved to: {args.output}")
        else:
            print(result.format(args.format))

    except Exception as e:
        print(f"Error generating refactor plan: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
