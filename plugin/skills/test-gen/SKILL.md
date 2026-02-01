---
name: test-gen
description: "Test generation for code. Triggers: 'generate tests', 'create unit tests', 'write tests for', 'add tests', 'test this function', 'pytest', 'unit test', 'integration test', 'mock', 'test coverage', 'need tests for'."
---

# Test Generation

AI-powered test generation with coverage optimization.

## Quick Start

```bash
# CLI (primary)
attune workflow run test-gen --path ./src/module.py

# Legacy alias
empathy workflow run test-gen --path ./src/module.py

# Natural language:
"generate tests for config.py"
"write unit tests for the auth module"
"add pytest tests with mocking"
```

## Usage

### Via MCP Tool

The `test_generation` tool is available via MCP:

```python
# Invoked automatically when you describe:
"Generate tests for config.py"
"Add unit tests for this module"
"Improve test coverage"
```

### Via Python

```python
from attune.workflows import TestGenerationWorkflow

workflow = TestGenerationWorkflow()
result = await workflow.execute(
    target_path="./src/module.py",
    coverage_target=90
)
print(result.generated_tests)
```

## Features

- **Unit Tests**: Function-level tests with edge cases
- **Integration Tests**: Cross-module interaction tests
- **Mocking**: Automatic mock generation for dependencies
- **Fixtures**: pytest fixtures for common setup
- **Coverage Analysis**: Identifies untested code paths

## Output

Returns:
- Generated test files
- Coverage report
- Suggested test improvements
- Missing edge case identification
