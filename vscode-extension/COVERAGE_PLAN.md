# Code Coverage Enhancement Plan
## XML-Enhanced Socratic Refinement

```xml
<prompt>
  <role>Test Coverage Architect</role>
  <goal>Increase code coverage from 16.11% to >40% using strategic, high-value unit tests</goal>

  <context>
    <current_coverage>16.11%</current_coverage>
    <target_coverage>>40%</target_coverage>
    <gap>~24 percentage points</gap>
    <current_tests>36 tests (24 unit, 12 integration)</current_tests>
    <problem>Integration tests don't contribute to coverage (subprocess isolation)</problem>
    <framework_type>CLI framework with Python backend and VSCode extension frontend</framework_type>
  </context>

  <instructions>
    <step>Analyze the current test architecture and coverage distribution</step>
    <step>Identify high-value modules that lack unit test coverage</step>
    <step>Prioritize modules by: (1) criticality, (2) complexity, (3) coverage impact</step>
    <step>Design import-based unit tests that execute code directly (not via subprocess)</step>
    <step>Focus on modules with reusable logic and clear boundaries</step>
    <step>Calculate expected coverage gain per module tested</step>
    <step>Create a phased implementation plan with measurable milestones</step>
  </instructions>

  <constraints>
    <rule>Tests must import modules directly (not use subprocess) to contribute to coverage</rule>
    <rule>Prioritize quality over quantity - strategic tests beat exhaustive tests</rule>
    <rule>Target 30-50% coverage range (industry standard for CLI frameworks)</rule>
    <rule>Avoid testing CLI entry points (they require subprocess and don't contribute)</rule>
    <rule>Focus on business logic, not infrastructure code</rule>
    <rule>Maintain 100% test pass rate throughout implementation</rule>
  </constraints>

  <method>socratic</method>
  <output_format>Phased implementation plan with options, module priority matrix, and coverage projections</output_format>
</prompt>
```

---

## Socratic Analysis: Understanding the Problem

### Question 1: Why is coverage currently at 16.11%?

**Analysis**:
- Only **5 unit test files** contribute to coverage:
  - `test_telemetry_module.py`
  - `test_config.py`
  - `test_workflows.py`
  - `test_cli_commands.py`
  - `test_utils.py`
- The **12 integration tests** use `subprocess.run()` to invoke the CLI
- Subprocess isolation = no coverage tracking for the invoked code

**Key Insight**: We need more import-based unit tests, not more integration tests.

---

### Question 2: Which modules have the highest coverage ROI?

**Priority Matrix** (Impact × Criticality × Testability):

| Module | Lines | Complexity | Criticality | Testability | Priority Score |
|--------|-------|------------|-------------|-------------|----------------|
| `workflows/` | ~800 | High | High | Medium | **9.0** |
| `config/` | ~300 | Medium | High | High | **8.5** |
| `telemetry/` | ~400 | Medium | High | High | **8.0** |
| `llm/` | ~500 | High | Medium | Low | **6.5** |
| `patterns/` | ~350 | Medium | Medium | High | **7.5** |
| `cli/` | ~200 | Low | Low | Low | **3.0** (skip - subprocess only) |

**Strategic Focus Areas**:
1. **Workflows** - Core business logic, high line count
2. **Config** - Critical for framework initialization
3. **Telemetry** - Already partially tested, easy gains
4. **Patterns** - Bug prediction logic, pure functions

---

### Question 3: What are our implementation options?

## Option A: Focused High-Impact (Recommended)
**Target**: 40-45% coverage
**Effort**: 2-3 hours
**Approach**: Test 3-4 high-priority modules strategically

**Modules to Test**:
1. **Workflows Module** (~15% coverage gain)
   - Test workflow discovery
   - Test workflow validation
   - Test stage execution logic
   - Test error handling

2. **Config Module** (~8% coverage gain)
   - Test config loading/merging
   - Test validation rules
   - Test environment variable substitution

3. **Telemetry Module** (~5% coverage gain)
   - Expand existing tests
   - Test cost calculations
   - Test provider aggregation

**Expected Coverage**: ~44% (16% + 15% + 8% + 5%)

---

## Option B: Comprehensive Coverage
**Target**: 50-60% coverage
**Effort**: 5-6 hours
**Approach**: Test all high and medium priority modules

**Additional Modules** (beyond Option A):
4. **Patterns Module** (~7% coverage gain)
   - Test bug prediction patterns
   - Test scanner logic
   - Test false positive filtering

5. **LLM Module** (~6% coverage gain)
   - Test prompt building
   - Test response parsing
   - Test retry logic
   - Mock API calls

**Expected Coverage**: ~57% (44% + 7% + 6%)

---

## Option C: Minimum Viable (Quick Win)
**Target**: 30-35% coverage
**Effort**: 1 hour
**Approach**: Expand existing test coverage in already-tested modules

**Modules to Expand**:
1. **Telemetry** (existing tests)
2. **Config** (existing tests)
3. **Workflows** (existing tests)

**Expected Coverage**: ~32% (16% + 16%)

---

## Recommended Plan: Option A (Phased Approach)

### Phase 1: Workflows Module (Week 1)
**Goal**: +15% coverage → 31% total

**Test Files to Create**:
- `tests/unit/test_workflow_discovery.py`
- `tests/unit/test_workflow_validation.py`
- `tests/unit/test_workflow_execution.py`

**Key Tests** (~20 tests):
- ✓ Discover workflows from directory
- ✓ Parse workflow YAML files
- ✓ Validate workflow structure
- ✓ Execute workflow stages
- ✓ Handle missing dependencies
- ✓ Error recovery mechanisms

---

### Phase 2: Config Module (Week 2)
**Goal**: +8% coverage → 39% total

**Test Files to Create**:
- `tests/unit/test_config_loading.py`
- `tests/unit/test_config_validation.py`
- `tests/unit/test_config_merging.py`

**Key Tests** (~15 tests):
- ✓ Load config from YAML
- ✓ Merge user + default configs
- ✓ Environment variable substitution
- ✓ Validate required fields
- ✓ Handle malformed configs
- ✓ Config precedence rules

---

### Phase 3: Telemetry Module (Week 3)
**Goal**: +5% coverage → 44% total

**Test Files to Expand**:
- `tests/unit/test_telemetry_module.py` (existing)

**Additional Tests** (~10 tests):
- ✓ Multi-provider aggregation
- ✓ Cost estimation accuracy
- ✓ Token counting logic
- ✓ Usage pattern detection
- ✓ Cost optimization suggestions

---

## Implementation Strategy

### 1. Test Design Principles
```python
# ✓ GOOD: Import-based unit test (contributes to coverage)
from empathy_os.workflows import WorkflowDiscovery

@pytest.mark.unit
def test_discover_workflows():
    discovery = WorkflowDiscovery("./test-workflows")
    workflows = discovery.discover()
    assert len(workflows) > 0

# ✗ BAD: Subprocess test (doesn't contribute to coverage)
@pytest.mark.integration
def test_workflow_list():
    result = subprocess.run(["empathy", "workflow", "list"])
    assert result.returncode == 0
```

### 2. Mocking Strategy
- **Mock external dependencies**: LLM APIs, file system, network calls
- **Use fixtures**: Shared test data in `tests/fixtures/`
- **Parameterized tests**: Test multiple scenarios efficiently

### 3. Coverage Measurement
```bash
# Run unit tests with coverage
pytest tests/unit/ --cov=src/empathy_os --cov-report=term --cov-report=html

# Target: Coverage increase after each phase
# Phase 1: 31%
# Phase 2: 39%
# Phase 3: 44%
```

---

## Success Criteria

✓ **Coverage Target**: Achieve >40% coverage (target: 44%)
✓ **Test Quality**: Maintain 100% test pass rate
✓ **No Regressions**: All existing tests continue passing
✓ **Documentation**: Each test file includes docstrings explaining purpose
✓ **Maintainability**: Tests use fixtures and parameterization for DRY code
✓ **CI Integration**: Coverage reports generated on every push

---

## Risk Mitigation

| Risk | Impact | Mitigation |
|------|--------|------------|
| Tests break existing code | High | Run full test suite after each file |
| Coverage gains lower than projected | Medium | Start with highest-ROI modules first |
| Tests are brittle/hard to maintain | Medium | Use mocks and fixtures, avoid hardcoded values |
| Time estimate too optimistic | Low | Phased approach allows re-evaluation |

---

## Next Steps

**Option A (Recommended)**: Proceed with 3-phase plan → 44% coverage in ~2-3 hours
**Option B**: Comprehensive approach → 57% coverage in ~5-6 hours
**Option C**: Quick win → 32% coverage in ~1 hour

**Decision Required**: Which option should we execute?

After selection, I will:
1. Create the test files for Phase 1
2. Implement tests with proper mocking and fixtures
3. Run coverage reports and verify gains
4. Proceed to subsequent phases based on results
