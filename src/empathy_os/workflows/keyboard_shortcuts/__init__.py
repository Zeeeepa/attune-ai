"""
Keyboard Shortcuts Workflow Package

Generates optimized keyboard shortcuts for any project following
the "Keyboard Conductor" musical scale pattern.

Features:
- Multi-source feature discovery (VSCode, Python, YAML, LLM)
- Multi-layout generation (QWERTY, Dvorak, Colemak)
- Ergonomic optimization with mnemonic phrases
- Multiple output formats (keybindings, aliases, documentation)
"""

from .generators import (
    CLIAliasGenerator,
    MarkdownDocGenerator,
    VSCodeKeybindingsGenerator,
)
from .parsers import (
    FeatureParser,
    LLMFeatureAnalyzer,
    PyProjectParser,
    VSCodeCommandParser,
    YAMLManifestParser,
)
from .schema import (
    Category,
    Feature,
    FeatureManifest,
    LayoutConfig,
    ShortcutAssignment,
)
from .workflow import KeyboardShortcutWorkflow

__all__ = [
    "KeyboardShortcutWorkflow",
    "FeatureParser",
    "VSCodeCommandParser",
    "PyProjectParser",
    "YAMLManifestParser",
    "LLMFeatureAnalyzer",
    "VSCodeKeybindingsGenerator",
    "CLIAliasGenerator",
    "MarkdownDocGenerator",
    "FeatureManifest",
    "Feature",
    "Category",
    "LayoutConfig",
    "ShortcutAssignment",
]
