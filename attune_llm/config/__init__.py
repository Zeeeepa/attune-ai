"""Attune AI Configuration Module - DEPRECATED.

Use attune.config.agent_config instead for agent configuration models.
This module re-exports from attune.config.agent_config for backward compatibility.
Will be removed in attune-ai v3.0.0.

Copyright 2025 Smart-AI-Memory
Licensed under the Apache License, Version 2.0
"""

import warnings

warnings.warn(
    "attune_llm.config is deprecated. Use attune.config.agent_config instead. "
    "This module will be removed in attune-ai v3.0.0.",
    DeprecationWarning,
    stacklevel=2,
)

from attune.config.agent_config import (  # noqa: E402
    AgentOperationError,
    BookProductionConfig,
    MemDocsConfig,
    ModelTier,
    Provider,
    RedisConfig,
    UnifiedAgentConfig,
    WorkflowMode,
)

__all__ = [
    "AgentOperationError",
    "BookProductionConfig",
    "MemDocsConfig",
    "ModelTier",
    "Provider",
    "RedisConfig",
    "UnifiedAgentConfig",
    "WorkflowMode",
]
