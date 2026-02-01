"""Tests for CLI info commands.

Module: cli/commands/info.py (141 lines)
"""

from unittest.mock import Mock, patch

import pytest

from attune.cli.commands.info import cmd_frameworks, cmd_info

# ============================================================================
# cmd_info Tests
# ============================================================================


@pytest.mark.unit
class TestCmdInfo:
    """Test suite for cmd_info command."""

    @patch("attune.cli.commands.info.load_config")
    def test_cmd_info_loads_default_config(self, mock_load_config):
        """Test that cmd_info loads default config when no file specified."""
        # Given
        mock_config = Mock()
        mock_config.user_id = "test_user"
        mock_config.target_level = "intermediate"
        mock_config.confidence_threshold = 0.75
        mock_config.persistence_backend = "json"
        mock_config.persistence_path = "/tmp/test.json"
        mock_config.persistence_enabled = True
        mock_config.metrics_enabled = True
        mock_config.metrics_path = "/tmp/metrics"
        mock_config.pattern_library_enabled = True
        mock_config.pattern_sharing = True
        mock_config.pattern_confidence_threshold = 0.8
        mock_load_config.return_value = mock_config

        args = Mock()
        args.config = None

        # When
        cmd_info(args)

        # Then
        mock_load_config.assert_called_once_with()

    @patch("attune.cli.commands.info.load_config")
    def test_cmd_info_loads_custom_config(self, mock_load_config):
        """Test that cmd_info loads custom config file when provided."""
        # Given
        mock_config = Mock()
        mock_config.user_id = "test_user"
        mock_config.target_level = "intermediate"
        mock_config.confidence_threshold = 0.75
        mock_config.persistence_backend = "json"
        mock_config.persistence_path = "/tmp/test.json"
        mock_config.persistence_enabled = True
        mock_config.metrics_enabled = True
        mock_config.metrics_path = "/tmp/metrics"
        mock_config.pattern_library_enabled = True
        mock_config.pattern_sharing = True
        mock_config.pattern_confidence_threshold = 0.8
        mock_load_config.return_value = mock_config

        args = Mock()
        args.config = "/path/to/custom.yaml"

        # When
        cmd_info(args)

        # Then
        mock_load_config.assert_called_once_with(filepath="/path/to/custom.yaml")

    @patch("attune.cli.commands.info.load_config")
    def test_cmd_info_returns_none(self, mock_load_config):
        """Test that cmd_info returns None."""
        # Given
        mock_config = Mock()
        mock_config.user_id = "test_user"
        mock_config.target_level = "intermediate"
        mock_config.confidence_threshold = 0.75
        mock_config.persistence_backend = "json"
        mock_config.persistence_path = "/tmp/test.json"
        mock_config.persistence_enabled = True
        mock_config.metrics_enabled = True
        mock_config.metrics_path = "/tmp/metrics"
        mock_config.pattern_library_enabled = True
        mock_config.pattern_sharing = True
        mock_config.pattern_confidence_threshold = 0.8
        mock_load_config.return_value = mock_config

        args = Mock()
        args.config = None

        # When
        result = cmd_info(args)

        # Then
        assert result is None


# ============================================================================
# cmd_frameworks Tests
# ============================================================================


@pytest.mark.unit
class TestCmdFrameworks:
    """Test suite for cmd_frameworks command."""

    def test_cmd_frameworks_function_exists(self):
        """Test that cmd_frameworks function exists."""
        assert callable(cmd_frameworks)

