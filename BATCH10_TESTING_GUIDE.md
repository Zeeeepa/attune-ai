# Batch 10 Behavioral Testing Guide

Complete guide for generating and implementing behavioral tests for batch 10 modules (1,645 uncovered lines).

## Overview

Batch 10 represents modules with the highest number of uncovered lines. This guide helps you systematically create comprehensive behavioral tests targeting 80%+ coverage using the Given/When/Then pattern.

## Quick Start

### 1. View Batch 10 Modules

```bash
python scripts/show_batch10_modules.py
```

This displays all modules in batch 10 with their uncovered line counts.

### 2. Generate Test Templates

```bash
python scripts/generate_batch10_tests.py
```

This creates test file templates in `tests/behavioral/generated/batch10/` with:
- Given/When/Then structure
- Happy path tests
- Edge case tests
- Error handling tests
- Mock/integration tests
- Performance tests

### 3. Complete Tests

For each generated test file:

1. Read the source module to understand functions
2. Replace `# TODO:` comments with actual function calls
3. Run tests: `pytest tests/behavioral/generated/batch10/test_module.py -v`
4. Check coverage: `pytest tests/behavioral/generated/batch10/test_module.py --cov=src/module.py --cov-report=term-missing`
5. Add tests for uncovered lines
6. Repeat until 80%+ coverage

See `tests/behavioral/generated/batch10/QUICK_START.md` for detailed step-by-step instructions.

### 4. Track Progress

```bash
python scripts/check_batch10_progress.py
```

Shows overall progress and which modules have reached 80%+ coverage.

Use `--detailed` flag to see missing line numbers:

```bash
python scripts/check_batch10_progress.py --detailed
```

## File Structure

```
empathy-framework/
├── scripts/
│   ├── generate_batch10_tests.py      # Test generator
│   ├── show_batch10_modules.py        # Module list viewer
│   └── check_batch10_progress.py      # Progress tracker
│
├── tests/behavioral/generated/batch10/
│   ├── README.md                       # Directory overview
│   ├── QUICK_START.md                  # Step-by-step guide
│   ├── EXAMPLE_test_config_behavior.py # Complete example
│   ├── test_module1_behavior.py        # Generated tests (TODO items)
│   ├── test_module2_behavior.py        # Generated tests (TODO items)
│   └── ...
│
└── /tmp/coverage_batches.json          # Input data (module list)
```

## Test Structure

Each generated test file contains:

### 1. Happy Path Tests
```python
def test_basic_functionality_succeeds(self):
    """GIVEN valid input
    WHEN performing operation
    THEN operation succeeds
    """
    # Given: Setup
    # When: Action
    # Then: Verification
```

### 2. Edge Case Tests
```python
def test_with_empty_input_handles_gracefully(self):
    """GIVEN empty input
    WHEN processing
    THEN handles gracefully or raises error
    """
```

### 3. Error Handling Tests
```python
def test_with_invalid_type_raises_type_error(self):
    """GIVEN invalid type
    WHEN validating
    THEN raises TypeError
    """
```

### 4. Mock/Integration Tests
```python
@patch("module.logger")
def test_logs_info_on_success(self, mock_logger):
    """GIVEN successful operation
    WHEN operation completes
    THEN logs info message
    """
```

### 5. Performance Tests
```python
def test_processes_efficiently(self):
    """GIVEN large dataset
    WHEN processing
    THEN completes within reasonable time
    """
```

## Example Workflow

### Step 1: Generate Tests

```bash
python scripts/generate_batch10_tests.py
```

Output:
```
Generating tests for 15 modules...
Output directory: tests/behavioral/generated/batch10
Total uncovered lines: 1,645

  Generating test for src/empathy_os/config.py (120 uncovered lines)...
    ✓ Created tests/behavioral/generated/batch10/test_config_behavior.py
  ...

✓ Generated 15 test files
```

### Step 2: Complete One Module

Pick `test_config_behavior.py` as first module:

```bash
# Open test file
code tests/behavioral/generated/batch10/test_config_behavior.py

# Open source module to understand it
code src/empathy_os/config.py
```

Replace TODO items:

```python
# Before (generated template):
def test_basic_functionality_succeeds(self):
    # Given: Valid input data
    test_input = "valid_data"
    # When: Performing operation
    # TODO: Replace with actual function call
    result = None
    # Then: Operation succeeds
    assert result is not None

# After (completed):
def test_basic_functionality_succeeds(self):
    # Given: Valid user ID
    user_id = "test_user"
    # When: Creating config
    config = EmpathyConfig(user_id=user_id)
    # Then: Config created successfully
    assert config is not None
    assert config.user_id == user_id
```

### Step 3: Run Tests

```bash
pytest tests/behavioral/generated/batch10/test_config_behavior.py -v
```

### Step 4: Check Coverage

```bash
pytest tests/behavioral/generated/batch10/test_config_behavior.py \
  --cov=src/empathy_os/config.py \
  --cov-report=term-missing
```

Output:
```
Name                      Stmts   Miss  Cover   Missing
-------------------------------------------------------
src/empathy_os/config.py    100     25    75%   45-50, 60-65, 90-95
```

### Step 5: Add Tests for Missing Lines

Lines 45-50 are uncovered. Read source to understand what triggers them:

```python
# config.py lines 45-50 (example)
if path.startswith("/etc"):
    raise ValueError("Cannot write to system directory")
```

Add test:
```python
def test_blocks_system_directory_writes(self):
    """GIVEN path to system directory
    WHEN validating path
    THEN raises ValueError
    """
    # Given: System directory path
    system_path = "/etc/config.yaml"

    # When/Then: Raises ValueError
    with pytest.raises(ValueError, match="system directory"):
        _validate_file_path(system_path)
```

### Step 6: Verify 80%+ Coverage

```bash
pytest tests/behavioral/generated/batch10/test_config_behavior.py \
  --cov=src/empathy_os/config.py \
  --cov-report=term
```

Output:
```
Name                      Stmts   Miss  Cover
----------------------------------------------
src/empathy_os/config.py    100     18    82%   ✓ Goal reached!
```

### Step 7: Move to Next Module

Repeat steps 2-6 for each module in batch 10.

## Common Patterns

### Testing File Operations

```python
def test_writes_file(self, tmp_path):
    """Test file write operation."""
    # Given: Output path (use tmp_path fixture)
    output = tmp_path / "test.txt"

    # When: Writing
    write_function(str(output), "content")

    # Then: File created
    assert output.exists()
    assert output.read_text() == "content"
```

### Testing Error Conditions

```python
def test_raises_on_invalid_input(self):
    """Test error handling."""
    # Given: Invalid input
    invalid = None

    # When/Then: Raises error with message
    with pytest.raises(TypeError, match="cannot be None"):
        process(invalid)
```

### Testing with Mocks

```python
@patch("empathy_os.module.external_call")
def test_with_mocked_external(self, mock_external):
    """Test with mocked dependency."""
    # Given: Mock returns value
    mock_external.return_value = "result"

    # When: Calling function that uses external
    result = my_function()

    # Then: Mock called and result correct
    mock_external.assert_called_once()
    assert result == "result"
```

### Parametrized Tests

```python
@pytest.mark.parametrize("input_val,expected", [
    ("a", "A"),
    ("b", "B"),
    ("c", "C"),
])
def test_multiple_cases(self, input_val, expected):
    """Test multiple input scenarios."""
    assert transform(input_val) == expected
```

## Tools & Scripts

### show_batch10_modules.py

Shows all modules in batch 10 with uncovered line counts.

```bash
python scripts/show_batch10_modules.py
```

### generate_batch10_tests.py

Generates test file templates for all batch 10 modules.

```bash
python scripts/generate_batch10_tests.py
```

Features:
- Creates Given/When/Then test structure
- Includes happy path, edge cases, error handling
- Adds mock/integration tests
- Provides fixtures and helpers
- Auto-generates imports

### check_batch10_progress.py

Tracks overall progress toward 80%+ coverage goal.

```bash
python scripts/check_batch10_progress.py          # Summary
python scripts/check_batch10_progress.py --detailed  # With line numbers
```

Shows:
- Modules tested vs total
- Overall coverage percentage
- Modules at 80%+ vs below
- Progress bar
- Next steps

## Tips for Success

### 1. Start Simple
Begin with straightforward modules before complex ones.

### 2. One Function at a Time
Don't try to test entire module at once. Complete tests for one function, check coverage, then move to next.

### 3. Use tmp_path Fixture
Always use `tmp_path` for file operations:
```python
def test_file_op(self, tmp_path):
    output = tmp_path / "test.txt"
    # Use output for testing
```

### 4. Focus on Uncovered Lines
Coverage report shows exact line numbers. Add tests specifically targeting those lines.

### 5. Test Error Paths
Error handling code is often uncovered. Add tests for:
- Invalid inputs
- File errors
- Permission errors
- Type errors

### 6. Use Example as Reference
See `tests/behavioral/generated/batch10/EXAMPLE_test_config_behavior.py` for a complete example.

### 7. Check Coverage Incrementally
After each new test:
```bash
pytest test_file.py --cov=src/module.py --cov-report=term-missing
```

### 8. Parametrize Similar Tests
If testing multiple similar inputs, use `@pytest.mark.parametrize`.

## Coverage Goals

| Metric | Target | Stretch |
|--------|--------|---------|
| Per-module coverage | 80% | 90% |
| Overall batch 10 coverage | 80% | 85% |
| Tests passing | 100% | 100% |

## Progress Tracking

Update this table as you complete modules:

| Module | Status | Coverage | Notes |
|--------|--------|----------|-------|
| config.py | ⏳ In Progress | 0% | Starting module |
| ... | ⏳ Not Started | 0% | |

Legend:
- ✅ Complete (≥80%)
- ⏳ In Progress (<80%)
- ⏸️ Not Started

## Troubleshooting

### "Module not found" Error

```bash
# Install in development mode
pip install -e .

# Or add to PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:$(pwd)/src"
```

### Coverage Shows 0%

Ensure correct module path:
```bash
# Wrong
pytest --cov=config

# Right
pytest --cov=src/empathy_os/config
```

### Tests Pass but Coverage Low

Check "Missing" column in coverage report - those lines need tests.

### Can't Find Uncovered Lines

Generate HTML report for visual view:
```bash
pytest --cov=src/empathy_os/module.py --cov-report=html
open htmlcov/index.html
```

## Next Steps

1. ✅ Read this guide
2. ✅ View batch 10 modules: `python scripts/show_batch10_modules.py`
3. ✅ Generate tests: `python scripts/generate_batch10_tests.py`
4. ⏳ Complete one module (follow QUICK_START.md)
5. ⏳ Check progress: `python scripts/check_batch10_progress.py`
6. ⏳ Repeat for all modules
7. ⏳ Achieve 80%+ coverage on all modules

## Resources

- **Quick Start Guide**: `tests/behavioral/generated/batch10/QUICK_START.md`
- **Example Test**: `tests/behavioral/generated/batch10/EXAMPLE_test_config_behavior.py`
- **Directory README**: `tests/behavioral/generated/batch10/README.md`
- **Coding Standards**: `docs/CODING_STANDARDS.md`
- **Testing Requirements**: `.claude/rules/empathy/coding-standards-index.md#testing-requirements`

## Support

If you encounter issues:

1. Check example test file for patterns
2. Review source module to understand behavior
3. Read module docstrings for usage
4. Look at existing unit tests for similar modules

## Goal

Complete all batch 10 modules with:
- ✅ All TODO items replaced with actual implementations
- ✅ 80%+ coverage per module
- ✅ All tests passing
- ✅ Given/When/Then pattern followed throughout

**Target**: 1,645 uncovered lines → 80%+ coverage

Good luck! 🚀
