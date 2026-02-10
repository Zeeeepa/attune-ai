#!/usr/bin/env python3
"""Agent Team Creation Demo — Illustrates v2.5.1 Phase 1-4 Features.

This script demonstrates the new agent orchestration capabilities:

  Phase 1: AgentStateStore — persistent state, checkpoints, recovery
  Phase 2: SDKAgent — progressive tier escalation (CHEAP → CAPABLE → PREMIUM)
  Phase 3: DynamicTeam — build teams from templates with 4 strategies
  Phase 4: WorkflowComposer — compose entire workflows into teams

Run:
    uv run python examples/agent_team_demo.py

No API key required — agents use rule-based fallback when no LLM is available.
"""

from __future__ import annotations

import asyncio
import json
import shutil
import sys
import tempfile
from pathlib import Path

# Ensure the source tree is importable
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


def section(title: str) -> None:
    """Print a section header."""
    width = 60
    print(f"\n{'=' * width}")
    print(f"  {title}")
    print(f"{'=' * width}\n")


# ---------------------------------------------------------------------------
# Phase 1: Agent State Persistence
# ---------------------------------------------------------------------------

def demo_state_persistence(tmp_dir: str) -> None:
    """Demonstrate AgentStateStore: record, checkpoint, recover."""
    section("Phase 1: Agent State Persistence")

    from attune.agents.state.store import AgentStateStore

    store = AgentStateStore(storage_dir=tmp_dir)

    # 1. Record agent start
    exec_id = store.record_start(
        agent_id="security-auditor-01",
        role="Security Auditor",
        input_summary="Scan src/ for vulnerabilities",
    )
    print(f"  Started execution: {exec_id}")

    # 2. Save a checkpoint mid-execution
    store.save_checkpoint(
        agent_id="security-auditor-01",
        checkpoint_data={
            "completed_stages": ["triage"],
            "pending_stages": ["deep-scan", "report"],
            "findings_so_far": 3,
        },
    )
    print("  Saved mid-execution checkpoint")

    # 3. Record completion
    store.record_completion(
        agent_id="security-auditor-01",
        execution_id=exec_id,
        success=True,
        findings={"critical": 0, "high": 1, "medium": 2, "low": 5},
        score=92.0,
        cost=0.03,
        execution_time_ms=1500.0,
        tier_used="capable",
        confidence=0.9,
    )
    print("  Recorded completion (score=92, cost=$0.03)")

    # 4. Query state
    state = store.get_agent_state("security-auditor-01")
    if state:
        print(f"\n  Agent State Summary:")
        print(f"    Role:            {state.role}")
        print(f"    Total executions: {state.total_executions}")
        print(f"    Success rate:     {state.success_rate:.0%}")
        print(f"    Total cost:       ${state.total_cost:.3f}")
        print(f"    History entries:   {len(state.execution_history)}")

    # 5. Recover checkpoint
    checkpoint = store.get_last_checkpoint("security-auditor-01")
    if checkpoint:
        print(f"    Last checkpoint:  {checkpoint['completed_stages']}")

    # 6. Search agents by role
    results = store.search_history(role="Security", min_success_rate=0.5)
    print(f"\n  Search 'Security' agents (>50% success): {len(results)} found")

    return store


# ---------------------------------------------------------------------------
# Phase 2: SDK Agent with Tier Escalation
# ---------------------------------------------------------------------------

def demo_sdk_agent(store: "AgentStateStore") -> None:
    """Demonstrate SDKAgent with progressive tier escalation."""
    section("Phase 2: SDK Agent — Tier Escalation")

    from attune.agents.sdk.sdk_agent import SDKAgent
    from attune.agents.sdk.sdk_models import SDK_AVAILABLE, SDKExecutionMode

    print(f"  Agent SDK available: {SDK_AVAILABLE}")
    print(f"  Execution modes:     {[m.value for m in SDKExecutionMode]}")

    # Create agent with persistent state
    agent = SDKAgent(
        agent_id="demo-reviewer",
        role="Code Reviewer",
        system_prompt="You are a code quality expert. Review code for issues.",
        mode=SDKExecutionMode.TOOLS_ONLY,
        state_store=store,
    )

    print(f"\n  Created SDKAgent:")
    print(f"    ID:    {agent.agent_id}")
    print(f"    Role:  {agent.role}")
    print(f"    Mode:  {agent.mode.value}")
    print(f"    Tier:  {agent.current_tier.value} (starts CHEAP)")

    # Process some input (uses rule-based fallback without API key)
    result = agent.process({
        "task": "review",
        "code": "def add(x, y): return x + y",
        "language": "python",
    })

    print(f"\n  Execution Result:")
    print(f"    Success:    {result.success}")
    print(f"    Tier used:  {result.tier_used}")
    print(f"    Escalated:  {result.escalated}")
    print(f"    SDK used:   {result.sdk_used}")
    print(f"    Cost:       ${result.cost:.4f}")
    print(f"    Time:       {result.execution_time_ms:.1f}ms")

    # Check that state was persisted
    agent_state = store.get_agent_state("demo-reviewer")
    if agent_state:
        print(f"\n  Persistent State (recorded automatically):")
        print(f"    Executions: {agent_state.total_executions}")
        print(f"    Success:    {agent_state.successful_executions}")
        print(f"    Failed:     {agent_state.failed_executions}")


# ---------------------------------------------------------------------------
# Phase 3: Dynamic Team Composition
# ---------------------------------------------------------------------------

def demo_dynamic_team(store: "AgentStateStore") -> None:
    """Demonstrate DynamicTeamBuilder with templates and strategies."""
    section("Phase 3: Dynamic Team Composition")

    from attune.orchestration.agent_templates import (
        get_all_templates,
        get_template,
        get_templates_by_tier,
    )
    from attune.orchestration.team_builder import DynamicTeamBuilder
    from attune.orchestration.team_store import TeamSpecification

    # Show available templates
    templates = get_all_templates()
    print(f"  Available templates: {len(templates)}")
    for t in templates:
        print(f"    - {t.id:<30} [{t.tier_preference}] {t.role}")

    # Build team from specification
    print(f"\n  Building 'code-quality-review' team from spec...")

    spec = TeamSpecification(
        name="code-quality-review",
        agents=[
            {"template_id": "security_auditor", "role": "Security Auditor"},
            {"template_id": "code_reviewer", "role": "Code Reviewer"},
            {"template_id": "test_coverage_analyzer", "role": "Coverage Analyzer"},
        ],
        strategy="parallel",
        quality_gates={"min_score": 70},
    )

    builder = DynamicTeamBuilder(state_store=store)
    team = builder.build_from_spec(spec)

    print(f"    Team:     {team.team_name}")
    print(f"    Strategy: {team.strategy}")
    print(f"    Agents:   {len(team.agents)}")
    for agent in team.agents:
        print(f"      - {agent.role} ({agent.agent_id})")
    print(f"    Gates:    {len(team.quality_gates)}")

    # Execute the team
    print(f"\n  Executing team (parallel strategy)...")
    result = asyncio.run(team.execute({
        "task": "Review code quality",
        "path": "src/attune/",
        "language": "python",
    }))

    print(f"\n  Team Result:")
    print(f"    Success:     {result.success}")
    print(f"    Strategy:    {result.strategy}")
    print(f"    Total cost:  ${result.total_cost:.4f}")
    print(f"    Time:        {result.execution_time_ms:.1f}ms")
    print(f"    Agent results:")
    for ar in result.agent_results:
        print(f"      - {ar.role}: success={ar.success}, tier={ar.tier_used}, "
              f"escalated={ar.escalated}")
    if result.quality_gate_results:
        print(f"    Quality gates:")
        for gate_name, passed in result.quality_gate_results.items():
            status = "PASS" if passed else "FAIL"
            print(f"      - {gate_name}: {status}")

    # Build team from MetaOrchestrator plan format
    print(f"\n  Building team from execution plan...")
    plan_team = builder.build_from_plan({
        "name": "security-deep-dive",
        "agents": [
            {"template_id": "security_auditor"},
            {"template_id": "architecture_analyst"},
        ],
        "strategy": "two_phase",
        "quality_gates": {"security_score": 80},
    })
    print(f"    Built '{plan_team.team_name}' with {len(plan_team.agents)} agents "
          f"({plan_team.strategy} strategy)")

    # Show tier distribution
    for tier in ["CHEAP", "CAPABLE", "PREMIUM"]:
        tier_templates = get_templates_by_tier(tier)
        print(f"\n  {tier} tier templates: {[t.id for t in tier_templates]}")


# ---------------------------------------------------------------------------
# Phase 4: Workflow Composition
# ---------------------------------------------------------------------------

def demo_workflow_composition(store: "AgentStateStore") -> None:
    """Demonstrate WorkflowComposer wrapping workflows as team agents."""
    section("Phase 4: Workflow Composition")

    from attune.orchestration.workflow_composer import WorkflowComposer
    from attune.orchestration.workflow_agent_adapter import WorkflowAgentAdapter

    print("  WorkflowComposer wraps entire BaseWorkflow subclasses")
    print("  as participants in a DynamicTeam.\n")

    print("  WorkflowAgentAdapter bridges async/sync:")
    print("    workflow.execute() -> SDKAgentResult\n")

    print("  Example usage (requires workflow subclasses):")
    print("    composer = WorkflowComposer(state_store=store)")
    print("    team = composer.compose(")
    print('        team_name="comprehensive-review",')
    print("        workflows=[")
    print('            {"workflow": SecurityAuditWorkflow, "kwargs": {"path": "src/"}},')
    print('            {"workflow": CodeReviewWorkflow, "kwargs": {"diff": "..."}},')
    print("        ],")
    print('        strategy="parallel",')
    print('        quality_gates={"min_score": 70},')
    print("    )")
    print("    result = await team.execute({'target': 'src/'})")

    # Demonstrate adapter directly
    print("\n  WorkflowAgentAdapter attributes:")
    print("    - workflow_class:  BaseWorkflow subclass to wrap")
    print("    - workflow_kwargs: Constructor kwargs forwarded to workflow")
    print("    - agent_id:        Unique ID (auto-generated if None)")
    print("    - role:            Human-readable name")
    print("    - state_store:     Optional persistent store forwarded to workflow")


# ---------------------------------------------------------------------------
# State Recovery Demo
# ---------------------------------------------------------------------------

def demo_recovery(store: "AgentStateStore") -> None:
    """Demonstrate agent crash recovery."""
    section("Bonus: Agent Recovery")

    from attune.agents.state.recovery import AgentRecoveryManager

    recovery = AgentRecoveryManager(state_store=store)

    # Simulate an interrupted agent
    exec_id = store.record_start(
        agent_id="interrupted-agent",
        role="Performance Profiler",
        input_summary="Profile hot paths",
    )
    store.save_checkpoint(
        agent_id="interrupted-agent",
        checkpoint_data={
            "completed": ["collect_metrics"],
            "pending": ["analyze", "report"],
            "partial_results": {"bottleneck": "json_parsing"},
        },
    )
    # Note: No record_completion — simulates a crash

    print("  Simulated crash of 'interrupted-agent'")

    # Find interrupted agents
    interrupted = recovery.find_interrupted_agents()
    print(f"  Found {len(interrupted)} interrupted agent(s)")

    for record in interrupted:
        checkpoint = recovery.recover_agent(record.agent_id)
        if checkpoint:
            print(f"\n  Recovered checkpoint for '{record.agent_id}':")
            print(f"    Completed stages: {checkpoint.get('completed', [])}")
            print(f"    Pending stages:   {checkpoint.get('pending', [])}")
            print(f"    Partial results:  {checkpoint.get('partial_results', {})}")

    # Mark as abandoned
    for record in interrupted:
        recovery.mark_abandoned(record.agent_id)
    print(f"\n  Marked {len(interrupted)} agent(s) as abandoned")


# ---------------------------------------------------------------------------
# Summary
# ---------------------------------------------------------------------------

def print_summary() -> None:
    """Print what was demonstrated."""
    section("Summary: v2.5.1 Agent Orchestration")

    features = [
        ("AgentStateStore", "Persistent JSON state, checkpoints, history trimming, recovery"),
        ("SDKAgent", "Progressive CHEAP→CAPABLE→PREMIUM escalation, SDK/API dual-mode"),
        ("DynamicTeamBuilder", "Build teams from specs, plans, or saved configs"),
        ("DynamicTeam", "4 strategies: parallel, sequential, two_phase, delegation"),
        ("13 Agent Templates", "Security, code review, test coverage, perf, docs, etc."),
        ("Quality Gates", "Per-agent and cross-team threshold enforcement"),
        ("WorkflowComposer", "Compose BaseWorkflow subclasses into DynamicTeam"),
        ("AgentRecoveryManager", "Find interrupted agents, restore checkpoints"),
    ]

    for name, desc in features:
        print(f"  {name:<25} {desc}")

    print(f"\n  All features are opt-in (default None). Zero impact on existing code.")
    print(f"  Redis optional for single-process use. Required for multi-process coordination.")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    """Run the full demo."""
    print("\n" + "=" * 60)
    print("  Attune AI v2.5.1 — Agent Team Creation Demo")
    print("=" * 60)

    # Use a temporary directory for state files
    tmp_dir = tempfile.mkdtemp(prefix="attune-demo-state-")

    try:
        # Phase 1: State Persistence
        store = demo_state_persistence(tmp_dir)

        # Phase 2: SDK Agent
        demo_sdk_agent(store)

        # Phase 3: Dynamic Teams
        demo_dynamic_team(store)

        # Phase 4: Workflow Composition
        demo_workflow_composition(store)

        # Bonus: Recovery
        demo_recovery(store)

        # Summary
        print_summary()

        # Show persisted files
        section("Persisted State Files")
        state_dir = Path(tmp_dir)
        for f in sorted(state_dir.glob("*.json")):
            data = json.loads(f.read_text())
            agent_id = data.get("agent_id", "?")
            execs = data.get("total_executions", 0)
            print(f"  {f.name:<40} agent={agent_id}, executions={execs}")

    finally:
        # Cleanup
        shutil.rmtree(tmp_dir, ignore_errors=True)

    print(f"\n{'=' * 60}")
    print("  Demo complete! All state files cleaned up.")
    print(f"{'=' * 60}\n")


if __name__ == "__main__":
    main()
