"""Test script for real coverage boost with actual tooling.

This script demonstrates the real tool integration by:
1. Running actual coverage analysis
2. Generating basic test files
3. Running tests to validate

Usage:
    python scripts/test_real_coverage_boost.py
"""

import asyncio
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from empathy_os.orchestration.real_tools import (RealCoverageAnalyzer,
                                                 RealTestGenerator,
                                                 RealTestValidator)


async def main():
    """Run real coverage boost demonstration."""
    print("=" * 60)
    print("REAL COVERAGE BOOST - TEST RUN")
    print("=" * 60)
    print()

    # Step 1: Analyze current coverage
    print("📊 Step 1: Running coverage analysis...")
    print("-" * 60)

    analyzer = RealCoverageAnalyzer(project_root=".")
    try:
        report = analyzer.analyze(target_package="src/empathy_os")
        print(f"✓ Current Coverage: {report.total_coverage:.2f}%")
        print(f"✓ Files Analyzed: {report.files_analyzed}")
        print(f"✓ Files Below 80%: {len(report.uncovered_files)}")
        print()

        # Show top 5 lowest coverage files
        sorted_files = sorted(
            report.uncovered_files, key=lambda x: x["coverage"]
        )[:5]
        print("  Top 5 Files Needing Coverage:")
        for file in sorted_files:
            print(f"    • {file['path']}: {file['coverage']:.1f}%")
        print()

    except Exception as e:
        print(f"✗ Coverage analysis failed: {e}")
        return 1

    # Step 2: Generate tests for lowest coverage file
    print("🔨 Step 2: Generating tests for lowest coverage file...")
    print("-" * 60)

    generator = RealTestGenerator(
        project_root=".", output_dir="tests/generated_experimental"
    )

    try:
        # Generate tests for the file with lowest coverage
        target_file = sorted_files[0]
        test_file = generator.generate_tests_for_file(
            target_file["path"], target_file["missing_lines"][:10]
        )
        print(f"✓ Generated test file: {test_file}")
        print(f"  Target: {target_file['path']} ({target_file['coverage']:.1f}%)")
        print()

    except Exception as e:
        print(f"✗ Test generation failed: {e}")
        return 1

    # Step 3: Validate generated tests
    print("✅ Step 3: Validating generated tests...")
    print("-" * 60)

    validator = RealTestValidator(project_root=".")

    try:
        validation = validator.validate_tests([test_file])
        print(f"✓ All Tests Passed: {validation['all_passed']}")
        print(f"✓ Passed: {validation['passed_count']}")
        print(f"✓ Failed: {validation['failed_count']}")
        print()

    except Exception as e:
        print(f"✗ Test validation failed: {e}")
        return 1

    # Step 4: Re-run coverage to see improvement
    print("📈 Step 4: Measuring coverage improvement...")
    print("-" * 60)

    try:
        new_report = analyzer.analyze(target_package="src/empathy_os")
        improvement = new_report.total_coverage - report.total_coverage

        print(f"✓ New Coverage: {new_report.total_coverage:.2f}%")
        print(f"✓ Improvement: {improvement:+.2f}%")
        print()

    except Exception as e:
        print(f"✗ Re-analysis failed: {e}")
        return 1

    print("=" * 60)
    print("✅ REAL COVERAGE BOOST TEST COMPLETE!")
    print("=" * 60)
    print()
    print(f"Summary:")
    print(f"  • Before: {report.total_coverage:.2f}%")
    print(f"  • After:  {new_report.total_coverage:.2f}%")
    print(f"  • Delta:  {improvement:+.2f}%")
    print(f"  • Tests Generated: 1")
    print(f"  • Generated Tests Location: tests/generated_experimental/")
    print()

    return 0


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
