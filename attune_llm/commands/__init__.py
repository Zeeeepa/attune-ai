"""attune_llm.commands - DEPRECATED. Use attune.commands instead.

This module re-exports from attune.commands for backward compatibility.
Will be removed in attune-ai v3.0.0.
"""

import warnings

warnings.warn(
    "attune_llm.commands is deprecated. Use attune.commands instead. "
    "This module will be removed in attune-ai v3.0.0.",
    DeprecationWarning,
    stacklevel=2,
)

from attune.commands import *  # noqa: F401,F403
from attune.commands import __all__  # noqa: F811
