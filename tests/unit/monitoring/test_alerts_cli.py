"""Unit tests for alert CLI

Tests the interactive alert setup wizard and alert engine.

Copyright 2025 Smart-AI-Memory
Licensed under Fair Source License 0.9
"""

import os
import tempfile
from pathlib import Path

import pytest

from empathy_os.monitoring.alerts_cli import AlertEngine


@pytest.mark.unit
class TestAlertEngineInitialization:
    """Test alert engine initialization."""

    def test_default_initialization(self):
        """Test initialization with default database path."""
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = os.path.join(tmpdir, "alerts.db")
            engine = AlertEngine(db_path=db_path)

            assert engine.db_path == Path(db_path)
            assert Path(db_path).exists()

    def test_creates_parent_directory(self):
        """Test that engine creates parent directory if it doesn't exist."""
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = os.path.join(tmpdir, "subdir", "alerts.db")
            AlertEngine(db_path=db_path)

            assert Path(db_path).parent.exists()
            assert Path(db_path).exists()

    def test_initializes_database_schema(self):
        """Test that database schema is created."""
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = os.path.join(tmpdir, "alerts.db")
            engine = AlertEngine(db_path=db_path)

            # Should be able to query alerts table
            alerts = engine.list_alerts()
            assert isinstance(alerts, list)


@pytest.mark.unit
class TestAlertEngineAddAlert:
    """Test adding alerts."""

    def test_add_alert_basic(self):
        """Test adding a basic alert."""
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = os.path.join(tmpdir, "alerts.db")
            engine = AlertEngine(db_path=db_path)

            engine.add_alert(
                alert_id="alert_001",
                name="Test Alert",
                metric="daily_cost",
                threshold=10.0,
                channel="vscode_output",
            )

            alerts = engine.list_alerts()
            assert len(alerts) == 1
            assert alerts[0]["id"] == "alert_001"
            assert alerts[0]["name"] == "Test Alert"
            assert alerts[0]["metric"] == "daily_cost"
            assert alerts[0]["threshold"] == 10.0
            assert alerts[0]["channel"] == "vscode_output"

    def test_add_alert_with_webhook(self):
        """Test adding alert with webhook URL."""
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = os.path.join(tmpdir, "alerts.db")
            engine = AlertEngine(db_path=db_path)

            engine.add_alert(
                alert_id="alert_001",
                name="Webhook Alert",
                metric="error_rate",
                threshold=5.0,
                channel="webhook",
                webhook_url="https://hooks.slack.com/test",
            )

            alerts = engine.list_alerts()
            assert alerts[0]["webhook_url"] == "https://hooks.slack.com/test"

    def test_add_alert_with_email(self):
        """Test adding alert with email."""
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = os.path.join(tmpdir, "alerts.db")
            engine = AlertEngine(db_path=db_path)

            engine.add_alert(
                alert_id="alert_001",
                name="Email Alert",
                metric="token_usage",
                threshold=100000.0,
                channel="email",
                email="admin@example.com",
            )

            alerts = engine.list_alerts()
            assert alerts[0]["email"] == "admin@example.com"

    def test_add_multiple_alerts(self):
        """Test adding multiple alerts."""
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = os.path.join(tmpdir, "alerts.db")
            engine = AlertEngine(db_path=db_path)

            engine.add_alert(
                alert_id="alert_001",
                name="Cost Alert",
                metric="daily_cost",
                threshold=10.0,
                channel="vscode_output",
            )

            engine.add_alert(
                alert_id="alert_002",
                name="Error Alert",
                metric="error_rate",
                threshold=5.0,
                channel="email",
                email="admin@example.com",
            )

            alerts = engine.list_alerts()
            assert len(alerts) == 2


@pytest.mark.unit
class TestAlertEngineListAlerts:
    """Test listing alerts."""

    def test_list_alerts_empty(self):
        """Test listing alerts when database is empty."""
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = os.path.join(tmpdir, "alerts.db")
            engine = AlertEngine(db_path=db_path)

            alerts = engine.list_alerts()
            assert len(alerts) == 0
            assert isinstance(alerts, list)

    def test_list_alerts_returns_all_fields(self):
        """Test that list_alerts returns all alert fields."""
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = os.path.join(tmpdir, "alerts.db")
            engine = AlertEngine(db_path=db_path)

            engine.add_alert(
                alert_id="alert_001",
                name="Test Alert",
                metric="daily_cost",
                threshold=10.0,
                channel="vscode_output",
            )

            alerts = engine.list_alerts()
            alert = alerts[0]

            # Check all expected fields exist
            assert "id" in alert
            assert "name" in alert
            assert "metric" in alert
            assert "threshold" in alert
            assert "channel" in alert
            assert "webhook_url" in alert
            assert "email" in alert
            assert "enabled" in alert
            assert "cooldown" in alert
            assert "created_at" in alert

    def test_list_alerts_enabled_field_is_boolean(self):
        """Test that enabled field is converted to boolean."""
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = os.path.join(tmpdir, "alerts.db")
            engine = AlertEngine(db_path=db_path)

            engine.add_alert(
                alert_id="alert_001",
                name="Test Alert",
                metric="daily_cost",
                threshold=10.0,
                channel="vscode_output",
            )

            alerts = engine.list_alerts()
            assert isinstance(alerts[0]["enabled"], bool)
            assert alerts[0]["enabled"] is True

    def test_list_alerts_default_values(self):
        """Test that default values are set correctly."""
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = os.path.join(tmpdir, "alerts.db")
            engine = AlertEngine(db_path=db_path)

            engine.add_alert(
                alert_id="alert_001",
                name="Test Alert",
                metric="daily_cost",
                threshold=10.0,
                channel="vscode_output",
            )

            alerts = engine.list_alerts()
            assert alerts[0]["enabled"] is True
            assert alerts[0]["cooldown"] == 3600  # Default 1 hour
            assert alerts[0]["webhook_url"] is None
            assert alerts[0]["email"] is None


@pytest.mark.unit
class TestAlertEngineDeleteAlert:
    """Test deleting alerts."""

    def test_delete_alert_success(self):
        """Test successfully deleting an alert."""
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = os.path.join(tmpdir, "alerts.db")
            engine = AlertEngine(db_path=db_path)

            engine.add_alert(
                alert_id="alert_001",
                name="Test Alert",
                metric="daily_cost",
                threshold=10.0,
                channel="vscode_output",
            )

            assert len(engine.list_alerts()) == 1

            deleted = engine.delete_alert("alert_001")

            assert deleted is True
            assert len(engine.list_alerts()) == 0

    def test_delete_nonexistent_alert(self):
        """Test deleting alert that doesn't exist."""
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = os.path.join(tmpdir, "alerts.db")
            engine = AlertEngine(db_path=db_path)

            deleted = engine.delete_alert("nonexistent")

            assert deleted is False

    def test_delete_alert_leaves_others(self):
        """Test that deleting one alert doesn't affect others."""
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = os.path.join(tmpdir, "alerts.db")
            engine = AlertEngine(db_path=db_path)

            engine.add_alert(
                alert_id="alert_001",
                name="Alert 1",
                metric="daily_cost",
                threshold=10.0,
                channel="vscode_output",
            )

            engine.add_alert(
                alert_id="alert_002",
                name="Alert 2",
                metric="error_rate",
                threshold=5.0,
                channel="email",
                email="admin@example.com",
            )

            assert len(engine.list_alerts()) == 2

            deleted = engine.delete_alert("alert_001")

            assert deleted is True
            alerts = engine.list_alerts()
            assert len(alerts) == 1
            assert alerts[0]["id"] == "alert_002"


@pytest.mark.unit
class TestAlertEngineMetricTypes:
    """Test different metric types."""

    def test_daily_cost_alert(self):
        """Test creating daily_cost alert."""
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = os.path.join(tmpdir, "alerts.db")
            engine = AlertEngine(db_path=db_path)

            engine.add_alert(
                alert_id="alert_001",
                name="Daily Cost Alert",
                metric="daily_cost",
                threshold=10.0,
                channel="vscode_output",
            )

            alerts = engine.list_alerts()
            assert alerts[0]["metric"] == "daily_cost"

    def test_error_rate_alert(self):
        """Test creating error_rate alert."""
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = os.path.join(tmpdir, "alerts.db")
            engine = AlertEngine(db_path=db_path)

            engine.add_alert(
                alert_id="alert_001",
                name="Error Rate Alert",
                metric="error_rate",
                threshold=10.0,
                channel="vscode_output",
            )

            alerts = engine.list_alerts()
            assert alerts[0]["metric"] == "error_rate"

    def test_avg_latency_alert(self):
        """Test creating avg_latency alert."""
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = os.path.join(tmpdir, "alerts.db")
            engine = AlertEngine(db_path=db_path)

            engine.add_alert(
                alert_id="alert_001",
                name="Latency Alert",
                metric="avg_latency",
                threshold=3000.0,
                channel="vscode_output",
            )

            alerts = engine.list_alerts()
            assert alerts[0]["metric"] == "avg_latency"

    def test_token_usage_alert(self):
        """Test creating token_usage alert."""
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = os.path.join(tmpdir, "alerts.db")
            engine = AlertEngine(db_path=db_path)

            engine.add_alert(
                alert_id="alert_001",
                name="Token Usage Alert",
                metric="token_usage",
                threshold=100000.0,
                channel="vscode_output",
            )

            alerts = engine.list_alerts()
            assert alerts[0]["metric"] == "token_usage"


@pytest.mark.unit
class TestAlertEngineChannelTypes:
    """Test different channel types."""

    def test_vscode_output_channel(self):
        """Test vscode_output channel."""
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = os.path.join(tmpdir, "alerts.db")
            engine = AlertEngine(db_path=db_path)

            engine.add_alert(
                alert_id="alert_001",
                name="VSCode Alert",
                metric="daily_cost",
                threshold=10.0,
                channel="vscode_output",
            )

            alerts = engine.list_alerts()
            assert alerts[0]["channel"] == "vscode_output"

    def test_webhook_channel(self):
        """Test webhook channel."""
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = os.path.join(tmpdir, "alerts.db")
            engine = AlertEngine(db_path=db_path)

            engine.add_alert(
                alert_id="alert_001",
                name="Webhook Alert",
                metric="daily_cost",
                threshold=10.0,
                channel="webhook",
                webhook_url="https://hooks.slack.com/test",
            )

            alerts = engine.list_alerts()
            assert alerts[0]["channel"] == "webhook"
            assert alerts[0]["webhook_url"] == "https://hooks.slack.com/test"

    def test_email_channel(self):
        """Test email channel."""
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = os.path.join(tmpdir, "alerts.db")
            engine = AlertEngine(db_path=db_path)

            engine.add_alert(
                alert_id="alert_001",
                name="Email Alert",
                metric="daily_cost",
                threshold=10.0,
                channel="email",
                email="admin@example.com",
            )

            alerts = engine.list_alerts()
            assert alerts[0]["channel"] == "email"
            assert alerts[0]["email"] == "admin@example.com"


@pytest.mark.unit
class TestAlertEnginePersistence:
    """Test alert persistence across engine instances."""

    def test_alerts_persist_across_instances(self):
        """Test that alerts persist when creating new engine instances."""
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = os.path.join(tmpdir, "alerts.db")

            # Create first engine and add alert
            engine1 = AlertEngine(db_path=db_path)
            engine1.add_alert(
                alert_id="alert_001",
                name="Test Alert",
                metric="daily_cost",
                threshold=10.0,
                channel="vscode_output",
            )

            # Create second engine with same database
            engine2 = AlertEngine(db_path=db_path)
            alerts = engine2.list_alerts()

            assert len(alerts) == 1
            assert alerts[0]["id"] == "alert_001"

    def test_delete_persists_across_instances(self):
        """Test that deletions persist across engine instances."""
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = os.path.join(tmpdir, "alerts.db")

            # Create first engine and add alert
            engine1 = AlertEngine(db_path=db_path)
            engine1.add_alert(
                alert_id="alert_001",
                name="Test Alert",
                metric="daily_cost",
                threshold=10.0,
                channel="vscode_output",
            )

            # Delete with first engine
            engine1.delete_alert("alert_001")

            # Verify deletion with second engine
            engine2 = AlertEngine(db_path=db_path)
            alerts = engine2.list_alerts()

            assert len(alerts) == 0
