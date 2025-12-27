# Debugging Skill

Use this skill when debugging issues in the Empathy Framework.

## Common Issue Categories

### 1. Model/Provider Issues
- **API Key Missing**: Check `ANTHROPIC_API_KEY`, `OPENAI_API_KEY`, or `OLLAMA_BASE_URL`
- **Model Not Found**: Verify model ID in `src/empathy_os/models/registry.py`
- **Rate Limits**: Check provider quotas, implement backoff

### 2. Workflow Failures
- **Import Errors**: Ensure workflow is registered in `workflows/__init__.py`
- **Type Errors**: Run `python -m mypy src/empathy_os/`
- **Missing Dependencies**: Check `pyproject.toml` dependencies

### 3. VSCode Extension Issues
- **Panel Not Loading**: Check webview HTML in `EmpathyDashboardPanel.ts`
- **Commands Not Working**: Verify registration in `extension.ts` and `package.json`
- **Message Passing**: Debug `_setWebviewMessageListener` handlers

### 4. Cost Calculation Issues
- **Zero Cost**: Ensure `result.cost` is accumulated from executor calls
- **Token Estimation**: Check tiktoken encoding in `token_estimator.py`

## Debugging Commands

```bash
# Type checking
python -m mypy src/empathy_os/ --ignore-missing-imports

# Linting
ruff check src/empathy_os/

# Run specific test
python -m pytest tests/test_specific.py -v --tb=long

# Check workflow registration
python -c "from empathy_os.workflows import WORKFLOWS; print(list(WORKFLOWS.keys()))"

# Test executor
python -c "
import asyncio
from empathy_os.models.executor import get_executor
async def test():
    ex = get_executor()
    r = await ex.execute('Say hello', tier='cheap')
    print(f'Response: {r.content[:100]}...')
    print(f'Cost: ${r.cost:.6f}')
asyncio.run(test())
"
```

## Log Locations
- Audit logs: `/var/log/empathy/audit.jsonl`
- Test output: `pytest --tb=long`
- VSCode extension: Developer Tools Console

## Quick Fixes

| Symptom | Likely Cause | Fix |
|---------|--------------|-----|
| `ModuleNotFoundError` | Not installed in dev mode | `pip install -e .` |
| `AttributeError: 'NoneType'` | Missing config/env | Check `.env` file |
| `TypeError: cannot unpack` | API response changed | Check model provider docs |
| `asyncio.TimeoutError` | Slow model response | Increase timeout or use faster tier |
