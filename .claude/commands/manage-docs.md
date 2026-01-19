# /manage-docs - Documentation Management Agent Team

Invoke an AI agent team to ensure documentation stays in sync with code.

## What This Does

Creates and executes a team of specialized agents:
- **Documentation Analyst** - Identifies missing docstrings and stale docs
- **Documentation Reviewer** - Validates findings and removes false positives
- **Documentation Synthesizer** - Creates prioritized action plan

## Usage

```
/manage-docs
```

## Instructions for Claude

When the user invokes /manage-docs, execute this workflow:

1. Run the documentation management meta-workflow with real execution:
   ```bash
   python -m empathy_os.meta_workflows.cli_meta_workflows run manage-docs --real --use-defaults
   ```

2. If ANTHROPIC_API_KEY is not set, fall back to mock execution:
   ```bash
   python -m empathy_os.meta_workflows.cli_meta_workflows run manage-docs --use-defaults
   ```

3. Present the results to the user with:
   - Missing docstrings count
   - Outdated documentation identified
   - README freshness status
   - Prioritized improvement suggestions

## Expected Output

The command will output:
- Documentation gap analysis
- Stale documentation detection
- API documentation completeness
- Prioritized action items for documentation improvements
