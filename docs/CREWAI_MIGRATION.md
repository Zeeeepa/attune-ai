# CrewAI Migration Guide

**Version:** 4.4.0
**Last Updated:** 2026-01-19

This guide helps you migrate from the deprecated Crew-based workflows to the new meta-workflow system.

## Overview

As of v4.4.0, the Crew-based workflows are deprecated. They will continue to work but emit deprecation warnings. The meta-workflow system provides equivalent functionality with several advantages:

### Why Migrate?

| Feature | Crew Workflows | Meta-Workflows |
|---------|----------------|----------------|
| LLM Provider | Anthropic SDK (same) | Anthropic SDK (same) |
| Dependency | CrewAI + LangChain (unused) | None (direct Anthropic) |
| Configuration | Hardcoded | Form-based (Socratic) |
| Agent Composition | Static | Dynamic (rule-based) |
| Tier Escalation | Manual | Automatic (70-85% cost savings) |
| Session Context | None | Built-in learning |
| Testing | Limited | 125+ tests |

### Migration Benefits

1. **Smaller dependency footprint** - No CrewAI/LangChain required
2. **Interactive configuration** - Socratic questioning adapts to your needs
3. **Cost optimization** - Progressive tier escalation saves 70-85%
4. **Learning** - Session context remembers your preferences
5. **Extensibility** - Create custom templates easily

## Migration Map

| Deprecated Workflow | Meta-Workflow Template |
|---------------------|----------------------|
| `ReleasePreparationCrew` | `empathy meta-workflow run release-prep` |
| `TestCoverageBoostCrew` | `empathy meta-workflow run test-coverage-boost` |
| `TestMaintenanceCrew` | `empathy meta-workflow run test-maintenance` |
| `ManageDocumentationCrew` | `empathy meta-workflow run manage-docs` |

## Step-by-Step Migration

### 1. Release Preparation

**Before (deprecated):**
```python
from empathy_os.workflows.release_prep_crew import ReleasePreparationCrew

crew = ReleasePreparationCrew(
    project_root=".",
    quality_gates={
        "security": 0.0,
        "coverage": 80.0,
        "quality": 7.0,
        "documentation": 100.0,
    }
)
result = await crew.execute(path="./src")

if result.approved:
    print("Ready for release!")
else:
    for blocker in result.blockers:
        print(f"BLOCKER: {blocker}")
```

**After (meta-workflow):**
```bash
# CLI usage
empathy meta-workflow run release-prep

# The form will ask:
# - Run security vulnerability scan? [Yes/No]
# - Verify test coverage meets threshold? [Yes/No]
# - Minimum coverage threshold (%) [70%/80%/85%/90%]
# - Run code quality review? [Yes/No]
# - Verify documentation completeness? [Yes/No]
```

**Programmatic usage:**
```python
from empathy_os.meta_workflows import MetaOrchestrator
from empathy_os.meta_workflows.form_engine import SocraticFormEngine

# Create orchestrator
orchestrator = MetaOrchestrator()

# Run with form collection
result = await orchestrator.run_workflow(
    template_id="release-prep",
    project_root="./src",
)

if result.success:
    print(f"Cost: ${result.total_cost:.4f}")
    for agent_result in result.agent_results:
        print(f"- {agent_result.role}: {'✓' if agent_result.success else '✗'}")
```

### 2. Test Coverage Boost

**Before (deprecated):**
```python
from empathy_os.workflows.test_coverage_boost_crew import TestCoverageBoostCrew

crew = TestCoverageBoostCrew(
    target_coverage=85.0,
    project_root="."
)
result = await crew.execute()

print(f"Coverage improved by {result.coverage_improvement}%")
```

**After (meta-workflow):**
```bash
empathy meta-workflow run test-coverage-boost

# Form asks:
# - Target coverage percentage [70%/75%/80%/85%/90%]
# - Test style preference [pytest/unittest/auto-detect]
# - Prioritize high-impact files? [Yes/No]
# - Include edge case tests? [Yes/No]
```

### 3. Test Maintenance

**Before (deprecated):**
```python
from empathy_os.workflows.test_maintenance_crew import TestMaintenanceCrew, CrewConfig

config = CrewConfig(
    max_files_per_run=10,
    staleness_threshold_days=7,
    enable_auto_validation=True,
)
crew = TestMaintenanceCrew(".", config=config)
result = await crew.run(mode="full")
```

**After (meta-workflow):**
```bash
empathy meta-workflow run test-maintenance

# Form asks:
# - Maintenance mode [full/analyze/generate/validate/report]
# - Maximum files to process [5/10/20/50]
# - Staleness threshold (days) [3/7/14/30]
# - Enable auto-validation? [Yes/No]
```

### 4. Documentation Management

**Before (deprecated):**
```python
from empathy_os.workflows.manage_documentation import ManageDocumentationCrew

crew = ManageDocumentationCrew(project_root=".")
result = await crew.execute(path="./src")

print(result.formatted_report)
```

**After (meta-workflow):**
```bash
empathy meta-workflow run manage-docs

# Form asks:
# - Check for missing docstrings? [Yes/No]
# - Check README freshness? [Yes/No]
# - Check API documentation? [Yes/No]
# - Generate update suggestions? [Yes/No]
```

## Advanced Usage

### Using Defaults (Non-Interactive)

Skip the form and use default values:

```bash
empathy meta-workflow run release-prep --use-defaults
```

### Custom Templates

Create your own template based on built-in ones:

```python
from empathy_os.meta_workflows.builtin_templates import RELEASE_PREP_TEMPLATE
from empathy_os.meta_workflows import TemplateRegistry

# Copy and modify
my_template = RELEASE_PREP_TEMPLATE
my_template.template_id = "my-release-prep"
my_template.form_schema.questions[2].default = "90%"  # Higher coverage

# Save
registry = TemplateRegistry()
registry.save_template(my_template)

# Use
# empathy meta-workflow run my-release-prep
```

### Programmatic Form Responses

Provide form responses programmatically:

```python
from empathy_os.meta_workflows import MetaOrchestrator
from empathy_os.meta_workflows.models import FormResponse

orchestrator = MetaOrchestrator()

# Pre-filled responses
responses = FormResponse(
    template_id="release-prep",
    responses={
        "security_scan": "Yes",
        "test_coverage_check": "Yes",
        "coverage_threshold": "85%",
        "quality_review": "Yes",
        "doc_verification": "No",  # Skip docs
    }
)

result = await orchestrator.run_workflow(
    template_id="release-prep",
    form_response=responses,
)
```

## FAQ

### Q: Do I need to install CrewAI?

No. The meta-workflow system uses the Anthropic SDK directly. CrewAI is now an optional dependency:

```bash
# Standard install (no CrewAI needed)
pip install empathy-framework

# If you want CrewAI (for legacy code)
pip install empathy-framework[crewai]
```

### Q: Will the old Crew workflows stop working?

Not immediately. They emit deprecation warnings but continue to function. Plan to migrate before the next major version (v5.0.0) when they may be removed.

### Q: How do I suppress the deprecation warning?

If you must use the old workflows temporarily:

```python
import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning, module="empathy_os.workflows")
```

### Q: What about custom Crew workflows I created?

Custom workflows based on the Crew pattern can continue using EmpathyLLMExecutor. Consider migrating to meta-workflow templates for better maintainability:

1. Define a `FormSchema` with questions
2. Create `AgentCompositionRule` entries for each agent
3. Save as a `MetaWorkflowTemplate`
4. Run with `empathy meta-workflow run <your-template-id>`

### Q: How do I track execution costs?

The meta-workflow system tracks costs automatically:

```python
result = await orchestrator.run_workflow("release-prep")

print(f"Total cost: ${result.total_cost:.4f}")
for agent_result in result.agent_results:
    print(f"  {agent_result.role}: ${agent_result.cost:.4f} ({agent_result.tier_used})")
```

## Support

- **Issues**: [GitHub Issues](https://github.com/Smart-AI-Memory/empathy-framework/issues)
- **Discussions**: [GitHub Discussions](https://github.com/Smart-AI-Memory/empathy-framework/discussions)
- **Documentation**: [docs/META_WORKFLOWS.md](META_WORKFLOWS.md)
