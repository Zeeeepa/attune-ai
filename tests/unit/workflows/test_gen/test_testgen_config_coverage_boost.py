"""Tests for test generation configuration.

Module: workflows/test_gen/config.py (88 lines)
"""

import pytest

from empathy_os.workflows.test_gen.config import (
    DEFAULT_SKIP_PATTERNS,
    TEST_GEN_STEPS,
)
from empathy_os.workflows.step_config import WorkflowStepConfig


# ============================================================================
# DEFAULT_SKIP_PATTERNS Tests
# ============================================================================


@pytest.mark.unit
class TestDefaultSkipPatterns:
    """Test suite for DEFAULT_SKIP_PATTERNS constant."""

    def test_skip_patterns_is_list(self):
        """Test that DEFAULT_SKIP_PATTERNS is a list."""
        assert isinstance(DEFAULT_SKIP_PATTERNS, list)

    def test_skip_patterns_not_empty(self):
        """Test that DEFAULT_SKIP_PATTERNS is not empty."""
        assert len(DEFAULT_SKIP_PATTERNS) > 0

    def test_skip_patterns_contains_git(self):
        """Test that skip patterns includes .git directory."""
        assert ".git" in DEFAULT_SKIP_PATTERNS

    def test_skip_patterns_contains_pycache(self):
        """Test that skip patterns includes __pycache__."""
        assert "__pycache__" in DEFAULT_SKIP_PATTERNS

    def test_skip_patterns_contains_node_modules(self):
        """Test that skip patterns includes node_modules."""
        assert "node_modules" in DEFAULT_SKIP_PATTERNS

    def test_skip_patterns_contains_venv(self):
        """Test that skip patterns includes venv directories."""
        assert "venv" in DEFAULT_SKIP_PATTERNS
        assert ".venv" in DEFAULT_SKIP_PATTERNS

    def test_skip_patterns_all_strings(self):
        """Test that all skip patterns are strings."""
        for pattern in DEFAULT_SKIP_PATTERNS:
            assert isinstance(pattern, str)


# ============================================================================
# TEST_GEN_STEPS Tests
# ============================================================================


@pytest.mark.unit
class TestTestGenSteps:
    """Test suite for TEST_GEN_STEPS constant."""

    def test_steps_is_dict(self):
        """Test that TEST_GEN_STEPS is a dictionary."""
        assert isinstance(TEST_GEN_STEPS, dict)

    def test_steps_has_identify(self):
        """Test that TEST_GEN_STEPS has identify step."""
        assert "identify" in TEST_GEN_STEPS
        assert isinstance(TEST_GEN_STEPS["identify"], WorkflowStepConfig)

    def test_steps_has_analyze(self):
        """Test that TEST_GEN_STEPS has analyze step."""
        assert "analyze" in TEST_GEN_STEPS
        assert isinstance(TEST_GEN_STEPS["analyze"], WorkflowStepConfig)

    def test_steps_has_generate(self):
        """Test that TEST_GEN_STEPS has generate step."""
        assert "generate" in TEST_GEN_STEPS
        assert isinstance(TEST_GEN_STEPS["generate"], WorkflowStepConfig)

    def test_steps_has_review(self):
        """Test that TEST_GEN_STEPS has review step."""
        assert "review" in TEST_GEN_STEPS
        assert isinstance(TEST_GEN_STEPS["review"], WorkflowStepConfig)

    def test_steps_count(self):
        """Test that TEST_GEN_STEPS has exactly 4 steps."""
        assert len(TEST_GEN_STEPS) == 4

    def test_identify_step_tier_cheap(self):
        """Test that identify step uses cheap tier."""
        assert TEST_GEN_STEPS["identify"].tier_hint == "cheap"

    def test_analyze_step_tier_capable(self):
        """Test that analyze step uses capable tier."""
        assert TEST_GEN_STEPS["analyze"].tier_hint == "capable"

    def test_generate_step_tier_capable(self):
        """Test that generate step uses capable tier."""
        assert TEST_GEN_STEPS["generate"].tier_hint == "capable"

    def test_review_step_tier_premium(self):
        """Test that review step uses premium tier."""
        assert TEST_GEN_STEPS["review"].tier_hint == "premium"

    def test_all_steps_have_max_tokens(self):
        """Test that all steps have max_tokens configured."""
        for step_name, step_config in TEST_GEN_STEPS.items():
            assert step_config.max_tokens > 0
