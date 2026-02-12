"""attune_llm.commands.registry - DEPRECATED. Use attune.commands.registry instead.

This module re-exports from attune.commands.registry for backward compatibility.
Will be removed in attune-ai v3.0.0.
"""

import warnings

warnings.warn(
    "attune_llm.commands.registry is deprecated. Use attune.commands.registry instead. "
    "This module will be removed in attune-ai v3.0.0.",
    DeprecationWarning,
    stacklevel=2,
)

from attune.commands.registry import *  # noqa: F401,F403
