"""attune_llm.commands.loader - DEPRECATED. Use attune.commands.loader instead.

This module re-exports from attune.commands.loader for backward compatibility.
Will be removed in attune-ai v3.0.0.
"""

import warnings

warnings.warn(
    "attune_llm.commands.loader is deprecated. Use attune.commands.loader instead. "
    "This module will be removed in attune-ai v3.0.0.",
    DeprecationWarning,
    stacklevel=2,
)

from attune.commands.loader import *  # noqa: F401,F403
