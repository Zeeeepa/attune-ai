"""Attune AI Routing Module

Intelligent request routing to workflows using LLM classification.

Usage:
    from attune.routing import SmartRouter, quick_route

    # Full router
    router = SmartRouter()
    decision = await router.route("Fix security issue in auth.py")
    print(f"Use: {decision.primary_workflow}")

    # Quick helper
    decision = await quick_route("Optimize database queries")

Copyright 2025 Smart AI Memory, LLC
Licensed under the Apache License, Version 2.0
"""

from .chain_executor import ChainConfig, ChainExecution, ChainExecutor, ChainStep, ChainTrigger
from .classifier import ClassificationResult, HaikuClassifier
from .model_router import ModelConfig, ModelRouter, ModelTier, TaskRouting
from .smart_router import RoutingDecision, SmartRouter, quick_route
from .workflow_registry import WORKFLOW_REGISTRY, WorkflowInfo, WorkflowRegistry

__all__ = [
    "WORKFLOW_REGISTRY",
    "ChainConfig",
    "ChainExecution",
    # Chain Executor
    "ChainExecutor",
    "ChainStep",
    "ChainTrigger",
    "ClassificationResult",
    # Classifier
    "HaikuClassifier",
    # Model Router
    "ModelConfig",
    "ModelRouter",
    "ModelTier",
    "RoutingDecision",
    # Smart Router
    "SmartRouter",
    "TaskRouting",
    "WorkflowInfo",
    # Workflow Registry
    "WorkflowRegistry",
    "quick_route",
]
