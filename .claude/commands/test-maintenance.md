# /test-maintenance - Test Maintenance Workflow

Automated test lifecycle management using AI-powered analysis.

## What This Does

Runs 4 specialized analyses to maintain test health:

- **Stale Test Detector** - Find outdated or broken tests
- **Coverage Gap Analyzer** - Identify untested code paths
- **Flaky Test Finder** - Detect unreliable tests
- **Test Health Reporter** - Generate actionable report

## Usage

```
/test-maintenance
```

## Instructions for Claude

When the user invokes /test-maintenance, execute these steps using the Task tool.
This runs entirely within Claude Code using the user's Max subscription ($0 cost).

### Step 1: Run Test Suite and Collect Metrics

Run tests with verbose output:

```bash
pytest tests/ -v --tb=short 2>&1 | tail -100
```

Note any failures or errors.

### Step 2: Detect Stale Tests

Use the Task tool with subagent_type="Explore":

```
Analyze the test suite for stale or problematic tests:

1. Find tests that haven't been updated recently but test changed code
2. Identify tests with hardcoded dates or values that may be outdated
3. Look for tests that test removed or renamed functions
4. Find tests with TODO/FIXME/skip markers that need attention

Check tests/ directory and compare with recent src/ changes.
```

### Step 3: Find Flaky Tests

Use the Task tool with subagent_type="Explore":

```
Identify potentially flaky tests:

1. Tests that depend on timing (sleep, timeouts)
2. Tests that depend on external services
3. Tests with random elements without fixed seeds
4. Tests that passed/failed inconsistently in recent runs

Look for patterns like: time.sleep, datetime.now(), random., external URLs
```

### Step 4: Analyze Test Organization

Use the Task tool with subagent_type="Explore":

```
Review test organization and quality:

1. Are tests well-organized by module?
2. Are there duplicate tests testing the same thing?
3. Are test names descriptive?
4. Are fixtures being reused appropriately?

Identify opportunities to improve test maintainability.
```

### Step 5: Generate Maintenance Report

Create a test maintenance report:

```markdown
## Test Maintenance Report

### Test Suite Health: [HEALTHY / NEEDS ATTENTION / CRITICAL]

### Summary
- Total tests: X
- Passing: Y
- Failing: Z
- Skipped: N

### Stale Tests Found

| Test | Issue | Recommendation |
|------|-------|----------------|
| test_x | Tests removed function | Delete or update |

### Potentially Flaky Tests

| Test | Risk Factor | Fix |
|------|-------------|-----|
| test_y | Uses time.sleep | Mock time |

### Maintenance Actions

1. **High Priority**
   - [list critical fixes]

2. **Medium Priority**
   - [list improvements]

3. **Low Priority**
   - [list nice-to-haves]
```

## Cost

**$0** - Runs entirely within Claude Code using your Max subscription.

## Alternative: API Mode

To use the API-based execution instead (costs $0.10-$0.80):

```bash
empathy meta-workflow run test-maintenance --real --use-defaults
```
