#!/usr/bin/env python3
"""
Dependency Check Runner

Analyzes project dependencies for security and health.
Uses attune-ai package if installed, otherwise falls back to bundled core.
"""

import argparse
import asyncio
import sys
from pathlib import Path


def get_workflow():
    """Get the DependencyCheckWorkflow, preferring installed package."""
    try:
        from attune.workflows import DependencyCheckWorkflow
        return DependencyCheckWorkflow()
    except ImportError:
        try:
            from ...core.workflows import DependencyCheckWorkflow
            return DependencyCheckWorkflow()
        except ImportError:
            print("Error: attune-ai not installed and bundled core not found.")
            print("Install with: pip install attune-ai")
            sys.exit(1)


async def main():
    parser = argparse.ArgumentParser(
        description="Check dependencies for security and health",
        epilog="For more info: https://attune-ai.org/docs/dependency-check"
    )
    parser.add_argument(
        "--path", "-p",
        type=str,
        default=".",
        help="Project path"
    )
    parser.add_argument(
        "--output", "-o",
        type=str,
        help="Output file for report"
    )
    parser.add_argument(
        "--check-licenses",
        action="store_true",
        help="Include license compatibility check"
    )
    parser.add_argument(
        "--check-outdated",
        action="store_true",
        default=True,
        help="Check for outdated packages"
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

    print(f"📦 Checking dependencies in: {target_path}")
    print("-" * 50)

    try:
        result = await workflow.execute(
            project_path=str(target_path),
            check_licenses=args.check_licenses,
            check_outdated=args.check_outdated
        )

        if args.output:
            import json
            with open(args.output, "w") as f:
                json.dump(result.to_dict(), f, indent=2)
            print(f"Report saved to: {args.output}")
        else:
            print(result.format(args.format))

        if result.has_vulnerabilities:
            print("\n⚠️  Vulnerabilities found!")
            sys.exit(1)

    except Exception as e:
        print(f"Error checking dependencies: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
