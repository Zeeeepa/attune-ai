# /release-prep - Release Preparation Workflow

Comprehensive release readiness assessment using AI agent analysis.

## What This Does

Runs 4 specialized analyses to check your code before release:

- **Security Audit** - Vulnerabilities, secrets, dependency issues
- **Test Coverage** - Verify coverage meets 80% threshold
- **Code Quality** - Linting, complexity, best practices
- **Documentation** - API docs, README, CHANGELOG completeness

## Usage

```
/release-prep
```

## Instructions for Claude

When the user invokes /release-prep, execute these steps using the Task tool.
This runs entirely within Claude Code using the user's Max subscription ($0 cost).

### Step 1: Security Audit

Use the Task tool with subagent_type="Explore":

```
Analyze this codebase for security vulnerabilities:

1. Search for dangerous patterns:
   - eval() or exec() usage (search with Grep)
   - SQL injection risks
   - Command injection (subprocess with shell=True)
   - Hardcoded secrets or API keys

2. Check for path traversal vulnerabilities
3. Review authentication/authorization patterns

Report as CRITICAL/HIGH/MEDIUM severity.
```

### Step 2: Test Coverage Analysis

First run coverage check with Bash:

```bash
pytest --cov=src --cov-report=term-missing -q 2>&1 | head -80
```

Then analyze with Task (subagent_type="Explore"):

```
Based on the coverage output:
1. What is the current coverage %?
2. Which files are below 80%?
3. Which uncovered paths are highest risk?
4. Any failing tests?
```

### Step 3: Code Quality Review

Run linting with Bash:

```bash
ruff check src/ --statistics 2>&1 | head -40
```

Then analyze results - identify top quality issues.

### Step 4: Documentation Check

Use Task (subagent_type="Explore", model="haiku"):

```
Check documentation completeness:
1. Public APIs have docstrings?
2. README.md is current?
3. CHANGELOG.md updated for this release?
```

### Step 5: Synthesize Final Report

Create a release readiness report:

```markdown
## Release Readiness Report

### Overall Status: [READY / NEEDS WORK / BLOCKED]

| Area | Status | Issues |
|------|--------|--------|
| Security | PASS/FAIL | X critical, Y high |
| Test Coverage | X% (target 80%) | PASS/FAIL |
| Code Quality | PASS/FAIL | X issues |
| Documentation | PASS/FAIL | X gaps |

### Blockers (must fix)
- [list any critical issues]

### Recommendations
- [list improvements]

### Release Decision
[Ready to release / Fix blockers first / Needs more work]
```

## Cost

**$0** - Runs entirely within Claude Code using your Max subscription.

## Alternative: API Mode

To use the API-based execution instead (costs $0.10-$0.75):

```bash
empathy meta-workflow run release-prep --real --use-defaults
```
