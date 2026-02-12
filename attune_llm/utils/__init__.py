"""attune_llm.utils - DEPRECATED. Use attune.utils instead.

This module re-exports from attune.utils for backward compatibility.
Will be removed in attune-ai v3.0.0.
"""

import warnings

warnings.warn(
    "attune_llm.utils is deprecated. Use attune.utils instead. "
    "This module will be removed in attune-ai v3.0.0.",
    DeprecationWarning,
    stacklevel=2,
)

from attune.utils import *  # noqa: F401,F403
from attune.utils import __all__  # noqa: F811
