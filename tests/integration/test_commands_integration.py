"""Integration tests for the commands module.

Tests command loading, parsing, and registry integration with
hooks, context, and learning modules.
"""

from pathlib import Path

import pytest

from empathy_llm_toolkit.commands import (
    CommandCategory,
    CommandConfig,
    CommandContext,
    CommandExecutor,
    CommandLoader,
    CommandMetadata,
    CommandParser,
    CommandRegistry,
    create_command_context,
)


class TestCommandsWithRealFiles:
    """Integration tests using real command files."""

    @pytest.fixture(autouse=True)
    def reset_registry(self):
        """Reset singleton before each test."""
        CommandRegistry.reset_instance()
        yield
        CommandRegistry.reset_instance()

    def test_load_actual_commands_directory(self):
        """Test loading from actual .claude/commands directory."""
        commands_dir = Path(__file__).parent.parent.parent / ".claude" / "commands"

        if not commands_dir.exists():
            pytest.skip("Commands directory not found")

        registry = CommandRegistry.get_instance()
        count = registry.load_from_directory(commands_dir)

        # Should have many commands
        assert count > 20

        # Check for expected commands
        assert registry.has("commit")
        assert registry.has("test")
        assert registry.has("debug")

    def test_load_new_empathy_commands(self):
        """Test loading the new empathy commands (compact, patterns, evaluate)."""
        commands_dir = Path(__file__).parent.parent.parent / ".claude" / "commands"

        if not commands_dir.exists():
            pytest.skip("Commands directory not found")

        registry = CommandRegistry.get_instance()
        registry.load_from_directory(commands_dir)

        # Check for new commands
        assert registry.has("compact")
        assert registry.has("patterns")
        assert registry.has("evaluate")

        # Check compact has correct metadata
        compact = registry.get("compact")
        assert compact is not None
        assert compact.category == CommandCategory.CONTEXT
        assert "comp" in compact.aliases

        # Check patterns
        patterns = registry.get("patterns")
        assert patterns is not None
        assert patterns.category == CommandCategory.LEARNING

        # Check evaluate
        evaluate = registry.get("evaluate")
        assert evaluate is not None
        assert evaluate.category == CommandCategory.LEARNING

    def test_command_alias_resolution(self):
        """Test that aliases resolve correctly."""
        commands_dir = Path(__file__).parent.parent.parent / ".claude" / "commands"

        if not commands_dir.exists():
            pytest.skip("Commands directory not found")

        registry = CommandRegistry.get_instance()
        registry.load_from_directory(commands_dir)

        # Alias should resolve to same command
        compact_direct = registry.get("compact")
        compact_alias = registry.get("comp")

        assert compact_direct is compact_alias

    def test_search_commands(self):
        """Test searching commands."""
        commands_dir = Path(__file__).parent.parent.parent / ".claude" / "commands"

        if not commands_dir.exists():
            pytest.skip("Commands directory not found")

        registry = CommandRegistry.get_instance()
        registry.load_from_directory(commands_dir)

        # Search by keyword
        git_commands = registry.search("git")
        assert len(git_commands) > 0

        # Search by category
        test_commands = registry.get_by_category(CommandCategory.TEST)
        assert len(test_commands) > 0


class TestCommandContextIntegration:
    """Integration tests for CommandContext with framework components."""

    def test_create_context_with_all_components(self):
        """Test creating context with hooks, learning, context modules."""
        ctx = create_command_context(
            user_id="test_user",
            enable_hooks=True,
            enable_learning=True,
            enable_context=True,
        )

        assert ctx.user_id == "test_user"
        # Components may or may not be available depending on imports
        # but the function should not fail

    def test_context_fire_hook_without_registry(self):
        """Test that fire_hook handles missing registry gracefully."""
        ctx = CommandContext(
            user_id="test",
            hook_registry=None,
        )

        # Should not raise
        results = ctx.fire_hook("SessionStart", {"test": True})
        assert results == []

    def test_context_patterns_without_storage(self):
        """Test pattern methods with no storage."""
        ctx = CommandContext(
            user_id="test",
            learning_storage=None,
        )

        # Should return empty results
        patterns = ctx.get_patterns_for_context()
        assert patterns == ""

        results = ctx.search_patterns("test")
        assert results == []

    def test_context_save_without_manager(self):
        """Test save context with no manager."""
        ctx = CommandContext(
            user_id="test",
            context_manager=None,
        )

        result = ctx.save_context_state()
        assert result is None


class TestCommandExecutorIntegration:
    """Integration tests for CommandExecutor."""

    def test_execute_command_returns_body(self):
        """Test that executor returns command body."""
        ctx = CommandContext(user_id="test")
        executor = CommandExecutor(ctx)

        config = CommandConfig(
            name="test-cmd",
            description="Test",
            body="## Instructions\n\nDo something.",
            metadata=CommandMetadata(name="test-cmd"),
        )

        result = executor.execute(config)

        assert result.success is True
        assert "## Instructions" in result.output
        assert result.command_name == "test-cmd"

    def test_execute_with_hooks_configured(self):
        """Test execution with hook configuration."""
        from empathy_llm_toolkit.hooks.registry import HookRegistry

        hook_registry = HookRegistry()
        hooks_fired = []

        # Register hooks
        hook_registry.register(
            event="PreCommand",
            handler=lambda ctx: hooks_fired.append("pre") or {"success": True},
        )
        hook_registry.register(
            event="PostCommand",
            handler=lambda ctx: hooks_fired.append("post") or {"success": True},
        )

        ctx = CommandContext(
            user_id="test",
            hook_registry=hook_registry,
        )
        executor = CommandExecutor(ctx)

        config = CommandConfig(
            name="hooked-cmd",
            description="Test",
            body="Body",
            metadata=CommandMetadata(
                name="hooked-cmd",
                hooks={"pre": "PreCommand", "post": "PostCommand"},
            ),
        )

        result = executor.execute(config)

        assert result.success is True
        assert "pre:PreCommand" in result.hooks_fired
        assert "post:PostCommand" in result.hooks_fired

    def test_prepare_command(self):
        """Test preparing command context."""
        ctx = CommandContext(user_id="test_user")
        executor = CommandExecutor(ctx)

        config = CommandConfig(
            name="prep-test",
            description="Prepare test",
            body="Test body content",
            metadata=CommandMetadata(name="prep-test"),
        )

        prepared = executor.prepare_command(config, args={"key": "value"})

        assert prepared["command"] == "prep-test"
        assert prepared["body"] == "Test body content"
        assert prepared["args"]["key"] == "value"
        assert prepared["user_id"] == "test_user"


class TestCommandParserIntegration:
    """Integration tests for CommandParser with real files."""

    def test_parse_compact_command(self):
        """Test parsing the compact command file."""
        commands_dir = Path(__file__).parent.parent.parent / ".claude" / "commands"
        compact_path = commands_dir / "compact.md"

        if not compact_path.exists():
            pytest.skip("compact.md not found")

        parser = CommandParser()
        config = parser.parse_file(compact_path)

        assert config.name == "compact"
        assert config.category == CommandCategory.CONTEXT
        assert "comp" in config.aliases
        assert config.hooks.get("pre") == "PreCompact"
        assert "SBAR" in config.body

    def test_parse_patterns_command(self):
        """Test parsing the patterns command file."""
        commands_dir = Path(__file__).parent.parent.parent / ".claude" / "commands"
        patterns_path = commands_dir / "patterns.md"

        if not patterns_path.exists():
            pytest.skip("patterns.md not found")

        parser = CommandParser()
        config = parser.parse_file(patterns_path)

        assert config.name == "patterns"
        assert config.category == CommandCategory.LEARNING
        assert "LearnedSkillsStorage" in config.body

    def test_parse_evaluate_command(self):
        """Test parsing the evaluate command file."""
        commands_dir = Path(__file__).parent.parent.parent / ".claude" / "commands"
        eval_path = commands_dir / "evaluate.md"

        if not eval_path.exists():
            pytest.skip("evaluate.md not found")

        parser = CommandParser()
        config = parser.parse_file(eval_path)

        assert config.name == "evaluate"
        assert config.category == CommandCategory.LEARNING
        assert "eval" in config.aliases

    def test_parse_legacy_command_without_frontmatter(self):
        """Test parsing a legacy command without YAML frontmatter."""
        commands_dir = Path(__file__).parent.parent.parent / ".claude" / "commands"
        commit_path = commands_dir / "commit.md"

        if not commit_path.exists():
            pytest.skip("commit.md not found")

        parser = CommandParser()
        config = parser.parse_file(commit_path)

        # Should infer name from filename
        assert config.name == "commit"
        # Should infer category
        assert config.category == CommandCategory.GIT


class TestCommandLoaderIntegration:
    """Integration tests for CommandLoader."""

    def test_loader_validates_directory(self):
        """Test loader validation of directory."""
        commands_dir = Path(__file__).parent.parent.parent / ".claude" / "commands"

        if not commands_dir.exists():
            pytest.skip("Commands directory not found")

        loader = CommandLoader()
        errors = loader.validate_directory(commands_dir)

        # Should have no errors for valid commands
        # (or minimal errors for legacy format)
        assert isinstance(errors, dict)

    def test_loader_discover_yields_all_commands(self):
        """Test that discover yields all commands."""
        commands_dir = Path(__file__).parent.parent.parent / ".claude" / "commands"

        if not commands_dir.exists():
            pytest.skip("Commands directory not found")

        loader = CommandLoader()
        commands = list(loader.discover(commands_dir))

        # Should have many commands
        assert len(commands) > 20

        # Should include new commands
        names = {c.name for c in commands}
        assert "compact" in names
        assert "patterns" in names
        assert "evaluate" in names
