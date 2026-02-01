"""Tool Adapters for Code Inspection Pipeline

Each adapter wraps an existing inspection tool and converts its output
to the unified ToolResult format for the pipeline.

Copyright 2025 Smart AI Memory, LLC
Licensed under Fair Source 0.9
"""

from .code_health_adapter import CodeHealthAdapter

__all__ = [
    "CodeHealthAdapter",
]
