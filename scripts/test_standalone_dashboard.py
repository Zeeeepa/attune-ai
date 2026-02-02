#!/usr/bin/env python3
"""Test standalone dashboard server with Redis data."""
import sys
import threading
import time
import urllib.request
import json
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from attune.dashboard import run_standalone_dashboard


def start_server():
    """Start dashboard server."""
    run_standalone_dashboard(host="127.0.0.1", port=8888)


def test_endpoints():
    """Test all API endpoints with actual data."""
    # Start server in background
    server_thread = threading.Thread(target=start_server, daemon=True)
    server_thread.start()

    # Give server time to start
    time.sleep(1.5)

    print("=" * 70)
    print("STANDALONE DASHBOARD TEST - WITH REAL REDIS DATA")
    print("=" * 70)
    print()

    endpoints = [
        ("/api/health", "System Health"),
        ("/api/agents", "Active Agents"),
        ("/api/signals?limit=5", "Coordination Signals"),
        ("/api/events?limit=5", "Event Stream"),
        ("/api/approvals", "Pending Approvals"),
        ("/api/feedback/workflows", "Quality Metrics"),
        ("/api/feedback/underperforming?threshold=0.7", "Underperforming Stages"),
    ]

    all_ok = True
    for endpoint, description in endpoints:
        try:
            url = f"http://127.0.0.1:8888{endpoint}"
            response = urllib.request.urlopen(url, timeout=3)
            status = response.status
            data_raw = response.read().decode()
            data = json.loads(data_raw)

            if status == 200:
                # Count items in response
                if isinstance(data, list):
                    count = len(data)
                    print(f"✅ {description}: {count} items")
                    if count > 0 and count <= 3:
                        # Show sample data for small lists
                        print(f"   Sample: {json.dumps(data[0], indent=2)[:150]}...")
                elif isinstance(data, dict):
                    print(f"✅ {description}: {json.dumps(data, indent=2)}")
            else:
                print(f"⚠️  {description}: Status {status}")
                all_ok = False

        except Exception as e:
            print(f"❌ {description}: Error - {e}")
            all_ok = False

    print()
    print("=" * 70)
    if all_ok:
        print("✅ STANDALONE DASHBOARD IS WORKING WITH REDIS DATA!")
    else:
        print("⚠️  SOME ENDPOINTS FAILED")
    print("=" * 70)
    print()
    print("🚀 To start the dashboard:")
    print("   ./scripts/start_dashboard.sh")
    print()
    print("📊 Then open in browser:")
    print("   http://localhost:8000")
    print()


if __name__ == "__main__":
    # Check Redis has data first
    import redis

    try:
        r = redis.Redis(host="localhost", port=6379)
        key_count = r.dbsize()
        print()
        print(f"📊 Redis has {key_count} keys")
        if key_count == 0:
            print("⚠️  Warning: Redis is empty!")
            print("   Run: python scripts/populate_redis_direct.py")
            print()
        else:
            print("✅ Redis has data - proceeding with tests")
            print()
    except Exception as e:
        print(f"❌ Cannot connect to Redis: {e}")
        print("   Make sure Redis is running: redis-server")
        sys.exit(1)

    test_endpoints()

    # Let it run for a moment
    time.sleep(2)
    print("\n✅ Test complete - server will shut down now")
