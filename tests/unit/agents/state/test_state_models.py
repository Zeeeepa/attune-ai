"""Tests for agent state data models.

Tests serialization round-trips, computed properties, and edge cases
for AgentExecutionRecord and AgentStateRecord.

Copyright 2026 Smart-AI-Memory
Licensed under Apache 2.0
"""

from attune.agents.state.models import AgentExecutionRecord, AgentStateRecord


class TestAgentExecutionRecord:
    """Tests for AgentExecutionRecord dataclass."""

    def test_default_values(self) -> None:
        """Test that defaults are sensible."""
        record = AgentExecutionRecord(
            execution_id="exec-001",
            agent_id="agent-001",
            role="Security Auditor",
        )
        assert record.status == "running"
        assert record.tier_used == "cheap"
        assert record.score == 0.0
        assert record.cost == 0.0
        assert record.completed_at is None
        assert record.error is None
        assert record.started_at  # Auto-populated

    def test_to_dict_round_trip(self) -> None:
        """Test serialization and deserialization produce identical records."""
        original = AgentExecutionRecord(
            execution_id="exec-002",
            agent_id="agent-002",
            role="Test Coverage",
            started_at="2026-02-10T12:00:00",
            completed_at="2026-02-10T12:00:05",
            status="completed",
            tier_used="capable",
            input_summary="Analyzing src/",
            findings={"coverage": 85.0, "files": ["a.py", "b.py"]},
            score=85.0,
            confidence=0.9,
            cost=0.03,
            execution_time_ms=5000.0,
            error=None,
        )
        data = original.to_dict()
        restored = AgentExecutionRecord.from_dict(data)

        assert restored.execution_id == original.execution_id
        assert restored.agent_id == original.agent_id
        assert restored.role == original.role
        assert restored.status == original.status
        assert restored.tier_used == original.tier_used
        assert restored.findings == original.findings
        assert restored.score == original.score
        assert restored.confidence == original.confidence
        assert restored.cost == original.cost

    def test_from_dict_with_missing_optional_fields(self) -> None:
        """Test deserialization handles missing optional fields gracefully."""
        minimal = {
            "execution_id": "exec-003",
            "agent_id": "agent-003",
            "role": "Code Quality",
        }
        record = AgentExecutionRecord.from_dict(minimal)
        assert record.status == "running"
        assert record.findings == {}
        assert record.error is None

    def test_to_dict_includes_error(self) -> None:
        """Test that error field is serialized."""
        record = AgentExecutionRecord(
            execution_id="exec-err",
            agent_id="agent-err",
            role="Failing Agent",
            status="failed",
            error="Connection timeout",
        )
        data = record.to_dict()
        assert data["error"] == "Connection timeout"
        assert data["status"] == "failed"


class TestAgentStateRecord:
    """Tests for AgentStateRecord dataclass."""

    def test_success_rate_with_no_executions(self) -> None:
        """Test success_rate returns 0.0 when no executions recorded."""
        record = AgentStateRecord(agent_id="agent-01", role="Auditor")
        assert record.success_rate == 0.0

    def test_success_rate_calculation(self) -> None:
        """Test success_rate computes correctly."""
        record = AgentStateRecord(
            agent_id="agent-02",
            role="Auditor",
            total_executions=10,
            successful_executions=7,
            failed_executions=3,
        )
        assert record.success_rate == 0.7

    def test_avg_cost_with_no_executions(self) -> None:
        """Test avg_cost returns 0.0 when no executions recorded."""
        record = AgentStateRecord(agent_id="agent-03", role="Auditor")
        assert record.avg_cost == 0.0

    def test_avg_cost_calculation(self) -> None:
        """Test avg_cost computes correctly."""
        record = AgentStateRecord(
            agent_id="agent-04",
            role="Auditor",
            total_executions=4,
            total_cost=0.12,
        )
        assert abs(record.avg_cost - 0.03) < 1e-9

    def test_avg_score_from_history(self) -> None:
        """Test avg_score computes from completed executions only."""
        record = AgentStateRecord(
            agent_id="agent-05",
            role="Auditor",
            execution_history=[
                AgentExecutionRecord(
                    execution_id="e1",
                    agent_id="agent-05",
                    role="Auditor",
                    status="completed",
                    score=80.0,
                ),
                AgentExecutionRecord(
                    execution_id="e2",
                    agent_id="agent-05",
                    role="Auditor",
                    status="failed",
                    score=20.0,
                ),
                AgentExecutionRecord(
                    execution_id="e3",
                    agent_id="agent-05",
                    role="Auditor",
                    status="completed",
                    score=90.0,
                ),
            ],
        )
        # Only completed: (80 + 90) / 2 = 85
        assert record.avg_score == 85.0

    def test_avg_score_with_no_completed(self) -> None:
        """Test avg_score returns 0.0 when no completed executions."""
        record = AgentStateRecord(
            agent_id="agent-06",
            role="Auditor",
            execution_history=[
                AgentExecutionRecord(
                    execution_id="e1",
                    agent_id="agent-06",
                    role="Auditor",
                    status="running",
                ),
            ],
        )
        assert record.avg_score == 0.0

    def test_to_dict_round_trip(self) -> None:
        """Test full serialization round-trip with history."""
        original = AgentStateRecord(
            agent_id="agent-07",
            role="Security Auditor",
            created_at="2026-02-10T10:00:00",
            last_active="2026-02-10T12:00:00",
            total_executions=3,
            successful_executions=2,
            failed_executions=1,
            total_cost=0.09,
            accumulated_metrics={"avg_response_ms": 1500.0},
            execution_history=[
                AgentExecutionRecord(
                    execution_id="e1",
                    agent_id="agent-07",
                    role="Security Auditor",
                    status="completed",
                    score=95.0,
                ),
            ],
            last_checkpoint={"step": 3, "partial_results": ["a", "b"]},
        )
        data = original.to_dict()
        restored = AgentStateRecord.from_dict(data)

        assert restored.agent_id == original.agent_id
        assert restored.role == original.role
        assert restored.total_executions == original.total_executions
        assert restored.success_rate == original.success_rate
        assert restored.total_cost == original.total_cost
        assert restored.accumulated_metrics == original.accumulated_metrics
        assert len(restored.execution_history) == 1
        assert restored.execution_history[0].score == 95.0
        assert restored.last_checkpoint == {"step": 3, "partial_results": ["a", "b"]}

    def test_from_dict_with_empty_history(self) -> None:
        """Test deserialization with empty history."""
        data = {"agent_id": "agent-08", "role": "Tester"}
        record = AgentStateRecord.from_dict(data)
        assert record.execution_history == []
        assert record.total_executions == 0
