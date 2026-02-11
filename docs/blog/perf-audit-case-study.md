# From 67 to 100: Automated Performance Auditing with Attune AI

*How a single CLI command found and fixed performance issues in under 5 minutes.*

---

## The Problem

You've written code that works. Tests pass. But how do you know it's *fast*? Manual performance reviews are tedious, inconsistent, and usually get skipped under deadline pressure.

We ran into this with Attune AI's own codebase. Two demo scripts had triple-nested loops generating test data — functional, but O(n^3) with unnecessary overhead. Nobody caught it during code review.

## One Command

```bash
/attune perf
```

That's it. Attune's performance audit workflow scanned the entire codebase and returned a scored report in seconds:

**Score: 67/100 (Needs Optimization)**

| Priority | File | Issue |
|----------|------|-------|
| HIGH | `examples/dashboard_demo.py:195` | Triple nested loop (O(n^3)) |
| HIGH | `scripts/populate_redis_direct.py:169` | Triple nested loop (O(n^3)) + unbatched Redis writes |

## The Fix

### Before: Triple Nested Loops

```python
for workflow in workflows:
    for stage in stages:
        for tier in tiers:
            # Process each combination
            base_quality = 0.65 if tier == "cheap" else 0.80 if tier == "capable" else 0.90
            for i in range(num_samples):
                r.setex(key, 604800, value)  # Individual Redis call per iteration
```

Three levels of nesting. Plus each Redis `setex` was a separate network round-trip.

### After: itertools.product() + Redis Pipelining

```python
import itertools

tier_quality = {"cheap": 0.65, "capable": 0.80, "premium": 0.90}
pipe = r.pipeline()

for workflow, stage, tier in itertools.product(workflows, stages, tiers):
    base_quality = tier_quality[tier]
    for i in range(num_samples):
        pipe.setex(key, 604800, value)  # Batched — single round-trip

pipe.execute()  # One network call for all writes
```

Two changes:
1. **`itertools.product()`** flattens the triple nesting into a single loop
2. **Redis pipelining** batches all `setex` calls into one network round-trip

### Validation

```bash
/attune perf
```

**Score: 100/100** — Zero findings.

## What Happened Under the Hood

Attune's performance audit workflow uses a 3-tier model routing system:

1. **Cheap tier (Haiku)** scans for known antipatterns: nested loops, unbatched I/O, large list copies
2. **Capable tier (Sonnet)** analyzes context if cheap tier flags ambiguous findings
3. **Premium tier (Opus)** only activates for architectural-level performance analysis

For this scan, everything resolved at the cheap tier — **$0.00 cost** when running in Claude Code.

## Why This Matters

- **Automated**: No manual profiling setup required
- **Scored**: Quantified output (67 → 100) instead of vague suggestions
- **Actionable**: Specific file:line references with concrete fix patterns
- **Free**: $0 in Claude Code using your existing subscription
- **Fast**: Full codebase scan + report in under 30 seconds

## Try It

```bash
pip install attune-ai
attune setup
```

Then in Claude Code:

```bash
/attune perf
```

Or from the terminal:

```bash
attune workflow run perf-audit --path ./src
```

---

*Built with [Attune AI](https://github.com/Smart-AI-Memory/attune-ai) — AI-powered developer workflows with cost optimization.*
