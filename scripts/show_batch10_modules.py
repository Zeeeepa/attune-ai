#!/usr/bin/env python3
"""Show modules in batch 10 for test generation.

Usage:
    python scripts/show_batch10_modules.py
"""

import json
import sys
from pathlib import Path


def main():
    """Display batch 10 modules and statistics."""
    batches_file = Path("/tmp/coverage_batches.json")

    if not batches_file.exists():
        print(f"Error: {batches_file} not found", file=sys.stderr)
        print("\nPlease create coverage batches first:", file=sys.stderr)
        print("  Run coverage analysis and generate batches", file=sys.stderr)
        return 1

    # Load batches
    with batches_file.open() as f:
        batches = json.load(f)

    batch_10 = batches.get("batch_10")
    if not batch_10:
        print("Error: batch_10 not found in batches file", file=sys.stderr)
        return 1

    # Display summary
    print("=" * 70)
    print("BATCH 10 MODULES - Test Generation Targets")
    print("=" * 70)
    print()
    print(f"Total Modules: {len(batch_10['modules'])}")
    print(f"Total Uncovered Lines: {batch_10['total_uncovered_lines']:,}")
    print(f"Coverage Goal: 80%+")
    print()

    # Display modules table
    print("Modules to Test:")
    print("-" * 70)
    print(f"{'Module':<50} {'Uncovered Lines':>18}")
    print("-" * 70)

    for module_info in batch_10["modules"]:
        module_path = module_info["module"]
        uncovered = module_info["uncovered_lines"]

        # Truncate long paths for display
        display_path = module_path
        if len(display_path) > 48:
            display_path = "..." + display_path[-45:]

        print(f"{display_path:<50} {uncovered:>18,}")

    print("-" * 70)
    print(f"{'TOTAL':<50} {batch_10['total_uncovered_lines']:>18,}")
    print()

    # Display next steps
    print("Next Steps:")
    print("  1. Generate tests:")
    print("     python scripts/generate_batch10_tests.py")
    print()
    print("  2. Complete TODO items in generated test files")
    print()
    print("  3. Run tests:")
    print("     pytest tests/behavioral/generated/batch10/ -v")
    print()
    print("  4. Check coverage:")
    print("     pytest tests/behavioral/generated/batch10/ --cov=src --cov-report=term-missing")
    print()

    return 0


if __name__ == "__main__":
    sys.exit(main())
