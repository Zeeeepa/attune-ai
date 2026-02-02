#!/usr/bin/env python3
"""Check progress on batch 10 test coverage.

This script runs tests for batch 10 and reports coverage progress.

Usage:
    python scripts/check_batch10_progress.py
    python scripts/check_batch10_progress.py --detailed
"""

import subprocess
import sys
import json
from pathlib import Path
import argparse


def run_coverage(test_path: Path, detailed: bool = False) -> dict:
    """Run pytest with coverage and return results.

    Args:
        test_path: Path to test directory
        detailed: If True, show detailed coverage report

    Returns:
        Coverage results dictionary
    """
    cmd = [
        "pytest",
        str(test_path),
        "--cov=src",
        "--cov-report=term-missing" if detailed else "--cov-report=term",
        "--cov-report=json",
        "-q",  # Quiet mode
    ]

    try:
        result = subprocess.run(
            cmd,
            cwd=Path(__file__).parent.parent,
            capture_output=True,
            text=True,
        )

        # Load coverage JSON
        coverage_file = Path(".coverage.json")
        if coverage_file.exists():
            with coverage_file.open() as f:
                return json.load(f)
        else:
            return {}

    except subprocess.CalledProcessError as e:
        print(f"Error running coverage: {e}", file=sys.stderr)
        return {}


def load_batch_10_modules() -> list[dict]:
    """Load batch 10 modules from batches file.

    Returns:
        List of module dictionaries
    """
    batches_file = Path("/tmp/coverage_batches.json")

    if not batches_file.exists():
        return []

    with batches_file.open() as f:
        batches = json.load(f)

    batch_10 = batches.get("batch_10", {})
    return batch_10.get("modules", [])


def calculate_coverage_stats(modules: list[dict], coverage_data: dict) -> dict:
    """Calculate coverage statistics for batch 10 modules.

    Args:
        modules: List of module info dicts
        coverage_data: Coverage data from pytest

    Returns:
        Statistics dictionary
    """
    stats = {
        "total_modules": len(modules),
        "modules_tested": 0,
        "total_lines": 0,
        "covered_lines": 0,
        "target_lines": 0,
        "modules_at_80_percent": 0,
        "modules_below_80_percent": 0,
    }

    if not coverage_data or "files" not in coverage_data:
        return stats

    files_data = coverage_data["files"]

    for module_info in modules:
        module_path = module_info["module"]
        uncovered = module_info["uncovered_lines"]
        stats["target_lines"] += uncovered

        # Check if module has coverage data
        if module_path in files_data:
            file_data = files_data[module_path]
            total = file_data.get("summary", {}).get("num_statements", 0)
            covered = file_data.get("summary", {}).get("covered_lines", 0)

            stats["total_lines"] += total
            stats["covered_lines"] += covered
            stats["modules_tested"] += 1

            # Calculate coverage percentage
            if total > 0:
                coverage_pct = (covered / total) * 100
                if coverage_pct >= 80:
                    stats["modules_at_80_percent"] += 1
                else:
                    stats["modules_below_80_percent"] += 1

    return stats


def print_progress_report(stats: dict, detailed: bool = False):
    """Print progress report.

    Args:
        stats: Statistics dictionary
        detailed: If True, print detailed breakdown
    """
    print()
    print("=" * 70)
    print("BATCH 10 TEST COVERAGE PROGRESS")
    print("=" * 70)
    print()

    # Overall progress
    print("Overall Progress:")
    print(f"  Modules in Batch: {stats['total_modules']}")
    print(f"  Modules Tested: {stats['modules_tested']}")
    print(f"  Modules Not Started: {stats['total_modules'] - stats['modules_tested']}")
    print()

    # Coverage statistics
    if stats["total_lines"] > 0:
        overall_pct = (stats["covered_lines"] / stats["total_lines"]) * 100
        print("Coverage Statistics:")
        print(f"  Total Lines: {stats['total_lines']:,}")
        print(f"  Covered Lines: {stats['covered_lines']:,}")
        print(f"  Overall Coverage: {overall_pct:.1f}%")
        print()

    # Goal progress
    print("Goal Progress (80%+ per module):")
    print(f"  ✅ At Goal (≥80%): {stats['modules_at_80_percent']}")
    print(f"  ⚠️  Below Goal (<80%): {stats['modules_below_80_percent']}")
    print()

    # Progress bar
    if stats["total_modules"] > 0:
        completed_pct = (stats["modules_at_80_percent"] / stats["total_modules"]) * 100
        bar_width = 50
        filled = int((completed_pct / 100) * bar_width)
        bar = "█" * filled + "░" * (bar_width - filled)
        print(f"Progress: [{bar}] {completed_pct:.1f}%")
        print()

    # Next steps
    if stats["modules_below_80_percent"] > 0:
        print("Next Steps:")
        print("  1. Focus on modules below 80% coverage")
        print("  2. Review uncovered lines in coverage report")
        print("  3. Add tests targeting those specific lines")
        print()
        print("Run with --detailed flag to see which lines are missing")
    elif stats["modules_at_80_percent"] == stats["total_modules"]:
        print("🎉 All modules have reached 80%+ coverage!")
        print("   Great work!")
    else:
        print("Next Steps:")
        print("  1. Generate tests: python scripts/generate_batch10_tests.py")
        print("  2. Complete TODO items in generated test files")
        print("  3. Run tests and check coverage")

    print()


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Check batch 10 test coverage progress")
    parser.add_argument(
        "--detailed",
        action="store_true",
        help="Show detailed coverage report with missing lines",
    )
    args = parser.parse_args()

    # Paths
    test_path = Path(__file__).parent.parent / "tests" / "behavioral" / "generated" / "batch10"

    # Check if test directory exists
    if not test_path.exists():
        print(f"Error: Test directory not found: {test_path}", file=sys.stderr)
        print("\nRun: python scripts/generate_batch10_tests.py", file=sys.stderr)
        return 1

    # Check if any test files exist
    test_files = list(test_path.glob("test_*.py"))
    if not test_files:
        print(f"Error: No test files found in {test_path}", file=sys.stderr)
        print("\nRun: python scripts/generate_batch10_tests.py", file=sys.stderr)
        return 1

    # Load batch 10 modules
    print("Loading batch 10 configuration...")
    modules = load_batch_10_modules()

    if not modules:
        print("Warning: Could not load batch 10 modules", file=sys.stderr)
        print("Coverage comparison will be limited", file=sys.stderr)
        modules = []

    # Run coverage
    print(f"Running tests in {test_path}...")
    coverage_data = run_coverage(test_path, detailed=args.detailed)

    # Calculate statistics
    stats = calculate_coverage_stats(modules, coverage_data)

    # Print report
    print_progress_report(stats, detailed=args.detailed)

    return 0


if __name__ == "__main__":
    sys.exit(main())
