"""Dynamic Analysis Node - Phase 2

Runs conditional dynamic analysis based on Phase 1 results.
Can skip if critical issues found, or deep-dive if patterns match.

Tools:
- Code Review (anti-pattern detection)
- Memory-Enhanced Debugging (historical bug correlation)
- Advanced Debugging (systematic linter-based)

Copyright 2025 Smart AI Memory, LLC
Licensed under Fair Source 0.9
"""

import asyncio
import logging
from datetime import datetime

from ..state import CodeInspectionState, InspectionPhase, add_audit_entry

logger = logging.getLogger(__name__)

# NOTE: CodeReviewAdapter and DebuggingAdapter have been deprecated.
# Dynamic analysis tools are now available through CLI workflows.
# See: empathy workflow run bug-predict


async def run_dynamic_analysis(state: CodeInspectionState) -> CodeInspectionState:
    """Phase 2: Run conditional dynamic analysis.

    Args:
        state: Current inspection state

    Returns:
        Updated state with dynamic analysis results

    """
    logger.info(f"[Phase 2] Starting dynamic analysis for {state['project_path']}")

    state["current_phase"] = InspectionPhase.DYNAMIC_ANALYSIS.value
    add_audit_entry(state, "dynamic_analysis", "Starting Phase 2: Dynamic Analysis")

    state["project_path"]
    enabled_tools = state["enabled_tools"]

    # Get security context from Phase 1 for informed review
    if state.get("security_scan_result"):
        state["security_scan_result"].get("findings", [])

    # Build list of tasks
    tasks = []
    task_names = []

    # NOTE: code_review and memory_debugging adapters have been deprecated.
    # Dynamic analysis tools are now available through CLI workflows.
    # See: empathy workflow run bug-predict
    if enabled_tools.get("code_review", True):
        logger.warning("code_review tool is deprecated - use 'empathy workflow run bug-predict'")

    if enabled_tools.get("memory_debugging", True):
        logger.warning(
            "memory_debugging tool is deprecated - use 'empathy workflow run bug-predict'"
        )

    if not tasks:
        logger.warning("No dynamic analysis tools enabled")
        state["completed_phases"].append(InspectionPhase.DYNAMIC_ANALYSIS.value)
        return state

    # Run tasks (can be parallel or sequential)
    if state.get("parallel_mode", True) and len(tasks) > 1:
        logger.info(f"Running {len(tasks)} dynamic tools in parallel: {task_names}")
        results = await asyncio.gather(*tasks, return_exceptions=True)
    else:
        logger.info(f"Running {len(tasks)} dynamic tools: {task_names}")
        results = []
        for task in tasks:
            try:
                result = await task
                results.append(result)
            except Exception as e:
                results.append(e)

    # Process results
    total_findings = 0
    historical_matches = []

    for i, result in enumerate(results):
        tool_name = task_names[i]

        if isinstance(result, Exception):
            logger.error(f"Tool {tool_name} failed: {result}")
            state["errors"].append(f"{tool_name}: {result!s}")
            continue

        # Store result
        state["dynamic_analysis_results"][tool_name] = result

        # Also store in individual fields
        if tool_name == "code_review":
            state["code_review_result"] = result
        elif tool_name == "memory_debugging":
            state["memory_debugging_result"] = result
            # Extract historical matches
            historical_matches.extend(result.get("metadata", {}).get("historical_matches", []))
        elif tool_name == "advanced_debugging":
            state["advanced_debugging_result"] = result

        total_findings += result.get("findings_count", 0)

        logger.info(
            f"{tool_name}: status={result.get('status')}, "
            f"score={result.get('score')}, "
            f"findings={result.get('findings_count')}",
        )

    # Update state
    state["historical_patterns_matched"] = historical_matches
    state["completed_phases"].append(InspectionPhase.DYNAMIC_ANALYSIS.value)
    state["last_updated"] = datetime.now().isoformat()

    add_audit_entry(
        state,
        "dynamic_analysis",
        "Phase 2 complete",
        {
            "tools_run": task_names,
            "total_findings": total_findings,
            "historical_matches": len(historical_matches),
        },
    )

    logger.info(f"[Phase 2] Complete: {total_findings} findings")

    return state


async def run_deep_dive_analysis(state: CodeInspectionState) -> CodeInspectionState:
    """Deep-dive analysis triggered by historical pattern matches.

    Runs additional advanced debugging for files with pattern matches.

    Args:
        state: Current inspection state

    Returns:
        Updated state with deep-dive results

    """
    logger.info("[Phase 2+] Starting deep-dive analysis")

    state["deep_dive_triggered"] = True
    state["deep_dive_reason"] = "Historical pattern matches found"
    add_audit_entry(state, "deep_dive", "Starting deep-dive analysis")

    state["project_path"]

    # NOTE: DebuggingAdapter has been deprecated.
    # Advanced debugging is now available through CLI workflows.
    logger.warning("advanced_debugging tool is deprecated - use 'empathy workflow run bug-predict'")
    state["dynamic_analysis_results"]["advanced_debugging"] = {
        "status": "skipped",
        "message": "DebuggingAdapter deprecated - use CLI workflows",
        "findings_count": 0,
    }
    state["advanced_debugging_result"] = state["dynamic_analysis_results"]["advanced_debugging"]

    # Also run standard dynamic analysis
    state = await run_dynamic_analysis(state)

    add_audit_entry(
        state,
        "deep_dive",
        "Deep-dive complete",
        {"advanced_debugging_run": True},
    )

    return state


async def handle_skip_dynamic(state: CodeInspectionState) -> CodeInspectionState:
    """Handle skipping dynamic analysis due to critical issues.

    Args:
        state: Current inspection state

    Returns:
        Updated state with skip information

    """
    logger.info(f"[Phase 2] Skipping dynamic analysis: {state.get('skip_reason', 'unknown')}")

    state["dynamic_analysis_skipped"] = True
    state["completed_phases"].append(InspectionPhase.DYNAMIC_ANALYSIS.value)
    state["skipped_phases"].append(f"dynamic_analysis: {state.get('skip_reason', 'unknown')}")

    add_audit_entry(
        state,
        "dynamic_analysis",
        "Phase 2 skipped",
        {"reason": state.get("skip_reason", "unknown")},
    )

    return state
