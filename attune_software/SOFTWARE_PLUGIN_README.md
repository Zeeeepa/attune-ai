# Software Development Plugin

> **DEPRECATION NOTICE (January 2026):** The `empathy_software_plugin.wizards` module has been removed. Please use CLI workflows instead.

Production-ready analysis tools for software development.

**Copyright 2025-2026 Smart AI Memory**
**Licensed under the Apache License, Version 2.0**

## Overview

The Software Development Plugin provides analysis capabilities through CLI workflows.

## Recommended Approach

```bash
# Security analysis
attune workflow run security-audit --path ./src

# Bug prediction
attune workflow run bug-predict --path ./src

# Test coverage analysis
attune workflow run test-coverage --path ./src
```

Or use the Python workflow API:

```python
from attune.workflows import BugPredictWorkflow

workflow = BugPredictWorkflow()
result = await workflow.execute(target_path="./src")
```

## Migration Guide

| Old Wizard | New Approach |
|------------|--------------|
| `EnhancedTestingWizard` | `attune workflow run test-coverage` |
| `PerformanceProfilingWizard` | `attune workflow run profile` |
| `SecurityAnalysisWizard` | `attune workflow run security-audit` |

## Installation

```bash
pip install attune-ai
```

## Support

- **Documentation:** [docs/](../docs/)
- **Issues:** [GitHub Issues](https://github.com/Smart-AI-Memory/attune-ai/issues)

## License

Copyright 2025-2026 Smart AI Memory - Licensed under the Apache License, Version 2.0
