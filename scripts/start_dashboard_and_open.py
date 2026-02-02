#!/usr/bin/env python3
"""Start dashboard and open browser when ready.

Improved version that:
- Polls health endpoint instead of fixed sleep
- Uses webbrowser module (cross-platform)
- Handles errors gracefully
- Tracks background process
"""

import subprocess
import sys
import time
import webbrowser
from pathlib import Path

try:
    import requests

    HAS_REQUESTS = True
except ImportError:
    # Fallback to urllib if requests not available
    import urllib.request

    HAS_REQUESTS = False


def check_health(host: str, port: int) -> bool:
    """Check if dashboard is responding."""
    url = f"http://{host}:{port}/api/health"

    try:
        if HAS_REQUESTS:
            response = requests.get(url, timeout=1)
            return response.status_code == 200
        else:
            # Fallback to urllib
            with urllib.request.urlopen(url, timeout=1) as response:
                return response.status == 200
    except Exception:
        return False


def start_dashboard_and_open(host: str = "127.0.0.1", port: int = 8000, max_wait: int = 30):
    """Start dashboard and open browser when ready.

    Args:
        host: Host to bind to
        port: Port to bind to
        max_wait: Maximum seconds to wait for dashboard to start

    Returns:
        subprocess.Popen object for the dashboard process
    """
    print("🚀 Starting Agent Coordination Dashboard...")
    print(f"📊 Will open browser when ready at http://{host}:{port}")
    print()

    # Get project root
    project_root = Path(__file__).parent.parent

    # Start dashboard in background
    cmd = [
        sys.executable,
        "-m",
        "attune.cli_minimal",
        "dashboard",
        "start",
        "--host",
        host,
        "--port",
        str(port),
    ]

    try:
        # Start process
        process = subprocess.Popen(
            cmd, cwd=project_root, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
        )

        print(f"✅ Dashboard process started (PID: {process.pid})")
        print()
        print("⏳ Waiting for dashboard to be ready...")

        # Poll health endpoint
        start_time = time.time()
        ready = False

        for attempt in range(max_wait * 2):  # Poll every 0.5s
            if check_health(host, port):
                ready = True
                elapsed = time.time() - start_time
                print(f"✅ Dashboard is ready! (took {elapsed:.1f}s)")
                print()
                break

            # Check if process died
            if process.poll() is not None:
                stdout, stderr = process.communicate()
                print("❌ Dashboard process terminated unexpectedly")
                if stderr:
                    print(f"Error: {stderr}")
                return None

            time.sleep(0.5)

            # Progress indicator
            if attempt % 4 == 0:
                print(f"   Still waiting... ({attempt//2}s)", end="\r")

        if not ready:
            print(f"\n❌ Dashboard did not start within {max_wait}s")
            print("   Check logs or try starting manually:")
            print(f"   empathy dashboard start --host {host} --port {port}")
            process.terminate()
            return None

        # Open browser
        url = f"http://{host}:{port}"
        print(f"🌐 Opening browser to {url}...")
        print()

        if webbrowser.open(url):
            print("✅ Browser opened successfully!")
        else:
            print("⚠️  Could not open browser automatically")
            print(f"   Please open manually: {url}")

        print()
        print("=" * 60)
        print("DASHBOARD RUNNING")
        print("=" * 60)
        print(f"  URL:        http://{host}:{port}")
        print(f"  Process ID: {process.pid}")
        print()
        print("To stop the dashboard:")
        print(f"  kill {process.pid}")
        print("  or")
        print(f"  pkill -f 'dashboard start'")
        print()

        return process

    except FileNotFoundError:
        print("❌ Could not find Python executable or empathy module")
        print("   Make sure you're in the project directory")
        return None
    except Exception as e:
        print(f"❌ Error starting dashboard: {e}")
        return None


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(description="Start dashboard and open browser")
    parser.add_argument("--host", default="127.0.0.1", help="Host to bind to")
    parser.add_argument("--port", type=int, default=8000, help="Port to bind to")
    parser.add_argument("--max-wait", type=int, default=30, help="Max seconds to wait")
    parser.add_argument("--no-open", action="store_true", help="Don't open browser")

    args = parser.parse_args()

    if args.no_open:
        # Just start without opening
        print("Starting dashboard without opening browser...")
        subprocess.run(
            [
                sys.executable,
                "-m",
                "attune.cli_minimal",
                "dashboard",
                "start",
                "--host",
                args.host,
                "--port",
                str(args.port),
            ]
        )
    else:
        # Start and open
        process = start_dashboard_and_open(args.host, args.port, args.max_wait)

        if process:
            # Keep script alive (or it will kill the subprocess)
            print("Press Ctrl+C to stop the dashboard...")
            try:
                process.wait()
            except KeyboardInterrupt:
                print("\n\n🛑 Stopping dashboard...")
                process.terminate()
                process.wait()
                print("✅ Dashboard stopped")


if __name__ == "__main__":
    main()
