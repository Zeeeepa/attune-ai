"""Behavioral tests for metrics/prompt_metrics.py module.

Tests prompt performance tracking, metrics aggregation, and analysis.

Copyright 2026 Smart-AI-Memory
Licensed under Apache 2.0
"""

import json
import pytest
from datetime import datetime, timedelta
from pathlib import Path
from empathy_os.metrics.prompt_metrics import (
    PromptMetrics,
    MetricsTracker,
)


class TestPromptMetrics:
    """Test PromptMetrics dataclass."""

    def test_creates_metrics(self):
        """Test creating prompt metrics."""
        metrics = PromptMetrics(
            timestamp=datetime.now().isoformat(),
            workflow="code-review",
            agent_role="Code Reviewer",
            task_description="Review Python code for best practices",
            model="claude-sonnet-4.5",
            prompt_tokens=1000,
            completion_tokens=500,
            total_tokens=1500,
            latency_ms=250.5,
            retry_count=0,
            parsing_success=True,
            validation_success=True,
            error_message=None,
            xml_structure_used=True,
        )

        assert metrics.workflow == "code-review"
        assert metrics.total_tokens == 1500
        assert metrics.parsing_success is True

    def test_converts_to_dict(self):
        """Test converting metrics to dictionary."""
        metrics = PromptMetrics(
            timestamp="2026-01-29T12:00:00",
            workflow="test-workflow",
            agent_role="Tester",
            task_description="Test task",
            model="gpt-4o",
            prompt_tokens=500,
            completion_tokens=250,
            total_tokens=750,
            latency_ms=100.0,
            retry_count=0,
            parsing_success=True,
            validation_success=None,
            error_message=None,
            xml_structure_used=False,
        )

        data = metrics.to_dict()

        assert data["workflow"] == "test-workflow"
        assert data["total_tokens"] == 750
        assert data["xml_structure_used"] is False

    def test_creates_from_dict(self):
        """Test creating metrics from dictionary."""
        data = {
            "timestamp": "2026-01-29T12:00:00",
            "workflow": "test-workflow",
            "agent_role": "Tester",
            "task_description": "Test task",
            "model": "gpt-4o",
            "prompt_tokens": 500,
            "completion_tokens": 250,
            "total_tokens": 750,
            "latency_ms": 100.0,
            "retry_count": 0,
            "parsing_success": True,
            "validation_success": None,
            "error_message": None,
            "xml_structure_used": False,
        }

        metrics = PromptMetrics.from_dict(data)

        assert metrics.workflow == "test-workflow"
        assert metrics.total_tokens == 750


class TestMetricsTracker:
    """Test MetricsTracker functionality."""

    def test_creates_metrics_file(self, tmp_path):
        """Test that metrics file is created."""
        metrics_file = tmp_path / "metrics.json"
        tracker = MetricsTracker(metrics_file=str(metrics_file))

        assert metrics_file.exists()

    def test_creates_parent_directory(self, tmp_path):
        """Test that parent directory is created if missing."""
        metrics_file = tmp_path / "subdir" / "metrics.json"
        tracker = MetricsTracker(metrics_file=str(metrics_file))

        assert metrics_file.exists()
        assert metrics_file.parent.exists()

    def test_logs_metric(self, tmp_path):
        """Test logging a metric."""
        metrics_file = tmp_path / "metrics.json"
        tracker = MetricsTracker(metrics_file=str(metrics_file))

        metric = PromptMetrics(
            timestamp=datetime.now().isoformat(),
            workflow="test-workflow",
            agent_role="Tester",
            task_description="Test task",
            model="gpt-4o",
            prompt_tokens=100,
            completion_tokens=50,
            total_tokens=150,
            latency_ms=50.0,
            retry_count=0,
            parsing_success=True,
            validation_success=True,
            error_message=None,
            xml_structure_used=False,
        )

        tracker.log_metric(metric)

        # Verify file was written
        content = metrics_file.read_text()
        assert "test-workflow" in content

    def test_logs_multiple_metrics(self, tmp_path):
        """Test logging multiple metrics."""
        metrics_file = tmp_path / "metrics.json"
        tracker = MetricsTracker(metrics_file=str(metrics_file))

        for i in range(5):
            metric = PromptMetrics(
                timestamp=datetime.now().isoformat(),
                workflow=f"workflow-{i}",
                agent_role="Tester",
                task_description=f"Task {i}",
                model="gpt-4o",
                prompt_tokens=100 * i,
                completion_tokens=50 * i,
                total_tokens=150 * i,
                latency_ms=50.0 * i,
                retry_count=0,
                parsing_success=True,
                validation_success=True,
                error_message=None,
                xml_structure_used=False,
            )
            tracker.log_metric(metric)

        # Verify all entries were written
        metrics = tracker.get_metrics()
        assert len(metrics) == 5

    def test_retrieves_all_metrics(self, tmp_path):
        """Test retrieving all metrics."""
        metrics_file = tmp_path / "metrics.json"
        tracker = MetricsTracker(metrics_file=str(metrics_file))

        # Log some metrics
        for i in range(3):
            metric = PromptMetrics(
                timestamp=datetime.now().isoformat(),
                workflow="test",
                agent_role="Tester",
                task_description="Task",
                model="gpt-4o",
                prompt_tokens=100,
                completion_tokens=50,
                total_tokens=150,
                latency_ms=50.0,
                retry_count=0,
                parsing_success=True,
                validation_success=True,
                error_message=None,
                xml_structure_used=False,
            )
            tracker.log_metric(metric)

        metrics = tracker.get_metrics()
        assert len(metrics) == 3

    def test_filters_by_workflow(self, tmp_path):
        """Test filtering metrics by workflow."""
        metrics_file = tmp_path / "metrics.json"
        tracker = MetricsTracker(metrics_file=str(metrics_file))

        # Log metrics for different workflows
        for workflow in ["code-review", "test-gen", "code-review"]:
            metric = PromptMetrics(
                timestamp=datetime.now().isoformat(),
                workflow=workflow,
                agent_role="Tester",
                task_description="Task",
                model="gpt-4o",
                prompt_tokens=100,
                completion_tokens=50,
                total_tokens=150,
                latency_ms=50.0,
                retry_count=0,
                parsing_success=True,
                validation_success=True,
                error_message=None,
                xml_structure_used=False,
            )
            tracker.log_metric(metric)

        # Filter by workflow
        code_review_metrics = tracker.get_metrics(workflow="code-review")
        assert len(code_review_metrics) == 2

        test_gen_metrics = tracker.get_metrics(workflow="test-gen")
        assert len(test_gen_metrics) == 1

    def test_filters_by_date_range(self, tmp_path):
        """Test filtering metrics by date range."""
        metrics_file = tmp_path / "metrics.json"
        tracker = MetricsTracker(metrics_file=str(metrics_file))

        # Log metrics with different timestamps
        now = datetime.now()
        yesterday = now - timedelta(days=1)
        tomorrow = now + timedelta(days=1)

        for timestamp in [yesterday, now, tomorrow]:
            metric = PromptMetrics(
                timestamp=timestamp.isoformat(),
                workflow="test",
                agent_role="Tester",
                task_description="Task",
                model="gpt-4o",
                prompt_tokens=100,
                completion_tokens=50,
                total_tokens=150,
                latency_ms=50.0,
                retry_count=0,
                parsing_success=True,
                validation_success=True,
                error_message=None,
                xml_structure_used=False,
            )
            tracker.log_metric(metric)

        # Filter by date range
        metrics = tracker.get_metrics(
            start_date=yesterday,
            end_date=now + timedelta(hours=1),
        )
        assert len(metrics) == 2  # yesterday and today


class TestMetricsAggregation:
    """Test metrics aggregation and summary generation."""

    def test_calculates_summary(self, tmp_path):
        """Test calculating summary statistics."""
        metrics_file = tmp_path / "metrics.json"
        tracker = MetricsTracker(metrics_file=str(metrics_file))

        # Log multiple metrics
        for i in range(10):
            metric = PromptMetrics(
                timestamp=datetime.now().isoformat(),
                workflow="test",
                agent_role="Tester",
                task_description="Task",
                model="gpt-4o",
                prompt_tokens=100 + i * 10,
                completion_tokens=50 + i * 5,
                total_tokens=150 + i * 15,
                latency_ms=50.0 + i * 10,
                retry_count=0 if i % 2 == 0 else 1,
                parsing_success=i % 3 != 0,
                validation_success=i % 4 != 0,
                error_message=None,
                xml_structure_used=True,
            )
            tracker.log_metric(metric)

        summary = tracker.get_summary()

        assert summary["total_executions"] == 10
        assert summary["avg_prompt_tokens"] > 0
        assert summary["avg_completion_tokens"] > 0
        assert summary["avg_latency_ms"] > 0

    def test_groups_by_workflow(self, tmp_path):
        """Test grouping summary by workflow."""
        metrics_file = tmp_path / "metrics.json"
        tracker = MetricsTracker(metrics_file=str(metrics_file))

        # Log metrics for different workflows
        for workflow in ["code-review", "test-gen", "code-review", "test-gen"]:
            metric = PromptMetrics(
                timestamp=datetime.now().isoformat(),
                workflow=workflow,
                agent_role="Tester",
                task_description="Task",
                model="gpt-4o",
                prompt_tokens=100,
                completion_tokens=50,
                total_tokens=150,
                latency_ms=50.0,
                retry_count=0,
                parsing_success=True,
                validation_success=True,
                error_message=None,
                xml_structure_used=False,
            )
            tracker.log_metric(metric)

        summary = tracker.get_summary_by_workflow()

        assert "code-review" in summary
        assert "test-gen" in summary
        assert summary["code-review"]["total_executions"] == 2
        assert summary["test-gen"]["total_executions"] == 2

    def test_groups_by_model(self, tmp_path):
        """Test grouping summary by model."""
        metrics_file = tmp_path / "metrics.json"
        tracker = MetricsTracker(metrics_file=str(metrics_file))

        # Log metrics for different models
        for model in ["gpt-4o", "claude-sonnet-4.5", "gpt-4o"]:
            metric = PromptMetrics(
                timestamp=datetime.now().isoformat(),
                workflow="test",
                agent_role="Tester",
                task_description="Task",
                model=model,
                prompt_tokens=100,
                completion_tokens=50,
                total_tokens=150,
                latency_ms=50.0,
                retry_count=0,
                parsing_success=True,
                validation_success=True,
                error_message=None,
                xml_structure_used=False,
            )
            tracker.log_metric(metric)

        summary = tracker.get_summary_by_model()

        assert "gpt-4o" in summary
        assert "claude-sonnet-4.5" in summary
        assert summary["gpt-4o"]["total_executions"] == 2


class TestErrorTracking:
    """Test error tracking in metrics."""

    def test_tracks_errors(self, tmp_path):
        """Test tracking failed executions."""
        metrics_file = tmp_path / "metrics.json"
        tracker = MetricsTracker(metrics_file=str(metrics_file))

        # Log successful execution
        tracker.log_metric(
            PromptMetrics(
                timestamp=datetime.now().isoformat(),
                workflow="test",
                agent_role="Tester",
                task_description="Task",
                model="gpt-4o",
                prompt_tokens=100,
                completion_tokens=50,
                total_tokens=150,
                latency_ms=50.0,
                retry_count=0,
                parsing_success=True,
                validation_success=True,
                error_message=None,
                xml_structure_used=False,
            )
        )

        # Log failed execution
        tracker.log_metric(
            PromptMetrics(
                timestamp=datetime.now().isoformat(),
                workflow="test",
                agent_role="Tester",
                task_description="Task",
                model="gpt-4o",
                prompt_tokens=100,
                completion_tokens=0,
                total_tokens=100,
                latency_ms=10.0,
                retry_count=2,
                parsing_success=False,
                validation_success=False,
                error_message="XML parsing failed",
                xml_structure_used=False,
            )
        )

        summary = tracker.get_summary()

        assert summary["error_count"] == 1
        assert summary["error_rate"] == 0.5  # 1 out of 2

    def test_tracks_retry_counts(self, tmp_path):
        """Test tracking retry attempts."""
        metrics_file = tmp_path / "metrics.json"
        tracker = MetricsTracker(metrics_file=str(metrics_file))

        for retry_count in [0, 1, 2, 0, 3]:
            tracker.log_metric(
                PromptMetrics(
                    timestamp=datetime.now().isoformat(),
                    workflow="test",
                    agent_role="Tester",
                    task_description="Task",
                    model="gpt-4o",
                    prompt_tokens=100,
                    completion_tokens=50,
                    total_tokens=150,
                    latency_ms=50.0,
                    retry_count=retry_count,
                    parsing_success=True,
                    validation_success=True,
                    error_message=None,
                    xml_structure_used=False,
                )
            )

        summary = tracker.get_summary()

        assert summary["total_retries"] == 6  # 0+1+2+0+3
        assert summary["avg_retries"] == 1.2  # 6/5


class TestXMLUsageTracking:
    """Test tracking of XML-enhanced prompt usage."""

    def test_tracks_xml_usage(self, tmp_path):
        """Test tracking XML structure usage."""
        metrics_file = tmp_path / "metrics.json"
        tracker = MetricsTracker(metrics_file=str(metrics_file))

        # Log metrics with and without XML
        for xml_used in [True, True, False, True, False]:
            tracker.log_metric(
                PromptMetrics(
                    timestamp=datetime.now().isoformat(),
                    workflow="test",
                    agent_role="Tester",
                    task_description="Task",
                    model="gpt-4o",
                    prompt_tokens=100,
                    completion_tokens=50,
                    total_tokens=150,
                    latency_ms=50.0,
                    retry_count=0,
                    parsing_success=True,
                    validation_success=True,
                    error_message=None,
                    xml_structure_used=xml_used,
                )
            )

        summary = tracker.get_summary()

        assert summary["xml_usage_count"] == 3
        assert summary["xml_usage_rate"] == 0.6  # 3 out of 5

    def test_compares_xml_vs_non_xml_performance(self, tmp_path):
        """Test comparing performance of XML vs non-XML prompts."""
        metrics_file = tmp_path / "metrics.json"
        tracker = MetricsTracker(metrics_file=str(metrics_file))

        # XML prompts with better performance
        for _ in range(5):
            tracker.log_metric(
                PromptMetrics(
                    timestamp=datetime.now().isoformat(),
                    workflow="test",
                    agent_role="Tester",
                    task_description="Task",
                    model="gpt-4o",
                    prompt_tokens=100,
                    completion_tokens=50,
                    total_tokens=150,
                    latency_ms=50.0,
                    retry_count=0,
                    parsing_success=True,
                    validation_success=True,
                    error_message=None,
                    xml_structure_used=True,
                )
            )

        # Non-XML prompts with worse performance
        for _ in range(5):
            tracker.log_metric(
                PromptMetrics(
                    timestamp=datetime.now().isoformat(),
                    workflow="test",
                    agent_role="Tester",
                    task_description="Task",
                    model="gpt-4o",
                    prompt_tokens=150,
                    completion_tokens=75,
                    total_tokens=225,
                    latency_ms=100.0,
                    retry_count=1,
                    parsing_success=False,
                    validation_success=False,
                    error_message="Failed",
                    xml_structure_used=False,
                )
            )

        comparison = tracker.compare_xml_performance()

        assert comparison["xml"]["avg_latency_ms"] < comparison["non_xml"]["avg_latency_ms"]
        assert comparison["xml"]["error_rate"] < comparison["non_xml"]["error_rate"]


class TestFileHandling:
    """Test file handling edge cases."""

    def test_handles_empty_file(self, tmp_path):
        """Test handling empty metrics file."""
        metrics_file = tmp_path / "metrics.json"
        metrics_file.write_text("")

        tracker = MetricsTracker(metrics_file=str(metrics_file))
        metrics = tracker.get_metrics()

        assert len(metrics) == 0

    def test_handles_corrupted_entries(self, tmp_path):
        """Test handling corrupted JSON entries."""
        metrics_file = tmp_path / "metrics.json"
        tracker = MetricsTracker(metrics_file=str(metrics_file))

        # Log valid metric
        tracker.log_metric(
            PromptMetrics(
                timestamp=datetime.now().isoformat(),
                workflow="test",
                agent_role="Tester",
                task_description="Task",
                model="gpt-4o",
                prompt_tokens=100,
                completion_tokens=50,
                total_tokens=150,
                latency_ms=50.0,
                retry_count=0,
                parsing_success=True,
                validation_success=True,
                error_message=None,
                xml_structure_used=False,
            )
        )

        # Manually append corrupted entry
        with open(metrics_file, "a") as f:
            f.write("invalid json\n")

        # Should skip corrupted entry
        metrics = tracker.get_metrics()
        assert len(metrics) == 1

    def test_handles_missing_file(self, tmp_path):
        """Test handling non-existent metrics file."""
        metrics_file = tmp_path / "nonexistent.json"
        tracker = MetricsTracker(metrics_file=str(metrics_file))

        metrics = tracker.get_metrics()
        assert len(metrics) == 0
