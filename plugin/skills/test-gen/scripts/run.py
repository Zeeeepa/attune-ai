#!/usr/bin/env python3
"""
Test Generation Runner

Generates unit tests for Python/JavaScript code.
Uses attune-ai package if installed, otherwise falls back to bundled core.
"""

import argparse
import asyncio
import sys
from pathlib import Path


def get_workflow():
    """Get the TestGenWorkflow, preferring installed package."""
    try:
        from attune.workflows import TestGenWorkflow
        return TestGenWorkflow()
    except ImportError:
        try:
            from ...core.workflows import TestGenWorkflow
            return TestGenWorkflow()
        except ImportError:
            print("Error: attune-ai not installed and bundled core not found.")
            print("Install with: pip install attune-ai")
            sys.exit(1)


async def main():
    parser = argparse.ArgumentParser(
        description="Generate tests for code",
        epilog="For more info: https://attune-ai.org/docs/test-gen"
    )
    parser.add_argument(
        "--path", "-p",
        type=str,
        required=True,
        help="Path to file or module to generate tests for"
    )
    parser.add_argument(
        "--output", "-o",
        type=str,
        help="Output directory for generated tests"
    )
    parser.add_argument(
        "--framework",
        type=str,
        choices=["pytest", "unittest", "jest", "mocha"],
        default="pytest",
        help="Test framework to use"
    )
    parser.add_argument(
        "--coverage-target",
        type=int,
        default=80,
        help="Target coverage percentage"
    )
    parser.add_argument(
        "--include-edge-cases",
        action="store_true",
        help="Generate edge case tests"
    )

    args = parser.parse_args()

    target_path = Path(args.path)
    if not target_path.exists():
        print(f"Error: Path '{args.path}' does not exist")
        sys.exit(1)

    workflow = get_workflow()

    print(f"🧪 Generating tests for: {target_path}")
    print(f"   Framework: {args.framework}")
    print(f"   Coverage target: {args.coverage_target}%")
    print("-" * 50)

    try:
        result = await workflow.execute(
            target_path=str(target_path),
            framework=args.framework,
            coverage_target=args.coverage_target,
            include_edge_cases=args.include_edge_cases
        )

        output_dir = Path(args.output) if args.output else target_path.parent / "tests"
        output_dir.mkdir(parents=True, exist_ok=True)

        for test_file in result.generated_tests:
            output_path = output_dir / test_file.name
            output_path.write_text(test_file.content)
            print(f"✓ Generated: {output_path}")

        print(f"\n{len(result.generated_tests)} test files generated")
        print(f"Estimated coverage: {result.estimated_coverage}%")

    except Exception as e:
        print(f"Error generating tests: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
