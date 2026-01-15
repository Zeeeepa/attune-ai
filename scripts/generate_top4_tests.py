"""Generate tests for the next 4 highest-impact files for coverage.

Target files (total ~1,874 missing lines):
1. memory/short_term.py - 619 lines (17.5% coverage)
2. telemetry/cli.py - 506 lines (4.0% coverage)
3. workflow_commands.py - 386 lines (4.1% coverage)
4. workflows/document_gen.py - 363 lines (5.8% coverage)

Expected total coverage gain: +6-8%
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from empathy_os.orchestration.real_tools import RealTestGenerator

def main():
    print("=" * 80)
    print("  GENERATING TESTS FOR TOP 4 HIGH-IMPACT FILES")
    print("=" * 80)
    print(f"\n{'File':<40} {'Missing Lines':<15} {'Expected Gain'}")
    print("-" * 80)
    print(f"{'memory/short_term.py':<40} {'619':<15} {'+2.0%'}")
    print(f"{'telemetry/cli.py':<40} {'506':<15} {'+1.6%'}")
    print(f"{'workflow_commands.py':<40} {'386':<15} {'+1.2%'}")
    print(f"{'workflows/document_gen.py':<40} {'363':<15} {'+1.1%'}")
    print("-" * 80)
    print(f"{'TOTAL':<40} {'1,874':<15} {'+6-8%'}\n")

    # Initialize generator with LLM support
    generator = RealTestGenerator(
        project_root=".",
        output_dir="tests/llm_generated",
        use_llm=True
    )

    target_files = [
        ("src/empathy_os/memory/short_term.py", 619),
        ("src/empathy_os/telemetry/cli.py", 506),
        ("src/empathy_os/workflow_commands.py", 386),
        ("src/empathy_os/workflows/document_gen.py", 363),
    ]

    results = []

    for i, (source_file, missing_count) in enumerate(target_files, 1):
        print(f"\n[{i}/4] Generating tests for: {source_file}")
        print(f"      Missing lines: ~{missing_count}")
        print("-" * 80)

        try:
            # Generate placeholder missing lines (will be read from actual coverage)
            missing_lines = list(range(1, missing_count + 1))

            test_path = generator.generate_tests_for_file(source_file, missing_lines)

            print(f"✅ SUCCESS: {test_path}")
            results.append((source_file, test_path, "success"))

        except Exception as e:
            print(f"❌ FAILED: {e}")
            results.append((source_file, None, f"error: {e}"))

        print()

    # Summary
    print("\n" + "=" * 80)
    print("  GENERATION SUMMARY")
    print("=" * 80)

    success_count = sum(1 for _, _, status in results if status == "success")
    print(f"\nCompleted: {success_count}/4 files")
    print("\nResults:")

    for source_file, test_path, status in results:
        file_name = Path(source_file).name
        if status == "success":
            print(f"  ✅ {file_name:<30} → {test_path}")
        else:
            print(f"  ❌ {file_name:<30} → {status}")

    if success_count > 0:
        print(f"\n📈 Next Steps:")
        print(f"  1. Review generated tests: ls -lh tests/llm_generated/")
        print(f"  2. Fix any API errors: pytest tests/llm_generated/ -v")
        print(f"  3. Check coverage: pytest tests/llm_generated/ --cov=src")
        print(f"  4. Expected final coverage: ~32-34% (current: 26.46%)")

    print("\n" + "=" * 80)

if __name__ == "__main__":
    main()
