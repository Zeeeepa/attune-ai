# Cost Optimization Skill

Use this skill when optimizing LLM costs in the Empathy Framework.

## Smart Tier System

### Tier Overview
| Tier | Models | Cost/1M tokens | Use Case |
|------|--------|----------------|----------|
| **cheap** | GPT-4o-mini, Haiku | ~$0.15 | Summarization, extraction |
| **capable** | GPT-4o, Sonnet 4.5 | ~$3.00 | Code review, bug fixing |
| **premium** | o1, Opus 4.5 | ~$15.00 | Architecture decisions |

### Potential Savings
- Using `cheap` instead of `capable`: **80-95% savings**
- Using `capable` instead of `premium`: **75-80% savings**

## Task-to-Tier Mapping

```python
TASK_TIER_RECOMMENDATIONS = {
    # CHEAP tier tasks
    "summarize": "cheap",
    "extract_keywords": "cheap",
    "format_text": "cheap",
    "simple_classification": "cheap",
    "count_items": "cheap",

    # CAPABLE tier tasks
    "code_review": "capable",
    "bug_fix": "capable",
    "write_tests": "capable",
    "explain_code": "capable",
    "refactor": "capable",

    # PREMIUM tier tasks
    "architecture_design": "premium",
    "security_audit": "premium",
    "complex_reasoning": "premium",
    "multi_step_planning": "premium",
}
```

## Implementation Pattern

```python
async def optimized_workflow(self) -> WorkflowResult:
    total_cost = 0.0

    # Step 1: Use CHEAP for initial extraction (saves 90%+)
    extraction = await self.executor.execute(
        prompt="Extract key points from this text...",
        tier="cheap"
    )
    total_cost += extraction.cost

    # Step 2: Use CAPABLE for analysis (main task)
    analysis = await self.executor.execute(
        prompt=f"Analyze these points: {extraction.content}",
        tier="capable"
    )
    total_cost += analysis.cost

    # Step 3: Use CHEAP for formatting (saves 90%+)
    formatted = await self.executor.execute(
        prompt=f"Format this as markdown: {analysis.content}",
        tier="cheap"
    )
    total_cost += formatted.cost

    return WorkflowResult(cost=total_cost, ...)
```

## Cost Monitoring

```bash
# Check workflow costs
python -m empathy_os.cli workflow code-review --path ./src

# View cost breakdown in output
# Example output:
# Completed in 2450ms | Cost: $0.0234
```

## Token Estimation

Before running expensive operations, estimate tokens:

```python
from empathy_os.models.token_estimator import estimate_tokens, estimate_cost

tokens = estimate_tokens(my_prompt)
estimated_cost = estimate_cost(tokens, model="claude-sonnet-4-5-20250514")
print(f"Estimated cost: ${estimated_cost:.4f}")
```

## Cost Reduction Strategies

1. **Batch Similar Tasks**: Combine multiple small prompts into one
2. **Cache Responses**: Don't re-query for identical inputs
3. **Truncate Context**: Only include relevant context, not full files
4. **Use Streaming**: For long outputs, stream to catch early errors
5. **Tier Fallback**: Start with `cheap`, only upgrade if quality insufficient
