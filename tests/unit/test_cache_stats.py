"""Tests for Cache Statistics and Performance Reporting

Tests comprehensive cache analysis functionality including:
- CacheHealthScore dataclass
- CacheAnalyzer health calculations
- CacheReporter report generation
- Various cache health scenarios

Copyright 2025 Smart-AI-Memory
Licensed under the Apache License, Version 2.0
"""

from unittest.mock import MagicMock, patch

import pytest

from attune.cache_monitor import CacheStats
from attune.cache_stats import (
    CacheAnalyzer,
    CacheHealthScore,
    CacheReporter,
)

# =========================================================================
# Test CacheHealthScore
# =========================================================================


class TestCacheHealthScore:
    """Tests for CacheHealthScore dataclass."""

    def test_create_health_score(self):
        """Test creating a health score."""
        score = CacheHealthScore(
            cache_name="test_cache",
            hit_rate=0.75,
            health="good",
            confidence="high",
            recommendation="Cache is performing well",
            reasons=["Strong hit rate", "Stable performance"],
        )

        assert score.cache_name == "test_cache"
        assert score.hit_rate == 0.75
        assert score.health == "good"
        assert score.confidence == "high"
        assert "performing well" in score.recommendation
        assert len(score.reasons) == 2

    def test_to_dict(self):
        """Test converting health score to dictionary."""
        score = CacheHealthScore(
            cache_name="ast_parse",
            hit_rate=0.8234,
            health="excellent",
            confidence="medium",
            recommendation="Monitor usage",
            reasons=["Good hit rate"],
        )

        data = score.to_dict()

        assert data["cache_name"] == "ast_parse"
        assert data["hit_rate"] == 0.8234  # Rounded to 4 decimal places
        assert data["health"] == "excellent"
        assert data["confidence"] == "medium"
        assert data["recommendation"] == "Monitor usage"
        assert data["reasons"] == ["Good hit rate"]

    def test_to_dict_rounds_hit_rate(self):
        """Test that to_dict rounds hit rate to 4 decimal places."""
        score = CacheHealthScore(
            cache_name="test",
            hit_rate=0.123456789,
            health="fair",
            confidence="low",
            recommendation="Test",
            reasons=[],
        )

        data = score.to_dict()

        assert data["hit_rate"] == 0.1235  # Rounded


# =========================================================================
# Test CacheAnalyzer - Basic Operations
# =========================================================================


class TestCacheAnalyzerBasic:
    """Tests for basic CacheAnalyzer operations."""

    def test_analyze_cache_not_found(self):
        """Test analyzing a cache that doesn't exist."""
        with patch("attune.cache_stats.CacheMonitor") as mock_monitor_cls:
            mock_monitor = MagicMock()
            mock_monitor.get_stats.return_value = None
            mock_monitor_cls.get_instance.return_value = mock_monitor

            result = CacheAnalyzer.analyze_cache("nonexistent")

            assert result is None

    def test_analyze_cache_success(self):
        """Test analyzing an existing cache."""
        stats = CacheStats(name="test_cache", hits=80, misses=20, max_size=100)

        with patch("attune.cache_stats.CacheMonitor") as mock_monitor_cls:
            mock_monitor = MagicMock()
            mock_monitor.get_stats.return_value = stats
            mock_monitor_cls.get_instance.return_value = mock_monitor

            result = CacheAnalyzer.analyze_cache("test_cache")

            assert result is not None
            assert result.cache_name == "test_cache"
            assert result.hit_rate == 0.8

    def test_analyze_all_empty(self):
        """Test analyzing when no caches exist."""
        with patch("attune.cache_stats.CacheMonitor") as mock_monitor_cls:
            mock_monitor = MagicMock()
            mock_monitor.get_all_stats.return_value = {}
            mock_monitor_cls.get_instance.return_value = mock_monitor

            result = CacheAnalyzer.analyze_all()

            assert result == {}

    def test_analyze_all_multiple_caches(self):
        """Test analyzing multiple caches."""
        stats1 = CacheStats(name="cache1", hits=80, misses=20)
        stats2 = CacheStats(name="cache2", hits=50, misses=50)

        with patch("attune.cache_stats.CacheMonitor") as mock_monitor_cls:
            mock_monitor = MagicMock()
            mock_monitor.get_all_stats.return_value = {"cache1": stats1, "cache2": stats2}
            mock_monitor_cls.get_instance.return_value = mock_monitor

            result = CacheAnalyzer.analyze_all()

            assert len(result) == 2
            assert "cache1" in result
            assert "cache2" in result


# =========================================================================
# Test CacheAnalyzer - Health Calculations
# =========================================================================


class TestCacheAnalyzerHealthCalculations:
    """Tests for health calculation logic."""

    def test_health_low_request_count_excellent(self):
        """Test health calculation with low request count and high hit rate."""
        stats = CacheStats(name="test", hits=8, misses=1)  # 9 requests, 89% hit rate

        result = CacheAnalyzer._calculate_health(stats)

        assert result.health == "excellent"
        assert result.confidence == "low"

    def test_health_low_request_count_good(self):
        """Test health calculation with low request count and good hit rate."""
        stats = CacheStats(name="test", hits=6, misses=3)  # 9 requests, 67% hit rate

        result = CacheAnalyzer._calculate_health(stats)

        assert result.health == "good"
        assert result.confidence == "low"

    def test_health_low_request_count_fair(self):
        """Test health calculation with low request count and fair hit rate."""
        stats = CacheStats(name="test", hits=4, misses=5)  # 9 requests, 44% hit rate

        result = CacheAnalyzer._calculate_health(stats)

        assert result.health == "fair"
        assert result.confidence == "low"

    def test_health_medium_request_count_excellent(self):
        """Test health calculation with medium request count and excellent hit rate."""
        stats = CacheStats(name="test", hits=70, misses=20)  # 90 requests, 78% hit rate

        result = CacheAnalyzer._calculate_health(stats)

        assert result.health == "excellent"
        assert result.confidence == "medium"

    def test_health_medium_request_count_good(self):
        """Test health calculation with medium request count and good hit rate."""
        stats = CacheStats(name="test", hits=50, misses=40)  # 90 requests, 56% hit rate

        result = CacheAnalyzer._calculate_health(stats)

        assert result.health == "good"
        assert result.confidence == "medium"

    def test_health_medium_request_count_fair(self):
        """Test health calculation with medium request count and fair hit rate."""
        stats = CacheStats(name="test", hits=35, misses=55)  # 90 requests, 39% hit rate

        result = CacheAnalyzer._calculate_health(stats)

        assert result.health == "fair"
        assert result.confidence == "medium"

    def test_health_medium_request_count_poor(self):
        """Test health calculation with medium request count and poor hit rate."""
        stats = CacheStats(name="test", hits=20, misses=70)  # 90 requests, 22% hit rate

        result = CacheAnalyzer._calculate_health(stats)

        assert result.health == "poor"
        assert result.confidence == "medium"

    def test_health_high_request_count_excellent(self):
        """Test health calculation with high request count and excellent hit rate."""
        stats = CacheStats(name="test", hits=700, misses=300)  # 1000 requests, 70% hit rate

        result = CacheAnalyzer._calculate_health(stats)

        assert result.health == "excellent"
        assert result.confidence == "high"

    def test_health_high_request_count_good(self):
        """Test health calculation with high request count and good hit rate."""
        stats = CacheStats(name="test", hits=450, misses=550)  # 1000 requests, 45% hit rate

        result = CacheAnalyzer._calculate_health(stats)

        assert result.health == "good"
        assert result.confidence == "high"

    def test_health_high_request_count_fair(self):
        """Test health calculation with high request count and fair hit rate."""
        stats = CacheStats(name="test", hits=250, misses=750)  # 1000 requests, 25% hit rate

        result = CacheAnalyzer._calculate_health(stats)

        assert result.health == "fair"
        assert result.confidence == "high"

    def test_health_high_request_count_poor(self):
        """Test health calculation with high request count and poor hit rate."""
        stats = CacheStats(name="test", hits=100, misses=900)  # 1000 requests, 10% hit rate

        result = CacheAnalyzer._calculate_health(stats)

        assert result.health == "poor"
        assert result.confidence == "high"


# =========================================================================
# Test CacheAnalyzer - Recommendations
# =========================================================================


class TestCacheAnalyzerRecommendations:
    """Tests for recommendation generation."""

    def test_high_hit_rate_high_requests(self):
        """Test recommendation for high hit rate with high request count."""
        stats = CacheStats(name="test", hits=800, misses=200)  # 80% hit rate, 1000 requests

        result = CacheAnalyzer._calculate_health(stats)

        assert "performing well" in result.recommendation
        assert "Strong hit rate" in result.reasons[0]

    def test_high_hit_rate_low_requests(self):
        """Test recommendation for high hit rate with low request count."""
        stats = CacheStats(name="test", hits=8, misses=1)  # 89% hit rate, 9 requests

        result = CacheAnalyzer._calculate_health(stats)

        assert "limited data" in result.recommendation
        assert "Strong hit rate" in result.reasons[0]

    def test_moderate_hit_rate(self):
        """Test recommendation for moderate hit rate."""
        stats = CacheStats(name="test", hits=55, misses=45)  # 55% hit rate

        result = CacheAnalyzer._calculate_health(stats)

        assert "Monitor for patterns" in result.recommendation
        assert "Moderate hit rate" in result.reasons[0]

    def test_low_hit_rate(self):
        """Test recommendation for low hit rate."""
        stats = CacheStats(name="test", hits=25, misses=75)  # 25% hit rate

        result = CacheAnalyzer._calculate_health(stats)

        assert "invalidation strategy" in result.recommendation
        assert "Low hit rate" in result.reasons[0]

    def test_very_low_hit_rate(self):
        """Test recommendation for very low hit rate."""
        stats = CacheStats(name="test", hits=10, misses=990)  # 1% hit rate

        result = CacheAnalyzer._calculate_health(stats)

        assert "disabling" in result.recommendation
        assert "Very low hit rate" in result.reasons[0]

    def test_cache_nearly_full(self):
        """Test recommendation when cache is nearly full."""
        stats = CacheStats(name="test", hits=700, misses=300, size=95, max_size=100)

        result = CacheAnalyzer._calculate_health(stats)

        assert "increasing cache size" in result.recommendation
        assert "nearly full" in result.reasons[-1]

    def test_cache_underutilized(self):
        """Test recommendation when cache is underutilized."""
        stats = CacheStats(name="test", hits=700, misses=300, size=5, max_size=100)

        result = CacheAnalyzer._calculate_health(stats)

        assert "reducing cache size" in result.recommendation
        assert "underutilized" in result.reasons[-1]

    def test_cache_thrashing(self):
        """Test recommendation for cache thrashing (high volume, low hit rate)."""
        stats = CacheStats(name="test", hits=200, misses=1800)  # 10% hit rate, 2000 requests

        result = CacheAnalyzer._calculate_health(stats)

        assert "thrashing" in result.reasons[-1]
        assert "cache lifetime" in result.recommendation


# =========================================================================
# Test CacheReporter - Health Report
# =========================================================================


class TestCacheReporterHealthReport:
    """Tests for health report generation."""

    def test_health_report_no_caches(self):
        """Test health report when no caches registered."""
        with patch.object(CacheAnalyzer, "analyze_all", return_value={}):
            result = CacheReporter.generate_health_report()

            assert "No caches registered" in result

    def test_health_report_single_cache(self):
        """Test health report with single cache."""
        health_score = CacheHealthScore(
            cache_name="test_cache",
            hit_rate=0.75,
            health="good",
            confidence="high",
            recommendation="Monitor performance",
            reasons=["Stable hit rate"],
        )

        with patch.object(CacheAnalyzer, "analyze_all", return_value={"test_cache": health_score}):
            result = CacheReporter.generate_health_report()

            assert "CACHE HEALTH REPORT" in result
            assert "test_cache" in result
            assert "GOOD" in result
            assert "HIGH" in result
            assert "75.0%" in result
            assert "Monitor performance" in result
            assert "SUMMARY" in result
            assert "Total Caches:    1" in result

    def test_health_report_multiple_caches(self):
        """Test health report with multiple caches."""
        scores = {
            "excellent_cache": CacheHealthScore(
                cache_name="excellent_cache",
                hit_rate=0.9,
                health="excellent",
                confidence="high",
                recommendation="Keep it up",
                reasons=[],
            ),
            "poor_cache": CacheHealthScore(
                cache_name="poor_cache",
                hit_rate=0.1,
                health="poor",
                confidence="high",
                recommendation="Consider disabling",
                reasons=[],
            ),
        }

        with patch.object(CacheAnalyzer, "analyze_all", return_value=scores):
            result = CacheReporter.generate_health_report()

            # Excellent should come before poor in sorted output
            assert result.index("excellent_cache") < result.index("poor_cache")
            assert "Excellent:       1" in result
            assert "Poor:            1" in result

    def test_health_report_verbose(self):
        """Test health report with verbose flag."""
        health_score = CacheHealthScore(
            cache_name="test_cache",
            hit_rate=0.75,
            health="good",
            confidence="high",
            recommendation="Monitor performance",
            reasons=["Reason 1", "Reason 2"],
        )

        with patch.object(CacheAnalyzer, "analyze_all", return_value={"test_cache": health_score}):
            result = CacheReporter.generate_health_report(verbose=True)

            assert "- Reason 1" in result
            assert "- Reason 2" in result

    def test_health_report_non_verbose(self):
        """Test health report without verbose flag doesn't show reasons."""
        health_score = CacheHealthScore(
            cache_name="test_cache",
            hit_rate=0.75,
            health="good",
            confidence="high",
            recommendation="Monitor performance",
            reasons=["Reason 1", "Reason 2"],
        )

        with patch.object(CacheAnalyzer, "analyze_all", return_value={"test_cache": health_score}):
            result = CacheReporter.generate_health_report(verbose=False)

            assert "- Reason 1" not in result
            assert "- Reason 2" not in result


# =========================================================================
# Test CacheReporter - Optimization Report
# =========================================================================


class TestCacheReporterOptimizationReport:
    """Tests for optimization report generation."""

    def test_optimization_report_structure(self):
        """Test optimization report has correct structure."""
        with patch("attune.cache_stats.CacheMonitor") as mock_monitor_cls:
            mock_monitor = MagicMock()
            mock_monitor.get_underperformers.return_value = []
            mock_monitor.get_high_performers.return_value = []
            mock_monitor_cls.get_instance.return_value = mock_monitor

            result = CacheReporter.generate_optimization_report()

            assert "CACHE OPTIMIZATION OPPORTUNITIES" in result

    def test_optimization_report_underperformers(self):
        """Test optimization report shows underperformers."""
        low_stats = CacheStats(name="slow_cache", hits=20, misses=80)
        health_score = CacheHealthScore(
            cache_name="slow_cache",
            hit_rate=0.2,
            health="poor",
            confidence="high",
            recommendation="Consider disabling",
            reasons=[],
        )

        with (
            patch("attune.cache_stats.CacheMonitor") as mock_monitor_cls,
            patch.object(CacheAnalyzer, "analyze_cache", return_value=health_score),
        ):
            mock_monitor = MagicMock()
            mock_monitor.get_underperformers.return_value = [low_stats]
            mock_monitor.get_high_performers.return_value = []
            mock_monitor_cls.get_instance.return_value = mock_monitor

            result = CacheReporter.generate_optimization_report()

            assert "LOW-PERFORMING CACHES" in result
            assert "slow_cache" in result
            assert "Consider disabling" in result

    def test_optimization_report_high_performers(self):
        """Test optimization report shows high performers."""
        high_stats = CacheStats(name="fast_cache", hits=800, misses=200)

        with patch("attune.cache_stats.CacheMonitor") as mock_monitor_cls:
            mock_monitor = MagicMock()
            mock_monitor.get_underperformers.return_value = []
            mock_monitor.get_high_performers.return_value = [high_stats]
            mock_monitor_cls.get_instance.return_value = mock_monitor

            result = CacheReporter.generate_optimization_report()

            assert "HIGH-PERFORMING CACHES" in result
            assert "fast_cache" in result
            assert "80.0%" in result


# =========================================================================
# Test CacheReporter - Full Report
# =========================================================================


class TestCacheReporterFullReport:
    """Tests for full report generation."""

    def test_full_report_structure(self):
        """Test full report has all sections."""
        with (
            patch("attune.cache_stats.CacheMonitor") as mock_monitor_cls,
            patch.object(CacheAnalyzer, "analyze_all", return_value={}),
        ):
            mock_monitor = MagicMock()
            mock_monitor.get_report.return_value = "Cache Report"
            mock_monitor.get_size_report.return_value = "Size Report"
            mock_monitor.get_underperformers.return_value = []
            mock_monitor.get_high_performers.return_value = []
            mock_monitor_cls.get_instance.return_value = mock_monitor

            result = CacheReporter.generate_full_report()

            assert "COMPREHENSIVE CACHE ANALYSIS REPORT" in result
            assert "Cache Report" in result
            assert "Size Report" in result
            # When no caches, health report says "No caches registered"
            assert "No caches registered" in result or "CACHE HEALTH REPORT" in result
            assert "CACHE OPTIMIZATION OPPORTUNITIES" in result


# =========================================================================
# Integration Tests
# =========================================================================


class TestIntegration:
    """Integration tests for cache statistics module."""

    def test_complete_analysis_workflow(self):
        """Test complete workflow: register -> record -> analyze -> report."""
        # Create mock stats simulating real cache behavior
        stats = CacheStats(
            name="integration_cache",
            hits=750,
            misses=250,
            size=80,
            max_size=100,
        )

        with patch("attune.cache_stats.CacheMonitor") as mock_monitor_cls:
            mock_monitor = MagicMock()
            mock_monitor.get_stats.return_value = stats
            mock_monitor.get_all_stats.return_value = {"integration_cache": stats}
            mock_monitor.get_underperformers.return_value = []
            mock_monitor.get_high_performers.return_value = [stats]
            mock_monitor.get_report.return_value = "Base Report"
            mock_monitor.get_size_report.return_value = "Size Report"
            mock_monitor_cls.get_instance.return_value = mock_monitor

            # Analyze single cache
            health = CacheAnalyzer.analyze_cache("integration_cache")
            assert health is not None
            assert health.health == "excellent"
            assert health.hit_rate == 0.75

            # Analyze all caches
            all_health = CacheAnalyzer.analyze_all()
            assert "integration_cache" in all_health

            # Generate reports
            health_report = CacheReporter.generate_health_report()
            assert "integration_cache" in health_report

            optimization_report = CacheReporter.generate_optimization_report()
            assert "HIGH-PERFORMING CACHES" in optimization_report

            full_report = CacheReporter.generate_full_report()
            assert "COMPREHENSIVE" in full_report

    def test_health_score_serialization_integration(self):
        """Test health score serialization in report context."""
        stats = CacheStats(name="serialization_test", hits=60, misses=40)

        result = CacheAnalyzer._calculate_health(stats)
        data = result.to_dict()

        # Verify all fields are serializable
        assert isinstance(data["cache_name"], str)
        assert isinstance(data["hit_rate"], float)
        assert isinstance(data["health"], str)
        assert isinstance(data["confidence"], str)
        assert isinstance(data["recommendation"], str)
        assert isinstance(data["reasons"], list)

    def test_boundary_conditions(self):
        """Test health calculation at boundary conditions."""
        # Zero requests
        zero_stats = CacheStats(name="zero", hits=0, misses=0)
        zero_health = CacheAnalyzer._calculate_health(zero_stats)
        assert zero_health.health == "fair"  # 0% hit rate with low confidence
        assert zero_health.confidence == "low"

        # Exactly 10 requests (boundary between low and medium)
        ten_stats = CacheStats(name="ten", hits=8, misses=2)
        ten_health = CacheAnalyzer._calculate_health(ten_stats)
        assert ten_health.confidence == "medium"  # >= 10 requests

        # Exactly 100 requests (boundary between medium and high)
        hundred_stats = CacheStats(name="hundred", hits=60, misses=40)
        hundred_health = CacheAnalyzer._calculate_health(hundred_stats)
        assert hundred_health.confidence == "high"  # >= 100 requests

    def test_all_health_levels(self):
        """Test that all health levels are reachable."""
        health_levels_seen = set()

        test_cases = [
            (90, 10),  # 90% hit rate
            (70, 30),  # 70% hit rate
            (40, 60),  # 40% hit rate
            (10, 90),  # 10% hit rate
        ]

        for hits, misses in test_cases:
            stats = CacheStats(name="test", hits=hits, misses=misses)
            health = CacheAnalyzer._calculate_health(stats)
            health_levels_seen.add(health.health)

        # Should have seen at least 3 of 4 levels
        assert len(health_levels_seen) >= 3


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
