# v4.1.0 - Progressive Tier Escalation System 🚀

Major feature release introducing intelligent cost optimization through automatic model tier progression.

## Highlights

- **70-85% cost savings** vs all-premium approach
- **Multi-tier execution**: cheap → capable → premium with smart escalation
- **Composite Quality Score (CQS)**: Multi-signal failure detection (test pass rate, coverage, assertion depth, LLM confidence)
- **Meta-orchestration**: Dynamic agent team creation (1/2/3 agents per tier)
- **Privacy-preserving telemetry**: SHA256-hashed user IDs, local-only storage
- **Comprehensive analytics**: Historical cost savings analysis
- **CLI tools**: Manage and analyze workflow results

## New Modules (857 lines)

- `core.py`: Data structures, Tier enum, FailureAnalysis, CQS calculation
- `orchestrator.py`: MetaOrchestrator, escalation logic, agent team creation
- `workflow.py`: ProgressiveWorkflow base class, budget controls
- `test_gen.py`: ProgressiveTestGenWorkflow implementation
- `telemetry.py`: ProgressiveTelemetry, privacy-preserving tracking
- `reports.py`: Report generation, analytics, result storage, cleanup
- `cli.py`: CLI commands (list, show, analytics, cleanup)
- `README.md`: Comprehensive documentation (450 lines)

## Test Suite

- ✅ **123 new tests** (100% pass rate)
- ✅ **86.57% coverage** on progressive module
- ✅ **6,802+ total tests passing**
- ✅ No regressions

## Quick Start

```python
from empathy_os.workflows.progressive import (
    ProgressiveTestGenWorkflow,
    EscalationConfig,
    Tier
)

# Configure
config = EscalationConfig(
    enabled=True,
    tiers=[Tier.CHEAP, Tier.CAPABLE, Tier.PREMIUM],
    max_cost=10.00,
    auto_approve_under=1.00
)

# Execute
workflow = ProgressiveTestGenWorkflow(config)
result = workflow.execute(target_file="src/calculator.py")

# Results
print(f"Cost: ${result.total_cost:.2f}")
print(f"Savings: ${result.cost_savings:.2f} ({result.cost_savings_percent:.0f}%)")
```

## Performance

| Metric              | Value     |
|---------------------|-----------|
| Average cost savings| 70-85%    |
| Cheap tier success  | 60-80%    |
| Test coverage       | 86.57%    |
| Production ready    | ✅ Yes    |

## Installation

```bash
pip install --upgrade empathy-framework
```

## Documentation

- [Progressive Workflows README](https://github.com/Smart-AI-Memory/empathy-framework/blob/main/src/empathy_os/workflows/progressive/README.md)
- [CHANGELOG](https://github.com/Smart-AI-Memory/empathy-framework/blob/main/CHANGELOG.md)

## Migration Guide

Progressive workflows are **opt-in**. Existing code continues unchanged. See [CHANGELOG.md](https://github.com/Smart-AI-Memory/empathy-framework/blob/main/CHANGELOG.md#410---2026-01-17) for details.

---

**Full Changelog**: https://github.com/Smart-AI-Memory/empathy-framework/compare/v4.0.5...v4.1.0
