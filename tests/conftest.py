"""Pytest configuration for Empathy Framework tests."""

import json
import os
from collections import defaultdict
from datetime import datetime
from pathlib import Path

import pytest

# Load test environment variables from .env.test
try:
    from dotenv import load_dotenv

    # Load .env.test if it exists (for local testing with mock API keys)
    test_env_path = Path(__file__).parent.parent / ".env.test"
    if test_env_path.exists():
        load_dotenv(test_env_path, override=True)
except ImportError:
    pass  # python-dotenv not installed

# =============================================================================
# File Test Tracking - Automatic per-file test result recording
# Supports both single-process and xdist parallel execution
# =============================================================================

# Global collector for test results per test file
_test_results_by_file: dict = defaultdict(
    lambda: {
        "passed": 0,
        "failed": 0,
        "skipped": 0,
        "errors": 0,
        "duration": 0.0,
        "failed_tests": [],
    }
)


def _map_test_to_source(test_file: str) -> str | None:
    """Map a test file path to its corresponding source file.

    Examples:
        tests/test_config.py -> src/empathy_os/config.py
        tests/unit/models/test_registry.py -> src/empathy_os/models/registry.py
        tests/unit/cli/test_cli_commands.py -> src/empathy_os/cli.py
    """
    test_path = Path(test_file)

    # Extract the test filename
    filename = test_path.stem  # e.g., "test_config" or "test_registry"
    if not filename.startswith("test_"):
        return None

    # Remove "test_" prefix to get source filename
    source_name = filename[5:]  # "config" or "registry" or "cli_commands"

    # Determine the module path from test location
    parts = test_path.parts

    # Handle tests/unit/<module>/test_*.py pattern
    if "unit" in parts:
        unit_idx = parts.index("unit")
        module_parts = parts[unit_idx + 1 : -1]  # Get parts between unit/ and filename

        if module_parts:
            # Try 1: Direct file in module (e.g., models/registry.py)
            source_path = Path("src/empathy_os") / "/".join(module_parts) / f"{source_name}.py"
            if source_path.exists():
                return str(source_path)

            # Try 2: Module package itself (e.g., cli.py for test_cli_commands.py)
            # Handle patterns like test_cli_commands -> cli/__init__.py or cli.py
            module_name = module_parts[0]  # e.g., "cli"
            if source_name.startswith(f"{module_name}_"):
                # test_cli_commands -> try cli.py first
                source_path = Path("src/empathy_os") / f"{module_name}.py"
                if source_path.exists():
                    return str(source_path)
                # Then try cli/__init__.py
                source_path = Path("src/empathy_os") / module_name / "__init__.py"
                if source_path.exists():
                    return str(source_path)

    # Handle tests/test_*.py pattern (direct tests)
    if "tests" in parts and parts[-1].startswith("test_"):
        # Try direct mapping to src/empathy_os/
        source_path = Path("src/empathy_os") / f"{source_name}.py"
        if source_path.exists():
            return str(source_path)

    # Fallback: search for the source file
    for candidate in Path("src").rglob(f"{source_name}.py"):
        if "__pycache__" not in str(candidate):
            return str(candidate)

    return None


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """Collect test results per test file."""
    outcome = yield
    report = outcome.get_result()

    # Only process the "call" phase (actual test execution)
    if report.when == "call":
        test_file = str(item.fspath)

        if report.passed:
            _test_results_by_file[test_file]["passed"] += 1
        elif report.failed:
            _test_results_by_file[test_file]["failed"] += 1
            # Only store first 10 failures per file to limit memory usage
            if len(_test_results_by_file[test_file]["failed_tests"]) < 10:
                # Truncate error message to prevent memory bloat
                error_msg = str(report.longrepr)[:500] if report.longrepr else "Unknown error"
                _test_results_by_file[test_file]["failed_tests"].append(
                    {
                        "name": item.name,
                        "file": test_file,
                        "error": error_msg,
                    }
                )
        elif report.skipped:
            _test_results_by_file[test_file]["skipped"] += 1

        # Track duration
        if hasattr(report, "duration"):
            _test_results_by_file[test_file]["duration"] += report.duration


# =============================================================================
# xdist Support - File-based result sharing between workers and main node
# =============================================================================

_XDIST_RESULTS_DIR = Path(".pytest_file_tracking")


def _get_worker_results_file(worker_id: str) -> Path:
    """Get the results file path for an xdist worker."""
    return _XDIST_RESULTS_DIR / f"worker_{worker_id}.json"


def _aggregate_xdist_results() -> dict:
    """Aggregate results from all xdist worker files."""
    aggregated = defaultdict(
        lambda: {
            "passed": 0,
            "failed": 0,
            "skipped": 0,
            "errors": 0,
            "duration": 0.0,
            "failed_tests": [],
        }
    )

    if not _XDIST_RESULTS_DIR.exists():
        return dict(aggregated)

    for results_file in _XDIST_RESULTS_DIR.glob("worker_*.json"):
        try:
            with open(results_file) as f:
                worker_results = json.load(f)
            for test_file, results in worker_results.items():
                aggregated[test_file]["passed"] += results.get("passed", 0)
                aggregated[test_file]["failed"] += results.get("failed", 0)
                aggregated[test_file]["skipped"] += results.get("skipped", 0)
                aggregated[test_file]["errors"] += results.get("errors", 0)
                aggregated[test_file]["duration"] += results.get("duration", 0.0)
                aggregated[test_file]["failed_tests"].extend(results.get("failed_tests", []))
            # Clean up worker file after reading
            results_file.unlink()
        except (json.JSONDecodeError, OSError):
            pass

    # Clean up directory if empty
    try:
        if _XDIST_RESULTS_DIR.exists() and not any(_XDIST_RESULTS_DIR.iterdir()):
            _XDIST_RESULTS_DIR.rmdir()
    except OSError:
        pass

    return dict(aggregated)


def pytest_sessionfinish(session, exitstatus):
    """Store file test records at end of test session."""
    # Check if this is an xdist worker
    if hasattr(session.config, "workerinput"):
        # This is a worker - write results to file for main node to collect
        if _test_results_by_file:
            worker_id = session.config.workerinput.get("workerid", "unknown")
            _XDIST_RESULTS_DIR.mkdir(exist_ok=True)
            results_file = _get_worker_results_file(worker_id)

            # Convert defaultdict to regular dict for serialization
            serializable_results = {}
            for test_file, results in _test_results_by_file.items():
                serializable_results[test_file] = dict(results)

            with open(results_file, "w") as f:
                json.dump(serializable_results, f)
        return

    # Check if tracking is enabled (can be disabled via env var)
    if os.environ.get("EMPATHY_SKIP_FILE_TRACKING", "").lower() in ("1", "true", "yes"):
        return

    # Determine which results to use:
    # - If xdist worker files exist, aggregate from them
    # - Otherwise, use local results (non-parallel execution)
    xdist_results = _aggregate_xdist_results()

    if xdist_results:
        results_to_store = xdist_results
    elif _test_results_by_file:
        results_to_store = dict(_test_results_by_file)
    else:
        return  # No results to store

    try:
        from empathy_os.models.telemetry import FileTestRecord, get_telemetry_store

        store = get_telemetry_store()
        timestamp = datetime.utcnow().isoformat() + "Z"

        for test_file, results in results_to_store.items():
            # Map test file to source file
            source_file = _map_test_to_source(test_file)
            if source_file is None:
                continue  # Skip if we can't map to source

            total = results["passed"] + results["failed"] + results["skipped"] + results["errors"]
            if total == 0:
                continue  # Skip empty results

            # Determine overall result
            if results["failed"] > 0 or results["errors"] > 0:
                last_test_result = "failed"
            elif results["passed"] > 0:
                last_test_result = "passed"
            elif results["skipped"] == total:
                last_test_result = "skipped"
            else:
                last_test_result = "no_tests"

            # Get file modification times
            source_path = Path(source_file)
            test_path = Path(test_file)

            source_modified_at = None
            tests_modified_at = None

            if source_path.exists():
                source_modified_at = (
                    datetime.fromtimestamp(source_path.stat().st_mtime).isoformat() + "Z"
                )

            if test_path.exists():
                tests_modified_at = (
                    datetime.fromtimestamp(test_path.stat().st_mtime).isoformat() + "Z"
                )

            # Check staleness
            is_stale = False
            if source_modified_at and tests_modified_at:
                is_stale = source_modified_at > tests_modified_at

            record = FileTestRecord(
                file_path=source_file,
                timestamp=timestamp,
                last_test_result=last_test_result,
                test_count=total,
                passed=results["passed"],
                failed=results["failed"],
                skipped=results["skipped"],
                errors=results["errors"],
                duration_seconds=results["duration"],
                test_file_path=test_file,
                failed_tests=results["failed_tests"],
                source_modified_at=source_modified_at,
                tests_modified_at=tests_modified_at,
                is_stale=is_stale,
            )

            store.log_file_test(record)

    except ImportError:
        # Telemetry module not available, skip tracking
        pass
    except Exception as e:
        # Don't fail tests due to tracking errors
        import sys

        print(f"\nWarning: File test tracking failed: {e}", file=sys.stderr)


def pytest_configure(config):
    """Configure pytest with custom settings."""
    # Add ini settings dynamically based on markers
    config.addinivalue_line("markers", "unit: Unit tests that import and test modules directly")
    config.addinivalue_line(
        "markers",
        "integration: Integration tests that run via subprocess (no coverage)",
    )


def pytest_collection_modifyitems(config, items):
    """Modify test collection to handle coverage properly."""
    # If running with coverage, only run unit tests unless explicitly requested
    if config.option.cov_source and not config.option.markexpr:
        skip_integration = pytest.mark.skip(reason="Integration tests don't provide coverage")
        for item in items:
            if "integration" in item.keywords:
                item.add_marker(skip_integration)


@pytest.fixture(autouse=True, scope="function")
def setup_test_environment(tmp_path, monkeypatch, request):
    """Automatically set up test environment for all tests.

    Creates necessary directories (.empathy, .claude, etc.) in the current directory.
    This prevents tests from failing due to missing directories.

    Args:
        tmp_path: pytest fixture providing a temporary directory
        monkeypatch: pytest fixture for modifying environment
        request: pytest request object

    Yields:
        Path: The current working directory with .empathy structure
    """
    # Save original working directory to restore later
    original_cwd = Path.cwd()

    # Create .empathy directory structure in current directory
    empathy_dir = original_cwd / ".empathy"
    empathy_dir.mkdir(parents=True, exist_ok=True)

    # Create subdirectories that might be needed
    (empathy_dir / "cost_tracking").mkdir(exist_ok=True)
    (empathy_dir / "telemetry").mkdir(exist_ok=True)
    (empathy_dir / "patterns").mkdir(exist_ok=True)

    # Create .claude directory if needed
    claude_dir = original_cwd / ".claude"
    claude_dir.mkdir(parents=True, exist_ok=True)

    yield original_cwd

    # Restore original working directory in case test changed it
    try:
        import os

        os.chdir(original_cwd)
    except (FileNotFoundError, OSError):
        # If original directory was deleted (e.g., by test cleanup), ignore
        pass
