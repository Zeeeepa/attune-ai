# /release-prep - Release Preparation Agent Team

Invoke an AI agent team to assess release readiness.

## What This Does

Creates and executes a team of specialized agents:
- **Security Auditor** - Vulnerability scanning
- **Test Coverage Analyst** - Test quality validation
- **Code Quality Reviewer** - Best practices check
- **Documentation Specialist** - Doc completeness verification

## Usage

```
/release-prep
```

## Instructions for Claude

When the user invokes /release-prep, execute this workflow:

1. Run the release preparation meta-workflow with real execution:
   ```bash
   python -m empathy_os.meta_workflows.cli_meta_workflows run release-prep --real --use-defaults
   ```

2. If ANTHROPIC_API_KEY is not set, fall back to mock execution:
   ```bash
   python -m empathy_os.meta_workflows.cli_meta_workflows run release-prep --use-defaults
   ```

3. Present the results to the user with:
   - Overall status (ready/not ready)
   - Agent findings summary
   - Any blockers identified
   - Recommended next steps

## Expected Output

The command will output:
- Agents created and executed
- Total cost of execution
- Results saved location
- Summary of findings from each agent
