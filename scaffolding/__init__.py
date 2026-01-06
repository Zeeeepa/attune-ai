"""Methodology Scaffolding for Wizard Factory.

Provides CLI tools and methodologies for creating new wizards quickly
using proven patterns.

Methodologies:
- Pattern-Compose: Select patterns, compose wizard (Recommended)
- TDD-First: Write tests first, implement wizard
- Prototype-Refine: Quick prototype, then refactor
- Risk-Driven: Focus on high-risk paths first
- Empathy-Centered: Design for user experience

Usage:
    # Create wizard using Pattern-Compose (recommended)
    python -m scaffolding create my_wizard --domain healthcare

    # Create with specific methodology
    python -m scaffolding create my_wizard --methodology tdd

    # Interactive mode
    python -m scaffolding create my_wizard --interactive

Copyright 2025 Smart AI Memory, LLC
Licensed under Fair Source 0.9
"""

from .methodologies.pattern_compose import PatternCompose
from .methodologies.tdd_first import TDDFirst

__all__ = [
    "PatternCompose",
    "TDDFirst",
]

__version__ = "1.0.0"
