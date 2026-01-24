# Strategic Compaction Skill

Preserve collaboration state through context compaction events.

## Purpose

When context windows approach their limits, this skill ensures:
- Trust levels are preserved
- Detected patterns survive compaction
- Pending work is captured via SBAR handoffs
- User preferences are maintained
- Session continuity is possible

## When to Use

- Context usage exceeds 50% of window
- Long-running sessions with accumulated state
- Before starting intensive operations
- When switching between major work phases

## Workflow

### Pre-Compaction

1. **Assess Current State**
   - Check trust level
   - Count detected patterns
   - Note current work phase
   - Identify pending work

2. **Create SBAR Handoff** (if needed)
   ```
   Situation: What's happening now
   Background: Relevant context
   Assessment: Current understanding
   Recommendation: Suggested next action
   ```

3. **Save Compact State**
   - User identity
   - Trust and empathy levels
   - Pattern summaries (top 10)
   - Session and phase tracking
   - Key preferences

### Post-Compaction

1. **Restore State**
   - Load most recent compact state
   - Apply trust level
   - Restore empathy level
   - Load preferences

2. **Generate Restoration Prompt**
   - Format session summary
   - Include known patterns
   - Present pending handoff

3. **Continue Work**
   - Clear addressed handoff
   - Resume from saved phase

## Integration Points

### Hooks
- `PreCompact`: Triggers state save
- `SessionStart`: Checks for state restoration

### Context Manager
```python
from empathy_llm_toolkit.context import ContextManager

manager = ContextManager()

# Save before compaction
manager.save_for_compaction(collaboration_state)

# Restore after compaction
state = manager.restore_state(user_id)
prompt = state.format_restoration_prompt()
```

### State Structure

```python
CompactState(
    user_id="user123",
    trust_level=0.8,
    empathy_level=4,
    detected_patterns=[...],  # PatternSummary list
    session_id="session-001",
    current_phase="implementation",
    completed_phases=["planning", "design"],
    pending_handoff=SBARHandoff(...),
    interaction_count=45,
    preferences={"verbosity": "high"},
)
```

## Best Practices

1. **Save Early, Save Often**
   - Don't wait for forced compaction
   - Save at natural breakpoints

2. **Keep Handoffs Actionable**
   - Clear situation description
   - Specific recommendation

3. **Limit Preserved Data**
   - Top 10 patterns only
   - Key preferences only
   - No sensitive data

4. **Verify Restoration**
   - Check trust level applied
   - Confirm patterns loaded
   - Address any pending handoff

## Attribution

Context management patterns inspired by everything-claude-code by Affaan Mustafa.
See: https://github.com/affaan-m/everything-claude-code (MIT License)
