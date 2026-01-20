# /test-coverage - Test Coverage Boost Workflow

Analyze and improve test coverage using AI-powered analysis.

## What This Does

Runs 3 specialized analyses to boost test coverage:

- **Gap Analyzer** - Identifies coverage gaps and prioritizes by impact
- **Test Generator** - Suggests tests for uncovered code paths
- **Test Validator** - Verifies test quality and coverage improvement

## Usage

```
/test-coverage
```

## Instructions for Claude

When the user invokes /test-coverage, execute these steps using the Task tool.
This runs entirely within Claude Code using the user's Max subscription ($0 cost).

### Step 1: Measure Current Coverage

Run coverage analysis with Bash:

```bash
pytest --cov=src --cov-report=term-missing --cov-report=html -q 2>&1 | tail -50
```

Record the current coverage percentage.

### Step 2: Gap Analysis

Use the Task tool with subagent_type="Explore":

```
Analyze the codebase for test coverage gaps:

1. Based on the coverage report, which files have the lowest coverage?
2. For each low-coverage file, identify:
   - Which functions/methods are untested
   - Which code paths are not covered
   - The risk level (high/medium/low) based on code complexity

3. Prioritize gaps by:
   - Business impact (core functionality first)
   - Risk of bugs
   - Ease of testing

Output a prioritized list of coverage gaps to address.
```

### Step 3: Generate Test Suggestions

Use the Task tool with subagent_type="Explore":

```
For the top 3 coverage gaps identified, generate test suggestions:

1. Read the untested code
2. Identify test cases needed:
   - Happy path tests
   - Edge cases
   - Error handling
3. Provide pytest-style test code that would cover these paths

Focus on high-value tests that catch real bugs.
```

### Step 4: Synthesize Report

Create a coverage improvement report:

```markdown
## Test Coverage Report

### Current Status
- Coverage: X%
- Target: 80%
- Gap: Y%

### Top Coverage Gaps (by priority)

| File | Current | Functions Missing Tests |
|------|---------|------------------------|
| file1.py | 45% | func_a, func_b |
| file2.py | 62% | method_x |

### Suggested Tests

(Include pytest code examples for each gap)

### Next Steps

1. [prioritized list of tests to write]
```

## Cost

**$0** - Runs entirely within Claude Code using your Max subscription.

## Alternative: API Mode

To use the API-based execution instead (costs $0.15-$1.00):

```bash
empathy meta-workflow run test-coverage-boost --real --use-defaults
```
