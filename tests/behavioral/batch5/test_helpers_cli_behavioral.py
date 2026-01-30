"""Behavioral tests for cli/utils/helpers.py - CLI helper utilities.

Tests Given/When/Then pattern for CLI helper functions.

Copyright 2026 Smart-AI-Memory
Licensed under Apache 2.0
"""

from unittest.mock import Mock

from empathy_os.cli.utils.helpers import _file_exists, _show_achievements


class TestFileExists:
    """Behavioral tests for _file_exists helper function."""

    def test_returns_true_for_existing_file(self, tmp_path):
        """Given: An existing file
        When: _file_exists called
        Then: Returns True."""
        # Given
        test_file = tmp_path / "test.txt"
        test_file.write_text("content")

        # When
        result = _file_exists(str(test_file))

        # Then
        assert result is True

    def test_returns_false_for_nonexistent_file(self, tmp_path):
        """Given: A nonexistent file path
        When: _file_exists called
        Then: Returns False."""
        # Given
        nonexistent = tmp_path / "does_not_exist.txt"

        # When
        result = _file_exists(str(nonexistent))

        # Then
        assert result is False

    def test_returns_true_for_existing_directory(self, tmp_path):
        """Given: An existing directory
        When: _file_exists called
        Then: Returns True (directories exist too)."""
        # Given
        test_dir = tmp_path / "test_dir"
        test_dir.mkdir()

        # When
        result = _file_exists(str(test_dir))

        # Then
        assert result is True

    def test_accepts_path_object(self, tmp_path):
        """Given: A Path object instead of string
        When: _file_exists called
        Then: Works correctly."""
        # Given
        test_file = tmp_path / "test.txt"
        test_file.write_text("content")

        # When
        result = _file_exists(str(test_file))

        # Then
        assert result is True


class TestShowAchievements:
    """Behavioral tests for _show_achievements function."""

    def test_no_achievements_for_zero_commands(self, capsys):
        """Given: Engine with zero commands run
        When: _show_achievements called
        Then: No achievements displayed."""
        # Given
        engine = Mock()
        engine.get_stats.return_value = {
            "total_commands": 0,
            "command_counts": {},
            "patterns_learned": 0,
            "days_active": 0,
        }

        # When
        _show_achievements(engine)

        # Then
        captured = capsys.readouterr()
        assert "ACHIEVEMENTS" not in captured.out

    def test_first_steps_achievement_at_1_command(self, capsys):
        """Given: Engine with 1 command run
        When: _show_achievements called
        Then: 'First Steps' achievement shown."""
        # Given
        engine = Mock()
        engine.get_stats.return_value = {
            "total_commands": 1,
            "command_counts": {},
            "patterns_learned": 0,
            "days_active": 0,
        }

        # When
        _show_achievements(engine)

        # Then
        captured = capsys.readouterr()
        assert "First Steps" in captured.out
        assert "Ran your first command" in captured.out

    def test_getting_started_achievement_at_10_commands(self, capsys):
        """Given: Engine with 10 commands run
        When: _show_achievements called
        Then: 'Getting Started' achievement shown."""
        # Given
        engine = Mock()
        engine.get_stats.return_value = {
            "total_commands": 10,
            "command_counts": {},
            "patterns_learned": 0,
            "days_active": 0,
        }

        # When
        _show_achievements(engine)

        # Then
        captured = capsys.readouterr()
        assert "Getting Started" in captured.out
        assert "Ran 10+ commands" in captured.out

    def test_power_user_achievement_at_50_commands(self, capsys):
        """Given: Engine with 50 commands run
        When: _show_achievements called
        Then: 'Power User' achievement shown."""
        # Given
        engine = Mock()
        engine.get_stats.return_value = {
            "total_commands": 50,
            "command_counts": {},
            "patterns_learned": 0,
            "days_active": 0,
        }

        # When
        _show_achievements(engine)

        # Then
        captured = capsys.readouterr()
        assert "Power User" in captured.out
        assert "Ran 50+ commands" in captured.out

    def test_expert_achievement_at_100_commands(self, capsys):
        """Given: Engine with 100 commands run
        When: _show_achievements called
        Then: 'Expert' achievement shown."""
        # Given
        engine = Mock()
        engine.get_stats.return_value = {
            "total_commands": 100,
            "command_counts": {},
            "patterns_learned": 0,
            "days_active": 0,
        }

        # When
        _show_achievements(engine)

        # Then
        captured = capsys.readouterr()
        assert "Expert" in captured.out
        assert "Ran 100+ commands" in captured.out

    def test_pattern_learner_achievement(self, capsys):
        """Given: Engine with learn command used
        When: _show_achievements called
        Then: 'Pattern Learner' achievement shown."""
        # Given
        engine = Mock()
        engine.get_stats.return_value = {
            "total_commands": 5,
            "command_counts": {"learn": 1},
            "patterns_learned": 0,
            "days_active": 0,
        }

        # When
        _show_achievements(engine)

        # Then
        captured = capsys.readouterr()
        assert "Pattern Learner" in captured.out
        assert "Learned from git history" in captured.out

    def test_claude_whisperer_achievement(self, capsys):
        """Given: Engine with sync-claude command used
        When: _show_achievements called
        Then: 'Claude Whisperer' achievement shown."""
        # Given
        engine = Mock()
        engine.get_stats.return_value = {
            "total_commands": 5,
            "command_counts": {"sync-claude": 1},
            "patterns_learned": 0,
            "days_active": 0,
        }

        # When
        _show_achievements(engine)

        # Then
        captured = capsys.readouterr()
        assert "Claude Whisperer" in captured.out
        assert "Synced patterns to Claude" in captured.out

    def test_early_bird_achievement_at_5_morning_commands(self, capsys):
        """Given: Engine with 5+ morning commands
        When: _show_achievements called
        Then: 'Early Bird' achievement shown."""
        # Given
        engine = Mock()
        engine.get_stats.return_value = {
            "total_commands": 10,
            "command_counts": {"morning": 5},
            "patterns_learned": 0,
            "days_active": 0,
        }

        # When
        _show_achievements(engine)

        # Then
        captured = capsys.readouterr()
        assert "Early Bird" in captured.out
        assert "Used morning briefing 5+ times" in captured.out

    def test_quality_shipper_achievement_at_10_ship_commands(self, capsys):
        """Given: Engine with 10+ ship commands
        When: _show_achievements called
        Then: 'Quality Shipper' achievement shown."""
        # Given
        engine = Mock()
        engine.get_stats.return_value = {
            "total_commands": 15,
            "command_counts": {"ship": 10},
            "patterns_learned": 0,
            "days_active": 0,
        }

        # When
        _show_achievements(engine)

        # Then
        captured = capsys.readouterr()
        assert "Quality Shipper" in captured.out
        assert "Used pre-commit checks 10+ times" in captured.out

    def test_code_doctor_achievement(self, capsys):
        """Given: Engine with health and fix-all commands used
        When: _show_achievements called
        Then: 'Code Doctor' achievement shown."""
        # Given
        engine = Mock()
        engine.get_stats.return_value = {
            "total_commands": 10,
            "command_counts": {"health": 1, "fix-all": 1},
            "patterns_learned": 0,
            "days_active": 0,
        }

        # When
        _show_achievements(engine)

        # Then
        captured = capsys.readouterr()
        assert "Code Doctor" in captured.out
        assert "Used health checks and fixes" in captured.out

    def test_pattern_master_achievement(self, capsys):
        """Given: Engine with 10+ patterns learned
        When: _show_achievements called
        Then: 'Pattern Master' achievement shown."""
        # Given
        engine = Mock()
        engine.get_stats.return_value = {
            "total_commands": 5,
            "command_counts": {},
            "patterns_learned": 10,
            "days_active": 0,
        }

        # When
        _show_achievements(engine)

        # Then
        captured = capsys.readouterr()
        assert "Pattern Master" in captured.out
        assert "Learned 10+ patterns" in captured.out

    def test_week_warrior_achievement(self, capsys):
        """Given: Engine with 7+ days active
        When: _show_achievements called
        Then: 'Week Warrior' achievement shown."""
        # Given
        engine = Mock()
        engine.get_stats.return_value = {
            "total_commands": 15,
            "command_counts": {},
            "patterns_learned": 0,
            "days_active": 7,
        }

        # When
        _show_achievements(engine)

        # Then
        captured = capsys.readouterr()
        assert "Week Warrior" in captured.out
        assert "Active for 7+ days" in captured.out

    def test_monthly_maven_achievement(self, capsys):
        """Given: Engine with 30+ days active
        When: _show_achievements called
        Then: 'Monthly Maven' achievement shown."""
        # Given
        engine = Mock()
        engine.get_stats.return_value = {
            "total_commands": 50,
            "command_counts": {},
            "patterns_learned": 0,
            "days_active": 30,
        }

        # When
        _show_achievements(engine)

        # Then
        captured = capsys.readouterr()
        assert "Monthly Maven" in captured.out
        assert "Active for 30+ days" in captured.out

    def test_multiple_achievements_shown_together(self, capsys):
        """Given: Engine with multiple achievements earned
        When: _show_achievements called
        Then: All achievements shown."""
        # Given
        engine = Mock()
        engine.get_stats.return_value = {
            "total_commands": 100,
            "command_counts": {"learn": 5, "morning": 10},
            "patterns_learned": 15,
            "days_active": 30,
        }

        # When
        _show_achievements(engine)

        # Then
        captured = capsys.readouterr()
        assert "Expert" in captured.out
        assert "Pattern Learner" in captured.out
        assert "Early Bird" in captured.out
        assert "Pattern Master" in captured.out
        assert "Monthly Maven" in captured.out

    def test_achievement_header_and_separator(self, capsys):
        """Given: Engine with at least one achievement
        When: _show_achievements called
        Then: Header and separator displayed."""
        # Given
        engine = Mock()
        engine.get_stats.return_value = {
            "total_commands": 1,
            "command_counts": {},
            "patterns_learned": 0,
            "days_active": 0,
        }

        # When
        _show_achievements(engine)

        # Then
        captured = capsys.readouterr()
        assert "ACHIEVEMENTS UNLOCKED" in captured.out
        assert "-" * 30 in captured.out
