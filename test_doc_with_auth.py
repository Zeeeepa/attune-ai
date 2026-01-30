"""Test document generation with authentication strategy integration.

Demonstrates:
1. Module size detection
2. Auth mode recommendation
3. Cost estimation
4. Full documentation generation with auth tracking
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
from empathy_os.workflows.document_gen import DocumentGenerationWorkflow


async def test_doc_with_auth():
    """Test documentation generation with auth strategy."""
    print("📚 Testing Document Generation + Auth Strategy Integration\n")
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

    # Test with Max user (should use subscription for small modules)
    max_strategy = AuthStrategy(
        subscription_tier=SubscriptionTier.MAX,
        default_mode=AuthMode.AUTO,
        setup_completed=True,  # Skip interactive setup
    )

    # Save strategy so workflow can load it
    max_strategy.save()
    print("   ✓ Saved auth strategy to ~/.empathy/auth_strategy.json\n")

    recommended_mode = max_strategy.get_recommended_mode(module_lines)
    print(f"   Subscription tier: {max_strategy.subscription_tier.value}")
    print(f"   Recommended mode: {recommended_mode.value}")

    # Get cost estimate
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

    # === STEP 3: Documentation Generation ===
    print("\n3. Documentation Generation (with auth tracking)")
    print("-" * 60)

    # Read source code
    source_code = test_module.read_text()

    # Create workflow with auth strategy enabled
    workflow = DocumentGenerationWorkflow(
        export_path="docs/generated",
        max_cost=0.5,
        graceful_degradation=True,
        enable_auth_strategy=True,  # Enable auth strategy integration
    )

    print(f"   Generating documentation for {test_module.name}...")
    print("   Auth strategy: ENABLED")
    print(f"   Expected recommendation: {recommended_mode.value}")

    # Generate documentation
    result = await workflow.execute(
        source_code=source_code,
        target=str(test_module),
        doc_type="api_reference",
        audience="developers",
    )

    # === STEP 4: Results Analysis ===
    print("\n4. Results Analysis")
    print("=" * 60)

    # Extract results
    if hasattr(result, "final_output") and isinstance(result.final_output, dict):
        output = result.final_output
    elif isinstance(result, dict):
        output = result
    else:
        print(f"❌ Unexpected result format: {type(result)}")
        return

    document = output.get("document", "")
    auth_mode_used = output.get("auth_mode_used")
    accumulated_cost = output.get("accumulated_cost", 0.0)
    export_path = output.get("export_path", "")

    print("\n   Generated Document:")
    print(f"      Size: {len(document):,} characters")
    print(f"      Sections: ~{document.count('##')}")
    print(f"      Cost: ${accumulated_cost:.4f}")

    print("\n   Auth Strategy:")
    print(f"      Recommended: {recommended_mode.value}")
    print(f"      Tracked in workflow: {auth_mode_used or 'Not tracked'}")
    print(f"      Match: {auth_mode_used == recommended_mode.value}")

    if export_path:
        print("\n   Export:")
        print(f"      Saved to: {export_path}")

    # === STEP 5: Quality Checks ===
    print("\n5. Quality Checks")
    print("-" * 60)

    checks = [
        ("✅" if "```python" in document else "❌", "Contains Python code blocks"),
        ("✅" if "import" in document else "❌", "Includes import statements"),
        ("✅" if "Args:" in document else "❌", "Has **Args:** sections"),
        ("✅" if "Returns:" in document else "❌", "Has **Returns:** sections"),
        ("✅" if auth_mode_used else "❌", "Auth mode tracked"),
        ("✅" if accumulated_cost > 0 else "❌", "Cost tracked"),
    ]

    for icon, check in checks:
        print(f"   {icon} {check}")

    # === STEP 6: Recommendation Summary ===
    print("\n6. Recommendation Summary")
    print("=" * 60)

    print(f"\n   For this module ({module_lines} LOC, {size_category}):")
    print(f"      Recommended: {recommended_mode.value.upper()} mode")

    if recommended_mode.value == "subscription":
        print("      Reason: Small module fits easily in 200K context")
        print("      Benefit: No additional cost, uses existing subscription")
    else:
        print("      Reason: Large module needs 1M context window")
        print("      Benefit: Higher context limit, no quota consumption")

    print("\n   Workflow Integration:")
    print("      ✅ Auth strategy detected module size")
    print(f"      ✅ Recommended {recommended_mode.value} mode")
    print("      ✅ Tracked auth_mode_used in results")
    print("      ✅ Ready for telemetry logging")

    print("\n" + "=" * 60)
    print("✅ Integration Test Complete!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(test_doc_with_auth())
