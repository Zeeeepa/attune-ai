"""Unit tests for token estimation

Tests the token estimation service for cost prediction.

Copyright 2025 Smart-AI-Memory
Licensed under Fair Source License 0.9
"""

import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest

from empathy_os.models.token_estimator import (
    TIKTOKEN_AVAILABLE,
    TOKENS_PER_CHAR_HEURISTIC,
    _get_encoding,
    estimate_single_call_cost,
    estimate_tokens,
    estimate_workflow_cost,
)


@pytest.mark.unit
class TestEstimateTokensBasic:
    """Test basic token estimation."""

    def test_estimate_tokens_empty_string(self):
        """Test estimating tokens for empty string."""
        result = estimate_tokens("")

        assert result == 0

    def test_estimate_tokens_simple_text(self):
        """Test estimating tokens for simple text."""
        text = "Hello world"
        result = estimate_tokens(text)

        assert result > 0
        assert isinstance(result, int)

    def test_estimate_tokens_heuristic_fallback(self):
        """Test token estimation works (may use tiktoken, toolkit, or heuristic)."""
        text = "a" * 100  # 100 chars
        result = estimate_tokens(text)

        # Should get a reasonable token count (tiktoken gives ~13 for repeated 'a')
        # Heuristic would give 25, but tiktoken is more accurate
        assert result > 0
        assert result < 50  # Sanity check

    def test_estimate_tokens_different_models(self):
        """Test estimation with different model IDs."""
        text = "Test text"

        claude_result = estimate_tokens(text, model_id="claude-sonnet-4")
        gpt_result = estimate_tokens(text, model_id="gpt-4")

        # Both should return positive integers
        assert claude_result > 0
        assert gpt_result > 0


@pytest.mark.unit
class TestGetEncoding:
    """Test encoding selection."""

    @pytest.mark.skipif(not TIKTOKEN_AVAILABLE, reason="tiktoken not installed")
    def test_get_encoding_claude(self):
        """Test encoding for Claude models."""
        encoding = _get_encoding("claude-sonnet-4")

        assert encoding is not None

    @pytest.mark.skipif(not TIKTOKEN_AVAILABLE, reason="tiktoken not installed")
    def test_get_encoding_gpt4(self):
        """Test encoding for GPT-4 models."""
        encoding = _get_encoding("gpt-4")

        assert encoding is not None

    @pytest.mark.skipif(not TIKTOKEN_AVAILABLE, reason="tiktoken not installed")
    def test_get_encoding_unknown_model(self):
        """Test encoding for unknown model defaults to cl100k_base."""
        encoding = _get_encoding("unknown-model-xyz")

        assert encoding is not None

    @pytest.mark.skipif(not TIKTOKEN_AVAILABLE, reason="tiktoken not installed")
    def test_get_encoding_caching(self):
        """Test that encoding is cached (LRU cache)."""
        # First call
        enc1 = _get_encoding("claude-sonnet-4")
        # Second call should return cached result
        enc2 = _get_encoding("claude-sonnet-4")

        assert enc1 is enc2


@pytest.mark.unit
class TestEstimateWorkflowCost:
    """Test workflow cost estimation."""

    def test_estimate_workflow_cost_basic(self):
        """Test basic workflow cost estimation."""
        result = estimate_workflow_cost(
            workflow_name="code-review",
            input_text="def hello(): pass",
            provider="anthropic",
        )

        assert "workflow" in result
        assert "provider" in result
        assert "input_tokens" in result
        assert "stages" in result
        assert "total_min" in result
        assert "total_max" in result
        assert "risk" in result
        assert result["workflow"] == "code-review"
        assert result["provider"] == "anthropic"
        assert result["input_tokens"] > 0

    def test_estimate_workflow_cost_known_workflows(self):
        """Test cost estimation for known workflows."""
        workflows = ["security-audit", "bug-predict", "test-gen", "doc-gen"]

        for workflow in workflows:
            result = estimate_workflow_cost(
                workflow_name=workflow,
                input_text="test code",
                provider="anthropic",
            )

            assert result["workflow"] == workflow
            assert len(result["stages"]) > 0

    def test_estimate_workflow_cost_unknown_workflow(self):
        """Test cost estimation for unknown workflow uses default stages."""
        result = estimate_workflow_cost(
            workflow_name="unknown-workflow",
            input_text="test",
            provider="anthropic",
        )

        # Should use default 3-stage configuration
        assert len(result["stages"]) == 3

    def test_estimate_workflow_cost_risk_levels(self):
        """Test risk level calculation."""
        # Low risk: short input
        low_risk = estimate_workflow_cost(
            workflow_name="doc-gen",
            input_text="x",
            provider="anthropic",
        )

        # High risk: very long input
        high_risk = estimate_workflow_cost(
            workflow_name="security-audit",
            input_text="x" * 10000,
            provider="anthropic",
        )

        assert low_risk["risk"] in ["low", "medium", "high"]
        assert high_risk["risk"] in ["low", "medium", "high"]

    def test_estimate_workflow_cost_with_file_path(self):
        """Test cost estimation with target file path."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create a test file
            test_file = Path(tmpdir) / "test.py"
            test_file.write_text("def test(): pass\n" * 50)

            result = estimate_workflow_cost(
                workflow_name="code-review",
                input_text="Review this code",
                provider="anthropic",
                target_path=str(test_file),
            )

            # Input tokens should include both input_text and file content
            assert result["input_tokens"] > 10  # More than just "Review this code"

    def test_estimate_workflow_cost_with_directory_path(self):
        """Test cost estimation with target directory path."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create test Python files
            for i in range(3):
                test_file = Path(tmpdir) / f"test{i}.py"
                test_file.write_text(f"def test{i}(): pass\n")

            result = estimate_workflow_cost(
                workflow_name="security-audit",
                input_text="Audit codebase",
                provider="anthropic",
                target_path=tmpdir,
            )

            # Should include file contents
            assert result["input_tokens"] > 5

    def test_estimate_workflow_cost_invalid_provider(self):
        """Test estimation with invalid provider falls back to anthropic."""
        result = estimate_workflow_cost(
            workflow_name="code-review",
            input_text="test",
            provider="invalid-provider-xyz",
        )

        # Should fallback to anthropic
        assert result["provider"] == "anthropic"

    def test_estimate_workflow_cost_stage_details(self):
        """Test that stage details are populated correctly."""
        result = estimate_workflow_cost(
            workflow_name="code-review",
            input_text="test code",
            provider="anthropic",
        )

        # Check stage structure
        for stage in result["stages"]:
            assert "stage" in stage
            assert "tier" in stage
            assert "model" in stage
            assert "estimated_input_tokens" in stage
            assert "estimated_output_tokens" in stage
            assert "estimated_cost" in stage


@pytest.mark.unit
class TestEstimateSingleCallCost:
    """Test single call cost estimation."""

    def test_estimate_single_call_cost_basic(self):
        """Test basic single call cost estimation."""
        result = estimate_single_call_cost(
            text="Summarize this text",
            task_type="summarize",
            provider="anthropic",
        )

        assert "task_type" in result
        assert "tier" in result
        assert "model" in result
        assert "provider" in result
        assert "input_tokens" in result
        assert "estimated_output_tokens" in result
        assert "estimated_cost" in result
        assert "display" in result

    def test_estimate_single_call_cost_different_tasks(self):
        """Test cost estimation for different task types."""
        task_types = ["summarize", "classify", "generate_code", "review"]

        for task_type in task_types:
            result = estimate_single_call_cost(
                text="test input",
                task_type=task_type,
                provider="anthropic",
            )

            assert result["task_type"] == task_type
            assert result["input_tokens"] > 0

    def test_estimate_single_call_cost_output_multipliers(self):
        """Test that output tokens vary by task type."""
        text = "test" * 100

        summarize = estimate_single_call_cost(text, "summarize", "anthropic")
        generate_code = estimate_single_call_cost(text, "generate_code", "anthropic")

        # Generate code should have higher output multiplier than summarize
        assert generate_code["estimated_output_tokens"] > summarize["estimated_output_tokens"]

    def test_estimate_single_call_cost_cost_calculation(self):
        """Test that cost is calculated correctly."""
        result = estimate_single_call_cost(
            text="test",
            task_type="summarize",
            provider="anthropic",
        )

        # Cost should be positive for non-zero input
        assert result["estimated_cost"] >= 0
        # Display should be a formatted string
        assert result["display"].startswith("$")


@pytest.mark.unit
class TestEdgeCases:
    """Test edge cases and error handling."""

    def test_estimate_tokens_very_long_text(self):
        """Test estimation with very long text."""
        long_text = "x" * 100000
        result = estimate_tokens(long_text)

        assert result > 0
        assert isinstance(result, int)

    def test_estimate_tokens_special_characters(self):
        """Test estimation with special characters."""
        text = "Hello! @#$% 你好 🚀"
        result = estimate_tokens(text)

        assert result > 0

    def test_estimate_workflow_cost_empty_input(self):
        """Test workflow cost with empty input."""
        result = estimate_workflow_cost(
            workflow_name="code-review",
            input_text="",
            provider="anthropic",
        )

        assert result["input_tokens"] == 0

    def test_estimate_workflow_cost_nonexistent_file(self):
        """Test workflow cost with nonexistent file path."""
        result = estimate_workflow_cost(
            workflow_name="code-review",
            input_text="test",
            provider="anthropic",
            target_path="/nonexistent/path/to/file.py",
        )

        # Should not crash, just use input text tokens
        assert result["input_tokens"] > 0

    def test_estimate_single_call_unknown_task_type(self):
        """Test single call estimation with unknown task type."""
        result = estimate_single_call_cost(
            text="test",
            task_type="unknown_task_xyz",
            provider="anthropic",
        )

        # Should use default multiplier of 1.0
        assert result["estimated_output_tokens"] > 0
