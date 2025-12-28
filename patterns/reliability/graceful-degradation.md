# Graceful Degradation Pattern

**Source Domain:** Reliability Engineering
**Location in Codebase:** `src/empathy_os/resilience/fallback.py`, `src/empathy_os/models/fallback.py`
**Level:** 4 (Anticipatory)

## Overview

When primary functionality fails, the system automatically falls back to alternative implementations or default values, maintaining partial functionality rather than complete failure.

## Fallback Chain Model

```
┌──────────┐    fail    ┌──────────┐    fail    ┌──────────┐    fail    ┌─────────┐
│ Primary  │ ─────────→ │Fallback 1│ ─────────→ │Fallback 2│ ─────────→ │ Default │
│ (API)    │            │ (Cache)  │            │  (DB)    │            │ Value   │
└──────────┘            └──────────┘            └──────────┘            └─────────┘
```

## Implementation

```python
from empathy_os.resilience.fallback import Fallback, fallback

# Decorator with default value
@fallback(get_from_cache, default=None)
async def get_data():
    return await api.fetch()

# Fallback chain
chain = Fallback(
    name="data_retrieval",
    functions=[get_from_api, get_from_cache, get_from_db],
    default_value={"status": "unavailable"}
)
result = await chain.execute()
```

## Multi-Model Fallback Strategies

```python
class FallbackStrategy(Enum):
    SAME_TIER_DIFFERENT_PROVIDER = "same_tier_different_provider"
    CHEAPER_TIER_SAME_PROVIDER = "cheaper_tier_same_provider"
    DIFFERENT_PROVIDER_ANY_TIER = "different_provider_any_tier"
    CUSTOM = "custom"
```

| Strategy | Use Case |
|----------|----------|
| Same tier, different provider | Maintain quality, switch vendor |
| Cheaper tier, same provider | Accept quality drop, control costs |
| Any provider, any tier | Maximum availability |
| Custom | Specific business rules |

## Key Insight

Graceful degradation is about **maintaining user value** even when systems fail. A degraded response is almost always better than an error.

## Design Principles

1. **Identify minimum viable functionality** - What's the least you can do that's still useful?
2. **Pre-configure fallbacks** - Don't decide during failure
3. **Make degradation visible** - Users should know they're getting reduced service
4. **Test fallback paths** - They're as critical as primary paths

## Metrics to Monitor

- Fallback invocation rate
- User experience during degraded mode
- Time to recovery from degraded state
- Which fallbacks are actually used

## Cross-Domain Transfer Potential

See [graceful-degradation-to-conversation.md](../cross-domain/graceful-degradation-to-conversation.md) for applying this pattern to conversation quality.
