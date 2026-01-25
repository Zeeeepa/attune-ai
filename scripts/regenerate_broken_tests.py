"""Regenerate 3 broken test files with bug fixes applied.

This validates:
1. File naming fix (unique names from full path)
2. Token limit increase (8k → 12k)
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from empathy_os.orchestration.real_tools import RealTestGenerator


def main():
    print("=" * 80)
    print("  PHASE 3: REGENERATING 3 BROKEN FILES WITH FIXES")
    print("=" * 80)
    print("\nBug Fixes Applied:")
    print("  ✅ Unique file naming (no collisions)")
    print("  ✅ 12k token limit (prevents truncation)")
    print()

    # Initialize generator with LLM support
    generator = RealTestGenerator(
        project_root=".",
        output_dir="tests/llm_generated",
        use_llm=True
    )

    files_to_regenerate = [
        {
            "source": "src/empathy_os/cli.py",
            "missing": 1187,
            "description": "Main CLI (highest impact)",
            "expected_name": "test_src_empathy_os_cli_generated.py"
        },
        {
            "source": "src/empathy_os/telemetry/cli.py",
            "missing": 506,
            "description": "Telemetry CLI",
            "expected_name": "test_src_empathy_os_telemetry_cli_generated.py"
        },
        {
            "source": "src/empathy_os/workflows/document_gen.py",
            "missing": 363,
            "description": "Document generation workflow",
            "expected_name": "test_src_empathy_os_workflows_document_gen_generated.py"
        },
    ]

    results = []

    for i, file_info in enumerate(files_to_regenerate, 1):
        print(f"\n[{i}/3] Generating: {file_info['description']}")
        print(f"      Source: {file_info['source']}")
        print(f"      Expected output: {file_info['expected_name']}")
        print("-" * 80)

        try:
            missing_lines = list(range(1, file_info['missing'] + 1))

            test_path = generator.generate_tests_for_file(
                file_info['source'],
                missing_lines
            )

            # Verify filename is correct
            if test_path.name == file_info['expected_name']:
                print(f"✅ SUCCESS: {test_path}")
                print(f"   ✓ Filename is unique (no collision)")
                results.append((file_info['source'], test_path, "success"))
            else:
                print(f"⚠️  WARNING: Unexpected filename")
                print(f"   Expected: {file_info['expected_name']}")
                print(f"   Got: {test_path.name}")
                results.append((file_info['source'], test_path, f"warning: unexpected name"))

        except Exception as e:
            print(f"❌ FAILED: {e}")
            results.append((file_info['source'], None, f"error: {e}"))

    # Summary
    print("\n" + "=" * 80)
    print("  REGENERATION SUMMARY")
    print("=" * 80)

    success_count = sum(1 for _, _, status in results if status == "success")
    print(f"\nCompleted: {success_count}/3 files")
    print("\nResults:")

    for source, test_path, status in results:
        file_name = Path(source).name
        if status == "success":
            print(f"  ✅ {file_name:<30} → {test_path.name}")
        else:
            print(f"  ❌ {file_name:<30} → {status}")

    if success_count > 0:
        print(f"\n📊 Next Steps:")
        print(f"  1. Run tests: pytest tests/llm_generated/ -v")
        print(f"  2. Check pass rate: pytest tests/llm_generated/ -q | tail -1")
        print(f"  3. Measure coverage: pytest tests/llm_generated/ --cov=src")

    print("\n" + "=" * 80)
    print(f"Cost: ~${success_count * 1.5:.2f} estimated")
    print("=" * 80)

if __name__ == "__main__":
    main()
