"""Plugin test fixtures.

Clears the module-level discovery cache between tests so that
mocked entry_points are always consulted.
"""

import pytest

import attune.plugins.registry as _registry_mod


@pytest.fixture(autouse=True)
def _clear_plugin_discovery_cache():
    """Reset plugin discovery cache before and after every test."""
    _registry_mod._discovery_cache = None
    _registry_mod._global_registry = None
    yield
    _registry_mod._discovery_cache = None
    _registry_mod._global_registry = None
