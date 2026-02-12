"""attune_llm.config.unified - DEPRECATED. Use attune.config.agent_config instead.

This module re-exports from attune.config.agent_config for backward compatibility.
Will be removed in attune-ai v3.0.0.
"""

import warnings

warnings.warn(
    "attune_llm.config.unified is deprecated. Use attune.config.agent_config instead. "
    "This module will be removed in attune-ai v3.0.0.",
    DeprecationWarning,
    stacklevel=2,
)

from attune.config.agent_config import *  # noqa: F401,F403
