"""Comprehensive benchmark comparing scanner optimization strategies.

Compares three implementations:
1. Original (baseline)
2. Optimized (Priority 1: skip AST for tests, optional dependencies)
3. Parallel (multi-core processing)

Usage:
    python benchmarks/benchmark_scanner_optimizations.py

Copyright 2025 Smart-AI-Memory
Licensed under Fair Source License 0.9
"""

import sys
import time
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "src"))

from attune.project_index.scanner import ProjectScanner  # noqa: E402
from attune.project_index.scanner_parallel import ParallelProjectScanner  # noqa: E402


def clear_all_caches():
    """Clear LRU caches for fair benchmarking."""
    # Clear scanner caches
    if hasattr(ProjectScanner._hash_file, "cache_clear"):
        ProjectScanner._hash_file.cache_clear()
    if hasattr(ProjectScanner._parse_python_cached, "cache_clear"):
        ProjectScanner._parse_python_cached.cache_clear()


def benchmark_baseline(iterations: int = 1) -> dict:
    """Benchmark baseline scanner (with dependencies).

    Args:
        iterations: Number of times to run (default: 1)

    Returns:
        Dictionary with timing and file count results
    """
    print("\n" + "=" * 70)
    print("BENCHMARK 1: Baseline Scanner (Original)")
    print("=" * 70)

    times = []
    summary = None

    for i in range(iterations):
        clear_all_caches()

        print(f"\nRun {i + 1}/{iterations}...")
        start = time.perf_counter()

        scanner = ProjectScanner(project_root=".")
        records, summary = scanner.scan(analyze_dependencies=True)

        duration = time.perf_counter() - start
        times.append(duration)

        print(f"  Time: {duration:.4f}s")
        print(f"  Files: {summary.total_files:,}")
        print(f"  Source: {summary.source_files:,}")
        print(f"  Tests: {summary.test_files:,}")

    avg_time = sum(times) / len(times)

    return {
        "name": "Baseline (with dependencies)",
        "avg_time": avg_time,
        "times": times,
        "files": summary.total_files if summary else 0,
    }


def benchmark_optimized_skip_ast(iterations: int = 1) -> dict:
    """Benchmark optimized scanner (skip AST for tests).

    Args:
        iterations: Number of times to run (default: 1)

    Returns:
        Dictionary with timing and file count results
    """
    print("\n" + "=" * 70)
    print("BENCHMARK 2: Optimized Scanner (Skip AST for Tests)")
    print("=" * 70)

    times = []
    summary = None

    for i in range(iterations):
        clear_all_caches()

        print(f"\nRun {i + 1}/{iterations}...")
        start = time.perf_counter()

        # The optimization is now built-in - just scan normally
        scanner = ProjectScanner(project_root=".")
        records, summary = scanner.scan(analyze_dependencies=True)

        duration = time.perf_counter() - start
        times.append(duration)

        print(f"  Time: {duration:.4f}s")
        print(f"  Files: {summary.total_files:,}")

    avg_time = sum(times) / len(times)

    return {
        "name": "Optimized (skip AST for tests)",
        "avg_time": avg_time,
        "times": times,
        "files": summary.total_files if summary else 0,
    }


def benchmark_optimized_no_deps(iterations: int = 1) -> dict:
    """Benchmark optimized scanner without dependency analysis.

    Args:
        iterations: Number of times to run (default: 1)

    Returns:
        Dictionary with timing and file count results
    """
    print("\n" + "=" * 70)
    print("BENCHMARK 3: Optimized Scanner (No Dependencies)")
    print("=" * 70)

    times = []
    summary = None

    for i in range(iterations):
        clear_all_caches()

        print(f"\nRun {i + 1}/{iterations}...")
        start = time.perf_counter()

        scanner = ProjectScanner(project_root=".")
        records, summary = scanner.scan(analyze_dependencies=False)

        duration = time.perf_counter() - start
        times.append(duration)

        print(f"  Time: {duration:.4f}s")
        print(f"  Files: {summary.total_files:,}")

    avg_time = sum(times) / len(times)

    return {
        "name": "Optimized (no dependencies)",
        "avg_time": avg_time,
        "times": times,
        "files": summary.total_files if summary else 0,
    }


def benchmark_parallel(workers: int = 4, iterations: int = 1) -> dict:
    """Benchmark parallel scanner.

    Args:
        workers: Number of worker processes
        iterations: Number of times to run (default: 1)

    Returns:
        Dictionary with timing and file count results
    """
    print("\n" + "=" * 70)
    print(f"BENCHMARK 4: Parallel Scanner ({workers} workers)")
    print("=" * 70)

    times = []
    summary = None

    for i in range(iterations):
        clear_all_caches()

        print(f"\nRun {i + 1}/{iterations}...")
        start = time.perf_counter()

        scanner = ParallelProjectScanner(project_root=".", workers=workers)
        records, summary = scanner.scan(analyze_dependencies=True)

        duration = time.perf_counter() - start
        times.append(duration)

        print(f"  Time: {duration:.4f}s")
        print(f"  Files: {summary.total_files:,}")

    avg_time = sum(times) / len(times)

    return {
        "name": f"Parallel ({workers} workers)",
        "avg_time": avg_time,
        "times": times,
        "files": summary.total_files if summary else 0,
        "workers": workers,
    }


def benchmark_parallel_no_deps(workers: int = 4, iterations: int = 1) -> dict:
    """Benchmark parallel scanner without dependency analysis.

    Args:
        workers: Number of worker processes
        iterations: Number of times to run (default: 1)

    Returns:
        Dictionary with timing and file count results
    """
    print("\n" + "=" * 70)
    print(f"BENCHMARK 5: Parallel Scanner ({workers} workers, No Dependencies)")
    print("=" * 70)

    times = []
    summary = None

    for i in range(iterations):
        clear_all_caches()

        print(f"\nRun {i + 1}/{iterations}...")
        start = time.perf_counter()

        scanner = ParallelProjectScanner(project_root=".", workers=workers)
        records, summary = scanner.scan(analyze_dependencies=False)

        duration = time.perf_counter() - start
        times.append(duration)

        print(f"  Time: {duration:.4f}s")
        print(f"  Files: {summary.total_files:,}")

    avg_time = sum(times) / len(times)

    return {
        "name": f"Parallel ({workers} workers, no deps)",
        "avg_time": avg_time,
        "times": times,
        "files": summary.total_files if summary else 0,
        "workers": workers,
    }


def print_comparison_table(results: list[dict]):
    """Print comparison table of all benchmark results.

    Args:
        results: List of benchmark result dictionaries
    """
    print("\n" + "=" * 70)
    print("COMPREHENSIVE COMPARISON")
    print("=" * 70)

    # Find baseline for speedup calculation
    baseline = results[0]["avg_time"]

    print("\n| Implementation | Time (s) | Speedup | Files | Notes |")
    print("|----------------|----------|---------|-------|-------|")

    for result in results:
        time_val = result["avg_time"]
        speedup = baseline / time_val if time_val > 0 else 0
        files = result["files"]
        name = result["name"]

        # Determine notes
        notes = ""
        if speedup >= 3.0:
            notes = "🚀 Excellent"
        elif speedup >= 2.0:
            notes = "✅ Great"
        elif speedup >= 1.5:
            notes = "👍 Good"
        elif speedup >= 1.1:
            notes = "⚡ Moderate"
        else:
            notes = "Baseline"

        print(f"| {name:30s} | {time_val:8.4f} | {speedup:7.2f}x | {files:5,} | {notes} |")

    print("\n" + "=" * 70)


def print_recommendations(results: list[dict]):
    """Print optimization recommendations based on benchmark results.

    Args:
        results: List of benchmark result dictionaries
    """
    print("\n" + "=" * 70)
    print("OPTIMIZATION RECOMMENDATIONS")
    print("=" * 70)

    baseline_time = results[0]["avg_time"]
    best_result = min(results, key=lambda r: r["avg_time"])
    best_speedup = baseline_time / best_result["avg_time"]

    print(f"\n🏆 Best configuration: {best_result['name']}")
    print(f"   Time: {best_result['avg_time']:.4f}s")
    print(f"   Speedup: {best_speedup:.2f}x")
    print(
        f"   Improvement: {((baseline_time - best_result['avg_time']) / baseline_time * 100):.1f}%"
    )

    print("\n💡 Recommendations by use case:")

    print("\n1. **Interactive Development** (quick scans, frequent runs):")
    print("   Use: Optimized scanner without dependencies")
    print("   Reason: Fastest for quick file analysis")

    print("\n2. **CI/CD** (thorough analysis, one-time scans):")
    print("   Use: Parallel scanner with all features")
    print("   Reason: Most thorough, worth the extra time")

    print("\n3. **Large Codebases** (>10,000 files):")
    print("   Use: Parallel scanner with dependencies")
    print("   Reason: Scales well with file count")

    print("\n4. **Small Codebases** (<1,000 files):")
    print("   Use: Optimized sequential scanner")
    print("   Reason: Parallel overhead not worth it")

    # Calculate optimal worker count
    parallel_results = [r for r in results if "workers" in r]
    if parallel_results:
        best_parallel = min(parallel_results, key=lambda r: r["avg_time"])
        print(f"\n5. **Optimal Worker Count:** {best_parallel.get('workers', 'N/A')}")
        print(f"   On this machine ({best_parallel.get('workers', 'N/A')} cores)")


def main():
    """Run comprehensive benchmark suite."""
    print("=" * 70)
    print("SCANNER OPTIMIZATION BENCHMARK SUITE")
    print("Empathy Framework - Project Scanner Performance Analysis")
    print("=" * 70)

    import multiprocessing as mp

    cpu_count = mp.cpu_count()
    print("\n📊 System Information:")
    print(f"   CPU cores: {cpu_count}")
    print(f"   Python: {sys.version.split()[0]}")
    print(f"   Project root: {project_root}")

    # Run all benchmarks
    iterations = 2  # Run each benchmark twice for averaging

    results = []

    # 1. Baseline (original implementation behavior)
    # Note: The optimizations are now built-in, but we still run with all features
    results.append(benchmark_baseline(iterations=iterations))

    # 2. Optimized (skip AST for tests) - now the default behavior
    results.append(benchmark_optimized_skip_ast(iterations=iterations))

    # 3. Optimized without dependencies
    results.append(benchmark_optimized_no_deps(iterations=iterations))

    # 4. Parallel with dependencies
    results.append(benchmark_parallel(workers=cpu_count, iterations=iterations))

    # 5. Parallel without dependencies (fastest)
    results.append(benchmark_parallel_no_deps(workers=cpu_count, iterations=iterations))

    # Print comparison and recommendations
    print_comparison_table(results)
    print_recommendations(results)

    print("\n" + "=" * 70)
    print("✅ BENCHMARK COMPLETE")
    print("=" * 70)

    # Save results to JSON for later analysis
    import json

    output_file = project_root / "benchmarks" / "optimization_results.json"
    with open(output_file, "w") as f:
        json.dump(
            {
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                "cpu_count": cpu_count,
                "python_version": sys.version,
                "results": results,
            },
            f,
            indent=2,
        )

    print(f"\n📁 Results saved to: {output_file}")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Benchmark interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Error during benchmarking: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)
