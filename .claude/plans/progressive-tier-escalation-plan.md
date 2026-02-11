# Progressive Tier Escalation System - Implementation Plan

**Version:** 1.0
**Created:** 2026-01-17
**Target Release:** v4.1.0
**Owner:** Engineering Team
**Status:** Planning Phase

---

## Executive Summary

Implement a cost-efficient, quality-driven progressive tier escalation system that automatically adapts model selection based on task complexity and failure analysis. Starting with cheap models for volume work, the system intelligently escalates to capable/premium tiers when quality thresholds aren't met, using meta-orchestration to create specialized agent teams optimized for each tier.

**Key Innovation**: LLM-guided retry logic with failure analysis context passing between tiers, ensuring each escalation learns from previous attempts.

---

## Design Decisions (Approved)

### 1. Integration Architecture: Full Hybrid
- Config-based defaults for zero-configuration usage
- CLI flags for per-run overrides
- Python decorator API for programmatic control
- **All three interfaces ship in v4.1.0**

### 2. Failure Detection: Multi-Signal Approach
Detect failures using 4 signals:
1. **Syntax errors** in generated code
2. **Execution failures** when running tests
3. **Quality metrics** (coverage, assertion depth)
4. **LLM confidence** signals (uncertainty in responses)

### 3. Escalation Strategy
```
Cheap Tier (≥2 attempts)
  ↓ (if <70 CQS or >30% failure)
Capable Tier (2-6 attempts, improvement-guided)
  ↓ (if stagnation: <5% improvement × 2 consecutive runs)
Premium Tier (single attempt)
  ↓ (if failed)
Human Escalation (interactive CLI report)
```

### 4. Quality Metrics: Composite Quality Score (CQS)

**Formula:**
```python
CQS = (
    0.40 × test_pass_rate +
    0.25 × code_coverage +
    0.20 × assertion_quality +
    0.15 × llm_confidence
) × syntax_error_penalty
```

**Thresholds:**
- CQS < 70: Poor → Escalate immediately
- CQS 70-79: Below acceptable → Retry or escalate
- CQS 80-94: Acceptable → Success
- CQS 95-100: Top tier → Excellent

**Per-Tier Escalation Triggers:**

| Transition | Failure Rate | Min CQS | Max Syntax Errors |
|------------|--------------|---------|-------------------|
| Cheap → Capable | >30% | <70 | >3 |
| Capable → Premium | >20% | <80 | >1 |

### 5. Meta-Orchestration Design

**Agent Team Composition:**
- **Cheap Tier**: Single TestGenerator agent, XML-enhanced prompt
- **Capable Tier**: Meta-agent analyzes failures → creates TestGenerator + FailureAnalyzer team
- **Premium Tier**: 3-agent team (TestGenerator + FailureAnalyzer + QualityReviewer)

**Context Passing (Option B - Failure Analysis):**
```xml
<capable_tier_prompt>
  <context_from_cheap_tier>
    <failure_summary>
      <pattern type="async_errors" count="15">Async/await syntax issues</pattern>
      <pattern type="mocking_errors" count="10">Incorrect mock setup</pattern>
      <pattern type="edge_cases" count="5">Missing edge case coverage</pattern>
    </failure_summary>

    <failed_attempts>
      <!-- Show 3 worst failed tests as examples -->
      <test_example quality_score="45">
        <code>{failed_test_code}</code>
        <errors>{specific_errors}</errors>
      </test_example>
    </failed_attempts>
  </context_from_cheap_tier>

  <task>
    Generate {N} tests that avoid the specific failure patterns above.
    Focus areas:
    1. Proper async/await patterns
    2. Correct mock setup (pytest-mock)
    3. Comprehensive edge case coverage

    Target functions: {failed_functions}
  </task>
</capable_tier_prompt>
```

### 6. Cost Management (Option 3)

**Three-Layer Cost Control:**

1. **Upfront Estimate** (before execution):
```bash
$ empathy workflow run test-gen --progressive

Estimated cost: $1.20 (exceeds $1.00 threshold)
├─ Cheap tier: $0.30 (100 tests, certain)
├─ Capable escalation: $0.50 (30 tests, 50% probability)
└─ Premium escalation: $0.40 (10 tests, 20% probability)

Proceed? [y/N]:
```

2. **Progressive Approval** (before each escalation):
```bash
✅ Cheap tier: 70/100 passed, CQS=75 ($0.28)

⚠️  Escalate 30 tests to Capable tier?
Additional cost: ~$0.45 (total: $0.73)
Proceed? [Y/n]:
```

3. **Auto-Approve Budget**:
```bash
# Auto-approve escalations under $5.00
$ empathy workflow run test-gen --progressive --auto-approve-under 5.00

# Only prompts if projected total exceeds $5.00
```

**Budget Controls:**
- Global budget cap (warn or abort if exceeded)
- Per-workflow budget limits
- Cost tracking in telemetry

### 7. Retry Logic: LLM-Guided with Stagnation Detection

**Cheap Tier:**
```python
for attempt in range(1, 3):  # Minimum 2 attempts
    result = cheap_agent.generate()
    cqs = calculate_quality_score(result)

    if cqs >= 80:  # Acceptable quality
        return result

    if cqs < 70 or result.syntax_errors > 3:
        break  # Escalate immediately

# Failed 2 attempts → escalate to Capable
```

**Capable Tier (Improvement-Guided):**
```python
previous_cqs = 0
stagnation_count = 0

for attempt in range(1, 7):  # Min 2, max 6 attempts
    result = capable_agent.generate(failure_context)
    current_cqs = calculate_quality_score(result)

    if current_cqs >= 95:  # Top tier quality
        return result

    improvement = current_cqs - previous_cqs

    if improvement < 5.0:  # <5% improvement
        stagnation_count += 1
    else:
        stagnation_count = 0  # Reset on meaningful improvement

    if stagnation_count >= 2:  # 2 consecutive stagnations
        break  # Escalate to Premium

    if current_cqs < 80 and attempt >= 2:
        break  # Below acceptable after 2 tries

    previous_cqs = current_cqs

# Stagnated or low quality → escalate to Premium
```

**Premium Tier:**
```python
result = premium_agent.generate(comprehensive_context)

if result.failed():
    escalate_to_human(detailed_report)
```

### 8. Partial Escalation Granularity

**Test Generation Workflow:**
- Granularity: Per-test
- Example: Generate 100 tests, escalate 30 failed tests to Capable

**Refactor Workflow:**
- Granularity: Per-file
- Example: Refactor 20 files, escalate 5 problematic files to Capable

**Debug Workflow:**
- Granularity: Per-error-type
- Example: Debug 10 errors, escalate "async race condition" errors to Capable

### 9. Human Escalation (Interactive CLI)

When Premium tier fails:

```bash
❌ PREMIUM TIER FAILED - HUMAN REVIEW REQUIRED

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📊 ESCALATION REPORT
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Task: Generate tests for src/complex_module.py
Total items: 10 tests

TIER PROGRESSION:
✅ Cheap:   60% success (6/10), CQS=65, Cost=$0.15
✅ Capable: 80% success (8/10), CQS=78, Cost=$0.32
❌ Premium: 90% success (9/10), CQS=85, Cost=$0.48
   └─ Failed: test_edge_case_async_timeout

REMAINING FAILURE:
Function: handle_async_timeout(connection, timeout_ms)
Issue: Cannot generate reliable test for race condition
Premium Agent Confidence: 45%

ATTEMPTED SOLUTIONS:
1. Cheap: Basic async test (syntax error)
2. Capable: Mock-based test (flaky, 50% pass rate)
3. Premium: Advanced async with pytest-timeout (still flaky)

PREMIUM AGENT ANALYSIS:
"This function has a race condition that requires
manual review. The timeout behavior is non-deterministic
without proper connection mocking infrastructure."

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

OPTIONS:
1. [S]kip this test (accept 90% coverage)
2. [M]anually write test (open editor)
3. [I]nvestigate function (debug mode)
4. [R]eport issue (create GitHub issue)
5. [A]bort workflow

Choice [S/m/i/r/a]:
```

### 10. Observability: Progression Reports

**Generated after each workflow:**

```bash
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🎯 PROGRESSIVE ESCALATION REPORT
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Workflow: test-gen
Target: src/app.py (100 functions)
Duration: 3m 42s
Total Cost: $0.95 (vs $3.20 if all Premium)

TIER BREAKDOWN:

📊 Cheap Tier (gpt-4o-mini)
   • Items: 100 tests
   • Attempts: 2 per test
   • Success: 70 tests (70%)
   • Quality: CQS=75 (acceptable)
   • Cost: $0.30
   • Duration: 1m 15s

📊 Capable Tier (claude-3-5-sonnet)
   • Items: 30 escalated tests
   • Attempts: 3.2 avg (improvement-guided)
   • Success: 25 tests (83%)
   • Quality: CQS=88 (good)
   • Cost: $0.45
   • Duration: 1m 50s
   • Improvements: +13% CQS from Cheap attempts

📊 Premium Tier (claude-opus-4)
   • Items: 5 escalated tests
   • Attempts: 1 per test
   • Success: 5 tests (100%)
   • Quality: CQS=96 (excellent)
   • Cost: $0.20
   • Duration: 37s

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

FINAL RESULTS:
✅ 100/100 tests generated
✅ Overall CQS: 92 (excellent)
✅ Coverage: 95%
✅ All tests passing

COST ANALYSIS:
💰 Total spent: $0.95
💰 Saved: $2.25 (70% cost reduction vs all-Premium)
💰 Cost per test: $0.0095

EFFICIENCY METRICS:
⚡ Cheap tier efficiency: 70% (good)
⚡ Capable tier efficiency: 83% (excellent)
⚡ Escalation rate: 30% → 5% (optimal)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Detailed results saved to:
.empathy/progressive_runs/test-gen-20260117-143022/

View full report:
empathy report show test-gen-20260117-143022
```

**Result Storage (Configurable):**

```yaml
# empathy.config.yml
progressive_escalation:
  save_tier_results: true  # Save all tier attempts
  storage:
    in_memory: true        # Always during execution
    json_files: true       # Save to .empathy/progressive_runs/
    database: false        # Optional long-term analytics
  retention:
    days: 30               # Auto-delete after 30 days
```

---

## Architecture Components

### Core Classes

```python
# src/attune/workflows/progressive/__init__.py

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Callable, Iterator
from enum import Enum

class Tier(Enum):
    """Model tier levels."""
    CHEAP = "cheap"
    CAPABLE = "capable"
    PREMIUM = "premium"

@dataclass
class FailureAnalysis:
    """Multi-signal failure detection."""
    syntax_errors: list[SyntaxError] = field(default_factory=list)
    test_failures: list[dict] = field(default_factory=list)
    test_pass_rate: float = 0.0
    coverage_percent: float = 0.0
    assertion_depth: float = 0.0
    confidence_score: float = 0.0
    llm_uncertainty_signals: list[str] = field(default_factory=list)

    def calculate_quality_score(self) -> float:
        """Calculate composite quality score (0-100)."""
        pass_rate_score = self.test_pass_rate * 100

        cqs = (
            0.40 * pass_rate_score +
            0.25 * self.coverage_percent +
            0.20 * min(self.assertion_depth * 10, 100) +
            0.15 * self.confidence_score * 100
        )

        # Syntax error penalty
        if len(self.syntax_errors) > 0:
            cqs *= 0.5

        return min(cqs, 100.0)

    @property
    def should_escalate(self) -> bool:
        """Multi-criteria escalation decision."""
        cqs = self.calculate_quality_score()
        return (
            cqs < 70 or
            len(self.syntax_errors) > 3 or
            self.test_pass_rate < 0.7 or
            self.coverage_percent < 60
        )

@dataclass
class TierResult:
    """Results from a single tier attempt."""
    tier: Tier
    model: str
    attempt: int
    timestamp: datetime

    # Generated artifacts
    generated_items: list[dict]  # Tests, refactored code, etc.

    # Analysis
    failure_analysis: FailureAnalysis
    cost: float
    duration: float

    # Decision
    escalated: bool = False
    escalation_reason: str = ""

    @property
    def quality_score(self) -> float:
        return self.failure_analysis.calculate_quality_score()

@dataclass
class ProgressiveWorkflowResult:
    """Complete progression history."""
    workflow_name: str
    task_id: str
    tier_results: list[TierResult]

    final_result: TierResult
    total_cost: float
    total_duration: float
    success: bool

    def generate_report(self) -> str:
        """Generate progression report."""
        # Implementation in next section
        pass

@dataclass
class EscalationConfig:
    """Configuration for progressive escalation."""
    enabled: bool = False
    tiers: list[Tier] = field(default_factory=lambda: [Tier.CHEAP, Tier.CAPABLE, Tier.PREMIUM])

    # Retry configuration
    cheap_min_attempts: int = 2
    capable_min_attempts: int = 2
    capable_max_attempts: int = 6

    # Thresholds
    cheap_to_capable_failure_rate: float = 0.30
    cheap_to_capable_min_cqs: float = 70
    cheap_to_capable_max_syntax_errors: int = 3

    capable_to_premium_failure_rate: float = 0.20
    capable_to_premium_min_cqs: float = 80
    capable_to_premium_max_syntax_errors: int = 1

    # Stagnation detection
    improvement_threshold: float = 5.0  # 5% CQS improvement
    consecutive_stagnation_limit: int = 2

    # Cost management
    max_cost: float = 5.00
    auto_approve_under: float | None = None
    warn_on_budget_exceeded: bool = True
    abort_on_budget_exceeded: bool = False

    # Storage
    save_tier_results: bool = True
    storage_path: str = ".empathy/progressive_runs"

class ProgressiveWorkflow:
    """Base class for workflows with progressive escalation."""

    def __init__(self, config: EscalationConfig):
        self.config = config
        self.tier_results: list[TierResult] = []
        self.meta_orchestrator = MetaOrchestrator()

    def execute(self, input_data: dict) -> ProgressiveWorkflowResult:
        """Execute workflow with progressive tier escalation."""
        # Main execution loop
        pass

    def _execute_tier(
        self,
        tier: Tier,
        items: list[Any],
        context: dict | None = None
    ) -> TierResult:
        """Execute items at specific tier."""
        pass

    def _should_escalate(
        self,
        tier: Tier,
        result: TierResult,
        attempt: int
    ) -> tuple[bool, str]:
        """Determine if escalation is needed."""
        pass

    def _estimate_cost(
        self,
        tier: Tier,
        item_count: int
    ) -> float:
        """Estimate cost for tier."""
        pass

    def _request_approval(
        self,
        message: str,
        estimated_cost: float
    ) -> bool:
        """Request user approval for escalation."""
        pass

class MetaOrchestrator:
    """Meta-agent that orchestrates tier progression and agent team creation."""

    def analyze_failure(
        self,
        tier: Tier,
        result: TierResult
    ) -> dict:
        """Analyze failures and recommend strategy."""
        # Returns: {"action": "escalate"|"retry", "reason": "...", "attempts": N}
        pass

    def create_agent_team(
        self,
        tier: Tier,
        failure_context: dict | None = None
    ) -> list[Any]:
        """Create specialized agent team for tier."""
        if tier == Tier.CHEAP:
            return [SingleGeneratorAgent()]
        elif tier == Tier.CAPABLE:
            return [
                GeneratorAgent(),
                FailureAnalyzerAgent(failure_context)
            ]
        else:  # Premium
            return [
                GeneratorAgent(),
                FailureAnalyzerAgent(failure_context),
                QualityReviewerAgent()
            ]

    def build_tier_prompt(
        self,
        tier: Tier,
        base_prompt: str,
        failure_context: dict | None = None
    ) -> str:
        """Build XML-enhanced prompt with failure context."""
        # Implementation in next section
        pass
```

### Integration Points

**1. Configuration (empathy.config.yml):**

```yaml
# Default progressive escalation settings
progressive_escalation:
  default_enabled: false  # Opt-in by default

  # Retry configuration
  retries:
    cheap_min_attempts: 2
    capable_min_attempts: 2
    capable_max_attempts: 6

  # Quality thresholds
  thresholds:
    cheap_to_capable:
      failure_rate: 0.30
      min_quality_score: 70
      max_syntax_errors: 3

    capable_to_premium:
      failure_rate: 0.20
      min_quality_score: 80
      max_syntax_errors: 1

    stagnation:
      improvement_threshold: 5.0
      consecutive_runs: 2

  # Cost management
  cost:
    default_max: 5.00
    auto_approve_under: null  # Null = always prompt
    warn_on_exceeded: true
    abort_on_exceeded: false

  # Storage
  storage:
    save_tier_results: true
    path: ".empathy/progressive_runs"
    retention_days: 30

# Per-workflow overrides
workflows:
  test-gen:
    progressive_escalation:
      enabled: true  # Auto-enable for test-gen
      cost:
        default_max: 10.00  # Higher budget for test generation

  refactor:
    progressive_escalation:
      enabled: false  # Disabled by default for refactor
```

**2. CLI Integration:**

```bash
# Enable progressive escalation
empathy workflow run test-gen --progressive

# With cost control
empathy workflow run test-gen --progressive --max-cost 10.00

# Auto-approve escalations under budget
empathy workflow run test-gen --progressive --auto-approve-under 5.00

# Disable for single run (override config)
empathy workflow run test-gen --no-progressive

# Show escalation plan without executing
empathy workflow run test-gen --progressive --dry-run --show-escalation-plan
```

**3. Python API (Decorator):**

```python
from attune.workflows.progressive import progressive_escalation
from attune.workflows import BaseWorkflow

@progressive_escalation(
    tiers=["cheap", "capable", "premium"],
    failure_threshold=0.3,
    max_cost=5.00
)
class TestGenWorkflow(BaseWorkflow):
    """Test generation with automatic tier escalation."""

    def execute(self, target_file: str):
        # Workflow implementation
        pass

# Runtime override
workflow = TestGenWorkflow()
result = workflow.execute(
    target_file="app.py",
    progressive=True,  # Enable escalation
    max_cost=10.00     # Override default
)
```

**4. Programmatic Control:**

```python
from attune.workflows.progressive import (
    ProgressiveWorkflow,
    EscalationConfig,
    Tier
)

# Custom configuration
config = EscalationConfig(
    enabled=True,
    tiers=[Tier.CHEAP, Tier.CAPABLE, Tier.PREMIUM],
    cheap_min_attempts=2,
    capable_max_attempts=8,  # Custom max
    max_cost=15.00,
    auto_approve_under=5.00
)

# Create workflow with custom config
workflow = TestGenProgressiveWorkflow(config=config)
result = workflow.execute(target_file="complex_module.py")

# Access progression details
for tier_result in result.tier_results:
    print(f"{tier_result.tier}: CQS={tier_result.quality_score}, Cost=${tier_result.cost}")

# Generate report
report = result.generate_report()
print(report)
```

---

## Implementation Phases

### Phase 1: Core Infrastructure (Week 1)

**Tasks:**
1. Create `src/attune/workflows/progressive/` module structure
2. Implement core classes:
   - `FailureAnalysis` with CQS calculation
   - `TierResult` and `ProgressiveWorkflowResult`
   - `EscalationConfig`
3. Implement `ProgressiveWorkflow` base class
4. Add configuration loading from `empathy.config.yml`
5. Write unit tests for CQS calculation (80%+ coverage)

**Deliverables:**
- [ ] Core data structures implemented
- [ ] Configuration schema defined
- [ ] 50+ unit tests passing
- [ ] Documentation for core classes

**Validation:**
```python
# Test CQS calculation
def test_composite_quality_score():
    analysis = FailureAnalysis(
        test_pass_rate=0.85,
        coverage_percent=78,
        assertion_depth=5.2,
        confidence_score=0.92,
        syntax_errors=[]
    )

    cqs = analysis.calculate_quality_score()

    # Expected: 0.4*85 + 0.25*78 + 0.2*52 + 0.15*92 = 87.7
    assert 87 <= cqs <= 88
```

---

### Phase 2: Meta-Orchestration (Week 2)

**Tasks:**
1. Implement `MetaOrchestrator` class
2. Build XML-enhanced prompt templates
3. Implement failure analysis logic
4. Create dynamic agent team composition
5. Implement context passing between tiers (Option B)
6. Write integration tests

**Key Implementation - Prompt Builder:**

```python
class MetaOrchestrator:
    def build_tier_prompt(
        self,
        tier: Tier,
        base_task: str,
        failure_context: dict | None = None
    ) -> str:
        """Build XML-enhanced prompt with failure context."""

        if tier == Tier.CHEAP:
            # Simple prompt for cheap tier
            return f"""
<task>
  <objective>{base_task}</objective>
  <quality_requirements>
    <pass_rate>70%+</pass_rate>
    <coverage>60%+</coverage>
  </quality_requirements>
</task>
"""

        elif tier == Tier.CAPABLE and failure_context:
            # Enhanced prompt with failure analysis
            failure_patterns = self._analyze_failure_patterns(
                failure_context["failures"]
            )

            return f"""
<task>
  <objective>{base_task}</objective>

  <context_from_previous_tier>
    <tier>cheap</tier>
    <quality_score>{failure_context["cqs"]}</quality_score>

    <failure_patterns>
      {self._format_failure_patterns_xml(failure_patterns)}
    </failure_patterns>

    <failed_attempts>
      {self._format_failed_examples_xml(failure_context["examples"][:3])}
    </failed_attempts>
  </context_from_previous_tier>

  <your_task>
    Generate improved solutions that avoid the specific failure patterns above.

    <focus_areas>
      {self._generate_focus_areas(failure_patterns)}
    </focus_areas>

    <quality_requirements>
      <pass_rate>80%+</pass_rate>
      <coverage>70%+</coverage>
      <quality_score>80+</quality_score>
    </quality_requirements>
  </your_task>
</task>
"""

        else:  # Premium tier
            # Most comprehensive prompt
            return f"""
<task>
  <objective>{base_task}</objective>

  <escalation_context>
    <previous_tiers>
      <tier name="cheap" quality="{failure_context.get('cheap_cqs', 0)}">
        {failure_context.get('cheap_summary', '')}
      </tier>
      <tier name="capable" quality="{failure_context.get('capable_cqs', 0)}">
        {failure_context.get('capable_summary', '')}
      </tier>
    </previous_tiers>

    <persistent_issues>
      {self._format_persistent_issues(failure_context)}
    </persistent_issues>
  </escalation_context>

  <expert_task>
    You are the final tier in a progressive escalation system.
    Previous tiers struggled with these items despite multiple attempts.

    Apply expert-level techniques to solve these difficult cases:

    {self._format_expert_guidance(failure_context)}

    <quality_requirements>
      <pass_rate>95%+</pass_rate>
      <coverage>85%+</coverage>
      <quality_score>95+</quality_score>
    </quality_requirements>
  </expert_task>
</task>
"""
```

**Deliverables:**
- [ ] MetaOrchestrator implemented
- [ ] XML prompt templates created
- [ ] Agent team composition working
- [ ] Context passing tested
- [ ] 30+ integration tests

---

### Phase 3: Test Generation Integration (Week 3)

**Tasks:**
1. Create `ProgressiveTestGenWorkflow` class
2. Implement test-specific failure detection
3. Add syntax checking for generated tests
4. Implement test execution for validation
5. Add coverage calculation
6. Integrate with existing test-gen workflow

**Key Implementation:**

```python
class ProgressiveTestGenWorkflow(ProgressiveWorkflow):
    """Test generation with progressive escalation."""

    def execute(self, target_file: str) -> ProgressiveWorkflowResult:
        """Generate tests with automatic tier escalation."""

        # Parse target file to get functions
        functions = self._parse_functions(target_file)

        # Estimate cost and request approval
        estimated_cost = self._estimate_total_cost(len(functions))
        if not self._request_approval(
            f"Generate {len(functions)} tests",
            estimated_cost
        ):
            raise UserCancelledError()

        # Start with cheap tier
        current_tier = Tier.CHEAP
        remaining_items = functions
        context = None

        while remaining_items and current_tier:
            tier_result = self._execute_tier(
                current_tier,
                remaining_items,
                context
            )

            self.tier_results.append(tier_result)

            # Separate successful and failed items
            successful = [
                item for item in tier_result.generated_items
                if item["quality_score"] >= 80
            ]
            failed = [
                item for item in tier_result.generated_items
                if item["quality_score"] < 80
            ]

            # Update remaining items
            remaining_items = failed

            # Check if escalation needed
            should_escalate, reason = self._should_escalate(
                current_tier,
                tier_result,
                attempt=1  # Simplified
            )

            if should_escalate and remaining_items:
                # Escalate to next tier
                current_tier = self._get_next_tier(current_tier)

                # Build context for next tier
                context = {
                    "previous_tier": tier_result.tier,
                    "cqs": tier_result.quality_score,
                    "failures": failed,
                    "examples": tier_result.generated_items[-3:]
                }
            else:
                break

        # Compile final result
        all_successful = []
        for tier_result in self.tier_results:
            all_successful.extend([
                item for item in tier_result.generated_items
                if item["quality_score"] >= 80
            ])

        final_result = self.tier_results[-1]

        return ProgressiveWorkflowResult(
            workflow_name="test-gen",
            task_id=f"test-gen-{datetime.now().strftime('%Y%m%d-%H%M%S')}",
            tier_results=self.tier_results,
            final_result=final_result,
            total_cost=sum(r.cost for r in self.tier_results),
            total_duration=sum(r.duration for r in self.tier_results),
            success=len(remaining_items) == 0
        )

    def _analyze_generated_test(self, test_code: str) -> FailureAnalysis:
        """Analyze quality of generated test."""

        analysis = FailureAnalysis()

        # 1. Check syntax
        try:
            ast.parse(test_code)
        except SyntaxError as e:
            analysis.syntax_errors.append(e)
            return analysis

        # 2. Run test
        pass_rate = self._execute_test(test_code)
        analysis.test_pass_rate = pass_rate

        # 3. Calculate coverage
        coverage = self._calculate_coverage(test_code)
        analysis.coverage_percent = coverage

        # 4. Count assertions
        assertion_count = self._count_assertions(test_code)
        analysis.assertion_depth = assertion_count

        # 5. Extract LLM confidence (if available)
        analysis.confidence_score = 0.8  # TODO: Parse from LLM response

        return analysis
```

**Deliverables:**
- [ ] ProgressiveTestGenWorkflow working
- [ ] Test execution integration
- [ ] Coverage calculation
- [ ] End-to-end tests on Attune AI codebase
- [ ] Performance benchmarks

---

### Phase 4: Cost Management & Approval (Week 4)

**Tasks:**
1. Implement cost estimation logic
2. Add approval prompts (CLI)
3. Implement auto-approve-under budget
4. Add cost tracking in telemetry
5. Create cost analysis reports

**Key Implementation:**

```python
class ProgressiveWorkflow:
    def _estimate_total_cost(self, item_count: int) -> float:
        """Estimate total cost with probabilistic escalation."""

        # Base cost: all items at cheap tier
        cheap_cost = self._estimate_tier_cost(Tier.CHEAP, item_count)

        # Estimated escalation (based on historical data or conservative estimate)
        # Assume 30% escalate to capable, 10% to premium
        capable_cost = self._estimate_tier_cost(Tier.CAPABLE, int(item_count * 0.3))
        premium_cost = self._estimate_tier_cost(Tier.PREMIUM, int(item_count * 0.1))

        total = cheap_cost + capable_cost + premium_cost

        return total

    def _estimate_tier_cost(self, tier: Tier, item_count: int) -> float:
        """Estimate cost for specific tier."""

        # Cost per item (tokens × rate)
        # These are example rates - adjust based on actual pricing
        COST_PER_ITEM = {
            Tier.CHEAP: 0.003,     # ~$0.003 per test (gpt-4o-mini)
            Tier.CAPABLE: 0.015,   # ~$0.015 per test (claude-3-5-sonnet)
            Tier.PREMIUM: 0.05     # ~$0.05 per test (claude-opus-4)
        }

        return COST_PER_ITEM[tier] * item_count

    def _request_approval(self, message: str, estimated_cost: float) -> bool:
        """Request user approval for execution."""

        # Check auto-approve threshold
        if self.config.auto_approve_under and estimated_cost <= self.config.auto_approve_under:
            return True

        # Check if exceeds threshold (default $1.00)
        threshold = 1.00

        if estimated_cost <= threshold:
            return True  # Under threshold, auto-approve

        # Prompt user
        print(f"\n⚠️  Cost Estimate:")
        print(f"   {message}")
        print(f"   Estimated total: ${estimated_cost:.2f}")
        print(f"   (Exceeds threshold of ${threshold:.2f})")
        print()

        response = input("Proceed? [y/N]: ").strip().lower()
        return response == 'y'

    def _check_budget(self) -> None:
        """Check if budget exceeded."""
        current_cost = sum(r.cost for r in self.tier_results)

        if current_cost > self.config.max_cost:
            if self.config.abort_on_budget_exceeded:
                raise BudgetExceededError(
                    f"Cost ${current_cost:.2f} exceeds budget ${self.config.max_cost:.2f}"
                )
            elif self.config.warn_on_budget_exceeded:
                print(f"\n⚠️  WARNING: Cost ${current_cost:.2f} exceeds budget ${self.config.max_cost:.2f}")
```

**Deliverables:**
- [ ] Cost estimation working
- [ ] Approval prompts implemented
- [ ] Budget checking functional
- [ ] Telemetry integration
- [ ] Cost reports generated

---

### Phase 5: Observability & Reporting (Week 5)

**Tasks:**
1. Implement progression report generation
2. Create result storage system
3. Add CLI command to view reports
4. Implement retention policy (auto-delete old results)
5. Create analytics for cost optimization

**Key Implementation:**

```python
class ProgressiveWorkflowResult:
    def generate_report(self) -> str:
        """Generate human-readable progression report."""

        report = []
        report.append("━" * 60)
        report.append("🎯 PROGRESSIVE ESCALATION REPORT")
        report.append("━" * 60)
        report.append("")
        report.append(f"Workflow: {self.workflow_name}")
        report.append(f"Task ID: {self.task_id}")
        report.append(f"Duration: {self._format_duration(self.total_duration)}")
        report.append(f"Total Cost: ${self.total_cost:.2f}")
        report.append("")

        # Calculate cost savings
        all_premium_cost = self._calculate_all_premium_cost()
        savings = all_premium_cost - self.total_cost
        savings_percent = (savings / all_premium_cost) * 100

        report.append(f"Cost Savings: ${savings:.2f} ({savings_percent:.0f}% vs all-Premium)")
        report.append("")
        report.append("TIER BREAKDOWN:")
        report.append("")

        # Tier-by-tier breakdown
        for tier_result in self.tier_results:
            tier_emoji = {
                Tier.CHEAP: "💰",
                Tier.CAPABLE: "📊",
                Tier.PREMIUM: "💎"
            }[tier_result.tier]

            report.append(f"{tier_emoji} {tier_result.tier.value.upper()} Tier ({tier_result.model})")
            report.append(f"   • Items: {len(tier_result.generated_items)}")
            report.append(f"   • Attempts: {tier_result.attempt}")

            success_count = sum(
                1 for item in tier_result.generated_items
                if item["quality_score"] >= 80
            )
            success_rate = success_count / len(tier_result.generated_items) * 100

            report.append(f"   • Success: {success_count}/{len(tier_result.generated_items)} ({success_rate:.0f}%)")
            report.append(f"   • Quality: CQS={tier_result.quality_score:.1f}")
            report.append(f"   • Cost: ${tier_result.cost:.2f}")
            report.append(f"   • Duration: {self._format_duration(tier_result.duration)}")

            if tier_result.escalated:
                report.append(f"   • Escalated: {tier_result.escalation_reason}")

            report.append("")

        report.append("━" * 60)
        report.append("")
        report.append("FINAL RESULTS:")

        total_items = sum(len(r.generated_items) for r in self.tier_results)
        total_successful = sum(
            sum(1 for item in r.generated_items if item["quality_score"] >= 80)
            for r in self.tier_results
        )

        report.append(f"✅ {total_successful}/{total_items} items completed")
        report.append(f"✅ Overall CQS: {self.final_result.quality_score:.0f}")
        report.append(f"{'✅' if self.success else '❌'} Status: {'Success' if self.success else 'Incomplete'}")
        report.append("")

        report.append("━" * 60)
        report.append("")
        report.append(f"Detailed results saved to:")
        report.append(f".empathy/progressive_runs/{self.task_id}/")
        report.append("")

        return "\n".join(report)

    def save_to_disk(self, storage_path: str) -> None:
        """Save detailed results to disk."""
        from pathlib import Path
        import json

        task_dir = Path(storage_path) / self.task_id
        task_dir.mkdir(parents=True, exist_ok=True)

        # Save summary
        summary = {
            "workflow": self.workflow_name,
            "task_id": self.task_id,
            "timestamp": datetime.now().isoformat(),
            "total_cost": self.total_cost,
            "total_duration": self.total_duration,
            "success": self.success,
            "tier_count": len(self.tier_results)
        }

        (task_dir / "summary.json").write_text(
            json.dumps(summary, indent=2)
        )

        # Save each tier result
        for i, tier_result in enumerate(self.tier_results):
            tier_data = {
                "tier": tier_result.tier.value,
                "model": tier_result.model,
                "attempt": tier_result.attempt,
                "timestamp": tier_result.timestamp.isoformat(),
                "quality_score": tier_result.quality_score,
                "cost": tier_result.cost,
                "duration": tier_result.duration,
                "escalated": tier_result.escalated,
                "escalation_reason": tier_result.escalation_reason,
                "generated_items": tier_result.generated_items,
                "failure_analysis": {
                    "syntax_errors": len(tier_result.failure_analysis.syntax_errors),
                    "test_pass_rate": tier_result.failure_analysis.test_pass_rate,
                    "coverage": tier_result.failure_analysis.coverage_percent
                }
            }

            (task_dir / f"tier_{i}_{tier_result.tier.value}.json").write_text(
                json.dumps(tier_data, indent=2)
            )

        # Save human-readable report
        (task_dir / "report.txt").write_text(self.generate_report())
```

**CLI Commands:**

```bash
# View saved reports
empathy report list

# View specific report
empathy report show test-gen-20260117-143022

# Analyze cost trends
empathy report analyze --last 30-days

# Clean up old reports
empathy report cleanup --older-than 30-days
```

**Deliverables:**
- [ ] Report generation working
- [ ] Result storage implemented
- [ ] CLI report commands
- [ ] Retention policy
- [ ] Analytics dashboard (optional)

---

### Phase 6: Refactor Workflow Integration (Week 6)

**Tasks:**
1. Create `ProgressiveRefactorWorkflow`
2. Implement per-file granularity
3. Add refactor-specific failure detection
4. Integration testing

**Key Differences from Test-Gen:**

```python
class ProgressiveRefactorWorkflow(ProgressiveWorkflow):
    """Refactor workflow with per-file escalation."""

    def execute(self, target_path: str) -> ProgressiveWorkflowResult:
        """Refactor files with progressive escalation."""

        # Get files to refactor
        files = self._get_refactor_targets(target_path)

        # Granularity: per-file (not per-function)
        remaining_items = files

        # Execute with escalation (same pattern as test-gen)
        # ...

    def _analyze_refactored_file(self, code: str) -> FailureAnalysis:
        """Analyze quality of refactored code."""

        analysis = FailureAnalysis()

        # 1. Syntax check
        try:
            ast.parse(code)
        except SyntaxError as e:
            analysis.syntax_errors.append(e)
            return analysis

        # 2. Run tests (ensure refactor didn't break functionality)
        test_results = self._run_tests_for_file(code)
        analysis.test_pass_rate = test_results.pass_rate

        # 3. Code quality metrics
        complexity = self._calculate_complexity(code)
        analysis.assertion_depth = 10 - complexity  # Lower complexity = higher score

        # 4. Coverage (did refactor maintain/improve coverage?)
        analysis.coverage_percent = self._calculate_coverage(code)

        # 5. LLM confidence
        analysis.confidence_score = 0.85

        return analysis
```

**Deliverables:**
- [ ] ProgressiveRefactorWorkflow implemented
- [ ] Per-file escalation working
- [ ] Refactor-specific metrics
- [ ] Integration tests

---

## Testing Strategy

### Unit Tests (Target: 150+ tests)

**Test Coverage:**
- ✅ `FailureAnalysis.calculate_quality_score()` - 20 tests
- ✅ Escalation decision logic - 30 tests
- ✅ Cost estimation - 15 tests
- ✅ Threshold checks - 25 tests
- ✅ Stagnation detection - 20 tests
- ✅ Context passing - 15 tests
- ✅ Prompt generation - 25 tests

**Example Test:**

```python
def test_escalation_on_consecutive_stagnation():
    """Test that consecutive stagnation triggers escalation."""

    config = EscalationConfig(
        improvement_threshold=5.0,
        consecutive_stagnation_limit=2
    )

    workflow = ProgressiveTestGenWorkflow(config)

    # Simulate stagnation: 78 -> 79 -> 80 (all <5% improvement)
    results = [
        create_tier_result(cqs=78, tier=Tier.CAPABLE),
        create_tier_result(cqs=79, tier=Tier.CAPABLE),  # +1% (stagnation)
        create_tier_result(cqs=80, tier=Tier.CAPABLE),  # +1% (stagnation)
    ]

    # After 2 consecutive stagnations, should escalate
    should_escalate, reason = workflow._check_stagnation(results)

    assert should_escalate is True
    assert "consecutive stagnation" in reason.lower()
```

### Integration Tests (Target: 50+ tests)

**Scenarios:**
- ✅ End-to-end test generation with escalation
- ✅ Cost approval workflows
- ✅ Budget exceeded handling
- ✅ Multi-tier progression
- ✅ Human escalation triggered
- ✅ Context passing between tiers
- ✅ Report generation

**Example Test:**

```python
def test_end_to_end_progressive_test_generation(tmp_path):
    """Test full progressive workflow on real code."""

    # Create test file
    test_file = tmp_path / "app.py"
    test_file.write_text("""
def simple_function(x):
    return x * 2

def complex_async_function(conn, timeout):
    # This is hard to test
    await conn.query_with_timeout(timeout)
""")

    # Configure workflow
    config = EscalationConfig(
        enabled=True,
        auto_approve_under=10.00,  # Auto-approve for test
        save_tier_results=True
    )

    workflow = ProgressiveTestGenWorkflow(config)

    # Execute
    result = workflow.execute(target_file=str(test_file))

    # Assertions
    assert result.success is True
    assert len(result.tier_results) >= 1  # At least cheap tier ran
    assert result.total_cost < 10.00  # Within budget

    # Verify escalation happened for complex function
    assert any(
        r.tier == Tier.CAPABLE or r.tier == Tier.PREMIUM
        for r in result.tier_results
    )

    # Verify report generated
    report = result.generate_report()
    assert "PROGRESSIVE ESCALATION REPORT" in report
    assert "Cost Savings" in report
```

### Performance Tests (Target: 10+ benchmarks)

**Benchmarks:**
- Cheap tier throughput (tests/second)
- Capable tier throughput
- Premium tier throughput
- Cost per test (by tier)
- Escalation decision time
- Report generation time

```python
def benchmark_cheap_tier_throughput(benchmark):
    """Benchmark test generation at cheap tier."""

    workflow = ProgressiveTestGenWorkflow(
        config=EscalationConfig(enabled=False)  # No escalation
    )

    def run_cheap_tier():
        return workflow._execute_tier(
            Tier.CHEAP,
            items=create_test_functions(100),
            context=None
        )

    result = benchmark(run_cheap_tier)

    # Assert reasonable performance
    assert result.stats.mean < 5.0  # <5 seconds for 100 tests
```

---

## Success Metrics

### Performance Targets

| Metric | Target | Stretch Goal |
|--------|--------|--------------|
| Cheap tier success rate | 70% | 80% |
| Capable tier success rate | 85% | 90% |
| Premium tier success rate | 95% | 98% |
| Overall cost reduction | 60% | 70% |
| Average escalation rate | 30% | 25% |
| Report generation time | <1s | <500ms |

### Quality Metrics

- ✅ 150+ unit tests (80%+ coverage)
- ✅ 50+ integration tests
- ✅ 10+ performance benchmarks
- ✅ Zero security vulnerabilities
- ✅ All coding standards met
- ✅ Documentation complete

### User Experience

- ✅ CLI provides clear cost estimates
- ✅ Approval prompts are informative
- ✅ Reports are human-readable
- ✅ Default config works for 80% of use cases
- ✅ Advanced users have full control

---

## Risk Mitigation

### Risk 1: Over-Escalation (False Positives)

**Risk:** System escalates too aggressively, wasting money.

**Mitigation:**
- Conservative thresholds (30% failure rate for Cheap→Capable)
- Multi-signal failure detection (not just pass rate)
- Stagnation detection requires 2 consecutive runs
- Telemetry to monitor escalation rates

**Validation:**
- Track escalation rate in production
- Adjust thresholds based on real data
- A/B test different threshold values

### Risk 2: Under-Escalation (False Negatives)

**Risk:** System doesn't escalate when it should, producing low-quality results.

**Mitigation:**
- Multiple failure signals (syntax, pass rate, coverage, confidence)
- Low CQS threshold (<70) triggers immediate escalation
- Premium tier always runs if Capable stagnates
- Human review of final results

**Validation:**
- Manual review of non-escalated results
- Compare quality vs all-Premium baseline
- User feedback on result quality

### Risk 3: Runaway Costs

**Risk:** Escalation loop causes unexpected high costs.

**Mitigation:**
- Max attempts limit (6 at Capable tier)
- Global budget cap with abort option
- Cost estimation before execution
- Approval prompts for >$1 tasks

**Validation:**
- Budget exceeded tests
- Cost tracking in telemetry
- Alert on cost anomalies

### Risk 4: Prompt Engineering Failures

**Risk:** XML-enhanced prompts don't improve quality.

**Mitigation:**
- Start with simple prompts, iterate based on results
- A/B test prompt variations
- Include failure examples in context
- Meta-agent learns from successful patterns

**Validation:**
- Compare CQS improvement with/without context passing
- Manual review of prompt effectiveness
- Iterate prompt templates based on data

---

## Rollout Plan

### Phase 1: Internal Testing (Week 7)

- Deploy to development environment
- Test on Attune AI test suite
- Gather telemetry on escalation rates
- Iterate based on findings

### Phase 2: Alpha Release (Week 8)

- Enable for select users (opt-in)
- Monitor cost and quality metrics
- Collect user feedback
- Fix bugs and refine thresholds

### Phase 3: Beta Release (Week 9)

- Enable by default for test-gen workflow
- Add to documentation
- Create tutorial/blog post
- Wider user testing

### Phase 4: General Availability (Week 10)

- Release v4.1.0 with progressive escalation
- Announce feature
- Monitor adoption
- Plan v4.2 enhancements (other workflow types)

---

## Future Enhancements (v4.2+)

**Additional Workflow Types:**
- Progressive debugging workflow
- Progressive documentation generation
- Progressive code review

**Advanced Features:**
- Learning from history (ML-based escalation prediction)
- Custom tier definitions (beyond cheap/capable/premium)
- Multi-model ensembles at each tier
- Cost optimization recommendations

**Observability:**
- Real-time dashboards
- Cost forecasting
- Quality trend analysis
- Anomaly detection

---

## Appendix A: Configuration Reference

**Complete empathy.config.yml example:**

```yaml
progressive_escalation:
  # Global defaults
  default_enabled: false

  # Retry configuration
  retries:
    cheap_min_attempts: 2
    cheap_max_attempts: 3
    capable_min_attempts: 2
    capable_max_attempts: 6
    premium_max_attempts: 1

  # Quality thresholds
  thresholds:
    cheap_to_capable:
      failure_rate: 0.30
      min_quality_score: 70
      max_syntax_errors: 3

    capable_to_premium:
      failure_rate: 0.20
      min_quality_score: 80
      max_syntax_errors: 1

    stagnation:
      improvement_threshold: 5.0
      consecutive_runs: 2
      max_attempts: 6

  # Cost management
  cost:
    default_max: 5.00
    auto_approve_under: null
    warn_on_exceeded: true
    abort_on_exceeded: false
    approval_threshold: 1.00

  # Storage
  storage:
    save_tier_results: true
    path: ".empathy/progressive_runs"
    retention_days: 30

  # Model tier mapping
  tiers:
    cheap:
      models: ["gpt-4o-mini", "claude-3-haiku"]
      default: "gpt-4o-mini"
    capable:
      models: ["claude-3-5-sonnet", "gpt-4o"]
      default: "claude-3-5-sonnet"
    premium:
      models: ["claude-opus-4", "o1"]
      default: "claude-opus-4"

# Per-workflow overrides
workflows:
  test-gen:
    progressive_escalation:
      enabled: true
      cost:
        default_max: 10.00
        auto_approve_under: 2.00

  refactor:
    progressive_escalation:
      enabled: false
      cost:
        default_max: 15.00
```

---

## Appendix B: CLI Command Reference

**All progressive escalation commands:**

```bash
# Basic usage
empathy workflow run test-gen --progressive
empathy workflow run refactor --progressive

# Cost control
empathy workflow run test-gen --progressive --max-cost 10.00
empathy workflow run test-gen --progressive --auto-approve-under 5.00

# Disable for specific run
empathy workflow run test-gen --no-progressive

# Show plan without executing
empathy workflow run test-gen --progressive --dry-run
empathy workflow run test-gen --progressive --show-escalation-plan

# View reports
empathy report list
empathy report show <task-id>
empathy report analyze --last 30-days
empathy report cleanup --older-than 30-days

# Configuration
empathy config get progressive_escalation
empathy config set progressive_escalation.default_enabled true
empathy config validate
```

---

## Appendix C: Python API Examples

**Common usage patterns:**

```python
from attune.workflows.progressive import (
    ProgressiveTestGenWorkflow,
    EscalationConfig,
    Tier
)

# Example 1: Simple usage with defaults
workflow = ProgressiveTestGenWorkflow()
result = workflow.execute(target_file="app.py", progressive=True)

# Example 2: Custom configuration
config = EscalationConfig(
    enabled=True,
    max_cost=10.00,
    auto_approve_under=5.00,
    cheap_min_attempts=3,
    capable_max_attempts=8
)
workflow = ProgressiveTestGenWorkflow(config)
result = workflow.execute(target_file="complex_module.py")

# Example 3: Decorator usage
from attune.workflows.progressive import progressive_escalation

@progressive_escalation(
    failure_threshold=0.25,
    max_cost=15.00
)
class CustomWorkflow(BaseWorkflow):
    def execute(self, input_data):
        # Implementation
        pass

# Example 4: Analyzing results
result = workflow.execute(target_file="app.py", progressive=True)

print(f"Total cost: ${result.total_cost:.2f}")
print(f"Success rate: {result.final_result.quality_score:.0f}%")

for tier_result in result.tier_results:
    print(f"{tier_result.tier}: {len(tier_result.generated_items)} items")

# Save detailed report
result.save_to_disk(".empathy/progressive_runs")

# Generate human-readable report
print(result.generate_report())
```

---

**End of Implementation Plan**

**Version:** 1.0
**Last Updated:** 2026-01-17
**Status:** Ready for Review → Implementation
