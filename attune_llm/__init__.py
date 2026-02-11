"""Empathy LLM Toolkit

Wraps LLM providers (OpenAI, Anthropic, local models) with Attune AI levels.

Enables progression from Level 1 (reactive) to Level 4 (anticipatory) AI collaboration
with any LLM backend.

Copyright 2025 Smart AI Memory, LLC
Licensed under the Apache License, Version 2.0
"""

from .core import EmpathyLLM
from .levels import EmpathyLevel
from .providers import AnthropicProvider, GeminiProvider, LocalProvider, OpenAIProvider
from .state import CollaborationState, UserPattern

__version__ = "1.9.5"

__all__ = [
    "AnthropicProvider",
    "CollaborationState",
    "EmpathyLLM",
    "EmpathyLevel",
    "GeminiProvider",
    "LocalProvider",
    "OpenAIProvider",
    "UserPattern",
]
