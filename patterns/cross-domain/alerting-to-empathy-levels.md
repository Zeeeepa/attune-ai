# Cross-Domain Transfer: Threshold Alerting → Empathy Level Transitions

**Source Pattern:** [Health Monitoring](../observability/health-monitoring.md)
**Source Domain:** Observability/SRE
**Target Domain:** Empathy Framework Levels
**Transfer Type:** Mechanism Mapping

## The Transfer Insight

Health monitoring uses thresholds to transition between HEALTHY → DEGRADED → UNHEALTHY states. The same mechanism can trigger transitions between empathy levels based on user interaction patterns.

## Mapping

| Health Monitoring | Empathy Levels |
|-------------------|----------------|
| Health check | User interaction signal |
| HEALTHY | Current empathy level appropriate |
| DEGRADED | User needs more support (escalate) |
| UNHEALTHY | Critical mismatch (major escalation) |
| Threshold | Interaction pattern trigger |
| Aggregation | Multi-signal combination |

## The 5-Level Empathy Model

```
Level 1: Reactive      - Respond to explicit requests
Level 2: Guided        - Offer structured assistance
Level 3: Proactive     - Anticipate immediate needs
Level 4: Anticipatory  - Predict future needs (30-90 days)
Level 5: Systems       - Cross-domain pattern transfer
```

## Implementation Sketch

```python
@dataclass
class EmpathyLevelMonitor:
    """Monitor user signals to adjust empathy level."""

    user_id: str
    current_level: int = 2  # Start at Guided

    # Escalation thresholds
    confusion_threshold: int = 3  # Questions about same topic
    frustration_threshold: float = 0.4  # Sentiment score
    repetition_threshold: int = 2  # Repeated requests

    # De-escalation thresholds
    independence_threshold: int = 5  # Self-resolved tasks
    expertise_threshold: float = 0.8  # Task completion rate

    async def check_signals(self, interaction: Interaction) -> LevelChange:
        """Check interaction signals for level change."""
        signals = []

        # Check confusion signal
        if self._count_topic_questions(interaction.topic) >= self.confusion_threshold:
            signals.append(Signal("confusion", severity="escalate"))

        # Check frustration signal
        sentiment = await self._analyze_sentiment(interaction.text)
        if sentiment < self.frustration_threshold:
            signals.append(Signal("frustration", severity="escalate"))

        # Check independence signal (de-escalation)
        if self._count_self_resolved() >= self.independence_threshold:
            signals.append(Signal("independence", severity="de-escalate"))

        return self._aggregate_signals(signals)

    def _aggregate_signals(self, signals: list[Signal]) -> LevelChange:
        """Aggregate signals (like health check aggregation)."""
        escalate_count = sum(1 for s in signals if s.severity == "escalate")
        de_escalate_count = sum(1 for s in signals if s.severity == "de-escalate")

        if escalate_count >= 2:
            return LevelChange(direction="up", magnitude=1)
        elif de_escalate_count >= 2 and escalate_count == 0:
            return LevelChange(direction="down", magnitude=1)
        else:
            return LevelChange(direction="none", magnitude=0)
```

## Signal Types for Each Transition

### Escalate (Need More Support)

| From | To | Trigger Signals |
|------|-----|-----------------|
| L1 (Reactive) | L2 (Guided) | Repeated questions, incomplete tasks |
| L2 (Guided) | L3 (Proactive) | Confusion, missed suggestions |
| L3 (Proactive) | L4 (Anticipatory) | Complex multi-step needs, pattern emergence |
| L4 (Anticipatory) | L5 (Systems) | Cross-domain problems, strategic needs |

### De-escalate (More Independent)

| From | To | Trigger Signals |
|------|-----|-----------------|
| L5 | L4 | Routine work, no strategic decisions |
| L4 | L3 | Short-term focus, immediate needs only |
| L3 | L2 | High self-resolution, expertise signals |
| L2 | L1 | Expert user, prefers minimal assistance |

## Example: Developer Onboarding Journey

```
Day 1: Level 2 (Guided)
  - New to codebase
  - Needs structured help

Week 2: Escalate to Level 3 (Proactive)
  - Still asking same questions (confusion_threshold hit)
  - AI starts proactively explaining patterns

Month 2: De-escalate to Level 2
  - High task completion (expertise_threshold hit)
  - User resolving issues independently

Month 6: Escalate to Level 4 (Anticipatory)
  - Working on architecture decisions
  - Cross-file refactoring patterns emerge
```

## Key Adaptations

1. **Bidirectional transitions** - Unlike health (recover to healthy), empathy levels go both ways intentionally
2. **User preference override** - Users can request a different level
3. **Context-specific levels** - Code review might be L3 while documentation is L2
4. **Gradual transitions** - No jumping from L1 to L5

## Why This Transfer Works

Both systems use **threshold-based state machines** to respond to changing conditions. The mechanism (monitor → aggregate → transition) is identical; only the signals and states differ.
