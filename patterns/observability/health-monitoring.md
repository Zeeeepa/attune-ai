# Health Monitoring & Threshold Alerting Pattern

**Source Domain:** Observability/Site Reliability Engineering
**Location in Codebase:** `src/attune/resilience/health.py`
**Level:** 4 (Anticipatory)

## Overview

Continuously monitors component health with automatic status aggregation and threshold-based alerting. Enables proactive response before users are affected.

## Health Status Model

```
┌───────────┐
│  HEALTHY  │ ← All checks pass
└───────────┘
      ↓ some checks degraded
┌───────────┐
│ DEGRADED  │ ← Partial functionality
└───────────┘
      ↓ critical checks fail
┌───────────┐
│ UNHEALTHY │ ← Major functionality impaired
└───────────┘
      ↓ can't determine
┌───────────┐
│  UNKNOWN  │ ← Health check itself failed
└───────────┘
```

## Implementation

```python
from attune.resilience.health import HealthCheck, HealthStatus

health = HealthCheck(version="3.3.3")

@health.register("database", critical=True)
async def check_database():
    await db.ping()
    return True

@health.register("memory_graph")
async def check_memory_graph():
    graph = MemoryGraph()
    return len(graph.nodes) >= 0

@health.register("wizard_registry")
async def check_wizards():
    count = len(wizard_registry.list())
    return count >= 5  # Threshold: at least 5 wizards loaded

# Run all checks
status = await health.run_all()
print(status.overall)  # HealthStatus.HEALTHY
print(status.to_dict())  # JSON for monitoring systems
```

## Aggregation Logic

```python
def aggregate_health(results: list[HealthCheckResult]) -> HealthStatus:
    statuses = [r.status for r in results]

    if all(s == HealthStatus.HEALTHY for s in statuses):
        return HealthStatus.HEALTHY
    elif any(s == HealthStatus.UNHEALTHY for s in statuses):
        return HealthStatus.UNHEALTHY
    elif any(s == HealthStatus.DEGRADED for s in statuses):
        return HealthStatus.DEGRADED
    else:
        return HealthStatus.UNKNOWN
```

## Default Health Checks (Built-in)

| Check | Threshold | Critical |
|-------|-----------|----------|
| `wizard_registry` | >= 5 wizards | No |
| `memory_graph` | Accessible | No |
| `smart_router` | Returns decision | Yes |
| `chain_executor` | Templates load | Yes |

## Key Insight

Health checks are **predictive** - a degraded status predicts future failures, enabling intervention before impact.

## Threshold Design Principles

1. **Set thresholds based on user impact**, not technical metrics
2. **Include buffer** - Alert when approaching limits, not at them
3. **Distinguish critical vs non-critical** - Not all degradation is equal
4. **Time-window thresholds** - Transient blips vs sustained issues

## Metrics to Monitor

- Time in each health state
- Health check execution time (slow checks = future problems)
- False positive/negative rates on alerts
- Mean time to recovery after UNHEALTHY

## Cross-Domain Transfer Potential

See [alerting-to-empathy-levels.md](../cross-domain/alerting-to-empathy-levels.md) for applying threshold alerting to empathy level transitions.
