"""Coverage boost tests for models/adaptive_routing.py

Targets uncovered adaptive model routing logic and performance analysis to increase
coverage from current baseline to 85%+.

Missing coverage areas:
- ModelPerformance quality_score calculation
- AdaptiveModelRouter._get_default_model() fallback logic
- get_best_model() with various constraints
- recommend_tier_upgrade() decision logic
- get_routing_stats() telemetry analysis
- _analyze_model_performance() metrics calculation
- Edge cases and boundary conditions

Copyright 2026 Smart-AI-Memory
Licensed under Apache 2.0
"""

from unittest.mock import MagicMock

import pytest

from empathy_os.models.adaptive_routing import AdaptiveModelRouter, ModelPerformance


@pytest.mark.unit
class TestModelPerformanceQualityScore:
    """Test ModelPerformance.quality_score property."""

    def test_quality_score_high_success_low_cost(self):
        """Test quality score for high success rate and low cost."""
        perf = ModelPerformance(
            model_id="claude-3-5-haiku-20241022",
            tier="cheap",
            success_rate=1.0,  # 100% success
            avg_latency_ms=500,
            avg_cost=0.001,  # $0.001 per call
            sample_size=100,
        )

        # Quality = (1.0 * 100) - (0.001 * 10) = 100 - 0.01 = 99.99
        assert perf.quality_score == pytest.approx(99.99, rel=1e-2)

    def test_quality_score_medium_success_medium_cost(self):
        """Test quality score for medium success rate and cost."""
        perf = ModelPerformance(
            model_id="claude-sonnet-4-5",
            tier="capable",
            success_rate=0.9,  # 90% success
            avg_latency_ms=800,
            avg_cost=0.01,  # $0.01 per call
            sample_size=50,
        )

        # Quality = (0.9 * 100) - (0.01 * 10) = 90 - 0.1 = 89.9
        assert perf.quality_score == pytest.approx(89.9, rel=1e-2)

    def test_quality_score_low_success_high_cost(self):
        """Test quality score for low success rate and high cost."""
        perf = ModelPerformance(
            model_id="claude-opus-4-5-20251101",
            tier="premium",
            success_rate=0.5,  # 50% success
            avg_latency_ms=1200,
            avg_cost=0.1,  # $0.10 per call
            sample_size=10,
        )

        # Quality = (0.5 * 100) - (0.1 * 10) = 50 - 1 = 49
        assert perf.quality_score == pytest.approx(49.0, rel=1e-2)

    def test_quality_score_perfect_performance(self):
        """Test quality score for perfect performance."""
        perf = ModelPerformance(
            model_id="test-model",
            tier="cheap",
            success_rate=1.0,
            avg_latency_ms=100,
            avg_cost=0.0001,  # Nearly free
            sample_size=1000,
        )

        # Quality = (1.0 * 100) - (0.0001 * 10) = 100 - 0.001 = 99.999
        assert perf.quality_score == pytest.approx(99.999, rel=1e-2)

    def test_quality_score_zero_success(self):
        """Test quality score when success rate is zero."""
        perf = ModelPerformance(
            model_id="failing-model",
            tier="cheap",
            success_rate=0.0,  # Total failure
            avg_latency_ms=500,
            avg_cost=0.01,
            sample_size=10,
        )

        # Quality = (0.0 * 100) - (0.01 * 10) = 0 - 0.1 = -0.1
        assert perf.quality_score == pytest.approx(-0.1, rel=1e-2)

    def test_quality_score_comparison(self):
        """Test that quality scores correctly compare different models."""
        cheap_model = ModelPerformance(
            model_id="haiku",
            tier="cheap",
            success_rate=0.95,
            avg_latency_ms=300,
            avg_cost=0.001,
            sample_size=100,
        )

        premium_model = ModelPerformance(
            model_id="opus",
            tier="premium",
            success_rate=0.98,
            avg_latency_ms=1000,
            avg_cost=0.05,
            sample_size=50,
        )

        # Cheap model: (0.95 * 100) - (0.001 * 10) = 95 - 0.01 = 94.99
        # Premium model: (0.98 * 100) - (0.05 * 10) = 98 - 0.5 = 97.5
        # Premium has higher quality despite higher cost
        assert premium_model.quality_score > cheap_model.quality_score


@pytest.mark.unit
class TestAdaptiveModelRouterDefaultModel:
    """Test AdaptiveModelRouter._get_default_model method."""

    def test_get_default_cheap_model(self):
        """Test getting default cheap tier model."""
        mock_telemetry = MagicMock()
        router = AdaptiveModelRouter(mock_telemetry)

        model_id = router._get_default_model("CHEAP")

        # Should return Haiku model
        assert "haiku" in model_id.lower()

    def test_get_default_capable_model(self):
        """Test getting default capable tier model."""
        mock_telemetry = MagicMock()
        router = AdaptiveModelRouter(mock_telemetry)

        model_id = router._get_default_model("CAPABLE")

        # Should return Sonnet model
        assert "sonnet" in model_id.lower()

    def test_get_default_premium_model(self):
        """Test getting default premium tier model."""
        mock_telemetry = MagicMock()
        router = AdaptiveModelRouter(mock_telemetry)

        model_id = router._get_default_model("PREMIUM")

        # Should return Opus model
        assert "opus" in model_id.lower()

    def test_get_default_model_case_insensitive(self):
        """Test that tier parameter is case-insensitive."""
        mock_telemetry = MagicMock()
        router = AdaptiveModelRouter(mock_telemetry)

        cheap1 = router._get_default_model("cheap")
        cheap2 = router._get_default_model("CHEAP")
        cheap3 = router._get_default_model("Cheap")

        assert cheap1 == cheap2 == cheap3

    def test_get_default_model_unknown_tier_returns_haiku(self):
        """Test that unknown tier falls back to Haiku."""
        mock_telemetry = MagicMock()
        router = AdaptiveModelRouter(mock_telemetry)

        model_id = router._get_default_model("UNKNOWN_TIER")

        # Should fall back to Haiku (cheap default)
        assert model_id == "claude-3-5-haiku-20241022"


@pytest.mark.unit
class TestAdaptiveModelRouterGetBestModel:
    """Test AdaptiveModelRouter.get_best_model method."""

    def test_get_best_model_no_telemetry_returns_default(self):
        """Test that with no telemetry data, returns default model."""
        mock_telemetry = MagicMock()
        mock_telemetry.get_recent_entries.return_value = []

        router = AdaptiveModelRouter(mock_telemetry)

        model = router.get_best_model(
            workflow="code-review",
            stage="analysis",
        )

        # Should return default cheap model
        assert "haiku" in model.lower()

    def test_get_best_model_with_cost_constraint(self):
        """Test get_best_model respects max_cost constraint."""
        mock_telemetry = MagicMock()

        # Mock telemetry with models of different costs (need 10+ calls per model for MIN_SAMPLE_SIZE)
        mock_telemetry.get_recent_entries.return_value = [
            {
                "workflow": "code-review",
                "stage": "analysis",
                "model": "claude-opus-4-5-20251101",
                "success": True,
                "duration_ms": 1200,
                "cost": 0.05,  # Expensive
            }
            for _ in range(10)
        ] + [
            {
                "workflow": "code-review",
                "stage": "analysis",
                "model": "claude-3-5-haiku-20241022",
                "success": True,
                "duration_ms": 300,
                "cost": 0.001,  # Cheap
            }
            for _ in range(10)
        ]

        router = AdaptiveModelRouter(mock_telemetry)

        # Request with low cost constraint
        model = router.get_best_model(
            workflow="code-review",
            stage="analysis",
            max_cost=0.01,  # Excludes Opus
        )

        # Should return Haiku (cheaper model)
        assert "haiku" in model.lower()

    def test_get_best_model_with_latency_constraint(self):
        """Test get_best_model respects max_latency_ms constraint."""
        mock_telemetry = MagicMock()

        # Mock telemetry with models of different latencies (need 10+ calls per model for MIN_SAMPLE_SIZE)
        mock_telemetry.get_recent_entries.return_value = [
            {
                "workflow": "code-review",
                "stage": "analysis",
                "model": "claude-opus-4-5-20251101",
                "success": True,
                "duration_ms": 2000,  # Slow
                "cost": 0.05,
            }
            for _ in range(10)
        ] + [
            {
                "workflow": "code-review",
                "stage": "analysis",
                "model": "claude-3-5-haiku-20241022",
                "success": True,
                "duration_ms": 300,  # Fast
                "cost": 0.001,
            }
            for _ in range(10)
        ]

        router = AdaptiveModelRouter(mock_telemetry)

        # Request with latency constraint
        model = router.get_best_model(
            workflow="code-review",
            stage="analysis",
            max_latency_ms=1000,  # Excludes Opus
        )

        # Should return Haiku (faster model)
        assert "haiku" in model.lower()

    def test_get_best_model_with_success_rate_filter(self):
        """Test get_best_model filters by minimum success rate."""
        mock_telemetry = MagicMock()

        # Mock telemetry with models of different success rates
        # Sonnet: 5/10 = 50% success (below 90% threshold)
        # Haiku: 10/10 = 100% success (meets 90% threshold)
        mock_telemetry.get_recent_entries.return_value = [
            {
                "workflow": "test-gen",
                "stage": "generate",
                "model": "claude-sonnet-4-5",
                "success": True,
                "duration_ms": 800,
                "cost": 0.01,
            }
            for _ in range(5)
        ] + [
            {
                "workflow": "test-gen",
                "stage": "generate",
                "model": "claude-sonnet-4-5",
                "success": False,
                "duration_ms": 500,
                "cost": 0.005,
            }
            for _ in range(5)
        ] + [
            {
                "workflow": "test-gen",
                "stage": "generate",
                "model": "claude-3-5-haiku-20241022",
                "success": True,
                "duration_ms": 300,
                "cost": 0.001,
            }
            for _ in range(10)
        ]

        router = AdaptiveModelRouter(mock_telemetry)

        # Request with high success rate requirement
        model = router.get_best_model(
            workflow="test-gen",
            stage="generate",
            min_success_rate=0.9,  # Requires 90% success - filters out Sonnet
        )

        # Should return Haiku (only model meeting 90% success rate)
        assert "haiku" in model.lower()


@pytest.mark.unit
class TestAdaptiveModelRouterTierUpgrade:
    """Test AdaptiveModelRouter.recommend_tier_upgrade method."""

    def test_recommend_upgrade_no_telemetry(self):
        """Test tier upgrade recommendation with no telemetry."""
        mock_telemetry = MagicMock()
        mock_telemetry.get_recent_entries.return_value = []

        router = AdaptiveModelRouter(mock_telemetry)

        should_upgrade, reason = router.recommend_tier_upgrade(
            workflow="code-review",
            stage="analysis",
        )

        # Should not recommend upgrade without data
        assert should_upgrade is False
        assert "Insufficient data" in reason

    def test_recommend_upgrade_high_failure_rate(self):
        """Test tier upgrade recommended when failure rate is high."""
        mock_telemetry = MagicMock()

        # Mock telemetry with high failure rate (>20%)
        calls = [
            {"workflow": "bug-predict", "stage": "analyze", "model": "claude-3-5-haiku-20241022", "success": False}
            for _ in range(30)  # 30 failures
        ] + [
            {"workflow": "bug-predict", "stage": "analyze", "model": "claude-3-5-haiku-20241022", "success": True}
            for _ in range(10)  # 10 successes
        ]
        # Failure rate: 30/40 = 75% (well above 20% threshold)

        mock_telemetry.get_recent_entries.return_value = calls

        router = AdaptiveModelRouter(mock_telemetry)

        should_upgrade, reason = router.recommend_tier_upgrade(
            workflow="bug-predict",
            stage="analyze",
        )

        # Should recommend upgrade due to high failure rate
        assert should_upgrade is True
        assert "failure rate" in reason.lower() or "high" in reason.lower()

    def test_no_upgrade_with_good_performance(self):
        """Test no upgrade recommended when performance is good."""
        mock_telemetry = MagicMock()

        # Mock telemetry with good performance (<20% failure)
        # Need to spread failures throughout, not bunch at end
        # Pattern: 9 successes, 1 failure, repeated 10 times = 10% failure rate throughout
        calls = []
        for _ in range(10):
            # 9 successes
            calls.extend([
                {"workflow": "code-review", "stage": "lint", "model": "claude-3-5-haiku-20241022", "success": True}
                for _ in range(9)
            ])
            # 1 failure
            calls.append(
                {"workflow": "code-review", "stage": "lint", "model": "claude-3-5-haiku-20241022", "success": False}
            )
        # Total: 90 successes + 10 failures = 100 calls
        # Recent 20: 18 successes + 2 failures = 10% (below 20% threshold)

        mock_telemetry.get_recent_entries.return_value = calls

        router = AdaptiveModelRouter(mock_telemetry)

        should_upgrade, reason = router.recommend_tier_upgrade(
            workflow="code-review",
            stage="lint",
        )

        # Should not recommend upgrade (performance is good even in recent window)
        assert should_upgrade is False


@pytest.mark.unit
class TestAdaptiveModelRouterRoutingStats:
    """Test AdaptiveModelRouter.get_routing_stats method."""

    def test_get_routing_stats_no_data(self):
        """Test routing stats with no telemetry data."""
        mock_telemetry = MagicMock()
        mock_telemetry.get_recent_entries.return_value = []

        router = AdaptiveModelRouter(mock_telemetry)

        stats = router.get_routing_stats(
            workflow="code-review",
            stage="analysis",
        )

        assert isinstance(stats, dict)
        assert "models_used" in stats
        assert stats["models_used"] == []
        assert stats["total_calls"] == 0
        assert stats["avg_cost"] == 0.0
        assert stats["avg_success_rate"] == 0.0

    def test_get_routing_stats_with_data(self):
        """Test routing stats with telemetry data."""
        mock_telemetry = MagicMock()

        # Mock telemetry with various model calls
        mock_telemetry.get_recent_entries.return_value = [
            {
                "workflow": "doc-gen",
                "stage": "write",
                "model": "claude-3-5-haiku-20241022",
                "success": True,
                "input_tokens": 1000,
                "output_tokens": 500,
                "duration_ms": 300,
                "cost": 0.001,
            },
            {
                "workflow": "doc-gen",
                "stage": "write",
                "model": "claude-sonnet-4-5",
                "success": True,
                "input_tokens": 2000,
                "output_tokens": 1000,
                "duration_ms": 800,
                "cost": 0.01,
            },
        ]

        router = AdaptiveModelRouter(mock_telemetry)

        stats = router.get_routing_stats(
            workflow="doc-gen",
            stage="write",
        )

        # Should return stats dictionary with correct structure
        assert isinstance(stats, dict)
        assert "models_used" in stats
        assert len(stats["models_used"]) == 2
        assert stats["total_calls"] == 2


@pytest.mark.unit
class TestAdaptiveModelRouterEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_router_initialization(self):
        """Test that router initializes correctly."""
        mock_telemetry = MagicMock()

        router = AdaptiveModelRouter(mock_telemetry)

        assert router.telemetry is mock_telemetry

    def test_model_performance_with_recent_failures(self):
        """Test ModelPerformance with recent_failures tracking."""
        perf = ModelPerformance(
            model_id="test-model",
            tier="cheap",
            success_rate=0.8,
            avg_latency_ms=500,
            avg_cost=0.01,
            sample_size=100,
            recent_failures=5,  # 5 recent failures
        )

        assert perf.recent_failures == 5
        assert perf.success_rate == 0.8

    def test_model_performance_default_recent_failures(self):
        """Test that recent_failures defaults to 0."""
        perf = ModelPerformance(
            model_id="test-model",
            tier="cheap",
            success_rate=1.0,
            avg_latency_ms=500,
            avg_cost=0.01,
            sample_size=100,
        )

        assert perf.recent_failures == 0

    def test_get_best_model_empty_workflow_stage(self):
        """Test get_best_model with empty workflow/stage names."""
        mock_telemetry = MagicMock()
        mock_telemetry.get_recent_entries.return_value = []

        router = AdaptiveModelRouter(mock_telemetry)

        # Should handle empty strings gracefully
        model = router.get_best_model(workflow="", stage="")

        assert isinstance(model, str)
        assert len(model) > 0  # Returns default model

    def test_quality_score_with_extreme_values(self):
        """Test quality_score with extreme cost values."""
        # Very expensive model
        expensive = ModelPerformance(
            model_id="expensive",
            tier="premium",
            success_rate=1.0,
            avg_latency_ms=1000,
            avg_cost=10.0,  # $10 per call!
            sample_size=10,
        )

        # Quality = (1.0 * 100) - (10.0 * 10) = 100 - 100 = 0
        assert expensive.quality_score == pytest.approx(0.0, rel=1e-2)

        # Very cheap model
        cheap = ModelPerformance(
            model_id="cheap",
            tier="cheap",
            success_rate=0.5,
            avg_latency_ms=100,
            avg_cost=0.00001,  # Nearly free
            sample_size=1000,
        )

        # Quality = (0.5 * 100) - (0.00001 * 10) = 50 - 0.0001 ≈ 50
        assert cheap.quality_score == pytest.approx(50.0, rel=1e-2)


@pytest.mark.unit
class TestAdaptiveModelRouterIntegration:
    """Integration-style tests combining multiple components."""

    def test_full_routing_workflow(self):
        """Test complete routing workflow from stats to recommendation."""
        mock_telemetry = MagicMock()

        # Simulate realistic telemetry data (need 10+ entries for MIN_SAMPLE_SIZE)
        mock_telemetry.get_recent_entries.return_value = [
            {
                "workflow": "test-workflow",
                "stage": "test-stage",
                "model": "claude-3-5-haiku-20241022",
                "success": True,
                "duration_ms": 250 + (i * 10),  # Vary slightly
                "cost": 0.001,
            }
            for i in range(10)
        ]

        router = AdaptiveModelRouter(mock_telemetry)

        # Get best model
        best_model = router.get_best_model(
            workflow="test-workflow",
            stage="test-stage",
        )

        # Get routing stats
        stats = router.get_routing_stats(
            workflow="test-workflow",
            stage="test-stage",
        )

        # Check tier upgrade recommendation
        should_upgrade, reason = router.recommend_tier_upgrade(
            workflow="test-workflow",
            stage="test-stage",
        )

        # All operations should complete successfully
        assert isinstance(best_model, str)
        assert isinstance(stats, dict)
        assert isinstance(should_upgrade, bool)
        assert isinstance(reason, str)
