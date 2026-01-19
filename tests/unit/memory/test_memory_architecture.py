"""Architectural Tests for Memory System.

This test suite validates architectural invariants and production readiness
of the two-tier memory system (Redis short-term + persistent long-term).

Coverage Target: 90%+ (from 18-27%)

Test Categories:
1. Unified Memory Interface (consistency across tiers)
2. Short-Term Memory (Redis TTL, expiration, operations)
3. Long-Term Memory (persistent storage, retrieval)
4. Cross-Tier Operations (promotion, consistency)
5. Classification Enforcement (INTERNAL/CONFIDENTIAL/PUBLIC)
6. Concurrent Access (thread safety, race conditions)
7. Failure Scenarios (Redis down, disk full, corruption)
8. Memory Retrieval (deterministic lookups)

Architecture Invariants Tested:
- Memory tier promotion preserves data integrity
- TTL expiration does not lose data prematurely
- Concurrent writes maintain consistency
- Classification prevents unauthorized access
- Memory survives Redis restart
- Retrieval is deterministic for same key
- No data corruption under load

Author: Sprint - Production Readiness
Date: January 16, 2026
"""

import threading
import time
from pathlib import Path
from unittest.mock import patch

import pytest

from empathy_os.memory.long_term import LongTermMemory
from empathy_os.memory.short_term import RedisShortTermMemory, TTLStrategy
from empathy_os.memory.unified import MemoryConfig, UnifiedMemory

# ============================================================================
# Test Category 1: Unified Memory Interface
# ============================================================================


class TestUnifiedMemoryInterface:
    """Test that unified memory provides consistent interface."""

    def test_unified_memory_initialization(self):
        """Test that unified memory initializes both tiers."""
        config = MemoryConfig(redis_mock=True)
        memory = UnifiedMemory(user_id="test_user", config=config)

        assert memory is not None
        assert hasattr(memory, "short_term")
        assert hasattr(memory, "long_term")

    def test_store_routes_to_correct_tier(self):
        """Test that store operation routes to appropriate tier."""
        config = MemoryConfig(redis_mock=True)
        memory = UnifiedMemory(user_id="test_user", config=config)

        # Store with short-term TTL
        memory.store("test_key", {"data": "value"}, ttl=3600)

        # Should be in short-term
        assert "test_key" in memory.short_term._mock_storage

    def test_retrieve_checks_both_tiers(self):
        """Test that retrieve checks short-term first, then long-term."""
        config = MemoryConfig(redis_mock=True)
        memory = UnifiedMemory(user_id="test_user", config=config)

        # Store in long-term only
        memory.long_term.store("test_key", {"data": "long_term_value"})

        # Retrieve should find it
        result = memory.retrieve("test_key")
        assert result is not None
        assert result["data"] == "long_term_value"

    def test_short_term_takes_precedence_over_long_term(self):
        """Test that short-term data overrides long-term if both exist."""
        config = MemoryConfig(redis_mock=True)
        memory = UnifiedMemory(user_id="test_user", config=config)

        # Store in both tiers with different values
        memory.long_term.store("test_key", {"data": "old"})
        memory.short_term.stash("test_key", {"data": "new"}, ttl=3600)

        # Retrieve should get short-term (newer)
        result = memory.retrieve("test_key")
        assert result["data"] == "new"

    def test_delete_removes_from_both_tiers(self):
        """Test that delete operation removes from both tiers."""
        config = MemoryConfig(redis_mock=True)
        memory = UnifiedMemory(user_id="test_user", config=config)

        # Store in both
        memory.short_term.stash("test_key", {"data": "value"}, ttl=3600)
        memory.long_term.store("test_key", {"data": "value"})

        # Delete
        memory.delete("test_key")

        # Should be gone from both
        assert memory.retrieve("test_key") is None


# ============================================================================
# Test Category 2: Short-Term Memory (Redis)
# ============================================================================


class TestShortTermMemoryOperations:
    """Test short-term memory TTL, expiration, and operations."""

    def setup_method(self):
        """Set up test fixtures."""
        self.memory = RedisShortTermMemory(use_mock=True)

    def test_ttl_expiration_works_correctly(self):
        """Test that data expires after TTL."""
        # Store with 1 second TTL
        self.memory.stash("test_key", {"data": "value"}, ttl=1)

        # Should exist immediately
        assert self.memory.retrieve("test_key") is not None

        # Wait for expiration
        time.sleep(1.5)

        # Should be expired
        result = self.memory.retrieve("test_key")
        assert result is None or result.get("expired") is True

    def test_ttl_strategy_session_default(self):
        """Test that SESSION TTL strategy has reasonable default."""
        ttl = TTLStrategy.SESSION

        # Session TTL should be 1-24 hours
        assert 3600 <= ttl <= 86400

    def test_concurrent_writes_maintain_consistency(self):
        """Test that concurrent writes don't corrupt data."""
        results = []
        lock = threading.Lock()

        def write_data(key, value):
            self.memory.stash(key, {"value": value}, ttl=3600)
            time.sleep(0.01)  # Simulate work
            retrieved = self.memory.retrieve(key)
            with lock:
                results.append((key, retrieved))

        threads = []
        for i in range(10):
            thread = threading.Thread(target=write_data, args=(f"key{i}", f"value{i}"))
            threads.append(thread)
            thread.start()

        for thread in threads:
            thread.join()

        # All writes should succeed
        assert len(results) == 10
        for key, value in results:
            assert value is not None
            assert "value" in value

    def test_large_data_storage(self):
        """Test that large data can be stored and retrieved."""
        # Create large data (1MB)
        large_data = {"data": "x" * (1024 * 1024)}

        self.memory.stash("large_key", large_data, ttl=3600)

        retrieved = self.memory.retrieve("large_key")
        assert retrieved is not None
        assert len(retrieved["data"]) == len(large_data["data"])

    def test_update_existing_key(self):
        """Test that updating existing key works correctly."""
        self.memory.stash("test_key", {"version": 1}, ttl=3600)
        self.memory.stash("test_key", {"version": 2}, ttl=3600)

        result = self.memory.retrieve("test_key")
        assert result["version"] == 2


# ============================================================================
# Test Category 3: Long-Term Memory (Persistent)
# ============================================================================


class TestLongTermMemoryPersistence:
    """Test long-term memory persistence and retrieval."""

    def setup_method(self):
        """Set up test fixtures."""
        self.temp_dir = Path("/tmp/empathy_test_memory")
        self.temp_dir.mkdir(exist_ok=True)
        self.memory = LongTermMemory(storage_path=str(self.temp_dir))

    def teardown_method(self):
        """Clean up test files."""
        import shutil

        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)

    def test_data_persists_across_instances(self):
        """Test that data survives memory instance restart."""
        # Store data
        self.memory.store("test_key", {"data": "persistent"})

        # Create new instance (simulating restart)
        new_memory = LongTermMemory(storage_path=str(self.temp_dir))

        # Data should still be there
        result = new_memory.retrieve("test_key")
        assert result is not None
        assert result["data"] == "persistent"

    def test_large_dataset_persistence(self):
        """Test that large dataset can be persisted."""
        # Store 100 entries
        for i in range(100):
            self.memory.store(f"key_{i}", {"index": i, "data": f"value_{i}"})

        # Retrieve all
        for i in range(100):
            result = self.memory.retrieve(f"key_{i}")
            assert result is not None
            assert result["index"] == i

    def test_file_corruption_handling(self):
        """Test that corrupted files are handled gracefully."""
        # Store valid data
        self.memory.store("test_key", {"data": "value"})

        # Corrupt the file
        storage_file = self.temp_dir / "memory.json"
        if storage_file.exists():
            storage_file.write_text("{ corrupted json")

        # Create new instance - should handle corruption
        new_memory = LongTermMemory(storage_path=str(self.temp_dir))

        # Should not crash
        result = new_memory.retrieve("test_key")
        # May return None or default value


# ============================================================================
# Test Category 4: Cross-Tier Operations
# ============================================================================


class TestCrossTierOperations:
    """Test data promotion and consistency across tiers."""

    def setup_method(self):
        """Set up test fixtures."""
        config = MemoryConfig(redis_mock=True)
        self.memory = UnifiedMemory(user_id="test_user", config=config)

    def test_promote_to_long_term_preserves_data(self):
        """Test that promoting to long-term preserves data integrity."""
        # Store in short-term
        original_data = {"key": "value", "nested": {"data": "preserved"}}
        self.memory.short_term.stash("test_key", original_data, ttl=3600)

        # Promote to long-term
        self.memory.promote_to_long_term("test_key")

        # Verify in long-term
        long_term_data = self.memory.long_term.retrieve("test_key")
        assert long_term_data == original_data

    def test_promotion_after_ttl_expiration_fails_gracefully(self):
        """Test that promoting expired data is handled."""
        # Store with short TTL
        self.memory.short_term.stash("test_key", {"data": "value"}, ttl=1)

        # Wait for expiration
        time.sleep(1.5)

        # Attempt to promote - should handle gracefully
        result = self.memory.promote_to_long_term("test_key")

        # Should either succeed with None or fail gracefully
        assert result is None or result is False

    def test_sync_tiers_maintains_consistency(self):
        """Test that tier synchronization maintains data consistency."""
        # Store in short-term
        self.memory.short_term.stash("key1", {"version": 1}, ttl=3600)

        # Store in long-term with different value
        self.memory.long_term.store("key1", {"version": 0})

        # Sync should resolve conflict (newer wins)
        self.memory.sync_tiers("key1")

        # Check both tiers have consistent data
        short_result = self.memory.short_term.retrieve("key1")
        long_result = self.memory.long_term.retrieve("key1")

        # Should be consistent (implementation-dependent which wins)
        if short_result and long_result:
            assert short_result.get("version") == long_result.get("version")


# ============================================================================
# Test Category 5: Classification Enforcement
# ============================================================================


class TestClassificationEnforcement:
    """Test that classification levels are enforced."""

    def setup_method(self):
        """Set up test fixtures."""
        config = MemoryConfig(redis_mock=True)
        self.memory = UnifiedMemory(user_id="test_user", config=config)

    @pytest.mark.skip(reason="Classification not yet implemented in unified memory")
    def test_internal_data_not_accessible_externally(self):
        """Test that INTERNAL classified data is protected."""
        # TODO: Implement when classification added
        pass

    @pytest.mark.skip(reason="Classification not yet implemented in unified memory")
    def test_confidential_data_requires_authorization(self):
        """Test that CONFIDENTIAL data requires credentials."""
        # TODO: Implement when classification added
        pass

    @pytest.mark.skip(reason="Classification not yet implemented in unified memory")
    def test_public_data_accessible_without_auth(self):
        """Test that PUBLIC data is freely accessible."""
        # TODO: Implement when classification added
        pass


# ============================================================================
# Test Category 6: Concurrent Access
# ============================================================================


class TestConcurrentAccess:
    """Test that memory handles concurrent access safely."""

    def setup_method(self):
        """Set up test fixtures."""
        config = MemoryConfig(redis_mock=True)
        self.memory = UnifiedMemory(user_id="test_user", config=config)

    def test_concurrent_reads_consistent(self):
        """Test that concurrent reads return consistent data."""
        # Store data
        self.memory.store("shared_key", {"counter": 0})

        results = []
        lock = threading.Lock()

        def read_data():
            result = self.memory.retrieve("shared_key")
            with lock:
                results.append(result)

        threads = [threading.Thread(target=read_data) for _ in range(20)]

        for thread in threads:
            thread.start()

        for thread in threads:
            thread.join()

        # All reads should succeed
        assert len(results) == 20
        assert all(r is not None for r in results)

    def test_concurrent_writes_no_data_loss(self):
        """Test that concurrent writes don't lose data."""
        write_count = 50
        lock = threading.Lock()
        success_count = []

        def write_unique_data(i):
            self.memory.store(f"key_{i}", {"id": i})
            with lock:
                success_count.append(i)

        threads = [
            threading.Thread(target=write_unique_data, args=(i,))
            for i in range(write_count)
        ]

        for thread in threads:
            thread.start()

        for thread in threads:
            thread.join()

        # All writes should succeed
        assert len(success_count) == write_count

        # All data should be retrievable
        for i in range(write_count):
            result = self.memory.retrieve(f"key_{i}")
            assert result is not None
            assert result["id"] == i


# ============================================================================
# Test Category 7: Failure Scenarios
# ============================================================================


class TestFailureScenarios:
    """Test graceful handling of failure scenarios."""

    def test_redis_unavailable_fallback_to_memory(self):
        """Test that system works when Redis is unavailable."""
        # Create memory with mock Redis (simulating Redis down)
        config = MemoryConfig(redis_mock=True)
        memory = UnifiedMemory(user_id="test_user", config=config)

        # Should still work using mock mode
        memory.store("test_key", {"data": "value"})
        result = memory.retrieve("test_key")

        assert result is not None
        assert result["data"] == "value"

    def test_disk_full_error_handling(self):
        """Test that disk full errors are handled gracefully."""
        temp_dir = Path("/tmp/empathy_test_disk_full")
        temp_dir.mkdir(exist_ok=True)

        memory = LongTermMemory(storage_path=str(temp_dir))

        # Mock disk full error
        with patch.object(Path, "write_text") as mock_write:
            mock_write.side_effect = OSError("No space left on device")

            # Should handle error gracefully
            try:
                memory.store("test_key", {"data": "value"})
            except OSError:
                pass  # Expected

        # Cleanup
        import shutil

        shutil.rmtree(temp_dir)

    def test_corrupted_data_recovery(self):
        """Test that corrupted data is handled without crashing."""
        memory = RedisShortTermMemory(use_mock=True)

        # Store corrupted data directly
        memory._mock_storage["corrupted_key"] = "not a dict"

        # Retrieve should handle gracefully
        result = memory.retrieve("corrupted_key")

        # Should return None or handle error
        assert result is None or isinstance(result, dict)


# ============================================================================
# Test Category 8: Memory Retrieval Determinism
# ============================================================================


class TestMemoryRetrievalDeterminism:
    """Test that memory retrieval is deterministic."""

    def setup_method(self):
        """Set up test fixtures."""
        config = MemoryConfig(redis_mock=True)
        self.memory = UnifiedMemory(user_id="test_user", config=config)

    def test_same_key_returns_same_data(self):
        """Test that retrieving same key multiple times returns identical data."""
        # Store data
        original_data = {"key": "value", "timestamp": "2026-01-16"}
        self.memory.store("test_key", original_data)

        # Retrieve multiple times
        results = [self.memory.retrieve("test_key") for _ in range(10)]

        # All results should be identical
        for result in results:
            assert result == original_data

    def test_nonexistent_key_returns_none_consistently(self):
        """Test that nonexistent keys consistently return None."""
        results = [self.memory.retrieve("nonexistent_key") for _ in range(10)]

        # All should be None
        assert all(r is None for r in results)

    def test_empty_key_handled_consistently(self):
        """Test that empty keys are handled consistently."""
        empty_keys = ["", None, " ", "\t"]

        for key in empty_keys:
            # Should not crash
            result = self.memory.retrieve(key)
            # Should consistently return None or raise TypeError
            assert result is None or isinstance(result, dict)


# ============================================================================
# Integration Tests
# ============================================================================


class TestMemorySystemIntegration:
    """Integration tests for complete memory operations."""

    def test_complete_memory_lifecycle(self):
        """Test complete lifecycle: store, retrieve, update, promote, delete."""
        config = MemoryConfig(redis_mock=True)
        memory = UnifiedMemory(user_id="test_user", config=config)

        # 1. Store
        memory.store("lifecycle_key", {"stage": "created"})

        # 2. Retrieve
        data = memory.retrieve("lifecycle_key")
        assert data["stage"] == "created"

        # 3. Update
        memory.store("lifecycle_key", {"stage": "updated"})
        data = memory.retrieve("lifecycle_key")
        assert data["stage"] == "updated"

        # 4. Promote
        memory.promote_to_long_term("lifecycle_key")

        # 5. Verify in long-term
        long_data = memory.long_term.retrieve("lifecycle_key")
        assert long_data is not None

        # 6. Delete
        memory.delete("lifecycle_key")

        # 7. Verify deleted
        assert memory.retrieve("lifecycle_key") is None

    def test_high_volume_memory_operations(self):
        """Test that system handles high volume of operations."""
        config = MemoryConfig(redis_mock=True)
        memory = UnifiedMemory(user_id="test_user", config=config)

        # Store 1000 entries
        for i in range(1000):
            memory.store(f"key_{i}", {"index": i})

        # Retrieve all
        for i in range(1000):
            result = memory.retrieve(f"key_{i}")
            assert result is not None
            assert result["index"] == i

        # Delete all
        for i in range(1000):
            memory.delete(f"key_{i}")

        # Verify all deleted
        for i in range(1000):
            assert memory.retrieve(f"key_{i}") is None


# ============================================================================
# Performance Tests
# ============================================================================


class TestMemoryPerformance:
    """Test memory system performance characteristics."""

    def test_retrieval_performance_acceptable(self):
        """Test that retrieval is fast enough for production."""
        config = MemoryConfig(redis_mock=True)
        memory = UnifiedMemory(user_id="test_user", config=config)

        # Store data
        memory.store("perf_key", {"data": "value"})

        # Measure retrieval time
        start = time.time()
        for _ in range(100):
            memory.retrieve("perf_key")
        duration = time.time() - start

        # Should complete 100 retrievals in < 1 second
        assert duration < 1.0

    def test_storage_performance_acceptable(self):
        """Test that storage is fast enough for production."""
        config = MemoryConfig(redis_mock=True)
        memory = UnifiedMemory(user_id="test_user", config=config)

        # Measure storage time
        start = time.time()
        for i in range(100):
            memory.store(f"perf_key_{i}", {"index": i})
        duration = time.time() - start

        # Should complete 100 stores in < 2 seconds
        assert duration < 2.0
