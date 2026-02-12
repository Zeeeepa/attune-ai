"""attune_llm.contextual_patterns - DEPRECATED. Use attune.patterns.contextual instead.

This module re-exports from attune.patterns.contextual for backward compatibility.
Will be removed in attune-ai v3.0.0.
"""

import warnings

warnings.warn(
    "attune_llm.contextual_patterns is deprecated. Use attune.patterns.contextual instead. "
    "This module will be removed in attune-ai v3.0.0.",
    DeprecationWarning,
    stacklevel=2,
)

from attune.patterns.contextual import *  # noqa: F401,F403
