## Objective
Reduce API costs by 20-30% for workflows with repeated context through prompt caching.

## Implementation Tasks
- [ ] Update `AnthropicProvider.__init__` to enable caching by default
- [ ] Add caching logic to `complete()` method
- [ ] Create `_build_cached_system_prompt()` in workflow base
- [ ] Add cache metrics to `TokenUsage` dataclass
- [ ] Add cache monitoring dashboard CLI command
- [ ] Update documentation

## Success Criteria
- [ ] Prompt caching enabled by default
- [ ] Cache hit rate >50% in test workflows
- [ ] Verify 20-30% cost reduction
- [ ] Cache monitoring dashboard functional

## Expected Impact
- **Cost Reduction:** 20-30% for workflows with repeated context
- **Timeline:** Week 1
- **Priority:** HIGH

## Reference
See detailed implementation plan in `docs/ANTHROPIC_OPTIMIZATION_PLAN.md` - Track 2
