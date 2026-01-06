"""Tests for tech_debt_adapter.py exception handling.

This test suite verifies the tech debt adapter exception handling
implemented in Sprint 1 of the bug remediation plan.

Copyright 2025 Smart AI Memory, LLC
Licensed under Fair Source 0.9
"""

import logging
from pathlib import Path
from unittest.mock import AsyncMock, patch

import pytest

from agents.code_inspection.adapters.tech_debt_adapter import TechDebtAdapter


@pytest.fixture
def temp_project(tmp_path):
    """Create a temporary project structure."""
    # Create some Python files with tech debt markers
    (tmp_path / "src").mkdir()
    (tmp_path / "src" / "main.py").write_text("# TODO: Refactor this function\ndef main(): pass")
    (tmp_path / "src" / "utils.py").write_text("# FIXME: Handle edge case\ndef helper(): pass")
    return tmp_path


class TestMainAnalyzeExceptions:
    """Test exception handling in main analyze() method."""

    @pytest.mark.asyncio
    async def test_import_error_triggers_fallback(self, temp_project, caplog):
        """ImportError should log and use fallback analysis."""
        adapter = TechDebtAdapter(str(temp_project))

        with patch(
            "empathy_software_plugin.wizards.tech_debt_wizard.TechDebtWizard",
            side_effect=ImportError("Module not found"),
        ):
            with caplog.at_level(logging.INFO):
                result = await adapter.analyze()

        # Should use fallback mode
        assert result["metadata"].get("mode") == "fallback"
        # Should log info about fallback
        assert any("fallback analysis" in record.message.lower() for record in caplog.records)

    @pytest.mark.asyncio
    async def test_key_error_logs_and_returns_error(self, temp_project, caplog):
        """KeyError should log error and return error result."""
        adapter = TechDebtAdapter(str(temp_project))

        mock_wizard = AsyncMock()
        mock_wizard.analyze.side_effect = KeyError("Required key missing")

        with patch(
            "empathy_software_plugin.wizards.tech_debt_wizard.TechDebtWizard",
            return_value=mock_wizard,
        ):
            with caplog.at_level(logging.ERROR):
                result = await adapter.analyze()

        # Should return error result
        assert result["status"] == "error"
        # Should log data error
        assert any("data error" in record.message.lower() for record in caplog.records)

    @pytest.mark.asyncio
    async def test_value_error_logs_and_returns_error(self, temp_project, caplog):
        """ValueError should log error and return error result."""
        adapter = TechDebtAdapter(str(temp_project))

        mock_wizard = AsyncMock()
        mock_wizard.analyze.side_effect = ValueError("Invalid configuration")

        with patch(
            "empathy_software_plugin.wizards.tech_debt_wizard.TechDebtWizard",
            return_value=mock_wizard,
        ):
            with caplog.at_level(logging.ERROR):
                result = await adapter.analyze()

        # Should return error result
        assert result["status"] == "error"
        assert "validation error" in result["error_message"].lower()
        # Should log error
        assert any("data error" in record.message.lower() for record in caplog.records)

    @pytest.mark.asyncio
    async def test_type_error_logs_and_returns_error(self, temp_project, caplog):
        """TypeError should log error and return error result."""
        adapter = TechDebtAdapter(str(temp_project))

        mock_wizard = AsyncMock()
        mock_wizard.analyze.side_effect = TypeError("Invalid argument type")

        with patch(
            "empathy_software_plugin.wizards.tech_debt_wizard.TechDebtWizard",
            return_value=mock_wizard,
        ):
            with caplog.at_level(logging.ERROR):
                result = await adapter.analyze()

        # Should return error result
        assert result["status"] == "error"
        assert "validation error" in result["error_message"].lower()

    @pytest.mark.asyncio
    async def test_os_error_logs_and_returns_error(self, temp_project, caplog):
        """OSError should log error and return error result."""
        adapter = TechDebtAdapter(str(temp_project))

        mock_wizard = AsyncMock()
        mock_wizard.analyze.side_effect = OSError("Permission denied")

        with patch(
            "empathy_software_plugin.wizards.tech_debt_wizard.TechDebtWizard",
            return_value=mock_wizard,
        ):
            with caplog.at_level(logging.ERROR):
                result = await adapter.analyze()

        # Should return error result
        assert result["status"] == "error"
        assert "cannot access project files" in result["error_message"].lower()
        # Should log file system error
        assert any("file system error" in record.message.lower() for record in caplog.records)

    @pytest.mark.asyncio
    async def test_unexpected_error_logs_with_traceback(self, temp_project, caplog):
        """Unexpected errors should log with full exception traceback."""
        adapter = TechDebtAdapter(str(temp_project))

        mock_wizard = AsyncMock()
        mock_wizard.analyze.side_effect = RuntimeError("Unexpected wizard error")

        with patch(
            "empathy_software_plugin.wizards.tech_debt_wizard.TechDebtWizard",
            return_value=mock_wizard,
        ):
            with caplog.at_level(logging.ERROR):
                result = await adapter.analyze()

        # Should return error result
        assert result["status"] == "error"
        assert "tech debt analysis failed" in result["error_message"].lower()
        # Should log exception with traceback
        assert any("unexpected error" in record.message.lower() for record in caplog.records)


class TestFallbackAnalyzeExceptions:
    """Test exception handling in fallback analysis."""

    @pytest.mark.asyncio
    async def test_permission_error_logs_and_skips(self, tmp_path, caplog):
        """Permission errors should log warning and skip file."""
        # Create a file we'll mock to raise PermissionError
        (tmp_path / "test.py").write_text("# TODO: test")

        adapter = TechDebtAdapter(str(tmp_path))

        with patch.object(Path, "read_text", side_effect=PermissionError("Access denied")):
            with caplog.at_level(logging.WARNING):
                result = await adapter._fallback_analyze(0.0)

        # Should complete successfully (skipping problematic files)
        assert result["status"] in ("pass", "warn", "fail")
        # Should log warning
        assert any("cannot access" in record.message.lower() for record in caplog.records)

    @pytest.mark.asyncio
    async def test_unicode_error_logs_and_skips(self, tmp_path, caplog):
        """Unicode decode errors should log debug and skip file."""
        # Create a file we'll mock to raise UnicodeDecodeError
        (tmp_path / "test.py").write_text("# TODO: test")

        adapter = TechDebtAdapter(str(tmp_path))

        with patch.object(
            Path,
            "read_text",
            side_effect=UnicodeDecodeError("utf-8", b"\xff\xfe", 0, 1, "invalid"),
        ):
            with caplog.at_level(logging.DEBUG):
                result = await adapter._fallback_analyze(0.0)

        # Should complete successfully
        assert result["status"] in ("pass", "warn", "fail")
        # Should log debug message
        assert any("cannot decode" in record.message.lower() for record in caplog.records)

    @pytest.mark.asyncio
    async def test_os_error_logs_and_skips(self, tmp_path, caplog):
        """OSError during file read should log warning and skip."""
        (tmp_path / "test.py").write_text("# TODO: test")

        adapter = TechDebtAdapter(str(tmp_path))

        with patch.object(Path, "read_text", side_effect=OSError("Disk error")):
            with caplog.at_level(logging.WARNING):
                result = await adapter._fallback_analyze(0.0)

        # Should complete successfully
        assert result["status"] in ("pass", "warn", "fail")
        # Should log warning
        assert any("cannot access" in record.message.lower() for record in caplog.records)

    @pytest.mark.asyncio
    async def test_successful_fallback_analysis(self, temp_project):
        """Fallback analysis should successfully find tech debt markers."""
        adapter = TechDebtAdapter(str(temp_project))

        result = await adapter._fallback_analyze(0.0)

        # Should find the TODO and FIXME markers
        assert result["findings_count"] >= 2
        assert result["status"] in ("pass", "warn", "fail")
        assert result["metadata"]["mode"] == "fallback"

        # Check that findings include TODO and FIXME
        codes = [f["code"] for f in result["findings"]]
        assert "TODO" in codes
        assert "FIXME" in codes


class TestSuccessfulAnalysis:
    """Test that successful analysis works correctly."""

    @pytest.mark.asyncio
    async def test_successful_wizard_analysis(self, temp_project):
        """Successful wizard analysis should return proper results."""
        adapter = TechDebtAdapter(str(temp_project))

        mock_wizard = AsyncMock()
        mock_wizard.analyze.return_value = {
            "debt_items": [
                {
                    "file_path": "src/main.py",
                    "line_number": 1,
                    "debt_type": "TODO",
                    "severity": "low",
                    "content": "Refactor this function",
                    "context": "def main(): pass",
                }
            ],
            "health_score": 90,
            "trajectory": {"trend": "improving"},
            "hotspots": ["src/main.py"],
            "by_type": {"TODO": 1},
        }

        with patch(
            "empathy_software_plugin.wizards.tech_debt_wizard.TechDebtWizard",
            return_value=mock_wizard,
        ):
            result = await adapter.analyze()

        # Should return successful result
        assert result["status"] == "pass"
        assert result["score"] == 90
        assert result["findings_count"] == 1
        assert result["findings"][0]["code"] == "TODO"

    @pytest.mark.asyncio
    async def test_fallback_when_wizard_unavailable(self, temp_project, caplog):
        """Should gracefully fall back when wizard module unavailable."""
        adapter = TechDebtAdapter(str(temp_project))

        # The wizard import will fail, triggering fallback
        with patch(
            "empathy_software_plugin.wizards.tech_debt_wizard.TechDebtWizard",
            side_effect=ImportError("Module not found"),
        ):
            with caplog.at_level(logging.INFO):
                result = await adapter.analyze()

        # Should use fallback
        assert result["metadata"]["mode"] == "fallback"
        # Should still find tech debt
        assert result["findings_count"] >= 2  # TODO and FIXME in test files


class TestLoggingAndErrorPropagation:
    """Test that logging and error propagation work correctly."""

    @pytest.mark.asyncio
    async def test_errors_are_not_silently_swallowed(self, temp_project):
        """Errors should be logged and returned, not silently ignored."""
        adapter = TechDebtAdapter(str(temp_project))

        mock_wizard = AsyncMock()
        mock_wizard.analyze.side_effect = RuntimeError("Critical error")

        with patch(
            "empathy_software_plugin.wizards.tech_debt_wizard.TechDebtWizard",
            return_value=mock_wizard,
        ):
            result = await adapter.analyze()

        # Error should be reported in result
        assert result["status"] == "error"
        assert "critical error" in result["error_message"].lower()

    @pytest.mark.asyncio
    async def test_file_errors_logged_not_silent(self, tmp_path, caplog):
        """File access errors should be logged, not fail silently."""
        (tmp_path / "test.py").write_text("# TODO: test")

        adapter = TechDebtAdapter(str(tmp_path))

        with patch.object(Path, "read_text", side_effect=PermissionError("Denied")):
            with caplog.at_level(logging.WARNING):
                result = await adapter._fallback_analyze(0.0)

        # Should log the error
        warning_logs = [r for r in caplog.records if r.levelno >= logging.WARNING]
        assert len(warning_logs) > 0
        assert any("cannot access" in r.message.lower() for r in warning_logs)

    @pytest.mark.asyncio
    async def test_exception_context_preserved(self, temp_project, caplog):
        """Exception logging should preserve context for debugging."""
        adapter = TechDebtAdapter(str(temp_project))

        mock_wizard = AsyncMock()
        mock_wizard.analyze.side_effect = RuntimeError("Detailed error message")

        with patch(
            "empathy_software_plugin.wizards.tech_debt_wizard.TechDebtWizard",
            return_value=mock_wizard,
        ):
            with caplog.at_level(logging.ERROR):
                result = await adapter.analyze()

        # Error message should include details
        assert "detailed error message" in result["error_message"].lower()
        # Should have logged the error
        error_logs = [r for r in caplog.records if r.levelno >= logging.ERROR]
        assert len(error_logs) > 0


class TestScoreCalculation:
    """Test that scoring works correctly with exception handling."""

    @pytest.mark.asyncio
    async def test_score_calculation_with_various_severities(self, temp_project):
        """Score calculation should work correctly."""
        adapter = TechDebtAdapter(str(temp_project))

        findings_by_severity = {
            "critical": 0,
            "high": 2,  # 2 FIXMEs
            "medium": 0,
            "low": 1,  # 1 TODO
            "info": 0,
        }

        score = adapter._calculate_score(findings_by_severity)

        # Score should be calculated based on penalties
        # high: 2 * 8 = 16, low: 1 * 0.5 = 0.5, total penalty = 16.5
        # Score = 100 - 16.5 = 83.5 -> 83 (int)
        assert score == 83

    @pytest.mark.asyncio
    async def test_severity_mapping(self, temp_project):
        """Severity mapping should work correctly."""
        adapter = TechDebtAdapter(str(temp_project))

        assert adapter._map_severity("CRITICAL") == "critical"
        assert adapter._map_severity("high") == "high"
        assert adapter._map_severity("Medium") == "medium"
        assert adapter._map_severity("unknown") == "medium"  # Default

    @pytest.mark.asyncio
    async def test_debt_type_severity(self, temp_project):
        """Debt type to severity mapping should be correct."""
        adapter = TechDebtAdapter(str(temp_project))

        assert adapter._get_debt_severity("FIXME") == "high"
        assert adapter._get_debt_severity("HACK") == "high"
        assert adapter._get_debt_severity("XXX") == "medium"
        assert adapter._get_debt_severity("TODO") == "low"
        assert adapter._get_debt_severity("UNKNOWN") == "low"  # Default
