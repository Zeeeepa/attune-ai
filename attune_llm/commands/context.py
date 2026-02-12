"""attune_llm.commands.context - DEPRECATED. Use attune.commands.context instead.

This module re-exports from attune.commands.context for backward compatibility.
Will be removed in attune-ai v3.0.0.
"""

import warnings

warnings.warn(
    "attune_llm.commands.context is deprecated. Use attune.commands.context instead. "
    "This module will be removed in attune-ai v3.0.0.",
    DeprecationWarning,
    stacklevel=2,
)

from attune.commands.context import *  # noqa: F401,F403
