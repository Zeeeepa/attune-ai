"""Tests for task complexity scoring.

Copyright 2026 Smart-AI-Memory
Licensed under Fair Source License 0.9
"""

from empathy_os.adaptive.task_complexity import TaskComplexity, TaskComplexityScorer


def test_simple_task_scoring():
    """Test scoring of simple task."""
    scorer = TaskComplexityScorer()

    score = scorer.score_task(
        description="Fix typo in README",
        context="# README\nTypo here",
        files=["README.md"],
    )

    assert score.complexity_level == TaskComplexity.SIMPLE
    assert score.token_count < 100
    assert score.line_count < 50
    assert score.file_count == 1


def test_moderate_task_scoring():
    """Test scoring of moderate task."""
    scorer = TaskComplexityScorer()

    # Generate moderate context
    context = "\n".join([f"line {i}" for i in range(100)])

    score = scorer.score_task(
        description="Refactor a single function with 100 lines",
        context=context,
        files=["module.py"],
    )

    assert score.complexity_level == TaskComplexity.MODERATE
    assert 50 <= score.line_count < 200


def test_complex_task_scoring():
    """Test scoring of complex task."""
    scorer = TaskComplexityScorer()

    # Generate large context
    context = "\n".join([f"line {i}" for i in range(500)])

    score = scorer.score_task(
        description="Refactor entire module with 500 lines",
        context=context,
        files=["module.py"],
    )

    assert score.complexity_level in [TaskComplexity.COMPLEX, TaskComplexity.VERY_COMPLEX]
    assert score.line_count >= 500


def test_very_complex_task_scoring():
    """Test scoring of very complex task."""
    scorer = TaskComplexityScorer()

    # Generate very large context
    context = "\n".join([f"def function_{i}(): pass" for i in range(2000)])

    score = scorer.score_task(
        description="Refactor entire codebase across multiple modules",
        context=context,
        files=["mod1.py", "mod2.py", "mod3.py"],
    )

    assert score.complexity_level == TaskComplexity.VERY_COMPLEX
    assert score.line_count >= 1000
    assert score.file_count == 3


def test_scoring_without_context():
    """Test scoring with only description."""
    scorer = TaskComplexityScorer()

    score = scorer.score_task(description="Simple task")

    assert score.complexity_level == TaskComplexity.SIMPLE
    assert score.line_count == 0
    assert score.file_count == 0


def test_scoring_without_files():
    """Test scoring without file list."""
    scorer = TaskComplexityScorer()

    score = scorer.score_task(
        description="Task description",
        context="Some context",
    )

    assert score.file_count == 0
    assert score.complexity_level in [
        TaskComplexity.SIMPLE,
        TaskComplexity.MODERATE,
    ]


def test_confidence_score():
    """Test that confidence is reasonable."""
    scorer = TaskComplexityScorer()

    score = scorer.score_task(description="Test task")

    assert 0 < score.confidence <= 1.0
