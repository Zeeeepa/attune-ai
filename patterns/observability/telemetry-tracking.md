# Telemetry & Resilience Tracking Pattern

**Source Domain:** Observability
**Location in Codebase:** `src/attune/models/telemetry.py`
**Level:** 3-4 (Proactive/Anticipatory)

## Overview

Comprehensive tracking of all LLM calls and system operations with resilience metadata. Enables post-hoc analysis, anomaly detection, and continuous improvement.

## LLM Call Record Structure

```python
@dataclass
class LLMCallRecord:
    # Identity
    call_id: str
    timestamp: datetime

    # Request details
    provider: str
    model: str
    tier: str
    task_type: str

    # Response metrics
    input_tokens: int
    output_tokens: int
    cost: float
    latency_ms: int

    # Resilience tracking
    fallback_used: bool = False
    fallback_chain: list[str] = field(default_factory=list)
    original_provider: str | None = None
    original_model: str | None = None
    retry_count: int = 0
    circuit_breaker_state: str | None = None

    # Error tracking
    success: bool = True
    error_type: str | None = None
    error_message: str | None = None
```

## Key Metrics for Level 5 Evolution

| Metric | Purpose | Level 5 Application |
|--------|---------|---------------------|
| `fallback_chain` | Which fallbacks were tried | Optimize fallback order |
| `retry_count` | Retries before success | Predict instability |
| `circuit_breaker_state` | Provider health | Proactive provider selection |
| `error_type` | Failure classification | Pattern recognition |

## Implementation

```python
from attune.models.telemetry import TelemetryBackend, LLMCallRecord

telemetry = TelemetryBackend()

# Record a call
record = LLMCallRecord(
    call_id="call_123",
    provider="anthropic",
    model="claude-sonnet-4-20250514",
    tier="capable",
    task_type="code_review",
    input_tokens=1500,
    output_tokens=800,
    cost=0.0069,
    latency_ms=2340,
    fallback_used=True,
    original_provider="openai",
    retry_count=2
)
await telemetry.record(record)

# Query for analysis
failed_calls = await telemetry.query(success=False, provider="openai")
fallback_rate = len([r for r in records if r.fallback_used]) / len(records)
```

## Key Insight

Telemetry enables **learning from failures**. Each failure record is data for improving the system's anticipatory capabilities.

## Analysis Queries for Pattern Discovery

```python
# Find providers with high failure rates
provider_failures = group_by(records, "provider").agg(
    failure_rate=lambda r: sum(not r.success) / len(r)
)

# Identify tasks that frequently need fallback
fallback_heavy_tasks = group_by(records, "task_type").filter(
    lambda r: r.fallback_rate > 0.1
)

# Detect degrading performance over time
latency_trend = records.rolling(window=100).mean("latency_ms")
```

## Cross-Domain Transfer Potential

The telemetry pattern can track:
- **User interaction patterns** - Which features need "fallback" help
- **Learning progress** - When users need extra support
- **Trust trajectory** - Trust score changes over time
