"""Unit tests for leverage point analysis module.

This test suite provides comprehensive coverage for the leverage point analyzer,
which identifies high-impact intervention points in systems based on Donella
Meadows's systems thinking framework.

Copyright 2025 Smart-AI-Memory
Licensed under the Apache License, Version 2.0
"""

import pytest

from attune.leverage_points import (
    LeverageLevel,
    LeveragePoint,
    LeveragePointAnalyzer,
)


@pytest.mark.unit
class TestLeverageLevel:
    """Test suite for LeverageLevel IntEnum."""

    def test_enum_values_exist(self):
        """Test that all 12 leverage level values are defined."""
        assert LeverageLevel.PARAMETERS == 1
        assert LeverageLevel.BUFFERS == 2
        assert LeverageLevel.STOCK_FLOW == 3
        assert LeverageLevel.DELAYS == 4
        assert LeverageLevel.BALANCING_LOOPS == 5
        assert LeverageLevel.REINFORCING_LOOPS == 6
        assert LeverageLevel.INFORMATION_FLOWS == 7
        assert LeverageLevel.RULES == 8
        assert LeverageLevel.SELF_ORGANIZATION == 9
        assert LeverageLevel.GOALS == 10
        assert LeverageLevel.PARADIGM == 11
        assert LeverageLevel.TRANSCEND_PARADIGM == 12

    def test_enum_is_int_enum(self):
        """Test that LeverageLevel is an IntEnum."""
        assert isinstance(LeverageLevel.PARAMETERS.value, int)
        assert isinstance(LeverageLevel.PARADIGM.value, int)

    def test_enum_ordering_by_effectiveness(self):
        """Test that higher numbers represent more effective leverage points."""
        # Most effective
        assert LeverageLevel.TRANSCEND_PARADIGM > LeverageLevel.PARADIGM
        assert LeverageLevel.PARADIGM > LeverageLevel.GOALS

        # Least effective
        assert LeverageLevel.PARAMETERS < LeverageLevel.BUFFERS
        assert LeverageLevel.BUFFERS < LeverageLevel.STOCK_FLOW

    def test_enum_can_be_compared_to_int(self):
        """Test that enum values can be compared to integers."""
        assert LeverageLevel.PARAMETERS == 1
        assert LeverageLevel.TRANSCEND_PARADIGM == 12
        assert LeverageLevel.PARADIGM > 10


@pytest.mark.unit
class TestLeveragePoint:
    """Test suite for LeveragePoint dataclass."""

    def test_create_leverage_point_with_required_fields(self):
        """Test creating leverage point with only required fields."""
        point = LeveragePoint(
            level=LeverageLevel.PARADIGM,
            description="Shift from tool to collaborator",
            problem_domain="trust",
        )

        assert point.level == LeverageLevel.PARADIGM
        assert point.description == "Shift from tool to collaborator"
        assert point.problem_domain == "trust"
        assert point.impact_potential == 0.5
        assert point.implementation_difficulty == 0.5
        assert point.current_state is None
        assert point.proposed_intervention is None
        assert point.expected_outcomes == []
        assert point.risks == []

    def test_create_leverage_point_with_all_fields(self):
        """Test creating leverage point with all fields specified."""
        point = LeveragePoint(
            level=LeverageLevel.INFORMATION_FLOWS,
            description="Increase transparency",
            problem_domain="trust",
            impact_potential=0.8,
            implementation_difficulty=0.3,
            current_state="Black box AI decisions",
            proposed_intervention="Show reasoning chains",
            expected_outcomes=["Users understand AI", "Trust increases"],
            risks=["Performance overhead", "Information overload"],
        )

        assert point.level == LeverageLevel.INFORMATION_FLOWS
        assert point.impact_potential == 0.8
        assert point.implementation_difficulty == 0.3
        assert point.current_state == "Black box AI decisions"
        assert point.proposed_intervention == "Show reasoning chains"
        assert len(point.expected_outcomes) == 2
        assert len(point.risks) == 2

    def test_leverage_point_impact_potential_range(self):
        """Test that impact potential is in 0.0-1.0 range."""
        point = LeveragePoint(
            level=LeverageLevel.GOALS,
            description="Test",
            problem_domain="test",
            impact_potential=0.9,
        )
        assert 0.0 <= point.impact_potential <= 1.0

    def test_leverage_point_implementation_difficulty_range(self):
        """Test that implementation difficulty is in 0.0-1.0 range."""
        point = LeveragePoint(
            level=LeverageLevel.PARAMETERS,
            description="Test",
            problem_domain="test",
            implementation_difficulty=0.2,
        )
        assert 0.0 <= point.implementation_difficulty <= 1.0


@pytest.mark.unit
class TestLeveragePointAnalyzerInit:
    """Test suite for LeveragePointAnalyzer initialization."""

    def test_analyzer_initializes_with_empty_points(self):
        """Test that analyzer starts with empty identified_points list."""
        analyzer = LeveragePointAnalyzer()
        assert analyzer.identified_points == []

    def test_multiple_analyzers_have_independent_state(self):
        """Test that multiple analyzer instances don't share state."""
        analyzer1 = LeveragePointAnalyzer()
        analyzer2 = LeveragePointAnalyzer()

        # Add point to analyzer1
        problem = {"class": "test", "description": "test problem"}
        analyzer1.find_leverage_points(problem)

        # analyzer2 should still be empty
        assert len(analyzer1.identified_points) > 0
        assert len(analyzer2.identified_points) == 0


@pytest.mark.unit
class TestFindLeveragePoints:
    """Test suite for finding leverage points."""

    def test_find_leverage_points_for_documentation_problem(self):
        """Test finding leverage points for documentation problems."""
        analyzer = LeveragePointAnalyzer()
        problem = {
            "class": "documentation_burden",
            "description": "Developers spend 40% time on docs",
            "instances": 18,
        }

        points = analyzer.find_leverage_points(problem)

        assert len(points) > 0
        assert all(isinstance(p, LeveragePoint) for p in points)
        assert any(p.problem_domain == "documentation" for p in points)

    def test_find_leverage_points_for_trust_problem(self):
        """Test finding leverage points for trust problems."""
        analyzer = LeveragePointAnalyzer()
        problem = {
            "class": "trust_deficit",
            "description": "Users don't trust AI recommendations",
            "instances": 50,
        }

        points = analyzer.find_leverage_points(problem)

        assert len(points) > 0
        assert any(p.problem_domain == "trust" for p in points)

    def test_find_leverage_points_for_efficiency_problem(self):
        """Test finding leverage points for efficiency problems."""
        analyzer = LeveragePointAnalyzer()
        problem = {
            "class": "efficiency_bottleneck",
            "description": "Process is too slow",
        }

        points = analyzer.find_leverage_points(problem)

        assert len(points) > 0
        assert any(p.problem_domain == "efficiency" for p in points)

    def test_find_leverage_points_for_unknown_problem_type(self):
        """Test that generic analysis is used for unknown problem types."""
        analyzer = LeveragePointAnalyzer()
        problem = {
            "class": "unknown_issue",
            "description": "Something is wrong",
        }

        points = analyzer.find_leverage_points(problem)

        assert len(points) > 0
        assert any(p.problem_domain == "unknown_issue" for p in points)

    def test_find_leverage_points_returns_ranked_list(self):
        """Test that returned points are ranked by effectiveness."""
        analyzer = LeveragePointAnalyzer()
        problem = {
            "class": "documentation_burden",
            "description": "Too much documentation work",
        }

        points = analyzer.find_leverage_points(problem)

        # Verify descending order (highest level first)
        for i in range(len(points) - 1):
            assert points[i].level >= points[i + 1].level

    def test_find_leverage_points_stores_in_identified_points(self):
        """Test that found points are stored in identified_points."""
        analyzer = LeveragePointAnalyzer()
        problem = {"class": "test", "description": "test problem"}

        points = analyzer.find_leverage_points(problem)

        assert len(analyzer.identified_points) == len(points)
        assert analyzer.identified_points == points

    def test_find_leverage_points_accumulates_across_calls(self):
        """Test that multiple calls accumulate points."""
        analyzer = LeveragePointAnalyzer()

        problem1 = {"class": "documentation_burden", "description": "docs"}
        problem2 = {"class": "trust_deficit", "description": "trust"}

        points1 = analyzer.find_leverage_points(problem1)
        points2 = analyzer.find_leverage_points(problem2)

        total_points = len(points1) + len(points2)
        assert len(analyzer.identified_points) == total_points

    def test_documentation_problem_keyword_in_description(self):
        """Test that 'documentation' keyword in description triggers doc analysis."""
        analyzer = LeveragePointAnalyzer()
        problem = {
            "class": "other_issue",
            "description": "documentation is taking too long",
        }

        points = analyzer.find_leverage_points(problem)
        assert any(p.problem_domain == "documentation" for p in points)

    def test_trust_problem_keyword_in_description(self):
        """Test that 'trust' keyword in description triggers trust analysis."""
        analyzer = LeveragePointAnalyzer()
        problem = {
            "class": "other_issue",
            "description": "users have trust issues with system",
        }

        points = analyzer.find_leverage_points(problem)
        assert any(p.problem_domain == "trust" for p in points)

    def test_efficiency_problem_keyword_in_description(self):
        """Test that 'speed' keyword triggers efficiency analysis."""
        analyzer = LeveragePointAnalyzer()
        problem = {
            "class": "other_issue",
            "description": "system speed is too slow",
        }

        points = analyzer.find_leverage_points(problem)
        assert any(p.problem_domain == "efficiency" for p in points)


@pytest.mark.unit
class TestRankByEffectiveness:
    """Test suite for ranking leverage points."""

    def test_rank_by_effectiveness_sorts_descending(self):
        """Test that ranking sorts by level in descending order."""
        analyzer = LeveragePointAnalyzer()

        points = [
            LeveragePoint(LeverageLevel.PARAMETERS, "Low", "test"),
            LeveragePoint(LeverageLevel.PARADIGM, "High", "test"),
            LeveragePoint(LeverageLevel.GOALS, "Medium", "test"),
        ]

        ranked = analyzer.rank_by_effectiveness(points)

        assert ranked[0].level == LeverageLevel.PARADIGM
        assert ranked[1].level == LeverageLevel.GOALS
        assert ranked[2].level == LeverageLevel.PARAMETERS

    def test_rank_by_effectiveness_preserves_all_points(self):
        """Test that ranking preserves all points."""
        analyzer = LeveragePointAnalyzer()

        points = [
            LeveragePoint(LeverageLevel.PARAMETERS, "P1", "test"),
            LeveragePoint(LeverageLevel.BUFFERS, "P2", "test"),
            LeveragePoint(LeverageLevel.GOALS, "P3", "test"),
        ]

        ranked = analyzer.rank_by_effectiveness(points)
        assert len(ranked) == len(points)

    def test_rank_by_effectiveness_handles_equal_levels(self):
        """Test ranking when multiple points have same level."""
        analyzer = LeveragePointAnalyzer()

        points = [
            LeveragePoint(LeverageLevel.PARADIGM, "P1", "test"),
            LeveragePoint(LeverageLevel.PARADIGM, "P2", "test"),
            LeveragePoint(LeverageLevel.PARAMETERS, "P3", "test"),
        ]

        ranked = analyzer.rank_by_effectiveness(points)

        # Both PARADIGM points should come before PARAMETERS
        assert ranked[0].level == LeverageLevel.PARADIGM
        assert ranked[1].level == LeverageLevel.PARADIGM
        assert ranked[2].level == LeverageLevel.PARAMETERS

    def test_rank_by_effectiveness_handles_empty_list(self):
        """Test that ranking handles empty list gracefully."""
        analyzer = LeveragePointAnalyzer()
        ranked = analyzer.rank_by_effectiveness([])
        assert ranked == []


@pytest.mark.unit
class TestGetTopLeveragePoints:
    """Test suite for getting top leverage points."""

    def test_get_top_leverage_points_returns_n_points(self):
        """Test that get_top_leverage_points returns requested number."""
        analyzer = LeveragePointAnalyzer()

        # Add some points
        problem = {"class": "documentation_burden", "description": "docs"}
        analyzer.find_leverage_points(problem)

        top_3 = analyzer.get_top_leverage_points(n=3)
        assert len(top_3) <= 3

    def test_get_top_leverage_points_returns_highest_levels(self):
        """Test that top points have highest leverage levels."""
        analyzer = LeveragePointAnalyzer()

        # Add points manually
        analyzer.identified_points = [
            LeveragePoint(LeverageLevel.PARAMETERS, "P1", "test"),
            LeveragePoint(LeverageLevel.PARADIGM, "P2", "test"),
            LeveragePoint(LeverageLevel.GOALS, "P3", "test"),
            LeveragePoint(LeverageLevel.BUFFERS, "P4", "test"),
        ]

        top_2 = analyzer.get_top_leverage_points(n=2)

        assert len(top_2) == 2
        assert top_2[0].level == LeverageLevel.PARADIGM
        assert top_2[1].level == LeverageLevel.GOALS

    def test_get_top_leverage_points_with_min_level(self):
        """Test filtering by minimum leverage level."""
        analyzer = LeveragePointAnalyzer()

        analyzer.identified_points = [
            LeveragePoint(LeverageLevel.PARAMETERS, "P1", "test"),
            LeveragePoint(LeverageLevel.PARADIGM, "P2", "test"),
            LeveragePoint(LeverageLevel.GOALS, "P3", "test"),
            LeveragePoint(LeverageLevel.INFORMATION_FLOWS, "P4", "test"),
        ]

        # Only get points at GOALS level or higher
        top = analyzer.get_top_leverage_points(n=5, min_level=LeverageLevel.GOALS)

        assert all(p.level >= LeverageLevel.GOALS for p in top)
        assert len(top) == 2  # Only PARADIGM and GOALS

    def test_get_top_leverage_points_handles_empty_list(self):
        """Test that get_top returns empty when no points identified."""
        analyzer = LeveragePointAnalyzer()
        top = analyzer.get_top_leverage_points(n=3)
        assert top == []

    def test_get_top_leverage_points_default_n_is_3(self):
        """Test that default n parameter is 3."""
        analyzer = LeveragePointAnalyzer()

        analyzer.identified_points = [
            LeveragePoint(LeverageLevel.PARAMETERS, f"P{i}", "test") for i in range(10)
        ]

        top = analyzer.get_top_leverage_points()
        assert len(top) == 3


@pytest.mark.unit
class TestAnalyzeInterventionFeasibility:
    """Test suite for intervention feasibility analysis."""

    def test_analyze_intervention_feasibility_returns_dict(self):
        """Test that feasibility analysis returns a dictionary."""
        analyzer = LeveragePointAnalyzer()

        point = LeveragePoint(
            level=LeverageLevel.PARADIGM,
            description="Test",
            problem_domain="test",
            impact_potential=0.9,
            implementation_difficulty=0.8,
        )

        result = analyzer.analyze_intervention_feasibility(point)

        assert isinstance(result, dict)
        assert "leverage_level" in result
        assert "impact_potential" in result
        assert "implementation_difficulty" in result
        assert "feasibility_score" in result
        assert "recommendation" in result
        assert "risks" in result
        assert "expected_outcomes" in result

    def test_feasibility_score_calculation(self):
        """Test that feasibility score is calculated correctly."""
        analyzer = LeveragePointAnalyzer()

        point = LeveragePoint(
            level=LeverageLevel.INFORMATION_FLOWS,
            description="Test",
            problem_domain="test",
            impact_potential=0.8,
            implementation_difficulty=0.4,
        )

        result = analyzer.analyze_intervention_feasibility(point)

        expected_score = 0.8 / 0.4
        assert result["feasibility_score"] == expected_score

    def test_feasibility_handles_zero_difficulty(self):
        """Test that zero difficulty doesn't cause division by zero."""
        analyzer = LeveragePointAnalyzer()

        point = LeveragePoint(
            level=LeverageLevel.PARAMETERS,
            description="Test",
            problem_domain="test",
            impact_potential=0.5,
            implementation_difficulty=0.0,
        )

        result = analyzer.analyze_intervention_feasibility(point)

        # Should use max(difficulty, 0.1) to avoid division by zero
        expected_score = 0.5 / 0.1
        assert result["feasibility_score"] == expected_score

    def test_highly_recommended_threshold(self):
        """Test that high feasibility score gets HIGHLY RECOMMENDED."""
        analyzer = LeveragePointAnalyzer()

        point = LeveragePoint(
            level=LeverageLevel.INFORMATION_FLOWS,
            description="Test",
            problem_domain="test",
            impact_potential=0.9,
            implementation_difficulty=0.5,  # Score: 1.8
        )

        result = analyzer.analyze_intervention_feasibility(point)
        assert "HIGHLY RECOMMENDED" in result["recommendation"]

    def test_recommended_threshold(self):
        """Test that medium feasibility score gets RECOMMENDED."""
        analyzer = LeveragePointAnalyzer()

        point = LeveragePoint(
            level=LeverageLevel.GOALS,
            description="Test",
            problem_domain="test",
            impact_potential=0.6,
            implementation_difficulty=0.5,  # Score: 1.2
        )

        result = analyzer.analyze_intervention_feasibility(point)
        assert "RECOMMENDED" in result["recommendation"]

    def test_consider_threshold(self):
        """Test that low-medium feasibility score gets CONSIDER."""
        analyzer = LeveragePointAnalyzer()

        point = LeveragePoint(
            level=LeverageLevel.PARADIGM,
            description="Test",
            problem_domain="test",
            impact_potential=0.7,
            implementation_difficulty=0.9,  # Score: 0.78
        )

        result = analyzer.analyze_intervention_feasibility(point)
        assert "CONSIDER" in result["recommendation"]

    def test_caution_threshold(self):
        """Test that low feasibility score gets CAUTION."""
        analyzer = LeveragePointAnalyzer()

        point = LeveragePoint(
            level=LeverageLevel.PARADIGM,
            description="Test",
            problem_domain="test",
            impact_potential=0.4,
            implementation_difficulty=0.9,  # Score: 0.44
        )

        result = analyzer.analyze_intervention_feasibility(point)
        assert "CAUTION" in result["recommendation"]

    def test_feasibility_includes_expected_outcomes(self):
        """Test that feasibility analysis includes expected outcomes."""
        analyzer = LeveragePointAnalyzer()

        point = LeveragePoint(
            level=LeverageLevel.GOALS,
            description="Test",
            problem_domain="test",
            expected_outcomes=["Outcome 1", "Outcome 2"],
        )

        result = analyzer.analyze_intervention_feasibility(point)
        assert result["expected_outcomes"] == ["Outcome 1", "Outcome 2"]

    def test_feasibility_includes_risks(self):
        """Test that feasibility analysis includes risks."""
        analyzer = LeveragePointAnalyzer()

        point = LeveragePoint(
            level=LeverageLevel.PARADIGM,
            description="Test",
            problem_domain="test",
            risks=["Risk 1", "Risk 2"],
        )

        result = analyzer.analyze_intervention_feasibility(point)
        assert result["risks"] == ["Risk 1", "Risk 2"]


@pytest.mark.unit
class TestReset:
    """Test suite for analyzer reset functionality."""

    def test_reset_clears_identified_points(self):
        """Test that reset clears identified_points list."""
        analyzer = LeveragePointAnalyzer()

        # Add some points
        problem = {"class": "test", "description": "test problem"}
        analyzer.find_leverage_points(problem)

        assert len(analyzer.identified_points) > 0

        # Reset
        analyzer.reset()

        assert analyzer.identified_points == []

    def test_reset_allows_reuse(self):
        """Test that analyzer can be reused after reset."""
        analyzer = LeveragePointAnalyzer()

        # First use
        problem1 = {"class": "test1", "description": "first problem"}
        points1 = analyzer.find_leverage_points(problem1)
        assert len(analyzer.identified_points) == len(points1)

        # Reset
        analyzer.reset()

        # Second use
        problem2 = {"class": "test2", "description": "second problem"}
        points2 = analyzer.find_leverage_points(problem2)

        # Should only have points from second use
        assert len(analyzer.identified_points) == len(points2)


@pytest.mark.unit
class TestDocumentationAnalysis:
    """Test suite for documentation problem analysis."""

    def test_documentation_analysis_includes_paradigm_shift(self):
        """Test that doc analysis includes paradigm-level intervention."""
        analyzer = LeveragePointAnalyzer()
        problem = {"class": "documentation_burden", "description": "docs"}

        points = analyzer.find_leverage_points(problem)

        paradigm_points = [p for p in points if p.level == LeverageLevel.PARADIGM]
        assert len(paradigm_points) > 0

    def test_documentation_analysis_includes_goal_change(self):
        """Test that doc analysis includes goals-level intervention."""
        analyzer = LeveragePointAnalyzer()
        problem = {"class": "documentation_burden", "description": "docs"}

        points = analyzer.find_leverage_points(problem)

        goal_points = [p for p in points if p.level == LeverageLevel.GOALS]
        assert len(goal_points) > 0

    def test_documentation_analysis_includes_self_organization(self):
        """Test that doc analysis includes self-organization intervention."""
        analyzer = LeveragePointAnalyzer()
        problem = {"class": "documentation_burden", "description": "docs"}

        points = analyzer.find_leverage_points(problem)

        self_org_points = [p for p in points if p.level == LeverageLevel.SELF_ORGANIZATION]
        assert len(self_org_points) > 0

    def test_documentation_analysis_includes_parameters(self):
        """Test that doc analysis includes parameter-level intervention."""
        analyzer = LeveragePointAnalyzer()
        problem = {"class": "documentation_burden", "description": "docs"}

        points = analyzer.find_leverage_points(problem)

        param_points = [p for p in points if p.level == LeverageLevel.PARAMETERS]
        assert len(param_points) > 0


@pytest.mark.unit
class TestTrustAnalysis:
    """Test suite for trust problem analysis."""

    def test_trust_analysis_includes_paradigm_shift(self):
        """Test that trust analysis includes paradigm-level intervention."""
        analyzer = LeveragePointAnalyzer()
        problem = {"class": "trust_deficit", "description": "trust issues"}

        points = analyzer.find_leverage_points(problem)

        paradigm_points = [p for p in points if p.level == LeverageLevel.PARADIGM]
        assert len(paradigm_points) > 0

    def test_trust_analysis_includes_information_flows(self):
        """Test that trust analysis includes information flow intervention."""
        analyzer = LeveragePointAnalyzer()
        problem = {"class": "trust_deficit", "description": "trust issues"}

        points = analyzer.find_leverage_points(problem)

        info_points = [p for p in points if p.level == LeverageLevel.INFORMATION_FLOWS]
        assert len(info_points) > 0

    def test_trust_analysis_includes_reinforcing_loops(self):
        """Test that trust analysis includes reinforcing feedback loops."""
        analyzer = LeveragePointAnalyzer()
        problem = {"class": "trust_deficit", "description": "trust issues"}

        points = analyzer.find_leverage_points(problem)

        loop_points = [p for p in points if p.level == LeverageLevel.REINFORCING_LOOPS]
        assert len(loop_points) > 0


@pytest.mark.unit
class TestEfficiencyAnalysis:
    """Test suite for efficiency problem analysis."""

    def test_efficiency_analysis_includes_goal_redefinition(self):
        """Test that efficiency analysis includes goals-level intervention."""
        analyzer = LeveragePointAnalyzer()
        problem = {"class": "efficiency_bottleneck", "description": "too slow"}

        points = analyzer.find_leverage_points(problem)

        goal_points = [p for p in points if p.level == LeverageLevel.GOALS]
        assert len(goal_points) > 0

    def test_efficiency_analysis_includes_delays(self):
        """Test that efficiency analysis includes delay reduction."""
        analyzer = LeveragePointAnalyzer()
        problem = {"class": "efficiency_bottleneck", "description": "too slow"}

        points = analyzer.find_leverage_points(problem)

        delay_points = [p for p in points if p.level == LeverageLevel.DELAYS]
        assert len(delay_points) > 0


@pytest.mark.unit
class TestGenericAnalysis:
    """Test suite for generic problem analysis."""

    def test_generic_analysis_includes_paradigm_shift(self):
        """Test that generic analysis includes paradigm-level intervention."""
        analyzer = LeveragePointAnalyzer()
        problem = {"class": "unknown_issue", "description": "something wrong"}

        points = analyzer.find_leverage_points(problem)

        paradigm_points = [p for p in points if p.level == LeverageLevel.PARADIGM]
        assert len(paradigm_points) > 0

    def test_generic_analysis_includes_information_flows(self):
        """Test that generic analysis includes information flow intervention."""
        analyzer = LeveragePointAnalyzer()
        problem = {"class": "unknown_issue", "description": "something wrong"}

        points = analyzer.find_leverage_points(problem)

        info_points = [p for p in points if p.level == LeverageLevel.INFORMATION_FLOWS]
        assert len(info_points) > 0
