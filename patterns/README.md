# Empathy Framework Pattern Catalog

A catalog of reusable patterns extracted from the Empathy Framework codebase, organized for cross-domain transfer and Level 5 (Systems Thinking) capability development.

## Purpose

This catalog serves three goals:

1. **Document existing patterns** - Capture what we've already built
2. **Enable cross-domain transfer** - Apply patterns from reliability to trust, from observability to empathy
3. **Accelerate Level 5 thinking** - Train the ability to recognize "this problem is like that solved problem"

## Pattern Categories

### Reliability Patterns
*Source: `src/attune/resilience/`*

| Pattern | Level | Key Insight |
|---------|-------|-------------|
| [Circuit Breaker](reliability/circuit-breaker.md) | 4 | Predict failures, fail fast |
| [Graceful Degradation](reliability/graceful-degradation.md) | 4 | Partial value beats total failure |
| [Retry with Backoff](reliability/retry-with-backoff.md) | 3 | Transient failures are recoverable |

### Observability Patterns
*Source: `src/attune/models/telemetry.py`, `src/attune/resilience/health.py`*

| Pattern | Level | Key Insight |
|---------|-------|-------------|
| [Health Monitoring](observability/health-monitoring.md) | 4 | Degraded predicts unhealthy |
| [Telemetry Tracking](observability/telemetry-tracking.md) | 3-4 | Failures are learning data |

### Cross-Domain Transfers
*The Level 5 breakthrough patterns*

| Transfer | From → To | Status | Key Insight |
|----------|-----------|--------|-------------|
| [Circuit Breaker → Trust](cross-domain/circuit-breaker-to-trust.md) | Reliability → Trust | **IMPLEMENTED** | Protect relationships like systems |
| [Alerting → Empathy Levels](cross-domain/alerting-to-empathy-levels.md) | Observability → Empathy | Documented | Thresholds trigger level changes |
| [Degradation → Conversation](cross-domain/graceful-degradation-to-conversation.md) | Reliability → UX | Documented | Degraded response beats failure |

### Implemented Transfers

| Transfer | Implementation | Guide |
|----------|----------------|-------|
| Circuit Breaker → Trust | [`src/attune/trust/`](../src/attune/trust/) | [Trust Circuit Breaker Guide](../docs/guides/trust-circuit-breaker.md) |

## Capability Level Reference

| Level | Name | Pattern Characteristic |
|-------|------|----------------------|
| 1 | Reactive | Respond to explicit requests |
| 2 | Guided | Follow established patterns |
| 3 | Proactive | Anticipate immediate needs |
| 4 | Anticipatory | Predict future needs (30-90 days) |
| 5 | Systems | Transfer patterns across domains |

## How to Use This Catalog

### For Developers
1. When facing a new problem, search for similar patterns
2. Check cross-domain transfers for non-obvious solutions
3. Contribute new patterns following the template

### For AI Systems
1. Reference patterns when solving problems
2. Propose cross-domain transfers when patterns match
3. Track pattern usage for learning

### For Architects
1. Ensure new features follow established patterns
2. Identify opportunities for pattern consolidation
3. Propose new cross-domain transfers

## Pattern Template

```markdown
# Pattern Name

**Source Domain:** Where this pattern originated
**Location in Codebase:** File paths
**Level:** Capability level (1-5)

## Overview
What problem does this solve?

## Implementation
Code examples from actual codebase

## Key Insight
The one thing to remember

## Cross-Domain Transfer Potential
Where else could this apply?
```

## Contributing

1. Identify a pattern in the codebase
2. Document using the template above
3. Look for cross-domain transfer opportunities
4. Add to the appropriate category

## Metrics

Track pattern catalog health:
- Patterns documented: 5
- Cross-domain transfers: 3 (1 implemented)
- Implementations: 1 (Trust Circuit Breaker)
- Coverage of codebase: ~40%
- Last updated: 2025-12-28

## Documentation

- [Pattern Catalog Guide](../docs/guides/pattern-catalog.md) - How to use and contribute to the catalog
- [Trust Circuit Breaker Guide](../docs/guides/trust-circuit-breaker.md) - Detailed guide for the implemented transfer

---

*This catalog is a key component of reaching Level 5 (Systems Thinking) capability.*
