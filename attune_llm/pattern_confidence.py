"""attune_llm.pattern_confidence - DEPRECATED. Use attune.patterns.confidence instead.

This module re-exports from attune.patterns.confidence for backward compatibility.
Will be removed in attune-ai v3.0.0.
"""

import warnings

warnings.warn(
    "attune_llm.pattern_confidence is deprecated. Use attune.patterns.confidence instead. "
    "This module will be removed in attune-ai v3.0.0.",
    DeprecationWarning,
    stacklevel=2,
)

from attune.patterns.confidence import *  # noqa: F401,F403
