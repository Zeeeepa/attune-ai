"""Test enhanced AutonomousTestGenerator on workflow module.

Validates Phase 1 improvements:
- Workflow detection
- Extended thinking (20K tokens)
- Prompt caching
- Full source code (no truncation)
- Workflow-specific prompts with mocking
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from attune.workflows.autonomous_test_gen import AutonomousTestGenerator


def main():
    """Test enhanced generator on a workflow module."""

    # Test on test_gen workflow (currently 8.57% coverage)
    test_module = {
        "file": "src/attune/workflows/test_gen/workflow.py",
        "description": "Test generation workflow - validate enhanced mocking",
    }

    print("=" * 70)
    print("TESTING ENHANCED AUTONOMOUS TEST GENERATOR")
    print("=" * 70)
    print(f"\nTarget: {test_module['file']}")
    print(f"Current coverage: 8.57%")
    print(f"Expected coverage: 40-50% (5x improvement)")
    print("\nEnhancements active:")
    print("  ✓ Extended thinking (20K token budget)")
    print("  ✓ Prompt caching (90% cost reduction)")
    print("  ✓ Full source code (no truncation)")
    print("  ✓ Workflow detection & specialized prompts")
    print("  ✓ LLM mocking templates")
    print("\n" + "=" * 70)

    # Create generator for test batch
    agent_id = "enhanced-test-validation"
    batch_num = 99  # Use batch 99 for validation

    generator = AutonomousTestGenerator(
        agent_id=agent_id, batch_num=batch_num, modules=[test_module]
    )

    print(f"\nAgent ID: {agent_id}")
    print(f"Output: tests/behavioral/generated/batch{batch_num}/")
    print("\nGenerating tests...\n")

    # Generate tests
    results = generator.generate_all()

    # Report results
    print("\n" + "=" * 70)
    print("VALIDATION RESULTS")
    print("=" * 70)
    print(f"Status: {'✅ SUCCESS' if results['completed'] > 0 else '❌ FAILED'}")
    print(f"Modules processed: {results['completed']}/{results['total_modules']}")
    print(f"Tests generated: {results['tests_generated']}")
    print(f"Files created: {results['files_created']}")

    if results["completed"] > 0:
        test_file = Path(results["files_created"][0])
        print(f"\n📄 Test file: {test_file}")
        print(f"   Size: {test_file.stat().st_size:,} bytes")

        # Check for workflow-specific patterns
        content = test_file.read_text()

        print("\n🔍 Validation checks:")
        has_llm_mock = "mock_llm" in content or "mocker.patch('anthropic" in content
        has_async = "@pytest.mark.asyncio" in content
        has_tier_test = "tier" in content.lower()
        has_proper_imports = "from attune.workflows.test_gen" in content

        print(f"   {'✅' if has_llm_mock else '❌'} LLM mocking present")
        print(f"   {'✅' if has_async else '❌'} Async test markers")
        print(f"   {'✅' if has_tier_test else '❌'} Tier routing tests")
        print(f"   {'✅' if has_proper_imports else '❌'} Proper imports")

        # Count test functions
        test_count = content.count("def test_") + content.count("async def test_")
        print(f"\n📊 Test functions: {test_count}")

        print("\n✨ Next step: Run coverage to validate improvement")
        print(f"   pytest {test_file} --cov=src/attune/workflows/test_gen/workflow.py")

    print("=" * 70)

    return 0 if results["completed"] > 0 else 1


if __name__ == "__main__":
    sys.exit(main())
