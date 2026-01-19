# Crew Integration Guide

> **DEPRECATED (v4.4.0):** CrewAI integration is deprecated in favor of native composition patterns. The meta-workflow system provides equivalent functionality with 6 built-in patterns (Sequential, Parallel, Debate, Teaching, Refinement, Adaptive) and requires no external dependencies. See [CREWAI_MIGRATION.md](../CREWAI_MIGRATION.md) for migration instructions.

Guide for integrating existing CrewAI crews into workflows (legacy).

## Available Crews

### 1. Code Review Crew
**File:** `empathy_llm_toolkit/agent_factory/crews/code_review.py`
**Main Method:** `.review(diff, files_changed)`
**Agents:** 5 agents (Lead, Security, Architecture, Quality, Performance)

**Usage Example:**
```python
from empathy_llm_toolkit.agent_factory.crews.code_review import CodeReviewCrew

async def run_stage(self, stage_name, tier, input_data):
    await self._initialize_crew()

    if stage_name == "review":
        result = await self._crew.review(
            diff=input_data.get("diff", ""),
            files_changed=input_data.get("files", [])
        )

        return {
            "verdict": result.verdict.value,
            "findings": [
                {
                    "title": f.title,
                    "severity": f.severity.value,
                    "category": f.category.value,
                    "suggestion": f.suggestion
                }
                for f in result.critical_findings
            ],
            "summary": result.summary
        }, 0, 0
```

### 2. Refactoring Crew
**File:** `empathy_llm_toolkit/agent_factory/crews/refactoring.py`
**Main Method:** `.analyze(code, file_path)`
**Agents:** 3 agents (Analyzer, Refactorer, Reviewer)

**Usage Example:**
```python
from empathy_llm_toolkit.agent_factory.crews.refactoring import RefactoringCrew

async def run_stage(self, stage_name, tier, input_data):
    await self._initialize_crew()

    if stage_name == "analyze":
        result = await self._crew.analyze(
            code=input_data.get("code", ""),
            file_path=input_data.get("path", ".")
        )

        return {
            "findings": [
                {
                    "title": f.title,
                    "description": f.description,
                    "category": f.category.value,
                    "severity": f.severity.value,
                    "file": f.file_path,
                    "lines": f"{f.start_line}-{f.end_line}"
                }
                for f in result.findings
            ],
            "summary": f"Found {len(result.findings)} refactoring opportunities"
        }, 0, 0
```

### 3. Security Audit Crew
**File:** `empathy_llm_toolkit/agent_factory/crews/security_audit.py`
**Main Method:** `.audit(code, file_path)`
**Agents:** 3 agents (Scanner, Analyst, Auditor)

**Usage Example:**
```python
from empathy_llm_toolkit.agent_factory.crews.security_audit import SecurityAuditCrew

async def run_stage(self, stage_name, tier, input_data):
    await self._initialize_crew()

    if stage_name == "audit":
        result = await self._crew.audit(
            code=input_data.get("code", ""),
            file_path=input_data.get("path", ".")
        )

        return {
            "vulnerabilities": [
                {
                    "title": v.title,
                    "severity": v.severity.value,
                    "cwe_id": v.cwe_id,
                    "remediation": v.remediation
                }
                for v in result.vulnerabilities
            ],
            "risk_score": result.overall_risk_score,
            "summary": result.summary
        }, 0, 0
```

### 4. Health Check Crew
**File:** `empathy_llm_toolkit/agent_factory/crews/health_check.py`
**Main Method:** `.check(project_path)`
**Agents:** 3 agents (Metrics, Tester, Reporter)

**Usage Example:**
```python
from empathy_llm_toolkit.agent_factory.crews.health_check import HealthCheckCrew

async def run_stage(self, stage_name, tier, input_data):
    await self._initialize_crew()

    if stage_name == "diagnose":
        result = await self._crew.check(
            project_path=input_data.get("path", ".")
        )

        return {
            "health_score": result.health_score,
            "metrics": result.metrics,
            "issues": [
                {
                    "category": i.category,
                    "severity": i.severity,
                    "description": i.description
                }
                for i in result.issues
            ],
            "recommendations": result.recommendations
        }, 0, 0
```

## Complete Workflow Template

Here's a complete workflow template that works with any crew:

```python
"""Workflow with Crew Integration

Replace CREW_NAME, CrewClass, and method_name with your specific crew.
"""

import logging
from typing import Any

from empathy_os.workflows.base import BaseWorkflow, ModelTier

logger = logging.getLogger(__name__)


class MyCrew

Workflow(BaseWorkflow):
    """Workflow using CREW_NAME crew."""

    name = "my-crew-workflow"
    description = "Description here"
    stages = ["stage1", "stage2"]
    tier_map = {
        "stage1": ModelTier.CAPABLE,
        "stage2": ModelTier.CAPABLE,
    }

    def __init__(self, **kwargs: Any):
        """Initialize workflow."""
        super().__init__(**kwargs)
        self._crew: Any = None
        self._crew_available = False

    async def _initialize_crew(self) -> None:
        """Initialize the crew."""
        if self._crew is not None:
            return

        try:
            # Import your crew here
            from empathy_llm_toolkit.agent_factory.crews.YOUR_CREW import YourCrew

            self._crew = YourCrew()
            self._crew_available = True
            logger.info("YourCrew initialized successfully")
        except ImportError as e:
            logger.warning(f"YourCrew not available: {e}")
            self._crew_available = False

    async def run_stage(
        self,
        stage_name: str,
        tier: ModelTier,
        input_data: Any,
    ) -> tuple[Any, int, int]:
        """Execute crew for the given stage."""
        await self._initialize_crew()

        if not self._crew_available:
            return {"error": "Crew not available"}, 0, 0

        try:
            # Route to appropriate crew method based on stage
            if stage_name == "stage1":
                result = await self._crew.your_method(
                    # Pass appropriate parameters
                    param1=input_data.get("key1"),
                    param2=input_data.get("key2")
                )

                # Format and return results
                return {
                    "status": "completed",
                    "data": result
                }, 0, 0

            elif stage_name == "stage2":
                # Another stage
                return {"status": "completed"}, 0, 0

            else:
                return {"error": f"Unknown stage: {stage_name}"}, 0, 0

        except Exception as e:
            logger.error(f"Crew execution failed: {e}")
            return {"error": str(e)}, 0, 0
```

## Crew Method Quick Reference

| Crew | Import Path | Main Method | Key Parameters |
|------|-------------|-------------|----------------|
| **Code Review** | `crews.code_review.CodeReviewCrew` | `.review()` | `diff`, `files_changed` |
| **Refactoring** | `crews.refactoring.RefactoringCrew` | `.analyze()` | `code`, `file_path` |
| **Security Audit** | `crews.security_audit.SecurityAuditCrew` | `.audit()` | `code`, `file_path` |
| **Health Check** | `crews.health_check.HealthCheckCrew` | `.check()` | `project_path` |

## Next Steps

1. **Update your test5 workflow** using the RefactoringCrew example above
2. **Test the integration** by running the workflow
3. **Create more workflows** using other crews as needed

## Tips

- ✅ Always initialize the crew in `_initialize_crew()` method
- ✅ Check `self._crew_available` before using the crew
- ✅ Handle errors gracefully with try/except
- ✅ Return meaningful results that match your workflow needs
- ✅ Use appropriate ModelTier for each stage

---

Generated for Empathy Framework v3.7.0
