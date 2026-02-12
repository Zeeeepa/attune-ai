"""attune_llm.commands.models - DEPRECATED. Use attune.commands.models instead.

This module re-exports from attune.commands.models for backward compatibility.
Will be removed in attune-ai v3.0.0.
"""

import warnings

warnings.warn(
    "attune_llm.commands.models is deprecated. Use attune.commands.models instead. "
    "This module will be removed in attune-ai v3.0.0.",
    DeprecationWarning,
    stacklevel=2,
)

from attune.commands.models import *  # noqa: F401,F403
