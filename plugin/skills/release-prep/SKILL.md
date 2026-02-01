---
name: release-prep
description: "Release preparation. Triggers: 'prepare release', 'release prep', 'ready to release', 'release checklist', 'pre-release', 'ship it', 'deploy', 'version bump', 'changelog', 'release candidate', 'go live'."
---

# Release Preparation

Multi-agent release readiness verification.

## Quick Start

```bash
# CLI (primary)
attune orchestrate release-prep

# Legacy alias
empathy orchestrate release-prep

# Natural language:
"prepare for release"
"is this ready to ship?"
"run release checklist"
```

## Usage

### Via MCP Tool

The `release_prep` tool is available via MCP:

```python
# Invoked automatically when you describe:
"Prepare for release"
"Check release readiness"
"Run release verification"
```

### Via Python

```python
from attune.orchestration import ReleasePrep

release = ReleasePrep()
result = await release.execute()
print(result.ready_for_release)
```

## Parallel Checks

4 agents run concurrently:

1. **Security Agent**: Vulnerability scan
2. **Test Agent**: Full test suite execution
3. **Docs Agent**: Documentation completeness
4. **Quality Agent**: Code quality metrics

## Output

Returns:
- Release readiness status (go/no-go)
- Individual agent reports
- Blocking issues list
- Generated changelog
- Version recommendation
