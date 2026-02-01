#!/usr/bin/env python3
"""
Research Synthesis Runner

Research and synthesize information from multiple sources.
Uses attune-ai package if installed, otherwise falls back to bundled core.
"""

import argparse
import asyncio
import sys
from pathlib import Path


def get_workflow():
    """Get the ResearchSynthesisWorkflow, preferring installed package."""
    try:
        from attune.workflows import ResearchSynthesisWorkflow
        return ResearchSynthesisWorkflow()
    except ImportError:
        try:
            from ...core.workflows import ResearchSynthesisWorkflow
            return ResearchSynthesisWorkflow()
        except ImportError:
            print("Error: attune-ai not installed and bundled core not found.")
            print("Install with: pip install attune-ai")
            sys.exit(1)


async def main():
    parser = argparse.ArgumentParser(
        description="Research and synthesize information",
        epilog="For more info: https://attune-ai.org/docs/research-synthesis"
    )
    parser.add_argument(
        "--topic", "-t",
        type=str,
        required=True,
        help="Topic to research"
    )
    parser.add_argument(
        "--sources", "-s",
        type=str,
        nargs="+",
        default=["."],
        help="Source paths to analyze"
    )
    parser.add_argument(
        "--output", "-o",
        type=str,
        help="Output file for report"
    )
    parser.add_argument(
        "--depth",
        type=str,
        choices=["quick", "standard", "deep"],
        default="standard",
        help="Research depth"
    )
    parser.add_argument(
        "--format",
        type=str,
        choices=["json", "text", "markdown"],
        default="markdown",
        help="Output format"
    )

    args = parser.parse_args()

    # Validate source paths
    for source in args.sources:
        if not Path(source).exists():
            print(f"Warning: Source '{source}' not found, skipping")

    workflow = get_workflow()

    print(f"🔬 Researching: {args.topic}")
    print(f"   Depth: {args.depth}")
    print(f"   Sources: {', '.join(args.sources)}")
    print("-" * 50)

    try:
        result = await workflow.execute(
            topic=args.topic,
            sources=args.sources,
            depth=args.depth
        )

        if args.output:
            with open(args.output, "w") as f:
                f.write(result.format(args.format))
            print(f"Report saved to: {args.output}")
        else:
            print(result.format(args.format))

    except Exception as e:
        print(f"Error during research: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
