#!/usr/bin/env python3
"""
Bug Prediction Runner

Predicts potential bugs using code analysis and patterns.
Uses attune-ai package if installed, otherwise falls back to bundled core.
"""

import argparse
import asyncio
import sys
from pathlib import Path


def get_workflow():
    """Get the BugPredictWorkflow, preferring installed package."""
    try:
        from attune.workflows import BugPredictWorkflow
        return BugPredictWorkflow()
    except ImportError:
        try:
            from ...core.workflows import BugPredictWorkflow
            return BugPredictWorkflow()
        except ImportError:
            print("Error: attune-ai not installed and bundled core not found.")
            print("Install with: pip install attune-ai")
            sys.exit(1)


async def main():
    parser = argparse.ArgumentParser(
        description="Predict potential bugs in code",
        epilog="For more info: https://attune-ai.org/docs/bug-predict"
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
        help="Output file for results"
    )
    parser.add_argument(
        "--threshold",
        type=float,
        default=0.7,
        help="Confidence threshold (0-1)"
    )
    parser.add_argument(
        "--format",
        type=str,
        choices=["json", "text", "markdown"],
        default="text",
        help="Output format"
    )

    args = parser.parse_args()

    target_path = Path(args.path)
    if not target_path.exists():
        print(f"Error: Path '{args.path}' does not exist")
        sys.exit(1)

    workflow = get_workflow()

    print(f"🐛 Predicting bugs in: {target_path}")
    print("-" * 50)

    try:
        result = await workflow.execute(
            target_path=str(target_path),
            confidence_threshold=args.threshold
        )

        if args.output:
            import json
            with open(args.output, "w") as f:
                json.dump(result.to_dict(), f, indent=2)
            print(f"Results saved to: {args.output}")
        else:
            print(result.format(args.format))

    except Exception as e:
        print(f"Error predicting bugs: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
