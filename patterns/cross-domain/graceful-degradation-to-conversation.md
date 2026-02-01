# Cross-Domain Transfer: Graceful Degradation → Conversation Quality

**Source Pattern:** [Graceful Degradation](../reliability/graceful-degradation.md)
**Source Domain:** Reliability Engineering
**Target Domain:** Conversational AI
**Transfer Type:** Strategy Mapping

## The Transfer Insight

When primary system functionality fails, graceful degradation maintains partial service. When AI conversation quality can't meet expectations, the same pattern provides **degraded but useful responses** rather than failure.

## Mapping

| Graceful Degradation | Conversation Quality |
|---------------------|----------------------|
| Primary service | Full, contextual response |
| Fallback 1 (cache) | Summarized response |
| Fallback 2 (DB) | Template response |
| Default value | Acknowledgment + escalation |
| Service failure | Can't answer well |

## Conversation Quality Fallback Chain

```
┌─────────────────┐    can't do    ┌─────────────────┐
│ Full Contextual │ ─────────────→ │   Summarized    │
│    Response     │                │    Response     │
└─────────────────┘                └────────┬────────┘
                                            │ can't do
                                            ↓
                                   ┌─────────────────┐
                                   │    Template     │
                                   │    Response     │
                                   └────────┬────────┘
                                            │ can't do
                                            ↓
                                   ┌─────────────────┐
                                   │  Acknowledge +  │
                                   │    Escalate     │
                                   └─────────────────┘
```

## Implementation Sketch

```python
@dataclass
class ConversationFallback:
    """Fallback chain for conversation quality."""

    async def respond(self, query: str, context: Context) -> Response:
        """Generate response with fallback chain."""

        # Level 1: Full contextual response
        try:
            if self._can_provide_full_response(query, context):
                return await self._full_response(query, context)
        except (ContextTooLarge, ModelUnavailable):
            pass

        # Level 2: Summarized response (less context)
        try:
            if self._can_provide_summary(query):
                return await self._summarized_response(query, context.summary())
        except InsufficientContext:
            pass

        # Level 3: Template response
        template = self._find_matching_template(query)
        if template:
            return Response(
                text=template.fill(query),
                quality="template",
                degraded=True
            )

        # Level 4: Acknowledge + escalate
        return Response(
            text="I don't have enough information to answer that well. "
                 "Could you provide more context, or would you like me to "
                 "search for relevant documentation?",
            quality="acknowledgment",
            degraded=True,
            escalation_options=["search_docs", "ask_clarifying", "transfer_human"]
        )
```

## Quality Levels

| Level | What User Gets | When Used |
|-------|----------------|-----------|
| Full | Complete, contextual answer | Normal operation |
| Summarized | Shorter, key points only | Context too large, time pressure |
| Template | Generic but relevant | Can't personalize |
| Acknowledgment | "I don't know, but..." | Can't help directly |

## Example: Code Review Degradation

```python
async def review_code(code: str, context: ProjectContext) -> Review:
    # Full review (ideal)
    if len(code) < 5000 and context.is_complete:
        return await full_review(code, context)

    # Summarized review (large files)
    if len(code) < 20000:
        return await summarized_review(code, context.summary())

    # Template review (very large)
    if len(code) < 50000:
        return template_review(code)  # Checklist-based

    # Acknowledgment (too large)
    return Review(
        text="This file is too large for a detailed review. "
             "Would you like me to review specific functions, "
             "or run automated linting?",
        suggestions=["review_function", "run_linter", "split_file"]
    )
```

## Key Adaptations

1. **Quality visibility** - Always tell users when response is degraded
2. **Offer alternatives** - Degraded response includes paths to better help
3. **No silent failure** - Even acknowledgment is a response
4. **Context-aware fallback** - Different fallbacks for different query types

## User Experience Principles

1. **Something is better than nothing** - A degraded answer beats an error
2. **Set expectations** - "Here's what I can do..." manages disappointment
3. **Provide exit ramps** - Always offer next steps
4. **Learn from degradation** - Track what causes fallbacks to improve

## Why This Transfer Works

Both patterns address **maintaining value when optimal service isn't possible**. The strategy (try best → fall back → acknowledge) is universal; only the definition of "service" changes.
