"""Unit tests for HybridCache.

Tests hybrid hash + semantic similarity caching with mocked sentence transformers.
"""

import time
from unittest.mock import Mock, patch

import numpy as np
import pytest

from empathy_os.cache.hybrid import HybridCache, cosine_similarity


class TestHybridCache:
    """Test suite for HybridCache."""

    @patch("sentence_transformers.SentenceTransformer")
    def test_init(self, mock_st):
        """Test cache initialization."""
        cache = HybridCache(
            max_size_mb=500,
            default_ttl=3600,
            similarity_threshold=0.95,
        )

        assert cache.max_size_mb == 500
        assert cache.default_ttl == 3600
        assert cache.similarity_threshold == 0.95
        assert cache.stats.hits == 0
        assert cache.stats.misses == 0
        mock_st.assert_called_once()

    @patch("sentence_transformers.SentenceTransformer")
    def test_hash_cache_hit(self, mock_st):
        """Test fast path hash cache hit."""
        # Mock sentence transformer
        mock_model = Mock()
        mock_st.return_value = mock_model

        cache = HybridCache()

        # Store response
        cache.put("code-review", "scan", "test prompt", "sonnet", {"result": "ok"})

        # Retrieve exact same (hash hit)
        result = cache.get("code-review", "scan", "test prompt", "sonnet")

        assert result == {"result": "ok"}
        assert cache.stats.hits == 1
        assert cache.stats.misses == 0

    @patch("sentence_transformers.SentenceTransformer")
    def test_semantic_cache_hit(self, mock_st):
        """Test semantic similarity cache hit."""
        # Mock sentence transformer
        mock_model = Mock()
        mock_st.return_value = mock_model

        # Mock embeddings (95% similar)
        embedding1 = np.array([1.0, 0.0, 0.0])
        embedding2 = np.array([0.95, 0.312, 0.0])  # ~95% cosine similarity

        def encode_side_effect(text, **kwargs):
            if text == "Add auth middleware":
                return embedding1
            elif text == "Add logging middleware":
                return embedding2
            return np.random.rand(3)

        mock_model.encode.side_effect = encode_side_effect

        cache = HybridCache(similarity_threshold=0.90)

        # Store original
        cache.put("code-review", "scan", "Add auth middleware", "sonnet", {"auth": "middleware"})

        # Retrieve similar (should hit semantic cache)
        result = cache.get("code-review", "scan", "Add logging middleware", "sonnet")

        assert result == {"auth": "middleware"}  # Returns cached response
        assert cache.stats.hits == 1

    @patch("sentence_transformers.SentenceTransformer")
    def test_semantic_cache_miss_below_threshold(self, mock_st):
        """Test semantic cache miss when similarity below threshold."""
        mock_model = Mock()
        mock_st.return_value = mock_model

        # Mock embeddings (70% similar - below 95% threshold)
        embedding1 = np.array([1.0, 0.0, 0.0])
        embedding2 = np.array([0.7, 0.714, 0.0])  # ~70% cosine similarity

        def encode_side_effect(text, **kwargs):
            if text == "prompt1":
                return embedding1
            elif text == "prompt2":
                return embedding2
            return np.random.rand(3)

        mock_model.encode.side_effect = encode_side_effect

        cache = HybridCache(similarity_threshold=0.95)

        # Store
        cache.put("code-review", "scan", "prompt1", "sonnet", {"id": 1})

        # Try to retrieve (similarity too low)
        result = cache.get("code-review", "scan", "prompt2", "sonnet")

        assert result is None
        assert cache.stats.misses == 1

    @patch("sentence_transformers.SentenceTransformer")
    def test_semantic_only_matches_same_workflow_stage_model(self, mock_st):
        """Test that semantic cache only matches same workflow/stage/model."""
        mock_model = Mock()
        mock_st.return_value = mock_model

        # Mock highly similar embeddings
        similar_embedding = np.array([1.0, 0.0, 0.0])
        mock_model.encode.return_value = similar_embedding

        cache = HybridCache(similarity_threshold=0.90)

        # Store in workflow A
        cache.put("code-review", "scan", "prompt", "sonnet", {"workflow": "A"})

        # Try different workflow (should miss even if embeddings match)
        result = cache.get("security-audit", "scan", "prompt", "sonnet")
        assert result is None

        # Try different stage
        result = cache.get("code-review", "classify", "prompt", "sonnet")
        assert result is None

        # Try different model
        result = cache.get("code-review", "scan", "prompt", "gpt-4")
        assert result is None

    @patch("sentence_transformers.SentenceTransformer")
    def test_semantic_hit_adds_to_hash_cache(self, mock_st):
        """Test that semantic hits are added to hash cache for future fast lookups."""
        mock_model = Mock()
        mock_st.return_value = mock_model

        # Mock similar embeddings
        embedding = np.array([1.0, 0.0, 0.0])
        mock_model.encode.return_value = embedding

        cache = HybridCache(similarity_threshold=0.90)

        # Store original
        cache.put("code-review", "scan", "prompt1", "sonnet", {"id": 1})

        # First lookup (semantic hit, slow)
        result1 = cache.get("code-review", "scan", "prompt2", "sonnet")
        assert result1 == {"id": 1}

        # Second lookup of same prompt (should now be hash hit, fast)
        result2 = cache.get("code-review", "scan", "prompt2", "sonnet")
        assert result2 == {"id": 1}
        assert cache.stats.hits == 2

    @patch("sentence_transformers.SentenceTransformer")
    def test_ttl_expiration(self, mock_st):
        """Test TTL expiration in hybrid cache."""
        mock_model = Mock()
        mock_st.return_value = mock_model

        cache = HybridCache(default_ttl=1)

        # Store
        cache.put("code-review", "scan", "prompt", "sonnet", {"result": "ok"})

        # Immediate retrieval works
        assert cache.get("code-review", "scan", "prompt", "sonnet") is not None

        # Wait for expiration
        time.sleep(1.1)

        # Should miss
        assert cache.get("code-review", "scan", "prompt", "sonnet") is None

    @patch("sentence_transformers.SentenceTransformer")
    def test_clear_both_caches(self, mock_st):
        """Test clearing both hash and semantic caches."""
        mock_model = Mock()
        mock_st.return_value = mock_model
        mock_model.encode.return_value = np.array([1.0, 0.0, 0.0])

        cache = HybridCache()

        # Add entries
        cache.put("code-review", "scan", "prompt1", "sonnet", {"id": 1})
        cache.put("code-review", "scan", "prompt2", "sonnet", {"id": 2})

        # Clear
        cache.clear()

        # Both caches should be empty
        assert len(cache._hash_cache) == 0
        assert len(cache._semantic_cache) == 0

    @patch("sentence_transformers.SentenceTransformer")
    def test_lru_eviction_both_caches(self, mock_st):
        """Test LRU eviction removes from both caches."""
        mock_model = Mock()
        mock_st.return_value = mock_model
        mock_model.encode.return_value = np.array([1.0, 0.0, 0.0])

        cache = HybridCache(max_memory_mb=0.01)

        # Add many entries
        for i in range(200):
            cache.put("code-review", "scan", f"prompt{i}", "sonnet", {"id": i})

        # Should have evicted some
        assert cache.stats.evictions > 0
        assert len(cache._hash_cache) < 200
        assert len(cache._semantic_cache) < 200

    @patch("sentence_transformers.SentenceTransformer")
    def test_size_info(self, mock_st):
        """Test cache size information."""
        mock_model = Mock()
        mock_st.return_value = mock_model
        mock_model.encode.return_value = np.array([1.0, 0.0, 0.0])

        cache = HybridCache(similarity_threshold=0.95)

        # Add entries
        for i in range(10):
            cache.put("code-review", "scan", f"prompt{i}", "sonnet", {"id": i})

        info = cache.size_info()
        assert info["hash_entries"] == 10
        assert info["semantic_entries"] == 10
        assert info["model"] == "all-MiniLM-L6-v2"
        assert info["threshold"] == 0.95

    def test_cosine_similarity(self):
        """Test cosine similarity calculation."""
        a = np.array([1.0, 0.0, 0.0])
        b = np.array([1.0, 0.0, 0.0])
        assert cosine_similarity(a, b) == pytest.approx(1.0)

        a = np.array([1.0, 0.0, 0.0])
        b = np.array([0.0, 1.0, 0.0])
        assert cosine_similarity(a, b) == pytest.approx(0.0)

        a = np.array([1.0, 1.0, 0.0])
        b = np.array([1.0, 1.0, 0.0])
        assert cosine_similarity(a, b) == pytest.approx(1.0)

    @patch("sentence_transformers.SentenceTransformer")
    def test_model_load_failure_graceful_degradation(self, mock_st):
        """Test graceful degradation if model fails to load."""
        # Mock model load failure
        mock_st.side_effect = Exception("Model load failed")

        cache = HybridCache()

        # Model should be None
        assert cache._model is None

        # Hash cache should still work
        cache.put("code-review", "scan", "prompt", "sonnet", {"result": "ok"})
        result = cache.get("code-review", "scan", "prompt", "sonnet")
        assert result == {"result": "ok"}
