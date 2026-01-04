# Empathy Framework Test Suite

## Test Organization

- **Unit Tests** (`tests/unit/`): Import and test modules directly, measured for coverage
- **Integration Tests** (root `test_*.py`): Run CLI commands via subprocess, no coverage

## Running Tests

### All Tests (Unit + Integration)
```bash
pytest
```

### Unit Tests Only (with coverage)
```bash
pytest -m unit --cov=src/empathy_os --cov-report=term-missing --cov-fail-under=10
```

### Integration Tests Only (no coverage)
```bash
pytest -m integration
```

### Specific Test File
```bash
pytest tests/unit/test_config.py
pytest test_dashboard.py
```

### With Verbose Output
```bash
pytest -v
pytest -vv  # Extra verbose
```

## Coverage Requirements

- **Unit tests**: Required to meet 10% coverage minimum
- **Integration tests**: Excluded from coverage (run CLI via subprocess)

## Test Markers

- `@pytest.mark.unit` - Unit test (imports modules, measured for coverage)
- `@pytest.mark.integration` - Integration test (subprocess, no coverage)
- `@pytest.mark.slow` - Slow test (can be skipped with `-m "not slow"`)
- `@pytest.mark.network` - Requires network (skip with `-m "not network"`)
- `@pytest.mark.llm` - Requires LLM API access

## Examples

```bash
# Run only fast unit tests with coverage
pytest -m "unit and not slow" --cov=src/empathy_os

# Run all tests except network-dependent ones
pytest -m "not network"

# Run integration tests with extra output
pytest -m integration -vv
```
