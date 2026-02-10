"""FHIR R4 Resource Builders and CDS Hooks Service.

Converts CDS decisions to FHIR R4 resources for hospital integration:
- Observation: Vital signs and ECG metrics (LOINC-coded)
- RiskAssessment: Overall clinical risk with probability
- ClinicalImpression: Clinical reasoning narrative and differentials
- DiagnosticReport: Consolidated report wrapping all observations
- Flag: Clinical alerts from protocol compliance and ECG
- AuditEvent: Decision audit trail entries
- Bundle: Collection of all resources for a decision

Copyright 2026 Smart-AI-Memory
Licensed under Apache 2.0
"""

from .resources import (
    build_audit_event,
    build_clinical_impression,
    build_diagnostic_report,
    build_flag,
    build_observations,
    build_risk_assessment,
    decision_to_fhir_bundle,
)

__all__ = [
    "build_audit_event",
    "build_clinical_impression",
    "build_diagnostic_report",
    "build_flag",
    "build_observations",
    "build_risk_assessment",
    "decision_to_fhir_bundle",
]
