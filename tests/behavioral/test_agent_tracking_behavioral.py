"""Behavioral tests for agent_tracking.py module.

Tests heartbeat coordination, agent status tracking, and TTL management.

Copyright 2026 Smart-AI-Memory
Licensed under Apache 2.0
"""

import time
from datetime import datetime

from empathy_os.telemetry.agent_tracking import (
    AgentHeartbeat,
    HeartbeatCoordinator,
)


class TestAgentHeartbeat:
    """Test AgentHeartbeat dataclass."""

    def test_creates_heartbeat(self):
        """Test creating an agent heartbeat."""
        heartbeat = AgentHeartbeat(
            agent_id="test-agent-123",
            status="running",
            progress=0.5,
            current_task="Processing files",
            last_beat=datetime.now(),
            metadata={"workflow": "code-review"},
        )

        assert heartbeat.agent_id == "test-agent-123"
        assert heartbeat.status == "running"
        assert heartbeat.progress == 0.5
        assert heartbeat.current_task == "Processing files"

    def test_converts_to_dict(self):
        """Test converting heartbeat to dictionary."""
        now = datetime.now()
        heartbeat = AgentHeartbeat(
            agent_id="test-agent",
            status="running",
            progress=0.75,
            current_task="Final step",
            last_beat=now,
            metadata={"run_id": "xyz"},
        )

        data = heartbeat.to_dict()

        assert data["agent_id"] == "test-agent"
        assert data["status"] == "running"
        assert data["progress"] == 0.75
        assert isinstance(data["last_beat"], str)  # ISO format

    def test_creates_from_dict(self):
        """Test creating heartbeat from dictionary."""
        data = {
            "agent_id": "test-agent",
            "status": "completed",
            "progress": 1.0,
            "current_task": "Done",
            "last_beat": "2026-01-29T12:00:00",
            "metadata": {"result": "success"},
        }

        heartbeat = AgentHeartbeat.from_dict(data)

        assert heartbeat.agent_id == "test-agent"
        assert heartbeat.status == "completed"
        assert isinstance(heartbeat.last_beat, datetime)

    def test_handles_missing_metadata(self):
        """Test handling missing metadata in dict."""
        data = {
            "agent_id": "test-agent",
            "status": "running",
            "progress": 0.5,
            "current_task": "Task",
            "last_beat": datetime.now(),
        }

        heartbeat = AgentHeartbeat.from_dict(data)

        assert heartbeat.metadata == {}


class TestHeartbeatCoordinator:
    """Test HeartbeatCoordinator functionality."""

    def test_starts_heartbeat(self):
        """Test starting agent heartbeat tracking."""
        coordinator = HeartbeatCoordinator()

        coordinator.start_heartbeat(
            agent_id="agent-1",
            metadata={"workflow": "test"},
        )

        # Agent should be in active list
        active = coordinator.get_active_agents()
        assert len(active) == 1
        assert active[0].agent_id == "agent-1"
        assert active[0].status == "starting"

    def test_updates_heartbeat(self):
        """Test updating heartbeat status."""
        coordinator = HeartbeatCoordinator()

        coordinator.start_heartbeat(agent_id="agent-1")
        coordinator.beat(
            agent_id="agent-1",
            status="running",
            progress=0.5,
            current_task="Processing",
        )

        active = coordinator.get_active_agents()
        assert active[0].status == "running"
        assert active[0].progress == 0.5
        assert active[0].current_task == "Processing"

    def test_stops_heartbeat(self):
        """Test stopping heartbeat tracking."""
        coordinator = HeartbeatCoordinator()

        coordinator.start_heartbeat(agent_id="agent-1")
        coordinator.stop_heartbeat(
            agent_id="agent-1",
            final_status="completed",
        )

        # Agent should be removed from active list
        active = coordinator.get_active_agents()
        assert len(active) == 0

    def test_tracks_multiple_agents(self):
        """Test tracking multiple agents simultaneously."""
        coordinator = HeartbeatCoordinator()

        coordinator.start_heartbeat(agent_id="agent-1", metadata={"type": "analyzer"})
        coordinator.start_heartbeat(agent_id="agent-2", metadata={"type": "reviewer"})

        active = coordinator.get_active_agents()
        assert len(active) == 2

        agent_ids = {agent.agent_id for agent in active}
        assert agent_ids == {"agent-1", "agent-2"}

    def test_detects_stale_heartbeats(self):
        """Test detection of stale heartbeats based on TTL."""
        coordinator = HeartbeatCoordinator()
        coordinator.HEARTBEAT_TTL = 1  # 1 second for testing

        coordinator.start_heartbeat(agent_id="agent-1")

        # Immediately should be active
        active = coordinator.get_active_agents()
        assert len(active) == 1

        # Wait for TTL to expire
        time.sleep(2)

        # Should now detect as stale
        stale = coordinator.get_stale_agents()
        assert len(stale) == 1
        assert stale[0].agent_id == "agent-1"

    def test_gets_agent_status(self):
        """Test retrieving individual agent status."""
        coordinator = HeartbeatCoordinator()

        coordinator.start_heartbeat(agent_id="agent-1", metadata={"run_id": "123"})
        coordinator.beat(
            agent_id="agent-1",
            status="running",
            progress=0.7,
            current_task="Final steps",
        )

        status = coordinator.get_agent_status("agent-1")

        assert status is not None
        assert status.agent_id == "agent-1"
        assert status.status == "running"
        assert status.progress == 0.7

    def test_returns_none_for_missing_agent(self):
        """Test that None is returned for non-existent agent."""
        coordinator = HeartbeatCoordinator()

        status = coordinator.get_agent_status("nonexistent")

        assert status is None

    def test_cleans_up_completed_agents(self):
        """Test cleanup of completed agents."""
        coordinator = HeartbeatCoordinator()

        coordinator.start_heartbeat(agent_id="agent-1")
        coordinator.beat(agent_id="agent-1", status="completed", progress=1.0)

        # Cleanup completed agents
        coordinator.cleanup_completed()

        active = coordinator.get_active_agents()
        assert len(active) == 0

    def test_preserves_running_agents_during_cleanup(self):
        """Test that running agents are preserved during cleanup."""
        coordinator = HeartbeatCoordinator()

        coordinator.start_heartbeat(agent_id="agent-1")
        coordinator.start_heartbeat(agent_id="agent-2")

        coordinator.beat(agent_id="agent-1", status="completed", progress=1.0)
        coordinator.beat(agent_id="agent-2", status="running", progress=0.5)

        coordinator.cleanup_completed()

        active = coordinator.get_active_agents()
        assert len(active) == 1
        assert active[0].agent_id == "agent-2"


class TestProgressTracking:
    """Test progress tracking functionality."""

    def test_tracks_progress_updates(self):
        """Test tracking progress from 0 to 100%."""
        coordinator = HeartbeatCoordinator()

        coordinator.start_heartbeat(agent_id="agent-1")

        # Update progress incrementally
        for i in range(11):
            progress = i / 10.0
            coordinator.beat(
                agent_id="agent-1",
                status="running",
                progress=progress,
                current_task=f"Step {i}",
            )

            status = coordinator.get_agent_status("agent-1")
            assert status.progress == progress

    def test_validates_progress_range(self):
        """Test that progress is kept within 0-1 range."""
        coordinator = HeartbeatCoordinator()

        coordinator.start_heartbeat(agent_id="agent-1")

        # Try to set progress > 1.0
        coordinator.beat(agent_id="agent-1", status="running", progress=1.5)

        status = coordinator.get_agent_status("agent-1")
        # Implementation should clamp to valid range
        assert 0.0 <= status.progress <= 1.0


class TestMetadataHandling:
    """Test metadata storage and retrieval."""

    def test_stores_metadata(self):
        """Test that metadata is stored with heartbeat."""
        coordinator = HeartbeatCoordinator()

        coordinator.start_heartbeat(
            agent_id="agent-1",
            metadata={
                "workflow": "code-review",
                "run_id": "abc123",
                "user": "test-user",
            },
        )

        status = coordinator.get_agent_status("agent-1")
        assert status.metadata["workflow"] == "code-review"
        assert status.metadata["run_id"] == "abc123"

    def test_updates_metadata(self):
        """Test updating metadata during execution."""
        coordinator = HeartbeatCoordinator()

        coordinator.start_heartbeat(
            agent_id="agent-1",
            metadata={"phase": "initialization"},
        )

        coordinator.beat(
            agent_id="agent-1",
            status="running",
            progress=0.5,
            metadata={"phase": "analysis", "files_processed": 10},
        )

        status = coordinator.get_agent_status("agent-1")
        assert status.metadata.get("phase") == "analysis"
        assert status.metadata.get("files_processed") == 10


class TestStatusTransitions:
    """Test agent status transitions."""

    def test_starting_to_running_transition(self):
        """Test transition from starting to running."""
        coordinator = HeartbeatCoordinator()

        coordinator.start_heartbeat(agent_id="agent-1")
        assert coordinator.get_agent_status("agent-1").status == "starting"

        coordinator.beat(agent_id="agent-1", status="running", progress=0.1)
        assert coordinator.get_agent_status("agent-1").status == "running"

    def test_running_to_completed_transition(self):
        """Test transition from running to completed."""
        coordinator = HeartbeatCoordinator()

        coordinator.start_heartbeat(agent_id="agent-1")
        coordinator.beat(agent_id="agent-1", status="running", progress=0.5)
        coordinator.beat(agent_id="agent-1", status="completed", progress=1.0)

        status = coordinator.get_agent_status("agent-1")
        assert status.status == "completed"
        assert status.progress == 1.0

    def test_running_to_failed_transition(self):
        """Test transition from running to failed."""
        coordinator = HeartbeatCoordinator()

        coordinator.start_heartbeat(agent_id="agent-1")
        coordinator.beat(agent_id="agent-1", status="running", progress=0.3)
        coordinator.beat(
            agent_id="agent-1",
            status="failed",
            progress=0.3,
            metadata={"error": "Connection timeout"},
        )

        status = coordinator.get_agent_status("agent-1")
        assert status.status == "failed"
        assert status.metadata.get("error") == "Connection timeout"


class TestTimestampHandling:
    """Test last beat timestamp handling."""

    def test_updates_last_beat_timestamp(self):
        """Test that last_beat is updated on each beat."""
        coordinator = HeartbeatCoordinator()

        coordinator.start_heartbeat(agent_id="agent-1")
        first_beat = coordinator.get_agent_status("agent-1").last_beat

        time.sleep(0.1)

        coordinator.beat(agent_id="agent-1", status="running", progress=0.5)
        second_beat = coordinator.get_agent_status("agent-1").last_beat

        assert second_beat > first_beat

    def test_calculates_time_since_last_beat(self):
        """Test calculating time elapsed since last beat."""
        coordinator = HeartbeatCoordinator()

        coordinator.start_heartbeat(agent_id="agent-1")
        time.sleep(0.5)

        status = coordinator.get_agent_status("agent-1")
        elapsed = (datetime.now() - status.last_beat).total_seconds()

        assert elapsed >= 0.4  # Allow some tolerance


class TestErrorHandling:
    """Test error handling in edge cases."""

    def test_handles_beat_for_nonexistent_agent(self):
        """Test handling beat update for non-existent agent."""
        coordinator = HeartbeatCoordinator()

        # Should not crash when updating non-existent agent
        coordinator.beat(
            agent_id="nonexistent",
            status="running",
            progress=0.5,
        )

    def test_handles_stop_for_nonexistent_agent(self):
        """Test handling stop for non-existent agent."""
        coordinator = HeartbeatCoordinator()

        # Should not crash when stopping non-existent agent
        coordinator.stop_heartbeat(
            agent_id="nonexistent",
            final_status="completed",
        )

    def test_handles_duplicate_start(self):
        """Test handling duplicate start requests."""
        coordinator = HeartbeatCoordinator()

        coordinator.start_heartbeat(agent_id="agent-1", metadata={"attempt": 1})
        coordinator.start_heartbeat(agent_id="agent-1", metadata={"attempt": 2})

        # Should only have one instance
        active = coordinator.get_active_agents()
        assert len(active) == 1


class TestConcurrentAccess:
    """Test handling of concurrent access patterns."""

    def test_multiple_agents_dont_interfere(self):
        """Test that multiple agents don't interfere with each other."""
        coordinator = HeartbeatCoordinator()

        # Start multiple agents
        for i in range(5):
            coordinator.start_heartbeat(
                agent_id=f"agent-{i}",
                metadata={"index": i},
            )

        # Update each independently
        for i in range(5):
            coordinator.beat(
                agent_id=f"agent-{i}",
                status="running",
                progress=i / 10.0,
                current_task=f"Task {i}",
            )

        # Verify each has correct state
        for i in range(5):
            status = coordinator.get_agent_status(f"agent-{i}")
            assert status.progress == i / 10.0
            assert status.current_task == f"Task {i}"
