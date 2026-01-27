---
name: testing
description: Testing hub - run tests, coverage analysis, TDD, benchmarks
category: hub
aliases: [test-hub, tests]
tags: [testing, coverage, benchmarks, hub]
version: "3.0"
question:
  header: "Testing Task"
  question: "What testing task do you need?"
  multiSelect: false
  options:
    - label: "🧪 Run & analyze tests"
      description: "Execute tests with failure analysis and coverage report"
    - label: "✨ Generate tests"
      description: "AI-powered test generation for your code"
    - label: "🎯 TDD session"
      description: "Test-driven development with red-green-refactor"
    - label: "⚡ Benchmarks"
      description: "Performance benchmarking and profiling"
---

# Testing

**Aliases:** `/test-hub`, `/tests`

Testing operations powered by Socratic agents that help you understand failures and design better tests.

## Quick Examples

```bash
/testing                    # Interactive menu
/testing run                # Run tests with guided failure analysis
/testing coverage           # Coverage analysis with risk prioritization
/testing tdd                # Test-driven development guidance
/testing benchmark          # Performance benchmarking
```

## Discovery

```yaml
Question:
  header: "Task"
  question: "What testing task do you need?"
  options:
    - label: "Run tests"
      description: "Execute tests with guided failure analysis"
    - label: "Coverage analysis"
      description: "Find gaps prioritized by risk"
    - label: "TDD workflow"
      description: "Test-driven development guidance"
    - label: "Benchmarks"
      description: "Performance testing and regression detection"
```

---

## Run Tests

**Agent:** `test-writer` | **Workflow:** `test_runner`

Execute tests with Socratic failure analysis that helps you understand *why* tests fail.

**Invoke:**

```bash
/testing run                    # Run full test suite
/testing run tests/unit/        # Run specific directory
/testing run -k "auth"          # Run tests matching pattern
/testing run --failed           # Re-run failed tests only
```

**The test-writer agent will:**

1. Run pytest with your chosen options
2. For failures, guide you through understanding *why* it failed
3. Ask: "Where does this value come from? What would cause it to be None?"
4. Help you distinguish test bugs from code bugs
5. Suggest whether to fix the test or the code

**Philosophy:** Instead of just showing "AssertionError: None != User", you'll hear "The test expects a User but got None. Let's trace: where does the User come from in this test?"

---

## Coverage Analysis

**Agent:** `quality-validator` | **Workflow:** `test_coverage_boost`

Coverage analysis that prioritizes gaps by *risk*, not just percentage.

**Invoke:**

```bash
/testing coverage               # Analyze overall coverage
/testing coverage src/auth/     # Focus on specific module
/testing coverage --target 80   # Aim for specific target
```

**The quality-validator agent will:**

1. Run coverage analysis
2. Identify gaps by *risk*, not just by line count
3. Ask: "What happens if this uncovered branch executes in production?"
4. Help you prioritize what actually matters to test
5. Suggest test cases that provide the most value

**Philosophy:** Instead of "Lines 78-85 not covered", you'll hear "These uncovered lines handle payment failures. Which is riskier: missing a happy path test or missing error handling coverage?"

**Coverage targets (guidelines):**

- Critical paths (auth, payments, data): 90%+
- Core business logic: 80%+
- Utilities and helpers: 70%+

---

## TDD Workflow

**Agent:** `test-writer` | **Workflow:** `test_gen`

Test-driven development with guided test design.

**Invoke:**

```bash
/testing tdd                         # Start TDD session
/testing tdd "add user validation"   # TDD for specific feature
```

**The test-writer agent will:**

1. Understand what you're building
2. Guide you to think about edge cases first
3. Ask: "What's the simplest case? What could go wrong?"
4. Help you write the test before the code
5. Guide red → green → refactor cycle

**Philosophy:** Instead of writing code then tests, you'll hear "Before we write `validate_email()`, what should it do when given an empty string? What about a string with no @ symbol?"

---

## Test Maintenance

**Agent:** `quality-validator` | **Workflow:** `test_maintenance`

Clean up and improve test suite quality.

**Invoke:**

```bash
/testing maintenance            # Analyze test suite health
/testing maintenance --flaky    # Focus on flaky tests
```

**The quality-validator agent will:**

1. Find duplicate tests
2. Identify flaky tests
3. Check for slow tests
4. Review test organization
5. Suggest improvements

**Common issues detected:**

- Tests without assertions
- Overly complex setup
- Missing teardown
- Hardcoded values
- Brittle selectors

---

## Run Benchmarks

**Agent:** `performance-analyst` | **Workflow:** benchmarking

Performance testing and regression detection.

**Invoke:**

```bash
/testing benchmark                    # Run all benchmarks
/testing benchmark src/core/parser    # Benchmark specific module
/testing benchmark --compare main     # Compare against baseline
```

**The performance-analyst agent will:**

1. Run pytest-benchmark or custom benchmarks
2. Measure execution time and memory usage
3. Compare against baseline
4. Identify performance regressions
5. Guide you to understand *why* something is slow

**Philosophy:** Instead of "Function X is 200ms slower", you'll hear "This function got slower. Looking at the diff, what changed? What operations might scale poorly?"

---

## Agent-Skill-Workflow Mapping

| Skill | Agent | Workflow | When to Use |
|-------|-------|----------|-------------|
| `/testing run` | test-writer | test_runner | Running tests, understanding failures |
| `/testing coverage` | quality-validator | test_coverage_boost | Finding and prioritizing coverage gaps |
| `/testing tdd` | test-writer | test_gen | Writing tests before code |
| `/testing maintenance` | quality-validator | test_maintenance | Cleaning up test suite |
| `/testing benchmark` | performance-analyst | (benchmarking) | Performance testing |

---

## When to Use Each Skill

```text
Tests are failing                → /testing run
Need more test coverage          → /testing coverage
Building new feature with TDD    → /testing tdd
Test suite is messy/slow         → /testing maintenance
Checking for performance issues  → /testing benchmark
```

---

## When NOT to Use This Hub

| If you need...       | Use instead |
|----------------------|-------------|
| Debug a failure      | `/dev debug` |
| Review code quality  | `/dev review` |
| Deploy/release       | `/release` |
| Write documentation  | `/docs` |

## Related Hubs

- `/dev` - Debug failures, code review
- `/release` - Pre-release validation
- `/workflows` - Run automated workflows (security-audit, test-gen, etc.)
- `/plan` - Feature planning
- `/agent` - Direct agent invocation
