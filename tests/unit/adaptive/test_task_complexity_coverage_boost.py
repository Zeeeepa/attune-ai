"""Comprehensive tests for task complexity scoring.

Tests for TaskComplexity enum, ComplexityScore dataclass, and TaskComplexityScorer.

Module: adaptive/task_complexity.py (128 lines)
"""

import pytest

from empathy_os.adaptive.task_complexity import (
    ComplexityScore,
    TaskComplexity,
    TaskComplexityScorer,
)


# ============================================================================
# TaskComplexity Enum Tests
# ============================================================================


@pytest.mark.unit
class TestTaskComplexity:
    """Test suite for TaskComplexity enum."""

    def test_enum_values_exist(self):
        """Test that all complexity levels exist."""
        assert TaskComplexity.SIMPLE.value == "simple"
        assert TaskComplexity.MODERATE.value == "moderate"
        assert TaskComplexity.COMPLEX.value == "complex"
        assert TaskComplexity.VERY_COMPLEX.value == "very_complex"

    def test_enum_count(self):
        """Test that enum has exactly 4 levels."""
        assert len(list(TaskComplexity)) == 4

    def test_enum_is_string_enum(self):
        """Test that enum values are strings."""
        for level in TaskComplexity:
            assert isinstance(level.value, str)


# ============================================================================
# ComplexityScore Dataclass Tests
# ============================================================================


@pytest.mark.unit
class TestComplexityScore:
    """Test suite for ComplexityScore dataclass."""

    def test_create_score_with_all_fields(self):
        """Test creating ComplexityScore with all fields."""
        score = ComplexityScore(
            token_count=150,
            line_count=75,
            file_count=3,
            complexity_level=TaskComplexity.MODERATE,
            confidence=0.8,
        )

        assert score.token_count == 150
        assert score.line_count == 75
        assert score.file_count == 3
        assert score.complexity_level == TaskComplexity.MODERATE
        assert score.confidence == 0.8

    def test_create_simple_score(self):
        """Test creating score for simple task."""
        score = ComplexityScore(
            token_count=50,
            line_count=20,
            file_count=1,
            complexity_level=TaskComplexity.SIMPLE,
            confidence=0.8,
        )

        assert score.complexity_level == TaskComplexity.SIMPLE
        assert score.token_count < 100
        assert score.line_count < 50

    def test_create_very_complex_score(self):
        """Test creating score for very complex task."""
        score = ComplexityScore(
            token_count=3000,
            line_count=1500,
            file_count=10,
            complexity_level=TaskComplexity.VERY_COMPLEX,
            confidence=0.8,
        )

        assert score.complexity_level == TaskComplexity.VERY_COMPLEX
        assert score.token_count > 2000
        assert score.line_count > 1000


# ============================================================================
# TaskComplexityScorer Initialization Tests
# ============================================================================


@pytest.mark.unit
class TestTaskComplexityScorerInit:
    """Test suite for TaskComplexityScorer initialization."""

    def test_scorer_initializes(self):
        """Test that scorer initializes successfully."""
        scorer = TaskComplexityScorer()
        assert scorer is not None

    def test_scorer_has_tokenizer_attribute(self):
        """Test that scorer has tokenizer attribute."""
        scorer = TaskComplexityScorer()
        # tokenizer may be None if tiktoken not installed
        assert hasattr(scorer, "tokenizer")


# ============================================================================
# TaskComplexityScorer.score_task Tests - Simple Tasks
# ============================================================================


@pytest.mark.unit
class TestScoreSimpleTasks:
    """Test suite for scoring simple tasks."""

    def test_score_simple_description_only(self):
        """Test scoring simple task with description only."""
        scorer = TaskComplexityScorer()
        score = scorer.score_task(description="Fix typo in README")

        assert score.token_count >= 0
        assert score.line_count == 0  # No context provided
        assert score.file_count == 0  # No files provided
        assert score.complexity_level == TaskComplexity.SIMPLE
        assert 0.0 <= score.confidence <= 1.0

    def test_score_simple_with_one_file(self):
        """Test scoring simple task with one file."""
        scorer = TaskComplexityScorer()
        score = scorer.score_task(
            description="Update README",
            files=["README.md"],
        )

        assert score.file_count == 1
        assert score.complexity_level == TaskComplexity.SIMPLE


# ============================================================================
# Confidence Score Tests
# ============================================================================


@pytest.mark.unit
class TestConfidenceScores:
    """Test suite for confidence scores."""

    def test_confidence_with_tokenizer(self):
        """Test that confidence is higher when tokenizer is available."""
        scorer = TaskComplexityScorer()
        score = scorer.score_task(description="Test task")

        # Confidence should be either 0.8 (with tiktoken) or 0.6 (without)
        assert score.confidence in [0.6, 0.8]

    def test_confidence_is_valid_range(self):
        """Test that confidence is always between 0 and 1."""
        scorer = TaskComplexityScorer()
        score = scorer.score_task(
            description="Any task",
            context="Some context",
            files=["file.py"],
        )

        assert 0.0 <= score.confidence <= 1.0


# ============================================================================
# Edge Cases and Special Scenarios
# ============================================================================


@pytest.mark.unit
class TestEdgeCases:
    """Test suite for edge cases."""

    def test_score_empty_description(self):
        """Test scoring with empty description."""
        scorer = TaskComplexityScorer()
        score = scorer.score_task(description="")

        assert score.token_count >= 0
        assert score.complexity_level == TaskComplexity.SIMPLE

    def test_score_with_none_context(self):
        """Test scoring with None context."""
        scorer = TaskComplexityScorer()
        score = scorer.score_task(description="Test", context=None)

        assert score.line_count == 0

    def test_score_with_none_files(self):
        """Test scoring with None files."""
        scorer = TaskComplexityScorer()
        score = scorer.score_task(description="Test", files=None)

        assert score.file_count == 0

    def test_score_with_empty_files_list(self):
        """Test scoring with empty files list."""
        scorer = TaskComplexityScorer()
        score = scorer.score_task(description="Test", files=[])

        assert score.file_count == 0

    def test_score_returns_complexity_score(self):
        """Test that score_task returns ComplexityScore instance."""
        scorer = TaskComplexityScorer()
        score = scorer.score_task(description="Test task")

        assert isinstance(score, ComplexityScore)
        assert hasattr(score, "token_count")
        assert hasattr(score, "line_count")
        assert hasattr(score, "file_count")
        assert hasattr(score, "complexity_level")
        assert hasattr(score, "confidence")
