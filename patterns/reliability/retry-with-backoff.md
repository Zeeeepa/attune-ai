# Retry with Exponential Backoff Pattern

**Source Domain:** Reliability Engineering
**Location in Codebase:** `src/empathy_os/resilience/retry.py`, `src/empathy_os/models/fallback.py`
**Level:** 3 (Proactive)

## Overview

Automatically retries failed operations with increasing delays between attempts. Prevents overwhelming recovering services while maximizing chances of eventual success.

## Backoff Calculation

```
delay = initial_delay * (backoff_factor ^ (attempt - 1))
delay = min(delay, max_delay)
if jitter:
    delay = delay * random(0.75, 1.25)
```

Example with defaults (initial=1s, factor=2x):
- Attempt 1: 1s
- Attempt 2: 2s
- Attempt 3: 4s
- Attempt 4: 8s (capped at max_delay)

## Implementation

```python
from empathy_os.resilience.retry import retry, RetryConfig

@retry(max_attempts=3, backoff_factor=2.0)
async def call_llm(prompt: str) -> str:
    return await api.complete(prompt)

# With callback on retry
@retry(
    max_attempts=3,
    on_retry=lambda exc, attempt: logger.warning(f"Retry {attempt}: {exc}")
)
async def api_call():
    return await service.fetch()
```

## Configuration

```python
@dataclass
class RetryConfig:
    max_attempts: int = 3
    backoff_factor: float = 2.0
    initial_delay: float = 1.0
    max_delay: float = 60.0
    jitter: bool = True  # Prevents thundering herd
    retryable_exceptions: tuple = (Exception,)
```

## Error Classification for Selective Retry

```python
def should_retry(error_type: str) -> bool:
    retryable = ["rate_limit", "timeout", "server_error", "connection_error"]
    return error_type in retryable

# Don't retry: authentication errors, validation errors, not found
```

## Key Insight

**Jitter is critical** - Without it, all clients retry at the same time, causing "thundering herd" that can take down recovering services.

## When NOT to Retry

- Authentication failures (won't succeed on retry)
- Validation errors (same input = same failure)
- Explicit rejection (service said "no")
- Idempotency not guaranteed (could cause duplicates)

## Metrics to Monitor

- Retry rate by error type
- Success rate per attempt number
- Total time spent in retries
- Retry exhaustion rate

## Cross-Domain Transfer Potential

The backoff concept applies to:
- **User engagement**: Back off on notifications if user isn't responding
- **Learning systems**: Reduce suggestion frequency for rejected recommendations
- **Trust recovery**: Gradually restore trust levels after violations
