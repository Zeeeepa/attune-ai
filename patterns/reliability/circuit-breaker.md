# Circuit Breaker Pattern

**Source Domain:** Reliability Engineering
**Location in Codebase:** `src/empathy_os/resilience/circuit_breaker.py`, `src/empathy_os/models/fallback.py`
**Level:** 4 (Anticipatory)

## Overview

Prevents cascading failures by temporarily disabling failing components. The circuit "opens" after repeated failures, allowing the system to fail fast rather than waiting for timeouts.

## Three-State Model

```
┌─────────┐    failures >= threshold    ┌─────────┐
│ CLOSED  │ ─────────────────────────→ │  OPEN   │
│(normal) │                             │(failing)│
└─────────┘                             └────┬────┘
     ↑                                       │
     │    success in half-open               │ timeout elapsed
     │                                       ↓
     └────────────────────────────── ┌───────────┐
                                     │ HALF_OPEN │
                                     │ (testing) │
                                     └───────────┘
```

## Implementation

```python
from empathy_os.resilience.circuit_breaker import circuit_breaker, CircuitBreaker

# Decorator usage
@circuit_breaker(failure_threshold=5, reset_timeout=60)
async def external_api_call():
    return await api.fetch()

# With fallback on circuit open
@circuit_breaker(fallback=lambda: {"status": "degraded"})
async def get_status():
    return await service.status()
```

## Configuration Options

| Parameter | Default | Description |
|-----------|---------|-------------|
| `failure_threshold` | 5 | Failures before opening circuit |
| `reset_timeout` | 60.0 | Seconds before testing recovery |
| `half_open_max_calls` | 3 | Test calls in half-open state |
| `excluded_exceptions` | () | Exceptions that don't trigger failures |

## Key Insight

The circuit breaker is **anticipatory** - it predicts that a failing service will continue to fail and proactively avoids it, rather than reactively handling each failure.

## Metrics to Monitor

- Circuit state transitions per hour
- Time spent in OPEN state
- Recovery success rate from HALF_OPEN
- Fallback invocation count

## Cross-Domain Transfer Potential

See [circuit-breaker-to-trust.md](../cross-domain/circuit-breaker-to-trust.md) for applying this pattern to user trust scoring.
