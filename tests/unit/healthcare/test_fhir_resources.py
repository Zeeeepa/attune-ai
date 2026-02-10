"""Comprehensive unit tests for FHIR R4 resource builders.

Tests cover all builder functions in src/attune/healthcare/fhir/resources.py:
- build_observations
- build_risk_assessment
- build_clinical_impression
- build_diagnostic_report
- build_flag
- build_audit_event
- decision_to_fhir_bundle

Uses mock CDSDecision objects to isolate builder logic from domain models.

Copyright 2026 Smart-AI-Memory
Licensed under Apache 2.0
"""

from __future__ import annotations

import json
import uuid
from unittest.mock import MagicMock

import pytest

from attune.healthcare.fhir.resources import (
    FHIR_SYSTEM_LOINC,
    FHIR_SYSTEM_OBSERVATION_CATEGORY,
    FHIR_SYSTEM_UNITS,
    LOINC_CODES,
    RISK_PROBABILITY,
    build_audit_event,
    build_clinical_impression,
    build_diagnostic_report,
    build_flag,
    build_observations,
    build_risk_assessment,
    decision_to_fhir_bundle,
)

# ---------------------------------------------------------------------------
# Fixtures / helpers
# ---------------------------------------------------------------------------


def make_mock_decision(with_ecg: bool = True) -> MagicMock:
    """Create a mock CDSDecision with representative clinical data.

    Args:
        with_ecg: Whether to include ECG analysis data.

    Returns:
        MagicMock configured as a CDSDecision.
    """
    decision = MagicMock()
    decision.patient_id = "test-patient-001"
    decision.overall_risk = "high"
    decision.confidence = 0.85
    decision.cost = 0.0042
    decision.alerts = ["Elevated heart rate", "Low SpO2"]
    decision.recommendations = ["Monitor continuously", "Consider O2 therapy"]
    decision.protocol_compliance = {"status": "activated"}
    decision.trajectory = {"state": "worsening"}

    # ECG analysis
    if with_ecg:
        ecg = MagicMock()
        ecg.heart_rate = 110.5
        ecg.hrv_sdnn = 45.2
        ecg.rhythm_classification = "sinus_tachycardia"
        ecg.pvc_burden_pct = 2.1
        ecg.clinical_flags = ["TACHYCARDIA"]
        ecg.score = 65
        ecg.confidence = 0.82
        ecg.arrhythmia_events = 5
        decision.ecg_analysis = ecg
    else:
        decision.ecg_analysis = None

    # Clinical reasoning
    reasoning = MagicMock()
    reasoning.narrative_summary = "Patient shows signs of cardiac distress."
    reasoning.differentials = ["Acute MI", "SVT"]
    reasoning.recommended_workup = ["12-lead ECG", "Troponin"]
    reasoning.risk_level = "high"
    reasoning.confidence = 0.85
    decision.clinical_reasoning = reasoning

    # Quality gates
    gate = MagicMock()
    gate.name = "Data Completeness"
    gate.threshold = 0.6
    gate.actual = 0.8
    gate.passed = True
    gate.clinical = True
    decision.quality_gates = [gate]

    # Agent results
    decision.agent_results = []

    return decision


def make_mock_decision_with_vitals() -> MagicMock:
    """Create a mock CDSDecision that includes current vitals in protocol_compliance.

    Returns:
        MagicMock with protocol_compliance containing vital sign values.
    """
    decision = make_mock_decision(with_ecg=False)
    decision.protocol_compliance = {
        "status": "activated",
        "current_vitals": {
            "hr": 110,
            "systolic_bp": 145,
            "diastolic_bp": 92,
            "respiratory_rate": 22,
            "temp_f": 101.2,
            "o2_sat": 91,
            "pain_score": 7,
        },
    }
    return decision


def _extract_loinc_code(observation: dict) -> str:
    """Extract the LOINC code string from a FHIR Observation resource."""
    return observation["code"]["coding"][0]["code"]


def _resource_types_in_bundle(bundle: dict) -> list[str]:
    """Get the list of resourceType values from bundle entries."""
    return [entry["resource"]["resourceType"] for entry in bundle["entry"]]


# ---------------------------------------------------------------------------
# Tests: build_observations
# ---------------------------------------------------------------------------


class TestBuildObservations:
    """Tests for build_observations()."""

    def test_returns_empty_list_when_no_vitals_and_no_ecg(self) -> None:
        """Observations list is empty when decision has no vitals and no ECG."""
        decision = make_mock_decision(with_ecg=False)
        observations = build_observations(decision)
        assert observations == []

    def test_vital_sign_observations_have_correct_loinc_codes(self) -> None:
        """Each vital sign observation uses the correct LOINC code from the mapping."""
        decision = make_mock_decision_with_vitals()
        observations = build_observations(decision)

        loinc_codes_found = {_extract_loinc_code(obs) for obs in observations}
        expected_codes = {LOINC_CODES[key]["code"] for key in decision.protocol_compliance["current_vitals"]}

        assert loinc_codes_found == expected_codes

    def test_vital_observations_count_matches_vitals_provided(self) -> None:
        """Number of observations matches number of vitals in protocol_compliance."""
        decision = make_mock_decision_with_vitals()
        observations = build_observations(decision)
        assert len(observations) == len(decision.protocol_compliance["current_vitals"])

    def test_observation_resource_type(self) -> None:
        """Every observation has resourceType 'Observation'."""
        decision = make_mock_decision_with_vitals()
        observations = build_observations(decision)
        for obs in observations:
            assert obs["resourceType"] == "Observation"

    def test_observation_has_id_and_meta(self) -> None:
        """Every observation has an id and meta element."""
        decision = make_mock_decision_with_vitals()
        observations = build_observations(decision)
        for obs in observations:
            assert "id" in obs
            assert "meta" in obs
            assert "lastUpdated" in obs["meta"]

    def test_observation_ids_are_unique(self) -> None:
        """Each observation receives a unique UUID-based id."""
        decision = make_mock_decision_with_vitals()
        observations = build_observations(decision)
        ids = [obs["id"] for obs in observations]
        assert len(ids) == len(set(ids))

    def test_observation_has_status_final(self) -> None:
        """Observations are created with status 'final'."""
        decision = make_mock_decision_with_vitals()
        observations = build_observations(decision)
        for obs in observations:
            assert obs["status"] == "final"

    def test_observation_category_is_vital_signs(self) -> None:
        """Observation category is 'vital-signs' with correct system URI."""
        decision = make_mock_decision_with_vitals()
        observations = build_observations(decision)
        for obs in observations:
            cat = obs["category"][0]["coding"][0]
            assert cat["system"] == FHIR_SYSTEM_OBSERVATION_CATEGORY
            assert cat["code"] == "vital-signs"

    def test_observation_subject_references_patient(self) -> None:
        """Observation subject references the correct patient."""
        decision = make_mock_decision_with_vitals()
        observations = build_observations(decision)
        for obs in observations:
            assert obs["subject"]["reference"] == f"Patient/{decision.patient_id}"

    def test_observation_value_quantity_has_correct_unit_system(self) -> None:
        """ValueQuantity uses the UCUM system for units."""
        decision = make_mock_decision_with_vitals()
        observations = build_observations(decision)
        for obs in observations:
            vq = obs["valueQuantity"]
            assert vq["system"] == FHIR_SYSTEM_UNITS

    def test_observation_value_is_float(self) -> None:
        """All observation values are floats."""
        decision = make_mock_decision_with_vitals()
        observations = build_observations(decision)
        for obs in observations:
            assert isinstance(obs["valueQuantity"]["value"], float)

    def test_vital_with_none_value_is_skipped(self) -> None:
        """A vital sign with a None value is skipped."""
        decision = make_mock_decision(with_ecg=False)
        decision.protocol_compliance = {
            "current_vitals": {
                "hr": 80,
                "o2_sat": None,
            },
        }
        observations = build_observations(decision)
        codes = {_extract_loinc_code(obs) for obs in observations}
        assert LOINC_CODES["hr"]["code"] in codes
        assert LOINC_CODES["o2_sat"]["code"] not in codes
        assert len(observations) == 1

    def test_heart_rate_observation_value(self) -> None:
        """Heart rate vital observation carries the correct numeric value."""
        decision = make_mock_decision(with_ecg=False)
        decision.protocol_compliance = {
            "current_vitals": {"hr": 88},
        }
        observations = build_observations(decision)
        assert len(observations) == 1
        assert observations[0]["valueQuantity"]["value"] == 88.0
        assert observations[0]["valueQuantity"]["unit"] == "/min"

    def test_observation_has_effective_datetime(self) -> None:
        """Each observation has an effectiveDateTime timestamp."""
        decision = make_mock_decision_with_vitals()
        observations = build_observations(decision)
        for obs in observations:
            assert "effectiveDateTime" in obs
            assert isinstance(obs["effectiveDateTime"], str)


# ---------------------------------------------------------------------------
# Tests: ECG-related observations
# ---------------------------------------------------------------------------


class TestBuildObservationsECG:
    """Tests for ECG-specific observations within build_observations()."""

    def test_ecg_heart_rate_observation_created(self) -> None:
        """ECG heart rate observation is created when ecg_analysis is present."""
        decision = make_mock_decision(with_ecg=True)
        observations = build_observations(decision)
        ecg_hr_obs = [obs for obs in observations if _extract_loinc_code(obs) == "76282-3"]
        assert len(ecg_hr_obs) == 1

    def test_ecg_heart_rate_value(self) -> None:
        """ECG heart rate observation carries the ECG-derived value."""
        decision = make_mock_decision(with_ecg=True)
        observations = build_observations(decision)
        ecg_hr_obs = [obs for obs in observations if _extract_loinc_code(obs) == "76282-3"][0]
        assert ecg_hr_obs["valueQuantity"]["value"] == 110.5
        assert ecg_hr_obs["valueQuantity"]["unit"] == "/min"

    def test_ecg_hrv_sdnn_observation_created(self) -> None:
        """HRV SDNN observation is created when ecg_analysis includes hrv_sdnn."""
        decision = make_mock_decision(with_ecg=True)
        observations = build_observations(decision)
        hrv_obs = [obs for obs in observations if _extract_loinc_code(obs) == "80404-7"]
        assert len(hrv_obs) == 1
        assert hrv_obs[0]["valueQuantity"]["value"] == 45.2
        assert hrv_obs[0]["valueQuantity"]["unit"] == "ms"

    def test_ecg_pvc_burden_observation_created(self) -> None:
        """PVC burden observation is created when pvc_burden_pct is not None."""
        decision = make_mock_decision(with_ecg=True)
        observations = build_observations(decision)
        pvc_obs = [obs for obs in observations if _extract_loinc_code(obs) == "8897-1"]
        assert len(pvc_obs) == 1
        assert pvc_obs[0]["valueQuantity"]["value"] == 2.1
        assert pvc_obs[0]["valueQuantity"]["unit"] == "%"

    def test_ecg_observations_total_count(self) -> None:
        """When ECG analysis is present (and no vitals), exactly 3 ECG observations are created."""
        decision = make_mock_decision(with_ecg=True)
        observations = build_observations(decision)
        # No current_vitals in protocol_compliance, so only ECG observations
        assert len(observations) == 3

    def test_no_ecg_observations_when_ecg_is_none(self) -> None:
        """No ECG observations are created when ecg_analysis is None."""
        decision = make_mock_decision(with_ecg=False)
        observations = build_observations(decision)
        ecg_loinc_codes = {"76282-3", "80404-7", "8897-1"}
        found_ecg_codes = {_extract_loinc_code(obs) for obs in observations} & ecg_loinc_codes
        assert found_ecg_codes == set()

    def test_ecg_missing_heart_rate_skips_observation(self) -> None:
        """When ECG heart_rate is falsy, the heart rate observation is skipped."""
        decision = make_mock_decision(with_ecg=True)
        decision.ecg_analysis.heart_rate = 0
        observations = build_observations(decision)
        ecg_hr_obs = [obs for obs in observations if _extract_loinc_code(obs) == "76282-3"]
        assert len(ecg_hr_obs) == 0

    def test_ecg_pvc_burden_none_skips_observation(self) -> None:
        """When pvc_burden_pct is None, the PVC observation is skipped."""
        decision = make_mock_decision(with_ecg=True)
        decision.ecg_analysis.pvc_burden_pct = None
        observations = build_observations(decision)
        pvc_obs = [obs for obs in observations if _extract_loinc_code(obs) == "8897-1"]
        assert len(pvc_obs) == 0

    def test_ecg_observations_all_have_vital_signs_category(self) -> None:
        """ECG observations are categorized as vital-signs."""
        decision = make_mock_decision(with_ecg=True)
        observations = build_observations(decision)
        for obs in observations:
            cat = obs["category"][0]["coding"][0]
            assert cat["code"] == "vital-signs"

    def test_ecg_observations_use_loinc_system(self) -> None:
        """ECG observation codes use the LOINC system URI."""
        decision = make_mock_decision(with_ecg=True)
        observations = build_observations(decision)
        for obs in observations:
            coding = obs["code"]["coding"][0]
            assert coding["system"] == FHIR_SYSTEM_LOINC

    def test_combined_vitals_and_ecg_observations(self) -> None:
        """Both vital sign and ECG observations are created when both data sources exist."""
        decision = make_mock_decision(with_ecg=True)
        decision.protocol_compliance = {
            "current_vitals": {"hr": 110, "o2_sat": 92},
        }
        observations = build_observations(decision)
        # 2 vitals + 3 ECG = 5
        assert len(observations) == 5


# ---------------------------------------------------------------------------
# Tests: build_risk_assessment
# ---------------------------------------------------------------------------


class TestBuildRiskAssessment:
    """Tests for build_risk_assessment()."""

    def test_resource_type_is_risk_assessment(self) -> None:
        """Resource type is 'RiskAssessment'."""
        decision = make_mock_decision()
        result = build_risk_assessment(decision)
        assert result["resourceType"] == "RiskAssessment"

    def test_has_id_and_meta(self) -> None:
        """RiskAssessment has id and meta fields."""
        decision = make_mock_decision()
        result = build_risk_assessment(decision)
        assert "id" in result
        assert "meta" in result
        assert "lastUpdated" in result["meta"]

    def test_status_is_final(self) -> None:
        """Status is 'final'."""
        decision = make_mock_decision()
        result = build_risk_assessment(decision)
        assert result["status"] == "final"

    def test_subject_references_patient(self) -> None:
        """Subject references the correct patient."""
        decision = make_mock_decision()
        result = build_risk_assessment(decision)
        assert result["subject"]["reference"] == "Patient/test-patient-001"

    @pytest.mark.parametrize(
        "risk_level,expected_probability",
        [
            ("critical", 0.95),
            ("high", 0.75),
            ("moderate", 0.45),
            ("low", 0.15),
        ],
    )
    def test_risk_level_maps_to_correct_probability(
        self, risk_level: str, expected_probability: float
    ) -> None:
        """Each risk level maps to the correct probability decimal."""
        decision = make_mock_decision()
        decision.overall_risk = risk_level
        result = build_risk_assessment(decision)
        assert result["prediction"][0]["probabilityDecimal"] == expected_probability

    def test_unknown_risk_level_defaults_to_low_probability(self) -> None:
        """An unrecognized risk level defaults to 0.15 probability."""
        decision = make_mock_decision()
        decision.overall_risk = "unknown_level"
        result = build_risk_assessment(decision)
        assert result["prediction"][0]["probabilityDecimal"] == 0.15

    def test_prediction_outcome_contains_risk_level(self) -> None:
        """Prediction outcome text contains the risk level string."""
        decision = make_mock_decision()
        result = build_risk_assessment(decision)
        assert "high" in result["prediction"][0]["outcome"]["text"]

    def test_prediction_rationale_is_narrative_summary(self) -> None:
        """Prediction rationale contains the clinical reasoning narrative summary."""
        decision = make_mock_decision()
        result = build_risk_assessment(decision)
        assert result["prediction"][0]["rationale"] == "Patient shows signs of cardiac distress."

    def test_mitigation_joins_recommendations(self) -> None:
        """Mitigation field is a semicolon-joined string of recommendations."""
        decision = make_mock_decision()
        result = build_risk_assessment(decision)
        assert result["mitigation"] == "Monitor continuously; Consider O2 therapy"

    def test_mitigation_is_none_when_no_recommendations(self) -> None:
        """Mitigation is None when recommendations list is empty."""
        decision = make_mock_decision()
        decision.recommendations = []
        result = build_risk_assessment(decision)
        assert result["mitigation"] is None

    def test_rationale_empty_when_no_clinical_reasoning(self) -> None:
        """Rationale is empty string when clinical_reasoning is None."""
        decision = make_mock_decision()
        decision.clinical_reasoning = None
        result = build_risk_assessment(decision)
        assert result["prediction"][0]["rationale"] == ""

    def test_method_text_mentions_attune(self) -> None:
        """Method text identifies the Attune CDS system."""
        decision = make_mock_decision()
        result = build_risk_assessment(decision)
        assert "Attune" in result["method"]["text"]


# ---------------------------------------------------------------------------
# Tests: build_clinical_impression
# ---------------------------------------------------------------------------


class TestBuildClinicalImpression:
    """Tests for build_clinical_impression()."""

    def test_resource_type(self) -> None:
        """Resource type is 'ClinicalImpression'."""
        decision = make_mock_decision()
        result = build_clinical_impression(decision)
        assert result["resourceType"] == "ClinicalImpression"

    def test_has_id_and_meta(self) -> None:
        """ClinicalImpression has id and meta fields."""
        decision = make_mock_decision()
        result = build_clinical_impression(decision)
        assert "id" in result
        assert "meta" in result

    def test_status_is_completed(self) -> None:
        """Status is 'completed'."""
        decision = make_mock_decision()
        result = build_clinical_impression(decision)
        assert result["status"] == "completed"

    def test_includes_differentials_as_findings(self) -> None:
        """Differentials from clinical_reasoning appear as findings."""
        decision = make_mock_decision()
        result = build_clinical_impression(decision)
        finding_texts = [f["itemCodeableConcept"]["text"] for f in result["finding"]]
        assert "Acute MI" in finding_texts
        assert "SVT" in finding_texts

    def test_finding_count_matches_differentials(self) -> None:
        """Number of findings matches number of differentials."""
        decision = make_mock_decision()
        result = build_clinical_impression(decision)
        assert len(result["finding"]) == 2

    def test_summary_is_narrative(self) -> None:
        """Summary contains the narrative summary from clinical reasoning."""
        decision = make_mock_decision()
        result = build_clinical_impression(decision)
        assert result["summary"] == "Patient shows signs of cardiac distress."

    def test_summary_fallback_when_no_reasoning(self) -> None:
        """Summary falls back to default text when clinical_reasoning is None."""
        decision = make_mock_decision()
        decision.clinical_reasoning = None
        result = build_clinical_impression(decision)
        assert result["summary"] == "No clinical reasoning available"

    def test_findings_empty_when_no_reasoning(self) -> None:
        """Findings list is empty when clinical_reasoning is None."""
        decision = make_mock_decision()
        decision.clinical_reasoning = None
        result = build_clinical_impression(decision)
        assert result["finding"] == []

    def test_protocol_urn_included(self) -> None:
        """Protocol field contains a URN derived from protocol_compliance."""
        decision = make_mock_decision()
        result = build_clinical_impression(decision)
        assert len(result["protocol"]) == 1
        assert result["protocol"][0].startswith("urn:attune:protocol:")

    def test_protocol_uses_unknown_when_name_missing(self) -> None:
        """Protocol defaults to 'unknown' when protocol_name is not in compliance dict."""
        decision = make_mock_decision()
        decision.protocol_compliance = {"status": "activated"}
        result = build_clinical_impression(decision)
        assert result["protocol"][0] == "urn:attune:protocol:unknown"

    def test_protocol_uses_provided_name(self) -> None:
        """Protocol uses the protocol_name from compliance dict when available."""
        decision = make_mock_decision()
        decision.protocol_compliance = {
            "status": "activated",
            "protocol_name": "sepsis-3",
        }
        result = build_clinical_impression(decision)
        assert result["protocol"][0] == "urn:attune:protocol:sepsis-3"

    def test_subject_references_patient(self) -> None:
        """Subject references the correct patient."""
        decision = make_mock_decision()
        result = build_clinical_impression(decision)
        assert result["subject"]["reference"] == "Patient/test-patient-001"


# ---------------------------------------------------------------------------
# Tests: build_diagnostic_report
# ---------------------------------------------------------------------------


class TestBuildDiagnosticReport:
    """Tests for build_diagnostic_report()."""

    def test_resource_type(self) -> None:
        """Resource type is 'DiagnosticReport'."""
        decision = make_mock_decision()
        result = build_diagnostic_report(decision)
        assert result["resourceType"] == "DiagnosticReport"

    def test_has_id_and_meta(self) -> None:
        """DiagnosticReport has id and meta fields."""
        decision = make_mock_decision()
        result = build_diagnostic_report(decision)
        assert "id" in result
        assert "meta" in result

    def test_status_is_final(self) -> None:
        """Status is 'final'."""
        decision = make_mock_decision()
        result = build_diagnostic_report(decision)
        assert result["status"] == "final"

    def test_wraps_observation_references(self) -> None:
        """Observation IDs are wrapped as references in the result field."""
        decision = make_mock_decision()
        obs_ids = ["obs-aaa", "obs-bbb", "obs-ccc"]
        result = build_diagnostic_report(decision, observation_refs=obs_ids)
        refs = [r["reference"] for r in result["result"]]
        assert refs == ["Observation/obs-aaa", "Observation/obs-bbb", "Observation/obs-ccc"]

    def test_result_empty_when_no_observation_refs(self) -> None:
        """Result list is empty when no observation_refs are provided."""
        decision = make_mock_decision()
        result = build_diagnostic_report(decision)
        assert result["result"] == []

    def test_result_empty_when_observation_refs_is_none(self) -> None:
        """Result list is empty when observation_refs is None."""
        decision = make_mock_decision()
        result = build_diagnostic_report(decision, observation_refs=None)
        assert result["result"] == []

    def test_conclusion_is_narrative_summary(self) -> None:
        """Conclusion contains the clinical reasoning narrative summary."""
        decision = make_mock_decision()
        result = build_diagnostic_report(decision)
        assert result["conclusion"] == "Patient shows signs of cardiac distress."

    def test_conclusion_empty_when_no_reasoning(self) -> None:
        """Conclusion is empty string when clinical_reasoning is None."""
        decision = make_mock_decision()
        decision.clinical_reasoning = None
        result = build_diagnostic_report(decision)
        assert result["conclusion"] == ""

    def test_subject_references_patient(self) -> None:
        """Subject references the correct patient."""
        decision = make_mock_decision()
        result = build_diagnostic_report(decision)
        assert result["subject"]["reference"] == "Patient/test-patient-001"

    def test_code_text_mentions_cds(self) -> None:
        """Code text mentions Clinical Decision Support."""
        decision = make_mock_decision()
        result = build_diagnostic_report(decision)
        assert "Clinical Decision Support" in result["code"]["text"]

    def test_category_coding_present(self) -> None:
        """Category has coding with system and code."""
        decision = make_mock_decision()
        result = build_diagnostic_report(decision)
        cat = result["category"][0]["coding"][0]
        assert cat["code"] == "HM"
        assert "system" in cat


# ---------------------------------------------------------------------------
# Tests: build_flag
# ---------------------------------------------------------------------------


class TestBuildFlag:
    """Tests for build_flag()."""

    def test_resource_type(self) -> None:
        """Resource type is 'Flag'."""
        result = build_flag("Elevated heart rate", "patient-001")
        assert result["resourceType"] == "Flag"

    def test_has_id_and_meta(self) -> None:
        """Flag has id and meta fields."""
        result = build_flag("Elevated heart rate", "patient-001")
        assert "id" in result
        assert "meta" in result

    def test_status_is_active(self) -> None:
        """Flag status is 'active'."""
        result = build_flag("Elevated heart rate", "patient-001")
        assert result["status"] == "active"

    def test_code_text_is_alert_message(self) -> None:
        """Code text contains the alert message."""
        result = build_flag("Low SpO2 detected", "patient-001")
        assert result["code"]["text"] == "Low SpO2 detected"

    def test_subject_references_patient(self) -> None:
        """Subject references the correct patient."""
        result = build_flag("Alert", "test-patient-xyz")
        assert result["subject"]["reference"] == "Patient/test-patient-xyz"

    def test_period_has_start(self) -> None:
        """Flag period includes a start timestamp."""
        result = build_flag("Alert", "patient-001")
        assert "start" in result["period"]
        assert isinstance(result["period"]["start"], str)

    def test_category_clinical_for_general_alert(self) -> None:
        """Category code is 'clinical' for a general alert."""
        result = build_flag("Elevated heart rate", "patient-001")
        cat = result["category"][0]["coding"][0]
        assert cat["code"] == "clinical"

    def test_category_clinical_for_ecg_alert(self) -> None:
        """Category code is 'clinical' for an ECG-related alert."""
        result = build_flag("ECG shows ST elevation", "patient-001")
        cat = result["category"][0]["coding"][0]
        assert cat["code"] == "clinical"

    def test_category_safety_for_protocol_alert(self) -> None:
        """Category code is 'safety' for a protocol-related alert."""
        result = build_flag("Violation of sepsis protocol detected", "patient-001")
        cat = result["category"][0]["coding"][0]
        assert cat["code"] == "safety"

    def test_category_system_uri(self) -> None:
        """Category coding uses the HL7 flag-category system URI."""
        result = build_flag("Some alert", "patient-001")
        cat = result["category"][0]["coding"][0]
        assert cat["system"] == "http://terminology.hl7.org/CodeSystem/flag-category"

    def test_flag_id_is_valid_uuid(self) -> None:
        """Flag id is a valid UUID string."""
        result = build_flag("Alert", "patient-001")
        uuid.UUID(result["id"])  # Raises ValueError if invalid


# ---------------------------------------------------------------------------
# Tests: build_audit_event
# ---------------------------------------------------------------------------


class TestBuildAuditEvent:
    """Tests for build_audit_event()."""

    def test_resource_type(self) -> None:
        """Resource type is 'AuditEvent'."""
        decision = make_mock_decision()
        result = build_audit_event("decision-123", decision)
        assert result["resourceType"] == "AuditEvent"

    def test_has_id_and_meta(self) -> None:
        """AuditEvent has id and meta fields."""
        decision = make_mock_decision()
        result = build_audit_event("decision-123", decision)
        assert "id" in result
        assert "meta" in result

    def test_action_is_execute(self) -> None:
        """Action code is 'E' for Execute."""
        decision = make_mock_decision()
        result = build_audit_event("decision-123", decision)
        assert result["action"] == "E"

    def test_outcome_is_success(self) -> None:
        """Outcome code is '0' for Success."""
        decision = make_mock_decision()
        result = build_audit_event("decision-123", decision)
        assert result["outcome"] == "0"

    def test_entity_references_patient(self) -> None:
        """Entity 'what' references the correct patient."""
        decision = make_mock_decision()
        result = build_audit_event("decision-123", decision)
        assert result["entity"][0]["what"]["reference"] == "Patient/test-patient-001"

    def test_entity_detail_contains_decision_id(self) -> None:
        """Entity detail includes the decision_id."""
        decision = make_mock_decision()
        result = build_audit_event("my-decision-uuid", decision)
        details = {d["type"]: d["valueString"] for d in result["entity"][0]["detail"]}
        assert details["decision_id"] == "my-decision-uuid"

    def test_entity_detail_contains_overall_risk(self) -> None:
        """Entity detail includes the overall_risk level."""
        decision = make_mock_decision()
        result = build_audit_event("decision-123", decision)
        details = {d["type"]: d["valueString"] for d in result["entity"][0]["detail"]}
        assert details["overall_risk"] == "high"

    def test_agent_requestor_is_true(self) -> None:
        """Agent requestor flag is True."""
        decision = make_mock_decision()
        result = build_audit_event("decision-123", decision)
        assert result["agent"][0]["requestor"] is True

    def test_agent_identifies_attune(self) -> None:
        """Agent 'who' identifies the Attune CDS System."""
        decision = make_mock_decision()
        result = build_audit_event("decision-123", decision)
        assert "Attune" in result["agent"][0]["who"]["display"]

    def test_source_observer_mentions_attune(self) -> None:
        """Source observer references Attune Healthcare CDS."""
        decision = make_mock_decision()
        result = build_audit_event("decision-123", decision)
        assert "Attune" in result["source"]["observer"]["display"]

    def test_subtype_is_cds_assessment(self) -> None:
        """Subtype identifies a CDS assessment event."""
        decision = make_mock_decision()
        result = build_audit_event("decision-123", decision)
        assert result["subtype"][0]["code"] == "cds-assessment"

    def test_recorded_is_iso_timestamp(self) -> None:
        """Recorded field is an ISO-format timestamp string."""
        decision = make_mock_decision()
        result = build_audit_event("decision-123", decision)
        assert isinstance(result["recorded"], str)
        # Basic ISO format check: should contain 'T' separator
        assert "T" in result["recorded"]


# ---------------------------------------------------------------------------
# Tests: decision_to_fhir_bundle
# ---------------------------------------------------------------------------


class TestDecisionToFhirBundle:
    """Tests for decision_to_fhir_bundle()."""

    def test_bundle_resource_type(self) -> None:
        """Bundle resource type is 'Bundle'."""
        decision = make_mock_decision()
        bundle = decision_to_fhir_bundle(decision)
        assert bundle["resourceType"] == "Bundle"

    def test_bundle_type_is_collection(self) -> None:
        """Bundle type is 'collection'."""
        decision = make_mock_decision()
        bundle = decision_to_fhir_bundle(decision)
        assert bundle["type"] == "collection"

    def test_bundle_has_id_and_meta(self) -> None:
        """Bundle has id and meta fields."""
        decision = make_mock_decision()
        bundle = decision_to_fhir_bundle(decision)
        assert "id" in bundle
        assert "meta" in bundle
        assert "lastUpdated" in bundle["meta"]

    def test_bundle_has_timestamp(self) -> None:
        """Bundle has a timestamp."""
        decision = make_mock_decision()
        bundle = decision_to_fhir_bundle(decision)
        assert "timestamp" in bundle
        assert isinstance(bundle["timestamp"], str)

    def test_bundle_contains_risk_assessment(self) -> None:
        """Bundle contains a RiskAssessment entry."""
        decision = make_mock_decision()
        bundle = decision_to_fhir_bundle(decision)
        types = _resource_types_in_bundle(bundle)
        assert "RiskAssessment" in types

    def test_bundle_contains_clinical_impression(self) -> None:
        """Bundle contains a ClinicalImpression entry."""
        decision = make_mock_decision()
        bundle = decision_to_fhir_bundle(decision)
        types = _resource_types_in_bundle(bundle)
        assert "ClinicalImpression" in types

    def test_bundle_contains_diagnostic_report(self) -> None:
        """Bundle contains a DiagnosticReport entry."""
        decision = make_mock_decision()
        bundle = decision_to_fhir_bundle(decision)
        types = _resource_types_in_bundle(bundle)
        assert "DiagnosticReport" in types

    def test_bundle_contains_audit_event(self) -> None:
        """Bundle contains an AuditEvent entry."""
        decision = make_mock_decision()
        bundle = decision_to_fhir_bundle(decision)
        types = _resource_types_in_bundle(bundle)
        assert "AuditEvent" in types

    def test_bundle_contains_flags_for_alerts(self) -> None:
        """Bundle contains one Flag per alert."""
        decision = make_mock_decision()
        bundle = decision_to_fhir_bundle(decision)
        types = _resource_types_in_bundle(bundle)
        flag_count = types.count("Flag")
        assert flag_count == len(decision.alerts)

    def test_bundle_contains_ecg_observations(self) -> None:
        """Bundle contains ECG Observation entries when ECG data is present."""
        decision = make_mock_decision(with_ecg=True)
        bundle = decision_to_fhir_bundle(decision)
        types = _resource_types_in_bundle(bundle)
        obs_count = types.count("Observation")
        # 3 ECG observations (hr, hrv, pvc)
        assert obs_count == 3

    def test_bundle_no_observations_without_data(self) -> None:
        """Bundle contains no Observation entries when no vitals or ECG data is present."""
        decision = make_mock_decision(with_ecg=False)
        bundle = decision_to_fhir_bundle(decision)
        types = _resource_types_in_bundle(bundle)
        assert "Observation" not in types

    def test_entries_have_full_url(self) -> None:
        """Every entry has a fullUrl field starting with 'urn:uuid:'."""
        decision = make_mock_decision()
        bundle = decision_to_fhir_bundle(decision)
        for entry in bundle["entry"]:
            assert "fullUrl" in entry
            assert entry["fullUrl"].startswith("urn:uuid:")

    def test_entries_have_resource(self) -> None:
        """Every entry has a resource field."""
        decision = make_mock_decision()
        bundle = decision_to_fhir_bundle(decision)
        for entry in bundle["entry"]:
            assert "resource" in entry
            assert "resourceType" in entry["resource"]

    def test_diagnostic_report_references_observations(self) -> None:
        """DiagnosticReport result field references all Observation IDs."""
        decision = make_mock_decision(with_ecg=True)
        bundle = decision_to_fhir_bundle(decision)

        obs_ids = []
        diag_report = None
        for entry in bundle["entry"]:
            res = entry["resource"]
            if res["resourceType"] == "Observation":
                obs_ids.append(res["id"])
            elif res["resourceType"] == "DiagnosticReport":
                diag_report = res

        assert diag_report is not None
        report_refs = [r["reference"] for r in diag_report["result"]]
        for obs_id in obs_ids:
            assert f"Observation/{obs_id}" in report_refs

    def test_bundle_with_no_alerts(self) -> None:
        """Bundle has no Flag entries when alerts list is empty."""
        decision = make_mock_decision()
        decision.alerts = []
        bundle = decision_to_fhir_bundle(decision)
        types = _resource_types_in_bundle(bundle)
        assert "Flag" not in types

    def test_bundle_with_none_alerts(self) -> None:
        """Bundle handles None alerts gracefully (no Flags)."""
        decision = make_mock_decision()
        decision.alerts = None
        bundle = decision_to_fhir_bundle(decision)
        types = _resource_types_in_bundle(bundle)
        assert "Flag" not in types

    def test_bundle_uses_provided_decision_id(self) -> None:
        """AuditEvent uses the provided decision_id."""
        decision = make_mock_decision()
        bundle = decision_to_fhir_bundle(decision, decision_id="custom-audit-id-42")
        audit = None
        for entry in bundle["entry"]:
            if entry["resource"]["resourceType"] == "AuditEvent":
                audit = entry["resource"]
                break

        assert audit is not None
        details = {d["type"]: d["valueString"] for d in audit["entity"][0]["detail"]}
        assert details["decision_id"] == "custom-audit-id-42"

    def test_bundle_generates_decision_id_when_none(self) -> None:
        """AuditEvent receives a generated decision_id when none is provided."""
        decision = make_mock_decision()
        bundle = decision_to_fhir_bundle(decision, decision_id=None)
        audit = None
        for entry in bundle["entry"]:
            if entry["resource"]["resourceType"] == "AuditEvent":
                audit = entry["resource"]
                break

        assert audit is not None
        details = {d["type"]: d["valueString"] for d in audit["entity"][0]["detail"]}
        assert details["decision_id"]  # Non-empty string


# ---------------------------------------------------------------------------
# Tests: JSON serializability
# ---------------------------------------------------------------------------


class TestJsonSerializability:
    """Tests that all FHIR resources are JSON-serializable."""

    def test_bundle_is_json_serializable(self) -> None:
        """Complete bundle can be serialized to JSON without errors."""
        decision = make_mock_decision(with_ecg=True)
        bundle = decision_to_fhir_bundle(decision, decision_id="test-id")
        serialized = json.dumps(bundle)
        assert isinstance(serialized, str)
        assert len(serialized) > 0

    def test_bundle_roundtrips_through_json(self) -> None:
        """Bundle can be serialized and deserialized back to equivalent dict."""
        decision = make_mock_decision(with_ecg=True)
        bundle = decision_to_fhir_bundle(decision)
        roundtripped = json.loads(json.dumps(bundle))
        assert roundtripped["resourceType"] == "Bundle"
        assert roundtripped["type"] == "collection"
        assert len(roundtripped["entry"]) == len(bundle["entry"])

    def test_observations_are_json_serializable(self) -> None:
        """Individual observations can be serialized to JSON."""
        decision = make_mock_decision_with_vitals()
        observations = build_observations(decision)
        for obs in observations:
            serialized = json.dumps(obs)
            assert isinstance(serialized, str)

    def test_risk_assessment_is_json_serializable(self) -> None:
        """RiskAssessment can be serialized to JSON."""
        decision = make_mock_decision()
        result = build_risk_assessment(decision)
        serialized = json.dumps(result)
        assert isinstance(serialized, str)

    def test_clinical_impression_is_json_serializable(self) -> None:
        """ClinicalImpression can be serialized to JSON."""
        decision = make_mock_decision()
        result = build_clinical_impression(decision)
        serialized = json.dumps(result)
        assert isinstance(serialized, str)

    def test_flag_is_json_serializable(self) -> None:
        """Flag can be serialized to JSON."""
        result = build_flag("Test alert", "patient-001")
        serialized = json.dumps(result)
        assert isinstance(serialized, str)

    def test_audit_event_is_json_serializable(self) -> None:
        """AuditEvent can be serialized to JSON."""
        decision = make_mock_decision()
        result = build_audit_event("test-id", decision)
        serialized = json.dumps(result)
        assert isinstance(serialized, str)

    def test_diagnostic_report_is_json_serializable(self) -> None:
        """DiagnosticReport can be serialized to JSON."""
        decision = make_mock_decision()
        result = build_diagnostic_report(decision, observation_refs=["obs-1"])
        serialized = json.dumps(result)
        assert isinstance(serialized, str)


# ---------------------------------------------------------------------------
# Tests: All resources have required FHIR metadata fields
# ---------------------------------------------------------------------------


class TestResourceMetadataFields:
    """Tests that all resources have resourceType, id, and meta fields."""

    def test_all_bundle_entries_have_resource_type(self) -> None:
        """Every resource in the bundle has a resourceType field."""
        decision = make_mock_decision(with_ecg=True)
        bundle = decision_to_fhir_bundle(decision)
        for entry in bundle["entry"]:
            assert "resourceType" in entry["resource"]
            assert isinstance(entry["resource"]["resourceType"], str)

    def test_all_bundle_entries_have_id(self) -> None:
        """Every resource in the bundle has an id field."""
        decision = make_mock_decision(with_ecg=True)
        bundle = decision_to_fhir_bundle(decision)
        for entry in bundle["entry"]:
            assert "id" in entry["resource"]
            assert isinstance(entry["resource"]["id"], str)
            assert len(entry["resource"]["id"]) > 0

    def test_all_bundle_entries_have_meta(self) -> None:
        """Every resource in the bundle has a meta field with lastUpdated."""
        decision = make_mock_decision(with_ecg=True)
        bundle = decision_to_fhir_bundle(decision)
        for entry in bundle["entry"]:
            assert "meta" in entry["resource"]
            assert "lastUpdated" in entry["resource"]["meta"]

    def test_all_ids_in_bundle_are_unique(self) -> None:
        """Every resource in the bundle has a unique id."""
        decision = make_mock_decision(with_ecg=True)
        bundle = decision_to_fhir_bundle(decision)
        ids = [entry["resource"]["id"] for entry in bundle["entry"]]
        # Include the bundle's own id
        ids.append(bundle["id"])
        assert len(ids) == len(set(ids))

    def test_all_ids_are_valid_uuids(self) -> None:
        """All resource IDs in the bundle are valid UUIDs."""
        decision = make_mock_decision(with_ecg=True)
        bundle = decision_to_fhir_bundle(decision)
        # Bundle itself
        uuid.UUID(bundle["id"])
        # All entries
        for entry in bundle["entry"]:
            uuid.UUID(entry["resource"]["id"])


# ---------------------------------------------------------------------------
# Tests: LOINC_CODES and RISK_PROBABILITY constants
# ---------------------------------------------------------------------------


class TestConstants:
    """Tests for module-level constants."""

    def test_loinc_codes_has_expected_keys(self) -> None:
        """LOINC_CODES contains all expected vital sign keys."""
        expected_keys = {
            "hr", "systolic_bp", "diastolic_bp", "respiratory_rate",
            "temp_f", "o2_sat", "pain_score", "ecg_hr", "hrv_sdnn", "pvc_burden",
        }
        assert set(LOINC_CODES.keys()) == expected_keys

    def test_loinc_codes_have_required_fields(self) -> None:
        """Each LOINC code entry has code, display, and unit fields."""
        for key, info in LOINC_CODES.items():
            assert "code" in info, f"Missing 'code' in LOINC_CODES['{key}']"
            assert "display" in info, f"Missing 'display' in LOINC_CODES['{key}']"
            assert "unit" in info, f"Missing 'unit' in LOINC_CODES['{key}']"

    def test_risk_probability_has_all_levels(self) -> None:
        """RISK_PROBABILITY maps all four risk levels."""
        assert set(RISK_PROBABILITY.keys()) == {"critical", "high", "moderate", "low"}

    def test_risk_probability_values_are_between_0_and_1(self) -> None:
        """All probability values are between 0 and 1."""
        for level, prob in RISK_PROBABILITY.items():
            assert 0.0 <= prob <= 1.0, f"Invalid probability for '{level}': {prob}"

    def test_risk_probability_decreasing_order(self) -> None:
        """Probabilities decrease as risk level decreases."""
        assert RISK_PROBABILITY["critical"] > RISK_PROBABILITY["high"]
        assert RISK_PROBABILITY["high"] > RISK_PROBABILITY["moderate"]
        assert RISK_PROBABILITY["moderate"] > RISK_PROBABILITY["low"]
