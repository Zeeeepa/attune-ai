#!/usr/bin/env python3
"""
Code Review Runner

Runs automated code review on files or directories.
Uses attune-ai package if installed, otherwise falls back to bundled core.
"""

import argparse
import asyncio
import sys
from pathlib import Path


def get_workflow():
    """Get the CodeReviewWorkflow, preferring installed package."""
    try:
        from attune.workflows import CodeReviewWorkflow
        return CodeReviewWorkflow()
    except ImportError:
        try:
            from ...core.workflows import CodeReviewWorkflow
            return CodeReviewWorkflow()
        except ImportError:
            print("Error: attune-ai not installed and bundled core not found.")
            print("Install with: pip install attune-ai")
            sys.exit(1)


async def main():
    parser = argparse.ArgumentParser(
        description="Run automated code review",
        epilog="For more info: https://attune-ai.org/docs/code-review"
    )
    parser.add_argument(
        "--path", "-p",
        type=str,
        default=".",
        help="Path to review (file or directory)"
    )
    parser.add_argument(
        "--output", "-o",
        type=str,
        help="Output file for results"
    )
    parser.add_argument(
        "--focus",
        type=str,
        nargs="+",
        choices=["style", "logic", "performance", "security", "maintainability"],
        help="Focus areas for review"
    )
    parser.add_argument(
        "--format",
        type=str,
        choices=["json", "text", "markdown", "github"],
        default="text",
        help="Output format"
    )

    args = parser.parse_args()

    target_path = Path(args.path)
    if not target_path.exists():
        print(f"Error: Path '{args.path}' does not exist")
        sys.exit(1)

    workflow = get_workflow()

    print(f"📝 Running code review on: {target_path}")
    print("-" * 50)

    try:
        result = await workflow.execute(
            target_path=str(target_path),
            focus_areas=args.focus
        )

        if args.output:
            import json
            with open(args.output, "w") as f:
                json.dump(result.to_dict(), f, indent=2)
            print(f"Results saved to: {args.output}")
        else:
            print(result.format(args.format))

    except Exception as e:
        print(f"Error running code review: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
