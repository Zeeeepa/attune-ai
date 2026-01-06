"""Unit tests for unified CLI (Typer-based)

Tests the main Empathy Framework CLI entry point.

Copyright 2025 Smart-AI-Memory
Licensed under Fair Source License 0.9
"""

import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
import typer
from typer.testing import CliRunner

from empathy_os.cli_unified import (
    app,
    cheatsheet,
    costs,
    dashboard,
    fix_all,
    get_empathy_version,
    health,
    init,
    inspect_cmd,
    learn,
    memory_patterns,
    memory_start,
    memory_stats,
    memory_status,
    memory_stop,
    morning,
    provider_show,
    run_repl,
    scan,
    ship,
    status,
    sync_claude,
    version_callback,
    wizard_list,
    wizard_run,
    workflow_list,
    workflow_run,
)


@pytest.mark.unit
class TestGetEmpathyVersion:
    """Test version retrieval."""

    def test_get_version_success(self):
        """Test getting version when package is installed."""
        with patch("empathy_os.cli_unified.get_version") as mock_get_version:
            mock_get_version.return_value = "1.8.0"
            version = get_empathy_version()

            assert version == "1.8.0"
            mock_get_version.assert_called_once_with("empathy-framework")

    def test_get_version_fallback(self):
        """Test version fallback when package not found."""
        with patch("empathy_os.cli_unified.get_version") as mock_get_version:
            mock_get_version.side_effect = Exception("Package not found")
            version = get_empathy_version()

            assert version == "dev"


@pytest.mark.unit
class TestVersionCallback:
    """Test version callback."""

    def test_version_callback_true(self):
        """Test version callback when enabled."""
        with patch("empathy_os.cli_unified.console") as mock_console:
            with pytest.raises(typer.Exit):
                version_callback(True)

            mock_console.print.assert_called_once()
            call_args = mock_console.print.call_args[0][0]
            assert "Empathy Framework" in call_args

    def test_version_callback_false(self):
        """Test version callback when disabled."""
        result = version_callback(False)

        assert result is None


@pytest.mark.unit
class TestMemoryCommands:
    """Test memory subcommand group."""

    @patch("empathy_os.cli_unified.subprocess.run")
    def test_memory_status(self, mock_run):
        """Test memory status command."""
        memory_status()

        mock_run.assert_called_once_with(
            [sys.executable, "-m", "empathy_os.memory.control_panel", "status"], check=False
        )

    @patch("empathy_os.cli_unified.subprocess.run")
    def test_memory_start(self, mock_run):
        """Test memory start command."""
        memory_start()

        mock_run.assert_called_once_with(
            [sys.executable, "-m", "empathy_os.memory.control_panel", "start"], check=False
        )

    @patch("empathy_os.cli_unified.subprocess.run")
    def test_memory_stop(self, mock_run):
        """Test memory stop command."""
        memory_stop()

        mock_run.assert_called_once_with(
            [sys.executable, "-m", "empathy_os.memory.control_panel", "stop"], check=False
        )

    @patch("empathy_os.cli_unified.subprocess.run")
    def test_memory_stats(self, mock_run):
        """Test memory stats command."""
        memory_stats()

        mock_run.assert_called_once_with(
            [sys.executable, "-m", "empathy_os.memory.control_panel", "stats"], check=False
        )

    @patch("empathy_os.cli_unified.subprocess.run")
    def test_memory_patterns(self, mock_run):
        """Test memory patterns command."""
        memory_patterns()

        mock_run.assert_called_once_with(
            [sys.executable, "-m", "empathy_os.memory.control_panel", "patterns", "--list"],
            check=False,
        )


@pytest.mark.unit
class TestProviderCommands:
    """Test provider subcommand group."""

    @patch("empathy_os.cli_unified.subprocess.run")
    def test_provider_show_default(self, mock_run):
        """Test provider show with defaults."""
        ctx = MagicMock()
        ctx.invoked_subcommand = None

        provider_show(ctx)

        expected_args = [sys.executable, "-m", "empathy_os.models.cli", "provider"]
        mock_run.assert_called_once_with(expected_args, check=False)

    @patch("empathy_os.cli_unified.subprocess.run")
    def test_provider_show_set_provider(self, mock_run):
        """Test provider show with set option."""
        ctx = MagicMock()
        ctx.invoked_subcommand = None

        provider_show(ctx, set_provider="anthropic")

        expected_args = [
            sys.executable,
            "-m",
            "empathy_os.models.cli",
            "provider",
            "--set",
            "anthropic",
        ]
        mock_run.assert_called_once_with(expected_args, check=False)

    @patch("empathy_os.cli_unified.subprocess.run")
    def test_provider_show_interactive(self, mock_run):
        """Test provider show with interactive flag."""
        ctx = MagicMock()
        ctx.invoked_subcommand = None

        provider_show(ctx, interactive=True)

        expected_args = [
            sys.executable,
            "-m",
            "empathy_os.models.cli",
            "provider",
            "--interactive",
        ]
        mock_run.assert_called_once_with(expected_args, check=False)

    @patch("empathy_os.cli_unified.subprocess.run")
    def test_provider_show_json_format(self, mock_run):
        """Test provider show with JSON format."""
        ctx = MagicMock()
        ctx.invoked_subcommand = None

        provider_show(ctx, format_out="json")

        expected_args = [sys.executable, "-m", "empathy_os.models.cli", "provider", "-f", "json"]
        mock_run.assert_called_once_with(expected_args, check=False)

    @patch("empathy_os.cli_unified.subprocess.run")
    def test_provider_show_with_subcommand(self, mock_run):
        """Test provider show skips when subcommand invoked."""
        ctx = MagicMock()
        ctx.invoked_subcommand = "registry"

        provider_show(ctx)

        mock_run.assert_not_called()


@pytest.mark.unit
class TestProviderSubcommands:
    """Test provider subcommands."""

    @patch("empathy_os.cli_unified.subprocess.run")
    def test_provider_registry_default(self, mock_run):
        """Test provider registry command."""
        from empathy_os.cli_unified import provider_registry

        provider_registry()

        expected_args = [sys.executable, "-m", "empathy_os.models.cli", "registry"]
        mock_run.assert_called_once_with(expected_args, check=False)

    @patch("empathy_os.cli_unified.subprocess.run")
    def test_provider_registry_with_filter(self, mock_run):
        """Test provider registry with provider filter."""
        from empathy_os.cli_unified import provider_registry

        provider_registry(provider_filter="anthropic")

        expected_args = [
            sys.executable,
            "-m",
            "empathy_os.models.cli",
            "registry",
            "--provider",
            "anthropic",
        ]
        mock_run.assert_called_once_with(expected_args, check=False)

    @patch("empathy_os.cli_unified.subprocess.run")
    def test_provider_costs_default(self, mock_run):
        """Test provider costs with defaults."""
        from empathy_os.cli_unified import provider_costs

        provider_costs()

        expected_args = [
            sys.executable,
            "-m",
            "empathy_os.models.cli",
            "costs",
            "--input-tokens",
            "10000",
            "--output-tokens",
            "2000",
        ]
        mock_run.assert_called_once_with(expected_args, check=False)

    @patch("empathy_os.cli_unified.subprocess.run")
    def test_provider_costs_custom_tokens(self, mock_run):
        """Test provider costs with custom token counts."""
        from empathy_os.cli_unified import provider_costs

        provider_costs(input_tokens=50000, output_tokens=5000)

        expected_args = [
            sys.executable,
            "-m",
            "empathy_os.models.cli",
            "costs",
            "--input-tokens",
            "50000",
            "--output-tokens",
            "5000",
        ]
        mock_run.assert_called_once_with(expected_args, check=False)

    @patch("empathy_os.cli_unified.subprocess.run")
    def test_provider_telemetry_default(self, mock_run):
        """Test provider telemetry with no flags."""
        from empathy_os.cli_unified import provider_telemetry

        provider_telemetry()

        expected_args = [sys.executable, "-m", "empathy_os.models.cli", "telemetry"]
        mock_run.assert_called_once_with(expected_args, check=False)

    @patch("empathy_os.cli_unified.subprocess.run")
    def test_provider_telemetry_summary(self, mock_run):
        """Test provider telemetry with summary flag."""
        from empathy_os.cli_unified import provider_telemetry

        provider_telemetry(summary=True)

        expected_args = [
            sys.executable,
            "-m",
            "empathy_os.models.cli",
            "telemetry",
            "--summary",
        ]
        mock_run.assert_called_once_with(expected_args, check=False)

    @patch("empathy_os.cli_unified.subprocess.run")
    def test_provider_telemetry_costs(self, mock_run):
        """Test provider telemetry with costs flag."""
        from empathy_os.cli_unified import provider_telemetry

        provider_telemetry(costs=True)

        expected_args = [sys.executable, "-m", "empathy_os.models.cli", "telemetry", "--costs"]
        mock_run.assert_called_once_with(expected_args, check=False)

    @patch("empathy_os.cli_unified.subprocess.run")
    def test_provider_telemetry_providers(self, mock_run):
        """Test provider telemetry with providers flag."""
        from empathy_os.cli_unified import provider_telemetry

        provider_telemetry(providers=True)

        expected_args = [
            sys.executable,
            "-m",
            "empathy_os.models.cli",
            "telemetry",
            "--providers",
        ]
        mock_run.assert_called_once_with(expected_args, check=False)

    @patch("empathy_os.cli_unified.subprocess.run")
    def test_provider_telemetry_all_flags(self, mock_run):
        """Test provider telemetry with all flags."""
        from empathy_os.cli_unified import provider_telemetry

        provider_telemetry(summary=True, costs=True, providers=True)

        expected_args = [
            sys.executable,
            "-m",
            "empathy_os.models.cli",
            "telemetry",
            "--summary",
            "--costs",
            "--providers",
        ]
        mock_run.assert_called_once_with(expected_args, check=False)


@pytest.mark.unit
class TestScanCommand:
    """Test scan command."""

    @patch("empathy_os.cli_unified.subprocess.run")
    @patch("empathy_os.cli_unified.console")
    def test_scan_default(self, mock_console, mock_run):
        """Test scan with defaults."""
        mock_run.return_value = MagicMock(returncode=0)

        scan()

        expected_args = ["empathy-scan", "."]
        mock_run.assert_called_once_with(expected_args, check=False, capture_output=False)
        mock_console.print.assert_not_called()

    @patch("empathy_os.cli_unified.subprocess.run")
    @patch("empathy_os.cli_unified.console")
    def test_scan_with_path(self, mock_console, mock_run):
        """Test scan with custom path."""
        mock_run.return_value = MagicMock(returncode=0)

        scan(path=Path("/test/path"))

        expected_args = ["empathy-scan", "/test/path"]
        mock_run.assert_called_once_with(expected_args, check=False, capture_output=False)

    @patch("empathy_os.cli_unified.subprocess.run")
    @patch("empathy_os.cli_unified.console")
    def test_scan_json_format(self, mock_console, mock_run):
        """Test scan with JSON format."""
        mock_run.return_value = MagicMock(returncode=0)

        scan(format_out="json")

        expected_args = ["empathy-scan", ".", "--format", "json"]
        mock_run.assert_called_once_with(expected_args, check=False, capture_output=False)

    @patch("empathy_os.cli_unified.subprocess.run")
    @patch("empathy_os.cli_unified.console")
    def test_scan_with_fix(self, mock_console, mock_run):
        """Test scan with fix flag."""
        mock_run.return_value = MagicMock(returncode=0)

        scan(fix=True)

        expected_args = ["empathy-scan", ".", "--fix"]
        mock_run.assert_called_once_with(expected_args, check=False, capture_output=False)

    @patch("empathy_os.cli_unified.subprocess.run")
    @patch("empathy_os.cli_unified.console")
    def test_scan_staged_only(self, mock_console, mock_run):
        """Test scan with staged flag."""
        mock_run.return_value = MagicMock(returncode=0)

        scan(staged=True)

        expected_args = ["empathy-scan", ".", "--staged"]
        mock_run.assert_called_once_with(expected_args, check=False, capture_output=False)

    @patch("empathy_os.cli_unified.subprocess.run")
    @patch("empathy_os.cli_unified.console")
    def test_scan_not_installed(self, mock_console, mock_run):
        """Test scan when command not available."""
        mock_run.return_value = MagicMock(returncode=1)

        scan()

        assert mock_console.print.call_count == 2
        # Check warning messages
        calls = mock_console.print.call_args_list
        assert "empathy-scan may not be installed" in str(calls[0])
        assert "pip install empathy-framework[software]" in str(calls[1])


@pytest.mark.unit
class TestInspectCommand:
    """Test inspect command."""

    @patch("empathy_os.cli_unified.subprocess.run")
    @patch("empathy_os.cli_unified.console")
    def test_inspect_default(self, mock_console, mock_run):
        """Test inspect with defaults."""
        mock_run.return_value = MagicMock(returncode=0)

        inspect_cmd()

        expected_args = ["empathy-inspect", "."]
        mock_run.assert_called_once_with(expected_args, check=False, capture_output=False)

    @patch("empathy_os.cli_unified.subprocess.run")
    @patch("empathy_os.cli_unified.console")
    def test_inspect_with_path(self, mock_console, mock_run):
        """Test inspect with custom path."""
        mock_run.return_value = MagicMock(returncode=0)

        inspect_cmd(path=Path("/custom/path"))

        expected_args = ["empathy-inspect", "/custom/path"]
        mock_run.assert_called_once_with(expected_args, check=False, capture_output=False)

    @patch("empathy_os.cli_unified.subprocess.run")
    @patch("empathy_os.cli_unified.console")
    def test_inspect_sarif_format(self, mock_console, mock_run):
        """Test inspect with SARIF format."""
        mock_run.return_value = MagicMock(returncode=0)

        inspect_cmd(format_out="sarif")

        expected_args = ["empathy-inspect", ".", "--format", "sarif"]
        mock_run.assert_called_once_with(expected_args, check=False, capture_output=False)

    @patch("empathy_os.cli_unified.subprocess.run")
    @patch("empathy_os.cli_unified.console")
    def test_inspect_not_installed(self, mock_console, mock_run):
        """Test inspect when command not available."""
        mock_run.return_value = MagicMock(returncode=1)

        inspect_cmd()

        assert mock_console.print.call_count == 2


@pytest.mark.unit
class TestSyncClaudeCommand:
    """Test sync-claude command."""

    @patch("empathy_os.cli_unified.subprocess.run")
    def test_sync_claude_default(self, mock_run):
        """Test sync-claude with default source."""
        sync_claude()

        expected_args = ["empathy-sync-claude", "--source", "patterns"]
        mock_run.assert_called_once_with(expected_args, check=False)

    @patch("empathy_os.cli_unified.subprocess.run")
    def test_sync_claude_bugs_source(self, mock_run):
        """Test sync-claude with bugs source."""
        sync_claude(source="bugs")

        expected_args = ["empathy-sync-claude", "--source", "bugs"]
        mock_run.assert_called_once_with(expected_args, check=False)


@pytest.mark.unit
class TestWorkflowCommands:
    """Test workflow delegation commands."""

    @patch("empathy_os.cli_unified.subprocess.run")
    def test_morning_command(self, mock_run):
        """Test morning briefing command."""
        morning()

        expected_args = [sys.executable, "-m", "empathy_os.cli", "morning"]
        mock_run.assert_called_once_with(expected_args, check=False)

    @patch("empathy_os.cli_unified.subprocess.run")
    def test_ship_default(self, mock_run):
        """Test ship command with defaults."""
        ship()

        expected_args = [sys.executable, "-m", "empathy_os.cli", "ship"]
        mock_run.assert_called_once_with(expected_args, check=False)

    @patch("empathy_os.cli_unified.subprocess.run")
    def test_ship_tests_only(self, mock_run):
        """Test ship command with tests-only flag."""
        ship(tests_only=True)

        expected_args = [sys.executable, "-m", "empathy_os.cli", "ship", "--tests-only"]
        mock_run.assert_called_once_with(expected_args, check=False)

    @patch("empathy_os.cli_unified.subprocess.run")
    def test_ship_security_only(self, mock_run):
        """Test ship command with security-only flag."""
        ship(security_only=True)

        expected_args = [sys.executable, "-m", "empathy_os.cli", "ship", "--security-only"]
        mock_run.assert_called_once_with(expected_args, check=False)

    @patch("empathy_os.cli_unified.subprocess.run")
    def test_ship_skip_sync(self, mock_run):
        """Test ship command with skip-sync flag."""
        ship(skip_sync=True)

        expected_args = [sys.executable, "-m", "empathy_os.cli", "ship", "--skip-sync"]
        mock_run.assert_called_once_with(expected_args, check=False)

    @patch("empathy_os.cli_unified.subprocess.run")
    def test_ship_all_flags(self, mock_run):
        """Test ship command with all flags."""
        ship(tests_only=True, security_only=True, skip_sync=True)

        expected_args = [
            sys.executable,
            "-m",
            "empathy_os.cli",
            "ship",
            "--tests-only",
            "--security-only",
            "--skip-sync",
        ]
        mock_run.assert_called_once_with(expected_args, check=False)

    @patch("empathy_os.cli_unified.subprocess.run")
    def test_health_default(self, mock_run):
        """Test health command with defaults."""
        health()

        expected_args = [sys.executable, "-m", "empathy_os.cli", "health"]
        mock_run.assert_called_once_with(expected_args, check=False)

    @patch("empathy_os.cli_unified.subprocess.run")
    def test_health_deep(self, mock_run):
        """Test health command with deep flag."""
        health(deep=True)

        expected_args = [sys.executable, "-m", "empathy_os.cli", "health", "--deep"]
        mock_run.assert_called_once_with(expected_args, check=False)

    @patch("empathy_os.cli_unified.subprocess.run")
    def test_health_fix(self, mock_run):
        """Test health command with fix flag."""
        health(fix=True)

        expected_args = [sys.executable, "-m", "empathy_os.cli", "health", "--fix"]
        mock_run.assert_called_once_with(expected_args, check=False)

    @patch("empathy_os.cli_unified.subprocess.run")
    def test_fix_all_command(self, mock_run):
        """Test fix-all command."""
        fix_all()

        expected_args = [sys.executable, "-m", "empathy_os.cli", "fix-all"]
        mock_run.assert_called_once_with(expected_args, check=False)

    @patch("empathy_os.cli_unified.subprocess.run")
    def test_learn_default(self, mock_run):
        """Test learn command with default."""
        learn()

        expected_args = [sys.executable, "-m", "empathy_os.cli", "learn", "--analyze", "20"]
        mock_run.assert_called_once_with(expected_args, check=False)

    @patch("empathy_os.cli_unified.subprocess.run")
    def test_learn_custom_analyze(self, mock_run):
        """Test learn command with custom analyze count."""
        learn(analyze=50)

        expected_args = [sys.executable, "-m", "empathy_os.cli", "learn", "--analyze", "50"]
        mock_run.assert_called_once_with(expected_args, check=False)

    @patch("empathy_os.cli_unified.subprocess.run")
    def test_run_repl_command(self, mock_run):
        """Test run REPL command."""
        run_repl()

        expected_args = [sys.executable, "-m", "empathy_os.cli", "run"]
        mock_run.assert_called_once_with(expected_args, check=False)


@pytest.mark.unit
class TestWizardCommands:
    """Test wizard subcommand group."""

    @patch("empathy_os.cli_unified.subprocess.run")
    def test_wizard_list(self, mock_run):
        """Test wizard list command."""
        wizard_list()

        expected_args = [sys.executable, "-m", "empathy_os.cli", "frameworks"]
        mock_run.assert_called_once_with(expected_args, check=False)

    @patch("empathy_os.cli_unified.subprocess.run")
    @patch("empathy_os.cli_unified.console")
    def test_wizard_run_default(self, mock_console, mock_run):
        """Test wizard run with defaults."""
        wizard_run(name="code-review")

        expected_args = ["empathy-scan", ".", "--wizards", "code-review"]
        mock_run.assert_called_once_with(expected_args, check=False)
        mock_console.print.assert_called_once()

    @patch("empathy_os.cli_unified.subprocess.run")
    @patch("empathy_os.cli_unified.console")
    def test_wizard_run_custom_path(self, mock_console, mock_run):
        """Test wizard run with custom path."""
        wizard_run(name="security-scan", path=Path("/src"))

        expected_args = ["empathy-scan", "/src", "--wizards", "security-scan"]
        mock_run.assert_called_once_with(expected_args, check=False)


@pytest.mark.unit
class TestWorkflowSubcommands:
    """Test workflow subcommand group."""

    @patch("empathy_os.cli_unified.subprocess.run")
    def test_workflow_list(self, mock_run):
        """Test workflow list command."""
        workflow_list()

        expected_args = [sys.executable, "-m", "empathy_os.cli", "workflow", "list"]
        mock_run.assert_called_once_with(expected_args, check=False)

    @patch("empathy_os.cli_unified.subprocess.run")
    def test_workflow_run_default(self, mock_run):
        """Test workflow run with default path."""
        workflow_run(name="code-review")

        expected_args = [
            sys.executable,
            "-m",
            "empathy_os.cli",
            "workflow",
            "run",
            "code-review",
            ".",
        ]
        mock_run.assert_called_once_with(expected_args, check=False)

    @patch("empathy_os.cli_unified.subprocess.run")
    def test_workflow_run_custom_path(self, mock_run):
        """Test workflow run with custom path."""
        workflow_run(name="bug-predict", path=Path("/test/src"))

        expected_args = [
            sys.executable,
            "-m",
            "empathy_os.cli",
            "workflow",
            "run",
            "bug-predict",
            "/test/src",
        ]
        mock_run.assert_called_once_with(expected_args, check=False)


@pytest.mark.unit
class TestUtilityCommands:
    """Test utility commands."""

    @patch("empathy_os.cli_unified.console")
    def test_cheatsheet(self, mock_console):
        """Test cheatsheet command."""
        cheatsheet()

        mock_console.print.assert_called_once()
        # Check Panel.fit was called with cheatsheet content
        call_args = mock_console.print.call_args[0][0]
        assert "Getting Started" in str(call_args)

    @patch("empathy_os.cli_unified.subprocess.run")
    def test_dashboard(self, mock_run):
        """Test dashboard command."""
        dashboard()

        expected_args = [sys.executable, "-m", "empathy_os.cli", "dashboard"]
        mock_run.assert_called_once_with(expected_args, check=False)

    @patch("empathy_os.cli_unified.subprocess.run")
    def test_costs_command(self, mock_run):
        """Test costs command."""
        costs()

        expected_args = [sys.executable, "-m", "empathy_os.cli", "costs"]
        mock_run.assert_called_once_with(expected_args, check=False)

    @patch("empathy_os.cli_unified.subprocess.run")
    def test_init_command(self, mock_run):
        """Test init command."""
        init()

        expected_args = [sys.executable, "-m", "empathy_os.cli", "init"]
        mock_run.assert_called_once_with(expected_args, check=False)

    @patch("empathy_os.cli_unified.subprocess.run")
    def test_status_command(self, mock_run):
        """Test status command."""
        status()

        expected_args = [sys.executable, "-m", "empathy_os.cli", "status"]
        mock_run.assert_called_once_with(expected_args, check=False)


@pytest.mark.unit
class TestCLIIntegration:
    """Integration tests for CLI runner."""

    def test_cli_app_exists(self):
        """Test CLI app is created."""
        assert app is not None
        assert isinstance(app, typer.Typer)

    def test_cli_help_text(self):
        """Test CLI has help text."""
        runner = CliRunner()
        result = runner.invoke(app, ["--help"])

        assert result.exit_code == 0
        assert "Empathy Framework" in result.output

    @patch("empathy_os.cli_unified.get_version")
    def test_cli_version_flag(self, mock_get_version):
        """Test --version flag."""
        mock_get_version.return_value = "1.8.0"
        runner = CliRunner()
        result = runner.invoke(app, ["--version"])

        assert result.exit_code == 0
        assert "Empathy Framework" in result.output
        assert "1.8.0" in result.output


@pytest.mark.unit
class TestEdgeCases:
    """Test edge cases and error handling."""

    @patch("empathy_os.cli_unified.subprocess.run")
    def test_memory_commands_with_failing_subprocess(self, mock_run):
        """Test memory commands handle subprocess failures."""
        mock_run.return_value = MagicMock(returncode=1)

        # Should not raise exception
        memory_status()
        memory_start()
        memory_stop()

        assert mock_run.call_count == 3

    @patch("empathy_os.cli_unified.subprocess.run")
    @patch("empathy_os.cli_unified.console")
    def test_scan_all_options_combined(self, mock_console, mock_run):
        """Test scan with all options enabled."""
        mock_run.return_value = MagicMock(returncode=0)

        scan(path=Path("/test"), format_out="sarif", fix=True, staged=True)

        expected_args = ["empathy-scan", "/test", "--format", "sarif", "--fix", "--staged"]
        mock_run.assert_called_once_with(expected_args, check=False, capture_output=False)

    @patch("empathy_os.cli_unified.subprocess.run")
    def test_provider_show_with_all_options(self, mock_run):
        """Test provider show with all options."""
        ctx = MagicMock()
        ctx.invoked_subcommand = None

        provider_show(ctx, set_provider="hybrid", interactive=True, format_out="json")

        # Should have all options
        call_args = mock_run.call_args[0][0]
        assert "--set" in call_args
        assert "hybrid" in call_args
        assert "--interactive" in call_args
        assert "-f" in call_args
        assert "json" in call_args
