"""Static Analysis Node - Phase 1

Runs all static analysis tools in parallel using asyncio.gather.
Following the pattern from book_production/pipeline.py.

Tools run in parallel:
- Code Health (lint, format, types)
- Security Scanner (OWASP, secrets)
- Tech Debt (TODO/FIXME scanning)
- Test Quality (code analysis only)

Copyright 2025 Smart AI Memory, LLC
Licensed under Fair Source 0.9
"""

import asyncio
import logging
from datetime import datetime

from ..adapters import CodeHealthAdapter
from ..state import CodeInspectionState, InspectionPhase, add_audit_entry

logger = logging.getLogger(__name__)

# NOTE: SecurityAdapter, TechDebtAdapter, TestQualityAdapter have been deprecated.
# These tools are now available through CLI workflows.
# See: empathy workflow run security-audit, empathy workflow run test-coverage


async def run_static_analysis(state: CodeInspectionState) -> CodeInspectionState:
    """Phase 1: Run all static analysis tools in parallel.

    Following the asyncio.gather pattern from book_production/pipeline.py.

    Args:
        state: Current inspection state

    Returns:
        Updated state with static analysis results

    """
    logger.info(f"[Phase 1] Starting static analysis for {state['project_path']}")

    state["current_phase"] = InspectionPhase.STATIC_ANALYSIS.value
    add_audit_entry(state, "static_analysis", "Starting Phase 1: Static Analysis")

    project_path = state["project_path"]
    enabled_tools = state["enabled_tools"]

    # Build list of tasks for enabled tools
    tasks = []
    task_names = []

    if enabled_tools.get("code_health", True):
        adapter = CodeHealthAdapter(
            project_root=project_path,
            config=state["tool_configs"].get("code_health"),
            target_paths=state.get("target_paths") or None,
        )
        tasks.append(adapter.analyze())
        task_names.append("code_health")

    # NOTE: security, tech_debt, and test_quality adapters have been deprecated.
    # These tools are now available through CLI workflows.
    if enabled_tools.get("security", True):
        logger.warning("security tool is deprecated - use 'empathy workflow run security-audit'")

    if enabled_tools.get("tech_debt", True):
        logger.warning("tech_debt tool is deprecated - use 'empathy workflow run bug-predict'")

    if enabled_tools.get("test_quality", True):
        logger.warning("test_quality tool is deprecated - use 'empathy workflow run test-coverage'")

    if not tasks:
        logger.warning("No static analysis tools enabled")
        state["completed_phases"].append(InspectionPhase.STATIC_ANALYSIS.value)
        return state

    # Run all tasks in parallel (or sequentially if parallel mode disabled)
    if state.get("parallel_mode", True):
        logger.info(f"Running {len(tasks)} tools in parallel: {task_names}")
        results = await asyncio.gather(*tasks, return_exceptions=True)
    else:
        logger.info(f"Running {len(tasks)} tools sequentially: {task_names}")
        results = []
        for task in tasks:
            try:
                result = await task
                results.append(result)
            except Exception as e:
                results.append(e)

    # Process results
    total_findings = 0
    critical_count = 0

    for i, result in enumerate(results):
        tool_name = task_names[i]

        if isinstance(result, Exception):
            logger.error(f"Tool {tool_name} failed: {result}")
            state["errors"].append(f"{tool_name}: {result!s}")
            continue

        # Store result
        state["static_analysis_results"][tool_name] = result

        # Also store in individual fields for easy access
        if tool_name == "code_health":
            state["code_health_result"] = result
        elif tool_name == "security":
            state["security_scan_result"] = result
        elif tool_name == "test_quality":
            state["test_quality_result"] = result
        elif tool_name == "tech_debt":
            state["tech_debt_result"] = result

        # Aggregate counts
        total_findings += result.get("findings_count", 0)
        critical_count += result.get("findings_by_severity", {}).get("critical", 0)

        logger.info(
            f"{tool_name}: status={result.get('status')}, "
            f"score={result.get('score')}, "
            f"findings={result.get('findings_count')}",
        )

    # Update state with aggregates
    state["static_findings_count"] = total_findings
    state["static_critical_count"] = critical_count
    state["completed_phases"].append(InspectionPhase.STATIC_ANALYSIS.value)
    state["last_updated"] = datetime.now().isoformat()

    # Add message for audit trail
    try:
        from langchain_core.messages import AIMessage

        state["messages"].append(
            AIMessage(
                content=f"Static analysis complete: {len(tasks)} tools run, "
                f"{total_findings} findings ({critical_count} critical)",
            ),
        )
    except ImportError:
        pass

    add_audit_entry(
        state,
        "static_analysis",
        "Phase 1 complete",
        {
            "tools_run": task_names,
            "total_findings": total_findings,
            "critical_count": critical_count,
            "results_summary": {
                name: {
                    "status": state["static_analysis_results"].get(name, {}).get("status"),
                    "score": state["static_analysis_results"].get(name, {}).get("score"),
                    "findings": state["static_analysis_results"]
                    .get(name, {})
                    .get("findings_count"),
                }
                for name in task_names
                if name in state["static_analysis_results"]
            },
        },
    )

    logger.info(f"[Phase 1] Complete: {total_findings} findings, {critical_count} critical")

    return state
