"""FHIR R4 Resource Builders.

Pure Python dict builders that convert CDSDecision components to FHIR R4
JSON resources. No external FHIR library required — optional validation
with fhir.resources if installed.

LOINC codes sourced from attune_healthcare.monitors.monitoring.sensor_parsers
FHIRObservationParser.LOINC_MAPPINGS for roundtrip compatibility.

Copyright 2026 Smart-AI-Memory
Licensed under Apache 2.0
"""

from __future__ import annotations

import logging
import uuid
from datetime import datetime, timezone
from typing import Any

logger = logging.getLogger(__name__)

# LOINC codes for vital signs and ECG metrics
# Matches sensor_parsers.py FHIRObservationParser.LOINC_MAPPINGS
LOINC_CODES: dict[str, dict[str, str]] = {
    "hr": {"code": "8867-4", "display": "Heart rate", "unit": "/min"},
    "systolic_bp": {"code": "8480-6", "display": "Systolic blood pressure", "unit": "mmHg"},
    "diastolic_bp": {"code": "8462-4", "display": "Diastolic blood pressure", "unit": "mmHg"},
    "respiratory_rate": {"code": "9279-1", "display": "Respiratory rate", "unit": "/min"},
    "temp_f": {"code": "8310-5", "display": "Body temperature", "unit": "degF"},
    "o2_sat": {"code": "2708-6", "display": "Oxygen saturation", "unit": "%"},
    "pain_score": {"code": "38208-5", "display": "Pain severity", "unit": "{score}"},
    # ECG-specific LOINC codes
    "ecg_hr": {"code": "76282-3", "display": "Heart rate by ECG", "unit": "/min"},
    "hrv_sdnn": {"code": "80404-7", "display": "Heart rate variability SDNN", "unit": "ms"},
    "pvc_burden": {"code": "8897-1", "display": "PVC burden", "unit": "%"},
}

FHIR_SYSTEM_LOINC = "http://loinc.org"
FHIR_SYSTEM_OBSERVATION_CATEGORY = (
    "http://terminology.hl7.org/CodeSystem/observation-category"
)
FHIR_SYSTEM_UNITS = "http://unitsofmeasure.org"


def _make_id() -> str:
    """Generate a FHIR-compatible resource ID."""
    return str(uuid.uuid4())


def _now_iso() -> str:
    """Get current UTC timestamp in ISO format."""
    return datetime.now(tz=timezone.utc).isoformat()


def _make_meta() -> dict[str, str]:
    """Create FHIR resource meta element."""
    return {"lastUpdated": _now_iso()}


def _make_patient_ref(patient_id: str) -> dict[str, str]:
    """Create FHIR patient reference."""
    return {"reference": f"Patient/{patient_id}"}


def build_observations(decision: Any) -> list[dict[str, Any]]:
    """Build FHIR Observation resources from a CDSDecision.

    Creates one Observation per vital sign present in protocol_compliance
    and one per ECG metric if ECG analysis is available.

    Args:
        decision: CDSDecision object

    Returns:
        List of FHIR R4 Observation resource dicts
    """
    observations: list[dict[str, Any]] = []
    patient_ref = _make_patient_ref(decision.patient_id)
    timestamp = _now_iso()

    # Vital sign observations from protocol compliance
    vitals = decision.protocol_compliance.get("current_vitals", {})
    if not vitals and hasattr(decision, "trajectory"):
        # Fallback: try to extract from trajectory trends
        vitals = {}

    for vital_key, loinc_info in LOINC_CODES.items():
        if vital_key in vitals:
            value = vitals[vital_key]
            if value is None:
                continue

            obs = {
                "resourceType": "Observation",
                "id": _make_id(),
                "meta": _make_meta(),
                "status": "final",
                "category": [
                    {
                        "coding": [
                            {
                                "system": FHIR_SYSTEM_OBSERVATION_CATEGORY,
                                "code": "vital-signs",
                                "display": "Vital Signs",
                            }
                        ]
                    }
                ],
                "code": {
                    "coding": [
                        {
                            "system": FHIR_SYSTEM_LOINC,
                            "code": loinc_info["code"],
                            "display": loinc_info["display"],
                        }
                    ]
                },
                "subject": patient_ref,
                "effectiveDateTime": timestamp,
                "valueQuantity": {
                    "value": float(value),
                    "unit": loinc_info["unit"],
                    "system": FHIR_SYSTEM_UNITS,
                    "code": loinc_info["unit"],
                },
            }
            observations.append(obs)

    # ECG observations
    if decision.ecg_analysis is not None:
        ecg = decision.ecg_analysis

        # Heart rate from ECG
        if ecg.heart_rate:
            observations.append({
                "resourceType": "Observation",
                "id": _make_id(),
                "meta": _make_meta(),
                "status": "final",
                "category": [
                    {
                        "coding": [
                            {
                                "system": FHIR_SYSTEM_OBSERVATION_CATEGORY,
                                "code": "vital-signs",
                                "display": "Vital Signs",
                            }
                        ]
                    }
                ],
                "code": {
                    "coding": [
                        {
                            "system": FHIR_SYSTEM_LOINC,
                            "code": "76282-3",
                            "display": "Heart rate by ECG",
                        }
                    ]
                },
                "subject": patient_ref,
                "effectiveDateTime": timestamp,
                "valueQuantity": {
                    "value": float(ecg.heart_rate),
                    "unit": "/min",
                    "system": FHIR_SYSTEM_UNITS,
                    "code": "/min",
                },
            })

        # HRV SDNN
        if ecg.hrv_sdnn:
            observations.append({
                "resourceType": "Observation",
                "id": _make_id(),
                "meta": _make_meta(),
                "status": "final",
                "category": [
                    {
                        "coding": [
                            {
                                "system": FHIR_SYSTEM_OBSERVATION_CATEGORY,
                                "code": "vital-signs",
                                "display": "Vital Signs",
                            }
                        ]
                    }
                ],
                "code": {
                    "coding": [
                        {
                            "system": FHIR_SYSTEM_LOINC,
                            "code": "80404-7",
                            "display": "Heart rate variability SDNN",
                        }
                    ]
                },
                "subject": patient_ref,
                "effectiveDateTime": timestamp,
                "valueQuantity": {
                    "value": float(ecg.hrv_sdnn),
                    "unit": "ms",
                    "system": FHIR_SYSTEM_UNITS,
                    "code": "ms",
                },
            })

        # PVC burden
        if ecg.pvc_burden_pct is not None:
            observations.append({
                "resourceType": "Observation",
                "id": _make_id(),
                "meta": _make_meta(),
                "status": "final",
                "category": [
                    {
                        "coding": [
                            {
                                "system": FHIR_SYSTEM_OBSERVATION_CATEGORY,
                                "code": "vital-signs",
                                "display": "Vital Signs",
                            }
                        ]
                    }
                ],
                "code": {
                    "coding": [
                        {
                            "system": FHIR_SYSTEM_LOINC,
                            "code": "8897-1",
                            "display": "PVC burden",
                        }
                    ]
                },
                "subject": patient_ref,
                "effectiveDateTime": timestamp,
                "valueQuantity": {
                    "value": float(ecg.pvc_burden_pct),
                    "unit": "%",
                    "system": FHIR_SYSTEM_UNITS,
                    "code": "%",
                },
            })

    return observations


# Risk level to probability mapping
RISK_PROBABILITY: dict[str, float] = {
    "critical": 0.95,
    "high": 0.75,
    "moderate": 0.45,
    "low": 0.15,
}


def build_risk_assessment(decision: Any) -> dict[str, Any]:
    """Build FHIR RiskAssessment from a CDSDecision.

    Args:
        decision: CDSDecision object

    Returns:
        FHIR R4 RiskAssessment resource dict
    """
    risk_level = getattr(decision, "overall_risk", "low")
    probability = RISK_PROBABILITY.get(risk_level, 0.15)

    narrative = ""
    if decision.clinical_reasoning is not None:
        narrative = decision.clinical_reasoning.narrative_summary

    return {
        "resourceType": "RiskAssessment",
        "id": _make_id(),
        "meta": _make_meta(),
        "status": "final",
        "subject": _make_patient_ref(decision.patient_id),
        "occurrenceDateTime": _now_iso(),
        "method": {
            "text": "Attune CDS Multi-Agent Assessment",
        },
        "prediction": [
            {
                "outcome": {
                    "text": f"Clinical risk: {risk_level}",
                },
                "probabilityDecimal": probability,
                "rationale": narrative,
            }
        ],
        "mitigation": "; ".join(decision.recommendations) if decision.recommendations else None,
    }


def build_clinical_impression(decision: Any) -> dict[str, Any]:
    """Build FHIR ClinicalImpression from a CDSDecision.

    Args:
        decision: CDSDecision object

    Returns:
        FHIR R4 ClinicalImpression resource dict
    """
    cr = decision.clinical_reasoning
    findings = []

    if cr is not None:
        for diff in cr.differentials:
            findings.append({
                "itemCodeableConcept": {"text": diff},
            })

    return {
        "resourceType": "ClinicalImpression",
        "id": _make_id(),
        "meta": _make_meta(),
        "status": "completed",
        "subject": _make_patient_ref(decision.patient_id),
        "effectiveDateTime": _now_iso(),
        "summary": cr.narrative_summary if cr else "No clinical reasoning available",
        "finding": findings,
        "protocol": [f"urn:attune:protocol:{decision.protocol_compliance.get('protocol_name', 'unknown')}"],
    }


def build_diagnostic_report(
    decision: Any,
    observation_refs: list[str] | None = None,
) -> dict[str, Any]:
    """Build FHIR DiagnosticReport wrapping all Observations.

    Args:
        decision: CDSDecision object
        observation_refs: List of Observation resource IDs to reference

    Returns:
        FHIR R4 DiagnosticReport resource dict
    """
    conclusion = ""
    if decision.clinical_reasoning is not None:
        conclusion = decision.clinical_reasoning.narrative_summary

    result_refs = []
    if observation_refs:
        result_refs = [{"reference": f"Observation/{ref}"} for ref in observation_refs]

    return {
        "resourceType": "DiagnosticReport",
        "id": _make_id(),
        "meta": _make_meta(),
        "status": "final",
        "category": [
            {
                "coding": [
                    {
                        "system": "http://terminology.hl7.org/CodeSystem/v2-0074",
                        "code": "HM",
                        "display": "Hematology",
                    }
                ]
            }
        ],
        "code": {
            "text": "Clinical Decision Support Assessment",
        },
        "subject": _make_patient_ref(decision.patient_id),
        "effectiveDateTime": _now_iso(),
        "conclusion": conclusion,
        "result": result_refs,
    }


def build_flag(alert: str, patient_ref: str) -> dict[str, Any]:
    """Build FHIR Flag resource from a clinical alert.

    Args:
        alert: Alert message text
        patient_ref: Patient ID for the reference

    Returns:
        FHIR R4 Flag resource dict
    """
    # Determine category from alert content
    category_code = "clinical"
    if "ECG" in alert:
        category_code = "clinical"
    elif "protocol" in alert.lower():
        category_code = "safety"

    return {
        "resourceType": "Flag",
        "id": _make_id(),
        "meta": _make_meta(),
        "status": "active",
        "category": [
            {
                "coding": [
                    {
                        "system": "http://terminology.hl7.org/CodeSystem/flag-category",
                        "code": category_code,
                        "display": category_code.title(),
                    }
                ]
            }
        ],
        "code": {
            "text": alert,
        },
        "subject": _make_patient_ref(patient_ref),
        "period": {
            "start": _now_iso(),
        },
    }


def build_audit_event(decision_id: str, decision: Any) -> dict[str, Any]:
    """Build FHIR AuditEvent for a CDS decision.

    Args:
        decision_id: UUID of the audit log entry
        decision: CDSDecision object

    Returns:
        FHIR R4 AuditEvent resource dict
    """
    return {
        "resourceType": "AuditEvent",
        "id": _make_id(),
        "meta": _make_meta(),
        "type": {
            "system": "http://dicom.nema.org/resources/ontology/DCM",
            "code": "110112",
            "display": "Query",
        },
        "subtype": [
            {
                "system": "urn:attune:cds",
                "code": "cds-assessment",
                "display": "Clinical Decision Support Assessment",
            }
        ],
        "action": "E",  # Execute
        "recorded": _now_iso(),
        "outcome": "0",  # Success
        "agent": [
            {
                "who": {
                    "display": "Attune CDS System",
                },
                "requestor": True,
            }
        ],
        "source": {
            "observer": {
                "display": "Attune Healthcare CDS",
            },
        },
        "entity": [
            {
                "what": _make_patient_ref(decision.patient_id),
                "type": {
                    "system": "http://terminology.hl7.org/CodeSystem/audit-entity-type",
                    "code": "1",
                    "display": "Person",
                },
                "detail": [
                    {
                        "type": "decision_id",
                        "valueString": decision_id,
                    },
                    {
                        "type": "overall_risk",
                        "valueString": decision.overall_risk,
                    },
                ],
            }
        ],
    }


def decision_to_fhir_bundle(
    decision: Any,
    decision_id: str | None = None,
) -> dict[str, Any]:
    """Convert a CDSDecision to a complete FHIR Bundle.

    Creates a Bundle (type="collection") containing all FHIR resources
    generated from the decision: Observations, RiskAssessment,
    ClinicalImpression, DiagnosticReport, Flags, and AuditEvent.

    Args:
        decision: CDSDecision object
        decision_id: Optional audit log UUID (for AuditEvent)

    Returns:
        FHIR R4 Bundle resource dict (JSON-serializable)
    """
    entries: list[dict[str, Any]] = []

    # Build Observations
    observations = build_observations(decision)
    obs_ids = [obs["id"] for obs in observations]
    for obs in observations:
        entries.append({
            "resource": obs,
            "fullUrl": f"urn:uuid:{obs['id']}",
        })

    # Build RiskAssessment
    risk = build_risk_assessment(decision)
    entries.append({
        "resource": risk,
        "fullUrl": f"urn:uuid:{risk['id']}",
    })

    # Build ClinicalImpression
    impression = build_clinical_impression(decision)
    entries.append({
        "resource": impression,
        "fullUrl": f"urn:uuid:{impression['id']}",
    })

    # Build DiagnosticReport
    report = build_diagnostic_report(decision, obs_ids)
    entries.append({
        "resource": report,
        "fullUrl": f"urn:uuid:{report['id']}",
    })

    # Build Flags from alerts
    for alert in (decision.alerts or []):
        flag = build_flag(alert, decision.patient_id)
        entries.append({
            "resource": flag,
            "fullUrl": f"urn:uuid:{flag['id']}",
        })

    # Build AuditEvent
    audit_id = decision_id or _make_id()
    audit = build_audit_event(audit_id, decision)
    entries.append({
        "resource": audit,
        "fullUrl": f"urn:uuid:{audit['id']}",
    })

    return {
        "resourceType": "Bundle",
        "id": _make_id(),
        "meta": _make_meta(),
        "type": "collection",
        "timestamp": _now_iso(),
        "entry": entries,
    }


def validate_with_fhir_resources(bundle: dict[str, Any]) -> bool:
    """Validate a FHIR Bundle using fhir.resources library.

    Optional validation — requires fhir.resources>=7.0.0 to be installed.
    Returns True if validation passes or library is not available.

    Args:
        bundle: FHIR Bundle dict to validate

    Returns:
        True if valid or library not installed, False if validation fails
    """
    try:
        from fhir.resources.R4B.bundle import Bundle

        Bundle.model_validate(bundle)
        return True
    except ImportError:
        logger.debug("fhir.resources not installed — skipping FHIR validation")
        return True
    except Exception as e:  # noqa: BLE001
        # INTENTIONAL: Validation failure should be reported, not raised
        logger.warning(f"FHIR validation failed: {e}")
        return False
