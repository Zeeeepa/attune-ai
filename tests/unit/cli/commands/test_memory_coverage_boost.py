"""Tests for memory CLI commands.

Module: cli/commands/memory.py (48 lines)
"""

import pytest
from unittest.mock import patch

from empathy_os.cli.commands.memory import (
    memory_app,
    memory_status,
    memory_start,
    memory_stop,
    memory_stats,
    memory_patterns,
)


@pytest.mark.unit
class TestMemoryApp:
    """Test suite for memory Typer app."""

    def test_memory_app_exists(self):
        """Test that memory_app Typer instance exists."""
        assert memory_app is not None


@pytest.mark.unit
class TestMemoryCommands:
    """Test suite for individual memory commands."""

    @patch("subprocess.run")
    def test_memory_status_calls_subprocess(self, mock_run):
        """Test that memory_status calls subprocess."""
        memory_status()
        
        mock_run.assert_called_once()
        args = mock_run.call_args[0][0]
        assert "empathy_os.memory.control_panel" in args
        assert "status" in args

    @patch("subprocess.run")
    def test_memory_start_calls_subprocess(self, mock_run):
        """Test that memory_start calls subprocess."""
        memory_start()
        
        mock_run.assert_called_once()
        args = mock_run.call_args[0][0]
        assert "start" in args

    @patch("subprocess.run")
    def test_memory_stop_calls_subprocess(self, mock_run):
        """Test that memory_stop calls subprocess."""
        memory_stop()
        
        mock_run.assert_called_once()
        args = mock_run.call_args[0][0]
        assert "stop" in args

    @patch("subprocess.run")
    def test_memory_stats_calls_subprocess(self, mock_run):
        """Test that memory_stats calls subprocess."""
        memory_stats()
        
        mock_run.assert_called_once()
        args = mock_run.call_args[0][0]
        assert "stats" in args

    @patch("subprocess.run")
    def test_memory_patterns_calls_subprocess(self, mock_run):
        """Test that memory_patterns calls subprocess."""
        memory_patterns()
        
        mock_run.assert_called_once()
        args = mock_run.call_args[0][0]
        assert "patterns" in args
        assert "--list" in args
