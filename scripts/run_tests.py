#!/usr/bin/env python3
"""Test Runner with Parallel/Sequential Fallback

Runs pytest with parallel execution by default, falling back to sequential
if parallel execution fails (e.g., due to memory issues or test isolation).

Usage:
    python scripts/run_tests.py [pytest args...]

Examples:
    python scripts/run_tests.py                     # Run all tests
    python scripts/run_tests.py tests/unit/        # Run unit tests only
    python scripts/run_tests.py -k "test_cache"    # Run tests matching pattern
    python scripts/run_tests.py --cov=src/         # With coverage
    python scripts/run_tests.py --sequential       # Force sequential mode

Copyright 2025 Smart AI Memory, LLC
Licensed under the Apache License, Version 2.0
"""

import subprocess
import sys
from pathlib import Path


def run_tests(args: list[str], parallel: bool = True) -> int:
    """Run pytest with given arguments.

    Args:
        args: Additional pytest arguments
        parallel: If True, use -n auto; if False, use -n 0

    Returns:
        Exit code from pytest
    """
    cmd = ["python", "-m", "pytest"]

    # Override parallelism setting
    if parallel:
        cmd.extend(["-n", "auto", "--dist", "loadfile"])
    else:
        cmd.extend(["-n", "0"])

    # Add user-provided arguments
    cmd.extend(args)

    print(f"Running: {' '.join(cmd)}")
    print("-" * 60)

    result = subprocess.run(cmd)
    return result.returncode


def main() -> int:
    """Main entry point with fallback logic."""
    # Parse our custom flags
    args = sys.argv[1:]
    force_sequential = "--sequential" in args
    force_parallel = "--parallel" in args

    # Remove our custom flags before passing to pytest
    args = [a for a in args if a not in ("--sequential", "--parallel")]

    if force_sequential:
        print("Running in sequential mode (--sequential flag)")
        return run_tests(args, parallel=False)

    if force_parallel:
        print("Running in parallel mode (--parallel flag)")
        return run_tests(args, parallel=True)

    # Default: try parallel first, fall back to sequential
    print("Attempting parallel execution...")
    exit_code = run_tests(args, parallel=True)

    # Check for specific failure patterns that warrant a retry
    # Exit codes: 0=success, 1=test failures, 2=interrupted, 3=internal error, 4=usage error
    if exit_code in (2, 3, 4):  # Not a normal test failure
        print()
        print("=" * 60)
        print("Parallel execution failed with error. Retrying sequentially...")
        print("=" * 60)
        print()
        exit_code = run_tests(args, parallel=False)

    return exit_code


if __name__ == "__main__":
    sys.exit(main())
