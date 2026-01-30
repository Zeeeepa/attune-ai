"""Test test generation with authentication strategy integration.

Demonstrates:
1. Module size detection
2. Auth mode recommendation
3. Cost estimation
4. Full test generation with auth tracking
"""

import asyncio
from pathlib import Path

from empathy_os.models import (
    AuthMode,
    AuthStrategy,
    SubscriptionTier,
    count_lines_of_code,
    get_module_size_category,
)
from empathy_os.workflows.test_gen import TestGenerationWorkflow


async def test_test_gen_with_auth():
    """Test test generation with auth strategy."""
    print("🧪 Testing Test Generation + Auth Strategy Integration\n")
    print("=" * 60)

    # Test on a small module
    test_module = Path("src/empathy_os/cache_stats.py")

    if not test_module.exists():
        print(f"❌ Test module not found: {test_module}")
        return

    # === STEP 1: Module Size Detection ===
    print("\n1. Module Size Detection")
    print("-" * 60)

    module_lines = count_lines_of_code(test_module)
    size_category = get_module_size_category(module_lines)

    print(f"   Module: {test_module.name}")
    print(f"   Lines of code: {module_lines}")
    print(f"   Size category: {size_category}")

    # === STEP 2: Auth Strategy Recommendation ===
    print("\n2. Auth Strategy Recommendation")
    print("-" * 60)

    max_strategy = AuthStrategy(
        subscription_tier=SubscriptionTier.MAX,
        default_mode=AuthMode.AUTO,
        setup_completed=True,
    )
    max_strategy.save()
    print("   ✓ Saved auth strategy to ~/.empathy/auth_strategy.json\n")

    recommended_mode = max_strategy.get_recommended_mode(module_lines)
    print(f"   Subscription tier: {max_strategy.subscription_tier.value}")
    print(f"   Recommended mode: {recommended_mode.value}")

    cost_estimate = max_strategy.estimate_cost(module_lines, recommended_mode)
    print("\n   Cost Estimate:")
    print(f"      Mode: {cost_estimate['mode']}")
    if cost_estimate["mode"] == "subscription":
        print(f"      Monetary cost: ${cost_estimate['monetary_cost']}")
        print(f"      Quota cost: {cost_estimate['quota_cost']}")
        print(f"      Fits in 200K context: {cost_estimate['fits_in_context']}")
    else:
        print(f"      Monetary cost: ${cost_estimate['monetary_cost']:.4f}")
        print(f"      Fits in 1M context: {cost_estimate['fits_in_context']}")

    # === STEP 3: Test Generation ===
    print("\n3. Test Generation (with auth tracking)")
    print("-" * 60)

    workflow = TestGenerationWorkflow(
        enable_auth_strategy=True,
        write_tests=False,  # Don't write files during test
    )

    print(f"   Generating tests for {test_module.name}...")
    print("   Auth strategy: ENABLED")
    print(f"   Expected recommendation: {recommended_mode.value}")

    # Run workflow (small scope for testing)
    result = await workflow.execute(
        path=str(test_module.parent),
        file_types=[".py"],
        max_files_to_scan=5,  # Limit scope for test
        max_candidates=3,
    )

    # === STEP 4: Results Analysis ===
    print("\n4. Results Analysis")
    print("=" * 60)

    if hasattr(result, "final_output") and isinstance(result.final_output, dict):
        output = result.final_output
    elif isinstance(result, dict):
        output = result
    else:
        print(f"❌ Unexpected result format: {type(result)}")
        return

    auth_mode_used = output.get("auth_mode_used")
    analysis_report = output.get("analysis_report", "")

    print("\n   Test Generation Results:")
    print(f"      Analysis: {len(analysis_report)} characters")

    print("\n   Auth Strategy:")
    print(f"      Recommended: {recommended_mode.value}")
    print(f"      Tracked in workflow: {auth_mode_used or 'Not tracked'}")
    print(f"      Match: {auth_mode_used == recommended_mode.value}")

    # === STEP 5: Quality Checks ===
    print("\n5. Quality Checks")
    print("-" * 60)

    checks = [
        ("✅" if analysis_report else "❌", "Analysis report generated"),
        ("✅" if auth_mode_used else "❌", "Auth mode tracked"),
    ]

    for icon, check in checks:
        print(f"   {icon} {check}")

    print("\n" + "=" * 60)
    print("✅ Integration Test Complete!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(test_test_gen_with_auth())
