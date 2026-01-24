# Continuous Learning Skill

Automatic pattern extraction from sessions to enable learning and improvement.

## Purpose

Continuous learning enables the Empathy Framework to:
- Learn from user corrections ("Actually, I meant...")
- Capture error resolution patterns
- Remember workarounds for framework quirks
- Track user preferences
- Store project-specific conventions

## Pattern Categories

| Category | Description | Example |
|----------|-------------|---------|
| `user_correction` | When users clarify/correct | "Actually, I meant async" |
| `error_resolution` | How errors were fixed | TypeError → add null check |
| `workaround` | Framework/library quirks | "Use X instead of Y" |
| `preference` | User style preferences | "I prefer detailed responses" |
| `project_specific` | Codebase conventions | "We use kebab-case" |

## Workflow

### Session Evaluation

At session end, the evaluator analyzes:
1. **Interaction quality** - Length, depth, outcomes
2. **Correction signals** - "Actually", "I meant", etc.
3. **Error patterns** - Problems raised and resolved
4. **Trust trajectory** - Did trust improve?

Sessions scoring above threshold (default: 0.4) are processed for pattern extraction.

### Pattern Extraction

The extractor identifies:
- User corrections → captures original, correction, and resolution
- Error mentions followed by success signals → captures fix
- Workaround keywords → captures alternative approaches
- Preference expressions → captures user preferences

### Storage

Patterns are stored per-user with:
- Unique pattern ID (content hash)
- Category and tags
- Confidence score
- Source session reference
- Extraction timestamp

## Integration

### SessionEnd Hook

```python
from empathy_llm_toolkit.hooks.scripts import run_evaluate_session

result = run_evaluate_session({
    "collaboration_state": state,
    "user_id": "user123",
    "session_id": "session-001",
})

if result["patterns_extracted"] > 0:
    print(f"Learned {result['patterns_extracted']} new patterns")
```

### Context Injection

```python
from empathy_llm_toolkit.learning import LearnedSkillsStorage

storage = LearnedSkillsStorage()
context = storage.format_patterns_for_context(
    user_id="user123",
    max_patterns=5,
)
# Returns markdown for injection into prompts
```

### API Usage

```python
from empathy_llm_toolkit.learning import (
    SessionEvaluator,
    PatternExtractor,
    LearnedSkillsStorage,
)

# Evaluate
evaluator = SessionEvaluator()
result = evaluator.evaluate(collaboration_state)

if result.recommended_extraction:
    # Extract
    extractor = PatternExtractor()
    patterns = extractor.extract_patterns(state, session_id)

    # Store
    storage = LearnedSkillsStorage()
    storage.save_patterns(user_id, patterns)
```

## Configuration

| Setting | Default | Description |
|---------|---------|-------------|
| `min_score_for_extraction` | 0.4 | Minimum evaluation score |
| `max_patterns_per_session` | 10 | Patterns to extract per session |
| `max_patterns_per_user` | 100 | Total patterns stored per user |
| `min_confidence` | 0.3 | Minimum confidence to store |

## Quality Ratings

| Rating | Score Range | Action |
|--------|-------------|--------|
| EXCELLENT | 0.7+ | High priority extraction |
| GOOD | 0.5-0.7 | Standard extraction |
| AVERAGE | 0.3-0.5 | Optional extraction |
| POOR | 0.1-0.3 | Skip extraction |
| SKIP | <0.1 | Do not process |

## Best Practices

1. **Don't Over-Extract**
   - Focus on high-confidence patterns
   - Limit patterns per session
   - Periodically cleanup old patterns

2. **Respect Privacy**
   - No PII in patterns
   - No sensitive code
   - User can clear their data

3. **Validate Patterns**
   - Check confidence scores
   - Verify category accuracy
   - Remove duplicates

4. **Use Contextually**
   - Inject relevant patterns only
   - Filter by category when appropriate
   - Limit context injection size

## Attribution

Continuous learning patterns inspired by everything-claude-code by Affaan Mustafa.
See: https://github.com/affaan-m/everything-claude-code (MIT License)
