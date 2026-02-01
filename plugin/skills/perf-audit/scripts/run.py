#!/usr/bin/env python3
"""
Performance Audit Runner

Analyzes code for performance issues and bottlenecks.
Uses attune-ai package if installed, otherwise falls back to bundled core.
"""

import argparse
import asyncio
import sys
from pathlib import Path


def get_workflow():
    """Get the PerfAuditWorkflow, preferring installed package."""
    try:
        from attune.workflows import PerfAuditWorkflow
        return PerfAuditWorkflow()
    except ImportError:
        try:
            from ...core.workflows import PerfAuditWorkflow
            return PerfAuditWorkflow()
        except ImportError:
            print("Error: attune-ai not installed and bundled core not found.")
            print("Install with: pip install attune-ai")
            sys.exit(1)


async def main():
    parser = argparse.ArgumentParser(
        description="Audit code for performance issues",
        epilog="For more info: https://attune-ai.org/docs/perf-audit"
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
        "--focus",
        type=str,
        nargs="+",
        choices=["algorithm", "memory", "io", "database", "caching"],
        help="Focus areas"
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

    print(f"⚡ Running performance audit on: {target_path}")
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
        print(f"Error running performance audit: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
