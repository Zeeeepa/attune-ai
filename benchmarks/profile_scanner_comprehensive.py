"""Comprehensive profiling of ProjectScanner - CPU and Memory analysis.

This script profiles the project scanner running on the Empathy Framework codebase,
measuring both execution time and memory usage to identify optimization opportunities.

Usage:
    python benchmarks/profile_scanner_comprehensive.py

Requirements:
    pip install memory_profiler

Copyright 2025 Smart-AI-Memory
Licensed under Fair Source License 0.9
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "src"))

import cProfile  # noqa: E402
import io  # noqa: E402
import pstats  # noqa: E402


def clear_caches():
    """Clear LRU caches to ensure fresh profiling."""
    from empathy_os.project_index.scanner import ProjectScanner

    # Clear cached functions
    if hasattr(ProjectScanner._hash_file, 'cache_clear'):
        ProjectScanner._hash_file.cache_clear()
    if hasattr(ProjectScanner._parse_python_cached, 'cache_clear'):
        ProjectScanner._parse_python_cached.cache_clear()


def profile_scanner_cpu():
    """Profile CPU time for scanner operations."""
    from empathy_os.project_index.scanner import ProjectScanner

    print("\n" + "=" * 70)
    print("CPU PROFILING - Project Scanner")
    print("=" * 70)

    # Clear caches for fresh run
    clear_caches()

    # Profile with cProfile
    profiler = cProfile.Profile()
    profiler.enable()

    # Run scanner
    scanner = ProjectScanner(project_root=".")
    records, summary = scanner.scan()

    profiler.disable()

    # Save profile data
    Path("benchmarks/profiles").mkdir(parents=True, exist_ok=True)
    profiler.dump_stats("benchmarks/profiles/scanner_cpu.prof")

    # Print stats
    s = io.StringIO()
    stats = pstats.Stats(profiler, stream=s)
    stats.sort_stats("cumulative")

    print("\n📊 TOP 20 FUNCTIONS BY CUMULATIVE TIME:\n")
    stats.print_stats(20)
    print(s.getvalue())

    print("\n📊 SCAN RESULTS:")
    print(f"  Total files: {summary.total_files:,}")
    print(f"  Source files: {summary.source_files:,}")
    print(f"  Test files: {summary.test_files:,}")
    print(f"  Lines of code: {summary.total_lines_of_code:,}")
    print(f"  Lines of test: {summary.total_lines_of_test:,}")
    print(f"  Test coverage: {summary.test_coverage_avg:.1f}%")

    print("\n💾 Profile saved to: benchmarks/profiles/scanner_cpu.prof")
    print("   Visualize with: snakeviz benchmarks/profiles/scanner_cpu.prof")

    return summary


def profile_scanner_memory():
    """Profile memory usage for scanner operations."""
    try:
        from memory_profiler import memory_usage
    except ImportError:
        print("\n⚠️  memory_profiler not installed")
        print("   Install with: pip install memory_profiler")
        return None

    from empathy_os.project_index.scanner import ProjectScanner

    print("\n" + "=" * 70)
    print("MEMORY PROFILING - Project Scanner")
    print("=" * 70)

    # Clear caches for fresh run
    clear_caches()

    # Profile memory usage
    def run_scanner():
        scanner = ProjectScanner(project_root=".")
        records, summary = scanner.scan()
        return summary

    print("\n⏳ Running memory profiler (this may take a moment)...\n")

    mem_usage = memory_usage(
        run_scanner,
        interval=0.1,
        timeout=None,
        max_usage=True,
        retval=True,
        include_children=True
    )

    if isinstance(mem_usage, tuple):
        max_memory, summary = mem_usage
    else:
        max_memory = max(mem_usage) if isinstance(mem_usage, list) else mem_usage
        summary = None

    print("📊 MEMORY USAGE:")
    print(f"  Peak memory: {max_memory:.2f} MB")

    if summary:
        files_per_mb = summary.total_files / max_memory if max_memory > 0 else 0
        print(f"  Files/MB: {files_per_mb:.1f}")
        print(f"  Memory per 1000 files: {1000 / files_per_mb:.2f} MB" if files_per_mb > 0 else "  N/A")

    return max_memory


def profile_cache_effectiveness():
    """Profile cache hit rates and performance impact."""
    import time

    from empathy_os.project_index.scanner import ProjectScanner

    print("\n" + "=" * 70)
    print("CACHE EFFECTIVENESS ANALYSIS")
    print("=" * 70)

    # First run (cold cache)
    clear_caches()

    print("\n⏱️  First scan (cold cache)...")
    start = time.perf_counter()
    scanner1 = ProjectScanner(project_root=".")
    records1, summary1 = scanner1.scan()
    cold_time = time.perf_counter() - start

    print(f"  Time: {cold_time:.4f}s")
    print(f"  Files: {summary1.total_files:,}")

    # Second run (warm cache)
    print("\n⏱️  Second scan (warm cache)...")
    start = time.perf_counter()
    scanner2 = ProjectScanner(project_root=".")
    records2, summary2 = scanner2.scan()
    warm_time = time.perf_counter() - start

    print(f"  Time: {warm_time:.4f}s")
    print(f"  Files: {summary2.total_files:,}")

    # Calculate improvement
    if cold_time > 0:
        speedup = cold_time / warm_time if warm_time > 0 else float("inf")
        improvement = ((cold_time - warm_time) / cold_time * 100) if cold_time > 0 else 0

        print("\n📈 CACHE PERFORMANCE:")
        print(f"  Cold cache time: {cold_time:.4f}s")
        print(f"  Warm cache time: {warm_time:.4f}s")
        print(f"  Speedup: {speedup:.2f}x")
        print(f"  Improvement: {improvement:.1f}%")

        # Estimate cache hit rate
        # If caching is effective, we should see significant speedup
        if speedup > 1.5:
            print(f"\n✅ Cache is effective! {speedup:.1f}x faster with warm cache")
        elif speedup > 1.1:
            print(f"\n⚠️  Cache provides moderate benefit ({speedup:.1f}x speedup)")
        else:
            print("\n❌ Cache may not be effective or files changed between runs")


def analyze_hotspots():
    """Analyze profiling results to identify optimization opportunities."""
    print("\n" + "=" * 70)
    print("HOTSPOT ANALYSIS")
    print("=" * 70)

    # Load profile data
    stats = pstats.Stats("benchmarks/profiles/scanner_cpu.prof")

    # Get top functions by cumulative time
    print("\n🔥 TOP HOTSPOTS (by cumulative time):\n")

    # Sort by cumulative time
    stats.sort_stats("cumulative")

    # Print top 10 with analysis
    s = io.StringIO()
    stats.stream = s
    stats.print_stats(10)

    output = s.getvalue()
    lines = output.split('\n')

    # Parse and analyze
    for line in lines:
        if 'scanner.py' in line or 'models.py' in line:
            print(f"  {line}")

    print("\n💡 OPTIMIZATION RECOMMENDATIONS:")
    print("\n1. File I/O Optimization:")
    print("   - Consider async file reading for large codebases")
    print("   - Implement file content caching with modification time tracking")

    print("\n2. AST Parsing Optimization:")
    print("   - Cache parsed ASTs with file hash invalidation")
    print("   - Skip parsing for non-Python files early")

    print("\n3. Pattern Matching Optimization:")
    print("   - Pre-compile regex patterns (already done)")
    print("   - Use frozenset for O(1) membership testing (already done)")

    print("\n4. Memory Optimization:")
    print("   - Use generators for large file lists")
    print("   - Consider streaming processing for very large codebases")


def generate_report(cpu_summary, mem_usage):
    """Generate comprehensive profiling report."""
    print("\n" + "=" * 70)
    print("COMPREHENSIVE PROFILING REPORT")
    print("=" * 70)

    if cpu_summary:
        print("\n📁 CODEBASE METRICS:")
        print(f"  Total files scanned: {cpu_summary.total_files:,}")
        print(f"  Source files: {cpu_summary.source_files:,}")
        print(f"  Test files: {cpu_summary.test_files:,}")
        print(f"  Test coverage: {cpu_summary.test_coverage_avg:.1f}%")
        print(f"  Lines of code: {cpu_summary.total_lines_of_code:,}")
        print(f"  Lines of test: {cpu_summary.total_lines_of_test:,}")

        # Calculate rates
        print("\n⚡ PERFORMANCE METRICS:")
        # These will be populated from profiling
        print("  See CPU and memory profiling sections above for detailed metrics")

    print("\n📊 PROFILING ARTIFACTS:")
    print("  CPU Profile: benchmarks/profiles/scanner_cpu.prof")
    print("  Visualize: snakeviz benchmarks/profiles/scanner_cpu.prof")

    if mem_usage:
        print("\n💾 MEMORY EFFICIENCY:")
        print(f"  Peak memory: {mem_usage:.2f} MB")
        if cpu_summary:
            mb_per_file = mem_usage / cpu_summary.total_files if cpu_summary.total_files > 0 else 0
            print(f"  Memory per file: {mb_per_file * 1024:.2f} KB")

    print("\n✅ NEXT STEPS:")
    print("1. Review snakeviz visualization to identify top bottlenecks")
    print("2. Focus on functions with >10% cumulative time")
    print("3. Consider implementing recommended optimizations")
    print("4. Re-run profiling after optimizations to measure impact")


def main():
    """Run comprehensive profiling suite."""
    print("\n" + "=" * 70)
    print("COMPREHENSIVE SCANNER PROFILING")
    print("Empathy Framework - Project Scanner Performance Analysis")
    print("=" * 70)

    try:
        # CPU profiling
        cpu_summary = profile_scanner_cpu()

        # Memory profiling
        mem_usage = profile_scanner_memory()

        # Cache effectiveness
        profile_cache_effectiveness()

        # Hotspot analysis
        analyze_hotspots()

        # Final report
        generate_report(cpu_summary, mem_usage)

        print("\n" + "=" * 70)
        print("✅ PROFILING COMPLETE")
        print("=" * 70)

    except Exception as e:
        print(f"\n❌ Error during profiling: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
