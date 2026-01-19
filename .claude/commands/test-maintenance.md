# /test-maintenance - Test Maintenance Agent Team

Invoke an AI agent team for automated test lifecycle management.

## What This Does

Creates and executes a team of specialized agents:
- **Test Analyst** - Analyzes coverage gaps and stale tests
- **Test Generator** - Creates new tests for priority files
- **Test Validator** - Runs generated tests to verify they work
- **Test Reporter** - Generates comprehensive status report

## Usage

```
/test-maintenance
```

## Instructions for Claude

When the user invokes /test-maintenance, execute this workflow:

1. Run the test maintenance meta-workflow with real execution:
   ```bash
   python -m empathy_os.meta_workflows.cli_meta_workflows run test-maintenance --real --use-defaults
   ```

2. If ANTHROPIC_API_KEY is not set, fall back to mock execution:
   ```bash
   python -m empathy_os.meta_workflows.cli_meta_workflows run test-maintenance --use-defaults
   ```

3. Present the results to the user with:
   - Stale tests detected
   - Coverage gaps identified
   - Tests generated and validated
   - Overall test suite health status

## Expected Output

The command will output:
- Test suite analysis
- Stale test detection results
- Generated tests (if applicable)
- Validation results
- Maintenance recommendations
