"""Tests for AgentRecoveryManager.

Tests interrupted agent detection, checkpoint recovery, and
abandoned execution marking.

Copyright 2026 Smart-AI-Memory
Licensed under Apache 2.0
"""

from pathlib import Path

from attune.agents.state.recovery import AgentRecoveryManager
from attune.agents.state.store import AgentStateStore


class TestAgentRecoveryManager:
    """Tests for AgentRecoveryManager."""

    def test_find_interrupted_agents_detects_running(self, tmp_path: Path) -> None:
        """Test that agents with 'running' executions are detected."""
        store = AgentStateStore(storage_dir=str(tmp_path))

        # Agent with running execution (simulates crash)
        store.record_start("crashed-agent", "Auditor", "Was scanning...")

        # Agent with completed execution (should not be detected)
        exec_id = store.record_start("good-agent", "Tester")
        store.record_completion(
            "good-agent", exec_id,
            success=True, findings={}, score=90.0, cost=0.01,
            execution_time_ms=100.0,
        )

        recovery = AgentRecoveryManager(store)
        interrupted = recovery.find_interrupted_agents()

        assert len(interrupted) == 1
        assert interrupted[0].agent_id == "crashed-agent"

    def test_find_interrupted_returns_empty_when_none(
        self, tmp_path: Path
    ) -> None:
        """Test that empty list returned when no agents are interrupted."""
        store = AgentStateStore(storage_dir=str(tmp_path))
        exec_id = store.record_start("healthy-agent", "Auditor")
        store.record_completion(
            "healthy-agent", exec_id,
            success=True, findings={}, score=95.0, cost=0.0,
            execution_time_ms=50.0,
        )

        recovery = AgentRecoveryManager(store)
        assert recovery.find_interrupted_agents() == []

    def test_recover_agent_returns_checkpoint(self, tmp_path: Path) -> None:
        """Test that recovery returns the last checkpoint."""
        store = AgentStateStore(storage_dir=str(tmp_path))
        store.record_start("checkpoint-agent", "Long Runner")
        store.save_checkpoint(
            "checkpoint-agent",
            {"step": 5, "partial": ["result1", "result2"]},
        )

        recovery = AgentRecoveryManager(store)
        checkpoint = recovery.recover_agent("checkpoint-agent")

        assert checkpoint == {"step": 5, "partial": ["result1", "result2"]}

    def test_recover_agent_returns_none_without_checkpoint(
        self, tmp_path: Path
    ) -> None:
        """Test that recovery returns None when no checkpoint exists."""
        store = AgentStateStore(storage_dir=str(tmp_path))
        store.record_start("no-checkpoint", "Runner")

        recovery = AgentRecoveryManager(store)
        assert recovery.recover_agent("no-checkpoint") is None

    def test_recover_agent_returns_none_for_unknown(
        self, tmp_path: Path
    ) -> None:
        """Test that recovery returns None for unknown agents."""
        store = AgentStateStore(storage_dir=str(tmp_path))
        recovery = AgentRecoveryManager(store)
        assert recovery.recover_agent("nonexistent") is None

    def test_mark_abandoned_updates_running_executions(
        self, tmp_path: Path
    ) -> None:
        """Test that mark_abandoned changes running to interrupted."""
        store = AgentStateStore(storage_dir=str(tmp_path))

        # Start two executions (simulates crash mid-second)
        store.record_start("abandon-agent", "Multi Runner")
        store.record_start("abandon-agent", "Multi Runner")

        recovery = AgentRecoveryManager(store)
        recovery.mark_abandoned("abandon-agent")

        state = store.get_agent_state("abandon-agent")
        assert state is not None
        for execution in state.execution_history:
            assert execution.status == "interrupted"
            assert execution.error == "Marked as interrupted by recovery manager"
        assert state.failed_executions == 2

    def test_mark_abandoned_skips_completed_executions(
        self, tmp_path: Path
    ) -> None:
        """Test that mark_abandoned only affects running executions."""
        store = AgentStateStore(storage_dir=str(tmp_path))

        # One completed, one running
        exec1 = store.record_start("mixed-agent", "Auditor")
        store.record_completion(
            "mixed-agent", exec1,
            success=True, findings={}, score=90.0, cost=0.0,
            execution_time_ms=100.0,
        )
        store.record_start("mixed-agent", "Auditor")  # Still running

        recovery = AgentRecoveryManager(store)
        recovery.mark_abandoned("mixed-agent")

        state = store.get_agent_state("mixed-agent")
        assert state is not None
        completed = [e for e in state.execution_history if e.status == "completed"]
        interrupted = [
            e for e in state.execution_history if e.status == "interrupted"
        ]
        assert len(completed) == 1
        assert len(interrupted) == 1

    def test_mark_abandoned_for_unknown_agent(self, tmp_path: Path) -> None:
        """Test that marking unknown agent doesn't crash."""
        store = AgentStateStore(storage_dir=str(tmp_path))
        recovery = AgentRecoveryManager(store)
        recovery.mark_abandoned("nonexistent")  # Should not raise
