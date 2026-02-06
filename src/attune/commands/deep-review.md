---
name: deep-review
description: Multi-pass deep code review — security, quality, and test gaps
category: hub
aliases: [review, dr]
tags: [review, security, quality, coverage, orchestration]
version: "1.0.0"
question:
  header: "Deep Review"
  question: "What would you like to review?"
  multiSelect: false
  options:
    - label: "Full review"
      description: "Security + quality + test gap analysis on a path"
    - label: "Security only"
      description: "CWE-focused vulnerability scan"
    - label: "Quality only"
      description: "Code quality and style analysis"
    - label: "Test gaps only"
      description: "Coverage analysis and missing test detection"
---

# deep-review

Multi-pass deep code review orchestrating security analysis, code quality checks, and test gap detection into a single synthesized report.

## Quick Shortcuts

| Shortcut | Action |
| -------- | ------ |
| `/deep-review <path>` | Full 3-pass review of target |
| `/deep-review security <path>` | Security-only pass |
| `/deep-review quality <path>` | Quality-only pass |
| `/deep-review tests <path>` | Test gap analysis only |

## Natural Language

Describe what you need:

- "deep review the auth module"
- "do a full review of src/attune/workflows/"
- "check security and test coverage for config.py"

## CRITICAL: Workflow Execution Instructions

**When this command is invoked with arguments, you MUST execute the review, not answer ad-hoc.**

### Context Gathering (ALWAYS DO FIRST)

Before executing any action below, gather current project context:

1. Run: `git status --short`
2. Run: `git log --oneline -5`
3. Run: `git branch --show-current`

Use this context to inform review scope (e.g., focus on recently changed files).

### Reasoning Approach

For deep reviews, use structured multi-pass reasoning:

<analysis-steps>
1. **Security pass** — Scan for CWE-95 (eval/exec), CWE-22 (path traversal), BLE001 (broad exceptions), B602 (shell injection), hardcoded secrets. Classify each as CRITICAL/HIGH/MEDIUM/LOW.
2. **Quality pass** — Check type hints, docstrings, line length, function complexity, duplicate code. Score each dimension 0-100.
3. **Test gap pass** — Run coverage analysis, identify untested public APIs, flag missing edge case and error handling tests.
4. **False positive filtering** — Cross-reference findings against known false positives (scanner-patterns.md): test fixtures, JavaScript .exec(), intentional broad catches.
5. **Synthesis** — Combine all passes into severity-sorted report with aggregate health score, blocking issues first, then improvements.
</analysis-steps>

### Shortcut Routing (EXECUTE THESE)

| Input | Action |
| ----- | ------ |
| `/deep-review <path>` | Run all 3 passes below, then synthesize |
| `/deep-review security <path>` | Run security pass only |
| `/deep-review quality <path>` | Run quality pass only |
| `/deep-review tests <path>` | Run test gap pass only |

### Pass 1: Security Review

Run read-only security analysis on the target:

```bash
uv run attune workflow run security-audit --path <target>
```

Focus areas (from coding standards):

- `eval()` / `exec()` usage (CWE-95) — CRITICAL
- Path traversal without `_validate_file_path()` (CWE-22) — CRITICAL
- Bare `except:` without `# INTENTIONAL:` (BLE001) — HIGH
- Hardcoded secrets — HIGH
- Shell injection risks (B602) — HIGH

### Pass 2: Code Quality

Run code quality analysis:

```bash
uv run attune workflow run code-review --path <target>
```

Check dimensions:

- Type hints on all public APIs
- Google-style docstrings
- Line length ≤100 characters
- Function complexity (flag functions >50 lines)
- No magic numbers

### Pass 3: Test Gap Analysis

Run coverage analysis on the target:

```bash
uv run pytest --cov=<target> --cov-report=term-missing -q
```

Identify:

- Public functions with 0% coverage
- Missing error handling tests
- Missing edge case tests
- Security tests required for file operations

### Synthesis: Combined Report

After all passes complete, produce a combined report:

```text
## Deep Review: <target>

**Health Score:** X/100
**Blocking Issues:** Y | **Improvements:** Z

### Security Findings
| Severity | File:Line | CWE | Finding | Fix |
|----------|-----------|-----|---------|-----|
| ...      | ...       | ... | ...     | ... |

### Quality Scores
| Dimension   | Score |
|-------------|-------|
| Type Hints  | X/100 |
| Docstrings  | X/100 |
| Complexity  | X/100 |
| Style       | X/100 |

### Test Gaps
| Module | Coverage | Missing Tests |
|--------|----------|---------------|
| ...    | ...      | ...           |

### Recommendations (Priority Order)
1. [BLOCKING] ...
2. [HIGH] ...
3. [MEDIUM] ...
```

### Natural Language Routing (EXECUTE THESE)

| Pattern | Action |
| ------- | ------ |
| "deep review", "full review", "review everything" | Run all 3 passes |
| "security", "vulnerabilities", "cwe" | Security pass only |
| "quality", "style", "lint" | Quality pass only |
| "test", "coverage", "gaps" | Test gap pass only |

**IMPORTANT:** When arguments are provided, DO NOT just display documentation. EXECUTE the review passes.
