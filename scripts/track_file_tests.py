#!/usr/bin/env python
"""Track per-file test results for CI integration.

This script scans source files and tracks their test status,
optionally using coverage data to enhance the records.

Usage:
    python scripts/track_file_tests.py [--coverage coverage.xml] [--limit N]

Copyright 2025 Smart-AI-Memory
Licensed under Fair Source License 0.9
"""

import argparse
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


def main():
    """Main entry point for file test tracking."""
    parser = argparse.ArgumentParser(description="Track per-file test results")
    parser.add_argument(
        "--coverage",
        type=str,
        help="Path to coverage.xml file for coverage data",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=100,
        help="Maximum number of files to track (default: 100)",
    )
    parser.add_argument(
        "--source-dir",
        type=str,
        default="src/empathy_os",
        help="Source directory to scan (default: src/empathy_os)",
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Verbose output",
    )
    args = parser.parse_args()

    try:
        from empathy_os.workflows.test_runner import track_file_tests
    except ImportError as e:
        print(f"Error importing empathy_os: {e}")
        print("Make sure the package is installed: pip install -e .")
        return 1

    # Get source files
    source_dir = Path(args.source_dir)
    if not source_dir.exists():
        print(f"Source directory not found: {source_dir}")
        return 1

    source_files = []
    for p in source_dir.rglob("*.py"):
        if "__pycache__" not in str(p) and not p.name.startswith("test_"):
            source_files.append(str(p))

    source_files = sorted(source_files)[: args.limit]
    print(f"Tracking {len(source_files)} source files...")

    # Parse coverage data if available
    coverage_data = {}
    if args.coverage:
        coverage_data = _parse_coverage_xml(args.coverage)
        if coverage_data:
            print(f"Loaded coverage data for {len(coverage_data)} files")

    # Track files
    results = {"passed": 0, "failed": 0, "no_tests": 0, "error": 0, "skipped": 0}

    for i, source_file in enumerate(source_files, 1):
        if args.verbose or i % 20 == 0:
            print(f"  Progress: {i}/{len(source_files)}...")

        try:
            result = track_file_tests(source_file)
            results[result.last_test_result] = results.get(result.last_test_result, 0) + 1

            if args.verbose:
                status = "PASS" if result.success else result.last_test_result.upper()
                print(f"    {status}: {source_file}")
        except Exception as e:
            print(f"    ERROR tracking {source_file}: {e}")
            results["error"] += 1

    # Summary
    print("\n" + "=" * 60)
    print("FILE TEST TRACKING SUMMARY")
    print("=" * 60)
    print(f"  Passed:    {results['passed']}")
    print(f"  Failed:    {results['failed']}")
    print(f"  No Tests:  {results['no_tests']}")
    print(f"  Errors:    {results['error']}")
    print(f"  Skipped:   {results['skipped']}")
    print("=" * 60)

    # Return error code if any failures
    if results["failed"] > 0:
        print(f"\n{results['failed']} file(s) have failing tests!")
        return 1

    return 0


def _parse_coverage_xml(coverage_file: str) -> dict:
    """Parse coverage.xml and return file coverage data.

    Args:
        coverage_file: Path to coverage.xml

    Returns:
        Dict mapping file paths to coverage percentage
    """
    coverage_path = Path(coverage_file)
    if not coverage_path.exists():
        print(f"Coverage file not found: {coverage_file}")
        return {}

    try:
        import xml.etree.ElementTree as ET

        tree = ET.parse(coverage_path)
        root = tree.getroot()

        coverage_data = {}
        for package in root.findall(".//package"):
            for class_elem in package.findall("classes/class"):
                filename = class_elem.attrib.get("filename", "")
                line_rate = float(class_elem.attrib.get("line-rate", 0))
                coverage_data[filename] = line_rate * 100

        return coverage_data
    except Exception as e:
        print(f"Error parsing coverage.xml: {e}")
        return {}


if __name__ == "__main__":
    sys.exit(main())
