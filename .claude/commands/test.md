Run the Empathy Framework test suite and report results.

1. Run: `pytest tests/ -v --tb=short`

2. If tests fail, summarize:
   - Which tests failed
   - Brief error description
   - Suggested fix if obvious

3. If tests pass, show:
   - Total tests run
   - Time taken
   - Coverage summary if available

Keep output concise.

## Need More Comprehensive Testing?

For advanced test maintenance with an AI agent team, use:

- `/test-coverage` - Boost test coverage with gap analysis and test generation
- `/test-maintenance` - Automated test lifecycle management

Or run directly:

```bash
empathy meta-workflow run test-coverage-boost --real --use-defaults
empathy meta-workflow run test-maintenance --real --use-defaults
```
