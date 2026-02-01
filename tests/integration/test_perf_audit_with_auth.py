"""Test performance audit with authentication strategy integration.

Demonstrates:
1. Codebase size detection
2. Auth mode recommendation
3. Cost estimation
4. Full performance audit with auth tracking
"""

import asyncio
from pathlib import Path

from attune.models import (
    AuthMode,
    AuthStrategy,
    SubscriptionTier,
    count_lines_of_code,
    get_module_size_category,
)
from attune.workflows.perf_audit import PerformanceAuditWorkflow


async def test_perf_audit_with_auth():
    """Test performance audit with auth strategy."""
    print("⚡ Testing Performance Audit + Auth Strategy Integration\n")
    print("=" * 60)

    # Test on src/attune directory
    test_directory = Path("src/attune")

    if not test_directory.exists():
        print(f"❌ Test directory not found: {test_directory}")
        return

    # === STEP 1: Codebase Size Detection ===
    print("\n1. Codebase Size Detection")
    print("-" * 60)

    # Calculate total LOC for the directory
    total_lines = 0
    file_count = 0
    for py_file in test_directory.rglob("*.py"):
        if any(skip in str(py_file) for skip in [".git", "__pycache__", "test"]):
            continue
        try:
            total_lines += count_lines_of_code(py_file)
            file_count += 1
        except Exception:
            pass

    size_category = get_module_size_category(total_lines)

    print(f"   Directory: {test_directory}")
    print(f"   Files: {file_count}")
    print(f"   Lines of code: {total_lines:,}")
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
    print("   ✓ Saved auth strategy to ~/.attune/auth_strategy.json\n")

    recommended_mode = max_strategy.get_recommended_mode(total_lines)
    print(f"   Subscription tier: {max_strategy.subscription_tier.value}")
    print(f"   Recommended mode: {recommended_mode.value}")

    cost_estimate = max_strategy.estimate_cost(total_lines, recommended_mode)
    print("\n   Cost Estimate:")
    print(f"      Mode: {cost_estimate['mode']}")
    if cost_estimate["mode"] == "subscription":
        print(f"      Monetary cost: ${cost_estimate['monetary_cost']}")
        print(f"      Quota cost: {cost_estimate['quota_cost']}")
        print(f"      Fits in 200K context: {cost_estimate['fits_in_context']}")
    else:
        print(f"      Monetary cost: ${cost_estimate['monetary_cost']:.4f}")
        print(f"      Fits in 1M context: {cost_estimate['fits_in_context']}")

    # === STEP 3: Performance Audit Execution ===
    print("\n3. Performance Audit (with auth tracking)")
    print("-" * 60)

    workflow = PerformanceAuditWorkflow(
        enable_auth_strategy=True,
        min_hotspots_for_premium=5,  # Higher threshold for test
    )

    print(f"   Auditing {test_directory}...")
    print("   Auth strategy: ENABLED")
    print(f"   Expected recommendation: {recommended_mode.value}")

    # Run workflow (limited scope for testing)
    result = await workflow.execute(
        path=str(test_directory),
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
    perf_score = output.get("perf_score", 0)
    perf_level = output.get("perf_level", "unknown")
    top_issues = output.get("top_issues", [])
    optimization_plan = output.get("optimization_plan", "")

    print("\n   Performance Audit Results:")
    print(f"      Performance Score: {perf_score}/100")
    print(f"      Performance Level: {perf_level}")
    print(f"      Top Issues: {len(top_issues)}")
    print(f"      Optimization Plan: {len(optimization_plan)} characters")

    print("\n   Auth Strategy:")
    print(f"      Recommended: {recommended_mode.value}")
    print(f"      Tracked in workflow: {auth_mode_used or 'Not tracked'}")
    print(f"      Match: {auth_mode_used == recommended_mode.value}")

    if top_issues:
        print("\n   Top Performance Issues:")
        for issue in top_issues[:3]:
            print(f"      - {issue.get('type', 'unknown')}: {issue.get('count', 0)} occurrences")

    # === STEP 5: Quality Checks ===
    print("\n5. Quality Checks")
    print("-" * 60)

    checks = [
        ("✅" if perf_score >= 0 else "❌", "Performance score calculated"),
        ("✅" if perf_level else "❌", "Performance level assigned"),
        ("✅" if optimization_plan else "❌", "Optimization plan generated"),
        ("✅" if auth_mode_used else "❌", "Auth mode tracked"),
        ("✅" if auth_mode_used == recommended_mode.value else "❌", "Auth mode matches recommendation"),
    ]

    for icon, check in checks:
        print(f"   {icon} {check}")

    print("\n" + "=" * 60)
    print("✅ Integration Test Complete!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(test_perf_audit_with_auth())
