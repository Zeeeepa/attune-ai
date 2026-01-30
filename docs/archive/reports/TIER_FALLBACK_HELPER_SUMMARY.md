---
description: TierFallbackHelper Extension Summary: ## Overview Extended `src/empathy_os/models/fallback.py` to add Sprint 1 convenience methods for simple tier-based fallbac
---

# TierFallbackHelper Extension Summary

## Overview
Extended `src/empathy_os/models/fallback.py` to add Sprint 1 convenience methods for simple tier-based fallback logic while preserving all existing sophisticated FallbackPolicy functionality.

## Changes Made

### 1. Added TierFallbackHelper Class
**Location:** `/src/empathy_os/models/fallback.py` (lines 690-763)

A new helper class with two simple class methods:

```python
class TierFallbackHelper:
    """Helper class for simple tier-based fallback logic."""

    TIER_PROGRESSION = {
        "cheap": "capable",
        "capable": "premium",
        "premium": None
    }

    @classmethod
    def get_next_tier(cls, current_tier: str) -> str | None:
        """Get next tier in fallback chain."""
        return cls.TIER_PROGRESSION.get(current_tier)

    @classmethod
    def should_fallback(cls, error: Exception, tier: str) -> bool:
        """Determine if fallback should be attempted."""
        if tier == "premium":
            return False
        fallback_errors = (TimeoutError, ConnectionError, OSError)
        return isinstance(error, fallback_errors)
```

### 2. Updated Module Exports
**Location:** `/src/empathy_os/models/__init__.py`

- Added `TierFallbackHelper` to imports from `.fallback`
- Added `TierFallbackHelper` to `__all__` export list

### 3. Created Comprehensive Test Suite
**Location:** `/tests/unit/models/test_tier_fallback_helper.py`

Created 17 tests covering:
- Tier progression logic (4 tests)
- Fallback decision logic (7 tests)
- Edge cases (4 tests)
- Integration with existing FallbackPolicy (2 tests)

**All tests pass:** ✅ 17/17 passed

## Usage Examples

### Import
```python
from empathy_os.models import TierFallbackHelper
```

### Get Next Tier
```python
>>> TierFallbackHelper.get_next_tier("cheap")
'capable'
>>> TierFallbackHelper.get_next_tier("capable")
'premium'
>>> TierFallbackHelper.get_next_tier("premium")
None
```

### Determine Fallback
```python
>>> TierFallbackHelper.should_fallback(TimeoutError(), "cheap")
True
>>> TierFallbackHelper.should_fallback(ValueError(), "cheap")
False
>>> TierFallbackHelper.should_fallback(TimeoutError(), "premium")
False
```

## Design Decisions

### 1. Separate Helper Class
- **Why:** Preserves existing FallbackPolicy for sophisticated use cases
- **Benefit:** Sprint 1 tests can use simple helpers without complex setup
- **Trade-off:** Two approaches exist, but they serve different purposes

### 2. Simple Tier Progression
- **Direction:** Always progresses UP in tiers (cheap → capable → premium)
- **Rationale:** Fallback should use more capable models when cheaper ones fail
- **Note:** Different from FallbackPolicy's `CHEAPER_TIER_SAME_PROVIDER` which goes DOWN in cost

### 3. Error Type Filtering
- **Fallback errors:** TimeoutError, ConnectionError, OSError
- **Non-fallback errors:** ValueError, TypeError, etc.
- **Rationale:** Network/infrastructure errors justify fallback; logic errors don't

### 4. Premium Tier Behavior
- **Never falls back from premium tier**
- **Rationale:** Premium is the highest tier; no higher tier available

## Backward Compatibility

✅ **All existing functionality preserved:**
- FallbackPolicy works exactly as before
- ResilientExecutor unchanged
- CircuitBreaker unchanged
- All default policies unchanged

✅ **No breaking changes:**
- All existing imports continue to work
- No changes to existing class interfaces
- Registry tests pass (30/30)
- New helper is purely additive

## Files Modified

1. `/src/empathy_os/models/fallback.py` - Added TierFallbackHelper class
2. `/src/empathy_os/models/__init__.py` - Added export
3. `/tests/unit/models/test_tier_fallback_helper.py` - New test file (17 tests)

## Testing

### New Tests
```bash
python -m pytest tests/unit/models/test_tier_fallback_helper.py -v
# Result: 17 passed in 0.86s
```

### Existing Tests (Backward Compatibility)
```bash
python -m pytest tests/unit/models/test_registry.py -v
# Result: 30 passed in 0.58s
```

### Integration Verification
```python
# Verified both classes can be imported and used together
from empathy_os.models import FallbackPolicy, TierFallbackHelper

# FallbackPolicy still works
policy = FallbackPolicy(
    primary_provider='anthropic',
    primary_tier='capable'
)
chain = policy.get_fallback_chain()

# TierFallbackHelper works alongside it
next_tier = TierFallbackHelper.get_next_tier('cheap')
```

## Use Cases

### Sprint 1 Simple Tests
```python
def test_basic_fallback():
    tier = "cheap"
    try:
        response = call_llm(tier=tier)
    except TimeoutError as e:
        if TierFallbackHelper.should_fallback(e, tier):
            next_tier = TierFallbackHelper.get_next_tier(tier)
            if next_tier:
                response = call_llm(tier=next_tier)
```

### Production Use (Existing FallbackPolicy)
```python
# For production, continue using sophisticated FallbackPolicy
policy = FallbackPolicy(
    primary_provider="anthropic",
    primary_tier="capable",
    strategy=FallbackStrategy.SAME_TIER_DIFFERENT_PROVIDER,
    max_retries=2
)
executor = ResilientExecutor(fallback_policy=policy)
```

## Documentation

### Class Docstrings
- ✅ Comprehensive docstrings on all methods
- ✅ Google-style parameter documentation
- ✅ Usage examples in docstrings
- ✅ Clear explanation of fallback logic

### Test Coverage
- ✅ Happy path tests
- ✅ Edge case tests
- ✅ Error handling tests
- ✅ Integration tests

## Next Steps

1. ✅ TierFallbackHelper implementation complete
2. ✅ Tests passing
3. ✅ Export from models package
4. 🔲 Use in Sprint 1 orchestration tests
5. 🔲 Consider deprecation path if FallbackPolicy is preferred long-term

## Notes

- Both approaches (TierFallbackHelper and FallbackPolicy) are valid
- TierFallbackHelper is simpler for testing
- FallbackPolicy is more flexible for production
- No need to choose one over the other - they coexist peacefully
