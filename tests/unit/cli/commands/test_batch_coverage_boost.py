"""Tests for CLI batch commands.

Module: cli/commands/batch.py (264 lines)
"""

from unittest.mock import Mock, patch

import pytest

from empathy_os.cli.commands.batch import (
    cmd_batch_results,
    cmd_batch_status,
    cmd_batch_submit,
    cmd_batch_wait,
)

# ============================================================================
# cmd_batch_submit Tests
# ============================================================================


@pytest.mark.unit
class TestCmdBatchSubmit:
    """Test suite for cmd_batch_submit command."""

    def test_batch_submit_missing_file_returns_1(self):
        """Test batch submit returns 1 when input file missing."""
        # Given
        args = Mock()
        args.input_file = "/nonexistent/file.json"

        # When
        result = cmd_batch_submit(args)

        # Then
        assert result == 1

    @patch.dict("os.environ", {}, clear=True)
    def test_batch_submit_missing_api_key_returns_1(self):
        """Test batch submit returns 1 when API key not set."""
        # Given
        args = Mock()
        args.input_file = __file__  # Use this file (exists)

        # When
        result = cmd_batch_submit(args)

        # Then
        assert result == 1


# ============================================================================
# cmd_batch_status Tests
# ============================================================================


@pytest.mark.unit
class TestCmdBatchStatus:
    """Test suite for cmd_batch_status command."""

    @patch.dict("os.environ", {}, clear=True)
    def test_batch_status_missing_api_key_returns_1(self):
        """Test batch status returns 1 when API key not set."""
        # Given
        args = Mock()
        args.batch_id = "batch_123"
        args.json = False

        # When
        result = cmd_batch_status(args)

        # Then
        assert result == 1


# ============================================================================
# cmd_batch_results Tests
# ============================================================================


@pytest.mark.unit
class TestCmdBatchResults:
    """Test suite for cmd_batch_results command."""

    @patch.dict("os.environ", {}, clear=True)
    def test_batch_results_missing_api_key_returns_1(self):
        """Test batch results returns 1 when API key not set."""
        # Given
        args = Mock()
        args.batch_id = "batch_123"
        args.output_file = "/tmp/output.json"

        # When
        result = cmd_batch_results(args)

        # Then
        assert result == 1


# ============================================================================
# cmd_batch_wait Tests
# ============================================================================


@pytest.mark.unit
class TestCmdBatchWait:
    """Test suite for cmd_batch_wait command."""

    @patch.dict("os.environ", {}, clear=True)
    def test_batch_wait_missing_api_key_returns_1(self):
        """Test batch wait returns 1 when API key not set."""
        # Given
        args = Mock()
        args.batch_id = "batch_123"
        args.output_file = "/tmp/output.json"
        args.poll_interval = 300
        args.timeout = 3600

        # When
        result = cmd_batch_wait(args)

        # Then
        assert result == 1
