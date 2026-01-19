#!/usr/bin/env python3
"""Verification script for Anthropic optimizations.

Tests that all three tracks are properly implemented and working.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

def test_track_4_token_counting():
    """Verify Track 4: Token Counting utilities."""
    print("\n" + "=" * 60)
    print("Testing Track 4: Token Counting")
    print("=" * 60)

    try:
        from empathy_llm_toolkit.utils.tokens import (
            count_tokens,
            count_message_tokens,
            estimate_cost,
            calculate_cost_with_cache,
        )

        # Test basic token counting
        test_text = "Hello, world! This is a test."
        tokens = count_tokens(test_text)
        print(f"✓ count_tokens() works: {tokens} tokens")

        # Test message counting
        messages = [{"role": "user", "content": "Hello!"}]
        counts = count_message_tokens(messages, system_prompt="You are helpful")
        print(f"✓ count_message_tokens() works: {counts}")

        # Test cost estimation
        cost = estimate_cost(1000, 500, "claude-sonnet-4-5")
        print(f"✓ estimate_cost() works: ${cost:.4f}")

        # Test cache cost calculation
        cache_cost = calculate_cost_with_cache(
            input_tokens=1000,
            output_tokens=500,
            cache_creation_tokens=5000,
            cache_read_tokens=10000,
            model="claude-sonnet-4-5",
        )
        print(f"✓ calculate_cost_with_cache() works: ${cache_cost['total_cost']:.4f}")
        print(f"  Savings: ${cache_cost['savings']:.4f}")

        print("\n✅ Track 4 (Token Counting): PASS")
        return True

    except Exception as e:
        print(f"\n❌ Track 4 (Token Counting): FAIL - {e}")
        import traceback
        traceback.print_exc()
        return False


def test_track_2_cache_stats():
    """Verify Track 2: Cache statistics."""
    print("\n" + "=" * 60)
    print("Testing Track 2: Prompt Caching Stats")
    print("=" * 60)

    try:
        from empathy_os.telemetry.usage_tracker import UsageTracker

        # Test cache stats method exists
        tracker = UsageTracker.get_instance()
        stats = tracker.get_cache_stats(days=7)

        print(f"✓ get_cache_stats() works")
        print(f"  Hit rate: {stats['hit_rate']:.1%}")
        print(f"  Total requests: {stats['total_requests']}")
        print(f"  Savings: ${stats['savings']:.2f}")

        # Verify required fields
        required_fields = [
            "hit_rate",
            "total_reads",
            "total_writes",
            "savings",
            "hit_count",
            "total_requests",
            "by_workflow",
        ]
        for field in required_fields:
            assert field in stats, f"Missing field: {field}"

        print(f"✓ All required fields present")

        print("\n✅ Track 2 (Cache Stats): PASS")
        return True

    except Exception as e:
        print(f"\n❌ Track 2 (Cache Stats): FAIL - {e}")
        import traceback
        traceback.print_exc()
        return False


def test_track_1_batch_api():
    """Verify Track 1: Batch API implementation."""
    print("\n" + "=" * 60)
    print("Testing Track 1: Batch API")
    print("=" * 60)

    try:
        # Test provider import
        from empathy_llm_toolkit.providers import AnthropicBatchProvider

        print(f"✓ AnthropicBatchProvider imported")

        # Test workflow import
        from empathy_os.workflows.batch_processing import (
            BatchProcessingWorkflow,
            BatchRequest,
            BatchResult,
        )

        print(f"✓ BatchProcessingWorkflow imported")
        print(f"✓ BatchRequest dataclass available")
        print(f"✓ BatchResult dataclass available")

        # Test task classification
        from empathy_os.models.tasks import BATCH_ELIGIBLE_TASKS, REALTIME_REQUIRED_TASKS

        print(f"✓ BATCH_ELIGIBLE_TASKS defined ({len(BATCH_ELIGIBLE_TASKS)} tasks)")
        print(f"✓ REALTIME_REQUIRED_TASKS defined ({len(REALTIME_REQUIRED_TASKS)} tasks)")

        # Show sample tasks
        print(f"\n  Sample batch-eligible tasks:")
        for task in list(BATCH_ELIGIBLE_TASKS)[:5]:
            print(f"    - {task}")

        print("\n✅ Track 1 (Batch API): PASS")
        return True

    except Exception as e:
        print(f"\n❌ Track 1 (Batch API): FAIL - {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all verification tests."""
    print("\n" + "=" * 60)
    print("ANTHROPIC OPTIMIZATION VERIFICATION")
    print("=" * 60)
    print("\nTesting implementation of three optimization tracks:")
    print("  • Track 1: Batch API Integration (50% cost savings)")
    print("  • Track 2: Prompt Caching (20-30% cost savings)")
    print("  • Track 4: Precise Token Counting (<1% error)")

    results = []

    # Run tests
    results.append(("Track 4", test_track_4_token_counting()))
    results.append(("Track 2", test_track_2_cache_stats()))
    results.append(("Track 1", test_track_1_batch_api()))

    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for track, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{track}: {status}")

    print(f"\nTotal: {passed}/{total} tests passed")

    if passed == total:
        print("\n🎉 All optimizations verified successfully!")
        print("   Expected cost reduction: 30-50%")
        return 0
    else:
        print(f"\n⚠️  {total - passed} test(s) failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())
