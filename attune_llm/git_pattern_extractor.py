"""attune_llm.git_pattern_extractor - DEPRECATED. Use attune.patterns.git_extractor instead.

This module re-exports from attune.patterns.git_extractor for backward compatibility.
Will be removed in attune-ai v3.0.0.
"""

import warnings

warnings.warn(
    "attune_llm.git_pattern_extractor is deprecated. Use attune.patterns.git_extractor instead. "
    "This module will be removed in attune-ai v3.0.0.",
    DeprecationWarning,
    stacklevel=2,
)

from attune.patterns.git_extractor import *  # noqa: F401,F403
