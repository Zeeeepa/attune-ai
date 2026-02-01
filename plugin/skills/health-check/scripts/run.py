#!/usr/bin/env python3
"""
Health Check Runner

Multi-agent parallel project health assessment.
Uses attune-ai package if installed, otherwise falls back to bundled core.
"""

import argparse
import asyncio
import sys
from pathlib import Path


def get_orchestrator():
    """Get the HealthCheckOrchestrator, preferring installed package."""
    try:
        from attune.orchestration import HealthCheckOrchestrator
        return HealthCheckOrchestrator()
    except ImportError:
        try:
            from ...core.orchestration import HealthCheckOrchestrator
            return HealthCheckOrchestrator()
        except ImportError:
            print("Error: attune-ai not installed and bundled core not found.")
            print("Install with: pip install attune-ai")
            sys.exit(1)


async def main():
    parser = argparse.ArgumentParser(
        description="Run comprehensive project health check",
        epilog="For more info: https://attune-ai.org/docs/health-check"
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
        "--skip",
        type=str,
        nargs="+",
        choices=["security", "tests", "docs", "quality", "deps", "perf"],
        help="Checks to skip"
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

    orchestrator = get_orchestrator()

    print(f"🏥 Running health check on: {target_path}")
    print("   Running 6 agents in parallel...")
    print("-" * 50)

    try:
        result = await orchestrator.execute(
            project_path=str(target_path),
            skip_checks=args.skip or []
        )

        if args.output:
            import json
            with open(args.output, "w") as f:
                if args.format == "json":
                    json.dump(result.to_dict(), f, indent=2)
                else:
                    f.write(result.format(args.format))
            print(f"Report saved to: {args.output}")
        else:
            print(result.format(args.format))

        print("\n" + "=" * 50)
        print(f"Health Score: {result.health_score}/100")

        if result.health_score >= 80:
            print("✅ Project is healthy!")
        elif result.health_score >= 60:
            print("⚠️  Project needs attention")
        else:
            print("❌ Project has significant issues")
            sys.exit(1)

    except Exception as e:
        print(f"Error running health check: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
