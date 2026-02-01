"""Behavioral tests configuration and fixtures.

This conftest ensures proper cleanup between tests to prevent test pollution.
"""

import pytest
from unittest.mock import patch


@pytest.fixture(autouse=True)
def cleanup_mocks():
    """Cleanup any leftover mocks after each test to prevent pollution.

    Some behavioral tests may leave patches active accidentally.
    This autouse fixture ensures a clean state for every test.
    """
    yield
    # Stop any leftover patches after test completes
    patch.stopall()
