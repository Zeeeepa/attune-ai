"""Launch autonomous test generation with dashboard monitoring.

Spawns multiple test generation agents that register with the dashboard.

Copyright 2026 Smart-AI-Memory
Licensed under Apache 2.0
"""

import json
import subprocess
import sys
import time
from pathlib import Path


def launch_batch(batch_num: int, modules: list[dict]) -> subprocess.Popen:
    """Launch a test generation batch as background process.

    Args:
        batch_num: Batch number
        modules: List of module dicts to process

    Returns:
        Process handle
    """
    modules_json = json.dumps(modules)

    # Launch as background process
    process = subprocess.Popen(
        [
            sys.executable,
            "-m",
            "attune.workflows.autonomous_test_gen",
            str(batch_num),
            modules_json,
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )

    print(f"✅ Launched Batch {batch_num} (PID: {process.pid})")
    return process


def main():
    """Launch all test generation batches."""
    print("="*60)
    print("Autonomous Test Generation with Dashboard Integration")
    print("="*60)
    print()

    # Load batch plan
    batch_file = Path("/tmp/coverage_batches.json")
    if not batch_file.exists():
        print(f"❌ Batch plan not found: {batch_file}")
        print("Run health check first to generate batch plan")
        sys.exit(1)

    with open(batch_file) as f:
        batches = json.load(f)

    print(f"📊 Found {len(batches)} batches to process")
    print(f"📍 Dashboard: http://localhost:8000")
    print()

    # Launch all batches
    processes = []
    for batch in batches:
        batch_num = batch["batch_num"]
        modules = batch["modules"]

        process = launch_batch(batch_num, modules)
        processes.append((batch_num, process))

        # Stagger launches by 2 seconds
        time.sleep(2)

    print()
    print(f"🚀 Launched {len(processes)} agents")
    print(f"📊 Monitor progress at: http://localhost:8000")
    print()
    print("Agents are running in background. Press Ctrl+C to stop all agents.")
    print()

    # Monitor processes
    try:
        while any(p.poll() is None for _, p in processes):
            time.sleep(5)

            # Show status
            running = sum(1 for _, p in processes if p.poll() is None)
            completed = len(processes) - running

            print(f"Status: {completed}/{len(processes)} batches complete, {running} running...")

    except KeyboardInterrupt:
        print()
        print("🛑 Stopping all agents...")
        for batch_num, process in processes:
            if process.poll() is None:
                process.terminate()
        print("All agents stopped")
        sys.exit(0)

    # All complete
    print()
    print("="*60)
    print("🎉 All batches complete!")
    print("="*60)

    # Show results
    for batch_num, process in processes:
        stdout, stderr = process.communicate()
        if process.returncode == 0:
            print(f"✅ Batch {batch_num}: Success")
        else:
            print(f"❌ Batch {batch_num}: Failed (code {process.returncode})")


if __name__ == "__main__":
    main()
