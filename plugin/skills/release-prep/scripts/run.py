#!/usr/bin/env python3
"""
Release Preparation Runner

Multi-agent release readiness verification.
Uses attune-ai package if installed, otherwise falls back to bundled core.
"""

import argparse
import asyncio
import sys
from pathlib import Path


def get_orchestrator():
    """Get the ReleasePrepOrchestrator, preferring installed package."""
    try:
        from attune.orchestration import ReleasePrepOrchestrator
        return ReleasePrepOrchestrator()
    except ImportError:
        try:
            from ...core.orchestration import ReleasePrepOrchestrator
            return ReleasePrepOrchestrator()
        except ImportError:
            print("Error: attune-ai not installed and bundled core not found.")
            print("Install with: pip install attune-ai")
            sys.exit(1)


async def main():
    parser = argparse.ArgumentParser(
        description="Prepare and verify release readiness",
        epilog="For more info: https://attune-ai.org/docs/release-prep"
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
        "--version",
        type=str,
        help="Version to release (auto-detected if not specified)"
    )
    parser.add_argument(
        "--skip",
        type=str,
        nargs="+",
        choices=["security", "tests", "docs", "quality"],
        help="Checks to skip"
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

    orchestrator = get_orchestrator()

    print(f"🚀 Running release preparation for: {target_path}")
    if args.version:
        print(f"   Target version: {args.version}")
    print("-" * 50)

    try:
        result = await orchestrator.execute(
            project_path=str(target_path),
            version=args.version,
            skip_checks=args.skip or []
        )

        if args.output:
            import json
            with open(args.output, "w") as f:
                json.dump(result.to_dict(), f, indent=2)
            print(f"Report saved to: {args.output}")
        else:
            print(result.format(args.format))

        # Print summary
        print("\n" + "=" * 50)
        if result.ready_for_release:
            print("✅ READY FOR RELEASE")
        else:
            print("❌ NOT READY - See blocking issues above")
            sys.exit(1)

    except Exception as e:
        print(f"Error running release prep: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
