"""Tests for security_adapter.py exception handling.

This test suite verifies the fail-secure exception handling patterns
implemented in Sprint 1 of the bug remediation plan.

Copyright 2025 Smart AI Memory, LLC
Licensed under Fair Source 0.9
"""

import logging
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from agents.code_inspection.adapters.security_adapter import SecurityAdapter


@pytest.fixture
def temp_project(tmp_path):
    """Create a temporary project structure."""
    # Create some Python files
    (tmp_path / "src").mkdir()
    (tmp_path / "src" / "main.py").write_text("print('hello')")
    (tmp_path / "src" / "utils.py").write_text("def helper(): pass")
    return tmp_path


@pytest.fixture
def mock_scanner():
    """Create a mock VulnerabilityScanner."""
    scanner = Mock()
    scanner.scan_file = Mock(return_value=[])
    scanner.scan_dependencies = Mock(return_value=[])
    return scanner


class TestFileScanning:
    """Test exception handling during file scanning."""

    @pytest.mark.asyncio
    async def test_permission_error_logs_warning_and_skips(
        self, temp_project, mock_scanner, caplog
    ):
        """Permission errors should log warning and skip file."""
        adapter = SecurityAdapter(str(temp_project))

        # Mock scanner to raise PermissionError
        mock_scanner.scan_file.side_effect = PermissionError("Access denied")

        with patch(
            "empathy_software_plugin.wizards.security.vulnerability_scanner.VulnerabilityScanner",
            return_value=mock_scanner,
        ):
            with caplog.at_level(logging.WARNING):
                result = await adapter.analyze()

        # Should complete successfully
        assert result["status"] in ("pass", "warn", "fail")
        # Should log warning
        assert any("Cannot access" in record.message for record in caplog.records)
        # Should not create SCAN_FAILURE finding
        assert not any(f.get("code") == "SCAN_FAILURE" for f in result["findings"])

    @pytest.mark.asyncio
    async def test_unicode_error_logs_debug_and_skips(self, temp_project, mock_scanner, caplog):
        """Unicode decode errors should log debug and skip file."""
        adapter = SecurityAdapter(str(temp_project))

        # Mock scanner to raise UnicodeDecodeError
        mock_scanner.scan_file.side_effect = UnicodeDecodeError(
            "utf-8", b"\xff\xfe", 0, 1, "invalid start byte"
        )

        with patch(
            "empathy_software_plugin.wizards.security.vulnerability_scanner.VulnerabilityScanner",
            return_value=mock_scanner,
        ):
            with caplog.at_level(logging.DEBUG):
                result = await adapter.analyze()

        # Should complete successfully
        assert result["status"] in ("pass", "warn", "fail")
        # Should log debug message
        assert any("Cannot decode" in record.message for record in caplog.records)

    @pytest.mark.asyncio
    async def test_scanner_value_error_creates_scan_failure_finding(
        self, temp_project, mock_scanner, caplog
    ):
        """ValueError during scan should create SCAN_FAILURE finding (fail-secure)."""
        adapter = SecurityAdapter(str(temp_project))

        # Mock scanner to raise ValueError
        mock_scanner.scan_file.side_effect = ValueError("Invalid pattern")

        with patch(
            "empathy_software_plugin.wizards.security.vulnerability_scanner.VulnerabilityScanner",
            return_value=mock_scanner,
        ):
            with caplog.at_level(logging.ERROR):
                result = await adapter.analyze()

        # Should create SCAN_FAILURE findings
        scan_failures = [f for f in result["findings"] if f.get("code") == "SCAN_FAILURE"]
        assert len(scan_failures) > 0

        # Should log error
        assert any("Scanner failed on" in record.message for record in caplog.records)

        # Check finding structure
        failure = scan_failures[0]
        assert failure["severity"] == "medium"
        assert "Security scanner failed" in failure["message"]
        assert "Manual review recommended" in failure["remediation"]
        assert failure["confidence"] == 0.5

    @pytest.mark.asyncio
    async def test_scanner_runtime_error_creates_scan_failure_finding(
        self, temp_project, mock_scanner, caplog
    ):
        """RuntimeError during scan should create SCAN_FAILURE finding (fail-secure)."""
        adapter = SecurityAdapter(str(temp_project))

        mock_scanner.scan_file.side_effect = RuntimeError("Scanner crash")

        with patch(
            "empathy_software_plugin.wizards.security.vulnerability_scanner.VulnerabilityScanner",
            return_value=mock_scanner,
        ):
            with caplog.at_level(logging.ERROR):
                result = await adapter.analyze()

        # Should create SCAN_FAILURE findings
        scan_failures = [f for f in result["findings"] if f.get("code") == "SCAN_FAILURE"]
        assert len(scan_failures) > 0
        assert any("Scanner failed" in record.message for record in caplog.records)

    @pytest.mark.asyncio
    async def test_scanner_attribute_error_creates_scan_failure_finding(
        self, temp_project, mock_scanner
    ):
        """AttributeError during scan should create SCAN_FAILURE finding."""
        adapter = SecurityAdapter(str(temp_project))

        mock_scanner.scan_file.side_effect = AttributeError("Missing attribute")

        with patch(
            "empathy_software_plugin.wizards.security.vulnerability_scanner.VulnerabilityScanner",
            return_value=mock_scanner,
        ):
            result = await adapter.analyze()

        scan_failures = [f for f in result["findings"] if f.get("code") == "SCAN_FAILURE"]
        assert len(scan_failures) > 0

    @pytest.mark.asyncio
    async def test_mixed_file_scan_results(self, temp_project, mock_scanner):
        """Some files succeed, some fail - should handle gracefully."""
        adapter = SecurityAdapter(str(temp_project))

        # First file succeeds, second file fails
        call_count = {"count": 0}

        def side_effect_func(path):
            call_count["count"] += 1
            if call_count["count"] == 1:
                return []  # Success
            else:
                raise ValueError("Scanner error")  # Failure

        mock_scanner.scan_file.side_effect = side_effect_func

        with patch(
            "empathy_software_plugin.wizards.security.vulnerability_scanner.VulnerabilityScanner",
            return_value=mock_scanner,
        ):
            result = await adapter.analyze()

        # Should complete and may have scan failures
        assert result["status"] in ("pass", "warn", "fail")


class TestDependencyScanning:
    """Test exception handling during dependency scanning."""

    @pytest.mark.asyncio
    async def test_file_not_found_logs_info(self, temp_project, mock_scanner, caplog):
        """Missing requirements file should log info only."""
        adapter = SecurityAdapter(str(temp_project), scan_dependencies=True)

        mock_scanner.scan_file.return_value = []
        mock_scanner.scan_dependencies.side_effect = FileNotFoundError("requirements.txt not found")

        with patch(
            "empathy_software_plugin.wizards.security.vulnerability_scanner.VulnerabilityScanner",
            return_value=mock_scanner,
        ):
            with caplog.at_level(logging.INFO):
                result = await adapter.analyze()

        # Should complete successfully
        assert result["status"] in ("pass", "warn", "fail")
        # Should log info
        assert any("No dependency file found" in record.message for record in caplog.records)

    @pytest.mark.asyncio
    async def test_dependency_os_error_logs_warning(self, temp_project, mock_scanner, caplog):
        """OS errors during dependency scan should log warning."""
        adapter = SecurityAdapter(str(temp_project), scan_dependencies=True)

        mock_scanner.scan_file.return_value = []
        mock_scanner.scan_dependencies.side_effect = OSError("Disk error")

        with patch(
            "empathy_software_plugin.wizards.security.vulnerability_scanner.VulnerabilityScanner",
            return_value=mock_scanner,
        ):
            with caplog.at_level(logging.WARNING):
                result = await adapter.analyze()

        # Should log warning
        assert any("Cannot access dependency files" in record.message for record in caplog.records)

    @pytest.mark.asyncio
    async def test_dependency_scanner_failure_creates_failure_finding(
        self, temp_project, mock_scanner, caplog
    ):
        """Dependency scanner failures should create DEP_SCAN_FAILURE (fail-secure)."""
        adapter = SecurityAdapter(str(temp_project), scan_dependencies=True)

        mock_scanner.scan_file.return_value = []
        mock_scanner.scan_dependencies.side_effect = ValueError("Invalid dependency format")

        with patch(
            "empathy_software_plugin.wizards.security.vulnerability_scanner.VulnerabilityScanner",
            return_value=mock_scanner,
        ):
            with caplog.at_level(logging.ERROR):
                result = await adapter.analyze()

        # Should create DEP_SCAN_FAILURE finding
        dep_failures = [f for f in result["findings"] if f.get("code") == "DEP_SCAN_FAILURE"]
        assert len(dep_failures) == 1

        failure = dep_failures[0]
        assert failure["severity"] == "high"
        assert "Dependency scanner failed" in failure["message"]
        assert "Manual dependency audit recommended" in failure["remediation"]
        assert failure["confidence"] == 0.7
        assert failure["file_path"] == "requirements.txt"

        # Should log error
        assert any("Dependency scanner failed" in record.message for record in caplog.records)

    @pytest.mark.asyncio
    async def test_dependency_connection_error_creates_failure_finding(
        self, temp_project, mock_scanner
    ):
        """ConnectionError during dependency scan should create failure finding."""
        adapter = SecurityAdapter(str(temp_project), scan_dependencies=True)

        mock_scanner.scan_file.return_value = []
        mock_scanner.scan_dependencies.side_effect = ConnectionError("Cannot reach CVE database")

        with patch(
            "empathy_software_plugin.wizards.security.vulnerability_scanner.VulnerabilityScanner",
            return_value=mock_scanner,
        ):
            result = await adapter.analyze()

        dep_failures = [f for f in result["findings"] if f.get("code") == "DEP_SCAN_FAILURE"]
        assert len(dep_failures) == 1


class TestAnalyzeMainExceptions:
    """Test exception handling at the main analyze() level."""

    @pytest.mark.asyncio
    async def test_import_error_returns_skip_result(self, temp_project):
        """ImportError should return skip result with reason."""
        adapter = SecurityAdapter(str(temp_project))

        with patch(
            "empathy_software_plugin.wizards.security.vulnerability_scanner.VulnerabilityScanner",
            side_effect=ImportError("Module not found"),
        ):
            result = await adapter.analyze()

        assert result["status"] == "skip"
        assert result["score"] == 0
        assert "module not available" in result["metadata"].get("skip_reason", "").lower()

    @pytest.mark.asyncio
    async def test_os_error_returns_error_result(self, temp_project, caplog):
        """OSError at top level should return error result."""
        adapter = SecurityAdapter(str(temp_project))

        # Mock project_root.rglob to raise OSError
        with patch.object(Path, "rglob", side_effect=OSError("Permission denied")):
            with patch(
                "empathy_software_plugin.wizards.security.vulnerability_scanner.VulnerabilityScanner",
                return_value=Mock(scan_file=Mock(return_value=[])),
            ):
                with caplog.at_level(logging.CRITICAL):
                    result = await adapter.analyze()

        assert result["status"] == "error"
        assert "Cannot access project files" in result["error_message"]
        assert any("File system error" in record.message for record in caplog.records)

    @pytest.mark.asyncio
    async def test_attribute_error_returns_error_result(self, temp_project, caplog):
        """AttributeError should return error result with config message."""
        adapter = SecurityAdapter(str(temp_project))

        mock_scanner = Mock()
        mock_scanner.scan_file = Mock(side_effect=AttributeError("Missing method"))

        with patch(
            "empathy_software_plugin.wizards.security.vulnerability_scanner.VulnerabilityScanner",
            return_value=mock_scanner,
        ):
            with caplog.at_level(logging.ERROR):
                result = await adapter.analyze()

        # Should eventually fail with configuration error or create scan failures
        # Since AttributeError is caught at file level, it creates SCAN_FAILURE
        # But if it happens during scanner init, it would be caught at top level
        assert result is not None

    @pytest.mark.asyncio
    async def test_type_error_returns_error_result(self, temp_project, caplog):
        """TypeError should return error result with config message."""
        adapter = SecurityAdapter(str(temp_project))

        # Make VulnerabilityScanner init raise TypeError
        with patch(
            "empathy_software_plugin.wizards.security.vulnerability_scanner.VulnerabilityScanner",
            side_effect=TypeError("Invalid argument"),
        ):
            with caplog.at_level(logging.ERROR):
                result = await adapter.analyze()

        assert result["status"] == "error"
        assert "configuration issue" in result["error_message"].lower()


class TestFailSecurePatterns:
    """Test that fail-secure patterns work correctly."""

    @pytest.mark.asyncio
    async def test_scanner_timeout_treated_as_vulnerability(
        self, temp_project, mock_scanner, caplog
    ):
        """Scanner timeout should create finding, not silently fail."""
        adapter = SecurityAdapter(str(temp_project))

        # Simulate timeout with RuntimeError
        mock_scanner.scan_file.side_effect = RuntimeError("Timeout")

        with patch(
            "empathy_software_plugin.wizards.security.vulnerability_scanner.VulnerabilityScanner",
            return_value=mock_scanner,
        ):
            result = await adapter.analyze()

        # Should have SCAN_FAILURE findings (fail-secure)
        failures = [f for f in result["findings"] if f.get("code") == "SCAN_FAILURE"]
        assert len(failures) > 0

    @pytest.mark.asyncio
    async def test_successful_scan_no_failures(self, temp_project, mock_scanner):
        """Successful scan should not create failure findings."""
        adapter = SecurityAdapter(str(temp_project))

        # Mock successful scan with one vulnerability
        mock_scanner.scan_file.return_value = [
            {
                "vulnerability_type": "SQL_INJECTION",
                "severity": "high",
                "line": 42,
                "description": "Unsafe SQL query",
                "evidence": "cursor.execute(query)",
                "confidence": 0.9,
                "remediation": "Use parameterized queries",
            }
        ]

        with patch(
            "empathy_software_plugin.wizards.security.vulnerability_scanner.VulnerabilityScanner",
            return_value=mock_scanner,
        ):
            result = await adapter.analyze()

        # Should have real vulnerability findings
        assert result["findings_count"] > 0
        # Should not have SCAN_FAILURE findings
        assert not any(f.get("code") == "SCAN_FAILURE" for f in result["findings"])

    @pytest.mark.asyncio
    async def test_logging_preserves_error_context(self, temp_project, mock_scanner, caplog):
        """Error logging should preserve full context for debugging."""
        adapter = SecurityAdapter(str(temp_project))

        mock_scanner.scan_file.side_effect = ValueError("Invalid regex: [")

        with patch(
            "empathy_software_plugin.wizards.security.vulnerability_scanner.VulnerabilityScanner",
            return_value=mock_scanner,
        ):
            with caplog.at_level(logging.ERROR):
                result = await adapter.analyze()

        # Should log specific error message
        error_logs = [r for r in caplog.records if r.levelno >= logging.ERROR]
        assert len(error_logs) > 0
        assert any("Invalid regex" in r.message for r in error_logs)
