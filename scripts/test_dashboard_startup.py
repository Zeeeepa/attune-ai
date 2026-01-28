#!/usr/bin/env python3
"""Quick test to verify dashboard starts correctly."""
import sys
import threading
import time
import urllib.request
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from empathy_os.dashboard import run_simple_dashboard


def start_server():
    """Start dashboard server."""
    run_simple_dashboard(host='127.0.0.1', port=8888)


def test_server():
    """Test server is responding."""
    # Start server in background
    server_thread = threading.Thread(target=start_server, daemon=True)
    server_thread.start()

    # Give server time to start
    time.sleep(1.5)

    # Test API endpoints
    endpoints = [
        '/api/health',
        '/api/agents',
    ]

    print("=" * 60)
    print("DASHBOARD SERVER TEST")
    print("=" * 60)
    print()

    all_ok = True
    for endpoint in endpoints:
        try:
            url = f'http://127.0.0.1:8888{endpoint}'
            response = urllib.request.urlopen(url, timeout=2)
            status = response.status
            data = response.read().decode()

            if status == 200:
                print(f"✅ {endpoint}: OK (200)")
                if len(data) < 200:
                    print(f"   Response: {data}")
                else:
                    print(f"   Response: {data[:100]}...")
            else:
                print(f"⚠️  {endpoint}: Status {status}")
                all_ok = False

        except Exception as e:
            print(f"❌ {endpoint}: Error - {e}")
            all_ok = False

    print()
    print("=" * 60)
    if all_ok:
        print("✅ DASHBOARD SERVER IS WORKING CORRECTLY")
    else:
        print("⚠️  SOME ENDPOINTS FAILED")
    print("=" * 60)
    print()
    print("🚀 To start the dashboard for real:")
    print("   ./scripts/start_dashboard.sh")
    print()
    print("📊 Then open: http://localhost:8000")
    print()


if __name__ == "__main__":
    test_server()
    # Let it run for 2 more seconds to show it's serving
    time.sleep(2)
    print("\n✅ Test complete - server will shut down now")
