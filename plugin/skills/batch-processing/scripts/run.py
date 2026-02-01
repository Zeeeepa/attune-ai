#!/usr/bin/env python3
"""
Batch Processing Runner

Process multiple requests via Anthropic Batch API for 50% cost savings.
Uses attune-ai package if installed, otherwise falls back to bundled core.
"""

import argparse
import asyncio
import sys
import json
from pathlib import Path


def get_workflow():
    """Get the BatchProcessingWorkflow, preferring installed package."""
    try:
        from attune.workflows import BatchProcessingWorkflow
        return BatchProcessingWorkflow()
    except ImportError:
        try:
            from ...core.workflows import BatchProcessingWorkflow
            return BatchProcessingWorkflow()
        except ImportError:
            print("Error: attune-ai not installed and bundled core not found.")
            print("Install with: pip install attune-ai")
            sys.exit(1)


async def main():
    parser = argparse.ArgumentParser(
        description="Batch processing for 50% cost savings",
        epilog="For more info: https://attune-ai.org/docs/batch-processing"
    )

    subparsers = parser.add_subparsers(dest="command", required=True)

    # Submit command
    submit_parser = subparsers.add_parser("submit", help="Submit a batch job")
    submit_parser.add_argument(
        "--input", "-i",
        type=str,
        required=True,
        help="Input JSON file with requests"
    )

    # Status command
    status_parser = subparsers.add_parser("status", help="Check batch status")
    status_parser.add_argument(
        "--batch-id", "-b",
        type=str,
        required=True,
        help="Batch ID to check"
    )

    # Results command
    results_parser = subparsers.add_parser("results", help="Get batch results")
    results_parser.add_argument(
        "--batch-id", "-b",
        type=str,
        required=True,
        help="Batch ID to get results for"
    )
    results_parser.add_argument(
        "--output", "-o",
        type=str,
        required=True,
        help="Output file for results"
    )

    args = parser.parse_args()

    workflow = get_workflow()

    try:
        if args.command == "submit":
            input_path = Path(args.input)
            if not input_path.exists():
                print(f"Error: Input file '{args.input}' not found")
                sys.exit(1)

            with open(input_path) as f:
                requests = json.load(f)

            print(f"📤 Submitting {len(requests)} requests to batch API...")
            batch_id = await workflow.submit(requests)
            print(f"✓ Batch submitted: {batch_id}")
            print(f"\nCheck status with: python run.py status --batch-id {batch_id}")

        elif args.command == "status":
            print(f"📊 Checking batch status: {args.batch_id}")
            status = await workflow.get_status(args.batch_id)
            print(f"Status: {status.state}")
            print(f"Progress: {status.completed}/{status.total}")
            if status.state == "completed":
                print(f"\nGet results with: python run.py results --batch-id {args.batch_id} -o output.json")

        elif args.command == "results":
            print(f"📥 Downloading results: {args.batch_id}")
            results = await workflow.get_results(args.batch_id)

            with open(args.output, "w") as f:
                json.dump(results, f, indent=2)
            print(f"✓ Results saved to: {args.output}")
            print(f"   {len(results)} responses retrieved")

    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
