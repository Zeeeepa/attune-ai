"""Unit tests for HashOnlyCache.

Tests exact-match hash-based caching with TTL, LRU eviction, and persistence.
"""

import time

from empathy_os.cache.hash_only import HashOnlyCache


class TestHashOnlyCache:
    """Test suite for HashOnlyCache."""

    def test_init(self):
        """Test cache initialization."""
        cache = HashOnlyCache(max_size_mb=100, default_ttl=3600)

        assert cache.max_size_mb == 100
        assert cache.max_memory_mb == 100
        assert cache.default_ttl == 3600
        assert cache.stats.hits == 0
        assert cache.stats.misses == 0

    def test_cache_miss(self):
        """Test cache miss on first lookup."""
        cache = HashOnlyCache()

        result = cache.get("code-review", "scan", "test prompt", "claude-sonnet")

        assert result is None
        assert cache.stats.misses == 1
        assert cache.stats.hits == 0

    def test_cache_hit_exact_match(self):
        """Test cache hit on exact prompt match."""
        cache = HashOnlyCache()

        # Store response
        cache.put("code-review", "scan", "test prompt", "claude-sonnet", {"result": "ok"})

        # Retrieve exact same prompt
        result = cache.get("code-review", "scan", "test prompt", "claude-sonnet")

        assert result == {"result": "ok"}
        assert cache.stats.hits == 1
        assert cache.stats.misses == 0

    def test_cache_miss_different_prompt(self):
        """Test cache miss with similar but different prompt."""
        cache = HashOnlyCache()

        # Store response
        cache.put("code-review", "scan", "test prompt", "claude-sonnet", {"result": "ok"})

        # Try slightly different prompt (should miss)
        result = cache.get("code-review", "scan", "test prompt!", "claude-sonnet")

        assert result is None
        assert cache.stats.misses == 1
        assert cache.stats.hits == 0

    def test_cache_key_includes_model(self):
        """Test that cache key includes model (different models don't share cache)."""
        cache = HashOnlyCache()

        # Store with model A
        cache.put("code-review", "scan", "test prompt", "claude-sonnet", {"model": "sonnet"})

        # Try to retrieve with model B (should miss)
        result = cache.get(
            "code-review",
            "scan",
            "test prompt",
            "gpt-4",
        )

        assert result is None
        assert cache.stats.misses == 1

    def test_cache_key_includes_workflow_and_stage(self):
        """Test that cache key includes workflow and stage."""
        cache = HashOnlyCache()

        # Store in workflow A, stage X
        cache.put("code-review", "scan", "test prompt", "sonnet", {"stage": "scan"})

        # Try different workflow (should miss)
        assert cache.get("security-audit", "scan", "test prompt", "sonnet") is None

        # Try different stage (should miss)
        assert cache.get("code-review", "classify", "test prompt", "sonnet") is None

    def test_ttl_expiration(self):
        """Test that entries expire based on TTL."""
        cache = HashOnlyCache(default_ttl=1)  # 1 second TTL

        # Store response
        cache.put("code-review", "scan", "test prompt", "sonnet", {"result": "ok"})

        # Immediate retrieval works
        assert cache.get("code-review", "scan", "test prompt", "sonnet") is not None

        # Wait for TTL to expire
        time.sleep(1.1)

        # Should now miss (expired)
        result = cache.get("code-review", "scan", "test prompt", "sonnet")
        assert result is None
        assert cache.stats.misses == 1

    def test_custom_ttl(self):
        """Test custom TTL per entry."""
        cache = HashOnlyCache(default_ttl=3600)

        # Store with custom 1-second TTL
        cache.put("code-review", "scan", "test prompt", "sonnet", {"result": "ok"}, ttl=1)

        # Wait for custom TTL to expire
        time.sleep(1.1)

        # Should miss (custom TTL expired)
        assert cache.get("code-review", "scan", "test prompt", "sonnet") is None

    def test_evict_expired(self):
        """Test manual expired entry eviction."""
        cache = HashOnlyCache(default_ttl=1)

        # Add multiple entries
        cache.put("code-review", "scan", "prompt1", "sonnet", {"id": 1})
        cache.put("code-review", "scan", "prompt2", "sonnet", {"id": 2})

        # Wait for expiration
        time.sleep(1.1)

        # Evict expired entries
        evicted = cache.evict_expired()

        assert evicted == 2
        assert cache.stats.evictions == 2

    def test_clear_cache(self):
        """Test clearing all cache entries."""
        cache = HashOnlyCache()

        # Add entries
        cache.put("code-review", "scan", "prompt1", "sonnet", {"id": 1})
        cache.put("code-review", "scan", "prompt2", "sonnet", {"id": 2})

        # Clear cache
        cache.clear()

        # Should miss after clear
        assert cache.get("code-review", "scan", "prompt1", "sonnet") is None
        assert cache.get("code-review", "scan", "prompt2", "sonnet") is None

    def test_lru_eviction(self):
        """Test LRU eviction when cache exceeds memory limit."""
        cache = HashOnlyCache(max_memory_mb=0.01)  # Very small limit

        # Add many entries to trigger eviction
        for i in range(200):
            cache.put("code-review", "scan", f"prompt{i}", "sonnet", {"id": i})

        # Should have evicted some entries
        assert cache.stats.evictions > 0
        assert len(cache._memory_cache) < 200

    def test_hit_rate_calculation(self):
        """Test cache hit rate calculation."""
        cache = HashOnlyCache()

        # Store one entry
        cache.put("code-review", "scan", "prompt", "sonnet", {"result": "ok"})

        # 3 hits, 2 misses
        cache.get("code-review", "scan", "prompt", "sonnet")  # hit
        cache.get("code-review", "scan", "prompt", "sonnet")  # hit
        cache.get("code-review", "scan", "prompt", "sonnet")  # hit
        cache.get("code-review", "scan", "other1", "sonnet")  # miss
        cache.get("code-review", "scan", "other2", "sonnet")  # miss

        stats = cache.get_stats()
        assert stats.hits == 3
        assert stats.misses == 2
        assert stats.total == 5
        assert stats.hit_rate == 60.0  # 3/5 = 60%

    def test_size_info(self):
        """Test cache size information."""
        cache = HashOnlyCache(max_memory_mb=100)

        # Add entries
        for i in range(10):
            cache.put("code-review", "scan", f"prompt{i}", "sonnet", {"id": i})

        info = cache.size_info()
        assert info["entries"] == 10
        assert info["max_memory_mb"] == 100
        assert info["estimated_mb"] > 0

    def test_access_time_tracking(self):
        """Test that access times are tracked for LRU."""
        cache = HashOnlyCache()

        # Add entry
        cache.put("code-review", "scan", "prompt", "sonnet", {"result": "ok"})

        # Access it (should update access time)
        cache.get("code-review", "scan", "prompt", "sonnet")

        # Check access time was recorded
        cache_key = cache._create_cache_key("code-review", "scan", "prompt", "sonnet")
        assert cache_key in cache._access_times
        assert cache._access_times[cache_key] > 0
