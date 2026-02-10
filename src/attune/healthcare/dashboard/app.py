"""Nurse Dashboard FastAPI Application.

Standalone web server for nurse bedside monitoring with:
- REST API for patient assessments and audit trail
- WebSocket for real-time patient updates and alerts
- FHIR Bundle generation for interoperability
- Static file serving for the frontend UI

Follows the same patterns as the developer dashboard at
``src/attune/dashboard/app.py`` (FastAPI + WebSocket ConnectionManager).

Copyright 2026 Smart-AI-Memory
Licensed under Apache 2.0
"""

from __future__ import annotations

import json
import logging
import time
from pathlib import Path
from typing import Any

from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles

from .models import (
    AssessRequest,
    AssessResponse,
    HealthResponse,
    ProtocolInfo,
)
from .websocket import NurseWebSocketManager

logger = logging.getLogger(__name__)

# =============================================================================
# Protocol Registry
# =============================================================================

PROTOCOLS: dict[str, ProtocolInfo] = {
    "cardiac": ProtocolInfo(
        name="cardiac",
        display_name="Cardiac Monitoring",
        description="Acute coronary syndrome, heart failure, arrhythmia monitoring",
    ),
    "sepsis": ProtocolInfo(
        name="sepsis",
        display_name="Sepsis Screening",
        description="qSOFA-based sepsis screening with early warning",
    ),
    "respiratory": ProtocolInfo(
        name="respiratory",
        display_name="Respiratory Distress",
        description="Respiratory failure, PE, COPD exacerbation monitoring",
    ),
    "post_operative": ProtocolInfo(
        name="post_operative",
        display_name="Post-Operative Care",
        description="Surgical site monitoring, VTE prevention, wound care",
    ),
}


# =============================================================================
# Application Factory
# =============================================================================


def create_nurse_app(redis_url: str | None = None) -> FastAPI:
    """Create the nurse dashboard FastAPI application.

    Uses the factory pattern so tests can create isolated app instances.
    Initializes CDS team and audit logger on startup and wires up all
    REST, WebSocket, and static-file endpoints.

    Args:
        redis_url: Optional Redis URL for coordination and pub/sub.
            When None, the dashboard operates without Redis (degraded mode).

    Returns:
        Configured FastAPI application ready for ``uvicorn.run()``.
    """
    app = FastAPI(
        title="Attune Nurse Dashboard",
        description="Clinical Decision Support monitoring for bedside nurses",
        version="2.5.0",
    )

    # CORS middleware for browser access
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Shared state
    ws_manager = NurseWebSocketManager()
    start_time = time.time()
    redis_client: Any = None
    audit_logger: Any = None
    cds_team: Any = None

    # -----------------------------------------------------------------
    # Lifecycle
    # -----------------------------------------------------------------

    @app.on_event("startup")
    async def startup() -> None:
        """Initialize Redis, audit logger, and CDS team on server start."""
        nonlocal redis_client, audit_logger, cds_team

        # Redis (optional)
        if redis_url:
            try:
                import redis as _redis_lib

                redis_client = _redis_lib.from_url(redis_url)
                redis_client.ping()
                logger.info("Nurse dashboard connected to Redis")
            except ImportError:
                logger.info("redis package not installed -- running without Redis")
                redis_client = None
            except ConnectionError as e:
                logger.info(f"Redis connection failed (non-fatal): {e}")
                redis_client = None
            except OSError as e:
                logger.info(f"Redis not reachable (non-fatal): {e}")
                redis_client = None

        # Audit logger
        try:
            from attune.healthcare.audit.decision_log import CDSAuditLogger

            audit_logger = CDSAuditLogger(redis_client=redis_client)
            logger.info("CDS audit logger initialized")
        except ImportError:
            logger.warning("CDSAuditLogger not available -- audit trail disabled")
        except OSError as e:
            logger.error(f"Audit logger initialization failed: {e}")

        # CDS team
        try:
            from attune.agents.healthcare.cds_team import CDSTeam

            cds_team = CDSTeam(audit_logger=audit_logger, redis_url=redis_url)
            logger.info("CDS team initialized")
        except ImportError:
            logger.warning("CDSTeam not available -- assessments disabled")
        except Exception as e:  # noqa: BLE001
            # INTENTIONAL: CDS team init may fail for many reasons (missing
            # config, bad Redis, etc.) but the dashboard should still serve
            # audit/health endpoints.
            logger.error(f"CDS team initialization failed: {e}")

    # -----------------------------------------------------------------
    # Health
    # -----------------------------------------------------------------

    @app.get("/api/health", response_model=HealthResponse)
    async def health() -> HealthResponse:
        """Return service health status.

        Returns:
            HealthResponse with uptime, Redis connectivity, and version.
        """
        return HealthResponse(
            redis_connected=redis_client is not None,
            uptime_seconds=round(time.time() - start_time, 1),
        )

    # -----------------------------------------------------------------
    # Protocols
    # -----------------------------------------------------------------

    @app.get("/api/protocols")
    async def list_protocols() -> list[ProtocolInfo]:
        """List available clinical protocols.

        Returns:
            List of ProtocolInfo objects describing each supported protocol.
        """
        return list(PROTOCOLS.values())

    # -----------------------------------------------------------------
    # Assessment
    # -----------------------------------------------------------------

    @app.post("/api/patients/{patient_id}/assess", response_model=AssessResponse)
    async def assess_patient(patient_id: str, request: AssessRequest) -> AssessResponse:
        """Run a CDS assessment for a patient.

        Delegates to CDSTeam.assess(), converts the CDSDecision to an
        AssessResponse, broadcasts updates to WebSocket subscribers, and
        sends global alerts for high/critical risk.

        Args:
            patient_id: Patient identifier (URL path parameter).
            request: Assessment request body with sensor data and protocol.

        Returns:
            AssessResponse with risk, alerts, recommendations, and quality gates.

        Raises:
            HTTPException: 503 if CDS team not initialized, 500 on assessment failure.
        """
        if cds_team is None:
            raise HTTPException(
                status_code=503,
                detail="CDS team not initialized. Check server logs.",
            )

        try:
            decision = await cds_team.assess(
                patient_id=patient_id,
                sensor_data=request.sensor_data,
                protocol_name=request.protocol_name,
                ecg_metrics=request.ecg_metrics,
                patient_context=request.patient_context,
            )
        except ValueError as e:
            logger.error(f"Assessment validation error for {patient_id}: {e}")
            raise HTTPException(status_code=422, detail=f"Invalid input: {e}")
        except ConnectionError as e:
            logger.error(f"Assessment connection error for {patient_id}: {e}")
            raise HTTPException(status_code=502, detail=f"Upstream connection error: {e}")
        except Exception as e:
            logger.error(f"Assessment failed for {patient_id}: {e}")
            raise HTTPException(status_code=500, detail=f"Assessment failed: {e}")

        # Build clinical_reasoning dict from ClinicalReasoningResult
        reasoning_dict: dict[str, Any] | None = None
        if decision.clinical_reasoning is not None:
            reasoning_dict = {
                "narrative_summary": decision.clinical_reasoning.narrative_summary,
                "differentials": decision.clinical_reasoning.differentials,
                "recommended_workup": decision.clinical_reasoning.recommended_workup,
                "risk_level": decision.clinical_reasoning.risk_level,
                "confidence": decision.clinical_reasoning.confidence,
            }

        # Build ecg_analysis dict from ECGAnalysisResult
        ecg_dict: dict[str, Any] | None = None
        if decision.ecg_analysis is not None:
            ecg_dict = {
                "heart_rate": decision.ecg_analysis.heart_rate,
                "hrv_sdnn": decision.ecg_analysis.hrv_sdnn,
                "rhythm_classification": decision.ecg_analysis.rhythm_classification,
                "arrhythmia_events": decision.ecg_analysis.arrhythmia_events,
                "pvc_burden_pct": decision.ecg_analysis.pvc_burden_pct,
                "clinical_flags": decision.ecg_analysis.clinical_flags,
                "confidence": decision.ecg_analysis.confidence,
                "score": decision.ecg_analysis.score,
            }

        response = AssessResponse(
            patient_id=decision.patient_id,
            overall_risk=decision.overall_risk,
            confidence=decision.confidence,
            alerts=decision.alerts,
            recommendations=decision.recommendations,
            clinical_reasoning=reasoning_dict,
            ecg_analysis=ecg_dict,
            quality_gates=[
                {
                    "name": g.name,
                    "passed": g.passed,
                    "actual": g.actual,
                    "threshold": g.threshold,
                }
                for g in decision.quality_gates
            ],
            cost=decision.cost,
            timestamp=decision.timestamp,
        )

        # Broadcast to WebSocket subscribers for this patient
        await ws_manager.broadcast_to_patient(
            patient_id,
            {
                "event": "new_assessment",
                "data": response.model_dump(),
            },
        )

        # Broadcast global alert for high/critical risk
        if decision.overall_risk in ("high", "critical"):
            await ws_manager.broadcast_alert(
                {
                    "patient_id": patient_id,
                    "risk": decision.overall_risk,
                    "alerts": decision.alerts,
                }
            )

        return response

    # -----------------------------------------------------------------
    # Decision History
    # -----------------------------------------------------------------

    @app.get("/api/patients/{patient_id}/history")
    async def patient_history(
        patient_id: str, limit: int = 20
    ) -> list[dict[str, Any]]:
        """Get assessment history for a patient.

        Args:
            patient_id: Patient identifier (URL path parameter).
            limit: Maximum number of decisions to return (default 20).

        Returns:
            List of decision dicts, most recent first. Empty list if
            audit logger is not available.
        """
        if audit_logger is None:
            return []
        try:
            return audit_logger.list_decisions(patient_id=patient_id, limit=limit)
        except OSError as e:
            logger.error(f"Failed to read patient history: {e}")
            return []

    # -----------------------------------------------------------------
    # Single Decision
    # -----------------------------------------------------------------

    @app.get("/api/decisions/{decision_id}")
    async def get_decision(decision_id: str) -> dict[str, Any]:
        """Retrieve a single decision by its UUID.

        Args:
            decision_id: UUID of the audit entry.

        Returns:
            Full decision dict from the audit trail.

        Raises:
            HTTPException: 503 if audit logger not initialized, 404 if not found.
        """
        if audit_logger is None:
            raise HTTPException(
                status_code=503, detail="Audit logger not initialized"
            )
        try:
            result = audit_logger.get_decision(decision_id)
        except OSError as e:
            logger.error(f"Failed to read decision {decision_id}: {e}")
            raise HTTPException(status_code=500, detail="Failed to read audit log")

        if result is None:
            raise HTTPException(status_code=404, detail="Decision not found")
        return result

    # -----------------------------------------------------------------
    # FHIR Bundle
    # -----------------------------------------------------------------

    @app.get("/api/decisions/{decision_id}/fhir")
    async def get_fhir_bundle(decision_id: str) -> dict[str, Any]:
        """Get a minimal FHIR R4 Bundle for a decision.

        Builds a Bundle containing a RiskAssessment resource from the
        stored audit entry. For full FHIR Bundles with Observations,
        ClinicalImpression, and DiagnosticReport, use
        ``decision_to_fhir_bundle()`` with the original CDSDecision object.

        Args:
            decision_id: UUID of the audit entry.

        Returns:
            FHIR R4 Bundle dict (JSON-serializable).

        Raises:
            HTTPException: 503 if audit logger not initialized, 404 if not found.
        """
        if audit_logger is None:
            raise HTTPException(
                status_code=503, detail="Audit logger not initialized"
            )

        try:
            entry = audit_logger.get_decision(decision_id)
        except OSError as e:
            logger.error(f"Failed to read decision for FHIR: {e}")
            raise HTTPException(status_code=500, detail="Failed to read audit log")

        if entry is None:
            raise HTTPException(status_code=404, detail="Decision not found")

        # Build minimal FHIR Bundle from stored audit data
        from attune.healthcare.fhir.resources import _make_id, _make_meta, _now_iso

        risk_id = _make_id()
        return {
            "resourceType": "Bundle",
            "id": _make_id(),
            "meta": _make_meta(),
            "type": "collection",
            "timestamp": _now_iso(),
            "entry": [
                {
                    "resource": {
                        "resourceType": "RiskAssessment",
                        "id": risk_id,
                        "meta": _make_meta(),
                        "status": "final",
                        "prediction": [
                            {
                                "outcome": {
                                    "text": (
                                        f"Clinical risk: "
                                        f"{entry.get('overall_risk', 'unknown')}"
                                    ),
                                },
                            }
                        ],
                    },
                    "fullUrl": f"urn:uuid:{risk_id}",
                }
            ],
        }

    # -----------------------------------------------------------------
    # Audit Trail
    # -----------------------------------------------------------------

    @app.get("/api/audit")
    async def audit_trail(
        limit: int = 50, offset: int = 0
    ) -> list[dict[str, Any]]:
        """Get paginated audit trail of all CDS decisions.

        Args:
            limit: Maximum number of entries to return (default 50).
            offset: Number of entries to skip (default 0).

        Returns:
            List of decision dicts. Empty list if audit logger unavailable.
        """
        if audit_logger is None:
            return []
        try:
            all_decisions = audit_logger.list_decisions(limit=limit + offset)
            return all_decisions[offset : offset + limit]
        except OSError as e:
            logger.error(f"Failed to read audit trail: {e}")
            return []

    # -----------------------------------------------------------------
    # WebSocket
    # -----------------------------------------------------------------

    @app.websocket("/ws/monitor")
    async def websocket_monitor(websocket: WebSocket) -> None:
        """WebSocket endpoint for real-time patient monitoring.

        Accepts JSON messages with the following actions:

        - ``{"action": "subscribe", "patient_ids": ["P001", "P002"]}``
          -- Subscribe to updates for specific patients.
        - ``{"action": "ping"}``
          -- Heartbeat, server replies with ``{"event": "pong"}``.

        The server pushes ``new_assessment`` events when assessments
        complete and ``alert`` events for high/critical risk patients.

        Args:
            websocket: The incoming WebSocket connection.
        """
        await ws_manager.connect(websocket)
        try:
            while True:
                data = await websocket.receive_text()
                try:
                    message = json.loads(data)
                except json.JSONDecodeError:
                    await websocket.send_text(
                        json.dumps({"error": "Invalid JSON"})
                    )
                    continue

                action = message.get("action")

                if action == "subscribe":
                    patient_ids = message.get("patient_ids", [])
                    if not isinstance(patient_ids, list):
                        await websocket.send_text(
                            json.dumps({"error": "patient_ids must be a list"})
                        )
                        continue
                    await ws_manager.subscribe(websocket, patient_ids)
                    await websocket.send_text(
                        json.dumps(
                            {
                                "event": "subscribed",
                                "patient_ids": patient_ids,
                            }
                        )
                    )
                elif action == "ping":
                    await websocket.send_text(json.dumps({"event": "pong"}))
                else:
                    await websocket.send_text(
                        json.dumps({"error": f"Unknown action: {action}"})
                    )

        except WebSocketDisconnect:
            await ws_manager.disconnect(websocket)

    # -----------------------------------------------------------------
    # Static Files & Frontend
    # -----------------------------------------------------------------

    static_dir = Path(__file__).parent / "static"
    if static_dir.exists():
        app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

        @app.get("/", response_class=HTMLResponse)
        async def serve_index() -> HTMLResponse:
            """Serve the dashboard frontend.

            Returns:
                HTML content of the index page, or a fallback message
                if the frontend is not installed.
            """
            index_file = static_dir / "index.html"
            if index_file.exists():
                return HTMLResponse(content=index_file.read_text())
            return HTMLResponse(
                content=(
                    "<html><head><title>Nurse Dashboard</title></head>"
                    "<body><h1>Nurse Dashboard</h1>"
                    "<p>Frontend not installed. "
                    "API docs available at <a href='/docs'>/docs</a>.</p>"
                    "</body></html>"
                )
            )

    return app


# =============================================================================
# Server Runner
# =============================================================================


def run_nurse_dashboard(
    host: str = "0.0.0.0",
    port: int = 8080,
    redis_url: str | None = None,
) -> None:
    """Run the nurse dashboard server.

    Creates the FastAPI application and starts it with uvicorn.

    Args:
        host: Network interface to bind to (default "0.0.0.0").
        port: Port number to listen on (default 8080).
        redis_url: Optional Redis URL for coordination and pub/sub.

    Example:
        >>> from attune.healthcare.dashboard import run_nurse_dashboard
        >>> run_nurse_dashboard(host="127.0.0.1", port=8080)
    """
    import uvicorn

    app = create_nurse_app(redis_url=redis_url)
    logger.info(f"Starting nurse dashboard at http://{host}:{port}")
    uvicorn.run(app, host=host, port=port)
