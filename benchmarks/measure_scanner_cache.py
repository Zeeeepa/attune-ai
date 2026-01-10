"""Measure Scanner Cache Performance

Runs the project scanner twice to measure cache hit rate and speedup.

Expected results:
- File hash cache: 80%+ hit rate
- AST parse cache: 90%+ hit rate
- Overall speedup: 40-60% faster on second scan

Usage:
    python benchmarks/measure_scanner_cache.py

Copyright 2025 Smart-AI-Memory
Licensed under Fair Source License 0.9
"""

import sys
import time
from functools import lru_cache
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from empathy_os.project_index.scanner import ProjectScanner


def get_cache_stats():
    """Get LRU cache statistics for scanner methods."""
    scanner = ProjectScanner(project_root=".")

    # Get cache info for both cached methods
    hash_info = scanner._hash_file.cache_info()
    parse_info = scanner._parse_python_cached.cache_info()

    return {
        "hash_cache": {
            "hits": hash_info.hits,
            "misses": hash_info.misses,
            "hit_rate": (
                hash_info.hits / (hash_info.hits + hash_info.misses) * 100
                if (hash_info.hits + hash_info.misses) > 0
                else 0
            ),
            "size": hash_info.currsize,
            "maxsize": hash_info.maxsize,
        },
        "parse_cache": {
            "hits": parse_info.hits,
            "misses": parse_info.misses,
            "hit_rate": (
                parse_info.hits / (parse_info.hits + parse_info.misses) * 100
                if (parse_info.hits + parse_info.misses) > 0
                else 0
            ),
            "size": parse_info.currsize,
            "maxsize": parse_info.maxsize,
        },
    }


def main():
    """Run scanner twice and measure cache performance."""
    print("=" * 70)
    print("SCANNER CACHE PERFORMANCE MEASUREMENT")
    print("=" * 70)
    print()

    # First scan - populates caches
    print("FIRST SCAN (Cold Cache)")
    print("-" * 70)
    scanner1 = ProjectScanner(project_root=".")

    start1 = time.perf_counter()
    records1, summary1 = scanner1.scan()
    duration1 = time.perf_counter() - start1

    print(f"✓ Scanned {summary1.total_files} files")
    print(f"✓ Source files: {summary1.source_files}")
    print(f"✓ Test files: {summary1.test_files}")
    print(f"✓ Lines of code: {summary1.total_lines_of_code:,}")
    print(f"✓ Duration: {duration1:.3f} seconds")
    print()

    # Get cache stats after first scan
    stats1 = get_cache_stats()
    print("Cache Statistics (After First Scan):")
    print(f"  File Hash Cache:")
    print(f"    - Hits: {stats1['hash_cache']['hits']}")
    print(f"    - Misses: {stats1['hash_cache']['misses']}")
    print(f"    - Hit Rate: {stats1['hash_cache']['hit_rate']:.1f}%")
    print(f"    - Size: {stats1['hash_cache']['size']}/{stats1['hash_cache']['maxsize']}")
    print(f"  AST Parse Cache:")
    print(f"    - Hits: {stats1['parse_cache']['hits']}")
    print(f"    - Misses: {stats1['parse_cache']['misses']}")
    print(f"    - Hit Rate: {stats1['parse_cache']['hit_rate']:.1f}%")
    print(f"    - Size: {stats1['parse_cache']['size']}/{stats1['parse_cache']['maxsize']}")
    print()

    # Second scan - uses caches
    print("SECOND SCAN (Warm Cache)")
    print("-" * 70)
    scanner2 = scanner1  # Reuse same scanner instance to keep caches

    start2 = time.perf_counter()
    records2, summary2 = scanner2.scan()
    duration2 = time.perf_counter() - start2

    print(f"✓ Scanned {summary2.total_files} files")
    print(f"✓ Source files: {summary2.source_files}")
    print(f"✓ Test files: {summary2.test_files}")
    print(f"✓ Lines of code: {summary2.total_lines_of_code:,}")
    print(f"✓ Duration: {duration2:.3f} seconds")
    print()

    # Get cache stats after second scan
    stats2 = get_cache_stats()
    print("Cache Statistics (After Second Scan):")
    print(f"  File Hash Cache:")
    print(f"    - Hits: {stats2['hash_cache']['hits']}")
    print(f"    - Misses: {stats2['hash_cache']['misses']}")
    print(f"    - Hit Rate: {stats2['hash_cache']['hit_rate']:.1f}%")
    print(f"    - Size: {stats2['hash_cache']['size']}/{stats2['hash_cache']['maxsize']}")
    print(f"  AST Parse Cache:")
    print(f"    - Hits: {stats2['parse_cache']['hits']}")
    print(f"    - Misses: {stats2['parse_cache']['misses']}")
    print(f"    - Hit Rate: {stats2['parse_cache']['hit_rate']:.1f}%")
    print(f"    - Size: {stats2['parse_cache']['size']}/{stats2['parse_cache']['maxsize']}")
    print()

    # Calculate improvement
    print("=" * 70)
    print("PERFORMANCE IMPROVEMENT")
    print("=" * 70)
    speedup = duration1 / duration2 if duration2 > 0 else 0
    improvement_pct = ((duration1 - duration2) / duration1 * 100) if duration1 > 0 else 0

    print(f"First scan:  {duration1:.3f} seconds")
    print(f"Second scan: {duration2:.3f} seconds")
    print(f"Speedup:     {speedup:.2f}x")
    print(f"Improvement: {improvement_pct:.1f}% faster")
    print()

    # Calculate incremental cache stats (second scan only)
    hash_hits_delta = stats2["hash_cache"]["hits"] - stats1["hash_cache"]["hits"]
    hash_misses_delta = stats2["hash_cache"]["misses"] - stats1["hash_cache"]["misses"]
    hash_hit_rate_2nd = (
        (hash_hits_delta / (hash_hits_delta + hash_misses_delta) * 100)
        if (hash_hits_delta + hash_misses_delta) > 0
        else 0
    )

    parse_hits_delta = stats2["parse_cache"]["hits"] - stats1["parse_cache"]["hits"]
    parse_misses_delta = stats2["parse_cache"]["misses"] - stats1["parse_cache"]["misses"]
    parse_hit_rate_2nd = (
        (parse_hits_delta / (parse_hits_delta + parse_misses_delta) * 100)
        if (parse_hits_delta + parse_misses_delta) > 0
        else 0
    )

    print("Cache Hit Rates (Second Scan Only):")
    print(f"  File Hash Cache: {hash_hit_rate_2nd:.1f}%")
    print(f"  AST Parse Cache: {parse_hit_rate_2nd:.1f}%")
    print()

    # Success criteria
    print("=" * 70)
    print("SUCCESS CRITERIA")
    print("=" * 70)

    hash_success = "✅" if hash_hit_rate_2nd >= 80 else "❌"
    parse_success = "✅" if parse_hit_rate_2nd >= 90 else "❌"
    speedup_success = "✅" if improvement_pct >= 40 else "❌"

    print(f"{hash_success} File Hash Cache Hit Rate: {hash_hit_rate_2nd:.1f}% (target: 80%+)")
    print(f"{parse_success} AST Parse Cache Hit Rate: {parse_hit_rate_2nd:.1f}% (target: 90%+)")
    print(f"{speedup_success} Overall Speedup: {improvement_pct:.1f}% (target: 40%+)")
    print()

    if all([hash_hit_rate_2nd >= 80, parse_hit_rate_2nd >= 90, improvement_pct >= 40]):
        print("✅ All success criteria met!")
    else:
        print("⚠️  Some targets not met - caching still provides benefit")

    print("=" * 70)


if __name__ == "__main__":
    main()
