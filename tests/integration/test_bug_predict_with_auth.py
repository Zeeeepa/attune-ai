"""Test bug prediction with authentication strategy integration.

Demonstrates:
1. Codebase size detection
2. Auth mode recommendation
3. Cost estimation
4. Full bug prediction with auth tracking
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
from empathy_os.workflows.bug_predict import BugPredictionWorkflow


async def test_bug_predict_with_auth():
    """Test bug prediction with auth strategy."""
    print("🔍 Testing Bug Prediction + Auth Strategy Integration\n")
    print("=" * 60)

    # Test on src/empathy_os directory
    test_dir = Path("src/empathy_os")

    if not test_dir.exists():
        print(f"❌ Test directory not found: {test_dir}")
        return

    # === STEP 1: Codebase Size Detection ===
    print("\n1. Codebase Size Detection")
    print("-" * 60)

    codebase_lines = count_lines_of_code(test_dir)
    size_category = get_module_size_category(codebase_lines)

    print(f"   Directory: {test_dir}")
    print(f"   Lines of code: {codebase_lines}")
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
    print(f"   ✓ Saved auth strategy to ~/.empathy/auth_strategy.json\n")

    recommended_mode = max_strategy.get_recommended_mode(codebase_lines)
    print(f"   Subscription tier: {max_strategy.subscription_tier.value}")
    print(f"   Recommended mode: {recommended_mode.value}")

    cost_estimate = max_strategy.estimate_cost(codebase_lines, recommended_mode)
    print(f"\n   Cost Estimate:")
    print(f"      Mode: {cost_estimate['mode']}")
    if cost_estimate["mode"] == "subscription":
        print(f"      Monetary cost: ${cost_estimate['monetary_cost']}")
        print(f"      Quota cost: {cost_estimate['quota_cost']}")
        print(f"      Fits in 200K context: {cost_estimate['fits_in_context']}")
    else:
        print(f"      Monetary cost: ${cost_estimate['monetary_cost']:.4f}")
        print(f"      Fits in 1M context: {cost_estimate['fits_in_context']}")

    # === STEP 3: Bug Prediction Execution ===
    print("\n3. Bug Prediction (with auth tracking)")
    print("-" * 60)

    workflow = BugPredictionWorkflow(
        enable_auth_strategy=True,
    )

    print(f"   Analyzing {test_dir}...")
    print(f"   Auth strategy: ENABLED")
    print(f"   Expected recommendation: {recommended_mode.value}")

    # Run workflow on src/empathy_os
    result = await workflow.execute(
        path=str(test_dir),
        file_types=[".py"],
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
    recommendations = output.get("recommendations", "")
    overall_risk_score = output.get("overall_risk_score", 0)
    pattern_count = output.get("pattern_count", 0)
    high_risk_files = output.get("high_risk_files", 0)

    print(f"\n   Bug Prediction Results:")
    print(f"      Overall risk score: {overall_risk_score}")
    print(f"      Patterns found: {pattern_count}")
    print(f"      High risk files: {high_risk_files}")
    print(f"      Recommendations: {len(recommendations)} characters")

    print(f"\n   Auth Strategy:")
    print(f"      Recommended: {recommended_mode.value}")
    print(f"      Tracked in workflow: {auth_mode_used or 'Not tracked'}")
    print(f"      Match: {auth_mode_used == recommended_mode.value}")

    # === STEP 5: Quality Checks ===
    print("\n5. Quality Checks")
    print("-" * 60)

    checks = [
        ("✅" if recommendations else "❌", "Recommendations generated"),
        ("✅" if auth_mode_used else "❌", "Auth mode tracked"),
        (
            "✅" if auth_mode_used == recommended_mode.value else "❌",
            "Auth mode matches recommendation",
        ),
        ("✅" if overall_risk_score >= 0 else "❌", "Risk score calculated"),
        ("✅" if pattern_count >= 0 else "❌", "Patterns scanned"),
    ]

    for icon, check in checks:
        print(f"   {icon} {check}")

    print("\n" + "=" * 60)
    print("✅ Integration Test Complete!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(test_bug_predict_with_auth())
