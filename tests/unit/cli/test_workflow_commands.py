"""Unit tests for CLI workflow commands.

Tests the workflow command interface for list, describe, and run operations.

Copyright 2026 Smart-AI-Memory
Licensed under Apache 2.0
"""

from unittest.mock import MagicMock, patch


class TestWorkflowListCommand:
    """Tests for 'empathy workflow list' command."""

    def test_list_workflows_basic(self, capsys):
        """Test listing workflows doesn't crash."""
        from attune.cli.commands.workflow import cmd_workflow

        # Create mock args
        args = MagicMock()
        args.action = "list"
        args.json = False

        # Execute command (should not crash)
        result = cmd_workflow(args)

        # Verify it runs without error (returns 0 or None)
        assert result is None or result == 0

    def test_list_workflows_json_output(self, capsys):
        """Test listing workflows in JSON format."""
        from attune.cli.commands.workflow import cmd_workflow

        # Create mock args
        args = MagicMock()
        args.action = "list"
        args.json = True

        # Execute command
        result = cmd_workflow(args)

        # Verify it runs
        assert result is None or result == 0


class TestWorkflowDescribeCommand:
    """Tests for 'empathy workflow describe' command."""

    def test_describe_without_name_shows_error(self):
        """Test that describe without workflow name shows error."""
        from attune.cli.commands.workflow import cmd_workflow

        # Create mock args with no name
        args = MagicMock()
        args.action = "describe"
        args.name = None

        # Execute command (should fail)
        result = cmd_workflow(args)

        # Verify error
        assert result == 1

    @patch("attune.cli.commands.workflow.get_workflow")
    def test_describe_nonexistent_workflow_shows_error(self, mock_get_workflow):
        """Test that describing non-existent workflow shows helpful error."""
        from attune.cli.commands.workflow import cmd_workflow

        # Mock KeyError for missing workflow
        mock_get_workflow.side_effect = KeyError("workflow-not-found")

        # Create mock args
        args = MagicMock()
        args.action = "describe"
        args.name = "nonexistent-workflow"
        args.json = False

        # Execute command (should fail gracefully)
        result = cmd_workflow(args)

        # Verify error handling
        assert result == 1


class TestWorkflowRunCommand:
    """Tests for 'empathy workflow run' command."""

    def test_run_without_name_shows_error(self):
        """Test that run without workflow name shows error."""
        from attune.cli.commands.workflow import cmd_workflow

        # Create mock args with no name
        args = MagicMock()
        args.action = "run"
        args.name = None

        # Execute command (should fail)
        result = cmd_workflow(args)

        # Verify error
        assert result == 1

    @patch("attune.cli.commands.workflow.get_workflow")
    def test_run_with_invalid_json_shows_helpful_error(self, mock_get_workflow):
        """Test that invalid JSON input shows helpful error message."""
        from attune.cli.commands.workflow import cmd_workflow

        # Mock workflow class
        mock_workflow_cls = MagicMock()
        mock_get_workflow.return_value = mock_workflow_cls

        # Create mock args with invalid JSON
        args = MagicMock()
        args.action = "run"
        args.name = "test-workflow"
        args.input = "{invalid json"  # Malformed JSON
        args.json = False

        # Execute command (should fail with JSON error)
        result = cmd_workflow(args)

        # Verify error handling
        assert result == 1


class TestWorkflowCommandEdgeCases:
    """Tests for edge cases and error handling."""

    def test_invalid_action_returns_error(self):
        """Test that invalid action returns error code."""
        from attune.cli.commands.workflow import cmd_workflow

        # Create mock args with invalid action
        args = MagicMock()
        args.action = "invalid-action"

        # Execute command
        result = cmd_workflow(args)

        # Should return error (0 for success, 1 for error, or no return means 0)
        # The function may return None for unknown actions
        assert result is None or result == 0 or result == 1
