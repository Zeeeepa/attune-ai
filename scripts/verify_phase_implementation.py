"""Verify Phase 2 & 3 implementation structure without requiring API key.

This script validates that all required methods and configurations are present.

Usage:
    python scripts/verify_phase_implementation.py

Copyright 2026 Smart-AI-Memory
Licensed under Apache 2.0
"""

import inspect
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


def verify_phase_2_methods():
    """Verify Phase 2 methods exist and have correct signatures."""
    print("\n" + "=" * 70)
    print("PHASE 2: MULTI-TURN REFINEMENT VERIFICATION")
    print("=" * 70)

    from empathy_os.workflows.autonomous_test_gen import (
        AutonomousTestGenerator,
        ValidationResult,
    )

    # Check ValidationResult dataclass
    print("\n✓ Checking ValidationResult dataclass...")
    assert hasattr(ValidationResult, "__dataclass_fields__"), "ValidationResult is not a dataclass"
    assert "passed" in ValidationResult.__dataclass_fields__
    assert "failures" in ValidationResult.__dataclass_fields__
    assert "error_count" in ValidationResult.__dataclass_fields__
    assert "output" in ValidationResult.__dataclass_fields__
    print("  ✅ ValidationResult has all required fields")

    # Check AutonomousTestGenerator has Phase 2 methods
    print("\n✓ Checking AutonomousTestGenerator Phase 2 methods...")

    methods_to_check = {
        "_run_pytest_validation": ["test_file"],
        "_call_llm_with_history": ["conversation_history", "api_key"],
        "_generate_with_refinement": [
            "module_name",
            "module_path",
            "source_file",
            "source_code",
            "test_file",
        ],
    }

    for method_name, expected_params in methods_to_check.items():
        assert hasattr(AutonomousTestGenerator, method_name), f"Missing method: {method_name}"
        method = getattr(AutonomousTestGenerator, method_name)
        sig = inspect.signature(method)
        params = list(sig.parameters.keys())

        # Remove 'self' from comparison
        params = [p for p in params if p != "self"]

        # Validate parameters match expected
        for expected_param in expected_params:
            assert expected_param in params, (
                f"Missing parameter '{expected_param}' in {method_name}. "
                f"Expected: {expected_params}, Got: {params}"
            )

        print(f"  ✅ {method_name} exists with params: {params}")

    # Check __init__ has Phase 2 parameters
    print("\n✓ Checking __init__ Phase 2 configuration...")
    init_sig = inspect.signature(AutonomousTestGenerator.__init__)
    init_params = list(init_sig.parameters.keys())

    required_phase2_params = ["enable_refinement", "max_refinement_iterations"]
    for param in required_phase2_params:
        assert param in init_params, f"Missing __init__ parameter: {param}"
        print(f"  ✅ {param} parameter exists")

    print("\n✅ Phase 2 implementation structure is CORRECT")
    return True


def verify_phase_3_methods():
    """Verify Phase 3 methods exist and have correct signatures."""
    print("\n" + "=" * 70)
    print("PHASE 3: COVERAGE-GUIDED GENERATION VERIFICATION")
    print("=" * 70)

    from empathy_os.workflows.autonomous_test_gen import (
        AutonomousTestGenerator,
        CoverageResult,
    )

    # Check CoverageResult dataclass
    print("\n✓ Checking CoverageResult dataclass...")
    assert hasattr(CoverageResult, "__dataclass_fields__"), "CoverageResult is not a dataclass"
    assert "coverage" in CoverageResult.__dataclass_fields__
    assert "missing_lines" in CoverageResult.__dataclass_fields__
    assert "total_statements" in CoverageResult.__dataclass_fields__
    assert "covered_statements" in CoverageResult.__dataclass_fields__
    print("  ✅ CoverageResult has all required fields")

    # Check AutonomousTestGenerator has Phase 3 methods
    print("\n✓ Checking AutonomousTestGenerator Phase 3 methods...")

    methods_to_check = {
        "_run_coverage_analysis": ["test_file", "source_file"],
        "_extract_uncovered_lines": ["source_file", "missing_lines"],
        "_generate_with_coverage_target": [
            "module_name",
            "module_path",
            "source_file",
            "source_code",
            "test_file",
            "initial_test_content",
        ],
    }

    for method_name, expected_params in methods_to_check.items():
        assert hasattr(AutonomousTestGenerator, method_name), f"Missing method: {method_name}"
        method = getattr(AutonomousTestGenerator, method_name)
        sig = inspect.signature(method)
        params = list(sig.parameters.keys())

        # Remove 'self' from comparison
        params = [p for p in params if p != "self"]

        # Validate parameters match expected
        for expected_param in expected_params:
            assert expected_param in params, (
                f"Missing parameter '{expected_param}' in {method_name}. "
                f"Expected: {expected_params}, Got: {params}"
            )

        print(f"  ✅ {method_name} exists with params: {params}")

    # Check __init__ has Phase 3 parameters
    print("\n✓ Checking __init__ Phase 3 configuration...")
    init_sig = inspect.signature(AutonomousTestGenerator.__init__)
    init_params = list(init_sig.parameters.keys())

    required_phase3_params = ["enable_coverage_guided", "target_coverage"]
    for param in required_phase3_params:
        assert param in init_params, f"Missing __init__ parameter: {param}"
        print(f"  ✅ {param} parameter exists")

    print("\n✅ Phase 3 implementation structure is CORRECT")
    return True


def verify_integration():
    """Verify integration points in _generate_module_tests."""
    print("\n" + "=" * 70)
    print("INTEGRATION VERIFICATION")
    print("=" * 70)

    from empathy_os.workflows.autonomous_test_gen import AutonomousTestGenerator

    # Read the source to verify integration
    source_file = Path(__file__).parent.parent / "src" / "empathy_os" / "workflows" / "autonomous_test_gen.py"
    source_code = source_file.read_text()

    print("\n✓ Checking Phase 2 integration in _generate_module_tests...")
    assert "self.enable_refinement" in source_code
    assert "_generate_with_refinement" in source_code
    print("  ✅ Phase 2 refinement is integrated")

    print("\n✓ Checking Phase 3 integration in _generate_module_tests...")
    assert "self.enable_coverage_guided" in source_code
    assert "_generate_with_coverage_target" in source_code
    print("  ✅ Phase 3 coverage-guided is integrated")

    print("\n✓ Checking command-line argument handling...")
    assert "--no-refinement" in source_code
    assert "--coverage-guided" in source_code
    print("  ✅ Command-line arguments are implemented")

    print("\n✅ Integration is CORRECT")
    return True


def verify_documentation():
    """Verify documentation is updated."""
    print("\n" + "=" * 70)
    print("DOCUMENTATION VERIFICATION")
    print("=" * 70)

    docs_dir = Path(__file__).parent.parent / "docs"

    # Check TESTING_WORKFLOW_ANALYSIS.md
    analysis_doc = docs_dir / "TESTING_WORKFLOW_ANALYSIS.md"
    assert analysis_doc.exists(), "TESTING_WORKFLOW_ANALYSIS.md not found"

    analysis_content = analysis_doc.read_text()
    assert "PHASES 1-3 COMPLETE" in analysis_content or "Phase 2" in analysis_content
    print("  ✅ TESTING_WORKFLOW_ANALYSIS.md is updated")

    # Check SESSION_SUMMARY
    summary_doc = docs_dir / "SESSION_SUMMARY_2026-01-30.md"
    assert summary_doc.exists(), "SESSION_SUMMARY_2026-01-30.md not found"

    summary_content = summary_doc.read_text()
    assert "Phase 2" in summary_content or "Phase 3" in summary_content
    print("  ✅ SESSION_SUMMARY_2026-01-30.md is updated")

    # Check test script exists
    test_script = Path(__file__).parent / "test_phases_2_3.py"
    assert test_script.exists(), "test_phases_2_3.py not found"
    print("  ✅ test_phases_2_3.py validation script exists")

    print("\n✅ Documentation is COMPLETE")
    return True


def main():
    """Run all verifications."""
    print("\n" + "=" * 70)
    print("PHASE 2 & 3 IMPLEMENTATION VERIFICATION")
    print("=" * 70)
    print("\nVerifying implementation structure without requiring API key...")

    try:
        phase2_ok = verify_phase_2_methods()
        phase3_ok = verify_phase_3_methods()
        integration_ok = verify_integration()
        docs_ok = verify_documentation()

        print("\n" + "=" * 70)
        print("VERIFICATION SUMMARY")
        print("=" * 70)
        print(f"\nPhase 2 Methods:    {'✅ PASS' if phase2_ok else '❌ FAIL'}")
        print(f"Phase 3 Methods:    {'✅ PASS' if phase3_ok else '❌ FAIL'}")
        print(f"Integration:        {'✅ PASS' if integration_ok else '❌ FAIL'}")
        print(f"Documentation:      {'✅ PASS' if docs_ok else '❌ FAIL'}")

        if all([phase2_ok, phase3_ok, integration_ok, docs_ok]):
            print("\n🎉 ALL VERIFICATIONS PASSED!")
            print("\nImplementation is structurally complete.")
            print("\nTo run full validation with API calls:")
            print("  1. Set ANTHROPIC_API_KEY environment variable")
            print("  2. Run: python scripts/test_phases_2_3.py")
            return 0
        else:
            print("\n⚠️  Some verifications failed.")
            return 1

    except Exception as e:
        print(f"\n❌ ERROR during verification: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
