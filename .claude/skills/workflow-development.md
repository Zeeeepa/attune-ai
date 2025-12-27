# Workflow Development Skill

Use this skill when creating or modifying Empathy Framework workflows.

## Context

Empathy Framework workflows are in `src/empathy_os/workflows/`. Each workflow:
- Inherits from `EmpathyWorkflow` base class
- Implements `execute()` async method
- Returns a dataclass result with `cost`, `duration_seconds`, and formatted `report`
- Uses the multi-tier executor for cost optimization

## Workflow Structure

```python
from dataclasses import dataclass
from empathy_os.workflows.base import EmpathyWorkflow, WorkflowResult

@dataclass
class MyWorkflowResult(WorkflowResult):
    """Custom result fields."""
    specific_data: str = ""

    def format_report(self) -> str:
        """Format as human-readable report."""
        lines = [
            "# My Workflow Report",
            "",
            f"**Result**: {self.specific_data}",
            "",
            "---",
            f"Completed in {self.duration_seconds * 1000:.0f}ms | Cost: ${self.cost:.4f}"
        ]
        return "\n".join(lines)

class MyWorkflow(EmpathyWorkflow[MyWorkflowResult]):
    """Description of what this workflow does."""

    name = "my-workflow"
    description = "Brief description"

    async def execute(self, **kwargs) -> MyWorkflowResult:
        start_time = time.time()
        total_cost = 0.0

        # Use appropriate tier for each task
        # cheap: summarization, simple extraction
        # capable: code review, bug fixing
        # premium: architecture decisions

        result = await self.executor.execute(
            prompt="...",
            tier="capable"
        )
        total_cost += result.cost

        duration = time.time() - start_time
        return MyWorkflowResult(
            success=True,
            cost=total_cost,
            duration_seconds=duration,
            specific_data=result.content
        )
```

## Key Patterns

1. **Tier Selection**: Use `cheap` for 80-96% cost savings on simple tasks
2. **Cost Tracking**: Always accumulate `result.cost` from each executor call
3. **Report Format**: Use milliseconds for duration, 4 decimal places for cost
4. **Error Handling**: Set `success=False` and include error in report

## Registration

Add to `src/empathy_os/workflows/__init__.py`:
```python
from .my_workflow import MyWorkflow
WORKFLOWS["my-workflow"] = MyWorkflow
```

## Testing

```bash
python -m empathy_os.cli workflow my-workflow --arg value
```
