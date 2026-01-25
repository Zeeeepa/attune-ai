---
name: testing
description: Testing hub - run tests, coverage analysis, maintenance, benchmarks
category: hub
aliases: [test-hub, tests]
tags: [testing, coverage, benchmarks, hub]
version: "2.0"
---

# Testing

**Aliases:** `/test-hub`, `/tests`

Run tests, analyze coverage, and benchmark performance.

## Quick Examples

```bash
/testing                    # Interactive menu
/testing "run unit tests"   # Run tests
/testing "check coverage"   # Coverage analysis
```

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

---

## Run Tests

Execute test suite and analyze results.

**Tell me:**

- Specific tests to run (or blank for full suite)
- Any flags needed (e.g., `-v`, `-x`, `--pdb`)

**I will:**

1. Run pytest with appropriate options
2. Analyze failures and errors
3. Identify patterns in failures
4. Suggest fixes for broken tests
5. Report summary of results

**Common patterns:**

```bash
pytest                           # Full suite
pytest tests/unit/               # Directory
pytest -k "test_name"            # By name
pytest -x                        # Stop on first failure
pytest --pdb                     # Debug on failure
pytest -v --tb=short             # Verbose, short traceback
```

---

## Coverage Analysis

Analyze test coverage and identify gaps.

**I will:**

1. Run `pytest --cov=src --cov-report=term-missing`
2. Identify files with low coverage
3. Find uncovered code paths
4. Prioritize what to test next
5. Suggest test cases for gaps

**Coverage targets:**

- Critical paths: 90%+
- Core modules: 80%+
- Utilities: 70%+

---

## Test Maintenance

Clean up and organize the test suite.

**I will:**

1. Find duplicate tests
2. Identify flaky tests
3. Check for slow tests
4. Review test organization
5. Suggest improvements

**Common issues:**

- Tests without assertions
- Overly complex setup
- Missing teardown
- Hardcoded values
- Brittle selectors

---

## Run Benchmarks

Performance benchmarking and regression detection.

**Tell me:**

- What to benchmark (function, module, or workflow)
- Baseline to compare against (optional)

**I will:**

1. Run `pytest-benchmark` or custom benchmarks
2. Measure execution time
3. Compare against baseline
4. Identify performance regressions
5. Suggest optimizations

---

## When NOT to Use This Hub

| If you need...       | Use instead |
| -------------------- | ----------- |
| Debug a failure      | `/dev`      |
| Review code quality  | `/workflow` |
| Write new tests      | `/workflow` |
| Deploy/release       | `/release`  |

## Related Hubs

- `/dev` - Debug failures, commits
- `/workflow` - TDD, code review
- `/release` - Pre-release validation
