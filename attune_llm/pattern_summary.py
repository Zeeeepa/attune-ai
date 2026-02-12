"""attune_llm.pattern_summary - DEPRECATED. Use attune.patterns.summary instead.

This module re-exports from attune.patterns.summary for backward compatibility.
Will be removed in attune-ai v3.0.0.
"""

import warnings

warnings.warn(
    "attune_llm.pattern_summary is deprecated. Use attune.patterns.summary instead. "
    "This module will be removed in attune-ai v3.0.0.",
    DeprecationWarning,
    stacklevel=2,
)

from attune.patterns.summary import *  # noqa: F401,F403
