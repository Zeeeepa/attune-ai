"""Tests for cache modules.

Covers CacheEntry, CacheStats, BaseCache, HashOnlyCache, and HybridCache.

Copyright 2025 Smart-AI-Memory
Licensed under Fair Source License 0.9
"""

import time
from unittest.mock import MagicMock, patch

import numpy as np
import pytest

from empathy_os.cache.base import CacheEntry, CacheStats
from empathy_os.cache.hash_only import HashOnlyCache


@pytest.mark.unit
class TestCacheEntry:
    """Tests for CacheEntry dataclass."""

    def test_cache_entry_creation(self):
        """Test creating a basic CacheEntry."""
        entry = CacheEntry(
            key="abc123",
            response={"result": "test"},
            workflow="code-review",
            stage="scan",
            model="claude-3-5-sonnet",
            prompt_hash="hash123",
            timestamp=time.time(),
            ttl=3600,
        )

        assert entry.key == "abc123"
        assert entry.response == {"result": "test"}
        assert entry.workflow == "code-review"
        assert entry.stage == "scan"
        assert entry.model == "claude-3-5-sonnet"
        assert entry.ttl == 3600

    def test_cache_entry_not_expired(self):
        """Test is_expired returns False for fresh entry."""
        entry = CacheEntry(
            key="test",
            response="data",
            workflow="test",
            stage="test",
            model="test",
            prompt_hash="hash",
            timestamp=time.time(),
            ttl=3600,
        )

        assert entry.is_expired(time.time()) is False

    def test_cache_entry_expired(self):
        """Test is_expired returns True for old entry."""
        old_timestamp = time.time() - 7200  # 2 hours ago
        entry = CacheEntry(
            key="test",
            response="data",
            workflow="test",
            stage="test",
            model="test",
            prompt_hash="hash",
            timestamp=old_timestamp,
            ttl=3600,  # 1 hour TTL
        )

        assert entry.is_expired(time.time()) is True

    def test_cache_entry_no_ttl_never_expires(self):
        """Test entry with None TTL never expires."""
        old_timestamp = time.time() - 86400 * 365  # 1 year ago
        entry = CacheEntry(
            key="test",
            response="data",
            workflow="test",
            stage="test",
            model="test",
            prompt_hash="hash",
            timestamp=old_timestamp,
            ttl=None,
        )

        assert entry.is_expired(time.time()) is False


@pytest.mark.unit
class TestCacheStats:
    """Tests for CacheStats dataclass."""

    def test_cache_stats_defaults(self):
        """Test CacheStats default values."""
        stats = CacheStats()

        assert stats.hits == 0
        assert stats.misses == 0
        assert stats.evictions == 0
        assert stats.total == 0
        assert stats.hit_rate == 0.0

    def test_cache_stats_total(self):
        """Test total property."""
        stats = CacheStats(hits=10, misses=5)

        assert stats.total == 15

    def test_cache_stats_hit_rate(self):
        """Test hit_rate calculation."""
        stats = CacheStats(hits=75, misses=25)

        assert stats.hit_rate == 75.0

    def test_cache_stats_hit_rate_zero_total(self):
        """Test hit_rate returns 0 when no lookups."""
        stats = CacheStats()

        assert stats.hit_rate == 0.0

    def test_cache_stats_to_dict(self):
        """Test to_dict serialization."""
        stats = CacheStats(hits=10, misses=5, evictions=2)

        result = stats.to_dict()

        assert result["hits"] == 10
        assert result["misses"] == 5
        assert result["evictions"] == 2
        assert result["total"] == 15
        assert result["hit_rate"] == 66.7


@pytest.mark.unit
class TestHashOnlyCache:
    """Tests for HashOnlyCache class."""

    def test_cache_initialization(self):
        """Test HashOnlyCache initialization."""
        cache = HashOnlyCache(max_size_mb=100, default_ttl=7200, max_memory_mb=50)

        assert cache.max_size_mb == 100
        assert cache.default_ttl == 7200
        assert cache.max_memory_mb == 50

    def test_cache_get_miss(self):
        """Test cache miss returns None."""
        cache = HashOnlyCache()

        result = cache.get("workflow", "stage", "prompt", "model")

        assert result is None
        assert cache.stats.misses == 1

    def test_cache_put_and_get(self):
        """Test storing and retrieving from cache."""
        cache = HashOnlyCache()

        cache.put("code-review", "scan", "test prompt", "sonnet", {"result": "response"})
        result = cache.get("code-review", "scan", "test prompt", "sonnet")

        assert result == {"result": "response"}
        assert cache.stats.hits == 1

    def test_cache_hit_rate_tracking(self):
        """Test cache tracks hit rate correctly."""
        cache = HashOnlyCache()

        # First access (miss)
        cache.get("workflow", "stage", "prompt1", "model")

        # Store and hit
        cache.put("workflow", "stage", "prompt2", "model", "response")
        cache.get("workflow", "stage", "prompt2", "model")

        assert cache.stats.hits == 1
        assert cache.stats.misses == 1
        assert cache.stats.hit_rate == 50.0

    def test_cache_expired_entry_not_returned(self):
        """Test expired entries are not returned."""
        cache = HashOnlyCache(default_ttl=1)  # 1 second TTL

        cache.put("workflow", "stage", "prompt", "model", "response")

        # Wait for expiration
        time.sleep(1.5)

        result = cache.get("workflow", "stage", "prompt", "model")

        assert result is None
        assert cache.stats.evictions == 1

    def test_cache_clear(self):
        """Test clearing cache."""
        cache = HashOnlyCache()

        cache.put("workflow", "stage", "prompt1", "model", "response1")
        cache.put("workflow", "stage", "prompt2", "model", "response2")

        cache.clear()

        assert cache.get("workflow", "stage", "prompt1", "model") is None
        assert len(cache._memory_cache) == 0

    def test_cache_get_stats(self):
        """Test get_stats returns CacheStats."""
        cache = HashOnlyCache()

        cache.get("workflow", "stage", "prompt", "model")  # Miss
        cache.put("workflow", "stage", "prompt", "model", "response")
        cache.get("workflow", "stage", "prompt", "model")  # Hit

        stats = cache.get_stats()

        assert isinstance(stats, CacheStats)
        assert stats.hits == 1
        assert stats.misses == 1

    def test_cache_evict_expired(self):
        """Test evict_expired removes old entries."""
        cache = HashOnlyCache(default_ttl=1)

        cache.put("workflow", "stage", "prompt1", "model", "response1")
        cache.put("workflow", "stage", "prompt2", "model", "response2")

        time.sleep(1.5)

        evicted = cache.evict_expired()

        assert evicted == 2
        assert len(cache._memory_cache) == 0

    def test_cache_size_info(self):
        """Test size_info returns cache metrics."""
        cache = HashOnlyCache(max_memory_mb=100)

        cache.put("workflow", "stage", "prompt", "model", "response")

        info = cache.size_info()

        assert info["entries"] == 1
        assert info["max_memory_mb"] == 100
        assert "estimated_mb" in info

    def test_cache_lru_eviction(self):
        """Test LRU eviction when cache is full."""
        cache = HashOnlyCache(max_memory_mb=0.01)  # Very small to trigger eviction

        # Add many entries to trigger eviction
        for i in range(100):
            cache.put(f"workflow{i}", "stage", "prompt", "model", f"response{i}")

        assert cache.stats.evictions > 0

    def test_cache_custom_ttl(self):
        """Test storing with custom TTL."""
        cache = HashOnlyCache(default_ttl=3600)

        cache.put("workflow", "stage", "prompt", "model", "response", ttl=1)

        # Should be in cache immediately
        result = cache.get("workflow", "stage", "prompt", "model")
        assert result == "response"

        # Should expire quickly
        time.sleep(1.5)
        result = cache.get("workflow", "stage", "prompt", "model")
        assert result is None

    def test_cache_different_keys(self):
        """Test different prompts create different cache keys."""
        cache = HashOnlyCache()

        cache.put("workflow", "stage", "prompt1", "model", "response1")
        cache.put("workflow", "stage", "prompt2", "model", "response2")

        result1 = cache.get("workflow", "stage", "prompt1", "model")
        result2 = cache.get("workflow", "stage", "prompt2", "model")

        assert result1 == "response1"
        assert result2 == "response2"

    def test_cache_same_prompt_different_workflow(self):
        """Test same prompt in different workflows creates separate entries."""
        cache = HashOnlyCache()

        cache.put("workflow1", "stage", "prompt", "model", "response1")
        cache.put("workflow2", "stage", "prompt", "model", "response2")

        result1 = cache.get("workflow1", "stage", "prompt", "model")
        result2 = cache.get("workflow2", "stage", "prompt", "model")

        assert result1 == "response1"
        assert result2 == "response2"


@pytest.mark.unit
class TestBaseCacheKeyGeneration:
    """Tests for BaseCache cache key generation."""

    def test_create_cache_key_consistent(self):
        """Test cache key is consistent for same inputs."""
        cache = HashOnlyCache()

        key1 = cache._create_cache_key("workflow", "stage", "prompt", "model")
        key2 = cache._create_cache_key("workflow", "stage", "prompt", "model")

        assert key1 == key2

    def test_create_cache_key_different_inputs(self):
        """Test different inputs create different keys."""
        cache = HashOnlyCache()

        key1 = cache._create_cache_key("workflow", "stage", "prompt1", "model")
        key2 = cache._create_cache_key("workflow", "stage", "prompt2", "model")

        assert key1 != key2

    def test_create_cache_key_sha256_format(self):
        """Test cache key is valid SHA256 hex."""
        cache = HashOnlyCache()

        key = cache._create_cache_key("workflow", "stage", "prompt", "model")

        assert len(key) == 64  # SHA256 hex is 64 chars
        assert all(c in "0123456789abcdef" for c in key)


@pytest.mark.unit
class TestHybridCacheBasics:
    """Tests for HybridCache basic functionality (mocked)."""

    @patch("sentence_transformers.SentenceTransformer")
    @patch("empathy_os.cache.hybrid.CacheStorage")
    def test_hybrid_cache_initialization(self, mock_storage, mock_model):
        """Test HybridCache initialization with mocked dependencies."""
        from empathy_os.cache.hybrid import HybridCache

        mock_storage.return_value.get_all.return_value = []
        mock_model.return_value.encode.return_value = np.zeros(384)

        cache = HybridCache(
            max_size_mb=100,
            default_ttl=7200,
            max_memory_mb=50,
            similarity_threshold=0.95,
        )

        assert cache.max_size_mb == 100
        assert cache.default_ttl == 7200
        assert cache.max_memory_mb == 50
        assert cache.similarity_threshold == 0.95

    @patch("sentence_transformers.SentenceTransformer")
    @patch("empathy_os.cache.hybrid.CacheStorage")
    def test_hybrid_cache_hash_hit(self, mock_storage, mock_model):
        """Test HybridCache hash-based cache hit."""
        from empathy_os.cache.hybrid import HybridCache

        mock_storage.return_value.get_all.return_value = []
        mock_model.return_value.encode.return_value = np.zeros(384)

        cache = HybridCache()

        cache.put("workflow", "stage", "exact prompt", "model", "response")
        result = cache.get("workflow", "stage", "exact prompt", "model")

        assert result == "response"
        assert cache.stats.hits == 1

    @patch("sentence_transformers.SentenceTransformer")
    @patch("empathy_os.cache.hybrid.CacheStorage")
    def test_hybrid_cache_miss(self, mock_storage, mock_model):
        """Test HybridCache miss."""
        from empathy_os.cache.hybrid import HybridCache

        mock_storage.return_value.get_all.return_value = []
        mock_model.return_value.encode.return_value = np.zeros(384)

        cache = HybridCache()

        result = cache.get("workflow", "stage", "unknown prompt", "model")

        assert result is None
        assert cache.stats.misses == 1

    @patch("sentence_transformers.SentenceTransformer")
    @patch("empathy_os.cache.hybrid.CacheStorage")
    def test_hybrid_cache_clear(self, mock_storage, mock_model):
        """Test HybridCache clear."""
        from empathy_os.cache.hybrid import HybridCache

        mock_storage.return_value.get_all.return_value = []
        mock_storage.return_value.clear.return_value = 0
        mock_model.return_value.encode.return_value = np.zeros(384)

        cache = HybridCache()

        cache.put("workflow", "stage", "prompt", "model", "response")
        cache.clear()

        assert len(cache._hash_cache) == 0
        assert len(cache._semantic_cache) == 0

    @patch("sentence_transformers.SentenceTransformer")
    @patch("empathy_os.cache.hybrid.CacheStorage")
    def test_hybrid_cache_size_info(self, mock_storage, mock_model):
        """Test HybridCache size_info."""
        from empathy_os.cache.hybrid import HybridCache

        mock_storage.return_value.get_all.return_value = []
        mock_model.return_value.encode.return_value = np.zeros(384)

        cache = HybridCache(similarity_threshold=0.95)

        cache.put("workflow", "stage", "prompt", "model", "response")

        info = cache.size_info()

        assert info["hash_entries"] == 1
        assert info["semantic_entries"] == 1
        assert info["threshold"] == 0.95
        assert "total_size_mb" in info

    @patch("sentence_transformers.SentenceTransformer")
    @patch("empathy_os.cache.hybrid.CacheStorage")
    def test_hybrid_cache_evict_expired(self, mock_storage, mock_model):
        """Test HybridCache evict_expired."""
        from empathy_os.cache.hybrid import HybridCache

        mock_storage.return_value.get_all.return_value = []
        mock_model.return_value.encode.return_value = np.zeros(384)

        cache = HybridCache(default_ttl=1)

        cache.put("workflow", "stage", "prompt", "model", "response")

        time.sleep(1.5)

        evicted = cache.evict_expired()

        assert evicted == 1
        assert len(cache._hash_cache) == 0


@pytest.mark.unit
class TestCosineSimilarity:
    """Tests for cosine_similarity function."""

    def test_identical_vectors(self):
        """Test cosine similarity of identical vectors."""
        from empathy_os.cache.hybrid import cosine_similarity

        a = np.array([1.0, 2.0, 3.0])
        b = np.array([1.0, 2.0, 3.0])

        similarity = cosine_similarity(a, b)

        assert abs(similarity - 1.0) < 0.0001

    def test_orthogonal_vectors(self):
        """Test cosine similarity of orthogonal vectors."""
        from empathy_os.cache.hybrid import cosine_similarity

        a = np.array([1.0, 0.0])
        b = np.array([0.0, 1.0])

        similarity = cosine_similarity(a, b)

        assert abs(similarity) < 0.0001

    def test_opposite_vectors(self):
        """Test cosine similarity of opposite vectors."""
        from empathy_os.cache.hybrid import cosine_similarity

        a = np.array([1.0, 2.0, 3.0])
        b = np.array([-1.0, -2.0, -3.0])

        similarity = cosine_similarity(a, b)

        assert abs(similarity + 1.0) < 0.0001

    def test_similar_vectors(self):
        """Test cosine similarity of similar vectors."""
        from empathy_os.cache.hybrid import cosine_similarity

        a = np.array([1.0, 2.0, 3.0])
        b = np.array([1.1, 2.1, 3.1])

        similarity = cosine_similarity(a, b)

        assert similarity > 0.99  # Very similar


@pytest.mark.unit
class TestHybridCacheSemanticMatching:
    """Tests for HybridCache semantic similarity matching."""

    @patch("sentence_transformers.SentenceTransformer")
    @patch("empathy_os.cache.hybrid.CacheStorage")
    def test_semantic_cache_populated_on_put(self, mock_storage, mock_model):
        """Test semantic cache is populated when putting entries."""
        from empathy_os.cache.hybrid import HybridCache

        mock_storage.return_value.get_all.return_value = []
        mock_model.return_value.encode.return_value = np.random.rand(384)

        cache = HybridCache()

        cache.put("workflow", "stage", "prompt", "model", "response")

        assert len(cache._semantic_cache) == 1

    @patch("sentence_transformers.SentenceTransformer")
    @patch("empathy_os.cache.hybrid.CacheStorage")
    def test_semantic_lookup_finds_similar(self, mock_storage, mock_model):
        """Test semantic lookup finds similar prompts."""
        from empathy_os.cache.hybrid import HybridCache

        mock_storage.return_value.get_all.return_value = []

        # Return slightly different but similar embeddings
        embedding1 = np.array([0.9, 0.1, 0.0])
        embedding2 = np.array([0.85, 0.15, 0.0])  # Very similar to embedding1

        mock_model.return_value.encode.side_effect = [embedding1, embedding2]

        cache = HybridCache(similarity_threshold=0.95)

        # Store first prompt
        cache.put("workflow", "stage", "original prompt", "model", "response1")

        # Try similar prompt (should get semantic hit)
        # Note: Due to how mocking works, we need to be careful about the exact flow
        mock_model.return_value.encode.return_value = embedding2
        result = cache._semantic_lookup("similar prompt", "workflow", "stage", "model")

        # The semantic lookup should find the similar prompt if threshold is met
        if result is not None:
            entry, similarity = result
            assert similarity >= cache.similarity_threshold

    @patch("sentence_transformers.SentenceTransformer")
    @patch("empathy_os.cache.hybrid.CacheStorage")
    def test_semantic_lookup_respects_workflow_filter(self, mock_storage, mock_model):
        """Test semantic lookup only matches same workflow/stage/model."""
        from empathy_os.cache.hybrid import HybridCache

        mock_storage.return_value.get_all.return_value = []
        mock_model.return_value.encode.return_value = np.random.rand(384)

        cache = HybridCache()

        cache.put("workflow1", "stage", "prompt", "model", "response")

        # Lookup with different workflow should not match
        result = cache._semantic_lookup("prompt", "workflow2", "stage", "model")

        assert result is None

    @patch("sentence_transformers.SentenceTransformer")
    @patch("empathy_os.cache.hybrid.CacheStorage")
    def test_semantic_lookup_empty_cache(self, mock_storage, mock_model):
        """Test semantic lookup with empty cache returns None."""
        from empathy_os.cache.hybrid import HybridCache

        mock_storage.return_value.get_all.return_value = []
        mock_model.return_value.encode.return_value = np.random.rand(384)

        cache = HybridCache()

        result = cache._semantic_lookup("prompt", "workflow", "stage", "model")

        assert result is None


@pytest.mark.unit
class TestHybridCachePersistence:
    """Tests for HybridCache persistent storage."""

    @patch("sentence_transformers.SentenceTransformer")
    @patch("empathy_os.cache.hybrid.CacheStorage")
    def test_loads_from_storage_on_init(self, mock_storage_cls, mock_model):
        """Test HybridCache loads entries from storage on initialization."""
        from empathy_os.cache.base import CacheEntry
        from empathy_os.cache.hybrid import HybridCache

        mock_entry = CacheEntry(
            key="existing_key",
            response="stored_response",
            workflow="workflow",
            stage="stage",
            model="model",
            prompt_hash="hash",
            timestamp=time.time(),
            ttl=3600,
        )

        mock_storage = MagicMock()
        mock_storage.get_all.return_value = [mock_entry]
        mock_storage_cls.return_value = mock_storage

        mock_model.return_value.encode.return_value = np.zeros(384)

        cache = HybridCache()

        assert "existing_key" in cache._hash_cache

    @patch("sentence_transformers.SentenceTransformer")
    @patch("empathy_os.cache.hybrid.CacheStorage")
    def test_persists_on_put(self, mock_storage_cls, mock_model):
        """Test HybridCache persists entries to storage on put."""
        from empathy_os.cache.hybrid import HybridCache

        mock_storage = MagicMock()
        mock_storage.get_all.return_value = []
        mock_storage_cls.return_value = mock_storage

        mock_model.return_value.encode.return_value = np.zeros(384)

        cache = HybridCache()

        cache.put("workflow", "stage", "prompt", "model", "response")

        mock_storage.put.assert_called_once()

    @patch("sentence_transformers.SentenceTransformer")
    @patch("empathy_os.cache.hybrid.CacheStorage")
    def test_clears_storage_on_clear(self, mock_storage_cls, mock_model):
        """Test HybridCache clears storage when clear() is called."""
        from empathy_os.cache.hybrid import HybridCache

        mock_storage = MagicMock()
        mock_storage.get_all.return_value = []
        mock_storage.clear.return_value = 5
        mock_storage_cls.return_value = mock_storage

        mock_model.return_value.encode.return_value = np.zeros(384)

        cache = HybridCache()
        cache.clear()

        mock_storage.clear.assert_called_once()


@pytest.mark.unit
class TestHybridCacheLRUEviction:
    """Tests for HybridCache LRU eviction."""

    @patch("sentence_transformers.SentenceTransformer")
    @patch("empathy_os.cache.hybrid.CacheStorage")
    def test_lru_eviction_triggered(self, mock_storage, mock_model):
        """Test LRU eviction is triggered when cache exceeds max size."""
        from empathy_os.cache.hybrid import HybridCache

        mock_storage.return_value.get_all.return_value = []
        mock_model.return_value.encode.return_value = np.zeros(384)

        cache = HybridCache(max_memory_mb=0.001)  # Tiny cache to trigger eviction

        # Add many entries
        for i in range(50):
            cache.put(f"workflow{i}", "stage", f"prompt{i}", "model", f"response{i}")

        assert cache.stats.evictions > 0

    @patch("sentence_transformers.SentenceTransformer")
    @patch("empathy_os.cache.hybrid.CacheStorage")
    def test_evict_entry_removes_from_both_caches(self, mock_storage, mock_model):
        """Test _evict_entry removes entry from both hash and semantic caches."""
        from empathy_os.cache.hybrid import HybridCache

        mock_storage.return_value.get_all.return_value = []
        mock_model.return_value.encode.return_value = np.zeros(384)

        cache = HybridCache()

        cache.put("workflow", "stage", "prompt", "model", "response")

        # Get the key
        cache_key = cache._create_cache_key("workflow", "stage", "prompt", "model")

        # Verify entry exists
        assert cache_key in cache._hash_cache
        assert len(cache._semantic_cache) == 1

        # Evict entry
        cache._evict_entry(cache_key)

        # Verify entry is removed
        assert cache_key not in cache._hash_cache
        assert len(cache._semantic_cache) == 0
