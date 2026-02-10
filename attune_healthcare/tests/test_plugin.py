"""Tests for attune_healthcare plugin.

These tests run standalone (no attune-ai core required) and verify
the HealthcarePlugin works with the conditional import stubs.

Copyright 2026 Smart-AI-Memory
Licensed under Apache 2.0
"""

from __future__ import annotations

from attune_healthcare.plugin import ClinicalMonitorWorkflow, HealthcarePlugin


class TestHealthcarePluginMetadata:
    """Tests for HealthcarePlugin.get_metadata()."""

    def test_returns_metadata(self) -> None:
        plugin = HealthcarePlugin()
        meta = plugin.get_metadata()
        assert meta.name == "Attune Healthcare"
        assert meta.version == "1.0.0"
        assert meta.domain == "healthcare"

    def test_metadata_has_description(self) -> None:
        plugin = HealthcarePlugin()
        meta = plugin.get_metadata()
        assert "clinical protocol" in meta.description.lower()

    def test_metadata_author(self) -> None:
        plugin = HealthcarePlugin()
        meta = plugin.get_metadata()
        assert meta.author == "Smart AI Memory, LLC"

    def test_metadata_license(self) -> None:
        plugin = HealthcarePlugin()
        meta = plugin.get_metadata()
        assert meta.license == "Apache-2.0"

    def test_metadata_no_dependencies(self) -> None:
        plugin = HealthcarePlugin()
        meta = plugin.get_metadata()
        assert meta.dependencies == []


class TestHealthcarePluginWorkflows:
    """Tests for HealthcarePlugin.register_workflows()."""

    def test_returns_dict(self) -> None:
        plugin = HealthcarePlugin()
        workflows = plugin.register_workflows()
        assert isinstance(workflows, dict)

    def test_registers_clinical_monitor(self) -> None:
        plugin = HealthcarePlugin()
        workflows = plugin.register_workflows()
        assert "clinical-monitor" in workflows
        assert workflows["clinical-monitor"] is ClinicalMonitorWorkflow


class TestClinicalMonitorWorkflow:
    """Tests for ClinicalMonitorWorkflow adapter."""

    def test_workflow_properties(self) -> None:
        wf = ClinicalMonitorWorkflow()
        assert wf.name == "clinical-protocol-monitor"
        assert wf.domain == "healthcare"
        assert wf.empathy_level == 4

    def test_required_context(self) -> None:
        wf = ClinicalMonitorWorkflow()
        required = wf.get_required_context()
        assert "patient_id" in required
        assert "sensor_data" in required

    def test_lazy_monitor_init(self) -> None:
        """Monitor should not be initialized until first use."""
        wf = ClinicalMonitorWorkflow()
        assert wf._monitor is None


class TestHealthcarePluginPatterns:
    """Tests for HealthcarePlugin.register_patterns()."""

    def test_returns_dict(self) -> None:
        plugin = HealthcarePlugin()
        patterns = plugin.register_patterns()
        assert isinstance(patterns, dict)

    def test_has_domain(self) -> None:
        plugin = HealthcarePlugin()
        patterns = plugin.register_patterns()
        assert patterns["domain"] == "healthcare"

    def test_has_early_deterioration_pattern(self) -> None:
        plugin = HealthcarePlugin()
        patterns = plugin.register_patterns()
        assert "early_deterioration" in patterns["patterns"]

    def test_has_protocol_compliance_drift_pattern(self) -> None:
        plugin = HealthcarePlugin()
        patterns = plugin.register_patterns()
        assert "protocol_compliance_drift" in patterns["patterns"]


class TestHealthcarePluginAutoDiscovery:
    """Tests for plugin auto-discovery integration."""

    def test_plugin_initialize(self) -> None:
        """Plugin should initialize and list workflows."""
        plugin = HealthcarePlugin()
        plugin.initialize()
        workflows = plugin.list_workflows()
        assert "clinical-monitor" in workflows

    def test_plugin_get_workflow(self) -> None:
        """Plugin should return workflow class by ID."""
        plugin = HealthcarePlugin()
        plugin.initialize()
        wf_class = plugin.get_workflow("clinical-monitor")
        assert wf_class is ClinicalMonitorWorkflow

    def test_plugin_get_nonexistent_workflow(self) -> None:
        """Plugin should return None for unknown workflow ID."""
        plugin = HealthcarePlugin()
        plugin.initialize()
        assert plugin.get_workflow("nonexistent") is None
