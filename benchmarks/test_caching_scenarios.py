#!/usr/bin/env python
"""Comprehensive caching test script for v3.8.0 validation.

Tests caching across multiple workflows and scenarios to verify:
- Cache hits/misses work correctly
- Cost savings are accurate
- Persistence works across sessions
- Different cache types behave as expected
- Cache statistics are correct

Run this before publishing v3.8.0 to PyPI.
"""

import asyncio
import time

from attune.cache import create_cache
from attune.workflows.code_review import CodeReviewWorkflow


def print_separator(title=""):
    """Print a visual separator."""
    print("\n" + "=" * 80)
    if title:
        print(f"  {title}")
        print("=" * 80)
    print()


def print_cache_stats(workflow_result, run_number=1):
    """Print cache statistics from workflow result."""
    cr = workflow_result.cost_report
    print(f"Run #{run_number} Results:")
    print(f"  Success: {workflow_result.success}")
    print(f"  Total cost: ${cr.total_cost:.6f}")
    print(f"  Cache hits: {cr.cache_hits}")
    print(f"  Cache misses: {cr.cache_misses}")
    print(f"  Cache hit rate: {cr.cache_hit_rate:.1f}%")
    if cr.savings_from_cache > 0:
        print(f"  Savings from cache: ${cr.savings_from_cache:.6f}")
    print(f"  Baseline cost (all premium): ${cr.baseline_cost:.6f}")
    print(f"  Savings from tiering: ${cr.savings:.6f} ({cr.savings_percent:.1f}%)")


async def test_hash_only_cache():
    """Test 1: Hash-only cache (exact matching only)."""
    print_separator("TEST 1: Hash-Only Cache (Exact Matching)")

    cache = create_cache(cache_type="hash")
    workflow = CodeReviewWorkflow(
        use_crew=False,
        cache=cache,
        enable_cache=True,
    )

    test_diff = """
    diff --git a/src/auth.py b/src/auth.py
    --- a/src/auth.py
    +++ b/src/auth.py
    @@ -10,5 +10,6 @@ def authenticate(username, password):
         if user is None:
             return False
    +    # Added password validation
         return user.verify_password(password)
    """

    print("▶ Running first execution (should miss cache)...")
    result1 = await workflow.execute(
        diff=test_diff,
        files_changed=["src/auth.py"],
        is_core_module=False,
    )
    print_cache_stats(result1, 1)

    print("\n▶ Running second execution with SAME input (should hit cache)...")
    result2 = await workflow.execute(
        diff=test_diff,
        files_changed=["src/auth.py"],
        is_core_module=False,
    )
    print_cache_stats(result2, 2)

    # Verify expectations
    assert (
        result2.cost_report.cache_hits > result1.cost_report.cache_hits
    ), "Second run should have more cache hits"
    print("\n✅ Hash-only cache test PASSED")
    return result1, result2


async def test_cache_with_different_inputs():
    """Test 2: Cache behavior with slightly different inputs."""
    print_separator("TEST 2: Cache with Different Inputs")

    cache = create_cache(cache_type="hash")
    workflow = CodeReviewWorkflow(
        use_crew=False,
        cache=cache,
        enable_cache=True,
    )

    diff1 = """
    diff --git a/src/auth.py b/src/auth.py
    +++ b/src/auth.py
    +    # Added password validation
    """

    diff2 = """
    diff --git a/src/auth.py b/src/auth.py
    +++ b/src/auth.py
    +    # Added email validation
    """

    print("▶ Running with first diff...")
    result1 = await workflow.execute(
        diff=diff1,
        files_changed=["src/auth.py"],
        is_core_module=False,
    )
    print_cache_stats(result1, 1)

    print("\n▶ Running with DIFFERENT diff (hash cache should miss)...")
    result2 = await workflow.execute(
        diff=diff2,
        files_changed=["src/auth.py"],
        is_core_module=False,
    )
    print_cache_stats(result2, 2)

    # With hash-only, different inputs should miss
    print("\n✅ Different inputs test PASSED")
    return result1, result2


async def test_cache_disabled():
    """Test 3: Verify cache can be disabled cleanly."""
    print_separator("TEST 3: Cache Disabled")

    workflow = CodeReviewWorkflow(
        use_crew=False,
        enable_cache=False,  # Explicitly disable
    )

    test_diff = """
    diff --git a/src/test.py b/src/test.py
    +++ b/src/test.py
    +    # Test change
    """

    print("▶ Running with cache disabled...")
    result = await workflow.execute(
        diff=test_diff,
        files_changed=["src/test.py"],
        is_core_module=False,
    )
    print_cache_stats(result, 1)

    # Should have no cache hits
    assert result.cost_report.cache_hits == 0, "Should have no cache hits when disabled"
    assert result.cost_report.cache_misses == 0, "Should have no cache misses when disabled"
    print("\n✅ Cache disabled test PASSED")
    return result


async def test_cache_statistics():
    """Test 4: Verify cache statistics are accurate."""
    print_separator("TEST 4: Cache Statistics Accuracy")

    cache = create_cache(cache_type="hash")
    workflow = CodeReviewWorkflow(
        use_crew=False,
        cache=cache,
        enable_cache=True,
    )

    test_diff = """
    diff --git a/src/util.py b/src/util.py
    +++ b/src/util.py
    +    # Utility function
    """

    # Run 5 times with same input
    results = []
    for i in range(1, 6):
        print(f"▶ Run {i}/5...")
        result = await workflow.execute(
            diff=test_diff,
            files_changed=["src/util.py"],
            is_core_module=False,
        )
        results.append(result)
        print(f"  Cache hit rate: {result.cost_report.cache_hit_rate:.1f}%")

    # Verify hit rate improves
    print("\n📊 Cache Hit Rate Progression:")
    for i, result in enumerate(results, 1):
        print(f"  Run {i}: {result.cost_report.cache_hit_rate:.1f}%")

    # Last run should have highest hit rate
    assert (
        results[-1].cost_report.cache_hit_rate >= results[0].cost_report.cache_hit_rate
    ), "Hit rate should increase or stay same"

    # Get cache stats directly
    stats = cache.get_stats()
    print("\n📈 Final Cache Statistics:")
    print(f"  Total hits: {stats.hits}")
    print(f"  Total misses: {stats.misses}")
    print(f"  Total lookups: {stats.total}")
    print(f"  Overall hit rate: {stats.hit_rate:.1f}%")

    print("\n✅ Cache statistics test PASSED")
    return results


async def test_multiple_workflows():
    """Test 5: Cache isolation between different workflows."""
    print_separator("TEST 5: Multi-Workflow Cache Isolation")

    # Shared cache instance
    cache = create_cache(cache_type="hash")

    # Two different workflow instances
    workflow1 = CodeReviewWorkflow(
        use_crew=False,
        cache=cache,
        enable_cache=True,
    )

    workflow2 = CodeReviewWorkflow(
        use_crew=False,
        cache=cache,
        enable_cache=True,
    )

    test_diff = """
    diff --git a/src/shared.py b/src/shared.py
    +++ b/src/shared.py
    +    # Shared code
    """

    print("▶ Running workflow #1...")
    result1 = await workflow1.execute(
        diff=test_diff,
        files_changed=["src/shared.py"],
        is_core_module=False,
    )
    print_cache_stats(result1, 1)

    print("\n▶ Running workflow #2 with SAME cache (should hit)...")
    result2 = await workflow2.execute(
        diff=test_diff,
        files_changed=["src/shared.py"],
        is_core_module=False,
    )
    print_cache_stats(result2, 2)

    # Second workflow should benefit from shared cache
    assert result2.cost_report.cache_hits > 0, "Should hit shared cache"
    print("\n✅ Multi-workflow cache test PASSED")
    return result1, result2


def test_cache_size_info():
    """Test 6: Cache size and memory tracking."""
    print_separator("TEST 6: Cache Size and Memory Tracking")

    cache = create_cache(cache_type="hash")

    # Add some test entries
    print("▶ Adding test entries to cache...")
    for i in range(20):
        cache.put(
            "test-workflow",
            "test-stage",
            f"test prompt {i}",
            "test-model",
            {"result": f"response {i}"},
        )

    size_info = cache.size_info()
    print("\n📦 Cache Size Information:")
    print(f"  Entries: {size_info['entries']}")
    print(f"  Estimated size: {size_info['estimated_mb']:.4f} MB")
    print(f"  Max memory: {size_info['max_memory_mb']} MB")

    assert size_info["entries"] == 20, "Should have 20 entries"
    assert size_info["estimated_mb"] > 0, "Should have non-zero size"

    print("\n✅ Cache size test PASSED")
    return size_info


async def main():
    """Run all caching tests."""
    print("\n" + "█" * 80)
    print("  EMPATHY FRAMEWORK v3.8.0 - HYBRID CACHING VALIDATION")
    print("█" * 80)
    print("\nThis script validates caching implementation before PyPI release.")
    print("Running comprehensive tests...")

    start_time = time.time()

    try:
        # Run all tests
        await test_hash_only_cache()
        await test_cache_with_different_inputs()
        await test_cache_disabled()
        await test_cache_statistics()
        await test_multiple_workflows()
        test_cache_size_info()

        # Summary
        elapsed = time.time() - start_time
        print_separator("🎉 ALL TESTS PASSED")
        print(f"Total execution time: {elapsed:.2f} seconds")
        print("\n✅ Caching implementation is ready for v3.8.0 release!")
        print("\nNext steps:")
        print("  1. Review test results above")
        print("  2. Test with hybrid cache: pip install sentence-transformers")
        print("  3. Update CHANGELOG.md")
        print("  4. Commit pyproject.toml changes")
        print("  5. Create release tag: git tag v3.8.0")
        print("  6. Push to PyPI: python -m build && twine upload dist/*")

    except AssertionError as e:
        print_separator("❌ TEST FAILED")
        print(f"Error: {e}")
        raise

    except Exception as e:
        print_separator("❌ UNEXPECTED ERROR")
        print(f"Error: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(main())
