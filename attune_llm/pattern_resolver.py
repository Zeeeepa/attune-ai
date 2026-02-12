"""attune_llm.pattern_resolver - DEPRECATED. Use attune.patterns.resolver instead.

This module re-exports from attune.patterns.resolver for backward compatibility.
Will be removed in attune-ai v3.0.0.
"""

import warnings

warnings.warn(
    "attune_llm.pattern_resolver is deprecated. Use attune.patterns.resolver instead. "
    "This module will be removed in attune-ai v3.0.0.",
    DeprecationWarning,
    stacklevel=2,
)

from attune.patterns.resolver import *  # noqa: F401,F403
