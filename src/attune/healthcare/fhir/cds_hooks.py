"""HL7 CDS Hooks v2.0 Service Endpoints.

Implements the CDS Hooks specification for EHR integration:
- Service discovery (GET /cds-services)
- Hook handlers (POST /cds-services/{id})
- Card response format with indicator/summary/suggestions

Designed for integration with Epic, Cerner, and other CDS Hooks-compatible EHRs.

See: https://cds-hooks.hl7.org/2.0/

Copyright 2026 Smart-AI-Memory
Licensed under Apache 2.0
"""

from __future__ import annotations

import logging
import uuid
from typing import Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


# ============================================================================
# Pydantic Models for CDS Hooks v2.0
# ============================================================================


class CDSHookRequest(BaseModel):
    """CDS Hooks request payload.

    Sent by the EHR when a clinical hook fires (e.g., patient chart opened,
    order signed). Contains the hook context and optionally pre-fetched FHIR
    resources.

    Attributes:
        hook: Hook that triggered (patient-view, order-sign, etc.)
        hookInstance: Unique UUID for this hook invocation
        fhirServer: Base URL of the EHR's FHIR server
        fhirAuthorization: OAuth2 token for FHIR server access
        context: Hook-specific context (e.g., patientId, encounterId)
        prefetch: Pre-fetched FHIR resources keyed by template name
    """

    hook: str = Field(..., description="Hook that triggered (patient-view, order-sign, etc.)")
    hookInstance: str = Field(..., description="Unique UUID for this hook invocation")
    fhirServer: str | None = Field(None, description="Base URL of the EHR's FHIR server")
    fhirAuthorization: dict[str, Any] | None = Field(
        None, description="OAuth2 token for FHIR server"
    )
    context: dict[str, Any] = Field(default_factory=dict, description="Hook-specific context")
    prefetch: dict[str, Any] | None = Field(None, description="Pre-fetched FHIR resources")


class CDSSource(BaseModel):
    """Source attribution for a CDS card.

    Attributes:
        label: Short display label for the source
        url: Optional URL for more information
        icon: Optional URL to an icon image
    """

    label: str = "Attune CDS"
    url: str | None = None
    icon: str | None = None


class CDSSuggestion(BaseModel):
    """Suggested action for a CDS card.

    Represents an actionable suggestion that can be auto-applied in the EHR.

    Attributes:
        label: Human-readable label for the suggestion
        uuid: Unique identifier for tracking acceptance
        isRecommended: Whether this is the recommended action
        actions: List of FHIR action resources (create, update, delete)
    """

    label: str
    uuid: str | None = None
    isRecommended: bool = False
    actions: list[dict[str, Any]] = Field(default_factory=list)


class CDSLink(BaseModel):
    """External link for a CDS card.

    Attributes:
        label: Display text for the link
        url: Target URL
        type: Link type ('absolute' or 'smart')
        appContext: Optional SMART app launch context
    """

    label: str
    url: str
    type: str = "absolute"
    appContext: str | None = None


class CDSCard(BaseModel):
    """CDS Hooks response card displayed in the EHR.

    Cards are the primary communication mechanism between CDS services and
    clinicians. Each card has an urgency indicator and actionable content.

    Attributes:
        uuid: Optional unique identifier for the card
        summary: One-sentence summary (must be <140 chars per spec)
        detail: Optional detailed markdown text
        indicator: Urgency level: 'info', 'warning', or 'critical'
        source: Attribution for this card
        suggestions: Suggested actions the clinician can take
        links: External links for more information
        overrideReasons: Reasons a clinician can select when overriding
    """

    uuid: str | None = None
    summary: str = Field(..., description="One-sentence summary (<140 chars)")
    detail: str | None = Field(None, description="Detailed markdown text")
    indicator: str = Field("info", description="Urgency: info, warning, critical")
    source: CDSSource = Field(default_factory=CDSSource)
    suggestions: list[CDSSuggestion] = Field(default_factory=list)
    links: list[CDSLink] = Field(default_factory=list)
    overrideReasons: list[dict[str, str]] | None = None


class CDSHookResponse(BaseModel):
    """CDS Hooks response payload.

    Attributes:
        cards: List of CDS cards to display in the EHR
    """

    cards: list[CDSCard] = Field(default_factory=list)


class CDSServiceDefinition(BaseModel):
    """CDS service definition returned by the discovery endpoint.

    Attributes:
        hook: The hook this service listens to
        title: Human-readable service title
        description: Human-readable description of the service
        id: Unique service identifier
        prefetch: FHIR query templates for pre-fetching resources
        usageRequirements: Optional free-text usage notes
    """

    hook: str
    title: str
    description: str
    id: str
    prefetch: dict[str, str] | None = None
    usageRequirements: str | None = None


# ============================================================================
# Service Definitions
# ============================================================================

SERVICES: dict[str, CDSServiceDefinition] = {
    "attune-patient-view": CDSServiceDefinition(
        hook="patient-view",
        title="Attune Clinical Decision Support",
        description=(
            "Provides risk assessment, protocol compliance, and clinical "
            "recommendations when a patient chart is opened."
        ),
        id="attune-patient-view",
        prefetch={
            "patient": "Patient/{{context.patientId}}",
            "observations": (
                "Observation?patient={{context.patientId}}"
                "&category=vital-signs&_sort=-date&_count=20"
            ),
        },
    ),
    "attune-order-sign": CDSServiceDefinition(
        hook="order-sign",
        title="Attune Order Review",
        description=(
            "Reviews medication and lab orders against current clinical "
            "status and protocol compliance."
        ),
        id="attune-order-sign",
        prefetch={
            "patient": "Patient/{{context.patientId}}",
            "medications": (
                "MedicationRequest?patient={{context.patientId}}&status=active"
            ),
        },
    ),
    "attune-encounter-start": CDSServiceDefinition(
        hook="encounter-start",
        title="Attune Encounter Assessment",
        description="Runs initial clinical assessment at the start of a patient encounter.",
        id="attune-encounter-start",
        prefetch={
            "patient": "Patient/{{context.patientId}}",
            "encounter": "Encounter/{{context.encounterId}}",
        },
    ),
}


# ============================================================================
# LOINC Code Mapping (matches resources.py LOINC_CODES)
# ============================================================================

_LOINC_TO_VITAL_KEY: dict[str, str] = {
    "8867-4": "hr",
    "8480-6": "systolic_bp",
    "8462-4": "diastolic_bp",
    "9279-1": "respiratory_rate",
    "8310-5": "temp_f",
    "2708-6": "o2_sat",
}


# ============================================================================
# Helper Functions
# ============================================================================


def _extract_vitals_from_prefetch(prefetch: dict[str, Any] | None) -> dict[str, Any]:
    """Extract vital signs from FHIR prefetch Observation resources.

    Parses prefetched FHIR Observation resources (Bundles or individual
    resources) and maps LOINC-coded vital signs to the flat key format
    expected by CDSTeam.assess().

    Args:
        prefetch: CDS Hooks prefetch data containing FHIR resources.
            Expected keys include 'observations' containing a FHIR Bundle
            or list of Observation resources.

    Returns:
        Dict mapping vital sign keys (hr, systolic_bp, etc.) to numeric values.
        Empty dict if no prefetch data or no parseable observations.
    """
    if not prefetch:
        return {}

    vitals: dict[str, Any] = {}

    observations_data = prefetch.get("observations", {})

    # Normalize to a list of Observation resource dicts
    entries: list[dict[str, Any]] = []
    if isinstance(observations_data, dict):
        resource_type = observations_data.get("resourceType", "")
        if resource_type == "Bundle":
            entries = [
                e.get("resource", {}) for e in observations_data.get("entry", [])
            ]
        elif resource_type == "Observation":
            entries = [observations_data]
    elif isinstance(observations_data, list):
        entries = observations_data

    for obs in entries:
        if not isinstance(obs, dict):
            continue
        coding_list = obs.get("code", {}).get("coding", [])
        for coding in coding_list:
            loinc_code = coding.get("code", "")
            vital_key = _LOINC_TO_VITAL_KEY.get(loinc_code)
            if vital_key is not None:
                value_quantity = obs.get("valueQuantity", {})
                if "value" in value_quantity:
                    vitals[vital_key] = value_quantity["value"]

    return vitals


def _risk_to_indicator(risk_level: str) -> str:
    """Map CDS risk level to CDS Hooks card indicator.

    Args:
        risk_level: Overall risk from CDSDecision
            (low, moderate, high, critical).

    Returns:
        CDS Hooks indicator string: 'info', 'warning', or 'critical'.
    """
    mapping: dict[str, str] = {
        "critical": "critical",
        "high": "warning",
        "moderate": "info",
        "low": "info",
    }
    return mapping.get(risk_level, "info")


def _build_cards_from_decision(decision: Any) -> list[CDSCard]:
    """Convert a CDSDecision to CDS Hooks response cards.

    Produces one or more cards from a CDSDecision object:
    - A primary assessment card with risk, reasoning, and recommendations
    - Individual alert cards for each clinical alert
    - An ECG analysis card if ECG data was processed

    Args:
        decision: CDSDecision object from CDSTeam.assess().

    Returns:
        List of CDSCard objects ready for CDS Hooks response.
    """
    cards: list[CDSCard] = []

    # ------------------------------------------------------------------
    # Primary assessment card
    # ------------------------------------------------------------------
    risk = getattr(decision, "overall_risk", "low")
    indicator = _risk_to_indicator(risk)

    # Build summary (<140 chars per CDS Hooks spec)
    summary = f"Patient risk: {risk.upper()}"
    if decision.clinical_reasoning and decision.clinical_reasoning.narrative_summary:
        summary = decision.clinical_reasoning.narrative_summary[:140]

    # Build detail markdown
    detail_parts: list[str] = []
    if decision.clinical_reasoning:
        detail_parts.append(f"**Risk Level:** {risk.upper()}")
        detail_parts.append(f"**Confidence:** {decision.confidence:.0%}")
        detail_parts.append("")
        detail_parts.append(decision.clinical_reasoning.narrative_summary)

        if decision.clinical_reasoning.differentials:
            detail_parts.append("")
            detail_parts.append("**Differential Considerations:**")
            for diff in decision.clinical_reasoning.differentials:
                detail_parts.append(f"- {diff}")

    # Build suggestions from recommendations (max 5 per CDS Hooks UX guidance)
    suggestions: list[CDSSuggestion] = []
    for rec in (decision.recommendations or [])[:5]:
        suggestions.append(
            CDSSuggestion(
                label=rec,
                uuid=str(uuid.uuid4()),
            )
        )

    cards.append(
        CDSCard(
            uuid=str(uuid.uuid4()),
            summary=summary,
            detail="\n".join(detail_parts) if detail_parts else None,
            indicator=indicator,
            source=CDSSource(label="Attune CDS", url="https://smartaimemory.com"),
            suggestions=suggestions,
        )
    )

    # ------------------------------------------------------------------
    # Alert cards
    # ------------------------------------------------------------------
    for alert in decision.alerts or []:
        alert_indicator = "warning" if "ECG" in alert else "info"
        cards.append(
            CDSCard(
                uuid=str(uuid.uuid4()),
                summary=alert[:140],
                indicator=alert_indicator,
                source=CDSSource(label="Attune CDS"),
            )
        )

    # ------------------------------------------------------------------
    # ECG analysis card
    # ------------------------------------------------------------------
    if decision.ecg_analysis is not None:
        ecg = decision.ecg_analysis
        ecg_summary = (
            f"ECG: {ecg.rhythm_classification.replace('_', ' ').title()}, "
            f"HR {ecg.heart_rate:.0f} bpm"
        )[:140]

        ecg_detail_parts = [
            f"**Rhythm:** {ecg.rhythm_classification.replace('_', ' ').title()}",
            f"**Heart Rate:** {ecg.heart_rate:.0f} bpm",
            f"**PVC Burden:** {ecg.pvc_burden_pct:.1f}%",
            f"**HRV (SDNN):** {ecg.hrv_sdnn:.0f} ms",
        ]
        if ecg.clinical_flags:
            ecg_detail_parts.append(f"**Flags:** {', '.join(ecg.clinical_flags)}")

        ecg_indicator = "warning" if ecg.clinical_flags else "info"
        cards.append(
            CDSCard(
                uuid=str(uuid.uuid4()),
                summary=ecg_summary,
                detail="\n".join(ecg_detail_parts),
                indicator=ecg_indicator,
                source=CDSSource(label="Attune ECG Analysis"),
            )
        )

    return cards


# ============================================================================
# Router Factory
# ============================================================================


def create_cds_hooks_router() -> APIRouter:
    """Create the CDS Hooks v2.0 API router.

    Returns an APIRouter with two endpoints:

    - ``GET /cds-services`` -- Discovery endpoint listing available CDS services
    - ``POST /cds-services/{service_id}`` -- Hook handler that runs CDS
      assessment and returns cards

    Returns:
        FastAPI APIRouter with CDS Hooks endpoints mounted.
    """
    router = APIRouter(tags=["CDS Hooks"])

    @router.get("/cds-services")
    async def service_discovery() -> dict[str, list[dict[str, Any]]]:
        """CDS Hooks service discovery endpoint.

        Returns the list of available CDS services per the CDS Hooks v2.0
        specification. EHRs call this endpoint to learn which hooks this
        service supports and what FHIR resources to prefetch.

        Returns:
            Dict with 'services' key containing list of service definitions.
        """
        return {
            "services": [svc.model_dump(exclude_none=True) for svc in SERVICES.values()]
        }

    @router.post("/cds-services/{service_id}")
    async def handle_hook(service_id: str, request: CDSHookRequest) -> dict[str, Any]:
        """Handle a CDS Hooks invocation.

        Receives hook context from the EHR, extracts patient data from
        prefetch, runs the CDSTeam assessment pipeline, and returns CDS
        cards for display to the clinician.

        Args:
            service_id: Identifier of the CDS service to invoke.
            request: CDS Hooks request payload with context and prefetch.

        Returns:
            CDS Hooks response dict with 'cards' list.

        Raises:
            HTTPException: 404 if service_id is not registered.
        """
        if service_id not in SERVICES:
            raise HTTPException(
                status_code=404,
                detail=f"Unknown service: {service_id}",
            )

        # Extract patient ID from hook context
        patient_id = request.context.get("patientId", "unknown")

        # Extract vitals from prefetched FHIR Observations
        vitals = _extract_vitals_from_prefetch(request.prefetch)

        # Map service to clinical protocol
        protocol_map: dict[str, str] = {
            "attune-patient-view": "cardiac",
            "attune-order-sign": "cardiac",
            "attune-encounter-start": "cardiac",
        }
        protocol_name = protocol_map.get(service_id, "cardiac")

        # If no vitals in prefetch, return informational card
        if not vitals:
            return CDSHookResponse(
                cards=[
                    CDSCard(
                        uuid=str(uuid.uuid4()),
                        summary="No recent vital signs available for assessment",
                        indicator="info",
                        source=CDSSource(label="Attune CDS"),
                    )
                ]
            ).model_dump()

        # Run CDS assessment pipeline
        try:
            from attune.agents.healthcare.cds_team import CDSTeam

            team = CDSTeam()
            decision = await team.assess(
                patient_id=patient_id,
                sensor_data=vitals,
                protocol_name=protocol_name,
            )

            cards = _build_cards_from_decision(decision)
            return CDSHookResponse(cards=cards).model_dump()

        except ImportError as e:
            logger.error(f"CDS team import failed: {e}")
            return CDSHookResponse(
                cards=[
                    CDSCard(
                        uuid=str(uuid.uuid4()),
                        summary="CDS assessment module not available",
                        indicator="info",
                        source=CDSSource(label="Attune CDS"),
                    )
                ]
            ).model_dump()
        except Exception as e:  # noqa: BLE001
            # INTENTIONAL: CDS Hooks spec requires returning a valid response
            # even on internal errors. EHR systems expect a 200 with empty/info
            # cards rather than a 500 error which would disrupt clinical workflow.
            logger.exception(f"CDS Hooks assessment failed for patient {patient_id}: {e}")
            return CDSHookResponse(
                cards=[
                    CDSCard(
                        uuid=str(uuid.uuid4()),
                        summary="CDS assessment temporarily unavailable",
                        indicator="info",
                        source=CDSSource(label="Attune CDS"),
                    )
                ]
            ).model_dump()

    return router
