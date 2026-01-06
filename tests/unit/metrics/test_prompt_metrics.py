"""Unit tests for prompt metrics tracking

Tests the PromptMetrics dataclass and MetricsTracker for performance monitoring.

Copyright 2025 Smart-AI-Memory
Licensed under Fair Source License 0.9
"""

import json
import tempfile
from datetime import datetime, timedelta
from pathlib import Path

import pytest

from empathy_os.metrics.prompt_metrics import MetricsTracker, PromptMetrics


@pytest.mark.unit
class TestPromptMetricsDataclass:
    """Test PromptMetrics dataclass."""

    def test_initialization(self):
        """Test creating a PromptMetrics instance."""
        metric = PromptMetrics(
            timestamp="2026-01-05T10:00:00Z",
            workflow="code_review",
            agent_role="Code Reviewer",
            task_description="Review authentication module",
            model="gpt-4",
            prompt_tokens=1000,
            completion_tokens=500,
            total_tokens=1500,
            latency_ms=2500.5,
            retry_count=0,
            parsing_success=True,
            validation_success=True,
            error_message=None,
            xml_structure_used=True,
        )

        assert metric.timestamp == "2026-01-05T10:00:00Z"
        assert metric.workflow == "code_review"
        assert metric.agent_role == "Code Reviewer"
        assert metric.task_description == "Review authentication module"
        assert metric.model == "gpt-4"
        assert metric.prompt_tokens == 1000
        assert metric.completion_tokens == 500
        assert metric.total_tokens == 1500
        assert metric.latency_ms == 2500.5
        assert metric.retry_count == 0
        assert metric.parsing_success is True
        assert metric.validation_success is True
        assert metric.error_message is None
        assert metric.xml_structure_used is True

    def test_to_dict(self):
        """Test converting PromptMetrics to dictionary."""
        metric = PromptMetrics(
            timestamp="2026-01-05T10:00:00Z",
            workflow="code_review",
            agent_role="Code Reviewer",
            task_description="Test task",
            model="gpt-4",
            prompt_tokens=100,
            completion_tokens=50,
            total_tokens=150,
            latency_ms=1000.0,
            retry_count=1,
            parsing_success=True,
            validation_success=None,
            error_message=None,
            xml_structure_used=False,
        )

        data = metric.to_dict()

        assert isinstance(data, dict)
        assert data["timestamp"] == "2026-01-05T10:00:00Z"
        assert data["workflow"] == "code_review"
        assert data["prompt_tokens"] == 100
        assert data["completion_tokens"] == 50
        assert data["validation_success"] is None

    def test_from_dict(self):
        """Test creating PromptMetrics from dictionary."""
        data = {
            "timestamp": "2026-01-05T10:00:00Z",
            "workflow": "bug_predict",
            "agent_role": "Bug Predictor",
            "task_description": "Scan codebase",
            "model": "claude-sonnet-4",
            "prompt_tokens": 2000,
            "completion_tokens": 1000,
            "total_tokens": 3000,
            "latency_ms": 3500.0,
            "retry_count": 2,
            "parsing_success": False,
            "validation_success": False,
            "error_message": "XML parse error",
            "xml_structure_used": True,
        }

        metric = PromptMetrics.from_dict(data)

        assert metric.timestamp == "2026-01-05T10:00:00Z"
        assert metric.workflow == "bug_predict"
        assert metric.error_message == "XML parse error"
        assert metric.retry_count == 2

    def test_roundtrip_serialization(self):
        """Test that to_dict/from_dict roundtrip works."""
        original = PromptMetrics(
            timestamp="2026-01-05T10:00:00Z",
            workflow="test",
            agent_role="Tester",
            task_description="Test",
            model="test-model",
            prompt_tokens=100,
            completion_tokens=50,
            total_tokens=150,
            latency_ms=1000.0,
            retry_count=0,
            parsing_success=True,
            validation_success=True,
            error_message=None,
            xml_structure_used=True,
        )

        data = original.to_dict()
        restored = PromptMetrics.from_dict(data)

        assert original.timestamp == restored.timestamp
        assert original.workflow == restored.workflow
        assert original.total_tokens == restored.total_tokens


@pytest.mark.unit
class TestMetricsTrackerInitialization:
    """Test MetricsTracker initialization."""

    def test_initialization_creates_file(self):
        """Test that initialization creates metrics file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            metrics_file = Path(tmpdir) / "metrics.json"
            tracker = MetricsTracker(str(metrics_file))

            assert metrics_file.exists()
            assert tracker.metrics_file == metrics_file

    def test_initialization_creates_parent_directory(self):
        """Test that initialization creates parent directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            metrics_file = Path(tmpdir) / "subdir" / "metrics.json"
            MetricsTracker(str(metrics_file))

            assert metrics_file.parent.exists()
            assert metrics_file.exists()

    def test_initialization_with_existing_file(self):
        """Test initialization with existing metrics file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            metrics_file = Path(tmpdir) / "metrics.json"
            metrics_file.write_text("existing content\n")

            MetricsTracker(str(metrics_file))

            assert metrics_file.exists()
            assert metrics_file.read_text() == "existing content\n"


@pytest.mark.unit
class TestMetricsTrackerLogging:
    """Test logging metrics to file."""

    def test_log_metric_writes_to_file(self):
        """Test that log_metric writes metric to file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            metrics_file = Path(tmpdir) / "metrics.json"
            tracker = MetricsTracker(str(metrics_file))

            metric = PromptMetrics(
                timestamp="2026-01-05T10:00:00Z",
                workflow="test",
                agent_role="Tester",
                task_description="Test task",
                model="test-model",
                prompt_tokens=100,
                completion_tokens=50,
                total_tokens=150,
                latency_ms=1000.0,
                retry_count=0,
                parsing_success=True,
                validation_success=True,
                error_message=None,
                xml_structure_used=True,
            )

            tracker.log_metric(metric)

            # Verify file contains the metric
            content = metrics_file.read_text()
            assert "test" in content
            assert "test-model" in content

    def test_log_metric_appends_to_file(self):
        """Test that log_metric appends (doesn't overwrite)."""
        with tempfile.TemporaryDirectory() as tmpdir:
            metrics_file = Path(tmpdir) / "metrics.json"
            tracker = MetricsTracker(str(metrics_file))

            metric1 = PromptMetrics(
                timestamp="2026-01-05T10:00:00Z",
                workflow="test1",
                agent_role="Tester",
                task_description="Task 1",
                model="model1",
                prompt_tokens=100,
                completion_tokens=50,
                total_tokens=150,
                latency_ms=1000.0,
                retry_count=0,
                parsing_success=True,
                validation_success=True,
                error_message=None,
                xml_structure_used=True,
            )

            metric2 = PromptMetrics(
                timestamp="2026-01-05T10:01:00Z",
                workflow="test2",
                agent_role="Tester",
                task_description="Task 2",
                model="model2",
                prompt_tokens=200,
                completion_tokens=100,
                total_tokens=300,
                latency_ms=2000.0,
                retry_count=1,
                parsing_success=True,
                validation_success=True,
                error_message=None,
                xml_structure_used=False,
            )

            tracker.log_metric(metric1)
            tracker.log_metric(metric2)

            # Verify both metrics are in file
            content = metrics_file.read_text()
            lines = content.strip().split("\n")
            assert len(lines) == 2
            assert "test1" in lines[0]
            assert "test2" in lines[1]

    def test_log_metric_json_lines_format(self):
        """Test that metrics are logged in JSON Lines format."""
        with tempfile.TemporaryDirectory() as tmpdir:
            metrics_file = Path(tmpdir) / "metrics.json"
            tracker = MetricsTracker(str(metrics_file))

            metric = PromptMetrics(
                timestamp="2026-01-05T10:00:00Z",
                workflow="test",
                agent_role="Tester",
                task_description="Test",
                model="test-model",
                prompt_tokens=100,
                completion_tokens=50,
                total_tokens=150,
                latency_ms=1000.0,
                retry_count=0,
                parsing_success=True,
                validation_success=True,
                error_message=None,
                xml_structure_used=True,
            )

            tracker.log_metric(metric)

            # Verify each line is valid JSON
            content = metrics_file.read_text()
            for line in content.strip().split("\n"):
                data = json.loads(line)
                assert isinstance(data, dict)
                assert "workflow" in data


@pytest.mark.unit
class TestMetricsTrackerRetrieval:
    """Test retrieving metrics from file."""

    def test_get_metrics_empty_file(self):
        """Test get_metrics with empty file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            metrics_file = Path(tmpdir) / "metrics.json"
            tracker = MetricsTracker(str(metrics_file))

            metrics = tracker.get_metrics()

            assert metrics == []

    def test_get_metrics_all(self):
        """Test get_metrics returns all metrics."""
        with tempfile.TemporaryDirectory() as tmpdir:
            metrics_file = Path(tmpdir) / "metrics.json"
            tracker = MetricsTracker(str(metrics_file))

            # Log multiple metrics
            for i in range(3):
                metric = PromptMetrics(
                    timestamp=f"2026-01-05T10:0{i}:00",
                    workflow=f"test{i}",
                    agent_role="Tester",
                    task_description=f"Task {i}",
                    model="test-model",
                    prompt_tokens=100,
                    completion_tokens=50,
                    total_tokens=150,
                    latency_ms=1000.0,
                    retry_count=0,
                    parsing_success=True,
                    validation_success=True,
                    error_message=None,
                    xml_structure_used=True,
                )
                tracker.log_metric(metric)

            metrics = tracker.get_metrics()

            assert len(metrics) == 3
            assert all(isinstance(m, PromptMetrics) for m in metrics)

    def test_get_metrics_filter_by_workflow(self):
        """Test get_metrics with workflow filter."""
        with tempfile.TemporaryDirectory() as tmpdir:
            metrics_file = Path(tmpdir) / "metrics.json"
            tracker = MetricsTracker(str(metrics_file))

            # Log metrics for different workflows
            workflows = ["code_review", "bug_predict", "code_review"]
            for i, workflow in enumerate(workflows):
                metric = PromptMetrics(
                    timestamp=f"2026-01-05T10:0{i}:00",
                    workflow=workflow,
                    agent_role="Tester",
                    task_description=f"Task {i}",
                    model="test-model",
                    prompt_tokens=100,
                    completion_tokens=50,
                    total_tokens=150,
                    latency_ms=1000.0,
                    retry_count=0,
                    parsing_success=True,
                    validation_success=True,
                    error_message=None,
                    xml_structure_used=True,
                )
                tracker.log_metric(metric)

            metrics = tracker.get_metrics(workflow="code_review")

            assert len(metrics) == 2
            assert all(m.workflow == "code_review" for m in metrics)

    def test_get_metrics_filter_by_date_range(self):
        """Test get_metrics with date range filter."""
        with tempfile.TemporaryDirectory() as tmpdir:
            metrics_file = Path(tmpdir) / "metrics.json"
            tracker = MetricsTracker(str(metrics_file))

            # Log metrics at different times
            base_time = datetime(2026, 1, 5, 10, 0, 0)
            for i in range(5):
                timestamp = base_time + timedelta(hours=i)
                metric = PromptMetrics(
                    timestamp=timestamp.isoformat(),
                    workflow="test",
                    agent_role="Tester",
                    task_description=f"Task {i}",
                    model="test-model",
                    prompt_tokens=100,
                    completion_tokens=50,
                    total_tokens=150,
                    latency_ms=1000.0,
                    retry_count=0,
                    parsing_success=True,
                    validation_success=True,
                    error_message=None,
                    xml_structure_used=True,
                )
                tracker.log_metric(metric)

            # Filter for middle 3 hours
            start_date = base_time + timedelta(hours=1)
            end_date = base_time + timedelta(hours=3)
            metrics = tracker.get_metrics(start_date=start_date, end_date=end_date)

            assert len(metrics) == 3


@pytest.mark.unit
class TestMetricsTrackerSummary:
    """Test summary statistics."""

    def test_get_summary_empty(self):
        """Test get_summary with no metrics."""
        with tempfile.TemporaryDirectory() as tmpdir:
            metrics_file = Path(tmpdir) / "metrics.json"
            tracker = MetricsTracker(str(metrics_file))

            summary = tracker.get_summary()

            assert summary["total_prompts"] == 0
            assert summary["avg_tokens"] == 0
            assert summary["avg_latency_ms"] == 0
            assert summary["success_rate"] == 0
            assert summary["retry_rate"] == 0

    def test_get_summary_basic(self):
        """Test get_summary with basic metrics."""
        with tempfile.TemporaryDirectory() as tmpdir:
            metrics_file = Path(tmpdir) / "metrics.json"
            tracker = MetricsTracker(str(metrics_file))

            # Log 3 metrics
            for i in range(3):
                metric = PromptMetrics(
                    timestamp=f"2026-01-05T10:0{i}:00",
                    workflow="test",
                    agent_role="Tester",
                    task_description=f"Task {i}",
                    model="test-model",
                    prompt_tokens=100,
                    completion_tokens=50,
                    total_tokens=150,
                    latency_ms=1000.0,
                    retry_count=0,
                    parsing_success=True,
                    validation_success=True,
                    error_message=None,
                    xml_structure_used=True,
                )
                tracker.log_metric(metric)

            summary = tracker.get_summary()

            assert summary["total_prompts"] == 3
            assert summary["avg_tokens"] == 150.0
            assert summary["avg_latency_ms"] == 1000.0
            assert summary["success_rate"] == 1.0  # All successful
            assert summary["retry_rate"] == 0.0

    def test_get_summary_with_failures(self):
        """Test get_summary with some failures."""
        with tempfile.TemporaryDirectory() as tmpdir:
            metrics_file = Path(tmpdir) / "metrics.json"
            tracker = MetricsTracker(str(metrics_file))

            # 2 successful, 1 failed
            successes = [True, True, False]
            for i, success in enumerate(successes):
                metric = PromptMetrics(
                    timestamp=f"2026-01-05T10:0{i}:00",
                    workflow="test",
                    agent_role="Tester",
                    task_description=f"Task {i}",
                    model="test-model",
                    prompt_tokens=100,
                    completion_tokens=50,
                    total_tokens=150,
                    latency_ms=1000.0,
                    retry_count=0,
                    parsing_success=success,
                    validation_success=None,
                    error_message=None if success else "Error",
                    xml_structure_used=True,
                )
                tracker.log_metric(metric)

            summary = tracker.get_summary()

            assert summary["total_prompts"] == 3
            assert summary["success_rate"] == pytest.approx(2 / 3)

    def test_get_summary_with_retries(self):
        """Test get_summary with retries."""
        with tempfile.TemporaryDirectory() as tmpdir:
            metrics_file = Path(tmpdir) / "metrics.json"
            tracker = MetricsTracker(str(metrics_file))

            # Different retry counts
            retry_counts = [0, 1, 2]
            for i, retry_count in enumerate(retry_counts):
                metric = PromptMetrics(
                    timestamp=f"2026-01-05T10:0{i}:00",
                    workflow="test",
                    agent_role="Tester",
                    task_description=f"Task {i}",
                    model="test-model",
                    prompt_tokens=100,
                    completion_tokens=50,
                    total_tokens=150,
                    latency_ms=1000.0,
                    retry_count=retry_count,
                    parsing_success=True,
                    validation_success=True,
                    error_message=None,
                    xml_structure_used=True,
                )
                tracker.log_metric(metric)

            summary = tracker.get_summary()

            assert summary["retry_rate"] == pytest.approx(1.0)  # (0+1+2)/3

    def test_get_summary_filter_by_workflow(self):
        """Test get_summary with workflow filter."""
        with tempfile.TemporaryDirectory() as tmpdir:
            metrics_file = Path(tmpdir) / "metrics.json"
            tracker = MetricsTracker(str(metrics_file))

            # Log metrics for different workflows
            workflows = ["code_review", "code_review", "bug_predict"]
            for i, workflow in enumerate(workflows):
                metric = PromptMetrics(
                    timestamp=f"2026-01-05T10:0{i}:00",
                    workflow=workflow,
                    agent_role="Tester",
                    task_description=f"Task {i}",
                    model="test-model",
                    prompt_tokens=100 * (i + 1),
                    completion_tokens=50,
                    total_tokens=150 * (i + 1),
                    latency_ms=1000.0,
                    retry_count=0,
                    parsing_success=True,
                    validation_success=True,
                    error_message=None,
                    xml_structure_used=True,
                )
                tracker.log_metric(metric)

            summary = tracker.get_summary(workflow="code_review")

            assert summary["total_prompts"] == 2
            # (150 + 300) / 2 = 225
            assert summary["avg_tokens"] == 225.0
