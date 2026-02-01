---
name: perf-audit
description: "Performance analysis. Triggers: 'performance audit', 'find bottlenecks', 'slow code', 'optimize performance', 'memory leak', 'speed up', 'profiling', 'latency', 'throughput', 'scaling issues', 'why is this slow', 'performance issues'."
---

# Performance Audit

AI-powered performance analysis and optimization.

## Quick Start

```bash
# CLI (primary)
attune workflow run perf-audit --path ./src

# Legacy alias
empathy workflow run perf-audit --path ./src

# Natural language:
"find performance bottlenecks"
"why is my code slow?"
"check for memory leaks"
```

## Usage

### Via MCP Tool

The `performance_audit` tool is available via MCP:

```python
# Invoked automatically when you describe:
"Analyze performance bottlenecks"
"Find slow code"
"Optimize this module"
```

### Via Python

```python
from attune.workflows import PerformanceAuditWorkflow

workflow = PerformanceAuditWorkflow()
result = await workflow.execute(target_path="./src")
print(result.bottlenecks)
```

## Analysis Areas

- **Algorithm Complexity**: O(n²) patterns, inefficient loops
- **Memory Usage**: Leaks, unnecessary allocations
- **I/O Operations**: Blocking calls, connection pooling
- **Database Queries**: N+1 queries, missing indexes
- **Caching Opportunities**: Repeated computations

## Output

Returns:
- Prioritized performance issues
- Impact estimates
- Specific optimization suggestions
- Before/after code examples
