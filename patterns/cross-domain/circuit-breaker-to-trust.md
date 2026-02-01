# Cross-Domain Transfer: Circuit Breaker → Trust Scoring

**Source Pattern:** [Circuit Breaker](../reliability/circuit-breaker.md)
**Source Domain:** Reliability Engineering
**Target Domain:** Human-AI Trust Management
**Transfer Type:** Conceptual Mapping
**Status:** IMPLEMENTED
**Implementation:** [src/attune/trust/circuit_breaker.py](../../src/attune/trust/circuit_breaker.py)
**Guide:** [docs/guides/trust-circuit-breaker.md](../../docs/guides/trust-circuit-breaker.md)

## The Transfer Insight

Circuit breakers protect systems from cascading failures by temporarily disabling unreliable components. The same pattern can protect **user trust** by temporarily limiting AI autonomy when trust has been damaged.

## Mapping

| Circuit Breaker | Trust Scoring |
|-----------------|---------------|
| Service/API | AI autonomy level |
| Failure | Trust-damaging event (wrong answer, ignored preference) |
| CLOSED state | Full autonomy |
| OPEN state | Reduced autonomy, require confirmation |
| HALF_OPEN state | Supervised autonomy, testing trust recovery |
| Reset timeout | Trust recovery period |

## Implementation Sketch

```python
@dataclass
class TrustCircuitBreaker:
    """Circuit breaker for AI autonomy based on trust."""

    user_id: str
    trust_damage_threshold: int = 3  # Events before reducing autonomy
    recovery_period_hours: float = 24.0
    supervised_actions: int = 5  # Actions in "half-open" before full trust

    # States
    FULL_AUTONOMY = "full"      # CLOSED - act freely
    REDUCED_AUTONOMY = "reduced"  # OPEN - require confirmation
    SUPERVISED = "supervised"    # HALF_OPEN - testing trust

    async def should_require_confirmation(self, action: str) -> bool:
        """Check if action needs user confirmation."""
        state = self._get_trust_state()

        if state == self.FULL_AUTONOMY:
            return False  # Act freely
        elif state == self.REDUCED_AUTONOMY:
            return True  # Always confirm
        else:  # SUPERVISED
            return action in self.high_impact_actions

    def record_trust_damage(self, event: str):
        """Record an event that damaged trust."""
        self._damage_count += 1
        if self._damage_count >= self.trust_damage_threshold:
            self._transition_to_reduced_autonomy()

    def record_positive_interaction(self):
        """Record a positive interaction (builds trust)."""
        if self._state == self.SUPERVISED:
            self._supervised_successes += 1
            if self._supervised_successes >= self.supervised_actions:
                self._transition_to_full_autonomy()
```

## Use Cases

### 1. Wrong Answer Recovery

```
User asks factual question
  ↓
AI gives incorrect answer
  ↓
User corrects AI
  ↓
Trust circuit "trips" → REDUCED_AUTONOMY
  ↓
AI now confirms factual claims before stating
  ↓
After 5 confirmed-correct answers → SUPERVISED
  ↓
After 5 more unconfirmed-correct → FULL_AUTONOMY
```

### 2. Preference Violation Recovery

```
User has preference: "Always use TypeScript"
  ↓
AI generates JavaScript code
  ↓
User expresses frustration
  ↓
Trust circuit "trips" for code generation
  ↓
AI now confirms language choice before generating
  ↓
Gradual recovery through successful interactions
```

## Key Adaptations from Original Pattern

1. **Asymmetric recovery** - Trust rebuilds slower than it degrades (unlike services)
2. **Domain-specific states** - Not just on/off, but graduated autonomy
3. **Action-specific circuits** - Trust in code review ≠ trust in writing
4. **Visible state** - Users should know their trust level (transparency)

## Metrics

- Time at each trust level
- Trust damage events per user
- Recovery success rate
- User satisfaction at each autonomy level

## Why This Transfer Works

Both patterns solve the same abstract problem: **protecting a relationship (system↔service or AI↔user) from repeated negative interactions by temporarily reducing engagement intensity**.
