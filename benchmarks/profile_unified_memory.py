"""Memory profiling for UnifiedMemory (src/attune/memory/unified.py)

Run with:
    python -m memory_profiler benchmarks/profile_unified_memory.py

Or for line-by-line profiling:
    mprof run benchmarks/profile_unified_memory.py
    mprof plot  # View graph
"""

import json
import os
import sys
import tempfile
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

# Force mock mode for testing (no Redis required)
os.environ["EMPATHY_REDIS_MOCK"] = "true"
os.environ["EMPATHY_ENV"] = "development"

from memory_profiler import profile

# Create test data directory
TEST_DIR = tempfile.mkdtemp(prefix="empathy_profile_")


def create_test_patterns(storage_dir: str, count: int = 100) -> None:
    """Create test pattern files for profiling."""
    patterns_dir = Path(storage_dir)
    patterns_dir.mkdir(parents=True, exist_ok=True)

    for i in range(count):
        pattern = {
            "pattern_id": f"pattern_{i:04d}",
            "pattern_type": "test_pattern" if i % 2 == 0 else "algorithm",
            "content": f"Test pattern content {i}. " * 50,  # ~1KB per pattern
            "classification": "PUBLIC",
            "metadata": {
                "created_by": "profiler",
                "index": i,
                "tags": [f"tag_{j}" for j in range(10)],
            }
        }
        pattern_file = patterns_dir / f"pattern_{i:04d}.json"
        with pattern_file.open("w") as f:
            json.dump(pattern, f)


@profile
def profile_initialization():
    """Profile UnifiedMemory initialization."""
    from attune.memory.unified import Environment, MemoryConfig, UnifiedMemory

    config = MemoryConfig(
        environment=Environment.DEVELOPMENT,
        redis_mock=True,
        storage_dir=TEST_DIR,
        encryption_enabled=False,
        claude_memory_enabled=False,
    )

    memory = UnifiedMemory(user_id="profiler@test.com", config=config)
    return memory


@profile
def profile_stash_retrieve(memory):
    """Profile short-term memory stash and retrieve operations."""
    # Stash 100 items
    for i in range(100):
        data = {
            "key": f"item_{i}",
            "value": "x" * 1000,  # 1KB per item
            "metadata": {"index": i}
        }
        memory.stash(f"test_key_{i}", data)

    # Retrieve 100 items
    results = []
    for i in range(100):
        result = memory.retrieve(f"test_key_{i}")
        if result:
            results.append(result)

    return len(results)


@profile
def profile_persist_pattern(memory):
    """Profile long-term memory persist operations."""
    results = []
    for i in range(20):
        result = memory.persist_pattern(
            content=f"Algorithm pattern {i}: " + "x" * 500,
            pattern_type="algorithm",
            classification="PUBLIC",
            metadata={"index": i, "tags": ["profiling", "test"]},
        )
        if result:
            results.append(result)

    return results


@profile
def profile_search_patterns(memory):
    """Profile pattern search operations."""
    # Create test patterns first
    create_test_patterns(TEST_DIR, count=500)

    # Search with different queries
    results = []

    # Search 1: By pattern type
    r1 = memory.search_patterns(pattern_type="test_pattern", limit=50)
    results.append(("by_type", len(r1)))

    # Search 2: By query
    r2 = memory.search_patterns(query="content", limit=50)
    results.append(("by_query", len(r2)))

    # Search 3: Combined filters
    r3 = memory.search_patterns(
        query="pattern",
        pattern_type="algorithm",
        limit=100
    )
    results.append(("combined", len(r3)))

    return results


@profile
def profile_get_all_patterns(memory):
    """Profile _get_all_patterns (full scan operation)."""
    # This is the potentially expensive operation
    patterns = memory._get_all_patterns()
    return len(patterns)


@profile
def profile_iter_all_patterns(memory):
    """Profile _iter_all_patterns (memory-efficient generator)."""
    # Count patterns without loading all into memory
    count = 0
    for pattern in memory._iter_all_patterns():
        count += 1
    return count


@profile
def profile_recall_with_cache(memory, pattern_ids):
    """Profile recall_pattern with caching enabled."""
    results = []

    # First pass: populate cache
    for pid in pattern_ids[:10]:
        result = memory.recall_pattern(pid, use_cache=True)
        if result:
            results.append(result)

    # Second pass: should hit cache
    for pid in pattern_ids[:10]:
        result = memory.recall_pattern(pid, use_cache=True)
        if result:
            results.append(result)

    return len(results)


@profile
def profile_promote_pattern(memory):
    """Profile pattern promotion (short-term -> long-term)."""
    # Stage patterns
    staged_ids = []
    for i in range(10):
        staged_id = memory.stage_pattern(
            pattern_data={
                "name": f"Staged Pattern {i}",
                "description": f"Test staged pattern {i}",
                "content": "Promotion test content " * 20,
                "confidence": 0.9,
            },
            pattern_type="staged_test",
        )
        if staged_id:
            staged_ids.append(staged_id)

    # Promote first 5 patterns
    promoted = []
    for staged_id in staged_ids[:5]:
        result = memory.promote_pattern(staged_id)
        if result:
            promoted.append(result)

    return len(promoted)


def run_all_profiles():
    """Run all profiling tests."""
    print("=" * 70)
    print("MEMORY PROFILING: UnifiedMemory (with optimizations)")
    print("=" * 70)
    print(f"\nTest storage directory: {TEST_DIR}")
    print("\n" + "-" * 70)

    # 1. Profile initialization
    print("\n[1/8] Profiling initialization...")
    memory = profile_initialization()

    # 2. Profile stash/retrieve
    print("\n[2/8] Profiling stash/retrieve...")
    count = profile_stash_retrieve(memory)
    print(f"    Retrieved {count} items")

    # 3. Profile persist_pattern
    print("\n[3/8] Profiling persist_pattern...")
    persisted = profile_persist_pattern(memory)
    print(f"    Persisted {len(persisted)} patterns")

    # 4. Profile search_patterns (now optimized with heapq)
    print("\n[4/8] Profiling search_patterns (optimized with heapq)...")
    search_results = profile_search_patterns(memory)
    for name, count in search_results:
        print(f"    {name}: {count} results")

    # 5. Profile _get_all_patterns (loads all into memory)
    print("\n[5/8] Profiling _get_all_patterns (list version)...")
    total = profile_get_all_patterns(memory)
    print(f"    Loaded {total} patterns into list")

    # 6. Profile _iter_all_patterns (memory-efficient generator)
    print("\n[6/8] Profiling _iter_all_patterns (generator version)...")
    total_iter = profile_iter_all_patterns(memory)
    print(f"    Iterated {total_iter} patterns via generator")

    # 7. Profile recall_pattern with caching
    print("\n[7/8] Profiling recall_pattern with LRU cache...")
    # Get some pattern IDs to test with
    pattern_ids = [f"pat_{i:04d}" for i in range(20)]
    cached_count = profile_recall_with_cache(memory, pattern_ids)
    print(f"    Recalled {cached_count} patterns (with cache)")

    # 8. Profile promote_pattern
    print("\n[8/8] Profiling promote_pattern...")
    promoted = profile_promote_pattern(memory)
    print(f"    Promoted {promoted} patterns")

    print("\n" + "=" * 70)
    print("PROFILING COMPLETE")
    print("=" * 70)
    print(f"\nResults saved to: {TEST_DIR}")
    print("\nFor memory timeline graph, run:")
    print("  mprof run benchmarks/profile_unified_memory.py")
    print("  mprof plot")


if __name__ == "__main__":
    run_all_profiles()
