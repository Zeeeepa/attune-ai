"""Healthcare Plugin for Attune AI Framework.

Registers the Clinical Protocol Monitoring system as a plugin
that can be auto-discovered via entry points.

Works standalone (zero core deps) or integrated with attune-ai core.

Copyright 2025 Smart AI Memory, LLC
Licensed under Fair Source 0.9
"""

import logging
from dataclasses import dataclass
from typing import Any

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Conditional import: use attune core if available, otherwise define stubs
# so the package works standalone without attune-ai installed.
# ---------------------------------------------------------------------------
try:
    from attune.plugins import BasePlugin, BaseWorkflow, PluginMetadata
except ImportError:

    @dataclass
    class PluginMetadata:  # type: ignore[no-redef]
        """Minimal stub when attune-ai core is not installed."""

        name: str
        version: str
        domain: str
        description: str
        author: str
        license: str
        requires_core_version: str
        dependencies: list[str] | None = None

    class BaseWorkflow:  # type: ignore[no-redef]
        """Minimal stub when attune-ai core is not installed."""

        def __init__(self, name: str = "", domain: str = "", empathy_level: int = 1, **kwargs: Any):
            self.name = name
            self.domain = domain
            self.empathy_level = empathy_level

        async def analyze(self, context: dict[str, Any]) -> dict[str, Any]:
            raise NotImplementedError

        def get_required_context(self) -> list[str]:
            raise NotImplementedError

    class BasePlugin:  # type: ignore[no-redef]
        """Minimal stub when attune-ai core is not installed."""

        def __init__(self) -> None:
            self._workflows: dict[str, type] = {}
            self._initialized = False

        def get_metadata(self) -> "PluginMetadata":
            raise NotImplementedError

        def register_workflows(self) -> dict[str, type]:
            raise NotImplementedError

        def register_patterns(self) -> dict[str, Any]:
            return {}

        def initialize(self) -> None:
            if self._initialized:
                return
            self._workflows = self.register_workflows()
            self._initialized = True

        def list_workflows(self) -> list[str]:
            if not self._initialized:
                self.initialize()
            return list(self._workflows.keys())

        def get_workflow(self, workflow_id: str) -> type | None:
            if not self._initialized:
                self.initialize()
            return self._workflows.get(workflow_id)


# ---------------------------------------------------------------------------
# Workflow adapter: wraps ClinicalProtocolMonitor in BaseWorkflow interface
# ---------------------------------------------------------------------------


class ClinicalMonitorWorkflow(BaseWorkflow):
    """Adapter that wraps ClinicalProtocolMonitor as a BaseWorkflow.

    This allows the monitor to be discovered and used through the
    plugin registry's standard workflow interface.
    """

    def __init__(self, **kwargs: Any):
        super().__init__(
            name="clinical-protocol-monitor",
            domain="healthcare",
            empathy_level=4,
            **kwargs,
        )
        self._monitor = None

    def _get_monitor(self) -> Any:
        """Lazy-init the monitor to avoid import cost at registration time."""
        if self._monitor is None:
            from attune_healthcare.monitors.clinical_protocol_monitor import (
                ClinicalProtocolMonitor,
            )

            self._monitor = ClinicalProtocolMonitor()
        return self._monitor

    async def analyze(self, context: dict[str, Any]) -> dict[str, Any]:
        """Delegate to ClinicalProtocolMonitor.analyze()."""
        return await self._get_monitor().analyze(context)

    def get_required_context(self) -> list[str]:
        """Declare required context fields."""
        return ["patient_id", "sensor_data"]


# ---------------------------------------------------------------------------
# Plugin registration
# ---------------------------------------------------------------------------


class HealthcarePlugin(BasePlugin):
    """Healthcare Domain Plugin.

    Provides clinical protocol monitoring workflows for patient safety.
    Operates at Level 4 (Anticipatory Empathy) -- predicts patient
    deterioration before critical thresholds are reached.
    """

    def get_metadata(self) -> PluginMetadata:
        """Return plugin metadata."""
        return PluginMetadata(
            name="Attune Healthcare",
            version="1.0.0",
            domain="healthcare",
            description=(
                "Clinical protocol monitoring with Level 4 anticipatory analysis. "
                "Monitors vitals against clinical protocols (sepsis, cardiac, respiratory) "
                "and predicts patient deterioration before critical thresholds."
            ),
            author="Smart AI Memory, LLC",
            license="Apache-2.0",
            requires_core_version="2.4.0",
            dependencies=[],
        )

    def register_workflows(self) -> dict[str, type[BaseWorkflow]]:
        """Register healthcare workflows."""
        return {
            "clinical-monitor": ClinicalMonitorWorkflow,
        }

    def register_patterns(self) -> dict[str, Any]:
        """Register healthcare-specific patterns."""
        return {
            "domain": "healthcare",
            "patterns": {
                "protocol_compliance_drift": {
                    "description": (
                        "Protocol compliance decreases over time without active monitoring. "
                        "Alert when compliance rate drops below 90%."
                    ),
                    "indicators": [
                        "compliance_rate",
                        "intervention_timeliness",
                        "documentation_completeness",
                    ],
                },
                "early_deterioration": {
                    "description": (
                        "Vital sign trends indicate potential deterioration before "
                        "clinical criteria are met. Level 4 anticipatory detection."
                    ),
                    "indicators": [
                        "vital_trend_direction",
                        "trajectory_state",
                        "time_to_critical",
                    ],
                },
            },
        }
