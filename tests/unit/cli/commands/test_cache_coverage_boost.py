"""Tests for CLI cache commands.

Module: cli/commands/cache.py (248 lines)
"""

import pytest
from unittest.mock import Mock, patch, mock_open
from pathlib import Path

from empathy_os.cli.commands.cache import (
    cmd_cache_stats,
    cmd_cache_clear,
    _collect_cache_stats,
    _display_cache_report,
)


# ============================================================================
# cmd_cache_stats Tests
# ============================================================================


@pytest.mark.unit
class TestCmdCacheStats:
    """Test suite for cmd_cache_stats command."""

    @patch("empathy_os.cli.commands.cache._collect_cache_stats")
    @patch("empathy_os.cli.commands.cache._display_cache_report")
    def test_cache_stats_calls_collect(self, mock_display, mock_collect):
        """Test that cache_stats calls _collect_cache_stats."""
        # Given
        mock_collect.return_value = {
            "days_analyzed": 7,
            "total_requests": 100,
            "cache_hits": 50,
        }
        args = Mock()
        args.days = 7
        args.format = "table"
        args.verbose = False

        # When
        cmd_cache_stats(args)

        # Then
        mock_collect.assert_called_once_with(days=7)
        mock_display.assert_called_once()

    @patch("empathy_os.cli.commands.cache._collect_cache_stats")
    def test_cache_stats_json_output(self, mock_collect):
        """Test cache_stats with JSON format."""
        # Given
        stats = {
            "days_analyzed": 7,
            "total_requests": 100,
            "cache_hits": 50,
        }
        mock_collect.return_value = stats
        
        args = Mock()
        args.days = 7
        args.format = "json"
        args.verbose = False

        # When
        cmd_cache_stats(args)

        # Then
        mock_collect.assert_called_once_with(days=7)


# ============================================================================
# cmd_cache_clear Tests
# ============================================================================


@pytest.mark.unit
class TestCmdCacheClear:
    """Test suite for cmd_cache_clear command."""

    def test_cache_clear_returns_none(self):
        """Test that cache_clear completes without errors."""
        # Given
        args = Mock()

        # When
        result = cmd_cache_clear(args)

        # Then
        assert result is None


# ============================================================================
# _collect_cache_stats Tests
# ============================================================================


@pytest.mark.unit
class TestCollectCacheStats:
    """Test suite for _collect_cache_stats function."""

    def test_collect_stats_no_log_file(self):
        """Test _collect_cache_stats when no log file found."""
        # When
        with patch("pathlib.Path.exists", return_value=False):
            stats = _collect_cache_stats(days=7)

        # Then
        assert "error" in stats
        assert stats["total_requests"] == 0
        assert stats["cache_hits"] == 0

    @patch("builtins.open", new_callable=mock_open, read_data="")
    @patch("pathlib.Path.exists", return_value=True)
    def test_collect_stats_empty_log(self, mock_exists, mock_file):
        """Test _collect_cache_stats with empty log file."""
        # When
        stats = _collect_cache_stats(days=7)

        # Then
        assert stats["days_analyzed"] == 7
        assert stats["total_requests"] >= 0

    @patch("builtins.open", new_callable=mock_open, read_data="2026-01-30 10:00:00 - Cache HIT: 1,000 tokens read, saved $0.50\n")
    @patch("pathlib.Path.exists", return_value=True)
    def test_collect_stats_with_cache_hit(self, mock_exists, mock_file):
        """Test _collect_cache_stats parses cache hit correctly."""
        # When
        stats = _collect_cache_stats(days=7)

        # Then
        assert stats["cache_hits"] >= 1
        assert stats["total_cache_read_tokens"] >= 1000
        assert stats["total_savings"] >= 0.50


# ============================================================================
# _display_cache_report Tests
# ============================================================================


@pytest.mark.unit
class TestDisplayCacheReport:
    """Test suite for _display_cache_report function."""

    def test_display_report_with_error(self):
        """Test _display_cache_report handles error stats."""
        # Given
        stats = {
            "error": "No log file found",
            "message": "Enable logging"
        }

        # When
        result = _display_cache_report(stats, verbose=False)

        # Then
        assert result is None  # Should complete without exception

    def test_display_report_normal_stats(self):
        """Test _display_cache_report with normal stats."""
        # Given
        stats = {
            "days_analyzed": 7,
            "log_file": "/tmp/test.log",
            "total_requests": 100,
            "cache_hits": 50,
            "cache_writes": 30,
            "cache_hit_rate": 50.0,
            "total_cache_read_tokens": 10000,
            "total_cache_write_tokens": 5000,
            "total_savings": 12.50,
            "avg_savings_per_hit": 0.25
        }

        # When
        result = _display_cache_report(stats, verbose=False)

        # Then
        assert result is None

    def test_display_report_verbose_mode(self):
        """Test _display_cache_report in verbose mode."""
        # Given
        stats = {
            "days_analyzed": 7,
            "log_file": "/tmp/test.log",
            "total_requests": 100,
            "cache_hits": 50,
            "cache_writes": 30,
            "cache_hit_rate": 50.0,
            "total_cache_read_tokens": 10000,
            "total_cache_write_tokens": 5000,
            "total_savings": 12.50,
            "avg_savings_per_hit": 0.25
        }

        # When
        result = _display_cache_report(stats, verbose=True)

        # Then
        assert result is None


# ============================================================================
# Edge Cases
# ============================================================================


@pytest.mark.unit
class TestCacheEdgeCases:
    """Test suite for edge cases."""

