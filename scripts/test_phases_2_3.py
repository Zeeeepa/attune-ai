"""Test script for Phase 2 & 3 enhanced test generation.

Validates that multi-turn refinement and coverage-guided generation work correctly.

Usage:
    python scripts/test_phases_2_3.py

Expected behavior:
- Phase 2: Generates tests, validates them, and refines if failures occur
- Phase 3: Runs coverage analysis and adds tests for uncovered lines

Copyright 2026 Smart-AI-Memory
Licensed under Apache 2.0
"""

import json
import subprocess
import sys
from pathlib import Path


def test_phase_2_refinement():
    """Test Phase 2: Multi-Turn Refinement."""
    print("\n" + "=" * 70)
    print("PHASE 2: MULTI-TURN REFINEMENT TEST")
    print("=" * 70)

    # Test on a workflow module (complex, likely to need refinement)
    test_module = {
        "file": "src/attune/workflows/test_gen/workflow.py",
        "description": "Test generation workflow - validate refinement",
    }

    modules_json = json.dumps([test_module])

    print("\n📝 Testing Phase 2 on workflow module...")
    print(f"   Module: {test_module['file']}")
    print("   Features:")
    print("   ✅ Multi-turn refinement ENABLED")
    print("   ❌ Coverage-guided DISABLED")
    print()

    try:
        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "attune.workflows.autonomous_test_gen",
                "100",  # batch100 for testing
                modules_json,
                # Phase 2 enabled by default, no coverage-guided
            ],
            timeout=600,  # 10 min timeout
            capture_output=True,
            text=True,
        )

        print("STDOUT:")
        print(result.stdout)

        if result.returncode != 0:
            print("\nSTDERR:")
            print(result.stderr)
            print("\n❌ Phase 2 test FAILED")
            return False

        # Check output for Phase 2 indicators
        output = result.stdout + result.stderr

        phase_2_checks = {
            "Multi-turn enabled": "Phase 2: Multi-turn refinement" in output,
            "Refinement iteration": "Refinement iteration" in output,
            "Test validation": "Pytest validation" in output or "passed=" in output.lower(),
        }

        print("\n📊 Phase 2 Validation:")
        all_passed = True
        for check_name, passed in phase_2_checks.items():
            status = "✅" if passed else "❌"
            print(f"   {status} {check_name}")
            if not passed:
                all_passed = False

        # Check generated files
        test_file = Path("tests/behavioral/generated/batch100/test_workflow_behavioral.py")
        if test_file.exists():
            print(f"\n✅ Test file generated: {test_file}")
            content = test_file.read_text()
            print(f"   Size: {len(content)} bytes")

            # Check for quality indicators
            quality_checks = {
                "Has fixtures": "@pytest.fixture" in content,
                "Has async tests": "@pytest.mark.asyncio" in content,
                "Has mocking": "mock" in content.lower() or "Mock" in content,
                "Has docstrings": '"""' in content or "'''" in content,
            }

            print("\n   Quality checks:")
            for check_name, passed in quality_checks.items():
                status = "✅" if passed else "⚠️ "
                print(f"      {status} {check_name}")

        else:
            print(f"\n❌ Test file not found: {test_file}")
            all_passed = False

        return all_passed

    except subprocess.TimeoutExpired:
        print("\n❌ Phase 2 test TIMEOUT (>10 min)")
        return False
    except Exception as e:
        print(f"\n❌ Phase 2 test ERROR: {e}")
        return False


def test_phase_3_coverage_guided():
    """Test Phase 3: Coverage-Guided Generation."""
    print("\n" + "=" * 70)
    print("PHASE 3: COVERAGE-GUIDED GENERATION TEST")
    print("=" * 70)

    # Test on a simpler utility module for faster coverage testing
    test_module = {
        "file": "src/attune/config.py",
        "description": "Configuration module - validate coverage improvement",
    }

    modules_json = json.dumps([test_module])

    print("\n📊 Testing Phase 3 on utility module...")
    print(f"   Module: {test_module['file']}")
    print("   Features:")
    print("   ✅ Multi-turn refinement ENABLED")
    print("   ✅ Coverage-guided ENABLED (80% target)")
    print()

    try:
        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "attune.workflows.autonomous_test_gen",
                "101",  # batch101 for testing
                modules_json,
                "--coverage-guided",  # Enable Phase 3
            ],
            timeout=900,  # 15 min timeout (coverage is slower)
            capture_output=True,
            text=True,
        )

        print("STDOUT:")
        print(result.stdout)

        if result.returncode != 0:
            print("\nSTDERR:")
            print(result.stderr)
            print("\n❌ Phase 3 test FAILED")
            return False

        # Check output for Phase 3 indicators
        output = result.stdout + result.stderr

        phase_3_checks = {
            "Coverage-guided enabled": "Phase 3: Coverage-guided" in output,
            "Coverage iteration": "Coverage iteration" in output,
            "Coverage analysis": "coverage" in output.lower(),
            "Uncovered lines": "uncovered" in output.lower() or "missing" in output.lower(),
        }

        print("\n📊 Phase 3 Validation:")
        all_passed = True
        for check_name, passed in phase_3_checks.items():
            status = "✅" if passed else "❌"
            print(f"   {status} {check_name}")
            if not passed:
                all_passed = False

        # Check generated files
        test_file = Path("tests/behavioral/generated/batch101/test_config_behavioral.py")
        if test_file.exists():
            print(f"\n✅ Test file generated: {test_file}")
            content = test_file.read_text()
            print(f"   Size: {len(content)} bytes")

            # Count test functions
            test_count = content.count("def test_")
            print(f"   Test functions: {test_count}")

            # Run coverage to verify improvement
            try:
                coverage_result = subprocess.run(
                    [
                        sys.executable,
                        "-m",
                        "pytest",
                        str(test_file),
                        f"--cov={test_module['file']}",
                        "--cov-report=term-missing",
                    ],
                    capture_output=True,
                    text=True,
                    timeout=120,
                )

                # Extract coverage percentage
                for line in coverage_result.stdout.split("\n"):
                    if "TOTAL" in line or test_module["file"].split("/")[-1] in line:
                        print(f"\n   Coverage line: {line}")

            except Exception as e:
                print(f"\n⚠️  Could not run coverage check: {e}")

        else:
            print(f"\n❌ Test file not found: {test_file}")
            all_passed = False

        return all_passed

    except subprocess.TimeoutExpired:
        print("\n❌ Phase 3 test TIMEOUT (>15 min)")
        return False
    except Exception as e:
        print(f"\n❌ Phase 3 test ERROR: {e}")
        return False


def main():
    """Run all phase tests."""
    print("\n" + "=" * 70)
    print("TESTING PHASE 2 & 3 ENHANCEMENTS")
    print("=" * 70)
    print("\nThis will:")
    print("  1. Test Phase 2 multi-turn refinement")
    print("  2. Test Phase 3 coverage-guided generation")
    print(f"\nExpected duration: ~15-20 minutes")
    print("\n⚠️  Requires ANTHROPIC_API_KEY environment variable")

    import os

    if not os.getenv("ANTHROPIC_API_KEY"):
        print("\n❌ ERROR: ANTHROPIC_API_KEY not set")
        print("   Set it with: export ANTHROPIC_API_KEY=your_key_here")
        sys.exit(1)

    print("\nStarting tests...\n")

    # Test Phase 2
    phase_2_passed = test_phase_2_refinement()

    # Test Phase 3 (optional - comment out if you want to test Phase 2 only)
    phase_3_passed = test_phase_3_coverage_guided()

    # Summary
    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)
    print(
        f"\nPhase 2 (Multi-Turn Refinement):     {'✅ PASSED' if phase_2_passed else '❌ FAILED'}"
    )
    print(f"Phase 3 (Coverage-Guided Generation): {'✅ PASSED' if phase_3_passed else '❌ FAILED'}")

    if phase_2_passed and phase_3_passed:
        print("\n🎉 All tests PASSED! Phase 2 & 3 are working correctly.")
        sys.exit(0)
    else:
        print("\n⚠️  Some tests FAILED. Review output above for details.")
        sys.exit(1)


if __name__ == "__main__":
    main()
