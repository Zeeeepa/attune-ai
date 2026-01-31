"""Tests for CLI info parsers.

Module: cli/parsers/info.py (26 lines)

Tests command registration for info and frameworks commands.
"""

import pytest
from argparse import ArgumentParser

from empathy_os.cli.parsers.info import register_parsers
from empathy_os.cli.commands import info as info_commands


@pytest.mark.unit
class TestInfoParserRegistration:
    """Test suite for info parser registration."""

    def test_registers_info_command(self):
        """Test that info command is registered."""
        # Given
        parser = ArgumentParser()
        subparsers = parser.add_subparsers()

        # When
        register_parsers(subparsers)
        args = parser.parse_args(["info"])

        # Then
        assert hasattr(args, "func")
        assert args.func == info_commands.cmd_info

    def test_info_command_has_config_argument(self):
        """Test that info command accepts --config argument."""
        # Given
        parser = ArgumentParser()
        subparsers = parser.add_subparsers()
        register_parsers(subparsers)

        # When
        args = parser.parse_args(["info", "--config", "test.yml"])

        # Then
        assert args.config == "test.yml"

    def test_info_config_argument_is_optional(self):
        """Test that --config is optional for info command."""
        # Given
        parser = ArgumentParser()
        subparsers = parser.add_subparsers()
        register_parsers(subparsers)

        # When
        args = parser.parse_args(["info"])

        # Then
        assert args.config is None


@pytest.mark.unit
class TestFrameworksParserRegistration:
    """Test suite for frameworks parser registration."""

    def test_registers_frameworks_command(self):
        """Test that frameworks command is registered."""
        # Given
        parser = ArgumentParser()
        subparsers = parser.add_subparsers()

        # When
        register_parsers(subparsers)
        args = parser.parse_args(["frameworks"])

        # Then
        assert hasattr(args, "func")
        assert args.func == info_commands.cmd_frameworks

    def test_frameworks_command_has_all_flag(self):
        """Test that frameworks command accepts --all flag."""
        # Given
        parser = ArgumentParser()
        subparsers = parser.add_subparsers()
        register_parsers(subparsers)

        # When
        args = parser.parse_args(["frameworks", "--all"])

        # Then
        assert args.all is True

    def test_frameworks_all_flag_defaults_to_false(self):
        """Test that --all defaults to False."""
        # Given
        parser = ArgumentParser()
        subparsers = parser.add_subparsers()
        register_parsers(subparsers)

        # When
        args = parser.parse_args(["frameworks"])

        # Then
        assert args.all is False

    def test_frameworks_command_has_recommend_argument(self):
        """Test that frameworks command accepts --recommend argument."""
        # Given
        parser = ArgumentParser()
        subparsers = parser.add_subparsers()
        register_parsers(subparsers)

        # When
        args = parser.parse_args(["frameworks", "--recommend", "testing"])

        # Then
        assert args.recommend == "testing"

    def test_frameworks_recommend_is_optional(self):
        """Test that --recommend is optional."""
        # Given
        parser = ArgumentParser()
        subparsers = parser.add_subparsers()
        register_parsers(subparsers)

        # When
        args = parser.parse_args(["frameworks"])

        # Then
        assert args.recommend is None

    def test_frameworks_command_has_json_flag(self):
        """Test that frameworks command accepts --json flag."""
        # Given
        parser = ArgumentParser()
        subparsers = parser.add_subparsers()
        register_parsers(subparsers)

        # When
        args = parser.parse_args(["frameworks", "--json"])

        # Then
        assert args.json is True

    def test_frameworks_json_flag_defaults_to_false(self):
        """Test that --json defaults to False."""
        # Given
        parser = ArgumentParser()
        subparsers = parser.add_subparsers()
        register_parsers(subparsers)

        # When
        args = parser.parse_args(["frameworks"])

        # Then
        assert args.json is False

    def test_frameworks_accepts_multiple_flags(self):
        """Test that frameworks command accepts multiple flags together."""
        # Given
        parser = ArgumentParser()
        subparsers = parser.add_subparsers()
        register_parsers(subparsers)

        # When
        args = parser.parse_args(["frameworks", "--all", "--json", "--recommend", "analysis"])

        # Then
        assert args.all is True
        assert args.json is True
        assert args.recommend == "analysis"
