# Batch 10 Behavioral Testing - Complete Index

Quick reference for all batch 10 testing resources.

## 📋 Quick Start

**New to batch 10 testing?** Start here:

1. **Read**: [BATCH10_TESTING_GUIDE.md](./BATCH10_TESTING_GUIDE.md) (5 min)
2. **Run**: `python scripts/batch10_workflow.py` (Interactive)
3. **Reference**: [tests/behavioral/generated/batch10/QUICK_START.md](./tests/behavioral/generated/batch10/QUICK_START.md)

## 📂 All Resources

### Top-Level Documentation

| File | Purpose | Read Time |
|------|---------|-----------|
| [BATCH10_TESTING_GUIDE.md](./BATCH10_TESTING_GUIDE.md) | Complete guide with examples | 15 min |
| [BATCH10_IMPLEMENTATION_SUMMARY.md](./BATCH10_IMPLEMENTATION_SUMMARY.md) | What was created and how to use it | 10 min |
| **[BATCH10_INDEX.md](./BATCH10_INDEX.md)** | This file - quick reference index | 2 min |

### Scripts (in `scripts/`)

| Script | Purpose | Usage |
|--------|---------|-------|
| [batch10_workflow.py](./scripts/batch10_workflow.py) | **⭐ Master workflow** - Start here | `python scripts/batch10_workflow.py` |
| [show_batch10_modules.py](./scripts/show_batch10_modules.py) | View modules to test | `python scripts/show_batch10_modules.py` |
| [generate_batch10_tests.py](./scripts/generate_batch10_tests.py) | Generate test templates | `python scripts/generate_batch10_tests.py` |
| [validate_batch10_tests.py](./scripts/validate_batch10_tests.py) | Validate test quality | `python scripts/validate_batch10_tests.py` |
| [check_batch10_progress.py](./scripts/check_batch10_progress.py) | Track coverage progress | `python scripts/check_batch10_progress.py` |
| [BATCH10_SCRIPTS_README.md](./scripts/BATCH10_SCRIPTS_README.md) | Scripts documentation | Read for details |

### Test Directory (in `tests/behavioral/generated/batch10/`)

| File | Purpose |
|------|---------|
| [README.md](./tests/behavioral/generated/batch10/README.md) | Test directory overview |
| [QUICK_START.md](./tests/behavioral/generated/batch10/QUICK_START.md) | Step-by-step completion guide |
| [EXAMPLE_test_config_behavior.py](./tests/behavioral/generated/batch10/EXAMPLE_test_config_behavior.py) | **Complete reference example** |
| `test_*_behavior.py` | Generated test files (TODO items) |

## 🚀 Common Tasks

### First Time Setup

```bash
# Interactive workflow (recommended)
python scripts/batch10_workflow.py

# Or run all steps automatically
python scripts/batch10_workflow.py --all
```

### View What Needs Testing

```bash
python scripts/show_batch10_modules.py
```

### Generate Test Templates

```bash
python scripts/generate_batch10_tests.py
```

### Complete Tests

1. Open generated test file: `tests/behavioral/generated/batch10/test_module_behavior.py`
2. Read source module to understand functions
3. Replace `# TODO:` comments with actual code
4. See `EXAMPLE_test_config_behavior.py` for reference

### Validate Your Work

```bash
python scripts/validate_batch10_tests.py
```

### Run Tests

```bash
pytest tests/behavioral/generated/batch10/ -v
```

### Check Coverage Progress

```bash
python scripts/check_batch10_progress.py
```

### Check Coverage for Specific Module

```bash
pytest tests/behavioral/generated/batch10/test_config_behavior.py \
  --cov=src/empathy_os/config.py \
  --cov-report=term-missing
```

## 📊 Progress Tracking

Track your progress with these commands:

```bash
# Overall progress
python scripts/check_batch10_progress.py

# Detailed view with line numbers
python scripts/check_batch10_progress.py --detailed

# Validation status
python scripts/validate_batch10_tests.py

# HTML coverage report
pytest tests/behavioral/generated/batch10/ \
  --cov=src \
  --cov-report=html
open htmlcov/index.html
```

## 📖 Learning Path

### Beginner (Never written behavioral tests)

1. Read: [BATCH10_TESTING_GUIDE.md](./BATCH10_TESTING_GUIDE.md) - Quick Start section
2. Read: [tests/behavioral/generated/batch10/QUICK_START.md](./tests/behavioral/generated/batch10/QUICK_START.md)
3. Study: [EXAMPLE_test_config_behavior.py](./tests/behavioral/generated/batch10/EXAMPLE_test_config_behavior.py)
4. Try: Complete one simple module
5. Run: `python scripts/batch10_workflow.py` for guidance

### Intermediate (Familiar with pytest)

1. Skim: [BATCH10_TESTING_GUIDE.md](./BATCH10_TESTING_GUIDE.md) - Common Patterns section
2. Run: `python scripts/generate_batch10_tests.py`
3. Complete: Replace TODO items in test files
4. Validate: `python scripts/validate_batch10_tests.py`
5. Track: `python scripts/check_batch10_progress.py`

### Advanced (Writing tests efficiently)

1. Generate all: `python scripts/generate_batch10_tests.py`
2. Batch complete: Edit multiple files at once
3. Run incrementally: Test each module as you complete it
4. Optimize: Target uncovered lines directly
5. Validate: Ensure 80%+ coverage on all modules

## 🎯 Goals

| Metric | Target | Stretch |
|--------|--------|---------|
| Per-module coverage | 80% | 90% |
| Overall batch 10 coverage | 80% | 85% |
| Tests passing | 100% | 100% |
| Validation passing | 100% | 100% |

**Total Target**: 1,645 uncovered lines → 80%+ coverage

## 🔧 Troubleshooting

### Can't find modules
**Solution**: Ensure `/tmp/coverage_batches.json` exists

### Import errors
**Solution**: `pip install -e .`

### Coverage shows 0%
**Solution**: Use full path `--cov=src/empathy_os/module`

### Tests pass but low coverage
**Solution**: Check coverage report's "Missing" column, add tests for those lines

### Don't know what to test
**Solution**: Read source module, see `EXAMPLE_test_config_behavior.py`

See full troubleshooting in:
- [BATCH10_TESTING_GUIDE.md](./BATCH10_TESTING_GUIDE.md#troubleshooting)
- [tests/behavioral/generated/batch10/QUICK_START.md](./tests/behavioral/generated/batch10/QUICK_START.md#troubleshooting)

## 📝 Cheat Sheet

### Commands

```bash
# Workflow
python scripts/batch10_workflow.py              # Interactive
python scripts/batch10_workflow.py --all        # Run all steps

# Individual steps
python scripts/show_batch10_modules.py          # View modules
python scripts/generate_batch10_tests.py        # Generate tests
python scripts/validate_batch10_tests.py        # Validate
python scripts/check_batch10_progress.py        # Progress

# Testing
pytest tests/behavioral/generated/batch10/ -v                     # Run all
pytest tests/behavioral/generated/batch10/test_module.py -v       # Run one
pytest tests/behavioral/generated/batch10/ --cov=src --cov-report=term-missing
```

### File Locations

```
empathy-framework/
├── BATCH10_TESTING_GUIDE.md              # Main guide
├── BATCH10_IMPLEMENTATION_SUMMARY.md     # What was created
├── BATCH10_INDEX.md                      # This file
│
├── scripts/
│   ├── batch10_workflow.py               # Master workflow
│   ├── show_batch10_modules.py           # View modules
│   ├── generate_batch10_tests.py         # Generate tests
│   ├── validate_batch10_tests.py         # Validate
│   ├── check_batch10_progress.py         # Progress
│   └── BATCH10_SCRIPTS_README.md         # Scripts docs
│
└── tests/behavioral/generated/batch10/
    ├── README.md                         # Directory overview
    ├── QUICK_START.md                    # Step-by-step guide
    ├── EXAMPLE_test_config_behavior.py   # Reference example
    └── test_*_behavior.py                # Generated tests
```

### Test Pattern Template

```python
def test_scenario_name(self):
    """GIVEN preconditions
    WHEN action occurs
    THEN expected outcome
    """
    # Given: Setup
    test_data = create_test_data()

    # When: Action
    result = perform_action(test_data)

    # Then: Verification
    assert result == expected_value
```

## ✅ Checklist

Track your progress:

- [ ] Read BATCH10_TESTING_GUIDE.md
- [ ] Run batch10_workflow.py to see modules
- [ ] Generate test templates
- [ ] Review EXAMPLE_test_config_behavior.py
- [ ] Complete TODO items in first test file
- [ ] Run tests for first module
- [ ] Check coverage for first module
- [ ] Achieve 80%+ on first module
- [ ] Repeat for all modules
- [ ] Validate all tests pass
- [ ] Check overall progress shows 80%+
- [ ] Celebrate! 🎉

## 🎓 Best Practices

1. **Start Simple**: Begin with straightforward modules
2. **One at a Time**: Complete one module fully before moving to next
3. **Use Example**: Reference `EXAMPLE_test_config_behavior.py` frequently
4. **Check Often**: Validate and check coverage incrementally
5. **Focus on Uncovered**: Target specific line numbers from coverage report
6. **Test Errors**: Don't forget error handling paths
7. **Use Fixtures**: Leverage `tmp_path` for file operations
8. **Parametrize**: Use `@pytest.mark.parametrize` for similar tests

## 📚 Related Documentation

- [Coding Standards](./docs/CODING_STANDARDS.md)
- [Testing Requirements](./.claude/rules/empathy/coding-standards-index.md#testing-requirements)
- [Behavioral Testing Guide](./tests/behavioral/README.md)

## 🆘 Support

If stuck:
1. Check [QUICK_START.md](./tests/behavioral/generated/batch10/QUICK_START.md)
2. Review [EXAMPLE_test_config_behavior.py](./tests/behavioral/generated/batch10/EXAMPLE_test_config_behavior.py)
3. Read source module to understand what to test
4. Run validation to see what's missing
5. Check existing unit tests for similar patterns

## 🎯 Next Steps

**Choose your path:**

### Path A: Guided (Recommended for first time)
```bash
python scripts/batch10_workflow.py
# Follow interactive prompts
```

### Path B: Quick Start (Familiar with process)
```bash
python scripts/generate_batch10_tests.py
# Edit test files
pytest tests/behavioral/generated/batch10/ -v
python scripts/check_batch10_progress.py
```

### Path C: Manual (Full control)
1. View modules: `python scripts/show_batch10_modules.py`
2. Generate tests: `python scripts/generate_batch10_tests.py`
3. Complete TODO items (see QUICK_START.md)
4. Validate: `python scripts/validate_batch10_tests.py`
5. Run tests: `pytest tests/behavioral/generated/batch10/ -v`
6. Check coverage: `python scripts/check_batch10_progress.py`
7. Iterate until 80%+ coverage

---

**Version**: 1.0
**Created**: 2026-01-29
**Maintainer**: Engineering Team

**Quick Start**: `python scripts/batch10_workflow.py`
