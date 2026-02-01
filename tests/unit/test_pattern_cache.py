"""Tests for attune.pattern_cache"""

from attune.pattern_cache import PatternMatchCache, cached_pattern_query


class TestPatternMatchCache:
    """Tests for PatternMatchCache class."""

    def test_initialization(self):
        """Test PatternMatchCache initialization."""
        cache = PatternMatchCache(max_size=100)

        assert cache is not None
        assert cache.max_size == 100
        assert isinstance(cache._cache, dict)
        assert isinstance(cache._access_order, list)
        assert len(cache._cache) == 0
        assert len(cache._access_order) == 0

    def test_get_miss(self):
        """Test get returns None on cache miss."""
        cache = PatternMatchCache()

        context = {"domain": "testing", "language": "python"}
        result = cache.get(context)

        assert result is None

    def test_set_and_get(self):
        """Test setting and getting cached values."""
        cache = PatternMatchCache()

        context = {"domain": "testing", "language": "python"}
        expected_result = ["pattern1", "pattern2"]

        # Set value
        cache.set(context, expected_result)

        # Verify cache size
        assert len(cache._cache) == 1

        # Get value
        result = cache.get(context)

        assert result == expected_result
        assert result is expected_result  # Same object

    def test_cache_key_consistency(self):
        """Test that same context produces same cache key."""
        cache = PatternMatchCache()

        # Different order but same content
        context1 = {"language": "python", "domain": "testing"}
        context2 = {"domain": "testing", "language": "python"}

        result = ["pattern1"]

        cache.set(context1, result)
        cached = cache.get(context2)

        # Should get same result (keys are identical due to sort_keys=True)
        assert cached == result

    def test_lru_eviction(self):
        """Test LRU eviction when cache is full."""
        cache = PatternMatchCache(max_size=3)

        # Fill cache
        cache.set({"id": 1}, "result1")
        cache.set({"id": 2}, "result2")
        cache.set({"id": 3}, "result3")

        assert len(cache._cache) == 3

        # Add one more - should evict oldest (id=1)
        cache.set({"id": 4}, "result4")

        assert len(cache._cache) == 3
        assert cache.get({"id": 1}) is None  # Evicted
        assert cache.get({"id": 2}) == "result2"
        assert cache.get({"id": 3}) == "result3"
        assert cache.get({"id": 4}) == "result4"

    def test_lru_access_order(self):
        """Test that accessing an item moves it to end of LRU."""
        cache = PatternMatchCache(max_size=3)

        cache.set({"id": 1}, "result1")
        cache.set({"id": 2}, "result2")
        cache.set({"id": 3}, "result3")

        # Access id=1 (moves to end)
        cache.get({"id": 1})

        # Add id=4 - should evict id=2 (now oldest)
        cache.set({"id": 4}, "result4")

        assert cache.get({"id": 1}) == "result1"  # Still there
        assert cache.get({"id": 2}) is None  # Evicted
        assert cache.get({"id": 3}) == "result3"
        assert cache.get({"id": 4}) == "result4"

    def test_clear(self):
        """Test clearing cache."""
        cache = PatternMatchCache()

        # Add some items
        cache.set({"id": 1}, "result1")
        cache.set({"id": 2}, "result2")

        assert len(cache._cache) == 2

        # Clear
        cache.clear()

        assert len(cache._cache) == 0
        assert len(cache._access_order) == 0
        assert cache.get({"id": 1}) is None
        assert cache.get({"id": 2}) is None

    def test_get_or_compute_cache_hit(self):
        """Test get_or_compute returns cached value on hit."""
        cache = PatternMatchCache()

        context = {"domain": "testing"}
        expected = ["pattern1"]

        # Prime cache
        cache.set(context, expected)

        # Compute function should NOT be called
        compute_called = False

        def compute():
            nonlocal compute_called
            compute_called = True
            return ["pattern2"]

        result = cache.get_or_compute(context, compute)

        assert result == expected
        assert not compute_called  # Should use cached value

    def test_get_or_compute_cache_miss(self):
        """Test get_or_compute computes and caches on miss."""
        cache = PatternMatchCache()

        context = {"domain": "testing"}

        # Compute function SHOULD be called
        compute_called = False
        expected = ["pattern1"]

        def compute():
            nonlocal compute_called
            compute_called = True
            return expected

        result = cache.get_or_compute(context, compute)

        assert result == expected
        assert compute_called

        # Verify cached for next time
        result2 = cache.get(context)
        assert result2 == expected

    def test_update_existing_key(self):
        """Test updating existing cache key."""
        cache = PatternMatchCache()

        context = {"id": 1}

        # Set initial value
        cache.set(context, "result1")
        assert cache.get(context) == "result1"

        # Update value
        cache.set(context, "result2")
        assert cache.get(context) == "result2"

        # Should still only have 1 entry
        assert len(cache._cache) == 1


def test_cached_pattern_query_decorator():
    """Test cached_pattern_query decorator."""
    cache = PatternMatchCache()

    # Track how many times function is called
    call_count = 0

    class MockQueryClass:
        @cached_pattern_query(cache)
        def query_patterns(self, context, min_confidence=0.5):
            nonlocal call_count
            call_count += 1
            return [f"pattern_{context['id']}"]

    obj = MockQueryClass()

    context = {"id": 1}

    # First call - should execute function
    result1 = obj.query_patterns(context, min_confidence=0.5)
    assert result1 == ["pattern_1"]
    assert call_count == 1

    # Second call with same args - should use cache
    result2 = obj.query_patterns(context, min_confidence=0.5)
    assert result2 == ["pattern_1"]
    assert call_count == 1  # Not called again

    # Different kwargs - should execute again
    result3 = obj.query_patterns(context, min_confidence=0.8)
    assert result3 == ["pattern_1"]
    assert call_count == 2  # Called again


def test_cached_pattern_query_with_different_contexts():
    """Test decorator caches different contexts separately."""
    cache = PatternMatchCache()

    class MockQueryClass:
        @cached_pattern_query(cache)
        def query_patterns(self, context):
            return [f"pattern_{context['id']}"]

    obj = MockQueryClass()

    result1 = obj.query_patterns({"id": 1})
    result2 = obj.query_patterns({"id": 2})
    result3 = obj.query_patterns({"id": 1})  # Same as first

    assert result1 == ["pattern_1"]
    assert result2 == ["pattern_2"]
    assert result3 == ["pattern_1"]

    # All three results should be cached
    assert len(cache._cache) == 2  # Two unique contexts
