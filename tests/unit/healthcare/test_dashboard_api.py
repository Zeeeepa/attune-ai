"""Unit tests for Nurse Dashboard FastAPI backend.

Tests cover REST endpoints, Pydantic model validation,
and WebSocket manager behaviour. CDSTeam.assess() is mocked
to avoid real agent execution.

Copyright 2026 Smart-AI-Memory
Licensed under Apache 2.0
"""

from __future__ import annotations

import json
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi import WebSocket
from fastapi.testclient import TestClient

from attune.agents.healthcare.cds_models import (
    CDSDecision,
    CDSQualityGate,
    ClinicalReasoningResult,
    ECGAnalysisResult,
)
from attune.healthcare.dashboard.app import PROTOCOLS, create_nurse_app
from attune.healthcare.dashboard.models import (
    AssessRequest,
    AssessResponse,
    AuditEntry,
    HealthResponse,
    PatientSummary,
    ProtocolInfo,
)
from attune.healthcare.dashboard.websocket import NurseWebSocketManager

# =============================================================================
# Fixtures
# =============================================================================


def _make_cds_decision(
    patient_id: str = "P-TEST-001",
    overall_risk: str = "moderate",
    confidence: float = 0.85,
    alerts: list[str] | None = None,
    recommendations: list[str] | None = None,
    include_reasoning: bool = False,
    include_ecg: bool = False,
) -> CDSDecision:
    """Build a CDSDecision for testing.

    Args:
        patient_id: Patient identifier.
        overall_risk: Risk level string.
        confidence: Confidence score.
        alerts: Optional list of alert messages.
        recommendations: Optional list of recommendation messages.
        include_reasoning: Whether to include ClinicalReasoningResult.
        include_ecg: Whether to include ECGAnalysisResult.

    Returns:
        A populated CDSDecision dataclass.
    """
    reasoning = None
    if include_reasoning:
        reasoning = ClinicalReasoningResult(
            narrative_summary="CDS Advisory: elevated troponin trend noted.",
            differentials=["NSTEMI", "Unstable angina"],
            recommended_workup=["Serial troponin", "12-lead ECG"],
            risk_level="high",
            confidence=0.9,
        )

    ecg = None
    if include_ecg:
        ecg = ECGAnalysisResult(
            heart_rate=88.0,
            hrv_sdnn=42.5,
            rhythm_classification="sinus_rhythm",
            arrhythmia_events=2,
            pvc_burden_pct=1.5,
            clinical_flags=["borderline_hrv"],
            confidence=0.92,
            score=78.0,
        )

    return CDSDecision(
        patient_id=patient_id,
        overall_risk=overall_risk,
        confidence=confidence,
        alerts=alerts or ["Monitor BP closely"],
        recommendations=recommendations or ["Recheck vitals in 30 min"],
        clinical_reasoning=reasoning,
        ecg_analysis=ecg,
        quality_gates=[
            CDSQualityGate(
                name="data_completeness",
                threshold=0.6,
                actual=0.85,
                passed=True,
            ),
            CDSQualityGate(
                name="min_confidence",
                threshold=0.5,
                actual=confidence,
                passed=confidence >= 0.5,
            ),
        ],
        cost=0.0042,
        timestamp=datetime(2026, 2, 9, 12, 0, 0).isoformat(),
    )


@pytest.fixture()
def mock_cds_team() -> MagicMock:
    """Return a MagicMock CDSTeam whose assess() is an AsyncMock."""
    team = MagicMock()
    team.assess = AsyncMock(return_value=_make_cds_decision())
    return team


@pytest.fixture()
def mock_audit_logger() -> MagicMock:
    """Return a MagicMock audit logger with common methods."""
    logger_mock = MagicMock()
    logger_mock.list_decisions = MagicMock(return_value=[])
    logger_mock.get_decision = MagicMock(return_value=None)
    return logger_mock


@pytest.fixture()
def app_no_startup() -> TestClient:
    """Create TestClient for a bare app (no startup side-effects).

    The CDS team and audit logger remain None, which lets us test
    endpoints that degrade gracefully without them.
    """
    app = create_nurse_app(redis_url=None)
    return TestClient(app, raise_server_exceptions=False)


@pytest.fixture()
def app_with_cds(mock_cds_team: MagicMock, mock_audit_logger: MagicMock) -> TestClient:
    """Create TestClient with mocked CDS team and audit logger.

    Patches the startup imports so the shared ``cds_team`` and
    ``audit_logger`` closures are set to our mocks.
    """
    app = create_nurse_app(redis_url=None)

    # Manually inject mocks into the closure by calling the startup
    # and intercepting the import.
    # Since the factory uses closures, we patch the modules that
    # startup() imports and trigger the event manually.
    with patch(
        "attune.healthcare.dashboard.app.CDSTeam",
        create=True,
    ) as _cls_team, patch(
        "attune.healthcare.dashboard.app.CDSAuditLogger",
        create=True,
    ) as _cls_audit:
        pass  # We cannot easily trigger FastAPI startup in sync tests.

    # Alternative: directly set the closure variables via app.state or
    # by patching the inner function references. FastAPI stores route
    # handlers that capture the nonlocal variables. We patch them by
    # running the startup event then overriding the module-level imports.

    # Simplest approach: use the TestClient context manager which fires
    # lifespan/startup events, but mock the imports inside startup.
    with patch.dict("sys.modules", {
        "attune.agents.healthcare.cds_team": MagicMock(
            CDSTeam=MagicMock(return_value=mock_cds_team)
        ),
        "attune.healthcare.audit.decision_log": MagicMock(
            CDSAuditLogger=MagicMock(return_value=mock_audit_logger)
        ),
    }):
        # Recreate the app so startup() picks up the patched modules
        app = create_nurse_app(redis_url=None)
        # Use context manager to trigger startup/shutdown lifespan events
        with TestClient(app, raise_server_exceptions=False) as client:
            yield client


# =============================================================================
# Health Endpoint Tests
# =============================================================================


class TestHealthEndpoint:
    """Tests for GET /api/health."""

    def test_health_returns_200(self, app_no_startup: TestClient) -> None:
        """GET /api/health returns HTTP 200 with status 'healthy'."""
        response = app_no_startup.get("/api/health")
        assert response.status_code == 200
        body = response.json()
        assert body["status"] == "healthy"

    def test_health_response_fields(self, app_no_startup: TestClient) -> None:
        """Health response includes all expected fields."""
        body = app_no_startup.get("/api/health").json()
        assert "service" in body
        assert body["service"] == "attune-nurse-dashboard"
        assert "version" in body
        assert "redis_connected" in body
        assert "uptime_seconds" in body

    def test_health_redis_disconnected(self, app_no_startup: TestClient) -> None:
        """When no Redis URL is provided, redis_connected is False."""
        body = app_no_startup.get("/api/health").json()
        assert body["redis_connected"] is False

    def test_health_uptime_non_negative(self, app_no_startup: TestClient) -> None:
        """Uptime should be a non-negative number."""
        body = app_no_startup.get("/api/health").json()
        assert body["uptime_seconds"] >= 0.0


# =============================================================================
# Protocol Endpoint Tests
# =============================================================================


class TestProtocolsEndpoint:
    """Tests for GET /api/protocols."""

    def test_protocols_returns_list(self, app_no_startup: TestClient) -> None:
        """GET /api/protocols returns a list."""
        response = app_no_startup.get("/api/protocols")
        assert response.status_code == 200
        protocols = response.json()
        assert isinstance(protocols, list)

    def test_protocols_has_expected_entries(self, app_no_startup: TestClient) -> None:
        """Response contains the four predefined protocols."""
        protocols = app_no_startup.get("/api/protocols").json()
        names = {p["name"] for p in protocols}
        assert names == {"cardiac", "sepsis", "respiratory", "post_operative"}

    def test_protocol_entry_has_required_fields(self, app_no_startup: TestClient) -> None:
        """Each protocol entry has name, display_name, description."""
        protocols = app_no_startup.get("/api/protocols").json()
        for proto in protocols:
            assert "name" in proto
            assert "display_name" in proto
            assert "description" in proto

    def test_protocols_matches_registry(self, app_no_startup: TestClient) -> None:
        """API output matches the PROTOCOLS dict in the module."""
        protocols = app_no_startup.get("/api/protocols").json()
        assert len(protocols) == len(PROTOCOLS)
        for proto in protocols:
            assert proto["name"] in PROTOCOLS


# =============================================================================
# Assessment Endpoint Tests
# =============================================================================


class TestAssessEndpoint:
    """Tests for POST /api/patients/{id}/assess."""

    def test_assess_returns_503_when_cds_unavailable(
        self, app_no_startup: TestClient
    ) -> None:
        """Without CDS team, assess endpoint returns 503."""
        response = app_no_startup.post(
            "/api/patients/P001/assess",
            json={
                "sensor_data": {"hr": 80, "systolic_bp": 120},
                "protocol_name": "cardiac",
            },
        )
        assert response.status_code == 503
        assert "CDS team not initialized" in response.json()["detail"]

    def test_assess_returns_valid_response(
        self, app_with_cds: TestClient, mock_cds_team: MagicMock
    ) -> None:
        """With mocked CDS team, assess returns a valid AssessResponse."""
        response = app_with_cds.post(
            "/api/patients/P-TEST-001/assess",
            json={
                "sensor_data": {"hr": 88, "systolic_bp": 135, "o2_sat": 96},
                "protocol_name": "cardiac",
            },
        )
        assert response.status_code == 200
        body = response.json()
        assert body["patient_id"] == "P-TEST-001"
        assert body["overall_risk"] == "moderate"
        assert body["confidence"] == 0.85
        assert isinstance(body["alerts"], list)
        assert isinstance(body["recommendations"], list)
        assert isinstance(body["quality_gates"], list)

    def test_assess_includes_quality_gates(
        self, app_with_cds: TestClient, mock_cds_team: MagicMock
    ) -> None:
        """Response quality_gates list contains expected gate structures."""
        response = app_with_cds.post(
            "/api/patients/P-TEST-001/assess",
            json={
                "sensor_data": {"hr": 80},
                "protocol_name": "sepsis",
            },
        )
        body = response.json()
        gates = body["quality_gates"]
        assert len(gates) == 2
        gate_names = {g["name"] for g in gates}
        assert "data_completeness" in gate_names
        assert "min_confidence" in gate_names
        for gate in gates:
            assert "passed" in gate
            assert "actual" in gate
            assert "threshold" in gate

    def test_assess_with_clinical_reasoning(
        self, app_with_cds: TestClient, mock_cds_team: MagicMock
    ) -> None:
        """When CDSDecision includes clinical_reasoning, response contains it."""
        decision = _make_cds_decision(include_reasoning=True)
        mock_cds_team.assess = AsyncMock(return_value=decision)

        response = app_with_cds.post(
            "/api/patients/P-TEST-001/assess",
            json={
                "sensor_data": {"hr": 100, "systolic_bp": 90},
                "protocol_name": "cardiac",
            },
        )
        body = response.json()
        reasoning = body.get("clinical_reasoning")
        assert reasoning is not None
        assert "narrative_summary" in reasoning
        assert "differentials" in reasoning
        assert isinstance(reasoning["differentials"], list)

    def test_assess_with_ecg_analysis(
        self, app_with_cds: TestClient, mock_cds_team: MagicMock
    ) -> None:
        """When CDSDecision includes ecg_analysis, response contains it."""
        decision = _make_cds_decision(include_ecg=True)
        mock_cds_team.assess = AsyncMock(return_value=decision)

        response = app_with_cds.post(
            "/api/patients/P-TEST-001/assess",
            json={
                "sensor_data": {"hr": 88},
                "protocol_name": "cardiac",
                "ecg_metrics": {"heart_rate": 88.0},
            },
        )
        body = response.json()
        ecg = body.get("ecg_analysis")
        assert ecg is not None
        assert ecg["heart_rate"] == 88.0
        assert ecg["rhythm_classification"] == "sinus_rhythm"
        assert "clinical_flags" in ecg

    def test_assess_no_reasoning_or_ecg_returns_null(
        self, app_with_cds: TestClient, mock_cds_team: MagicMock
    ) -> None:
        """When CDSDecision has no reasoning/ecg, response fields are null."""
        decision = _make_cds_decision(include_reasoning=False, include_ecg=False)
        mock_cds_team.assess = AsyncMock(return_value=decision)

        response = app_with_cds.post(
            "/api/patients/P-TEST-001/assess",
            json={
                "sensor_data": {"hr": 72},
                "protocol_name": "respiratory",
            },
        )
        body = response.json()
        assert body["clinical_reasoning"] is None
        assert body["ecg_analysis"] is None


# =============================================================================
# Decision Endpoint Tests
# =============================================================================


class TestDecisionEndpoint:
    """Tests for GET /api/decisions/{id}."""

    def test_decision_503_when_audit_unavailable(
        self, app_no_startup: TestClient
    ) -> None:
        """Without audit logger, decision endpoint returns 503."""
        response = app_no_startup.get("/api/decisions/some-uuid")
        assert response.status_code == 503

    def test_decision_404_when_not_found(
        self, app_with_cds: TestClient, mock_audit_logger: MagicMock
    ) -> None:
        """When audit logger returns None, endpoint returns 404."""
        mock_audit_logger.get_decision.return_value = None
        response = app_with_cds.get("/api/decisions/nonexistent-uuid")
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    def test_decision_returns_data_when_found(
        self, app_with_cds: TestClient, mock_audit_logger: MagicMock
    ) -> None:
        """When audit logger finds the decision, endpoint returns it."""
        decision_data = {
            "decision_id": "abc-123",
            "patient_id": "P001",
            "overall_risk": "high",
            "timestamp": "2026-02-09T12:00:00",
        }
        mock_audit_logger.get_decision.return_value = decision_data

        response = app_with_cds.get("/api/decisions/abc-123")
        assert response.status_code == 200
        assert response.json()["overall_risk"] == "high"


# =============================================================================
# Audit Trail Endpoint Tests
# =============================================================================


class TestAuditEndpoint:
    """Tests for GET /api/audit."""

    def test_audit_returns_empty_when_no_logger(
        self, app_no_startup: TestClient
    ) -> None:
        """Without audit logger, audit endpoint returns empty list."""
        response = app_no_startup.get("/api/audit")
        assert response.status_code == 200
        assert response.json() == []

    def test_audit_returns_list(
        self, app_with_cds: TestClient, mock_audit_logger: MagicMock
    ) -> None:
        """Audit endpoint returns a list from the audit logger."""
        mock_audit_logger.list_decisions.return_value = [
            {"decision_id": "d1", "overall_risk": "low"},
            {"decision_id": "d2", "overall_risk": "high"},
        ]
        response = app_with_cds.get("/api/audit")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 2


# =============================================================================
# Pydantic Model Validation Tests
# =============================================================================


class TestPydanticModels:
    """Tests for request/response Pydantic model validation."""

    def test_assess_request_valid(self) -> None:
        """AssessRequest accepts valid input."""
        req = AssessRequest(
            sensor_data={"hr": 80, "systolic_bp": 120},
            protocol_name="cardiac",
        )
        assert req.protocol_name == "cardiac"
        assert req.sensor_data["hr"] == 80
        assert req.ecg_metrics is None
        assert req.patient_context is None

    def test_assess_request_with_optional_fields(self) -> None:
        """AssessRequest accepts optional ecg_metrics and patient_context."""
        req = AssessRequest(
            sensor_data={"hr": 72},
            protocol_name="sepsis",
            ecg_metrics={"heart_rate": 72.0},
            patient_context={"age": 65, "medications": ["metoprolol"]},
        )
        assert req.ecg_metrics is not None
        assert req.patient_context["age"] == 65

    def test_assess_request_missing_required_field_raises(self) -> None:
        """AssessRequest raises ValidationError without sensor_data."""
        from pydantic import ValidationError

        with pytest.raises(ValidationError):
            AssessRequest(protocol_name="cardiac")  # type: ignore[call-arg]

    def test_assess_request_missing_protocol_raises(self) -> None:
        """AssessRequest raises ValidationError without protocol_name."""
        from pydantic import ValidationError

        with pytest.raises(ValidationError):
            AssessRequest(sensor_data={"hr": 80})  # type: ignore[call-arg]

    def test_health_response_defaults(self) -> None:
        """HealthResponse has correct default values."""
        resp = HealthResponse()
        assert resp.status == "healthy"
        assert resp.service == "attune-nurse-dashboard"
        assert resp.version == "2.5.0"
        assert resp.redis_connected is False
        assert resp.uptime_seconds == 0.0

    def test_health_response_custom_values(self) -> None:
        """HealthResponse accepts overridden field values."""
        resp = HealthResponse(
            status="degraded",
            redis_connected=True,
            uptime_seconds=123.4,
        )
        assert resp.status == "degraded"
        assert resp.redis_connected is True
        assert resp.uptime_seconds == 123.4

    def test_assess_response_defaults(self) -> None:
        """AssessResponse has correct defaults for optional fields."""
        resp = AssessResponse(
            patient_id="P001",
            overall_risk="low",
            confidence=0.9,
            alerts=[],
            recommendations=[],
        )
        assert resp.clinical_reasoning is None
        assert resp.ecg_analysis is None
        assert resp.quality_gates == []
        assert resp.cost == 0.0
        assert resp.timestamp == ""

    def test_protocol_info_construction(self) -> None:
        """ProtocolInfo stores name, display_name, description."""
        info = ProtocolInfo(
            name="cardiac",
            display_name="Cardiac Monitoring",
            description="ACS monitoring",
        )
        assert info.name == "cardiac"
        assert info.display_name == "Cardiac Monitoring"

    def test_patient_summary_defaults(self) -> None:
        """PatientSummary has expected defaults."""
        summary = PatientSummary(patient_id="P001")
        assert summary.latest_risk == "unknown"
        assert summary.alert_count == 0

    def test_audit_entry_construction(self) -> None:
        """AuditEntry stores all required fields."""
        entry = AuditEntry(
            decision_id="uuid-1",
            timestamp="2026-02-09T12:00:00",
            patient_id_hash="abc123hash",
            overall_risk="moderate",
            confidence=0.8,
            cost=0.005,
        )
        assert entry.decision_id == "uuid-1"
        assert entry.overall_risk == "moderate"
        assert entry.cost == 0.005


# =============================================================================
# WebSocket Manager Unit Tests
# =============================================================================


class TestNurseWebSocketManager:
    """Tests for NurseWebSocketManager connect/disconnect/subscribe/broadcast."""

    @pytest.fixture()
    def manager(self) -> NurseWebSocketManager:
        """Fresh NurseWebSocketManager instance."""
        return NurseWebSocketManager()

    @pytest.fixture()
    def mock_ws(self) -> MagicMock:
        """Create a mock WebSocket with async methods."""
        ws = MagicMock(spec=WebSocket)
        ws.accept = AsyncMock()
        ws.send_text = AsyncMock()
        ws.receive_text = AsyncMock()
        return ws

    @pytest.mark.asyncio()
    async def test_connect_adds_to_active(
        self, manager: NurseWebSocketManager, mock_ws: MagicMock
    ) -> None:
        """connect() accepts the WebSocket and adds it to active_connections."""
        await manager.connect(mock_ws)
        assert mock_ws in manager.active_connections
        assert manager.connection_count == 1
        mock_ws.accept.assert_awaited_once()

    @pytest.mark.asyncio()
    async def test_disconnect_removes_from_active(
        self, manager: NurseWebSocketManager, mock_ws: MagicMock
    ) -> None:
        """disconnect() removes the WebSocket from active_connections."""
        await manager.connect(mock_ws)
        await manager.disconnect(mock_ws)
        assert mock_ws not in manager.active_connections
        assert manager.connection_count == 0

    @pytest.mark.asyncio()
    async def test_disconnect_cleans_up_subscriptions(
        self, manager: NurseWebSocketManager, mock_ws: MagicMock
    ) -> None:
        """disconnect() removes WebSocket from all patient subscriptions."""
        await manager.connect(mock_ws)
        await manager.subscribe(mock_ws, ["P001", "P002"])
        assert manager.subscription_count == 2

        await manager.disconnect(mock_ws)
        assert manager.subscription_count == 0
        assert "P001" not in manager.subscriptions
        assert "P002" not in manager.subscriptions

    @pytest.mark.asyncio()
    async def test_subscribe_creates_patient_entries(
        self, manager: NurseWebSocketManager, mock_ws: MagicMock
    ) -> None:
        """subscribe() adds the WebSocket to each patient's subscriber set."""
        await manager.connect(mock_ws)
        await manager.subscribe(mock_ws, ["P001", "P002", "P003"])

        assert "P001" in manager.subscriptions
        assert mock_ws in manager.subscriptions["P001"]
        assert manager.subscription_count == 3

    @pytest.mark.asyncio()
    async def test_subscribe_multiple_ws_to_same_patient(
        self, manager: NurseWebSocketManager
    ) -> None:
        """Multiple WebSockets can subscribe to the same patient."""
        ws1 = MagicMock(spec=WebSocket)
        ws1.accept = AsyncMock()
        ws1.send_text = AsyncMock()
        ws2 = MagicMock(spec=WebSocket)
        ws2.accept = AsyncMock()
        ws2.send_text = AsyncMock()

        await manager.connect(ws1)
        await manager.connect(ws2)
        await manager.subscribe(ws1, ["P001"])
        await manager.subscribe(ws2, ["P001"])

        assert len(manager.subscriptions["P001"]) == 2

    @pytest.mark.asyncio()
    async def test_broadcast_to_patient_sends_to_subscribers(
        self, manager: NurseWebSocketManager, mock_ws: MagicMock
    ) -> None:
        """broadcast_to_patient() sends JSON to subscribed WebSockets."""
        await manager.connect(mock_ws)
        await manager.subscribe(mock_ws, ["P001"])

        await manager.broadcast_to_patient("P001", {"event": "new_assessment"})

        mock_ws.send_text.assert_awaited_once()
        sent_data = json.loads(mock_ws.send_text.call_args[0][0])
        assert sent_data["patient_id"] == "P001"
        assert sent_data["event"] == "new_assessment"

    @pytest.mark.asyncio()
    async def test_broadcast_to_patient_skips_unsubscribed(
        self, manager: NurseWebSocketManager, mock_ws: MagicMock
    ) -> None:
        """broadcast_to_patient() does nothing if no subscribers for patient."""
        await manager.connect(mock_ws)
        await manager.subscribe(mock_ws, ["P001"])

        await manager.broadcast_to_patient("P999", {"event": "test"})
        mock_ws.send_text.assert_not_awaited()

    @pytest.mark.asyncio()
    async def test_broadcast_alert_sends_to_all(
        self, manager: NurseWebSocketManager
    ) -> None:
        """broadcast_alert() sends to ALL active connections."""
        ws1 = MagicMock(spec=WebSocket)
        ws1.accept = AsyncMock()
        ws1.send_text = AsyncMock()
        ws2 = MagicMock(spec=WebSocket)
        ws2.accept = AsyncMock()
        ws2.send_text = AsyncMock()

        await manager.connect(ws1)
        await manager.connect(ws2)

        await manager.broadcast_alert({"patient_id": "P001", "risk": "critical"})

        ws1.send_text.assert_awaited_once()
        ws2.send_text.assert_awaited_once()
        sent = json.loads(ws1.send_text.call_args[0][0])
        assert sent["event"] == "alert"
        assert sent["risk"] == "critical"

    @pytest.mark.asyncio()
    async def test_broadcast_alert_no_connections(
        self, manager: NurseWebSocketManager
    ) -> None:
        """broadcast_alert() does nothing with zero connections."""
        await manager.broadcast_alert({"risk": "high"})
        # No exception; just returns silently

    @pytest.mark.asyncio()
    async def test_disconnect_idempotent(
        self, manager: NurseWebSocketManager, mock_ws: MagicMock
    ) -> None:
        """Disconnecting an already-disconnected WebSocket does not error."""
        await manager.connect(mock_ws)
        await manager.disconnect(mock_ws)
        await manager.disconnect(mock_ws)  # Should not raise
        assert manager.connection_count == 0

    @pytest.mark.asyncio()
    async def test_connection_count_property(
        self, manager: NurseWebSocketManager
    ) -> None:
        """connection_count reflects the current number of active connections."""
        assert manager.connection_count == 0
        ws1 = MagicMock(spec=WebSocket)
        ws1.accept = AsyncMock()
        ws2 = MagicMock(spec=WebSocket)
        ws2.accept = AsyncMock()

        await manager.connect(ws1)
        assert manager.connection_count == 1
        await manager.connect(ws2)
        assert manager.connection_count == 2
        await manager.disconnect(ws1)
        assert manager.connection_count == 1


# =============================================================================
# WebSocket Endpoint Integration Tests
# =============================================================================


class TestWebSocketEndpoint:
    """Integration tests for the /ws/monitor WebSocket endpoint."""

    def test_websocket_ping_pong(self, app_no_startup: TestClient) -> None:
        """WebSocket responds to ping with pong."""
        with app_no_startup.websocket_connect("/ws/monitor") as ws:
            ws.send_text(json.dumps({"action": "ping"}))
            data = json.loads(ws.receive_text())
            assert data["event"] == "pong"

    def test_websocket_subscribe(self, app_no_startup: TestClient) -> None:
        """WebSocket subscribe action returns subscribed confirmation."""
        with app_no_startup.websocket_connect("/ws/monitor") as ws:
            ws.send_text(
                json.dumps({"action": "subscribe", "patient_ids": ["P001", "P002"]})
            )
            data = json.loads(ws.receive_text())
            assert data["event"] == "subscribed"
            assert set(data["patient_ids"]) == {"P001", "P002"}

    def test_websocket_invalid_json(self, app_no_startup: TestClient) -> None:
        """WebSocket returns error for invalid JSON."""
        with app_no_startup.websocket_connect("/ws/monitor") as ws:
            ws.send_text("not-valid-json")
            data = json.loads(ws.receive_text())
            assert "error" in data
            assert "Invalid JSON" in data["error"]

    def test_websocket_unknown_action(self, app_no_startup: TestClient) -> None:
        """WebSocket returns error for unknown action."""
        with app_no_startup.websocket_connect("/ws/monitor") as ws:
            ws.send_text(json.dumps({"action": "unknown_action"}))
            data = json.loads(ws.receive_text())
            assert "error" in data
            assert "Unknown action" in data["error"]

    def test_websocket_subscribe_invalid_patient_ids(
        self, app_no_startup: TestClient
    ) -> None:
        """WebSocket returns error when patient_ids is not a list."""
        with app_no_startup.websocket_connect("/ws/monitor") as ws:
            ws.send_text(
                json.dumps({"action": "subscribe", "patient_ids": "not-a-list"})
            )
            data = json.loads(ws.receive_text())
            assert "error" in data
            assert "patient_ids must be a list" in data["error"]
