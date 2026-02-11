"""Unit tests for task complexity scoring

Tests the TaskComplexityScorer for adaptive prompt selection.

Copyright 2025 Smart-AI-Memory
Licensed under the Apache License, Version 2.0
"""

from unittest.mock import MagicMock, patch

import pytest

from attune.adaptive.task_complexity import (
    ComplexityScore,
    TaskComplexity,
    TaskComplexityScorer,
)


@pytest.mark.unit
class TestTaskComplexityEnum:
    """Test TaskComplexity enum."""

    def test_enum_values(self):
        """Test that enum has expected values."""
        assert TaskComplexity.SIMPLE.value == "simple"
        assert TaskComplexity.MODERATE.value == "moderate"
        assert TaskComplexity.COMPLEX.value == "complex"
        assert TaskComplexity.VERY_COMPLEX.value == "very_complex"

    def test_enum_members(self):
        """Test that all expected members exist."""
        members = list(TaskComplexity)
        assert len(members) == 4
        assert TaskComplexity.SIMPLE in members
        assert TaskComplexity.MODERATE in members
        assert TaskComplexity.COMPLEX in members
        assert TaskComplexity.VERY_COMPLEX in members


@pytest.mark.unit
class TestComplexityScore:
    """Test ComplexityScore dataclass."""

    def test_initialization(self):
        """Test creating a ComplexityScore."""
        score = ComplexityScore(
            token_count=100,
            line_count=50,
            file_count=2,
            complexity_level=TaskComplexity.SIMPLE,
            confidence=0.8,
        )

        assert score.token_count == 100
        assert score.line_count == 50
        assert score.file_count == 2
        assert score.complexity_level == TaskComplexity.SIMPLE
        assert score.confidence == 0.8


@pytest.mark.unit
class TestTaskComplexityScorerInitialization:
    """Test TaskComplexityScorer initialization."""

    @patch("attune.adaptive.task_complexity.tiktoken")
    def test_initialization_with_tiktoken(self, mock_tiktoken):
        """Test initialization when tiktoken is available."""
        mock_encoding = MagicMock()
        mock_tiktoken.get_encoding.return_value = mock_encoding

        scorer = TaskComplexityScorer()

        assert scorer.tokenizer == mock_encoding
        mock_tiktoken.get_encoding.assert_called_once_with("cl100k_base")

    @patch("attune.adaptive.task_complexity.tiktoken", None)
    def test_initialization_without_tiktoken(self):
        """Test initialization when tiktoken is not available."""
        scorer = TaskComplexityScorer()

        assert scorer.tokenizer is None


@pytest.mark.unit
class TestTaskComplexityScorerSimpleTasks:
    """Test scoring simple tasks."""

    @patch("attune.adaptive.task_complexity.tiktoken")
    def test_simple_task_with_tokenizer(self, mock_tiktoken):
        """Test scoring a simple task with tiktoken."""
        mock_encoding = MagicMock()
        # Short description: 20 tokens
        mock_encoding.encode.return_value = [0] * 20
        mock_tiktoken.get_encoding.return_value = mock_encoding

        scorer = TaskComplexityScorer()
        score = scorer.score_task(description="Fix typo in README")

        assert score.complexity_level == TaskComplexity.SIMPLE
        assert score.token_count == 20
        assert score.line_count == 0
        assert score.file_count == 0
        assert score.confidence == 0.8

    @patch("attune.adaptive.task_complexity.tiktoken", None)
    def test_simple_task_without_tokenizer(self):
        """Test scoring a simple task without tiktoken (fallback)."""
        scorer = TaskComplexityScorer()
        # Short description: ~20 chars = ~5 tokens (4 chars per token)
        score = scorer.score_task(description="Fix typo in README")

        assert score.complexity_level == TaskComplexity.SIMPLE
        assert score.token_count < 100
        assert score.line_count == 0
        assert score.file_count == 0
        assert score.confidence == 0.6  # Lower confidence without tokenizer

    @patch("attune.adaptive.task_complexity.tiktoken")
    def test_simple_task_with_small_context(self, mock_tiktoken):
        """Test simple task with small code context."""
        mock_encoding = MagicMock()
        # Description: 10 tokens, Context: 30 tokens = 40 total
        mock_encoding.encode.side_effect = [[0] * 10, [0] * 30]
        mock_tiktoken.get_encoding.return_value = mock_encoding

        scorer = TaskComplexityScorer()
        context = "def hello():\n    print('world')"
        score = scorer.score_task(description="Add docstring", context=context)

        assert score.complexity_level == TaskComplexity.SIMPLE
        assert score.token_count == 40
        assert score.line_count == 2
        assert score.file_count == 0


@pytest.mark.unit
class TestTaskComplexityScorerModerateTasks:
    """Test scoring moderate complexity tasks."""

    @patch("attune.adaptive.task_complexity.tiktoken")
    def test_moderate_task(self, mock_tiktoken):
        """Test scoring a moderate complexity task."""
        mock_encoding = MagicMock()
        # Description: 50 tokens, Context: 200 tokens = 250 total
        mock_encoding.encode.side_effect = [[0] * 50, [0] * 200]
        mock_tiktoken.get_encoding.return_value = mock_encoding

        scorer = TaskComplexityScorer()
        context = "\n".join([f"line {i}" for i in range(100)])  # 100 lines
        score = scorer.score_task(description="Refactor function", context=context)

        assert score.complexity_level == TaskComplexity.MODERATE
        assert score.token_count == 250
        assert score.line_count == 100
        assert score.file_count == 0

    @patch("attune.adaptive.task_complexity.tiktoken")
    def test_moderate_task_with_files(self, mock_tiktoken):
        """Test moderate task with multiple files."""
        mock_encoding = MagicMock()
        mock_encoding.encode.side_effect = [[0] * 100, [0] * 300]
        mock_tiktoken.get_encoding.return_value = mock_encoding

        scorer = TaskComplexityScorer()
        context = "\n".join([f"line {i}" for i in range(150)])
        files = ["auth.py", "session.py"]
        score = scorer.score_task(description="Add authentication", context=context, files=files)

        assert score.complexity_level == TaskComplexity.MODERATE
        assert score.file_count == 2


@pytest.mark.unit
class TestTaskComplexityScorerComplexTasks:
    """Test scoring complex tasks."""

    @patch("attune.adaptive.task_complexity.tiktoken")
    def test_complex_task(self, mock_tiktoken):
        """Test scoring a complex task."""
        mock_encoding = MagicMock()
        # Description: 100 tokens, Context: 800 tokens = 900 total
        mock_encoding.encode.side_effect = [[0] * 100, [0] * 800]
        mock_tiktoken.get_encoding.return_value = mock_encoding

        scorer = TaskComplexityScorer()
        context = "\n".join([f"line {i}" for i in range(500)])  # 500 lines
        score = scorer.score_task(description="Implement new API endpoint", context=context)

        assert score.complexity_level == TaskComplexity.COMPLEX
        assert score.token_count == 900
        assert score.line_count == 500

    @patch("attune.adaptive.task_complexity.tiktoken")
    def test_complex_task_with_many_files(self, mock_tiktoken):
        """Test complex task with many files."""
        mock_encoding = MagicMock()
        mock_encoding.encode.side_effect = [[0] * 200, [0] * 1200]
        mock_tiktoken.get_encoding.return_value = mock_encoding

        scorer = TaskComplexityScorer()
        context = "\n".join([f"line {i}" for i in range(800)])
        files = ["api.py", "models.py", "tests.py", "docs.py"]
        score = scorer.score_task(description="Add new feature", context=context, files=files)

        assert score.complexity_level == TaskComplexity.COMPLEX
        assert score.file_count == 4


@pytest.mark.unit
class TestTaskComplexityScorerVeryComplexTasks:
    """Test scoring very complex tasks."""

    @patch("attune.adaptive.task_complexity.tiktoken")
    def test_very_complex_task(self, mock_tiktoken):
        """Test scoring a very complex task."""
        mock_encoding = MagicMock()
        # Description: 200 tokens, Context: 3000 tokens = 3200 total
        mock_encoding.encode.side_effect = [[0] * 200, [0] * 3000]
        mock_tiktoken.get_encoding.return_value = mock_encoding

        scorer = TaskComplexityScorer()
        context = "\n".join([f"line {i}" for i in range(1500)])  # 1500 lines
        score = scorer.score_task(description="Major refactoring of entire module", context=context)

        assert score.complexity_level == TaskComplexity.VERY_COMPLEX
        assert score.token_count == 3200
        assert score.line_count == 1500

    @patch("attune.adaptive.task_complexity.tiktoken")
    def test_very_complex_by_tokens_only(self, mock_tiktoken):
        """Test very complex classification by tokens alone."""
        mock_encoding = MagicMock()
        # Description: 2500 tokens (exceeds threshold)
        mock_encoding.encode.return_value = [0] * 2500
        mock_tiktoken.get_encoding.return_value = mock_encoding

        scorer = TaskComplexityScorer()
        score = scorer.score_task(description="Very long description " * 100)  # Long description

        assert score.complexity_level == TaskComplexity.VERY_COMPLEX
        assert score.token_count >= 2000

    @patch("attune.adaptive.task_complexity.tiktoken")
    def test_very_complex_by_lines_only(self, mock_tiktoken):
        """Test very complex classification by line count alone."""
        mock_encoding = MagicMock()
        # Small tokens but many lines
        mock_encoding.encode.side_effect = [[0] * 50, [0] * 100]
        mock_tiktoken.get_encoding.return_value = mock_encoding

        scorer = TaskComplexityScorer()
        context = "\n".join([f"line {i}" for i in range(1200)])  # >1000 lines
        score = scorer.score_task(description="Short task", context=context)

        assert score.complexity_level == TaskComplexity.VERY_COMPLEX
        assert score.line_count >= 1000


@pytest.mark.unit
class TestTaskComplexityScorerEdgeCases:
    """Test edge cases and boundary conditions."""

    @patch("attune.adaptive.task_complexity.tiktoken", None)
    def test_fallback_estimation_accuracy(self):
        """Test fallback token estimation without tiktoken."""
        scorer = TaskComplexityScorer()

        # Test with known string length
        description = "a" * 400  # 400 chars = ~100 tokens (4 chars per token)
        score = scorer.score_task(description=description)

        assert score.token_count == 100
        assert score.confidence == 0.6

    @patch("attune.adaptive.task_complexity.tiktoken")
    def test_empty_description(self, mock_tiktoken):
        """Test scoring with empty description."""
        mock_encoding = MagicMock()
        mock_encoding.encode.return_value = []
        mock_tiktoken.get_encoding.return_value = mock_encoding

        scorer = TaskComplexityScorer()
        score = scorer.score_task(description="")

        assert score.complexity_level == TaskComplexity.SIMPLE
        assert score.token_count == 0

    @patch("attune.adaptive.task_complexity.tiktoken")
    def test_no_context_no_files(self, mock_tiktoken):
        """Test scoring with only description."""
        mock_encoding = MagicMock()
        mock_encoding.encode.return_value = [0] * 50
        mock_tiktoken.get_encoding.return_value = mock_encoding

        scorer = TaskComplexityScorer()
        score = scorer.score_task(description="Simple task")

        assert score.line_count == 0
        assert score.file_count == 0

    @patch("attune.adaptive.task_complexity.tiktoken")
    def test_empty_files_list(self, mock_tiktoken):
        """Test scoring with empty files list."""
        mock_encoding = MagicMock()
        mock_encoding.encode.return_value = [0] * 50
        mock_tiktoken.get_encoding.return_value = mock_encoding

        scorer = TaskComplexityScorer()
        score = scorer.score_task(description="Task", files=[])

        assert score.file_count == 0

    @patch("attune.adaptive.task_complexity.tiktoken")
    def test_boundary_simple_moderate(self, mock_tiktoken):
        """Test boundary between SIMPLE and MODERATE."""
        mock_encoding = MagicMock()
        # Exactly 100 tokens and 50 lines (boundary)
        mock_encoding.encode.side_effect = [[0] * 50, [0] * 50]
        mock_tiktoken.get_encoding.return_value = mock_encoding

        scorer = TaskComplexityScorer()
        context = "\n".join([f"line {i}" for i in range(50)])
        score = scorer.score_task(description="Boundary test", context=context)

        # Should be MODERATE (threshold is <100, <50 for SIMPLE)
        assert score.complexity_level == TaskComplexity.MODERATE

    @patch("attune.adaptive.task_complexity.tiktoken")
    def test_boundary_moderate_complex(self, mock_tiktoken):
        """Test boundary between MODERATE and COMPLEX."""
        mock_encoding = MagicMock()
        # Exactly 500 tokens and 200 lines
        mock_encoding.encode.side_effect = [[0] * 250, [0] * 250]
        mock_tiktoken.get_encoding.return_value = mock_encoding

        scorer = TaskComplexityScorer()
        context = "\n".join([f"line {i}" for i in range(200)])
        score = scorer.score_task(description="Boundary test", context=context)

        # Should be COMPLEX (threshold is <500, <200 for MODERATE)
        assert score.complexity_level == TaskComplexity.COMPLEX

    @patch("attune.adaptive.task_complexity.tiktoken")
    def test_boundary_complex_very_complex(self, mock_tiktoken):
        """Test boundary between COMPLEX and VERY_COMPLEX."""
        mock_encoding = MagicMock()
        # Exactly 2000 tokens and 1000 lines
        mock_encoding.encode.side_effect = [[0] * 1000, [0] * 1000]
        mock_tiktoken.get_encoding.return_value = mock_encoding

        scorer = TaskComplexityScorer()
        context = "\n".join([f"line {i}" for i in range(1000)])
        score = scorer.score_task(description="Boundary test", context=context)

        # Should be VERY_COMPLEX (threshold is <2000, <1000 for COMPLEX)
        assert score.complexity_level == TaskComplexity.VERY_COMPLEX
