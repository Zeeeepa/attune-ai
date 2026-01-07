# Tier Routing Savings: Sensitivity Analysis

**Question**: Does the "80% savings" claim hold up across different usage patterns?

**Short Answer**: **No** - the 80% is based on a specific task distribution. Heavy Opus usage = much less savings.

---

## Pricing Constants

| Tier | Model | Cost per Task* |
|------|-------|----------------|
| CHEAP | Haiku | $0.0075 |
| CAPABLE | Sonnet | $0.090 |
| PREMIUM | Opus | $0.450 |

*Typical task: 5,000 input tokens, 1,000 output tokens

---

## Scenario Analysis: How Savings Change with Usage Patterns

### Scenario 1: Heavy PREMIUM Usage (Architecture-Heavy Workflow)
**Task Distribution**: 60% PREMIUM, 30% CAPABLE, 10% CHEAP (8 tasks)

**Without routing (baseline)**: 8 × $0.450 = $3.60

**With routing**:
- 4.8 PREMIUM @ $0.450 = $2.16
- 2.4 CAPABLE @ $0.090 = $0.216
- 0.8 CHEAP @ $0.0075 = $0.006
- **Total**: $2.38

**Savings**: ($3.60 - $2.38) / $3.60 = **34% reduction** ❌ (NOT 80%)

---

### Scenario 2: Balanced Usage (Original "80%" Example)
**Task Distribution**: 12.5% PREMIUM, 37.5% CAPABLE, 50% CHEAP (8 tasks)

**Without routing**: 8 × $0.450 = $3.60

**With routing**:
- 1 PREMIUM @ $0.450 = $0.450
- 3 CAPABLE @ $0.090 = $0.270
- 4 CHEAP @ $0.0075 = $0.030
- **Total**: $0.75

**Savings**: ($3.60 - $0.75) / $3.60 = **79% reduction** ✅ (The "80%" claim)

---

### Scenario 3: Research/Analysis Heavy (Lots of Sonnet)
**Task Distribution**: 10% PREMIUM, 70% CAPABLE, 20% CHEAP (10 tasks)

**Without routing**: 10 × $0.450 = $4.50

**With routing**:
- 1 PREMIUM @ $0.450 = $0.450
- 7 CAPABLE @ $0.090 = $0.630
- 2 CHEAP @ $0.0075 = $0.015
- **Total**: $1.095

**Savings**: ($4.50 - $1.095) / $4.50 = **76% reduction** ✅ (Close to 80%)

---

### Scenario 4: Data Processing Heavy (Lots of Haiku)
**Task Distribution**: 5% PREMIUM, 25% CAPABLE, 70% CHEAP (20 tasks)

**Without routing**: 20 × $0.450 = $9.00

**With routing**:
- 1 PREMIUM @ $0.450 = $0.450
- 5 CAPABLE @ $0.090 = $0.450
- 14 CHEAP @ $0.0075 = $0.105
- **Total**: $1.005

**Savings**: ($9.00 - $1.005) / $9.00 = **89% reduction** ✅ (Better than 80%)

---

### Scenario 5: Worst Case (All Tasks Need PREMIUM)
**Task Distribution**: 100% PREMIUM (security audit of critical code)

**Without routing**: 5 × $0.450 = $2.25

**With routing**:
- 5 PREMIUM @ $0.450 = $2.25 (can't route down, quality required)

**Savings**: $0 / $2.25 = **0% reduction** ❌ (No savings possible)

---

## Summary Table

| Scenario | PREMIUM % | CAPABLE % | CHEAP % | Savings | Notes |
|----------|-----------|-----------|---------|---------|-------|
| Heavy Architecture | 60% | 30% | 10% | 34% | ❌ Much less than 80% |
| Balanced (original) | 12.5% | 37.5% | 50% | 79-80% | ✅ The "80%" claim |
| Analysis Heavy | 10% | 70% | 20% | 76% | ✅ Close to 80% |
| Data Processing | 5% | 25% | 70% | 89% | ✅ Better than 80% |
| All Critical | 100% | 0% | 0% | 0% | ❌ No routing possible |

---

## The Real Formula

```
Savings = (Baseline - Routed) / Baseline

Where:
Baseline = Total_Tasks × PREMIUM_Cost
Routed = (Premium_Tasks × $0.450) +
         (Capable_Tasks × $0.090) +
         (Cheap_Tasks × $0.0075)

Savings depends on task distribution:
- More PREMIUM tasks → Less savings
- More CHEAP tasks → More savings
```

---

## Key Insight: The 80% is NOT Universal

**What we should say**:
- ✅ "80% savings on **typical** workflows (12% PREMIUM, 38% CAPABLE, 50% CHEAP)"
- ✅ "Savings range: 34-89% depending on task complexity"
- ✅ "Best for workflows with many simple tasks (formatting, summaries, checks)"
- ❌ NOT: "80% savings" (without qualifiers)

---

## Do We Have Real Measurement Data?

**Current Status**: ❌ **THEORETICAL ONLY**

- The 80% is based on **pricing math** + **assumed task distribution**
- We do NOT have real telemetry data showing actual user savings
- We do NOT track tier usage distribution in production workflows

**What we need**:
1. Telemetry: Track actual tier usage per workflow
2. Baseline measurements: What would it cost without routing?
3. Real user case studies: Actual savings in production

---

## Honest Claim (What We Should Say Instead)

**Current Claim** (pyproject.toml, README):
> "tier routing (80% cost savings)"

**Honest Claim**:
> "tier routing (up to 89% cost savings on typical workflows, varies by task complexity)"

Or more conservative:
> "tier routing (34-89% cost savings depending on task distribution, avg ~75%)"

---

## Bottom Line

The 80% savings is:
1. ✅ **Mathematically correct** for the specific example (12.5% PREMIUM, 37.5% CAPABLE, 50% CHEAP)
2. ❌ **NOT universal** - depends heavily on your actual task distribution
3. ❌ **NOT measured** - theoretical calculation, no real telemetry
4. ⚠️ **Optimistic** - assumes you would have used all Opus without routing (unlikely)

**If you use Opus heavily** (60%+ of tasks), expect **30-40% savings**, not 80%.

---

**Generated**: 2026-01-07
**Purpose**: Verify tier routing claims with sensitivity analysis
**Recommendation**: Update claims to include task distribution caveat
