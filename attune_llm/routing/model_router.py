"""attune_llm.routing.model_router - DEPRECATED. Use attune.routing.model_router instead.

This module re-exports from attune.routing.model_router for backward compatibility.
Will be removed in attune-ai v3.0.0.
"""

import warnings

warnings.warn(
    "attune_llm.routing.model_router is deprecated. Use attune.routing.model_router instead. "
    "This module will be removed in attune-ai v3.0.0.",
    DeprecationWarning,
    stacklevel=2,
)

from attune.routing.model_router import *  # noqa: F401,F403
