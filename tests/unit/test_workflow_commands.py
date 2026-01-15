"""Tests for workflow_commands.py using real data and file I/O.

Copyright 2025 Smart AI Memory, LLC
Licensed under Fair Source 0.9
"""

import pytest
import json
import subprocess
from pathlib import Path
from datetime import datetime, timedelta

from empathy_os import workflow_commands


class TestLoadPatterns:
    """Test _load_patterns with real file I/O."""

    def test_load_patterns_from_existing_directory(self, tmp_path):
        """Test loading patterns from directory with real JSON files."""
        patterns_dir = tmp_path / "patterns"
        patterns_dir.mkdir()

        # Create real pattern files
        debugging_patterns = {
            "patterns": [
                {"id": "pattern1", "description": "Debug pattern 1"},
                {"id": "pattern2", "description": "Debug pattern 2"}
            ]
        }

        security_patterns = {
            "patterns": [
                {"id": "sec1", "description": "Security pattern 1"}
            ]
        }

        # Write real JSON files
        (patterns_dir / "debugging.json").write_text(json.dumps(debugging_patterns))
        (patterns_dir / "security.json").write_text(json.dumps(security_patterns))

        # Load patterns
        result = workflow_commands._load_patterns(str(patterns_dir))

        # Verify loaded correctly
        assert "debugging" in result
        assert len(result["debugging"]) == 2
        assert result["debugging"][0]["id"] == "pattern1"

        assert "security" in result
        assert len(result["security"]) == 1
        assert result["security"][0]["id"] == "sec1"

    def test_load_patterns_from_nonexistent_directory(self, tmp_path):
        """Test loading patterns when directory doesn't exist."""
        nonexistent_dir = tmp_path / "nonexistent"

        result = workflow_commands._load_patterns(str(nonexistent_dir))

        # Should return empty pattern structure
        assert isinstance(result, dict)
        assert "debugging" in result
        assert result["debugging"] == []
        assert "security" in result
        assert result["security"] == []

    def test_load_patterns_with_items_key(self, tmp_path):
        """Test loading patterns when JSON uses 'items' key instead of 'patterns'."""
        patterns_dir = tmp_path / "patterns"
        patterns_dir.mkdir()

        # Create pattern file with 'items' key
        tech_debt_data = {
            "items": [
                {"id": "debt1", "description": "Technical debt item 1"},
                {"id": "debt2", "description": "Technical debt item 2"}
            ]
        }

        (patterns_dir / "tech_debt.json").write_text(json.dumps(tech_debt_data))

        result = workflow_commands._load_patterns(str(patterns_dir))

        # Should load from 'items' key
        assert "tech_debt" in result
        assert len(result["tech_debt"]) == 2
        assert result["tech_debt"][0]["id"] == "debt1"

    def test_load_patterns_handles_invalid_json(self, tmp_path):
        """Test loading patterns with corrupted JSON file."""
        patterns_dir = tmp_path / "patterns"
        patterns_dir.mkdir()

        # Create invalid JSON file
        (patterns_dir / "debugging.json").write_text("{ invalid json }")

        result = workflow_commands._load_patterns(str(patterns_dir))

        # Should handle gracefully
        assert isinstance(result, dict)
        assert "debugging" in result
        # Should be empty due to JSON error
        assert result["debugging"] == []

    def test_load_patterns_handles_missing_files(self, tmp_path):
        """Test loading patterns when some pattern files are missing."""
        patterns_dir = tmp_path / "patterns"
        patterns_dir.mkdir()

        # Only create debugging patterns
        debugging_data = {"patterns": [{"id": "d1"}]}
        (patterns_dir / "debugging.json").write_text(json.dumps(debugging_data))

        result = workflow_commands._load_patterns(str(patterns_dir))

        # Should have debugging but empty others
        assert len(result["debugging"]) == 1
        assert result["security"] == []
        assert result["tech_debt"] == []


class TestLoadStats:
    """Test _load_stats with real file I/O."""

    def test_load_stats_from_existing_file(self, tmp_path):
        """Test loading stats from existing stats.json file."""
        empathy_dir = tmp_path / ".empathy"
        empathy_dir.mkdir()

        # Create real stats file
        stats_data = {
            "commands": {
                "morning": 5,
                "ship": 3
            },
            "last_session": "2025-01-14T10:00:00",
            "patterns_learned": 12
        }

        (empathy_dir / "stats.json").write_text(json.dumps(stats_data))

        result = workflow_commands._load_stats(str(empathy_dir))

        # Verify loaded correctly
        assert result["commands"]["morning"] == 5
        assert result["commands"]["ship"] == 3
        assert result["patterns_learned"] == 12
        assert result["last_session"] == "2025-01-14T10:00:00"

    def test_load_stats_from_nonexistent_file(self, tmp_path):
        """Test loading stats when file doesn't exist."""
        empathy_dir = tmp_path / ".empathy"
        empathy_dir.mkdir()

        result = workflow_commands._load_stats(str(empathy_dir))

        # Should return default structure
        assert result["commands"] == {}
        assert result["last_session"] is None
        assert result["patterns_learned"] == 0

    def test_load_stats_handles_invalid_json(self, tmp_path):
        """Test loading stats with corrupted JSON."""
        empathy_dir = tmp_path / ".empathy"
        empathy_dir.mkdir()

        (empathy_dir / "stats.json").write_text("{ corrupted }")

        result = workflow_commands._load_stats(str(empathy_dir))

        # Should return defaults on error
        assert result["commands"] == {}
        assert result["last_session"] is None


class TestSaveStats:
    """Test _save_stats with real file I/O."""

    def test_save_stats_creates_directory(self, tmp_path):
        """Test save_stats creates directory if it doesn't exist."""
        empathy_dir = tmp_path / ".empathy"

        stats_data = {
            "commands": {"morning": 1},
            "last_session": "2025-01-14",
            "patterns_learned": 5
        }

        workflow_commands._save_stats(stats_data, str(empathy_dir))

        # Verify directory was created
        assert empathy_dir.exists()
        assert empathy_dir.is_dir()

        # Verify file was created
        stats_file = empathy_dir / "stats.json"
        assert stats_file.exists()

    def test_save_stats_writes_valid_json(self, tmp_path):
        """Test save_stats writes valid JSON that can be read back."""
        empathy_dir = tmp_path / ".empathy"
        empathy_dir.mkdir()

        stats_data = {
            "commands": {
                "morning": 3,
                "ship": 2,
                "fix-all": 1
            },
            "last_session": "2025-01-14T12:00:00",
            "patterns_learned": 10
        }

        workflow_commands._save_stats(stats_data, str(empathy_dir))

        # Read back and verify
        stats_file = empathy_dir / "stats.json"
        loaded_data = json.loads(stats_file.read_text())

        assert loaded_data["commands"]["morning"] == 3
        assert loaded_data["commands"]["ship"] == 2
        assert loaded_data["patterns_learned"] == 10

    def test_save_stats_overwrites_existing_file(self, tmp_path):
        """Test save_stats overwrites existing stats file."""
        empathy_dir = tmp_path / ".empathy"
        empathy_dir.mkdir()

        # Save initial stats
        initial_stats = {"commands": {"morning": 1}, "patterns_learned": 5}
        workflow_commands._save_stats(initial_stats, str(empathy_dir))

        # Save updated stats
        updated_stats = {"commands": {"morning": 2}, "patterns_learned": 7}
        workflow_commands._save_stats(updated_stats, str(empathy_dir))

        # Verify updated stats were saved
        loaded = json.loads((empathy_dir / "stats.json").read_text())
        assert loaded["commands"]["morning"] == 2
        assert loaded["patterns_learned"] == 7

    def test_save_stats_handles_datetime_objects(self, tmp_path):
        """Test save_stats converts datetime objects to strings."""
        empathy_dir = tmp_path / ".empathy"
        empathy_dir.mkdir()

        now = datetime.now()
        stats_data = {
            "commands": {},
            "last_session": now,
            "patterns_learned": 0
        }

        # Should not raise error
        workflow_commands._save_stats(stats_data, str(empathy_dir))

        # Should be saved as string
        loaded = json.loads((empathy_dir / "stats.json").read_text())
        assert isinstance(loaded["last_session"], str)


class TestRunCommand:
    """Test _run_command with real subprocess calls."""

    def test_run_command_successful_execution(self):
        """Test running a successful command."""
        # Use a simple, reliable command
        success, output = workflow_commands._run_command(["echo", "hello world"])

        assert success is True
        assert "hello world" in output

    def test_run_command_failed_execution(self):
        """Test running a command that fails."""
        # Use a command that will fail
        success, output = workflow_commands._run_command(["false"])

        assert success is False

    def test_run_command_nonexistent_command(self):
        """Test running a command that doesn't exist."""
        success, output = workflow_commands._run_command(["nonexistent_command_12345"])

        assert success is False
        assert "not found" in output.lower() or "Command not found" in output

    def test_run_command_with_arguments(self):
        """Test running command with multiple arguments."""
        success, output = workflow_commands._run_command(["echo", "arg1", "arg2"])

        assert success is True
        assert "arg1" in output
        assert "arg2" in output

    def test_run_command_captures_stderr(self):
        """Test that stderr is captured in output."""
        # Use sh -c to write to stderr
        success, output = workflow_commands._run_command(
            ["sh", "-c", "echo 'error message' >&2"]
        )

        assert "error message" in output


class TestGetTechDebtTrend:
    """Test _get_tech_debt_trend with real file I/O."""

    def test_tech_debt_increasing_trend(self, tmp_path):
        """Test detecting increasing tech debt."""
        patterns_dir = tmp_path / "patterns"
        patterns_dir.mkdir()

        # Create tech debt file with increasing trend
        tech_debt_data = {
            "snapshots": [
                {"timestamp": "2025-01-10", "total_items": 5},
                {"timestamp": "2025-01-14", "total_items": 8}
            ]
        }

        (patterns_dir / "tech_debt.json").write_text(json.dumps(tech_debt_data))

        result = workflow_commands._get_tech_debt_trend(str(patterns_dir))

        assert result == "increasing"

    def test_tech_debt_decreasing_trend(self, tmp_path):
        """Test detecting decreasing tech debt."""
        patterns_dir = tmp_path / "patterns"
        patterns_dir.mkdir()

        # Create tech debt file with decreasing trend
        tech_debt_data = {
            "snapshots": [
                {"timestamp": "2025-01-10", "total_items": 10},
                {"timestamp": "2025-01-14", "total_items": 6}
            ]
        }

        (patterns_dir / "tech_debt.json").write_text(json.dumps(tech_debt_data))

        result = workflow_commands._get_tech_debt_trend(str(patterns_dir))

        assert result == "decreasing"

    def test_tech_debt_stable_trend(self, tmp_path):
        """Test detecting stable tech debt."""
        patterns_dir = tmp_path / "patterns"
        patterns_dir.mkdir()

        # Create tech debt file with stable values
        tech_debt_data = {
            "snapshots": [
                {"timestamp": "2025-01-10", "total_items": 7},
                {"timestamp": "2025-01-14", "total_items": 7}
            ]
        }

        (patterns_dir / "tech_debt.json").write_text(json.dumps(tech_debt_data))

        result = workflow_commands._get_tech_debt_trend(str(patterns_dir))

        assert result == "stable"

    def test_tech_debt_insufficient_data(self, tmp_path):
        """Test with insufficient snapshot data."""
        patterns_dir = tmp_path / "patterns"
        patterns_dir.mkdir()

        # Create tech debt file with only one snapshot
        tech_debt_data = {
            "snapshots": [
                {"timestamp": "2025-01-14", "total_items": 5}
            ]
        }

        (patterns_dir / "tech_debt.json").write_text(json.dumps(tech_debt_data))

        result = workflow_commands._get_tech_debt_trend(str(patterns_dir))

        assert result == "insufficient_data"

    def test_tech_debt_no_file(self, tmp_path):
        """Test when tech_debt.json doesn't exist."""
        patterns_dir = tmp_path / "patterns"
        patterns_dir.mkdir()

        result = workflow_commands._get_tech_debt_trend(str(patterns_dir))

        assert result == "unknown"

    def test_tech_debt_multiple_snapshots(self, tmp_path):
        """Test with multiple snapshots (uses last two)."""
        patterns_dir = tmp_path / "patterns"
        patterns_dir.mkdir()

        # Create tech debt file with many snapshots
        tech_debt_data = {
            "snapshots": [
                {"timestamp": "2025-01-01", "total_items": 10},
                {"timestamp": "2025-01-07", "total_items": 8},
                {"timestamp": "2025-01-10", "total_items": 12},
                {"timestamp": "2025-01-14", "total_items": 15}
            ]
        }

        (patterns_dir / "tech_debt.json").write_text(json.dumps(tech_debt_data))

        result = workflow_commands._get_tech_debt_trend(str(patterns_dir))

        # Should compare last two: 12 -> 15
        assert result == "increasing"


class TestStatsLoadSaveRoundTrip:
    """Integration tests for stats load/save workflow."""

    def test_save_and_load_roundtrip(self, tmp_path):
        """Test saving stats and loading them back."""
        empathy_dir = tmp_path / ".empathy"

        original_stats = {
            "commands": {
                "morning": 10,
                "ship": 5,
                "fix-all": 3,
                "learn": 2
            },
            "last_session": "2025-01-14T15:30:00",
            "patterns_learned": 25
        }

        # Save
        workflow_commands._save_stats(original_stats, str(empathy_dir))

        # Load
        loaded_stats = workflow_commands._load_stats(str(empathy_dir))

        # Verify roundtrip
        assert loaded_stats["commands"]["morning"] == 10
        assert loaded_stats["commands"]["ship"] == 5
        assert loaded_stats["patterns_learned"] == 25


class TestPatternsLoadingIntegration:
    """Integration tests for full pattern loading workflow."""

    def test_load_all_pattern_types(self, tmp_path):
        """Test loading all four pattern types."""
        patterns_dir = tmp_path / "patterns"
        patterns_dir.mkdir()

        # Create all pattern type files
        pattern_types = {
            "debugging": [{"id": "d1"}],
            "security": [{"id": "s1"}, {"id": "s2"}],
            "tech_debt": [{"id": "t1"}, {"id": "t2"}, {"id": "t3"}],
            "inspection": [{"id": "i1"}]
        }

        for pattern_type, patterns in pattern_types.items():
            data = {"patterns": patterns}
            (patterns_dir / f"{pattern_type}.json").write_text(json.dumps(data))

        # Load all
        result = workflow_commands._load_patterns(str(patterns_dir))

        # Verify all loaded
        assert len(result["debugging"]) == 1
        assert len(result["security"]) == 2
        assert len(result["tech_debt"]) == 3
        assert len(result["inspection"]) == 1
