"""Pydantic models for Nurse Dashboard API.

Request/response schemas for the clinical decision support
nurse dashboard REST API. Uses Pydantic v2 BaseModel for
automatic validation and OpenAPI schema generation.

Copyright 2026 Smart-AI-Memory
Licensed under Apache 2.0
"""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field

# =============================================================================
# Request Models
# =============================================================================


class AssessRequest(BaseModel):
    """Request body for patient assessment.

    Attributes:
        sensor_data: Vital signs dict (hr, systolic_bp, diastolic_bp,
            respiratory_rate, temp_f, o2_sat, pain_score).
        protocol_name: Clinical protocol to assess against
            (cardiac, sepsis, respiratory, post_operative).
        ecg_metrics: Optional ECG metrics from PhysioNet waveform analysis.
        patient_context: Optional patient demographics, medications, history.
    """

    sensor_data: dict[str, Any] = Field(
        ...,
        description="Vital signs dict (hr, systolic_bp, respiratory_rate, temp_f, o2_sat, etc.)",
    )
    protocol_name: str = Field(
        ...,
        description="Protocol to assess (cardiac, sepsis, respiratory, post_operative)",
    )
    ecg_metrics: dict[str, Any] | None = Field(
        None,
        description="Optional ECG metrics from waveform analysis",
    )
    patient_context: dict[str, Any] | None = Field(
        None,
        description="Optional patient demographics, medications, and history",
    )


# =============================================================================
# Response Models
# =============================================================================


class AssessResponse(BaseModel):
    """Response from patient assessment.

    Attributes:
        patient_id: Patient identifier from the URL path.
        overall_risk: Risk level (low, moderate, high, critical).
        confidence: Overall confidence score (0.0-1.0).
        alerts: List of clinical alert messages.
        recommendations: List of clinical recommendations.
        clinical_reasoning: Optional narrative summary and differentials.
        ecg_analysis: Optional ECG analysis results.
        quality_gates: Quality gate evaluation results.
        cost: Total LLM API cost in USD.
        timestamp: Assessment timestamp (ISO 8601).
    """

    patient_id: str
    overall_risk: str
    confidence: float
    alerts: list[str]
    recommendations: list[str]
    clinical_reasoning: dict[str, Any] | None = None
    ecg_analysis: dict[str, Any] | None = None
    quality_gates: list[dict[str, Any]] = Field(default_factory=list)
    cost: float = 0.0
    timestamp: str = ""


class PatientSummary(BaseModel):
    """Summary of a patient's current status.

    Attributes:
        patient_id: Patient identifier.
        latest_risk: Most recent risk level.
        protocol_status: Current protocol compliance status.
        last_updated: Timestamp of last assessment.
        alert_count: Number of active alerts.
    """

    patient_id: str
    latest_risk: str = "unknown"
    protocol_status: str = ""
    last_updated: str = ""
    alert_count: int = 0


class AuditEntry(BaseModel):
    """Audit trail entry summary.

    Attributes:
        decision_id: UUID of the audit entry.
        timestamp: When the decision was made (ISO 8601).
        patient_id_hash: SHA256 hash of the patient ID (HIPAA).
        overall_risk: Risk level at time of decision.
        confidence: Confidence score at time of decision.
        cost: LLM API cost for this decision.
    """

    decision_id: str
    timestamp: str
    patient_id_hash: str
    overall_risk: str
    confidence: float = 0.0
    cost: float = 0.0


class HealthResponse(BaseModel):
    """Health check response.

    Attributes:
        status: Service health status (healthy, degraded, unhealthy).
        service: Service identifier.
        version: Application version.
        redis_connected: Whether Redis is available.
        uptime_seconds: Seconds since server startup.
    """

    status: str = "healthy"
    service: str = "attune-nurse-dashboard"
    version: str = "2.5.0"
    redis_connected: bool = False
    uptime_seconds: float = 0.0


class ProtocolInfo(BaseModel):
    """Protocol information for the protocol listing endpoint.

    Attributes:
        name: Internal protocol identifier.
        display_name: Human-readable protocol name.
        description: Brief description of what the protocol monitors.
    """

    name: str
    display_name: str
    description: str
