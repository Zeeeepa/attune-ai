"""Tests for attune_software/plugin.py — SoftwarePlugin.

Covers get_metadata, register_workflows (with import failures), register_patterns.

Copyright 2026 Smart-AI-Memory
Licensed under Apache 2.0
"""

from __future__ import annotations

from unittest.mock import patch

from attune_software.plugin import _WORKFLOW_MAP, SoftwarePlugin


class TestSoftwarePluginMetadata:
    """Tests for SoftwarePlugin.get_metadata()."""

    def test_returns_plugin_metadata(self) -> None:
        plugin = SoftwarePlugin()
        meta = plugin.get_metadata()
        assert meta.name == "Attune Software Development"
        assert meta.version == "1.0.0"
        assert meta.domain == "software"

    def test_metadata_has_description(self) -> None:
        plugin = SoftwarePlugin()
        meta = plugin.get_metadata()
        assert "code review" in meta.description

    def test_metadata_has_author(self) -> None:
        plugin = SoftwarePlugin()
        meta = plugin.get_metadata()
        assert meta.author == "Smart AI Memory, LLC"

    def test_metadata_license(self) -> None:
        plugin = SoftwarePlugin()
        meta = plugin.get_metadata()
        assert meta.license == "Apache-2.0"

    def test_metadata_requires_core_version(self) -> None:
        plugin = SoftwarePlugin()
        meta = plugin.get_metadata()
        assert meta.requires_core_version == "2.4.0"


class TestSoftwarePluginWorkflows:
    """Tests for SoftwarePlugin.register_workflows()."""

    def test_returns_dict(self) -> None:
        plugin = SoftwarePlugin()
        workflows = plugin.register_workflows()
        assert isinstance(workflows, dict)

    def test_registers_expected_workflows(self) -> None:
        """Should register workflows that exist in attune.workflows."""
        plugin = SoftwarePlugin()
        workflows = plugin.register_workflows()
        # At least some workflows should be available in dev environment
        assert len(workflows) > 0

    def test_workflow_map_contains_expected_ids(self) -> None:
        """The workflow map should contain the expected workflow IDs."""
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

    def test_graceful_degradation_all_imports_fail(self) -> None:
        """If all workflow imports fail, should return empty dict."""
        plugin = SoftwarePlugin()
        # Patch importlib.import_module to fail for all workflow modules
        with patch(
            "attune_software.plugin.importlib.import_module",
            side_effect=ImportError("mocked"),
        ):
            workflows = plugin.register_workflows()
            assert isinstance(workflows, dict)
            assert len(workflows) == 0

    def test_graceful_degradation_partial_imports_fail(self) -> None:
        """If some workflow imports fail, others should still register."""
        plugin = SoftwarePlugin()
        original_import = __import__

        call_count = 0

        def failing_import(name, *args, **kwargs):
            nonlocal call_count
            call_count += 1
            # Fail on every other import
            if call_count % 2 == 0:
                raise ImportError(f"mocked failure for {name}")
            return original_import(name, *args, **kwargs)

        with patch(
            "attune_software.plugin.importlib.import_module",
            side_effect=failing_import,
        ):
            workflows = plugin.register_workflows()
            assert isinstance(workflows, dict)


class TestSoftwarePluginPatterns:
    """Tests for SoftwarePlugin.register_patterns()."""

    def test_returns_dict(self) -> None:
        plugin = SoftwarePlugin()
        patterns = plugin.register_patterns()
        assert isinstance(patterns, dict)

    def test_has_domain(self) -> None:
        plugin = SoftwarePlugin()
        patterns = plugin.register_patterns()
        assert patterns["domain"] == "software"

    def test_has_patterns_key(self) -> None:
        plugin = SoftwarePlugin()
        patterns = plugin.register_patterns()
        assert "patterns" in patterns

    def test_testing_bottleneck_pattern(self) -> None:
        plugin = SoftwarePlugin()
        patterns = plugin.register_patterns()
        assert "testing_bottleneck" in patterns["patterns"]
        tb = patterns["patterns"]["testing_bottleneck"]
        assert "description" in tb
        assert "indicators" in tb
        assert "threshold" in tb

    def test_security_drift_pattern(self) -> None:
        plugin = SoftwarePlugin()
        patterns = plugin.register_patterns()
        assert "security_drift" in patterns["patterns"]
        sd = patterns["patterns"]["security_drift"]
        assert "indicators" in sd
