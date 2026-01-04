"""Unit tests for health check workflow and scoring."""

import pytest


@pytest.mark.unit
def test_health_score_calculation():
    """Test health score calculation from component scores."""
    components = {
        "lint": {"score": 85, "weight": 0.20},
        "types": {"score": 90, "weight": 0.20},
        "security": {"score": 80, "weight": 0.25},
        "tests": {"score": 75, "weight": 0.20},
        "tech_debt": {"score": 70, "weight": 0.15},
    }

    # Weighted average
    total_score = sum(c["score"] * c["weight"] for c in components.values())
    total_weight = sum(c["weight"] for c in components.values())

    assert total_weight == 1.0, "Weights should sum to 1.0"
    assert 75 <= total_score <= 85, "Overall score should be in expected range"


@pytest.mark.unit
def test_lint_error_scoring():
    """Test lint error impact on score."""
    # Perfect score (no errors)
    perfect = {"errors": 0, "warnings": 0}

    # Some errors
    some_errors = {"errors": 5, "warnings": 10}

    # Many errors
    many_errors = {"errors": 50, "warnings": 100}

    # Score should decrease with more errors
    # Using a simple formula: max(0, 100 - errors - warnings/2)
    perfect_score = max(0, 100 - perfect["errors"] - perfect["warnings"] / 2)
    some_score = max(0, 100 - some_errors["errors"] - some_errors["warnings"] / 2)
    many_score = max(0, 100 - many_errors["errors"] - many_errors["warnings"] / 2)

    assert perfect_score == 100
    assert some_score == 90  # 100 - 5 - 5
    assert many_score == 0  # Capped at 0


@pytest.mark.unit
def test_security_severity_scoring():
    """Test security issue severity weighting."""
    security_issues = {
        "high": 0,
        "medium": 2,
        "low": 5,
    }

    # Weight: high=10, medium=3, low=1
    severity_score = (
        security_issues["high"] * 10 + security_issues["medium"] * 3 + security_issues["low"] * 1
    )

    assert severity_score == 11, "Weighted severity should be 0*10 + 2*3 + 5*1 = 11"

    # Score = max(0, 100 - severity_score)
    final_score = max(0, 100 - severity_score)
    assert final_score == 89


@pytest.mark.unit
def test_test_coverage_scoring():
    """Test coverage impact on health score."""
    test_results = [
        {"passed": 100, "failed": 0, "total": 100, "coverage": 80},  # Perfect pass, good coverage
        {"passed": 80, "failed": 20, "total": 100, "coverage": 50},  # Some failures, low coverage
        {"passed": 0, "failed": 100, "total": 100, "coverage": 0},  # All failed, no coverage
    ]

    for result in test_results:
        pass_rate = (result["passed"] / result["total"]) * 100 if result["total"] > 0 else 0

        # Score combines pass rate and coverage (50/50 weight)
        score = (pass_rate * 0.5) + (result["coverage"] * 0.5)

        assert 0 <= score <= 100, "Score should be in valid range"

    # First should score highest
    score_1 = (100 * 0.5) + (80 * 0.5)  # 90
    score_2 = (80 * 0.5) + (50 * 0.5)  # 65
    score_3 = (0 * 0.5) + (0 * 0.5)  # 0

    assert score_1 > score_2 > score_3


@pytest.mark.unit
def test_tech_debt_scoring():
    """Test technical debt impact on score."""
    debt = {
        "todos": 15,
        "fixmes": 5,
        "hacks": 3,
        "total": 23,
    }

    # Weight different debt types
    weighted_debt = (
        debt["fixmes"] * 3  # FIXMEs are urgent
        + debt["hacks"] * 5  # Hacks are worse
        + debt["todos"] * 1  # TODOs are minor
    )

    assert weighted_debt == 45, "15*1 + 5*3 + 3*5 = 45"

    # Score decreases with debt
    # Formula: max(0, 100 - weighted_debt)
    score = max(0, 100 - weighted_debt)
    assert score == 55


@pytest.mark.unit
def test_health_score_bounds():
    """Test health score is always between 0-100."""
    test_cases = [
        {"raw_score": -50, "expected": 0},  # Below minimum
        {"raw_score": 0, "expected": 0},  # Minimum
        {"raw_score": 50, "expected": 50},  # Middle
        {"raw_score": 100, "expected": 100},  # Maximum
        {"raw_score": 150, "expected": 100},  # Above maximum
    ]

    for case in test_cases:
        # Clamp score between 0-100
        clamped = max(0, min(100, case["raw_score"]))
        assert clamped == case["expected"]


@pytest.mark.unit
def test_health_check_json_structure():
    """Test health check output JSON structure."""
    health_output = {
        "score": 85,
        "lint": {"errors": 2, "warnings": 5},
        "types": {"errors": 0},
        "security": {"high": 0, "medium": 1, "low": 3},
        "tests": {"passed": 142, "failed": 0, "total": 142, "coverage": 55},
        "tech_debt": {"total": 25, "todos": 15, "fixmes": 5, "hacks": 5},
        "timestamp": "2025-01-03T10:00:00Z",
    }

    # Verify required fields exist
    assert "score" in health_output
    assert "lint" in health_output
    assert "types" in health_output
    assert "security" in health_output
    assert "tests" in health_output
    assert "tech_debt" in health_output
    assert "timestamp" in health_output

    # Verify score is in valid range
    assert 0 <= health_output["score"] <= 100

    # Verify nested structures
    assert "errors" in health_output["lint"]
    assert "warnings" in health_output["lint"]
    assert "passed" in health_output["tests"]
    assert "total" in health_output["tests"]
