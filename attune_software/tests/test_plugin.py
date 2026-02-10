"""Tests for attune_software plugin.

These tests verify the SoftwarePlugin works correctly with
workflow registration and graceful degradation.

Copyright 2026 Smart-AI-Memory
Licensed under Apache 2.0
"""

from __future__ import annotations

from unittest.mock import patch

from attune_software.plugin import _WORKFLOW_MAP, SoftwarePlugin


class TestSoftwarePluginMetadata:
    """Tests for SoftwarePlugin.get_metadata()."""

    def test_returns_metadata(self) -> None:
        plugin = SoftwarePlugin()
        meta = plugin.get_metadata()
        assert meta.name == "Attune Software Development"
        assert meta.version == "1.0.0"
        assert meta.domain == "software"

    def test_metadata_requires_core(self) -> None:
        plugin = SoftwarePlugin()
        meta = plugin.get_metadata()
        assert meta.requires_core_version == "2.4.0"


class TestSoftwarePluginWorkflows:
    """Tests for SoftwarePlugin.register_workflows()."""

    def test_returns_dict(self) -> None:
        plugin = SoftwarePlugin()
        workflows = plugin.register_workflows()
        assert isinstance(workflows, dict)

    def test_workflow_map_keys(self) -> None:
        expected = {
            "code-review",
            "bug-predict",
            "security-audit",
            "perf-audit",
            "test-gen",
            "refactor-plan",
            "dependency-check",
        }
        assert set(_WORKFLOW_MAP.keys()) == expected

    def test_graceful_degradation(self) -> None:
        """All imports failing should return empty dict."""
        plugin = SoftwarePlugin()
        with patch(
            "attune_software.plugin.importlib.import_module",
            side_effect=ImportError("mocked"),
        ):
            workflows = plugin.register_workflows()
            assert workflows == {}


class TestSoftwarePluginPatterns:
    """Tests for SoftwarePlugin.register_patterns()."""

    def test_has_software_domain(self) -> None:
        plugin = SoftwarePlugin()
        patterns = plugin.register_patterns()
        assert patterns["domain"] == "software"

    def test_has_testing_bottleneck(self) -> None:
        plugin = SoftwarePlugin()
        patterns = plugin.register_patterns()
        assert "testing_bottleneck" in patterns["patterns"]

    def test_has_security_drift(self) -> None:
        plugin = SoftwarePlugin()
        patterns = plugin.register_patterns()
        assert "security_drift" in patterns["patterns"]
