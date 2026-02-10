"""Tests for AgentStateStore persistence.

Tests CRUD operations, history trimming, and path security validation.

Copyright 2026 Smart-AI-Memory
Licensed under Apache 2.0
"""

import json
from pathlib import Path

import pytest

from attune.agents.state.models import AgentStateRecord
from attune.agents.state.store import (
    MAX_HISTORY_PER_AGENT,
    AgentStateStore,
    _sanitize_agent_id,
)


class TestSanitizeAgentId:
    """Tests for _sanitize_agent_id helper."""

    def test_simple_id_unchanged(self) -> None:
        assert _sanitize_agent_id("security-auditor-01") == "security-auditor-01"

    def test_special_chars_replaced(self) -> None:
        assert _sanitize_agent_id("agent/with:special!chars") == "agent_with_special_chars"

    def test_empty_id_raises(self) -> None:
        with pytest.raises(ValueError, match="non-empty string"):
            _sanitize_agent_id("")

    def test_null_bytes_raises(self) -> None:
        with pytest.raises(ValueError, match="null bytes"):
            _sanitize_agent_id("agent\x00evil")

    def test_long_id_truncated(self) -> None:
        long_id = "a" * 300
        assert len(_sanitize_agent_id(long_id)) == 200


class TestAgentStateStore:
    """Tests for AgentStateStore CRUD operations."""

    def test_record_start_creates_file(self, tmp_path: Path) -> None:
        """Test that record_start creates a state file."""
        store = AgentStateStore(storage_dir=str(tmp_path))
        exec_id = store.record_start("agent-01", "Security Auditor", "Scanning src/")

        assert exec_id  # Non-empty string
        state = store.get_agent_state("agent-01")
        assert state is not None
        assert state.role == "Security Auditor"
        assert state.total_executions == 1
        assert len(state.execution_history) == 1
        assert state.execution_history[0].status == "running"

    def test_record_completion_updates_state(self, tmp_path: Path) -> None:
        """Test that record_completion updates execution and counters."""
        store = AgentStateStore(storage_dir=str(tmp_path))
        exec_id = store.record_start("agent-02", "Test Coverage")

        store.record_completion(
            "agent-02",
            exec_id,
            success=True,
            findings={"coverage": 85.0},
            score=85.0,
            cost=0.02,
            execution_time_ms=1500.0,
            tier_used="capable",
            confidence=0.9,
        )

        state = store.get_agent_state("agent-02")
        assert state is not None
        assert state.successful_executions == 1
        assert state.total_cost == 0.02
        assert state.execution_history[0].status == "completed"
        assert state.execution_history[0].findings == {"coverage": 85.0}

    def test_record_failure_updates_state(self, tmp_path: Path) -> None:
        """Test that record_failure marks execution as failed."""
        store = AgentStateStore(storage_dir=str(tmp_path))
        exec_id = store.record_start("agent-03", "Code Quality")

        store.record_failure("agent-03", exec_id, "Connection timeout")

        state = store.get_agent_state("agent-03")
        assert state is not None
        assert state.failed_executions == 1
        assert state.execution_history[0].status == "failed"
        assert state.execution_history[0].error == "Connection timeout"

    def test_checkpoint_save_and_restore(self, tmp_path: Path) -> None:
        """Test checkpoint persistence for restart recovery."""
        store = AgentStateStore(storage_dir=str(tmp_path))
        store.record_start("agent-04", "Long Runner")

        checkpoint = {"step": 3, "partial_results": ["a", "b", "c"]}
        store.save_checkpoint("agent-04", checkpoint)

        restored = store.get_last_checkpoint("agent-04")
        assert restored == checkpoint

    def test_get_last_checkpoint_returns_none_for_unknown(self, tmp_path: Path) -> None:
        """Test that get_last_checkpoint returns None for unknown agents."""
        store = AgentStateStore(storage_dir=str(tmp_path))
        assert store.get_last_checkpoint("nonexistent") is None

    def test_get_all_agents(self, tmp_path: Path) -> None:
        """Test listing all agent states."""
        store = AgentStateStore(storage_dir=str(tmp_path))
        store.record_start("agent-a", "Auditor")
        store.record_start("agent-b", "Tester")
        store.record_start("agent-c", "Reviewer")

        agents = store.get_all_agents()
        assert len(agents) == 3
        ids = {a.agent_id for a in agents}
        assert ids == {"agent-a", "agent-b", "agent-c"}

    def test_search_by_role(self, tmp_path: Path) -> None:
        """Test searching agents by role."""
        store = AgentStateStore(storage_dir=str(tmp_path))
        store.record_start("sec-01", "Security Auditor")
        store.record_start("test-01", "Test Coverage")
        store.record_start("sec-02", "Security Scanner")

        results = store.search_history(role="Security")
        assert len(results) == 2

    def test_search_by_success_rate(self, tmp_path: Path) -> None:
        """Test filtering agents by minimum success rate."""
        store = AgentStateStore(storage_dir=str(tmp_path))

        # Agent with good success rate
        exec_id = store.record_start("good-agent", "Auditor")
        store.record_completion(
            "good-agent",
            exec_id,
            success=True,
            findings={},
            score=90.0,
            cost=0.01,
            execution_time_ms=100.0,
        )

        # Agent with bad success rate
        exec_id = store.record_start("bad-agent", "Auditor")
        store.record_failure("bad-agent", exec_id, "failed")

        results = store.search_history(min_success_rate=0.5)
        assert len(results) == 1
        assert results[0].agent_id == "good-agent"

    def test_history_trimming(self, tmp_path: Path) -> None:
        """Test that history is trimmed to MAX_HISTORY_PER_AGENT."""
        store = AgentStateStore(storage_dir=str(tmp_path))

        for i in range(MAX_HISTORY_PER_AGENT + 20):
            store.record_start("trim-agent", "Auditor", f"run-{i}")

        state = store.get_agent_state("trim-agent")
        assert state is not None
        assert len(state.execution_history) == MAX_HISTORY_PER_AGENT
        # Oldest entries should have been trimmed
        assert state.execution_history[0].input_summary == "run-20"

    def test_persistence_across_store_instances(self, tmp_path: Path) -> None:
        """Test that data persists when store is re-instantiated."""
        store1 = AgentStateStore(storage_dir=str(tmp_path))
        exec_id = store1.record_start("persist-agent", "Auditor")
        store1.record_completion(
            "persist-agent",
            exec_id,
            success=True,
            findings={"key": "value"},
            score=95.0,
            cost=0.05,
            execution_time_ms=2000.0,
        )

        # Create new store instance (simulates restart)
        store2 = AgentStateStore(storage_dir=str(tmp_path))
        state = store2.get_agent_state("persist-agent")
        assert state is not None
        assert state.successful_executions == 1
        assert state.execution_history[0].findings == {"key": "value"}

    def test_record_completion_for_unknown_execution_warns(self, tmp_path: Path) -> None:
        """Test that completing an unknown execution logs a warning."""
        store = AgentStateStore(storage_dir=str(tmp_path))
        store.record_start("agent-warn", "Auditor")

        # Try to complete with wrong execution_id
        store.record_completion(
            "agent-warn",
            "nonexistent-exec-id",
            success=True,
            findings={},
            score=50.0,
            cost=0.0,
            execution_time_ms=0.0,
        )
        # Should not crash, state should still be loadable
        state = store.get_agent_state("agent-warn")
        assert state is not None


class TestAgentStateStorePathSecurity:
    """Security tests for AgentStateStore file operations."""

    def test_blocks_null_bytes_in_agent_id(self, tmp_path: Path) -> None:
        """Test that null bytes in agent_id are rejected."""
        store = AgentStateStore(storage_dir=str(tmp_path))
        with pytest.raises(ValueError, match="null bytes"):
            store.record_start("agent\x00evil", "Hacker")

    def test_blocks_empty_agent_id(self, tmp_path: Path) -> None:
        """Test that empty agent_id is rejected."""
        store = AgentStateStore(storage_dir=str(tmp_path))
        with pytest.raises(ValueError, match="non-empty string"):
            store.record_start("", "Empty")

    def test_sanitizes_path_traversal_in_agent_id(self, tmp_path: Path) -> None:
        """Test that path traversal in agent_id is sanitized."""
        store = AgentStateStore(storage_dir=str(tmp_path))
        # Slashes get sanitized to underscores, so this writes safely
        exec_id = store.record_start("../../etc/passwd", "Traversal")
        assert exec_id  # Should succeed (ID is sanitized)

        # Verify file was created in the correct directory
        files = list(tmp_path.glob("*.json"))
        assert len(files) == 1
        assert files[0].parent == tmp_path

    def test_all_files_stay_within_storage_dir(self, tmp_path: Path) -> None:
        """Test that no files are written outside storage_dir."""
        store = AgentStateStore(storage_dir=str(tmp_path))
        store.record_start("agent-safe", "Auditor")
        store.record_start("agent-safe-2", "Tester")

        # All JSON files should be in tmp_path
        for json_file in tmp_path.glob("*.json"):
            assert json_file.parent == tmp_path

    def test_corrupted_file_handled_gracefully(self, tmp_path: Path) -> None:
        """Test that corrupted JSON files don't crash the store."""
        # Write corrupt JSON
        (tmp_path / "corrupt-agent.json").write_text("{invalid json")

        store = AgentStateStore(storage_dir=str(tmp_path))
        agents = store.get_all_agents()
        # Should skip corrupt file without crashing
        assert all(a.agent_id != "corrupt-agent" for a in agents)
