#!/usr/bin/env python3
"""
Document Generation Runner

Generates documentation from code automatically.
Uses attune-ai package if installed, otherwise falls back to bundled core.
"""

import argparse
import asyncio
import sys
from pathlib import Path


def get_workflow():
    """Get the DocumentGenWorkflow, preferring installed package."""
    try:
        from attune.workflows import DocumentGenWorkflow
        return DocumentGenWorkflow()
    except ImportError:
        try:
            from ...core.workflows import DocumentGenWorkflow
            return DocumentGenWorkflow()
        except ImportError:
            print("Error: attune-ai not installed and bundled core not found.")
            print("Install with: pip install attune-ai")
            sys.exit(1)


async def main():
    parser = argparse.ArgumentParser(
        description="Generate documentation from code",
        epilog="For more info: https://attune-ai.org/docs/document-gen"
    )
    parser.add_argument(
        "--path", "-p",
        type=str,
        default=".",
        help="Path to document"
    )
    parser.add_argument(
        "--output", "-o",
        type=str,
        default="./docs",
        help="Output directory"
    )
    parser.add_argument(
        "--type",
        type=str,
        nargs="+",
        choices=["api", "readme", "architecture", "tutorial"],
        default=["api"],
        help="Documentation types to generate"
    )
    parser.add_argument(
        "--format",
        type=str,
        choices=["markdown", "rst", "html"],
        default="markdown",
        help="Output format"
    )

    args = parser.parse_args()

    target_path = Path(args.path)
    if not target_path.exists():
        print(f"Error: Path '{args.path}' does not exist")
        sys.exit(1)

    workflow = get_workflow()

    print(f"📚 Generating documentation for: {target_path}")
    print(f"   Types: {', '.join(args.type)}")
    print(f"   Output: {args.output}")
    print("-" * 50)

    try:
        result = await workflow.execute(
            target_path=str(target_path),
            output_dir=args.output,
            doc_types=args.type,
            format=args.format
        )

        print(f"\n✓ Generated {len(result.files)} documentation files")
        for f in result.files:
            print(f"  - {f}")

    except Exception as e:
        print(f"Error generating documentation: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
