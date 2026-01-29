"""Behavioral tests for cli/utils/data.py - CLI help data and cheatsheets.

Tests Given/When/Then pattern for data structures.

Copyright 2026 Smart-AI-Memory
Licensed under Apache 2.0
"""

import pytest

from empathy_os.cli.utils.data import CHEATSHEET, EXPLAIN_CONTENT


class TestCheatsheet:
    """Behavioral tests for CHEATSHEET data structure."""

    def test_cheatsheet_is_dict(self):
        """Given: CHEATSHEET constant
        When: Checking type
        Then: It is a dictionary."""
        # Given/When/Then
        assert isinstance(CHEATSHEET, dict)

    def test_cheatsheet_has_getting_started_section(self):
        """Given: CHEATSHEET data
        When: Looking for 'Getting Started'
        Then: Section exists with commands."""
        # Given/When
        section = CHEATSHEET.get("Getting Started")

        # Then
        assert section is not None
        assert isinstance(section, list)
        assert len(section) > 0

    def test_cheatsheet_has_daily_workflow_section(self):
        """Given: CHEATSHEET data
        When: Looking for 'Daily Workflow'
        Then: Section exists with commands."""
        # Given/When
        section = CHEATSHEET.get("Daily Workflow")

        # Then
        assert section is not None
        assert isinstance(section, list)
        assert len(section) > 0

    def test_cheatsheet_has_code_quality_section(self):
        """Given: CHEATSHEET data
        When: Looking for 'Code Quality'
        Then: Section exists with commands."""
        # Given/When
        section = CHEATSHEET.get("Code Quality")

        # Then
        assert section is not None
        assert isinstance(section, list)

    def test_cheatsheet_has_pattern_learning_section(self):
        """Given: CHEATSHEET data
        When: Looking for 'Pattern Learning'
        Then: Section exists with commands."""
        # Given/When
        section = CHEATSHEET.get("Pattern Learning")

        # Then
        assert section is not None
        assert isinstance(section, list)

    def test_cheatsheet_commands_are_tuples(self):
        """Given: Any cheatsheet section
        When: Examining command entries
        Then: Each is (command, description) tuple."""
        # Given
        section = CHEATSHEET["Getting Started"]

        # When/Then
        for entry in section:
            assert isinstance(entry, tuple)
            assert len(entry) == 2
            assert isinstance(entry[0], str)  # command
            assert isinstance(entry[1], str)  # description

    def test_cheatsheet_init_command_exists(self):
        """Given: Getting Started section
        When: Looking for init command
        Then: Command is present."""
        # Given
        section = CHEATSHEET["Getting Started"]

        # When
        commands = [cmd for cmd, _ in section]

        # Then
        assert "empathy init" in commands

    def test_cheatsheet_morning_command_exists(self):
        """Given: Daily Workflow section
        When: Looking for morning command
        Then: Command is present."""
        # Given
        section = CHEATSHEET["Daily Workflow"]

        # When
        commands = [cmd for cmd, _ in section]

        # Then
        assert "empathy morning" in commands

    def test_cheatsheet_health_command_exists(self):
        """Given: Code Quality section
        When: Looking for health command
        Then: Command is present."""
        # Given
        section = CHEATSHEET["Code Quality"]

        # When
        commands = [cmd for cmd, _ in section]

        # Then
        assert "empathy health" in commands

    def test_all_sections_have_at_least_one_command(self):
        """Given: All cheatsheet sections
        When: Checking each section
        Then: Each has at least one command."""
        # Given/When/Then
        for section_name, commands in CHEATSHEET.items():
            assert len(commands) > 0, f"Section '{section_name}' is empty"


class TestExplainContent:
    """Behavioral tests for EXPLAIN_CONTENT data structure."""

    def test_explain_content_is_dict(self):
        """Given: EXPLAIN_CONTENT constant
        When: Checking type
        Then: It is a dictionary."""
        # Given/When/Then
        assert isinstance(EXPLAIN_CONTENT, dict)

    def test_explain_content_has_morning_explanation(self):
        """Given: EXPLAIN_CONTENT data
        When: Looking for 'morning' explanation
        Then: Explanation exists."""
        # Given/When
        explanation = EXPLAIN_CONTENT.get("morning")

        # Then
        assert explanation is not None
        assert isinstance(explanation, str)
        assert len(explanation) > 100  # Detailed explanation

    def test_explain_content_has_ship_explanation(self):
        """Given: EXPLAIN_CONTENT data
        When: Looking for 'ship' explanation
        Then: Explanation exists."""
        # Given/When
        explanation = EXPLAIN_CONTENT.get("ship")

        # Then
        assert explanation is not None
        assert isinstance(explanation, str)

    def test_explain_content_has_learn_explanation(self):
        """Given: EXPLAIN_CONTENT data
        When: Looking for 'learn' explanation
        Then: Explanation exists."""
        # Given/When
        explanation = EXPLAIN_CONTENT.get("learn")

        # Then
        assert explanation is not None
        assert isinstance(explanation, str)

    def test_explain_content_has_health_explanation(self):
        """Given: EXPLAIN_CONTENT data
        When: Looking for 'health' explanation
        Then: Explanation exists."""
        # Given/When
        explanation = EXPLAIN_CONTENT.get("health")

        # Then
        assert explanation is not None
        assert isinstance(explanation, str)

    def test_explain_content_has_sync_claude_explanation(self):
        """Given: EXPLAIN_CONTENT data
        When: Looking for 'sync-claude' explanation
        Then: Explanation exists."""
        # Given/When
        explanation = EXPLAIN_CONTENT.get("sync-claude")

        # Then
        assert explanation is not None
        assert isinstance(explanation, str)

    def test_morning_explanation_mentions_patterns(self):
        """Given: 'morning' explanation
        When: Checking content
        Then: Mentions pattern analysis."""
        # Given
        explanation = EXPLAIN_CONTENT["morning"]

        # When/Then
        assert "PATTERNS ANALYSIS" in explanation or "patterns" in explanation.lower()

    def test_ship_explanation_mentions_validation(self):
        """Given: 'ship' explanation
        When: Checking content
        Then: Mentions validation/checks."""
        # Given
        explanation = EXPLAIN_CONTENT["ship"]

        # When/Then
        assert "validation" in explanation.lower() or "checks" in explanation.lower()

    def test_learn_explanation_mentions_commits(self):
        """Given: 'learn' explanation
        When: Checking content
        Then: Mentions commit analysis."""
        # Given
        explanation = EXPLAIN_CONTENT["learn"]

        # When/Then
        assert "COMMIT" in explanation or "commit" in explanation.lower()

    def test_health_explanation_mentions_scoring(self):
        """Given: 'health' explanation
        When: Checking content
        Then: Mentions scoring system."""
        # Given
        explanation = EXPLAIN_CONTENT["health"]

        # When/Then
        assert "SCORING" in explanation or "score" in explanation.lower()

    def test_sync_claude_explanation_mentions_claude_code(self):
        """Given: 'sync-claude' explanation
        When: Checking content
        Then: Mentions Claude Code."""
        # Given
        explanation = EXPLAIN_CONTENT["sync-claude"]

        # When/Then
        assert "Claude Code" in explanation or "CLAUDE CODE" in explanation

    def test_all_explanations_are_multiline(self):
        """Given: All explanation texts
        When: Checking length
        Then: Each is detailed (multiple lines)."""
        # Given/When/Then
        for command, explanation in EXPLAIN_CONTENT.items():
            assert "\n" in explanation, f"'{command}' explanation is single-line"
            assert len(explanation.split("\n")) > 5, f"'{command}' explanation too short"
