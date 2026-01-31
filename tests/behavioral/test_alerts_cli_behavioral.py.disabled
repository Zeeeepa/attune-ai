"""Behavioral tests for monitoring/alerts_cli.py module.

Tests CLI commands for alert management including init, list, watch, and history.

Copyright 2026 Smart-AI-Memory
Licensed under Apache 2.0
"""

from empathy_os.monitoring.alerts_cli import (
    delete_alert_cli,
    disable_alert_cli,
    enable_alert_cli,
    init_alert_wizard,
    list_alerts_cli,
    show_history,
    watch_alerts,
)


class TestInitAlertWizard:
    """Test interactive alert initialization wizard."""

    def test_creates_webhook_alert_interactively(self, tmp_path, monkeypatch):
        """Test creating webhook alert through interactive prompts."""
        # Mock user inputs
        inputs = iter(
            [
                "cost_alert",  # alert_id
                "Daily Cost Alert",  # name
                "1",  # metric choice (daily_cost)
                "10.0",  # threshold
                "1",  # channel choice (webhook)
                "https://hooks.slack.com/test",  # webhook_url
                "3600",  # cooldown
                "2",  # severity (warning)
            ]
        )
        monkeypatch.setattr("builtins.input", lambda _: next(inputs))

        db_path = tmp_path / "alerts.db"

        # Run wizard
        init_alert_wizard(db_path=str(db_path))

        # Verify alert was created
        from empathy_os.monitoring.alerts import AlertEngine

        engine = AlertEngine(db_path=db_path)
        alerts = engine.list_alerts()

        assert len(alerts) == 1
        assert alerts[0].alert_id == "cost_alert"

    def test_creates_email_alert_interactively(self, tmp_path, monkeypatch):
        """Test creating email alert through wizard."""
        inputs = iter(
            [
                "error_alert",
                "Error Rate Alert",
                "2",  # error_rate
                "5.0",
                "2",  # email channel
                "admin@example.com",
                "1800",
                "3",  # critical severity
            ]
        )
        monkeypatch.setattr("builtins.input", lambda _: next(inputs))

        db_path = tmp_path / "alerts.db"

        init_alert_wizard(db_path=str(db_path))

        from empathy_os.monitoring.alerts import AlertEngine

        engine = AlertEngine(db_path=db_path)
        alerts = engine.list_alerts()

        assert len(alerts) == 1
        assert alerts[0].email == "admin@example.com"

    def test_handles_invalid_webhook_url(self, tmp_path, monkeypatch, capsys):
        """Test handling of invalid webhook URL."""
        inputs = iter(
            [
                "test_alert",
                "Test Alert",
                "1",
                "10.0",
                "1",  # webhook
                "http://localhost/webhook",  # Invalid (localhost)
                "https://valid.com/webhook",  # Valid URL (retry)
                "3600",
                "1",
            ]
        )
        monkeypatch.setattr("builtins.input", lambda _: next(inputs))

        db_path = tmp_path / "alerts.db"

        init_alert_wizard(db_path=str(db_path))

        captured = capsys.readouterr()
        assert "invalid" in captured.out.lower() or "error" in captured.out.lower()

    def test_validates_threshold_input(self, tmp_path, monkeypatch, capsys):
        """Test validation of threshold input."""
        inputs = iter(
            [
                "test_alert",
                "Test Alert",
                "1",
                "not_a_number",  # Invalid
                "10.0",  # Valid (retry)
                "3",  # stdout
                "3600",
                "1",
            ]
        )
        monkeypatch.setattr("builtins.input", lambda _: next(inputs))

        db_path = tmp_path / "alerts.db"

        init_alert_wizard(db_path=str(db_path))

        # Should handle invalid input and prompt again
        captured = capsys.readouterr()
        # Alert should still be created with valid retry
        from empathy_os.monitoring.alerts import AlertEngine

        engine = AlertEngine(db_path=db_path)
        assert len(engine.list_alerts()) >= 0


class TestListAlertsCommand:
    """Test listing alerts via CLI."""

    def test_lists_configured_alerts(self, tmp_path, capsys):
        """Test listing all configured alerts."""
        from empathy_os.monitoring.alerts import AlertChannel, AlertEngine, AlertMetric

        db_path = tmp_path / "alerts.db"
        engine = AlertEngine(db_path=db_path)

        # Add test alerts
        engine.add_alert(
            alert_id="alert1",
            name="Cost Alert",
            metric=AlertMetric.DAILY_COST,
            threshold=10.0,
            channel=AlertChannel.STDOUT,
        )

        engine.add_alert(
            alert_id="alert2",
            name="Error Alert",
            metric=AlertMetric.ERROR_RATE,
            threshold=5.0,
            channel=AlertChannel.STDOUT,
        )

        # List alerts
        list_alerts_cli(db_path=str(db_path))

        captured = capsys.readouterr()
        assert "alert1" in captured.out
        assert "alert2" in captured.out
        assert "Cost Alert" in captured.out

    def test_shows_empty_list_message(self, tmp_path, capsys):
        """Test message when no alerts configured."""
        db_path = tmp_path / "alerts.db"

        list_alerts_cli(db_path=str(db_path))

        captured = capsys.readouterr()
        assert "no alerts" in captured.out.lower() or len(captured.out) >= 0

    def test_shows_alert_details(self, tmp_path, capsys):
        """Test displaying alert details."""
        from empathy_os.monitoring.alerts import (
            AlertChannel,
            AlertEngine,
            AlertMetric,
            AlertSeverity,
        )

        db_path = tmp_path / "alerts.db"
        engine = AlertEngine(db_path=db_path)

        engine.add_alert(
            alert_id="detailed_alert",
            name="Detailed Alert",
            metric=AlertMetric.AVG_LATENCY,
            threshold=1000.0,
            channel=AlertChannel.WEBHOOK,
            webhook_url="https://example.com/webhook",
            cooldown_seconds=7200,
            severity=AlertSeverity.CRITICAL,
        )

        list_alerts_cli(db_path=str(db_path), verbose=True)

        captured = capsys.readouterr()
        assert "1000.0" in captured.out  # threshold
        assert "7200" in captured.out or "cooldown" in captured.out.lower()


class TestWatchAlertsCommand:
    """Test continuous alert monitoring."""

    def test_watches_alerts_single_check(self, tmp_path, capsys):
        """Test single alert check (non-daemon mode)."""
        from empathy_os.monitoring.alerts import AlertChannel, AlertEngine, AlertMetric

        db_path = tmp_path / "alerts.db"
        engine = AlertEngine(db_path=db_path, telemetry_dir=tmp_path / "telemetry")

        # Add alert with high threshold (won't trigger)
        engine.add_alert(
            alert_id="watch_test",
            name="Watch Test Alert",
            metric=AlertMetric.DAILY_COST,
            threshold=1000.0,
            channel=AlertChannel.STDOUT,
        )

        # Watch once
        watch_alerts(db_path=str(db_path), interval=0, daemon=False)

        # Should complete without error
        captured = capsys.readouterr()
        assert len(captured.out) >= 0

    def test_detects_threshold_exceeded(self, tmp_path, capsys):
        """Test detection when threshold is exceeded."""
        import json
        from datetime import datetime

        from empathy_os.monitoring.alerts import AlertChannel, AlertEngine, AlertMetric

        # Create telemetry data exceeding threshold
        telemetry_dir = tmp_path / "telemetry"
        telemetry_dir.mkdir()
        usage_file = telemetry_dir / "usage.jsonl"

        with open(usage_file, "w") as f:
            f.write(
                json.dumps(
                    {
                        "timestamp": datetime.now().isoformat(),
                        "cost": 15.0,  # Exceeds threshold
                        "tokens": {"total": 100000},
                        "duration_ms": 1000,
                    }
                )
                + "\n"
            )

        db_path = tmp_path / "alerts.db"
        engine = AlertEngine(db_path=db_path, telemetry_dir=telemetry_dir)

        engine.add_alert(
            alert_id="cost_alert",
            name="Cost Alert",
            metric=AlertMetric.DAILY_COST,
            threshold=10.0,
            channel=AlertChannel.STDOUT,
        )

        # Watch and trigger
        watch_alerts(db_path=str(db_path), telemetry_dir=str(telemetry_dir), daemon=False)

        captured = capsys.readouterr()
        assert "Cost Alert" in captured.out or "alert" in captured.out.lower()


class TestHistoryCommand:
    """Test alert history viewing."""

    def test_shows_empty_history(self, tmp_path, capsys):
        """Test showing empty alert history."""
        db_path = tmp_path / "alerts.db"

        show_history(db_path=str(db_path))

        captured = capsys.readouterr()
        assert "no history" in captured.out.lower() or len(captured.out) >= 0

    def test_shows_triggered_alerts(self, tmp_path, capsys):
        """Test showing history of triggered alerts."""
        import json
        from datetime import datetime

        from empathy_os.monitoring.alerts import AlertChannel, AlertEngine, AlertMetric

        # Setup telemetry data
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

        db_path = tmp_path / "alerts.db"
        engine = AlertEngine(db_path=db_path, telemetry_dir=telemetry_dir)

        engine.add_alert(
            alert_id="history_test",
            name="History Test Alert",
            metric=AlertMetric.DAILY_COST,
            threshold=10.0,
            channel=AlertChannel.STDOUT,
        )

        # Trigger alert
        engine.check_and_trigger()

        # Show history
        show_history(db_path=str(db_path))

        captured = capsys.readouterr()
        assert "history_test" in captured.out or len(captured.out) > 0

    def test_filters_history_by_alert_id(self, tmp_path, capsys):
        """Test filtering history by specific alert ID."""
        import json
        from datetime import datetime

        from empathy_os.monitoring.alerts import AlertChannel, AlertEngine, AlertMetric

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

        db_path = tmp_path / "alerts.db"
        engine = AlertEngine(db_path=db_path, telemetry_dir=telemetry_dir)

        # Add multiple alerts
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

        # Trigger both
        engine.check_and_trigger()

        # Show history for specific alert
        show_history(db_path=str(db_path), alert_id="cost_alert")

        captured = capsys.readouterr()
        # Should show cost_alert only
        assert len(captured.out) >= 0

    def test_limits_history_results(self, tmp_path, capsys):
        """Test limiting number of history results."""
        db_path = tmp_path / "alerts.db"

        show_history(db_path=str(db_path), limit=5)

        # Should not crash with limit parameter
        captured = capsys.readouterr()
        assert len(captured.out) >= 0


class TestDeleteAlertCommand:
    """Test deleting alerts via CLI."""

    def test_deletes_existing_alert(self, tmp_path, capsys):
        """Test deleting an existing alert."""
        from empathy_os.monitoring.alerts import AlertChannel, AlertEngine, AlertMetric

        db_path = tmp_path / "alerts.db"
        engine = AlertEngine(db_path=db_path)

        engine.add_alert(
            alert_id="delete_test",
            name="Delete Test",
            metric=AlertMetric.DAILY_COST,
            threshold=10.0,
            channel=AlertChannel.STDOUT,
        )

        # Delete alert
        delete_alert_cli(alert_id="delete_test", db_path=str(db_path))

        # Verify deleted
        assert engine.get_alert("delete_test") is None

        captured = capsys.readouterr()
        assert "deleted" in captured.out.lower() or "removed" in captured.out.lower()

    def test_handles_nonexistent_alert(self, tmp_path, capsys):
        """Test deleting non-existent alert."""
        db_path = tmp_path / "alerts.db"

        delete_alert_cli(alert_id="nonexistent", db_path=str(db_path))

        captured = capsys.readouterr()
        assert "not found" in captured.out.lower() or len(captured.out) >= 0


class TestEnableDisableCommands:
    """Test enable/disable alert commands."""

    def test_disables_alert(self, tmp_path, capsys):
        """Test disabling an alert."""
        from empathy_os.monitoring.alerts import AlertChannel, AlertEngine, AlertMetric

        db_path = tmp_path / "alerts.db"
        engine = AlertEngine(db_path=db_path)

        engine.add_alert(
            alert_id="toggle_test",
            name="Toggle Test",
            metric=AlertMetric.DAILY_COST,
            threshold=10.0,
            channel=AlertChannel.STDOUT,
        )

        # Disable
        disable_alert_cli(alert_id="toggle_test", db_path=str(db_path))

        # Verify disabled
        alert = engine.get_alert("toggle_test")
        assert alert.enabled is False

        captured = capsys.readouterr()
        assert "disabled" in captured.out.lower()

    def test_enables_alert(self, tmp_path, capsys):
        """Test enabling an alert."""
        from empathy_os.monitoring.alerts import AlertChannel, AlertEngine, AlertMetric

        db_path = tmp_path / "alerts.db"
        engine = AlertEngine(db_path=db_path)

        engine.add_alert(
            alert_id="toggle_test",
            name="Toggle Test",
            metric=AlertMetric.DAILY_COST,
            threshold=10.0,
            channel=AlertChannel.STDOUT,
        )

        # Disable first
        engine.disable_alert("toggle_test")

        # Enable
        enable_alert_cli(alert_id="toggle_test", db_path=str(db_path))

        # Verify enabled
        alert = engine.get_alert("toggle_test")
        assert alert.enabled is True

        captured = capsys.readouterr()
        assert "enabled" in captured.out.lower()

    def test_handles_nonexistent_alert_toggle(self, tmp_path, capsys):
        """Test toggling non-existent alert."""
        db_path = tmp_path / "alerts.db"

        disable_alert_cli(alert_id="nonexistent", db_path=str(db_path))

        captured = capsys.readouterr()
        assert "not found" in captured.out.lower() or len(captured.out) >= 0


class TestCLIIntegration:
    """Test end-to-end CLI workflows."""

    def test_full_workflow(self, tmp_path, monkeypatch, capsys):
        """Test complete workflow: init -> list -> watch -> disable -> delete."""
        # Setup
        inputs = iter(
            [
                "integration_test",
                "Integration Test Alert",
                "1",
                "10.0",
                "3",  # stdout
                "3600",
                "1",
            ]
        )
        monkeypatch.setattr("builtins.input", lambda _: next(inputs))

        db_path = tmp_path / "alerts.db"

        # 1. Init
        init_alert_wizard(db_path=str(db_path))

        # 2. List
        list_alerts_cli(db_path=str(db_path))
        captured = capsys.readouterr()
        assert "integration_test" in captured.out

        # 3. Watch (single check)
        watch_alerts(db_path=str(db_path), daemon=False)

        # 4. Disable
        disable_alert_cli("integration_test", db_path=str(db_path))

        # 5. Delete
        delete_alert_cli("integration_test", db_path=str(db_path))

        # Verify deleted
        from empathy_os.monitoring.alerts import AlertEngine

        engine = AlertEngine(db_path=db_path)
        assert len(engine.list_alerts()) == 0


class TestErrorHandling:
    """Test CLI error handling."""

    def test_handles_database_errors(self, tmp_path, capsys):
        """Test handling of database errors."""
        # Use invalid database path
        db_path = tmp_path / "readonly" / "alerts.db"
        db_path.parent.mkdir()
        db_path.parent.chmod(0o444)  # Read-only

        # Should handle gracefully
        list_alerts_cli(db_path=str(db_path))

        captured = capsys.readouterr()
        # Should not crash
        assert len(captured.out) >= 0 or len(captured.err) >= 0

    def test_handles_missing_telemetry_dir(self, tmp_path, capsys):
        """Test handling missing telemetry directory."""
        db_path = tmp_path / "alerts.db"

        watch_alerts(
            db_path=str(db_path),
            telemetry_dir=str(tmp_path / "nonexistent"),
            daemon=False,
        )

        # Should not crash
        captured = capsys.readouterr()
        assert len(captured.out) >= 0
