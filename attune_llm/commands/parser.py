"""attune_llm.commands.parser - DEPRECATED. Use attune.commands.parser instead.

This module re-exports from attune.commands.parser for backward compatibility.
Will be removed in attune-ai v3.0.0.
"""

import warnings

warnings.warn(
    "attune_llm.commands.parser is deprecated. Use attune.commands.parser instead. "
    "This module will be removed in attune-ai v3.0.0.",
    DeprecationWarning,
    stacklevel=2,
)

from attune.commands.parser import *  # noqa: F401,F403
