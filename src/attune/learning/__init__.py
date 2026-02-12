"""Continuous Learning Module for Attune AI

Automatic pattern extraction from sessions to enable learning and improvement.
Identifies valuable patterns from user interactions for future application.

Architectural patterns inspired by everything-claude-code by Affaan Mustafa.
See: https://github.com/affaan-m/everything-claude-code (MIT License)
See: ACKNOWLEDGMENTS.md for full attribution.

Copyright 2025 Smart AI Memory, LLC
Licensed under the Apache License, Version 2.0
"""

from attune.learning.evaluator import SessionEvaluator, SessionQuality
from attune.learning.extractor import (
    ExtractedPattern,
    PatternCategory,
    PatternExtractor,
)
from attune.learning.storage import LearnedSkill, LearnedSkillsStorage

__all__ = [
    "ExtractedPattern",
    "LearnedSkill",
    "LearnedSkillsStorage",
    "PatternCategory",
    "PatternExtractor",
    "SessionEvaluator",
    "SessionQuality",
]
