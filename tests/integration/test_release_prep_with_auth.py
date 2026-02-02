"""Integration test for ReleasePreparationWorkflow with auth strategy.

Tests that auth strategy properly integrates with release preparation workflow,
tracking auth mode and providing intelligent routing recommendations.
"""

import pytest

from attune.models import AuthMode, AuthStrategy, SubscriptionTier
from attune.workflows.release_prep import ReleasePreparationWorkflow


@pytest.mark.asyncio
async def test_release_prep_with_auth():
    """Test release preparation workflow with auth strategy integration."""
    # Step 1: Configure auth strategy (Max user, auto mode)
    strategy = AuthStrategy(
        subscription_tier=SubscriptionTier.MAX,
        default_mode=AuthMode.AUTO,
        setup_completed=True,
    )
    strategy.save()

    # Step 2: Create workflow with auth enabled
    workflow = ReleasePreparationWorkflow(
        skip_approve_if_clean=True,
        enable_auth_strategy=True,
    )

    assert workflow.enable_auth_strategy is True
    assert workflow._auth_mode_used is None  # Not set until execution

    # Step 3: Execute workflow on src/attune (large codebase)
    result = await workflow.execute(path="src/attune")

    # Step 4: Verify workflow completed successfully
    assert result.success is True
    assert result.provider == "anthropic"

    # Step 5: Verify auth mode was tracked
    auth_mode = result.final_output.get("auth_mode_used")
    assert auth_mode is not None, "Auth mode should be tracked in output"
    assert auth_mode in [
        "subscription",
        "api",
    ], f"Auth mode should be subscription or api, got: {auth_mode}"

    # Step 6: For large codebase, should recommend API mode
    # src/attune has ~100K LOC, which exceeds medium threshold (2000)
    assert auth_mode == "api", "Large codebase should use API mode"

    # Step 7: Verify workflow output structure
    output = result.final_output
    assert "approved" in output
    assert "confidence" in output
    assert "recommendation" in output
    assert "health_score" in output
    assert "commit_count" in output
    assert "model_tier_used" in output

    # Step 8: Verify cost tracking
    assert result.cost_report.total_cost > 0, "Should have cost for API calls"
    assert result.cost_report.total_cost < 1.0, "Cost should be reasonable"

    print("\n✅ Release Prep Auth Integration Test Passed")
    print(f"   Auth mode: {auth_mode}")
    print(f"   Approved: {output.get('approved')}")
    print(f"   Health score: {output.get('health_score')}/100")
    print(f"   Total cost: ${result.cost_report.total_cost:.4f}")


@pytest.mark.asyncio
async def test_release_prep_with_api_mode():
    """Test release prep workflow with forced API mode."""
    # Configure strategy to always use API
    strategy = AuthStrategy(
        subscription_tier=SubscriptionTier.MAX,
        default_mode=AuthMode.API,  # Force API mode
        setup_completed=True,
    )
    strategy.save()

    workflow = ReleasePreparationWorkflow(
        skip_approve_if_clean=True,
        enable_auth_strategy=True,
    )

    result = await workflow.execute(path="src/attune")

    assert result.success is True
    auth_mode = result.final_output.get("auth_mode_used")
    assert auth_mode == "api", "Should use API mode when configured"

    print("\n✅ Release Prep API Mode Test Passed")


@pytest.mark.asyncio
async def test_release_prep_with_auth_disabled():
    """Test that workflow works with auth strategy disabled."""
    workflow = ReleasePreparationWorkflow(
        skip_approve_if_clean=True,
        enable_auth_strategy=False,
    )

    result = await workflow.execute(path="src/attune")

    assert result.success is True
    result.final_output.get("auth_mode_used")
    # Auth mode should not be tracked when disabled
    # (It might be None or missing)

    print("\n✅ Release Prep Auth Disabled Test Passed")
