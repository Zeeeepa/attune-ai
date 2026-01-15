"""Generate comprehensive tests for cli.py - the highest-impact target.

cli.py has 1,187 missing lines (26.2% coverage) - biggest win for coverage.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from empathy_os.orchestration.real_tools import RealTestGenerator

def main():
    print("=" * 80)
    print("  GENERATING TESTS FOR CLI.PY (Highest Impact: 1,187 missing lines)")
    print("=" * 80)

    # Initialize generator with LLM support
    generator = RealTestGenerator(
        project_root=".",
        output_dir="tests/llm_generated",
        use_llm=True
    )

    # Generate tests for cli.py
    source_file = "src/empathy_os/cli.py"
    missing_lines = list(range(1, 1187))  # Placeholder - will be read from coverage

    print(f"\n📊 Target: {source_file}")
    print(f"📈 Missing lines: ~1,187")
    print(f"🎯 Expected coverage gain: +4-5%\n")

    try:
        test_path = generator.generate_tests_for_file(source_file, missing_lines)
        print(f"\n✅ SUCCESS!")
        print(f"Generated: {test_path}")
        print(f"\nNext steps:")
        print(f"  1. Review: cat {test_path} | head -100")
        print(f"  2. Fix any API errors (5-10 min)")
        print(f"  3. Run: pytest {test_path} -v")
        print(f"  4. Check coverage: pytest --cov=src/empathy_os/cli.py")

    except Exception as e:
        print(f"\n❌ FAILED: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
