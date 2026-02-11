"""Short-term memory module - Refactored modular structure.

This package provides Redis-backed short-term memory for the Attune framework.
The RedisShortTermMemory class is a facade that composes functionality from
specialized submodules.

Submodules:
    base: Core CRUD operations and connection management
    caching: Local LRU cache layer
    security: PII scrubbing and secrets detection
    working: Working memory (stash/retrieve)
    patterns: Pattern staging workflow
    conflicts: Conflict negotiation
    sessions: Collaboration session management
    batch: Batch operations for efficiency
    pagination: SCAN-based key pagination
    pubsub: Pub/Sub messaging
    streams: Redis Streams operations
    timelines: Time-window queries (sorted sets)
    queues: Task queue operations (lists)
    transactions: Atomic operations
    cross_session: Cross-session coordination

Backward Compatibility:
    All original imports continue to work:
    >>> from attune.memory.short_term import RedisShortTermMemory
    >>> from attune.memory.short_term import RedisConfig, StagedPattern

Copyright 2025 Smart-AI-Memory
Licensed under the Apache License, Version 2.0
"""

# Phase 8 Complete: Import from facade module
# The facade composes all 15 specialized submodules into a single class
# that maintains full backward compatibility with the original API.

# Import the main class from the facade module
from attune.memory.short_term.facade import (
    REDIS_AVAILABLE,
    RedisShortTermMemory,
    logger,
)

# Re-export redis module for test patching compatibility
try:
    import redis
except ImportError:
    redis = None  # type: ignore

# Import all public types from the types module (used by the implementation)
from attune.memory.types import (
    AccessTier,
    AgentCredentials,
    ConflictContext,
    PaginatedResult,
    RedisConfig,
    RedisMetrics,
    SecurityError,
    StagedPattern,
    TimeWindowQuery,
    TTLStrategy,
)

__all__ = [
    # Main class
    "RedisShortTermMemory",
    # Constants
    "REDIS_AVAILABLE",
    # Configuration
    "RedisConfig",
    "RedisMetrics",
    # Dataclasses
    "StagedPattern",
    "ConflictContext",
    "AgentCredentials",
    # Enums
    "AccessTier",
    "TTLStrategy",
    # Query types
    "TimeWindowQuery",
    "PaginatedResult",
    # Errors
    "SecurityError",
]
