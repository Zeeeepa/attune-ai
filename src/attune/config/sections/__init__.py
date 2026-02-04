"""Configuration section dataclasses for Attune AI.

This package contains the individual configuration section dataclasses
that compose the UnifiedConfig.

Copyright 2026 Smart-AI-Memory
Licensed under Fair Source License 0.9
"""

from attune.config.sections.analysis import AnalysisConfig
from attune.config.sections.auth import AuthConfig
from attune.config.sections.environment import EnvironmentConfig
from attune.config.sections.persistence import PersistenceConfig
from attune.config.sections.routing import RoutingConfig
from attune.config.sections.telemetry import TelemetryConfig
from attune.config.sections.workflows import WorkflowConfig

__all__ = [
    "AuthConfig",
    "RoutingConfig",
    "WorkflowConfig",
    "AnalysisConfig",
    "PersistenceConfig",
    "TelemetryConfig",
    "EnvironmentConfig",
]
