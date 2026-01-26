"""Unit tests for tier routing strategies.

Tests the routing strategy pattern and integration with BaseWorkflow.
"""

import pytest

from empathy_os.workflows.base import ModelTier
from empathy_os.workflows.routing import (
    BalancedRouting,
    CostOptimizedRouting,
    PerformanceOptimizedRouting,
    RoutingContext,
    TierRoutingStrategy,
)


@pytest.mark.unit
class TestRoutingContext:
    """Test RoutingContext dataclass."""

    def test_routing_context_creation(self):
        """Test creating a routing context."""
        context = RoutingContext(
            task_type="code-review:analyze",
            input_size=1000,
            complexity="moderate",
            budget_remaining=50.0,
            latency_sensitivity="medium",
        )

        assert context.task_type == "code-review:analyze"
        assert context.input_size == 1000
        assert context.complexity == "moderate"
        assert context.budget_remaining == 50.0
        assert context.latency_sensitivity == "medium"

    def test_routing_context_all_complexities(self):
        """Test all valid complexity values."""
        for complexity in ["simple", "moderate", "complex"]:
            context = RoutingContext(
                task_type="test",
                input_size=100,
                complexity=complexity,
                budget_remaining=10.0,
                latency_sensitivity="low",
            )
            assert context.complexity == complexity

    def test_routing_context_all_latency_levels(self):
        """Test all valid latency sensitivity values."""
        for latency in ["low", "medium", "high"]:
            context = RoutingContext(
                task_type="test",
                input_size=100,
                complexity="simple",
                budget_remaining=10.0,
                latency_sensitivity=latency,
            )
            assert context.latency_sensitivity == latency


@pytest.mark.unit
class TestCostOptimizedRouting:
    """Test CostOptimizedRouting strategy."""

    def test_simple_task_routes_to_cheap(self):
        """Test that simple tasks route to CHEAP tier."""
        strategy = CostOptimizedRouting()
        context = RoutingContext(
            task_type="summarize",
            input_size=500,
            complexity="simple",
            budget_remaining=100.0,
            latency_sensitivity="low",
        )

        tier = strategy.route(context)
        assert tier == ModelTier.CHEAP

    def test_moderate_task_routes_to_capable(self):
        """Test that moderate tasks route to CAPABLE tier."""
        strategy = CostOptimizedRouting()
        context = RoutingContext(
            task_type="analyze",
            input_size=2000,
            complexity="moderate",
            budget_remaining=100.0,
            latency_sensitivity="medium",
        )

        tier = strategy.route(context)
        assert tier == ModelTier.CAPABLE

    def test_complex_task_routes_to_premium(self):
        """Test that complex tasks route to PREMIUM tier."""
        strategy = CostOptimizedRouting()
        context = RoutingContext(
            task_type="synthesize",
            input_size=5000,
            complexity="complex",
            budget_remaining=100.0,
            latency_sensitivity="low",
        )

        tier = strategy.route(context)
        assert tier == ModelTier.PREMIUM

    def test_can_fallback_from_premium(self):
        """Test that fallback is allowed from PREMIUM."""
        strategy = CostOptimizedRouting()
        assert strategy.can_fallback(ModelTier.PREMIUM) is True

    def test_can_fallback_from_capable(self):
        """Test that fallback is allowed from CAPABLE."""
        strategy = CostOptimizedRouting()
        assert strategy.can_fallback(ModelTier.CAPABLE) is True

    def test_cannot_fallback_from_cheap(self):
        """Test that fallback is NOT allowed from CHEAP."""
        strategy = CostOptimizedRouting()
        assert strategy.can_fallback(ModelTier.CHEAP) is False


@pytest.mark.unit
class TestPerformanceOptimizedRouting:
    """Test PerformanceOptimizedRouting strategy."""

    def test_high_latency_sensitivity_routes_to_premium(self):
        """Test that high latency sensitivity routes to PREMIUM."""
        strategy = PerformanceOptimizedRouting()
        context = RoutingContext(
            task_type="interactive",
            input_size=100,
            complexity="simple",
            budget_remaining=100.0,
            latency_sensitivity="high",
        )

        tier = strategy.route(context)
        assert tier == ModelTier.PREMIUM

    def test_medium_latency_sensitivity_routes_to_capable(self):
        """Test that medium latency sensitivity routes to CAPABLE."""
        strategy = PerformanceOptimizedRouting()
        context = RoutingContext(
            task_type="analyze",
            input_size=1000,
            complexity="moderate",
            budget_remaining=100.0,
            latency_sensitivity="medium",
        )

        tier = strategy.route(context)
        assert tier == ModelTier.CAPABLE

    def test_low_latency_sensitivity_routes_to_capable(self):
        """Test that low latency sensitivity still routes to CAPABLE."""
        strategy = PerformanceOptimizedRouting()
        context = RoutingContext(
            task_type="batch",
            input_size=5000,
            complexity="complex",
            budget_remaining=100.0,
            latency_sensitivity="low",
        )

        tier = strategy.route(context)
        assert tier == ModelTier.CAPABLE

    def test_never_allows_fallback(self):
        """Test that performance strategy never allows fallback."""
        strategy = PerformanceOptimizedRouting()

        # No fallback from any tier
        assert strategy.can_fallback(ModelTier.PREMIUM) is False
        assert strategy.can_fallback(ModelTier.CAPABLE) is False
        assert strategy.can_fallback(ModelTier.CHEAP) is False


@pytest.mark.unit
class TestBalancedRouting:
    """Test BalancedRouting strategy."""

    def test_low_budget_routes_to_cheap(self):
        """Test that low budget routes to CHEAP tier."""
        strategy = BalancedRouting(total_budget=100.0)
        context = RoutingContext(
            task_type="analyze",
            input_size=1000,
            complexity="complex",  # Complex, but budget is low
            budget_remaining=15.0,  # 15% of budget
            latency_sensitivity="medium",
        )

        tier = strategy.route(context)
        assert tier == ModelTier.CHEAP

    def test_high_budget_complex_task_routes_to_premium(self):
        """Test that high budget + complex task routes to PREMIUM."""
        strategy = BalancedRouting(total_budget=100.0)
        context = RoutingContext(
            task_type="synthesize",
            input_size=5000,
            complexity="complex",
            budget_remaining=80.0,  # 80% of budget
            latency_sensitivity="low",
        )

        tier = strategy.route(context)
        assert tier == ModelTier.PREMIUM

    def test_medium_budget_routes_to_capable(self):
        """Test that medium budget routes to CAPABLE."""
        strategy = BalancedRouting(total_budget=100.0)
        context = RoutingContext(
            task_type="analyze",
            input_size=2000,
            complexity="moderate",
            budget_remaining=50.0,  # 50% of budget
            latency_sensitivity="medium",
        )

        tier = strategy.route(context)
        assert tier == ModelTier.CAPABLE

    def test_high_budget_simple_task_routes_to_capable(self):
        """Test that high budget + simple task still routes to CAPABLE."""
        strategy = BalancedRouting(total_budget=100.0)
        context = RoutingContext(
            task_type="summarize",
            input_size=500,
            complexity="simple",  # Simple task doesn't warrant PREMIUM
            budget_remaining=80.0,
            latency_sensitivity="low",
        )

        tier = strategy.route(context)
        assert tier == ModelTier.CAPABLE

    def test_always_allows_fallback(self):
        """Test that balanced strategy always allows fallback."""
        strategy = BalancedRouting(total_budget=100.0)

        assert strategy.can_fallback(ModelTier.PREMIUM) is True
        assert strategy.can_fallback(ModelTier.CAPABLE) is True
        assert strategy.can_fallback(ModelTier.CHEAP) is True


@pytest.mark.unit
class TestTierRoutingStrategyABC:
    """Test the abstract base class contract."""

    def test_strategies_are_subclasses(self):
        """Test that all strategies are subclasses of TierRoutingStrategy."""
        assert issubclass(CostOptimizedRouting, TierRoutingStrategy)
        assert issubclass(PerformanceOptimizedRouting, TierRoutingStrategy)
        assert issubclass(BalancedRouting, TierRoutingStrategy)

    def test_all_strategies_implement_route(self):
        """Test that all strategies implement route() method."""
        strategies = [
            CostOptimizedRouting(),
            PerformanceOptimizedRouting(),
            BalancedRouting(total_budget=100.0),
        ]

        context = RoutingContext(
            task_type="test",
            input_size=100,
            complexity="simple",
            budget_remaining=50.0,
            latency_sensitivity="low",
        )

        for strategy in strategies:
            tier = strategy.route(context)
            assert isinstance(tier, ModelTier)

    def test_all_strategies_implement_can_fallback(self):
        """Test that all strategies implement can_fallback() method."""
        strategies = [
            CostOptimizedRouting(),
            PerformanceOptimizedRouting(),
            BalancedRouting(total_budget=100.0),
        ]

        for strategy in strategies:
            result = strategy.can_fallback(ModelTier.CAPABLE)
            assert isinstance(result, bool)
