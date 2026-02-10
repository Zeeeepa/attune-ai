"""Attune Software Development Plugin.

Provides software development workflows (code review, bug prediction,
security audit, etc.) through the Attune AI plugin registry.

Copyright 2025 Smart AI Memory, LLC
Licensed under Apache-2.0
"""

from .plugin import SoftwarePlugin

__version__ = "1.0.0"
__all__ = ["SoftwarePlugin"]
