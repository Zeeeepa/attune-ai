#!/usr/bin/env python3
"""
Test Coverage Runner

Analyzes and improves test coverage.
Uses attune-ai package if installed, otherwise falls back to bundled core.
"""

import argparse
import asyncio
import sys
from pathlib import Path


def get_workflow():
    """Get the TestCoverageWorkflow, preferring installed package."""
    try:
        from attune.workflows import TestCoverageWorkflow
        return TestCoverageWorkflow()
    except ImportError:
        try:
            from ...core.workflows import TestCoverageWorkflow
            return TestCoverageWorkflow()
        except ImportError:
            print("Error: attune-ai not installed and bundled core not found.")
            print("Install with: pip install attune-ai")
            sys.exit(1)


async def main():
    parser = argparse.ArgumentParser(
        description="Analyze and improve test coverage",
        epilog="For more info: https://attune-ai.org/docs/test-coverage"
    )
    parser.add_argument(
        "--path", "-p",
        type=str,
        default=".",
        help="Project path"
    )
    parser.add_argument(
        "--target", "-t",
        type=int,
        default=80,
        help="Coverage target percentage"
    )
    parser.add_argument(
        "--output", "-o",
        type=str,
        help="Output directory for generated tests"
    )
    parser.add_argument(
        "--generate",
        action="store_true",
        help="Generate tests to fill gaps"
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

    print(f"📊 Analyzing test coverage: {target_path}")
    print(f"   Target: {args.target}%")
    print("-" * 50)

    try:
        result = await workflow.execute(
            project_path=str(target_path),
            coverage_target=args.target,
            generate_missing=args.generate
        )

        print(result.format(args.format))

        if args.generate and result.generated_tests:
            output_dir = Path(args.output) if args.output else target_path / "tests"
            output_dir.mkdir(parents=True, exist_ok=True)

            for test_file in result.generated_tests:
                output_path = output_dir / test_file.name
                output_path.write_text(test_file.content)
                print(f"✓ Generated: {output_path}")

        if result.current_coverage < args.target:
            print(f"\n⚠️  Coverage {result.current_coverage}% below target {args.target}%")
            sys.exit(1)

    except Exception as e:
        print(f"Error analyzing coverage: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
