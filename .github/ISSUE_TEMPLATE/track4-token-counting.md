## Objective
Replace rough token estimates with Anthropic's official token counter for accurate cost tracking.

## Implementation Tasks
- [ ] Create `empathy_llm_toolkit/utils/tokens.py` with token counting utilities
- [ ] Add `count_tokens()` and `count_message_tokens()` functions
- [ ] Update `AnthropicProvider` with `estimate_tokens()` and `calculate_actual_cost()`
- [ ] Add pre-request validation in workflow base
- [ ] Update telemetry to track accurate costs
- [ ] Add tests

## Success Criteria
- [ ] Token counting using Anthropic SDK
- [ ] All rough estimates replaced
- [ ] Cost accuracy within 1% of actual bills
- [ ] Pre-request validation functional

## Expected Impact
- **Cost Tracking:** Accurate to within 1% (vs 10-20% error)
- **Timeline:** Week 1
- **Priority:** HIGH

## Reference
See detailed implementation plan in `docs/ANTHROPIC_OPTIMIZATION_PLAN.md` - Track 4
