# Dashboard Testing Guide

**Status:** ✅ Ready to Test

## Quick Start

### 1. Populate Redis with Test Data (No API Required)

```bash
# Direct Redis population - bypasses all API layers
python scripts/populate_redis_direct.py
```

This creates:
- 5 agent heartbeats
- 10 coordination signals
- 15 event stream entries
- 2 pending approval requests
- 333 quality feedback samples

Total: **364 Redis keys**

### 2. Start the Dashboard

**Option A: Simple script**
```bash
./scripts/start_dashboard.sh
```

**Option B: Direct Python**
```bash
python -c "from src.attune.dashboard import run_simple_dashboard; run_simple_dashboard()"
```

**Option C: From examples (includes test data generation)**
```bash
python examples/dashboard_demo.py
```

### 3. Open in Browser

Navigate to: **http://localhost:8000**

The dashboard will show:
- ✅ System health status
- ✅ 5 active agents with heartbeats
- ✅ 10 coordination signals
- ✅ 15 stream events
- ✅ 2 pending approval requests
- ✅ Quality metrics for all workflows

## Dashboard Features

### Auto-Refresh
- Refreshes every 5 seconds automatically
- Manual refresh anytime with browser refresh (F5)

### Panels

1. **System Stats** (top bar)
   - Active agents count
   - Pending approvals count
   - Recent signals count
   - Event streams count

2. **Active Agents** (Pattern 1)
   - Agent ID and status
   - Current task
   - Progress bar
   - Color-coded status (green=running, yellow=idle)

3. **Approval Requests** (Pattern 5)
   - Approval type
   - Requesting agent
   - Context details
   - Approve/Reject buttons

4. **Quality Metrics** (Pattern 6)
   - Workflow/stage quality scores
   - Tier breakdown (cheap/capable/premium)
   - Sample counts
   - Trend indicators

5. **Recent Signals** (Pattern 2)
   - Signal type
   - Source → Target agent
   - Relative timestamps

6. **Event Stream** (Pattern 4)
   - Event type
   - Source agent
   - Relative timestamps

7. **Underperforming Stages** (Pattern 6)
   - Stages below 70% quality threshold
   - Quality ranges
   - Sample counts

## Testing Without API

The `populate_redis_direct.py` script writes directly to Redis without using any of the telemetry API classes. This means:

- ✅ No dependencies beyond redis-py
- ✅ No memory backend initialization needed
- ✅ No UsageTracker singleton required
- ✅ Fast and simple

## Regenerating Test Data

To refresh with new random data:

```bash
# Clear Redis (optional)
redis-cli FLUSHDB

# Regenerate data
python scripts/populate_redis_direct.py
```

Dashboard will pick up new data on next auto-refresh (5 seconds).

## Troubleshooting

### Dashboard shows "No active agents"

**Cause:** Redis data expired (TTL) or was cleared

**Solution:**
```bash
python scripts/populate_redis_direct.py
```

### Dashboard shows "System Degraded (No Redis)"

**Cause:** Redis is not running

**Solution:**
```bash
redis-server
```

### Port 8000 already in use

**Cause:** Another process using port 8000

**Solution:** Stop other server or use different port:
```python
python -c "from src.attune.dashboard import run_simple_dashboard; run_simple_dashboard(port=8080)"
```

## API Endpoints (for testing)

The dashboard exposes these REST endpoints:

- `GET /api/health` - System health status
- `GET /api/agents` - List active agents
- `GET /api/signals?limit=20` - Recent coordination signals
- `GET /api/events?limit=30` - Recent events
- `GET /api/approvals` - Pending approval requests
- `GET /api/feedback/workflows` - Quality metrics
- `GET /api/feedback/underperforming?threshold=0.7` - Underperforming stages
- `POST /api/approvals/{id}/approve` - Approve request
- `POST /api/approvals/{id}/reject` - Reject request

Test with curl:
```bash
curl http://localhost:8000/api/health
curl http://localhost:8000/api/agents
```

## Architecture

```
┌─────────────────────────────────────────┐
│         Browser (http://localhost:8000) │
└────────────────┬────────────────────────┘
                 │
                 │ HTTP GET (every 5s)
                 │
┌────────────────▼────────────────────────┐
│  simple_server.py (Python stdlib only)  │
│  - HTTPServer (no FastAPI/Flask)        │
│  - Serves HTML/CSS/JS                   │
│  - REST API endpoints                   │
└────────────────┬────────────────────────┘
                 │
                 │ redis-py
                 │
┌────────────────▼────────────────────────┐
│           Redis (localhost:6379)        │
│  - 364 keys with test data              │
│  - TTL-based expiration                 │
└─────────────────────────────────────────┘
```

## Zero Dependencies Design

**Core:** Python stdlib only
- `http.server` - Web server
- `json` - Data serialization
- `pathlib` - File handling
- `urllib.parse` - URL parsing

**Data Layer:** redis-py (already installed)
- Direct Redis access
- No telemetry API
- No memory backend initialization

**Frontend:** Vanilla JavaScript
- No frameworks
- No build process
- Works in any modern browser

---

**Next Steps:**

1. Start dashboard: `./scripts/start_dashboard.sh`
2. Open browser: `http://localhost:8000`
3. Watch auto-refresh show real-time data
4. Click "Approve" or "Reject" on approval requests to see interaction
5. Check console for API request logs

**Documentation:**
- Full guide: [docs/DASHBOARD_GUIDE.md](docs/DASHBOARD_GUIDE.md)
- Implementation summary: [docs/DASHBOARD_SUMMARY.md](docs/DASHBOARD_SUMMARY.md)
