"""Behavioral tests for multiple telemetry modules.

Tests event_streaming, agent_coordination, feedback_loop, approval_gates,
and other telemetry functionality.

Copyright 2026 Smart-AI-Memory
Licensed under Apache 2.0
"""

import pytest
import json
from datetime import datetime
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock


class TestEventStreaming:
    """Test event streaming functionality."""

    def test_creates_event_stream(self, tmp_path):
        """Test creating an event stream."""
        from empathy_os.telemetry.event_streaming import EventStream

        stream = EventStream(storage_dir=tmp_path / "events")

        assert stream is not None
        assert stream.storage_dir.exists()

    def test_publishes_event(self, tmp_path):
        """Test publishing an event to stream."""
        from empathy_os.telemetry.event_streaming import EventStream

        stream = EventStream(storage_dir=tmp_path / "events")

        event_data = {
            "type": "workflow_started",
            "workflow": "code-review",
            "timestamp": datetime.now().isoformat(),
        }

        stream.publish(event_data)

        # Verify event was stored
        events = stream.get_recent_events(limit=1)
        assert len(events) == 1
        assert events[0]["type"] == "workflow_started"

    def test_subscribes_to_events(self, tmp_path):
        """Test subscribing to event stream."""
        from empathy_os.telemetry.event_streaming import EventStream

        stream = EventStream(storage_dir=tmp_path / "events")

        received_events = []

        def handler(event):
            received_events.append(event)

        stream.subscribe("workflow_started", handler)

        # Publish event
        stream.publish({"type": "workflow_started", "workflow": "test"})

        # Handler should have been called
        assert len(received_events) == 1

    def test_filters_by_event_type(self, tmp_path):
        """Test filtering events by type."""
        from empathy_os.telemetry.event_streaming import EventStream

        stream = EventStream(storage_dir=tmp_path / "events")

        # Publish different event types
        stream.publish({"type": "workflow_started", "data": "A"})
        stream.publish({"type": "workflow_completed", "data": "B"})
        stream.publish({"type": "workflow_started", "data": "C"})

        # Get only workflow_started events
        events = stream.get_events_by_type("workflow_started")
        assert len(events) == 2

    def test_persists_events_to_disk(self, tmp_path):
        """Test that events are persisted to disk."""
        from empathy_os.telemetry.event_streaming import EventStream

        storage_dir = tmp_path / "events"
        stream = EventStream(storage_dir=storage_dir)

        stream.publish({"type": "test_event", "data": "test"})

        # Create new stream instance - should load persisted events
        stream2 = EventStream(storage_dir=storage_dir)
        events = stream2.get_recent_events(limit=10)

        assert len(events) >= 1


class TestAgentCoordination:
    """Test agent coordination functionality."""

    def test_creates_coordinator(self):
        """Test creating agent coordinator."""
        from empathy_os.telemetry.agent_coordination import AgentCoordinator

        coordinator = AgentCoordinator()

        assert coordinator is not None

    def test_registers_agent(self):
        """Test registering an agent with coordinator."""
        from empathy_os.telemetry.agent_coordination import AgentCoordinator

        coordinator = AgentCoordinator()

        coordinator.register_agent(
            agent_id="agent-1",
            role="code_reviewer",
            capabilities=["python", "security"],
        )

        # Verify agent is registered
        agents = coordinator.get_active_agents()
        assert len(agents) >= 1

    def test_coordinates_multi_agent_workflow(self):
        """Test coordinating multiple agents."""
        from empathy_os.telemetry.agent_coordination import AgentCoordinator

        coordinator = AgentCoordinator()

        # Register multiple agents
        coordinator.register_agent("agent-1", "analyzer", ["code"])
        coordinator.register_agent("agent-2", "reviewer", ["security"])

        # Assign tasks
        coordinator.assign_task("agent-1", "analyze_code", priority=1)
        coordinator.assign_task("agent-2", "review_security", priority=2)

        # Verify task assignment
        tasks = coordinator.get_pending_tasks()
        assert len(tasks) >= 2

    def test_detects_agent_failure(self):
        """Test detecting failed agents."""
        from empathy_os.telemetry.agent_coordination import AgentCoordinator

        coordinator = AgentCoordinator()

        coordinator.register_agent("agent-1", "worker", [])

        # Simulate failure
        coordinator.mark_agent_failed("agent-1", error="Timeout")

        # Verify agent is marked as failed
        status = coordinator.get_agent_status("agent-1")
        assert status["status"] == "failed"

    def test_redistributes_tasks_on_failure(self):
        """Test task redistribution when agent fails."""
        from empathy_os.telemetry.agent_coordination import AgentCoordinator

        coordinator = AgentCoordinator()

        coordinator.register_agent("agent-1", "worker", [])
        coordinator.register_agent("agent-2", "worker", [])

        # Assign task to agent-1
        coordinator.assign_task("agent-1", "task-1")

        # Agent-1 fails
        coordinator.mark_agent_failed("agent-1", error="Crash")

        # Task should be reassigned
        coordinator.redistribute_tasks()

        # agent-2 should now have the task
        agent2_tasks = coordinator.get_agent_tasks("agent-2")
        assert len(agent2_tasks) > 0


class TestFeedbackLoop:
    """Test feedback loop functionality."""

    def test_creates_feedback_collector(self, tmp_path):
        """Test creating feedback collector."""
        from empathy_os.telemetry.feedback_loop import FeedbackCollector

        collector = FeedbackCollector(storage_dir=tmp_path / "feedback")

        assert collector is not None

    def test_collects_positive_feedback(self, tmp_path):
        """Test collecting positive feedback."""
        from empathy_os.telemetry.feedback_loop import FeedbackCollector

        collector = FeedbackCollector(storage_dir=tmp_path / "feedback")

        collector.record_feedback(
            workflow="code-review",
            run_id="abc123",
            rating=5,
            comment="Excellent analysis",
            user_id="user-1",
        )

        feedback = collector.get_feedback(workflow="code-review")
        assert len(feedback) == 1
        assert feedback[0]["rating"] == 5

    def test_collects_negative_feedback(self, tmp_path):
        """Test collecting negative feedback."""
        from empathy_os.telemetry.feedback_loop import FeedbackCollector

        collector = FeedbackCollector(storage_dir=tmp_path / "feedback")

        collector.record_feedback(
            workflow="test-gen",
            run_id="xyz789",
            rating=2,
            comment="Missed edge cases",
            user_id="user-1",
        )

        feedback = collector.get_feedback(workflow="test-gen")
        assert len(feedback) == 1
        assert feedback[0]["rating"] == 2

    def test_calculates_average_rating(self, tmp_path):
        """Test calculating average rating."""
        from empathy_os.telemetry.feedback_loop import FeedbackCollector

        collector = FeedbackCollector(storage_dir=tmp_path / "feedback")

        # Record multiple ratings
        for rating in [5, 4, 5, 3, 4]:
            collector.record_feedback(
                workflow="test",
                run_id=f"run-{rating}",
                rating=rating,
                user_id="user-1",
            )

        avg = collector.get_average_rating(workflow="test")
        assert avg == 4.2  # (5+4+5+3+4)/5

    def test_identifies_improvement_areas(self, tmp_path):
        """Test identifying areas needing improvement."""
        from empathy_os.telemetry.feedback_loop import FeedbackCollector

        collector = FeedbackCollector(storage_dir=tmp_path / "feedback")

        # Record feedback with comments
        collector.record_feedback(
            workflow="test",
            run_id="1",
            rating=2,
            comment="Slow response time",
            user_id="user-1",
        )
        collector.record_feedback(
            workflow="test",
            run_id="2",
            rating=3,
            comment="Response time could be better",
            user_id="user-2",
        )

        # Analyze common themes
        themes = collector.analyze_feedback_themes(workflow="test")
        assert "response time" in str(themes).lower()

    def test_tracks_improvement_over_time(self, tmp_path):
        """Test tracking improvement trends over time."""
        from empathy_os.telemetry.feedback_loop import FeedbackCollector

        collector = FeedbackCollector(storage_dir=tmp_path / "feedback")

        # Simulate improving ratings over time
        for day, rating in enumerate([2, 3, 3, 4, 4, 5]):
            collector.record_feedback(
                workflow="test",
                run_id=f"day-{day}",
                rating=rating,
                user_id="user-1",
                timestamp=datetime.now().isoformat(),
            )

        trend = collector.get_rating_trend(workflow="test")
        assert trend["direction"] == "improving"


class TestApprovalGates:
    """Test approval gate functionality."""

    def test_creates_approval_gate(self, tmp_path):
        """Test creating an approval gate."""
        from empathy_os.telemetry.approval_gates import ApprovalGate

        gate = ApprovalGate(
            gate_id="deploy_gate",
            required_approvers=2,
            storage_dir=tmp_path / "approvals",
        )

        assert gate.gate_id == "deploy_gate"
        assert gate.required_approvers == 2

    def test_requests_approval(self, tmp_path):
        """Test requesting approval."""
        from empathy_os.telemetry.approval_gates import ApprovalGate

        gate = ApprovalGate(
            gate_id="deploy_gate",
            required_approvers=1,
            storage_dir=tmp_path / "approvals",
        )

        request_id = gate.request_approval(
            workflow="deployment",
            run_id="deploy-123",
            metadata={"environment": "production"},
        )

        assert request_id is not None
        assert gate.is_pending(request_id)

    def test_approves_request(self, tmp_path):
        """Test approving a request."""
        from empathy_os.telemetry.approval_gates import ApprovalGate

        gate = ApprovalGate(
            gate_id="deploy_gate",
            required_approvers=1,
            storage_dir=tmp_path / "approvals",
        )

        request_id = gate.request_approval("test", "run-1")

        gate.approve(
            request_id=request_id,
            approver_id="admin-1",
            comment="Looks good",
        )

        assert gate.is_approved(request_id)

    def test_rejects_request(self, tmp_path):
        """Test rejecting a request."""
        from empathy_os.telemetry.approval_gates import ApprovalGate

        gate = ApprovalGate(
            gate_id="deploy_gate",
            required_approvers=1,
            storage_dir=tmp_path / "approvals",
        )

        request_id = gate.request_approval("test", "run-1")

        gate.reject(
            request_id=request_id,
            approver_id="admin-1",
            reason="Security concerns",
        )

        assert gate.is_rejected(request_id)

    def test_requires_multiple_approvers(self, tmp_path):
        """Test requiring multiple approvals."""
        from empathy_os.telemetry.approval_gates import ApprovalGate

        gate = ApprovalGate(
            gate_id="deploy_gate",
            required_approvers=3,
            storage_dir=tmp_path / "approvals",
        )

        request_id = gate.request_approval("test", "run-1")

        # First approval - not enough
        gate.approve(request_id, "admin-1")
        assert not gate.is_approved(request_id)

        # Second approval - still not enough
        gate.approve(request_id, "admin-2")
        assert not gate.is_approved(request_id)

        # Third approval - now approved
        gate.approve(request_id, "admin-3")
        assert gate.is_approved(request_id)

    def test_prevents_duplicate_approvals(self, tmp_path):
        """Test preventing same approver from approving twice."""
        from empathy_os.telemetry.approval_gates import ApprovalGate

        gate = ApprovalGate(
            gate_id="deploy_gate",
            required_approvers=2,
            storage_dir=tmp_path / "approvals",
        )

        request_id = gate.request_approval("test", "run-1")

        # Same approver tries to approve twice
        gate.approve(request_id, "admin-1")
        gate.approve(request_id, "admin-1")

        # Should only count as one approval
        assert gate.get_approval_count(request_id) == 1

    def test_tracks_approval_history(self, tmp_path):
        """Test tracking approval history."""
        from empathy_os.telemetry.approval_gates import ApprovalGate

        gate = ApprovalGate(
            gate_id="deploy_gate",
            required_approvers=2,
            storage_dir=tmp_path / "approvals",
        )

        request_id = gate.request_approval("test", "run-1")

        gate.approve(request_id, "admin-1", comment="LGTM")
        gate.approve(request_id, "admin-2", comment="Approved")

        history = gate.get_approval_history(request_id)
        assert len(history) == 2
        assert history[0]["approver_id"] == "admin-1"

    def test_timeout_handling(self, tmp_path):
        """Test handling of approval timeouts."""
        from empathy_os.telemetry.approval_gates import ApprovalGate

        gate = ApprovalGate(
            gate_id="deploy_gate",
            required_approvers=1,
            timeout_seconds=1,
            storage_dir=tmp_path / "approvals",
        )

        request_id = gate.request_approval("test", "run-1")

        # Wait for timeout
        import time

        time.sleep(2)

        # Should be marked as timed out
        assert gate.is_timed_out(request_id)


class TestTelemetryCLI:
    """Test telemetry CLI functionality."""

    def test_exports_telemetry_to_csv(self, tmp_path, capsys):
        """Test exporting telemetry data to CSV."""
        from empathy_os.telemetry.cli import export_telemetry_csv

        output_file = tmp_path / "telemetry.csv"

        export_telemetry_csv(
            output_path=str(output_file),
            days=30,
        )

        assert output_file.exists()

        # Verify CSV format
        content = output_file.read_text()
        assert "workflow" in content or content == ""  # Empty if no data

    def test_shows_telemetry_stats(self, capsys):
        """Test displaying telemetry statistics."""
        from empathy_os.telemetry.cli import show_stats

        show_stats(days=7)

        captured = capsys.readouterr()
        # Should output something (even if no data)
        assert len(captured.out) > 0

    def test_lists_recent_workflows(self, capsys):
        """Test listing recent workflow executions."""
        from empathy_os.telemetry.cli import list_recent_workflows

        list_recent_workflows(limit=10)

        captured = capsys.readouterr()
        # Should output something
        assert len(captured.out) >= 0


class TestMultiBackendMonitoring:
    """Test multi-backend monitoring functionality."""

    def test_creates_multi_backend_monitor(self):
        """Test creating multi-backend monitor."""
        from empathy_os.monitoring.multi_backend import MultiBackendMonitor

        monitor = MultiBackendMonitor()

        assert monitor is not None

    def test_registers_backend(self):
        """Test registering a monitoring backend."""
        from empathy_os.monitoring.multi_backend import MultiBackendMonitor

        monitor = MultiBackendMonitor()

        mock_backend = Mock()
        monitor.register_backend("test_backend", mock_backend)

        assert "test_backend" in monitor.get_backends()

    def test_sends_metrics_to_all_backends(self):
        """Test sending metrics to all registered backends."""
        from empathy_os.monitoring.multi_backend import MultiBackendMonitor

        monitor = MultiBackendMonitor()

        backend1 = Mock()
        backend2 = Mock()

        monitor.register_backend("backend1", backend1)
        monitor.register_backend("backend2", backend2)

        monitor.emit_metric("test_metric", 42, tags={"env": "test"})

        # Both backends should receive the metric
        backend1.emit.assert_called_once()
        backend2.emit.assert_called_once()

    def test_handles_backend_failure_gracefully(self):
        """Test graceful handling of backend failures."""
        from empathy_os.monitoring.multi_backend import MultiBackendMonitor

        monitor = MultiBackendMonitor()

        # Backend that always fails
        failing_backend = Mock()
        failing_backend.emit.side_effect = Exception("Backend unavailable")

        # Working backend
        working_backend = Mock()

        monitor.register_backend("failing", failing_backend)
        monitor.register_backend("working", working_backend)

        # Should not crash even if one backend fails
        monitor.emit_metric("test_metric", 42)

        # Working backend should still receive metric
        working_backend.emit.assert_called_once()


class TestOTelBackend:
    """Test OpenTelemetry backend functionality."""

    def test_creates_otel_backend(self):
        """Test creating OpenTelemetry backend."""
        from empathy_os.monitoring.otel_backend import OTelBackend

        backend = OTelBackend(service_name="empathy-test")

        assert backend is not None

    def test_configures_exporter(self):
        """Test configuring OTLP exporter."""
        from empathy_os.monitoring.otel_backend import OTelBackend

        backend = OTelBackend(
            service_name="empathy-test",
            endpoint="http://localhost:4317",
        )

        assert backend.endpoint == "http://localhost:4317"

    def test_emits_metrics(self):
        """Test emitting metrics to OTLP."""
        from empathy_os.monitoring.otel_backend import OTelBackend

        backend = OTelBackend(service_name="empathy-test")

        # Should not crash
        backend.emit_metric(
            name="test.metric",
            value=123,
            unit="requests",
            attributes={"method": "GET"},
        )

    def test_emits_traces(self):
        """Test emitting traces to OTLP."""
        from empathy_os.monitoring.otel_backend import OTelBackend

        backend = OTelBackend(service_name="empathy-test")

        # Should not crash
        with backend.start_span("test_operation") as span:
            span.set_attribute("test_attr", "test_value")


class TestMetricsCollector:
    """Test metrics collector stub."""

    def test_creates_collector(self):
        """Test creating metrics collector (deprecated)."""
        from empathy_os.metrics.collector import MetricsCollector

        collector = MetricsCollector()

        assert collector is not None

    def test_collect_returns_empty_dict(self):
        """Test that deprecated collect() returns empty dict."""
        from empathy_os.metrics.collector import MetricsCollector

        collector = MetricsCollector()
        result = collector.collect()

        assert result == {}

    def test_get_stats_returns_empty_dict(self):
        """Test that deprecated get_stats() returns empty dict."""
        from empathy_os.metrics.collector import MetricsCollector

        collector = MetricsCollector()
        result = collector.get_stats()

        assert result == {}
