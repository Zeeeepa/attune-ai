#!/usr/bin/env python3
"""
PR Review Runner

Analyzes pull requests with diff analysis and actionable feedback.
Uses attune-ai package if installed, otherwise falls back to bundled core.
"""

import argparse
import asyncio
import sys


def get_workflow():
    """Get the PRReviewWorkflow, preferring installed package."""
    try:
        from attune.workflows import PRReviewWorkflow
        return PRReviewWorkflow()
    except ImportError:
        try:
            from ...core.workflows import PRReviewWorkflow
            return PRReviewWorkflow()
        except ImportError:
            print("Error: attune-ai not installed and bundled core not found.")
            print("Install with: pip install attune-ai")
            sys.exit(1)


async def main():
    parser = argparse.ArgumentParser(
        description="Review a pull request",
        epilog="For more info: https://attune-ai.org/docs/pr-review"
    )
    parser.add_argument(
        "--pr", "-p",
        type=int,
        required=True,
        help="PR number to review"
    )
    parser.add_argument(
        "--repo", "-r",
        type=str,
        help="Repository (owner/repo format)"
    )
    parser.add_argument(
        "--output", "-o",
        type=str,
        help="Output file for review"
    )
    parser.add_argument(
        "--format",
        type=str,
        choices=["json", "text", "markdown", "github"],
        default="markdown",
        help="Output format"
    )

    args = parser.parse_args()

    workflow = get_workflow()

    print(f"📋 Reviewing PR #{args.pr}")
    if args.repo:
        print(f"   Repository: {args.repo}")
    print("-" * 50)

    try:
        result = await workflow.execute(
            pr_number=args.pr,
            repo=args.repo
        )

        if args.output:
            import json
            with open(args.output, "w") as f:
                if args.format == "json":
                    json.dump(result.to_dict(), f, indent=2)
                else:
                    f.write(result.format(args.format))
            print(f"Review saved to: {args.output}")
        else:
            print(result.format(args.format))

    except Exception as e:
        print(f"Error reviewing PR: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
