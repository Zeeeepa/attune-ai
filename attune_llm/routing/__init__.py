"""attune_llm.routing - DEPRECATED. Use attune.routing instead.

Smart routing of tasks to appropriate model tiers for cost optimization:
- CHEAP tier: Triage, summarization, classification (Haiku/GPT-4o-mini)
- CAPABLE tier: Code generation, analysis, sub-agent work (Sonnet/GPT-4o)
- PREMIUM tier: Coordination, synthesis, critical decisions (Opus/o1)

Example:
    >>> from attune.routing import ModelRouter
    >>>
    >>> router = ModelRouter()
    >>> model = router.route("summarize", provider="anthropic")
    >>> print(model)  # claude-haiku-4-5-20251001

This module re-exports from attune.routing.model_router for backward compatibility.
Will be removed in attune-ai v3.0.0.

Copyright 2025 Smart AI Memory, LLC
Licensed under the Apache License, Version 2.0

"""

import warnings

warnings.warn(
    "attune_llm.routing is deprecated. Use attune.routing instead. "
    "This module will be removed in attune-ai v3.0.0.",
    DeprecationWarning,
    stacklevel=2,
)

from attune.routing.model_router import ModelConfig, ModelRouter, ModelTier, TaskRouting

__all__ = [
    "ModelConfig",
    "ModelRouter",
    "ModelTier",
    "TaskRouting",
]
