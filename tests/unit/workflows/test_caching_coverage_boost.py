"""Comprehensive coverage tests for Workflow Caching Mixin.

Tests CachedResponse, CacheAwareWorkflow protocol, and CachingMixin.

Copyright 2025 Smart-AI-Memory
Licensed under Fair Source License 0.9
"""

from unittest.mock import MagicMock, patch

import pytest

import empathy_os.workflows.caching as caching_module

CachedResponse = caching_module.CachedResponse
CacheAwareWorkflow = caching_module.CacheAwareWorkflow
CachingMixin = caching_module.CachingMixin


@pytest.mark.unit
class TestCachedResponse:
    """Test CachedResponse dataclass."""

    def test_cached_response_creation(self):
        """Test creating CachedResponse with all fields."""
        response = CachedResponse(
            content="Test response content",
            input_tokens=100,
            output_tokens=50,
        )

        assert response.content == "Test response content"
        assert response.input_tokens == 100
        assert response.output_tokens == 50

    def test_cached_response_to_dict(self):
        """Test converting CachedResponse to dictionary."""
        response = CachedResponse(
            content="Sample content",
            input_tokens=200,
            output_tokens=75,
        )

        result = response.to_dict()

        assert result == {
            "content": "Sample content",
            "input_tokens": 200,
            "output_tokens": 75,
        }

    def test_cached_response_from_dict(self):
        """Test creating CachedResponse from dictionary."""
        data = {
            "content": "Restored content",
            "input_tokens": 150,
            "output_tokens": 100,
        }

        response = CachedResponse.from_dict(data)

        assert response.content == "Restored content"
        assert response.input_tokens == 150
        assert response.output_tokens == 100

    def test_cached_response_round_trip(self):
        """Test to_dict and from_dict preserve data."""
        original = CachedResponse(
            content="Round trip test",
            input_tokens=500,
            output_tokens=250,
        )

        data = original.to_dict()
        restored = CachedResponse.from_dict(data)

        assert restored.content == original.content
        assert restored.input_tokens == original.input_tokens
        assert restored.output_tokens == original.output_tokens


@pytest.mark.unit
class TestCacheAwareWorkflow:
    """Test CacheAwareWorkflow protocol."""

    def test_protocol_checks_attributes(self):
        """Test CacheAwareWorkflow protocol validates attributes."""

        class ValidWorkflow:
            name = "test"
            _cache = None
            _enable_cache = True

            def get_model_for_tier(self, tier):
                return "model-id"

        workflow = ValidWorkflow()
        assert isinstance(workflow, CacheAwareWorkflow)

    def test_protocol_rejects_missing_attributes(self):
        """Test protocol rejects objects missing required attributes."""

        class InvalidWorkflow:
            name = "test"
            # Missing _cache, _enable_cache, get_model_for_tier

        workflow = InvalidWorkflow()
        assert not isinstance(workflow, CacheAwareWorkflow)


@pytest.mark.unit
class TestCachingMixinInitialization:
    """Test CachingMixin initialization and attributes."""

    def test_mixin_default_attributes(self):
        """Test CachingMixin has correct default attributes."""
        mixin = CachingMixin()

        assert mixin._cache is None
        assert mixin._enable_cache is True
        assert mixin._cache_setup_attempted is False
        assert mixin.name == "unknown"

    def test_mixin_can_override_defaults(self):
        """Test that subclass can override defaults."""

        class CustomWorkflow(CachingMixin):
            def __init__(self):
                self.name = "custom-workflow"
                self._enable_cache = False
                self._cache = MagicMock()

        workflow = CustomWorkflow()

        assert workflow.name == "custom-workflow"
        assert workflow._enable_cache is False
        assert workflow._cache is not None


@pytest.mark.unit
class TestMakeCacheKey:
    """Test _make_cache_key method."""

    def test_make_cache_key_with_system_and_user(self):
        """Test cache key combines system and user prompts."""
        mixin = CachingMixin()

        key = mixin._make_cache_key(
            system="You are a helpful assistant",
            user_message="Analyze this code",
        )

        assert key == "You are a helpful assistant\n\nAnalyze this code"

    def test_make_cache_key_with_user_only(self):
        """Test cache key with no system prompt."""
        mixin = CachingMixin()

        key = mixin._make_cache_key(system="", user_message="Generate tests")

        assert key == "Generate tests"

    def test_make_cache_key_empty_system(self):
        """Test cache key with empty string system prompt."""
        mixin = CachingMixin()

        key = mixin._make_cache_key(system="", user_message="User message")

        assert key == "User message"
        assert "\n\n" not in key


@pytest.mark.unit
class TestMaybeSetupCache:
    """Test _maybe_setup_cache method."""

    def test_maybe_setup_cache_respects_enable_flag(self):
        """Test that setup is skipped when caching disabled."""
        mixin = CachingMixin()
        mixin._enable_cache = False

        mixin._maybe_setup_cache()

        assert mixin._cache is None
        assert mixin._cache_setup_attempted is False

    def test_maybe_setup_cache_only_runs_once(self):
        """Test setup only runs once even if called multiple times."""
        mixin = CachingMixin()
        mixin.name = "test-workflow"
        mixin._cache = MagicMock()  # Already set

        mixin._maybe_setup_cache()
        mixin._maybe_setup_cache()
        mixin._maybe_setup_cache()

        # Should not attempt setup again
        assert mixin._cache_setup_attempted is True

    def test_maybe_setup_cache_uses_existing_cache(self):
        """Test that existing cache is not replaced."""
        mixin = CachingMixin()
        mixin.name = "test"
        existing_cache = MagicMock()
        mixin._cache = existing_cache

        mixin._maybe_setup_cache()

        assert mixin._cache is existing_cache
        assert mixin._cache_setup_attempted is True

    @patch("empathy_os.cache.auto_setup_cache")
    @patch("empathy_os.cache.create_cache")
    def test_maybe_setup_cache_creates_cache(self, mock_create, mock_auto):
        """Test that cache is created when not provided."""
        mixin = CachingMixin()
        mixin.name = "test-workflow"

        mock_cache = MagicMock()
        mock_create.return_value = mock_cache

        mixin._maybe_setup_cache()

        mock_auto.assert_called_once()
        mock_create.assert_called_once()
        assert mixin._cache is mock_cache

    @patch("empathy_os.cache.auto_setup_cache")
    @patch("empathy_os.cache.create_cache")
    def test_maybe_setup_cache_falls_back_to_hash_on_import_error(
        self, mock_create, mock_auto
    ):
        """Test fallback to hash cache when hybrid dependencies missing."""
        mixin = CachingMixin()
        mixin.name = "test"

        mock_auto.side_effect = ImportError("sentence-transformers not found")
        mock_hash_cache = MagicMock()
        mock_create.return_value = mock_hash_cache

        mixin._maybe_setup_cache()

        # Should call create_cache with hash type
        mock_create.assert_called_once_with(cache_type="hash")
        assert mixin._cache is mock_hash_cache

    @patch("empathy_os.cache.auto_setup_cache")
    def test_maybe_setup_cache_disables_on_os_error(self, mock_auto):
        """Test cache is disabled on file system errors."""
        mixin = CachingMixin()
        mixin.name = "test"

        mock_auto.side_effect = OSError("Permission denied")

        mixin._maybe_setup_cache()

        assert mixin._enable_cache is False
        assert mixin._cache is None

    @patch("empathy_os.cache.auto_setup_cache")
    def test_maybe_setup_cache_disables_on_permission_error(self, mock_auto):
        """Test cache is disabled on permission errors."""
        mixin = CachingMixin()
        mixin.name = "test"

        mock_auto.side_effect = PermissionError("Cannot write to cache dir")

        mixin._maybe_setup_cache()

        assert mixin._enable_cache is False

    @patch("empathy_os.cache.auto_setup_cache")
    def test_maybe_setup_cache_disables_on_value_error(self, mock_auto):
        """Test cache is disabled on configuration errors."""
        mixin = CachingMixin()
        mixin.name = "test"

        mock_auto.side_effect = ValueError("Invalid cache config")

        mixin._maybe_setup_cache()

        assert mixin._enable_cache is False


@pytest.mark.unit
class TestTryCacheLookup:
    """Test _try_cache_lookup method."""

    def test_try_cache_lookup_returns_none_when_disabled(self):
        """Test cache lookup returns None when caching disabled."""
        mixin = CachingMixin()
        mixin._enable_cache = False

        result = mixin._try_cache_lookup(
            stage="test",
            system="system",
            user_message="user",
            model="model-id",
        )

        assert result is None

    def test_try_cache_lookup_returns_none_when_no_cache(self):
        """Test cache lookup returns None when cache not set."""
        mixin = CachingMixin()
        mixin._cache = None

        result = mixin._try_cache_lookup(
            stage="test",
            system="",
            user_message="message",
            model="model",
        )

        assert result is None

    def test_try_cache_lookup_returns_cached_response(self):
        """Test successful cache lookup returns CachedResponse."""
        mixin = CachingMixin()
        mixin.name = "test-workflow"

        mock_cache = MagicMock()
        mock_cache.get.return_value = {
            "content": "Cached content",
            "input_tokens": 100,
            "output_tokens": 50,
        }
        mixin._cache = mock_cache

        result = mixin._try_cache_lookup(
            stage="analyze",
            system="System prompt",
            user_message="User message",
            model="claude-3",
        )

        assert isinstance(result, CachedResponse)
        assert result.content == "Cached content"
        assert result.input_tokens == 100
        assert result.output_tokens == 50

    def test_try_cache_lookup_calls_cache_with_correct_key(self):
        """Test cache is called with correct parameters."""
        mixin = CachingMixin()
        mixin.name = "workflow"

        mock_cache = MagicMock()
        mock_cache.get.return_value = None
        mixin._cache = mock_cache

        mixin._try_cache_lookup(
            stage="stage1",
            system="sys",
            user_message="user",
            model="model-x",
        )

        mock_cache.get.assert_called_once_with(
            "workflow", "stage1", "sys\n\nuser", "model-x"
        )

    def test_try_cache_lookup_handles_key_error(self):
        """Test cache lookup handles malformed cache data gracefully."""
        mixin = CachingMixin()
        mixin.name = "test"

        mock_cache = MagicMock()
        mock_cache.get.side_effect = KeyError("missing key")
        mixin._cache = mock_cache

        result = mixin._try_cache_lookup("stage", "", "msg", "model")

        assert result is None

    def test_try_cache_lookup_handles_type_error(self):
        """Test cache lookup handles type errors in cached data."""
        mixin = CachingMixin()
        mixin.name = "test"

        mock_cache = MagicMock()
        mock_cache.get.side_effect = TypeError("invalid data type")
        mixin._cache = mock_cache

        result = mixin._try_cache_lookup("stage", "", "msg", "model")

        assert result is None

    def test_try_cache_lookup_handles_os_error(self):
        """Test cache lookup handles file system errors."""
        mixin = CachingMixin()
        mixin.name = "test"

        mock_cache = MagicMock()
        mock_cache.get.side_effect = OSError("disk error")
        mixin._cache = mock_cache

        result = mixin._try_cache_lookup("stage", "", "msg", "model")

        assert result is None


@pytest.mark.unit
class TestStoreInCache:
    """Test _store_in_cache method."""

    def test_store_in_cache_returns_false_when_disabled(self):
        """Test store returns False when caching disabled."""
        mixin = CachingMixin()
        mixin._enable_cache = False

        response = CachedResponse("content", 10, 5)
        result = mixin._store_in_cache("stage", "", "msg", "model", response)

        assert result is False

    def test_store_in_cache_returns_false_when_no_cache(self):
        """Test store returns False when cache not set."""
        mixin = CachingMixin()
        mixin._cache = None

        response = CachedResponse("content", 10, 5)
        result = mixin._store_in_cache("stage", "", "msg", "model", response)

        assert result is False

    def test_store_in_cache_stores_response(self):
        """Test successful cache storage."""
        mixin = CachingMixin()
        mixin.name = "workflow"

        mock_cache = MagicMock()
        mixin._cache = mock_cache

        response = CachedResponse("Test content", 100, 50)
        result = mixin._store_in_cache(
            stage="analyze",
            system="System",
            user_message="User",
            model="model-id",
            response=response,
        )

        assert result is True
        mock_cache.put.assert_called_once()

    def test_store_in_cache_calls_put_with_correct_args(self):
        """Test cache.put is called with correct parameters."""
        mixin = CachingMixin()
        mixin.name = "test-workflow"

        mock_cache = MagicMock()
        mixin._cache = mock_cache

        response = CachedResponse("Content", 200, 75)
        mixin._store_in_cache(
            stage="stage1",
            system="sys",
            user_message="user",
            model="model-x",
            response=response,
        )

        mock_cache.put.assert_called_once_with(
            "test-workflow",
            "stage1",
            "sys\n\nuser",
            "model-x",
            {"content": "Content", "input_tokens": 200, "output_tokens": 75},
        )

    def test_store_in_cache_handles_os_error(self):
        """Test store handles file system errors gracefully."""
        mixin = CachingMixin()
        mixin.name = "test"

        mock_cache = MagicMock()
        mock_cache.put.side_effect = OSError("disk full")
        mixin._cache = mock_cache

        response = CachedResponse("content", 10, 5)
        result = mixin._store_in_cache("stage", "", "msg", "model", response)

        assert result is False

    def test_store_in_cache_handles_value_error(self):
        """Test store handles serialization errors."""
        mixin = CachingMixin()
        mixin.name = "test"

        mock_cache = MagicMock()
        mock_cache.put.side_effect = ValueError("cannot serialize")
        mixin._cache = mock_cache

        response = CachedResponse("content", 10, 5)
        result = mixin._store_in_cache("stage", "", "msg", "model", response)

        assert result is False


@pytest.mark.unit
class TestGetCacheType:
    """Test _get_cache_type method."""

    def test_get_cache_type_returns_none_when_no_cache(self):
        """Test returns 'none' when cache not set."""
        mixin = CachingMixin()
        mixin._cache = None

        cache_type = mixin._get_cache_type()

        assert cache_type == "none"

    def test_get_cache_type_returns_cache_type_attribute(self):
        """Test returns cache_type attribute when present."""
        mixin = CachingMixin()

        mock_cache = MagicMock()
        mock_cache.cache_type = "semantic"
        mixin._cache = mock_cache

        cache_type = mixin._get_cache_type()

        assert cache_type == "semantic"

    def test_get_cache_type_defaults_to_hash_when_no_attribute(self):
        """Test defaults to 'hash' when cache_type not available."""
        mixin = CachingMixin()

        mock_cache = MagicMock(spec=[])  # No cache_type attribute
        delattr(mock_cache, "cache_type")
        mixin._cache = mock_cache

        cache_type = mixin._get_cache_type()

        assert cache_type == "hash"

    def test_get_cache_type_handles_non_string_cache_type(self):
        """Test handles non-string cache_type values."""
        mixin = CachingMixin()

        mock_cache = MagicMock()
        mock_cache.cache_type = None
        mixin._cache = mock_cache

        cache_type = mixin._get_cache_type()

        assert cache_type == "hash"


@pytest.mark.unit
class TestGetCacheStats:
    """Test _get_cache_stats method."""

    def test_get_cache_stats_returns_zeros_when_no_cache(self):
        """Test returns zero stats when cache not set."""
        mixin = CachingMixin()
        mixin._cache = None

        stats = mixin._get_cache_stats()

        assert stats == {"hits": 0, "misses": 0, "hit_rate": 0.0}

    def test_get_cache_stats_returns_cache_statistics(self):
        """Test returns stats from cache."""
        mixin = CachingMixin()

        mock_stats = MagicMock()
        mock_stats.hits = 150
        mock_stats.misses = 50
        mock_stats.hit_rate = 0.75

        mock_cache = MagicMock()
        mock_cache.get_stats.return_value = mock_stats
        mixin._cache = mock_cache

        stats = mixin._get_cache_stats()

        assert stats == {"hits": 150, "misses": 50, "hit_rate": 0.75}

    def test_get_cache_stats_handles_missing_get_stats_method(self):
        """Test handles cache without get_stats method."""
        mixin = CachingMixin()

        mock_cache = MagicMock(spec=[])  # No get_stats method
        delattr(mock_cache, "get_stats")
        mixin._cache = mock_cache

        stats = mixin._get_cache_stats()

        assert stats == {"hits": 0, "misses": 0, "hit_rate": 0.0}

    def test_get_cache_stats_handles_attribute_error(self):
        """Test handles AttributeError gracefully."""
        mixin = CachingMixin()

        mock_cache = MagicMock()
        mock_cache.get_stats.side_effect = AttributeError("no stats")
        mixin._cache = mock_cache

        stats = mixin._get_cache_stats()

        assert stats == {"hits": 0, "misses": 0, "hit_rate": 0.0}


@pytest.mark.unit
class TestIntegration:
    """Integration tests for CachingMixin."""

    def test_full_cache_workflow(self):
        """Test complete caching workflow: setup, lookup, store."""

        class TestWorkflow(CachingMixin):
            def __init__(self):
                self.name = "integration-test"
                self._enable_cache = True
                self._cache = MagicMock()
                self._cache_setup_attempted = False

        workflow = TestWorkflow()

        # Setup cache
        workflow._maybe_setup_cache()
        assert workflow._cache_setup_attempted is True

        # Lookup (miss)
        workflow._cache.get.return_value = None
        result = workflow._try_cache_lookup("stage1", "sys", "user", "model")
        assert result is None

        # Store
        response = CachedResponse("New content", 100, 50)
        stored = workflow._store_in_cache("stage1", "sys", "user", "model", response)
        assert stored is True

        # Lookup (hit)
        workflow._cache.get.return_value = response.to_dict()
        result = workflow._try_cache_lookup("stage1", "sys", "user", "model")
        assert result is not None
        assert result.content == "New content"

    def test_caching_disabled_workflow(self):
        """Test workflow with caching disabled."""

        class DisabledCacheWorkflow(CachingMixin):
            def __init__(self):
                self.name = "no-cache"
                self._enable_cache = False

        workflow = DisabledCacheWorkflow()

        # Setup should do nothing
        workflow._maybe_setup_cache()
        assert workflow._cache is None

        # Lookup should return None
        result = workflow._try_cache_lookup("stage", "", "msg", "model")
        assert result is None

        # Store should return False
        response = CachedResponse("test", 10, 5)
        stored = workflow._store_in_cache("stage", "", "msg", "model", response)
        assert stored is False
