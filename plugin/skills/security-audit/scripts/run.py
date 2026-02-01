#!/usr/bin/env python3
"""
Security Audit Runner

Runs security vulnerability scanning on a codebase.
Uses attune-ai package if installed, otherwise falls back to bundled core.
"""

import argparse
import asyncio
import sys
from pathlib import Path


def get_workflow():
    """Get the SecurityAuditWorkflow, preferring installed package."""
    try:
        from attune.workflows import SecurityAuditWorkflow
        return SecurityAuditWorkflow()
    except ImportError:
        # Fall back to bundled core
        try:
            from ...core.workflows import SecurityAuditWorkflow
            return SecurityAuditWorkflow()
        except ImportError:
            print("Error: attune-ai not installed and bundled core not found.")
            print("Install with: pip install attune-ai")
            sys.exit(1)


async def main():
    parser = argparse.ArgumentParser(
        description="Run security audit on codebase",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python run.py --path ./src
  python run.py --path ./src --output report.json
  python run.py --path ./src --severity high

For more info: https://attune-ai.org/docs/security-audit
        """
    )
    parser.add_argument(
        "--path", "-p",
        type=str,
        default=".",
        help="Path to scan (default: current directory)"
    )
    parser.add_argument(
        "--output", "-o",
        type=str,
        help="Output file for results (JSON format)"
    )
    parser.add_argument(
        "--severity",
        type=str,
        choices=["low", "medium", "high", "critical"],
        default="low",
        help="Minimum severity to report (default: low)"
    )
    parser.add_argument(
        "--format",
        type=str,
        choices=["json", "text", "markdown"],
        default="text",
        help="Output format (default: text)"
    )

    args = parser.parse_args()

    # Validate path
    target_path = Path(args.path)
    if not target_path.exists():
        print(f"Error: Path '{args.path}' does not exist")
        sys.exit(1)

    # Run workflow
    workflow = get_workflow()

    print(f"🔒 Running security audit on: {target_path}")
    print("-" * 50)

    try:
        result = await workflow.execute(
            target_path=str(target_path),
            min_severity=args.severity
        )

        # Output results
        if args.output:
            import json
            with open(args.output, "w") as f:
                json.dump(result.to_dict(), f, indent=2)
            print(f"Results saved to: {args.output}")
        else:
            print(result.format(args.format))

        # Exit with error if critical findings
        if result.has_critical:
            sys.exit(1)

    except Exception as e:
        print(f"Error running security audit: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
