---
name: health-check
description: "Project health assessment. Triggers: 'health check', 'project health', 'full audit', 'how healthy is my code', 'project status', 'quality metrics', 'overall assessment', 'codebase health', 'comprehensive check'."
---

# Health Check

Multi-agent parallel health assessment.

## Quick Start

```bash
# CLI
attune orchestrate health-check

# Legacy alias
empathy orchestrate health-check
```

## Usage

### Via Script

```bash
python scripts/run.py --path . --full
```

### Via Python

```python
from attune.orchestration import HealthCheckOrchestrator

orchestrator = HealthCheckOrchestrator()
result = await orchestrator.execute()
print(result.health_score)
```

## Parallel Checks

Runs 6 agents concurrently:

1. **Security Agent**: Vulnerability scan
2. **Test Agent**: Coverage and test health
3. **Docs Agent**: Documentation completeness
4. **Quality Agent**: Code quality metrics
5. **Dependency Agent**: Package health
6. **Performance Agent**: Bottleneck detection

## Output

- Overall health score (0-100)
- Individual agent reports
- Trend comparison (vs last run)
- Priority action items
