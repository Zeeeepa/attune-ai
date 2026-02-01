---
name: test-coverage
description: "Test coverage analysis. Triggers: 'test coverage', 'coverage report', 'improve coverage', 'untested code', 'coverage target', '80% coverage', '90% coverage', 'missing tests', 'coverage gaps', 'what's not tested'."
---

# Test Coverage

Coverage analysis and automated test generation to hit targets.

## Quick Start

```bash
# CLI
attune workflow run test-coverage --target 90

# Legacy alias
empathy workflow run test-coverage --target 90
```

## Usage

### Via Script

```bash
python scripts/run.py --target 90 --path ./src
```

### Via Python

```python
from attune.workflows import TestCoverageWorkflow

workflow = TestCoverageWorkflow()
result = await workflow.execute(
    coverage_target=90,
    generate_missing=True
)
```

## Features

- Line and branch coverage analysis
- Uncovered path identification
- Automatic test generation for gaps
- Coverage trend tracking
- CI/CD integration support

## Output

- Current coverage metrics
- Gap analysis by file/function
- Generated test files
- Coverage improvement plan
