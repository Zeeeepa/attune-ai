"""Behavioral tests for monitoring/alerts.py module.

Tests alert configuration, threshold monitoring, notification delivery, and security.

Copyright 2026 Smart-AI-Memory
Licensed under Apache 2.0
"""

import json
from datetime import datetime

import pytest

from attune.monitoring.alerts import (
    AlertChannel,
    AlertConfig,
    AlertEngine,
    AlertMetric,
    AlertSeverity,
    _validate_webhook_url,
)


class TestWebhookValidation:
    """Test webhook URL validation for security."""

    def test_allows_valid_https_urls(self):
        """Test that valid HTTPS URLs are allowed."""
        valid_urls = [
            "https://hooks.slack.com/services/T00/B00/XXX",
            "https://discord.com/api/webhooks/123/abc",
            "https://example.com/webhook",
        ]

        for url in valid_urls:
            assert _validate_webhook_url(url) == url

    def test_allows_valid_http_urls(self):
        """Test that valid HTTP URLs are allowed (for testing)."""
        url = "http://example.com/webhook"
        assert _validate_webhook_url(url) == url

    def test_blocks_localhost(self):
        """Test that localhost URLs are blocked."""
        invalid_urls = [
            "http://localhost/webhook",
            "http://127.0.0.1/webhook",
            "http://[::1]/webhook",
        ]

        for url in invalid_urls:
            with pytest.raises(ValueError, match="local or metadata"):
                _validate_webhook_url(url)

    def test_blocks_metadata_services(self):
        """Test that cloud metadata services are blocked."""
        invalid_urls = [
            "http://169.254.169.254/latest/meta-data",  # AWS
            "http://metadata.google.internal/",  # GCP
        ]

        for url in invalid_urls:
            with pytest.raises(ValueError, match="local or metadata"):
                _validate_webhook_url(url)

    def test_blocks_private_ips(self):
        """Test that private IP ranges are blocked."""
        invalid_urls = [
            "http://10.0.0.1/webhook",
            "http://172.16.0.1/webhook",
            "http://192.168.1.1/webhook",
        ]

        for url in invalid_urls:
            with pytest.raises(ValueError, match="private IP"):
                _validate_webhook_url(url)

    def test_blocks_internal_service_ports(self):
        """Test that internal service ports are blocked."""
        invalid_urls = [
            "http://example.com:22/webhook",  # SSH
            "http://example.com:3306/webhook",  # MySQL
            "http://example.com:6379/webhook",  # Redis
        ]

        for url in invalid_urls:
            with pytest.raises(ValueError, match="internal service port"):
                _validate_webhook_url(url)

    def test_blocks_non_http_schemes(self):
        """Test that non-HTTP schemes are blocked."""
        invalid_urls = [
            "file:///etc/passwd",
            "ftp://example.com/webhook",
            "gopher://example.com",
        ]

        for url in invalid_urls:
            with pytest.raises(ValueError, match="Only http and https"):
                _validate_webhook_url(url)

    def test_blocks_empty_urls(self):
        """Test that empty URLs are blocked."""
        with pytest.raises(ValueError, match="non-empty string"):
            _validate_webhook_url("")

    def test_blocks_urls_without_hostname(self):
        """Test that URLs without hostname are blocked."""
        with pytest.raises(ValueError, match="valid hostname"):
            _validate_webhook_url("http://")


class TestAlertEngineInitialization:
    """Test AlertEngine initialization and database setup."""

    def test_creates_database(self, tmp_path):
        """Test that database is created on initialization."""
        db_path = tmp_path / "alerts.db"
        AlertEngine(db_path=db_path)

        assert db_path.exists()

    def test_creates_parent_directory(self, tmp_path):
        """Test that parent directory is created if missing."""
        db_path = tmp_path / "subdir" / "alerts.db"
        AlertEngine(db_path=db_path)

        assert db_path.exists()
        assert db_path.parent.exists()

    def test_uses_default_telemetry_dir(self, tmp_path):
        """Test default telemetry directory."""
        engine = AlertEngine(db_path=tmp_path / "alerts.db")

        # Should default to ~/.attune/telemetry
        assert "telemetry" in str(engine.telemetry_dir)


class TestAlertConfiguration:
    """Test alert configuration management."""

    def test_adds_webhook_alert(self, tmp_path):
        """Test adding a webhook alert."""
        engine = AlertEngine(db_path=tmp_path / "alerts.db")

        config = engine.add_alert(
            alert_id="cost_alert",
            name="Daily Cost Alert",
            metric=AlertMetric.DAILY_COST,
            threshold=10.0,
            channel=AlertChannel.WEBHOOK,
            webhook_url="https://hooks.slack.com/test",
        )

        assert config.alert_id == "cost_alert"
        assert config.name == "Daily Cost Alert"
        assert config.threshold == 10.0

    def test_adds_email_alert(self, tmp_path):
        """Test adding an email alert."""
        engine = AlertEngine(db_path=tmp_path / "alerts.db")

        config = engine.add_alert(
            alert_id="error_alert",
            name="Error Rate Alert",
            metric=AlertMetric.ERROR_RATE,
            threshold=5.0,
            channel=AlertChannel.EMAIL,
            email="admin@example.com",
        )

        assert config.alert_id == "error_alert"
        assert config.email == "admin@example.com"

    def test_adds_stdout_alert(self, tmp_path):
        """Test adding a stdout alert."""
        engine = AlertEngine(db_path=tmp_path / "alerts.db")

        config = engine.add_alert(
            alert_id="latency_alert",
            name="Latency Alert",
            metric=AlertMetric.AVG_LATENCY,
            threshold=1000.0,
            channel=AlertChannel.STDOUT,
        )

        assert config.alert_id == "latency_alert"
        assert config.channel == AlertChannel.STDOUT

    def test_requires_webhook_url_for_webhook_channel(self, tmp_path):
        """Test that webhook URL is required for webhook channel."""
        engine = AlertEngine(db_path=tmp_path / "alerts.db")

        with pytest.raises(ValueError, match="webhook_url required"):
            engine.add_alert(
                alert_id="test_alert",
                name="Test Alert",
                metric=AlertMetric.DAILY_COST,
                threshold=10.0,
                channel=AlertChannel.WEBHOOK,
                # Missing webhook_url
            )

    def test_requires_email_for_email_channel(self, tmp_path):
        """Test that email is required for email channel."""
        engine = AlertEngine(db_path=tmp_path / "alerts.db")

        with pytest.raises(ValueError, match="email required"):
            engine.add_alert(
                alert_id="test_alert",
                name="Test Alert",
                metric=AlertMetric.ERROR_RATE,
                threshold=5.0,
                channel=AlertChannel.EMAIL,
                # Missing email
            )

    def test_accepts_enum_or_string_values(self, tmp_path):
        """Test that both enum and string values are accepted."""
        engine = AlertEngine(db_path=tmp_path / "alerts.db")

        # Using enums
        config1 = engine.add_alert(
            alert_id="alert1",
            name="Alert 1",
            metric=AlertMetric.DAILY_COST,
            threshold=10.0,
            channel=AlertChannel.STDOUT,
            severity=AlertSeverity.WARNING,
        )

        # Using strings
        config2 = engine.add_alert(
            alert_id="alert2",
            name="Alert 2",
            metric="daily_cost",
            threshold=10.0,
            channel="stdout",
            severity="critical",
        )

        assert config1.metric == AlertMetric.DAILY_COST
        assert config2.metric == AlertMetric.DAILY_COST


class TestAlertListing:
    """Test alert listing and retrieval."""

    def test_lists_all_alerts(self, tmp_path):
        """Test listing all configured alerts."""
        engine = AlertEngine(db_path=tmp_path / "alerts.db")

        engine.add_alert(
            alert_id="alert1",
            name="Alert 1",
            metric=AlertMetric.DAILY_COST,
            threshold=10.0,
            channel=AlertChannel.STDOUT,
        )

        engine.add_alert(
            alert_id="alert2",
            name="Alert 2",
            metric=AlertMetric.ERROR_RATE,
            threshold=5.0,
            channel=AlertChannel.STDOUT,
        )

        alerts = engine.list_alerts()

        assert len(alerts) == 2
        assert alerts[0].alert_id == "alert1"
        assert alerts[1].alert_id == "alert2"

    def test_gets_specific_alert(self, tmp_path):
        """Test retrieving a specific alert by ID."""
        engine = AlertEngine(db_path=tmp_path / "alerts.db")

        engine.add_alert(
            alert_id="test_alert",
            name="Test Alert",
            metric=AlertMetric.DAILY_COST,
            threshold=10.0,
            channel=AlertChannel.STDOUT,
        )

        alert = engine.get_alert("test_alert")

        assert alert is not None
        assert alert.alert_id == "test_alert"
        assert alert.name == "Test Alert"

    def test_returns_none_for_missing_alert(self, tmp_path):
        """Test that None is returned for non-existent alert."""
        engine = AlertEngine(db_path=tmp_path / "alerts.db")

        alert = engine.get_alert("nonexistent")

        assert alert is None


class TestAlertManagement:
    """Test alert enable/disable/delete operations."""

    def test_deletes_alert(self, tmp_path):
        """Test deleting an alert."""
        engine = AlertEngine(db_path=tmp_path / "alerts.db")

        engine.add_alert(
            alert_id="test_alert",
            name="Test Alert",
            metric=AlertMetric.DAILY_COST,
            threshold=10.0,
            channel=AlertChannel.STDOUT,
        )

        deleted = engine.delete_alert("test_alert")

        assert deleted is True
        assert engine.get_alert("test_alert") is None

    def test_delete_returns_false_for_missing_alert(self, tmp_path):
        """Test that delete returns False for non-existent alert."""
        engine = AlertEngine(db_path=tmp_path / "alerts.db")

        deleted = engine.delete_alert("nonexistent")

        assert deleted is False

    def test_disables_alert(self, tmp_path):
        """Test disabling an alert."""
        engine = AlertEngine(db_path=tmp_path / "alerts.db")

        engine.add_alert(
            alert_id="test_alert",
            name="Test Alert",
            metric=AlertMetric.DAILY_COST,
            threshold=10.0,
            channel=AlertChannel.STDOUT,
        )

        result = engine.disable_alert("test_alert")

        assert result is True
        alert = engine.get_alert("test_alert")
        assert alert.enabled is False

    def test_enables_alert(self, tmp_path):
        """Test enabling an alert."""
        engine = AlertEngine(db_path=tmp_path / "alerts.db")

        engine.add_alert(
            alert_id="test_alert",
            name="Test Alert",
            metric=AlertMetric.DAILY_COST,
            threshold=10.0,
            channel=AlertChannel.STDOUT,
        )

        engine.disable_alert("test_alert")
        result = engine.enable_alert("test_alert")

        assert result is True
        alert = engine.get_alert("test_alert")
        assert alert.enabled is True


class TestMetricsCalculation:
    """Test telemetry metrics calculation."""

    def test_calculates_metrics_from_telemetry(self, tmp_path):
        """Test calculating metrics from telemetry files."""
        # Create telemetry directory and file
        telemetry_dir = tmp_path / "telemetry"
        telemetry_dir.mkdir()
        usage_file = telemetry_dir / "usage.jsonl"

        # Write sample telemetry data
        now = datetime.now()
        entries = [
            {
                "timestamp": now.isoformat(),
                "cost": 0.01,
                "tokens": {"total": 1000},
                "duration_ms": 500,
            },
            {
                "timestamp": now.isoformat(),
                "cost": 0.02,
                "tokens": {"total": 2000},
                "duration_ms": 1000,
                "error": True,
            },
        ]

        with open(usage_file, "w") as f:
            for entry in entries:
                f.write(json.dumps(entry) + "\n")

        engine = AlertEngine(
            db_path=tmp_path / "alerts.db",
            telemetry_dir=telemetry_dir,
        )

        metrics = engine.get_metrics()

        assert metrics["daily_cost"] == 0.03
        assert metrics["error_rate"] == 50.0  # 1 error out of 2 calls
        assert metrics["avg_latency"] == 750.0  # (500 + 1000) / 2
        assert metrics["token_usage"] == 3000

    def test_returns_zero_metrics_when_no_data(self, tmp_path):
        """Test that zero metrics are returned when no telemetry data exists."""
        engine = AlertEngine(
            db_path=tmp_path / "alerts.db",
            telemetry_dir=tmp_path / "nonexistent",
        )

        metrics = engine.get_metrics()

        assert metrics["daily_cost"] == 0.0
        assert metrics["error_rate"] == 0.0
        assert metrics["avg_latency"] == 0.0
        assert metrics["token_usage"] == 0

    def test_handles_corrupted_telemetry(self, tmp_path):
        """Test handling of corrupted telemetry data."""
        telemetry_dir = tmp_path / "telemetry"
        telemetry_dir.mkdir()
        usage_file = telemetry_dir / "usage.jsonl"

        # Write valid and invalid entries
        with open(usage_file, "w") as f:
            f.write(
                json.dumps(
                    {
                        "timestamp": datetime.now().isoformat(),
                        "cost": 0.01,
                        "tokens": {"total": 1000},
                        "duration_ms": 500,
                    }
                )
                + "\n"
            )
            f.write("invalid json\n")

        engine = AlertEngine(
            db_path=tmp_path / "alerts.db",
            telemetry_dir=telemetry_dir,
        )

        metrics = engine.get_metrics()

        # Should skip invalid entry and calculate from valid one
        assert metrics["daily_cost"] == 0.01


class TestAlertTriggering:
    """Test alert threshold checking and triggering."""

    def test_triggers_alert_when_threshold_exceeded(self, tmp_path, capsys):
        """Test that alert triggers when threshold is exceeded."""
        # Create telemetry data exceeding threshold
        telemetry_dir = tmp_path / "telemetry"
        telemetry_dir.mkdir()
        usage_file = telemetry_dir / "usage.jsonl"

        with open(usage_file, "w") as f:
            f.write(
                json.dumps(
                    {
                        "timestamp": datetime.now().isoformat(),
                        "cost": 15.0,  # Exceeds threshold of 10.0
                        "tokens": {"total": 100000},
                        "duration_ms": 1000,
                    }
                )
                + "\n"
            )

        engine = AlertEngine(
            db_path=tmp_path / "alerts.db",
            telemetry_dir=telemetry_dir,
        )

        engine.add_alert(
            alert_id="cost_alert",
            name="Cost Alert",
            metric=AlertMetric.DAILY_COST,
            threshold=10.0,
            channel=AlertChannel.STDOUT,
        )

        events = engine.check_and_trigger()

        assert len(events) == 1
        assert events[0].alert_id == "cost_alert"
        assert events[0].current_value == 15.0

        # Check that message was printed to stdout
        captured = capsys.readouterr()
        assert "Cost Alert" in captured.out

    def test_does_not_trigger_when_below_threshold(self, tmp_path):
        """Test that alert does not trigger when below threshold."""
        telemetry_dir = tmp_path / "telemetry"
        telemetry_dir.mkdir()
        usage_file = telemetry_dir / "usage.jsonl"

        with open(usage_file, "w") as f:
            f.write(
                json.dumps(
                    {
                        "timestamp": datetime.now().isoformat(),
                        "cost": 5.0,  # Below threshold of 10.0
                        "tokens": {"total": 50000},
                        "duration_ms": 500,
                    }
                )
                + "\n"
            )

        engine = AlertEngine(
            db_path=tmp_path / "alerts.db",
            telemetry_dir=telemetry_dir,
        )

        engine.add_alert(
            alert_id="cost_alert",
            name="Cost Alert",
            metric=AlertMetric.DAILY_COST,
            threshold=10.0,
            channel=AlertChannel.STDOUT,
        )

        events = engine.check_and_trigger()

        assert len(events) == 0

    def test_skips_disabled_alerts(self, tmp_path):
        """Test that disabled alerts are not triggered."""
        telemetry_dir = tmp_path / "telemetry"
        telemetry_dir.mkdir()
        usage_file = telemetry_dir / "usage.jsonl"

        with open(usage_file, "w") as f:
            f.write(
                json.dumps(
                    {
                        "timestamp": datetime.now().isoformat(),
                        "cost": 15.0,
                        "tokens": {"total": 100000},
                        "duration_ms": 1000,
                    }
                )
                + "\n"
            )

        engine = AlertEngine(
            db_path=tmp_path / "alerts.db",
            telemetry_dir=telemetry_dir,
        )

        engine.add_alert(
            alert_id="cost_alert",
            name="Cost Alert",
            metric=AlertMetric.DAILY_COST,
            threshold=10.0,
            channel=AlertChannel.STDOUT,
        )

        engine.disable_alert("cost_alert")

        events = engine.check_and_trigger()

        assert len(events) == 0


class TestCooldownMechanism:
    """Test alert cooldown to prevent spam."""

    def test_respects_cooldown_period(self, tmp_path):
        """Test that alerts respect cooldown period."""
        telemetry_dir = tmp_path / "telemetry"
        telemetry_dir.mkdir()
        usage_file = telemetry_dir / "usage.jsonl"

        with open(usage_file, "w") as f:
            f.write(
                json.dumps(
                    {
                        "timestamp": datetime.now().isoformat(),
                        "cost": 15.0,
                        "tokens": {"total": 100000},
                        "duration_ms": 1000,
                    }
                )
                + "\n"
            )

        engine = AlertEngine(
            db_path=tmp_path / "alerts.db",
            telemetry_dir=telemetry_dir,
        )

        engine.add_alert(
            alert_id="cost_alert",
            name="Cost Alert",
            metric=AlertMetric.DAILY_COST,
            threshold=10.0,
            channel=AlertChannel.STDOUT,
            cooldown_seconds=3600,  # 1 hour
        )

        # First check should trigger
        events1 = engine.check_and_trigger()
        assert len(events1) == 1

        # Second check immediately after should not trigger (cooldown)
        events2 = engine.check_and_trigger()
        assert len(events2) == 0


class TestAlertHistory:
    """Test alert history tracking."""

    def test_records_triggered_alerts(self, tmp_path):
        """Test that triggered alerts are recorded in history."""
        telemetry_dir = tmp_path / "telemetry"
        telemetry_dir.mkdir()
        usage_file = telemetry_dir / "usage.jsonl"

        with open(usage_file, "w") as f:
            f.write(
                json.dumps(
                    {
                        "timestamp": datetime.now().isoformat(),
                        "cost": 15.0,
                        "tokens": {"total": 100000},
                        "duration_ms": 1000,
                    }
                )
                + "\n"
            )

        engine = AlertEngine(
            db_path=tmp_path / "alerts.db",
            telemetry_dir=telemetry_dir,
        )

        engine.add_alert(
            alert_id="cost_alert",
            name="Cost Alert",
            metric=AlertMetric.DAILY_COST,
            threshold=10.0,
            channel=AlertChannel.STDOUT,
        )

        engine.check_and_trigger()

        history = engine.get_alert_history(alert_id="cost_alert")

        assert len(history) == 1
        assert history[0]["alert_id"] == "cost_alert"
        assert history[0]["current_value"] == 15.0
        assert history[0]["delivered"] is True

    def test_retrieves_all_history(self, tmp_path):
        """Test retrieving all alert history."""
        telemetry_dir = tmp_path / "telemetry"
        telemetry_dir.mkdir()
        usage_file = telemetry_dir / "usage.jsonl"

        with open(usage_file, "w") as f:
            f.write(
                json.dumps(
                    {
                        "timestamp": datetime.now().isoformat(),
                        "cost": 15.0,
                        "tokens": {"total": 100000},
                        "duration_ms": 1000,
                        "error": True,
                    }
                )
                + "\n"
            )

        engine = AlertEngine(
            db_path=tmp_path / "alerts.db",
            telemetry_dir=telemetry_dir,
        )

        # Add two different alerts
        engine.add_alert(
            alert_id="cost_alert",
            name="Cost Alert",
            metric=AlertMetric.DAILY_COST,
            threshold=10.0,
            channel=AlertChannel.STDOUT,
        )

        engine.add_alert(
            alert_id="error_alert",
            name="Error Alert",
            metric=AlertMetric.ERROR_RATE,
            threshold=50.0,
            channel=AlertChannel.STDOUT,
        )

        engine.check_and_trigger()

        # Get all history
        history = engine.get_alert_history()

        assert len(history) == 2


class TestAlertSerialization:
    """Test alert configuration serialization."""

    def test_converts_to_dict(self):
        """Test converting AlertConfig to dictionary."""
        config = AlertConfig(
            alert_id="test_alert",
            name="Test Alert",
            metric=AlertMetric.DAILY_COST,
            threshold=10.0,
            channel=AlertChannel.WEBHOOK,
            webhook_url="https://example.com/webhook",
            cooldown_seconds=3600,
            severity=AlertSeverity.WARNING,
            created_at=datetime(2026, 1, 1, 12, 0, 0),
        )

        data = config.to_dict()

        assert data["alert_id"] == "test_alert"
        assert data["metric"] == "daily_cost"
        assert data["threshold"] == 10.0
        assert data["channel"] == "webhook"
        assert data["webhook_url"] == "https://example.com/webhook"

    def test_creates_from_dict(self):
        """Test creating AlertConfig from dictionary."""
        data = {
            "alert_id": "test_alert",
            "name": "Test Alert",
            "metric": "daily_cost",
            "threshold": 10.0,
            "channel": "webhook",
            "webhook_url": "https://example.com/webhook",
            "cooldown_seconds": 3600,
            "severity": "warning",
            "created_at": "2026-01-01T12:00:00",
        }

        config = AlertConfig.from_dict(data)

        assert config.alert_id == "test_alert"
        assert config.metric == AlertMetric.DAILY_COST
        assert config.threshold == 10.0
