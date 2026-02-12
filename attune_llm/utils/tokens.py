"""attune_llm.utils.tokens - DEPRECATED. Use attune.utils.tokens instead.

This module re-exports from attune.utils.tokens for backward compatibility.
Will be removed in attune-ai v3.0.0.
"""

import warnings

warnings.warn(
    "attune_llm.utils.tokens is deprecated. Use attune.utils.tokens instead. "
    "This module will be removed in attune-ai v3.0.0.",
    DeprecationWarning,
    stacklevel=2,
)

from attune.utils.tokens import *  # noqa: F401,F403
