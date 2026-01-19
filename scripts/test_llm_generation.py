"""Test LLM-powered test generation on a single file.

This script tests the LLM integration by generating intelligent tests
for one low-coverage file.

Usage:
    python scripts/test_llm_generation.py
"""

import asyncio
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from empathy_os.orchestration.real_tools import (
    RealCoverageAnalyzer,
    RealTestGenerator,
    RealTestValidator,
)


async def main():
    """Test LLM test generation."""
    print("=" * 80)
    print("  LLM-POWERED TEST GENERATION - SINGLE FILE TEST")
    print("=" * 80)
    print()

    # Step 1: Find lowest coverage file
    print("📊 Step 1: Finding lowest coverage file...")
    print("-" * 80)

    analyzer = RealCoverageAnalyzer(project_root=".")
    report = analyzer.analyze(target_package="src/empathy_os")

    sorted_files = sorted(report.uncovered_files, key=lambda x: x["coverage"])
    target = sorted_files[0]

    print(f"✓ Target File: {target['path']}")
    print(f"✓ Current Coverage: {target['coverage']:.1f}%")
    print(f"✓ Missing Lines: {len(target['missing_lines'])} lines")
    print()

    # Step 2: Generate tests with LLM
    print("🧠 Step 2: Generating intelligent tests with Claude...")
    print("-" * 80)

    generator = RealTestGenerator(
        project_root=".",
        output_dir="tests/llm_generated",
        use_llm=True,  # Enable LLM
    )

    try:
        test_file = generator.generate_tests_for_file(
            target["path"], target["missing_lines"][:20]
        )
        print(f"✓ Generated: {test_file}")
        print()

        # Show preview
        print("📄 Test Preview (first 40 lines):")
        print("-" * 80)
        with test_file.open() as f:
            lines = f.readlines()[:40]
            for i, line in enumerate(lines, 1):
                print(f"{i:3d} | {line.rstrip()}")
        print()

    except Exception as e:
        print(f"✗ Generation failed: {e}")
        return 1

    # Step 3: Validate tests
    print("✅ Step 3: Validating generated tests...")
    print("-" * 80)

    validator = RealTestValidator(project_root=".")

    try:
        validation = validator.validate_tests([test_file])
        print(f"✓ Tests Passed: {validation['passed_count']}")
        print(f"✓ Tests Failed: {validation['failed_count']}")
        print()

        if validation["failed_count"] > 0:
            print("Failed test output (first 500 chars):")
            print(validation["output"][:500])
            print()

    except Exception as e:
        print(f"✗ Validation failed: {e}")
        return 1

    # Step 4: Measure improvement
    print("📈 Step 4: Measuring coverage improvement...")
    print("-" * 80)

    new_report = analyzer.analyze(target_package="src/empathy_os")
    improvement = new_report.total_coverage - report.total_coverage

    print(f"✓ Before: {report.total_coverage:.2f}%")
    print(f"✓ After:  {new_report.total_coverage:.2f}%")
    print(f"✓ Delta:  {improvement:+.2f}%")
    print()

    print("=" * 80)
    print("  ✅ LLM TEST GENERATION SUCCESSFUL!")
    print("=" * 80)
    print()
    print(f"  Generated file: {test_file}")
    print(f"  Quality: {'High ✨' if validation['passed_count'] > 0 else 'Needs work'}")
    print()

    return 0


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
