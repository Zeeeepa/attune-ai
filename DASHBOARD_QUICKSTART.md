# 🚀 Dashboard Quick Start

**Everything is ready!** Redis has **679 keys** with test data.

---

## Start in 3 Commands

```bash
cd /Users/patrickroebuck/Documents/empathy1-11-2025-local/attune-ai

# 1. Start the dashboard
./scripts/start_dashboard.sh

# 2. Open browser to http://localhost:8000
```

---

## What You'll See

✅ **System Health** - Redis status (healthy/degraded)
✅ **5 Active Agents** - With progress bars and status
✅ **2 Pending Approvals** - Click to approve/reject!
✅ **10 Coordination Signals** - Agent-to-agent messages
✅ **15 Event Streams** - Real-time events
✅ **27 Quality Metrics** - Performance by tier
✅ **Auto-refresh** - Updates every 5 seconds

---

## Regenerate Test Data

If data expires (heartbeats = 60s TTL):

```bash
python scripts/populate_redis_direct.py
```

---

## Test API Endpoints

```bash
# Health check
curl http://localhost:8000/api/health | jq

# Active agents
curl http://localhost:8000/api/agents | jq

# Quality metrics
curl http://localhost:8000/api/feedback/workflows | jq
```

---

## Full Documentation

- [docs/DASHBOARD_COMPLETE.md](docs/DASHBOARD_COMPLETE.md) - Complete guide (350+ lines)
- [docs/DASHBOARD_GUIDE.md](docs/DASHBOARD_GUIDE.md) - Usage reference
- [docs/DASHBOARD_TESTING.md](docs/DASHBOARD_TESTING.md) - Testing guide

---

**Status:** ✅ Production Ready
**Dependencies:** Python stdlib + redis-py only
**No Anthropic API calls** - Dashboard is free to run!
