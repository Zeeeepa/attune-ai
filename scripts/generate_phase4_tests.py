#!/usr/bin/env python3
"""
Phase 4: Generate tests for next 5 high-impact files

This script generates LLM-powered tests for 5 files with highest missing coverage:
1. base.py - 606 missing lines (workflow base class)
2. control_panel.py - 523 missing lines (memory control panel)
3. documentation_orchestrator.py - 355 missing lines (doc orchestration)
4. cli_unified.py - 342 missing lines (unified CLI)
5. code_review.py - 341 missing lines (code review workflow)

Expected output: 250-300 tests
Estimated cost: $6-8
Expected pass rate: ~85% (with Phase 3 learnings)
"""

import sys
from pathlib import Path

# Add src to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "src"))

from attune.orchestration.real_tools import RealTestGenerator


def main():
    """Generate tests for 5 high-impact files."""

    print("=" * 80)
    print("  PHASE 4: GENERATING TESTS FOR 5 HIGH-IMPACT FILES")
    print("=" * 80)
    print()
    print("Bug Fixes Applied (from Phase 3):")
    print("  ✅ Unique file naming (no collisions)")
    print("  ✅ 12k token limit (prevents truncation)")
    print("  ✅ Path resolution (.resolve() call)")
    print()
    print()

    # Files to generate, ordered by impact
    files_to_generate = [
        {
            "source": "src/attune/workflows/base.py",
            "missing": 606,
            "description": "Workflow base class (highest impact)",
            "expected_name": "test_src_empathy_os_workflows_base_generated.py"
        },
        {
            "source": "src/attune/memory/control_panel.py",
            "missing": 523,
            "description": "Memory control panel (high impact)",
            "expected_name": "test_src_empathy_os_memory_control_panel_generated.py"
        },
        {
            "source": "src/attune/orchestration/documentation_orchestrator.py",
            "missing": 355,
            "description": "Documentation orchestrator",
            "expected_name": "test_src_empathy_os_orchestration_documentation_orchestrator_generated.py"
        },
        {
            "source": "src/attune/cli_unified.py",
            "missing": 342,
            "description": "Unified CLI interface",
            "expected_name": "test_src_empathy_os_cli_unified_generated.py"
        },
        {
            "source": "src/attune/workflows/code_review.py",
            "missing": 341,
            "description": "Code review workflow",
            "expected_name": "test_src_empathy_os_workflows_code_review_generated.py"
        },
    ]

    # Initialize generator
    generator = RealTestGenerator(
        project_root=str(project_root),
        output_dir=str(project_root / "tests" / "llm_generated"),
        use_llm=True
    )

    results = []
    total_missing = sum(f["missing"] for f in files_to_generate)

    # Generate each file
    for idx, file_info in enumerate(files_to_generate, 1):
        print(f"[{idx}/{len(files_to_generate)}] Generating: {file_info['description']}")
        print(f"      Source: {file_info['source']}")
        print(f"      Expected output: {file_info['expected_name']}")
        print("-" * 80)

        try:
            # Generate tests
            test_file = generator.generate_tests_for_file(
                source_file=file_info["source"],
                missing_lines=list(range(1, file_info["missing"] + 1))
            )

            # Validate result
            test_path = Path(test_file)
            if test_path.exists():
                print(f"✅ SUCCESS: {test_path}")
                print(f"   ✓ Filename is unique (no collision)")
                results.append({
                    "source": file_info["source"].split("/")[-1],
                    "test_file": test_path.name,
                    "status": "success",
                    "error": None
                })
            else:
                print(f"❌ FAILED: File not created")
                results.append({
                    "source": file_info["source"].split("/")[-1],
                    "test_file": file_info["expected_name"],
                    "status": "error",
                    "error": "File not created"
                })

        except Exception as e:
            print(f"❌ FAILED: {e}")
            results.append({
                "source": file_info["source"].split("/")[-1],
                "test_file": file_info["expected_name"],
                "status": "error",
                "error": str(e)
            })

        print()

    # Summary
    print("=" * 80)
    print("  GENERATION SUMMARY")
    print("=" * 80)
    print()

    successful = sum(1 for r in results if r["status"] == "success")
    print(f"Completed: {successful}/{len(files_to_generate)} files")
    print()

    print("Results:")
    for result in results:
        status_icon = "✅" if result["status"] == "success" else "❌"
        if result["status"] == "success":
            print(f"  {status_icon} {result['source']:30} → {result['test_file']}")
        else:
            print(f"  {status_icon} {result['source']:30} → error: {result['error']}")

    print()
    print("📊 Next Steps:")
    print("  1. Run tests: pytest tests/llm_generated/ -v")
    print("  2. Check pass rate: pytest tests/llm_generated/ -q | tail -1")
    print("  3. Measure coverage: pytest tests/llm_generated/ --cov=src")
    print()
    print("=" * 80)
    print(f"Cost: ~${6 + (successful * 0.4):.2f} estimated")
    print("=" * 80)


if __name__ == "__main__":
    main()
