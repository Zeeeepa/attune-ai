---
name: testing
description: Testing hub - run tests, coverage analysis, maintenance, benchmarks
category: hub
aliases: [test-hub, tests]
tags: [testing, coverage, benchmarks, hub]
version: "1.0"
---

# Testing

Run tests, analyze coverage, and benchmark performance.

## Discovery

```yaml
Question:
  header: "Task"
  question: "What testing task do you need?"
  options:
    - label: "Run tests"
      description: "Execute test suite and analyze results"
    - label: "Coverage analysis"
      description: "Analyze test coverage and find gaps"
    - label: "Test maintenance"
      description: "Clean up and organize test suite"
    - label: "Run benchmarks"
      description: "Performance benchmarking"
```

## Routing

Based on selection:

| Selection | Command | Description |
|-----------|---------|-------------|
| Run tests | `/test` | Run tests with result analysis |
| Coverage analysis | `/test-coverage` | Analyze coverage and gaps |
| Test maintenance | `/test-maintenance` | Clean up test suite |
| Run benchmarks | `/benchmark` | Run performance benchmarks |

## Quick Access

- `/test` - Run full test suite
- `/test path/to/test.py` - Run specific tests
- `/test-coverage` - Analyze test coverage
- `/test-maintenance` - Clean up tests
- `/benchmark` - Run benchmarks

## Test Workflows

| Workflow | Use Case | Command |
|----------|----------|---------|
| Quick validation | Verify changes work | `/test` |
| Coverage check | Find untested code | `/test-coverage` |
| Suite cleanup | Remove flaky/duplicate tests | `/test-maintenance` |
| Performance | Measure and compare speed | `/benchmark` |

## When to Use Each

**Use `/test` when:**
- Before committing changes
- After refactoring
- Validating a fix
- Running CI locally

**Use `/test-coverage` when:**
- Reviewing test quality
- Finding untested code paths
- Before releases
- Setting coverage goals

**Use `/test-maintenance` when:**
- Tests are flaky or slow
- Suite needs organization
- Removing dead tests
- Improving test quality

**Use `/benchmark` when:**
- Measuring performance
- Comparing implementations
- Before/after optimization
- Detecting regressions
