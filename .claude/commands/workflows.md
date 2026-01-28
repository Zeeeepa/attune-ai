---
name: workflows
description: Run automated AI workflows with cost-optimized 3-tier model routing
category: hub
aliases: [wf, workflow]
tags: [workflows, automation, analysis, security, testing, hub]
version: "1.0"
question:
  header: "Workflow"
  question: "Which workflow do you want to run?"
  multiSelect: false
  options:
    - label: "🔒 Security audit"
      description: "Comprehensive security analysis with vulnerability detection"
    - label: "🐛 Bug prediction"
      description: "Predict potential bugs using learned patterns"
    - label: "⚡ Performance audit"
      description: "Identify performance bottlenecks and memory issues"
    - label: "📋 Browse all 23 workflows"
      description: "List all available workflows with descriptions"
---

# Automated Workflows

**Aliases:** `/wf`, `/workflow`

Run cost-optimized AI workflows that use 3-tier model routing for maximum efficiency.

## Quick Examples

```bash
/workflows                           # Interactive menu
/workflows run security-audit        # Run security analysis
/workflows run bug-predict ./src     # Predict bugs in src/
/workflows list                      # Show all workflows
```

## How Workflows Save You Money

Workflows use **3-tier model routing** to minimize costs while maximizing quality:

| Tier | Model | Cost | Used For |
|------|-------|------|----------|
| **CHEAP** | Claude Haiku | $0.80/M | Summarization, classification, triage |
| **CAPABLE** | Claude Sonnet | $3.00/M | Analysis, code generation, review |
| **PREMIUM** | Claude Opus | $15.00/M | Synthesis, architecture, coordination |

**Typical savings: 60-80%** vs using premium models for everything.

---

## Discovery

```yaml
Question:
  header: "Category"
  question: "What kind of workflow do you need?"
  options:
    - label: "Security & Quality"
      description: "Audit code for vulnerabilities, bugs, and performance issues"
    - label: "Testing"
      description: "Generate tests, boost coverage, run analysis"
    - label: "Documentation"
      description: "Generate and manage documentation"
    - label: "Release"
      description: "Prepare releases, check dependencies"
```

---

## Security & Quality Workflows

### security-audit

Scan code for security vulnerabilities using multi-tier analysis.

```bash
/workflows run security-audit
/workflows run security-audit ./src
```

**Stages:** scan (CHEAP) → analyze (CAPABLE) → recommend (PREMIUM)

**Output:** Security findings with severity, recommendations, and remediation steps.

---

### bug-predict

Predict likely bugs using pattern analysis and code smell detection.

```bash
/workflows run bug-predict
/workflows run bug-predict ./src
```

**Stages:** scan (CHEAP) → analyze (CAPABLE)

**Detects:**
- Dangerous `eval()`/`exec()` usage
- Broad exception handling
- TODO/FIXME comments
- Code complexity issues

---

### perf-audit

Analyze code for performance issues and optimization opportunities.

```bash
/workflows run perf-audit
/workflows run perf-audit ./src
```

**Stages:** scan (CHEAP) → analyze (CAPABLE) → optimize (PREMIUM)

**Output:** Performance score, hotspots, and optimization recommendations.

---

### code-review

Comprehensive code review with quality analysis.

```bash
/workflows run code-review
/workflows run code-review ./src/auth.py
```

**Stages:** analyze (CAPABLE)

**Checks:** Logic errors, security issues, maintainability, style.

---

## Testing Workflows

### test-gen

Generate test cases for uncovered code.

```bash
/workflows run test-gen
/workflows run test-gen ./src/utils.py
```

**Stages:** analyze (CAPABLE) → generate (PREMIUM)

**Output:** pytest test files with edge cases and assertions.

---

### test-coverage-boost

Multi-agent workflow to systematically improve test coverage.

```bash
/workflows run test-coverage-boost
```

**Uses meta-orchestration** with specialized agents for different testing concerns.

---

## Documentation Workflows

### doc-gen

Generate documentation from code.

```bash
/workflows run doc-gen
/workflows run doc-gen ./src/api/
```

**Stages:** analyze (CAPABLE) → generate (CAPABLE)

**Output:** Markdown documentation with API references.

---

### doc-orchestrator

Manage documentation across a project with intelligent updates.

```bash
/workflows run doc-orchestrator
```

**Meta-orchestrated** workflow for comprehensive documentation management.

---

## Release Workflows

### release-prep

Prepare a release with changelog, version bump, and checks.

```bash
/workflows run release-prep
/workflows run release-prep --version 2.0.0
```

**Stages:** analyze (CHEAP) → prepare (CAPABLE) → validate (PREMIUM)

---

### secure-release

Security-focused release pipeline with vulnerability scanning.

```bash
/workflows run secure-release
```

**Includes:** Dependency audit, security scan, release notes.

---

### dependency-check

Check dependencies for updates and vulnerabilities.

```bash
/workflows run dependency-check
```

**Stages:** scan (CHEAP)

**Output:** Outdated packages, security advisories, update recommendations.

---

## All Available Workflows

| Workflow | Description | Tiers |
|----------|-------------|-------|
| `security-audit` | Security vulnerability analysis | CHEAP → CAPABLE → PREMIUM |
| `bug-predict` | Bug and code smell detection | CHEAP → CAPABLE |
| `perf-audit` | Performance analysis | CHEAP → CAPABLE → PREMIUM |
| `code-review` | Comprehensive code review | CAPABLE |
| `test-gen` | Test case generation | CAPABLE → PREMIUM |
| `test-coverage-boost` | Coverage improvement | Meta-orchestrated |
| `doc-gen` | Documentation generation | CAPABLE |
| `doc-orchestrator` | Documentation management | Meta-orchestrated |
| `release-prep` | Release preparation | CHEAP → CAPABLE → PREMIUM |
| `secure-release` | Security-focused release | Multi-stage |
| `dependency-check` | Dependency analysis | CHEAP |
| `pr-review` | Pull request review | CAPABLE → PREMIUM |
| `refactor-plan` | Refactoring analysis | CAPABLE |
| `keyboard-shortcuts` | Generate keyboard shortcuts | CAPABLE |

---

## Running Workflows

### From Claude Code

```bash
/workflows run <name> [path]
```

### From CLI

```bash
empathy workflow list                      # List workflows
empathy workflow run security-audit        # Run workflow
empathy workflow run bug-predict --path ./src
empathy workflow run perf-audit --json     # JSON output for CI
```

### From Python

```python
from empathy_os.workflows import SecurityAuditWorkflow
import asyncio

async def main():
    workflow = SecurityAuditWorkflow()
    result = await workflow.execute(target_path="./src")

    print(f"Found {len(result.findings)} issues")
    print(f"Cost: ${result.cost_report.total_cost:.4f}")
    print(f"Saved: {result.cost_report.savings_percent:.1f}%")

asyncio.run(main())
```

---

## Progress Output

Workflows show real-time progress in your IDE:

```text
[  0%] ► Starting security-audit... ($0.0000)
[ 33%] ► Running scan... [CHEAP] ($0.0012) [2.3s]
[ 67%] ✓ Completed analyze [CAPABLE] ($0.0089) [8.1s]
[100%] ✓ Workflow completed ($0.0134) [12.3s]

──────────────────────────────────────────────────
Stage Summary:
  scan: 2.3s | $0.0012 | CHEAP
  analyze: 8.1s | $0.0089 | CAPABLE
  recommend: 2.0s | $0.0033 | PREMIUM
──────────────────────────────────────────────────
Total: $0.0134 | Saved: $0.0421 (76%)
```

---

## When NOT to Use This Hub

| If you need...              | Use instead |
| --------------------------- | ----------- |
| Plan before coding          | `/plan`     |
| Debug an issue              | `/dev`      |
| Run existing tests          | `/testing`  |
| Create commit/PR            | `/dev`      |

## Related Hubs

- `/plan` - Structured development approaches (TDD, planning, review)
- `/dev` - Debugging, commits, PRs
- `/testing` - Run tests, coverage analysis
- `/release` - Release and deployment
