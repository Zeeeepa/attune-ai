# Choose Your Path

You've installed the framework and run your first workflow. Now choose the approach that fits your needs.

---

## Three Ways to Use Empathy Framework

| Path | Best For | Complexity |
|------|----------|------------|
| [CLI Power User](#path-1-cli-power-user) | Quick tasks, automation, CI/CD | Simple |
| [Workflow Developer](#path-2-workflow-developer) | Custom automations, Python integration | Moderate |
| [Meta-Orchestration](#path-3-meta-orchestration) | Complex tasks, multi-agent teams | Advanced |

---

## Path 1: CLI Power User

**Best for:** Quick tasks, shell scripts, CI/CD pipelines

Use the `empathy` CLI to run pre-built workflows without writing Python.

### Key Commands

```bash
# Run workflows
empathy workflow run security-audit --path ./src
empathy workflow run bug-predict --path ./src
empathy workflow run release-prep --path .

# Track costs
empathy telemetry show
empathy telemetry savings --days 30
```

### Next Steps

- [CLI Guide](../reference/CLI_GUIDE.md) - Complete command reference
- [CLI Cheatsheet](../reference/CLI_CHEATSHEET.md) - Quick reference

---

## Path 2: Workflow Developer

**Best for:** Custom automations, integrating AI into Python apps

Use the Python API to run and build workflows.

### Using Built-in Workflows

```python
from empathy_os.workflows import SecurityAuditWorkflow
import asyncio

async def audit():
    workflow = SecurityAuditWorkflow()
    result = await workflow.execute(target_path="./src")
    print(f"Found {len(result.findings)} issues")

asyncio.run(audit())
```

### Next Steps

- [Practical Patterns](../how-to/practical-patterns.md) - Ready-to-use patterns
- [Examples](../tutorials/examples/simple-chatbot.md) - Working code

---

## Path 3: Meta-Orchestration

**Best for:** Complex tasks needing multiple AI agents

Describe what you want and let the framework compose agent teams.

```python
from empathy_os.orchestration import MetaOrchestrator

orchestrator = MetaOrchestrator()
plan = orchestrator.analyze_and_compose(
    task="Review code for security and suggest performance improvements",
    context={"path": "./src"}
)
result = await orchestrator.execute(plan)
```

### Next Steps

- [Meta-Orchestration Tutorial](../tutorials/META_ORCHESTRATION_TUTORIAL.md)
- [Multi-Agent Philosophy](../explanation/multi-agent-philosophy.md)

---

## Still Not Sure?

**Start with the CLI.** Move to Workflows when you need custom logic, and Meta-Orchestration when tasks get complex.
