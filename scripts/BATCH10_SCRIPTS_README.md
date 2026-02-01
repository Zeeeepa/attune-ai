# Batch 10 Testing Scripts

This directory contains scripts for generating and managing behavioral tests for batch 10 modules.

## Scripts Overview

### Core Scripts

#### 1. `batch10_workflow.py` - Master Workflow (⭐ Start Here)
**Purpose**: Interactive workflow orchestrator for the entire process

**Usage**:
```bash
# Interactive mode (recommended for first time)
python scripts/batch10_workflow.py

# Run all steps automatically
python scripts/batch10_workflow.py --all

# Run specific step
python scripts/batch10_workflow.py --step 1
python scripts/batch10_workflow.py --step 2
python scripts/batch10_workflow.py --step 3
python scripts/batch10_workflow.py --step 4
```

**Features**:
- Interactive menu system
- Guides through complete workflow
- Can run individual steps or all at once
- Provides helpful prompts and next steps

**When to Use**: First time setup or when you want guidance

---

#### 2. `show_batch10_modules.py` - Module List Viewer
**Purpose**: Display all modules in batch 10 with uncovered line counts

**Usage**:
```bash
python scripts/show_batch10_modules.py
```

**Output Example**:
```
====================================================================
BATCH 10 MODULES - Test Generation Targets
====================================================================

Total Modules: 15
Total Uncovered Lines: 1,645
Coverage Goal: 80%+

Modules to Test:
--------------------------------------------------------------------
Module                                             Uncovered Lines
--------------------------------------------------------------------
src/attune/config.py                                       120
src/attune/workflows/base.py                              200
...
--------------------------------------------------------------------
TOTAL                                                        1,645
```

**When to Use**: To see what needs to be tested before generating tests

---

#### 3. `generate_batch10_tests.py` - Test Generator
**Purpose**: Generate behavioral test templates for all batch 10 modules

**Usage**:
```bash
python scripts/generate_batch10_tests.py
```

**Input**: `/tmp/coverage_batches.json`

**Output**: Test files in `tests/behavioral/generated/batch10/`

**What It Generates**:
- One test file per batch 10 module
- ~300-500 lines per test file
- 15+ test methods per file
- Given/When/Then structure
- Happy path, edge cases, error handling
- Mock/integration tests
- Performance tests
- Fixtures and helpers

**When to Use**: After viewing modules, before completing tests

---

#### 4. `validate_batch10_tests.py` - Test Validator
**Purpose**: Validate test files for completeness and quality

**Usage**:
```bash
# Standard validation
python scripts/validate_batch10_tests.py

# Strict validation (more checks)
python scripts/validate_batch10_tests.py --strict
```

**Checks**:
- ❌ TODO items remaining
- ❌ Missing imports
- ⚠️ Missing Given/When/Then structure
- ⚠️ Missing docstrings
- ⚠️ No assertions (stub tests)
- ⚠️ Low test count (<5 tests)

**Output Example**:
```
Validating 15 test files...

✅ test_config_behavior.py
❌ test_base_behavior.py
   ❌ 5 TODO items remaining (must be completed)
   ⚠️  test_basic_functionality_succeeds: No assertions (stub test)

====================================================================
VALIDATION SUMMARY
====================================================================

Total Files: 15
Valid Files: 10
Files with Issues: 5
Completion: 66.7%
```

**When to Use**: After completing TODO items, before running tests

---

#### 5. `check_batch10_progress.py` - Progress Tracker
**Purpose**: Track overall coverage progress toward 80%+ goal

**Usage**:
```bash
# Summary report
python scripts/check_batch10_progress.py

# Detailed report with missing line numbers
python scripts/check_batch10_progress.py --detailed
```

**Output Example**:
```
====================================================================
BATCH 10 TEST COVERAGE PROGRESS
====================================================================

Overall Progress:
  Modules in Batch: 15
  Modules Tested: 12
  Modules Not Started: 3

Coverage Statistics:
  Total Lines: 1,645
  Covered Lines: 1,316
  Overall Coverage: 80.0%

Goal Progress (80%+ per module):
  ✅ At Goal (≥80%): 10
  ⚠️  Below Goal (<80%): 2

Progress: [████████████████████████████████████░░░░░░░░░] 66.7%
```

**When to Use**: After running tests, to track progress toward goal

---

## Complete Workflow Example

### First Time Setup

```bash
# Step 1: Run interactive workflow
python scripts/batch10_workflow.py

# Follow menu prompts:
# 1. View batch 10 modules → See what needs testing
# 2. Generate test templates → Create test files
# (Now edit the generated files to complete TODO items)
# 3. Validate test files → Check your work
# 4. Check coverage progress → See how close to goal
```

### Manual Workflow

```bash
# Step 1: View modules
python scripts/show_batch10_modules.py

# Step 2: Generate tests
python scripts/generate_batch10_tests.py

# Step 3: Complete TODO items
# Edit files in tests/behavioral/generated/batch10/
# Replace "# TODO:" comments with actual code

# Step 4: Validate
python scripts/validate_batch10_tests.py

# Step 5: Run tests
pytest tests/behavioral/generated/batch10/ -v

# Step 6: Check progress
python scripts/check_batch10_progress.py

# Step 7: Iterate
# Add more tests for uncovered lines
# Re-run validation and progress checks
```

### Quick Check Workflow

```bash
# Quick validation
python scripts/validate_batch10_tests.py

# Quick progress check
python scripts/check_batch10_progress.py

# Quick test run
pytest tests/behavioral/generated/batch10/ -v
```

## Input Requirements

All scripts expect `/tmp/coverage_batches.json` with this format:

```json
{
  "batch_10": {
    "modules": [
      {
        "module": "src/attune/config.py",
        "uncovered_lines": 120
      },
      {
        "module": "src/attune/workflows/base.py",
        "uncovered_lines": 200
      }
    ],
    "total_uncovered_lines": 1645
  }
}
```

**If you don't have this file**: Run your coverage analysis tool to generate it first.

## Output Locations

- **Generated Tests**: `tests/behavioral/generated/batch10/test_*_behavior.py`
- **Documentation**: `tests/behavioral/generated/batch10/README.md`
- **Quick Start Guide**: `tests/behavioral/generated/batch10/QUICK_START.md`
- **Example Test**: `tests/behavioral/generated/batch10/EXAMPLE_test_config_behavior.py`

## Script Dependencies

All scripts are standalone Python scripts with minimal dependencies:

- Python 3.8+
- Standard library only (no external packages required)
- `pytest` and `pytest-cov` (for running tests and coverage)

## Permissions

Make scripts executable (optional):

```bash
chmod +x scripts/batch10_workflow.py
chmod +x scripts/show_batch10_modules.py
chmod +x scripts/generate_batch10_tests.py
chmod +x scripts/validate_batch10_tests.py
chmod +x scripts/check_batch10_progress.py
```

Then run with:
```bash
./scripts/batch10_workflow.py
```

## Troubleshooting

### Script not found
**Problem**: `No such file or directory`

**Solution**: Run from project root
```bash
cd /path/to/attune-ai
python scripts/batch10_workflow.py
```

### Input file not found
**Problem**: `/tmp/coverage_batches.json not found`

**Solution**: Generate coverage batches first or check path

### Module import errors
**Problem**: `ModuleNotFoundError: No module named 'attune'`

**Solution**: Install package in development mode
```bash
pip install -e .
```

### Permission denied
**Problem**: `Permission denied` when running script

**Solution**: Make executable or use `python` explicitly
```bash
chmod +x scripts/batch10_workflow.py
# Or
python scripts/batch10_workflow.py
```

## Quick Reference

| Task | Command |
|------|---------|
| Start workflow | `python scripts/batch10_workflow.py` |
| View modules | `python scripts/show_batch10_modules.py` |
| Generate tests | `python scripts/generate_batch10_tests.py` |
| Validate tests | `python scripts/validate_batch10_tests.py` |
| Check progress | `python scripts/check_batch10_progress.py` |
| Run all steps | `python scripts/batch10_workflow.py --all` |

## Related Documentation

- **Main Guide**: `../BATCH10_TESTING_GUIDE.md`
- **Implementation Summary**: `../BATCH10_IMPLEMENTATION_SUMMARY.md`
- **Test Directory README**: `../tests/behavioral/generated/batch10/README.md`
- **Quick Start Guide**: `../tests/behavioral/generated/batch10/QUICK_START.md`

## Support

For issues or questions:
1. Check troubleshooting section above
2. Review documentation in `tests/behavioral/generated/batch10/`
3. See example test in `EXAMPLE_test_config_behavior.py`
4. Review coding standards in `docs/CODING_STANDARDS.md`

---

**Created**: 2026-01-29
**Version**: 1.0
**Maintainer**: Engineering Team
