---
name: dependency-check
description: "Dependency analysis. Triggers: 'check dependencies', 'outdated packages', 'vulnerable dependencies', 'update packages', 'license check', 'npm audit', 'pip check', 'dependency security', 'package versions', 'CVE in dependencies'."
---

# Dependency Check

Security and health analysis for project dependencies.

## Quick Start

```bash
# CLI
attune workflow run dependency-check

# Legacy alias
empathy workflow run dependency-check
```

## Usage

### Via Script

```bash
python scripts/run.py --path . --check-licenses
```

### Via Python

```python
from attune.workflows import DependencyCheckWorkflow

workflow = DependencyCheckWorkflow()
result = await workflow.execute()
print(result.vulnerabilities)
```

## Checks

- **Vulnerabilities**: CVE database lookup
- **Outdated**: Version comparison with latest
- **Licenses**: Compatibility analysis
- **Unused**: Dead dependency detection
- **Conflicts**: Version conflict identification

## Output

- Vulnerability report with severity
- Update recommendations
- License compliance matrix
- Dependency tree visualization
