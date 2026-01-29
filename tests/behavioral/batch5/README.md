# Batch 5: Utility & Helper Modules - Behavioral Tests

## Overview
This batch implements behavioral tests for 20 utility and helper modules following the Given/When/Then pattern.

## Test Files Created

### 1. test_exceptions_behavioral.py
**Module:** `empathy_os/exceptions.py`
**Test Count:** 30+ tests
**Coverage:**
- EmpathyFrameworkError (base exception)
- ValidationError
- PatternNotFoundError (with pattern_id storage)
- TrustThresholdError (with threshold comparison)
- ConfidenceThresholdError
- EmpathyLevelError
- LeveragePointError
- FeedbackLoopError
- CollaborationStateError

**Key Tests:**
- Exception initialization with custom messages
- Default message generation
- Attribute storage (pattern_id, trust levels, etc.)
- Exception inheritance verification

### 2. test_helpers_cli_behavioral.py
**Module:** `empathy_os/cli/utils/helpers.py`
**Test Count:** 25+ tests
**Coverage:**
- `_file_exists()` - File existence checker
- `_show_achievements()` - Achievement display

**Key Tests:**
- File existence detection for files and directories
- Achievement unlocking logic (10+ achievements)
- Achievement display formatting
- Multiple achievement combinations

**Achievements Tested:**
- First Steps (1 command)
- Getting Started (10 commands)
- Power User (50 commands)
- Expert (100 commands)
- Pattern Learner
- Claude Whisperer
- Early Bird (5 morning commands)
- Quality Shipper (10 ship commands)
- Code Doctor
- Pattern Master (10+ patterns)
- Week Warrior (7+ days)
- Monthly Maven (30+ days)

### 3. test_data_cli_behavioral.py
**Module:** `empathy_os/cli/utils/data.py`
**Test Count:** 20+ tests
**Coverage:**
- CHEATSHEET dictionary structure
- EXPLAIN_CONTENT dictionary structure

**Key Tests:**
- Cheatsheet sections (Getting Started, Daily Workflow, Code Quality, etc.)
- Command tuple structure validation
- Explanation content completeness
- Section-specific content verification

### 4. test_platform_utils_behavioral.py
**Module:** `empathy_os/platform_utils.py`
**Test Count:** 40+ tests
**Coverage:**
- Platform detection (is_windows, is_macos, is_linux)
- Default directory getters (log, data, config, cache)
- File operations (read_text_file, write_text_file, open_text_file)
- Path utilities (normalize_path, ensure_dir, get_temp_dir)
- Asyncio utilities (setup_asyncio_policy, safe_run_async)
- Platform information (PLATFORM_INFO, get_platform_info)

**Key Tests:**
- Platform detection (exactly one platform detected)
- Directory creation and path normalization
- UTF-8 encoding handling
- Asyncio coroutine execution
- Platform info structure validation

### 5. test_xml_validator_behavioral.py
**Module:** `empathy_os/validation/xml_validator.py`
**Test Count:** 25+ tests
**Coverage:**
- ValidationResult dataclass
- XMLValidator class
- validate_xml_response() convenience function

**Key Tests:**
- Well-formed XML validation
- Malformed XML with fallback parsing
- Strict mode validation
- Data extraction from nested XML
- Attribute extraction
- Empty/invalid XML handling

### 6. test_prompts_parser_behavioral.py
**Module:** `empathy_os/prompts/parser.py`
**Test Count:** 40+ tests
**Coverage:**
- Finding dataclass
- ParsedResponse dataclass

**Key Tests:**
- Finding initialization with severity, title, location
- Finding serialization (to_dict, from_dict)
- ParsedResponse with findings, checklist, errors
- Response serialization
- Fallback response creation

### 7. test_util_modules_batch_behavioral.py
**Modules:** 14 utility modules
**Test Count:** 60+ tests
**Modules Covered:**
1. models/validation.py - ConfigValidator, ValidationError, ValidationResult
2. memory/security/pii_scrubber.py - PIIScrubber
3. memory/security/secrets_detector.py - SecretsDetector
4. resilience/timeout.py - timeout decorator
5. resilience/retry.py - retry decorator
6. resilience/fallback.py - with_fallback decorator
7. workflow_patterns/core.py - WorkflowPattern
8. workflow_patterns/output.py - OutputFormatter
9. cache/base.py - BaseCache
10. memory/config.py - MemoryConfig
11. prompts/context.py - PromptContext
12. prompts/templates.py - PromptTemplate
13. models/executor.py - ModelExecutor
14. memory/security/audit_logger.py - AuditLogger

**Key Tests:**
- Config validation with error detection
- PII scrubbing and secrets detection
- Decorator application and parameter acceptance
- Base class existence and method availability
- Template rendering
- Integration tests

## Test Pattern

All tests follow the **Given/When/Then** pattern:

```python
def test_example_behavior(self):
    """Given: Initial state
    When: Action is performed
    Then: Expected outcome."""
    # Given
    setup_code()

    # When
    result = action()

    # Then
    assert result == expected
```

## Running Tests

```bash
# Run all batch 5 tests
pytest tests/behavioral/batch5/ -v

# Run specific test file
pytest tests/behavioral/batch5/test_exceptions_behavioral.py -v

# Run with coverage
pytest tests/behavioral/batch5/ --cov=empathy_os --cov-report=term-missing -v
```

## Test Categories

### Pure Function Tests
- exceptions.py (dataclasses and exception raising)
- helpers.py (_file_exists)
- platform_utils.py (platform detection, path operations)
- prompts/parser.py (dataclass serialization)

### Validation Tests
- xml_validator.py (XML parsing and validation)
- models/validation.py (config validation)
- pii_scrubber.py (PII detection)
- secrets_detector.py (secret detection)

### Output/Formatting Tests
- data.py (cheatsheet and help text)
- helpers.py (achievement display)
- workflow_patterns/output.py (output formatting)

### Decorator Tests
- resilience/timeout.py
- resilience/retry.py
- resilience/fallback.py

### Base Class Tests
- cache/base.py
- workflow_patterns/core.py
- models/executor.py

## Coverage Goals

- **Target:** 100% pass rate for all tests
- **Focus:** Simple, deterministic utility functions
- **Edge Cases:** Empty inputs, missing fields, type mismatches, boundary values
- **Error Conditions:** Invalid inputs, parsing failures, validation errors

## Key Features

1. **No Complex Mocking:** Most tests use real objects with minimal mocking
2. **Comprehensive Edge Cases:** Tests cover empty inputs, None values, missing attributes
3. **Clear Documentation:** Each test has docstring explaining Given/When/Then
4. **Defensive Testing:** Tests verify both success and failure paths
5. **Type Safety:** Tests verify correct types are returned
6. **Graceful Degradation:** Tests handle missing optional dependencies (try/except ImportError)

## Dependencies

Tests require:
- pytest
- unittest.mock (standard library)
- All modules being tested (with graceful fallback for optional modules)

## Notes

- Tests use `capsys` fixture for testing console output (achievements)
- Tests use `tmp_path` fixture for file operations
- Tests gracefully handle missing optional dependencies (wrapped in try/except ImportError)
- Integration tests verify modules work together

## Statistics

- **Total Test Files:** 7
- **Total Modules Tested:** 20
- **Estimated Total Tests:** 240+
- **Lines of Test Code:** ~2500+
- **Test Coverage:** Designed for 80%+ coverage of utility functions
