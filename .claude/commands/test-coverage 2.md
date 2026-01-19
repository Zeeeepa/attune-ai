# /test-coverage - Test Coverage Boost Agent Team

Invoke an AI agent team to analyze and improve test coverage.

## What This Does

Creates and executes a team of specialized agents:
- **Gap Analyzer** - Identifies coverage gaps and prioritizes by impact
- **Test Generator** - Creates tests for uncovered code
- **Test Validator** - Verifies generated tests pass and improve coverage

## Usage

```
/test-coverage
```

## Instructions for Claude

When the user invokes /test-coverage, execute this workflow:

1. Run the test coverage boost meta-workflow with real execution:
   ```bash
   python -m empathy_os.meta_workflows.cli_meta_workflows run test-coverage-boost --real --use-defaults
   ```

2. If ANTHROPIC_API_KEY is not set, fall back to mock execution:
   ```bash
   python -m empathy_os.meta_workflows.cli_meta_workflows run test-coverage-boost --use-defaults
   ```

3. Present the results to the user with:
   - Current coverage percentage
   - Coverage gaps identified
   - Tests generated (if any)
   - New coverage percentage after tests
   - Files that need attention

## Expected Output

The command will output:
- Gap analysis results
- Generated test files (if applicable)
- Coverage improvement metrics
- Prioritized list of remaining gaps
