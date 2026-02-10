"""Unit tests for CDS Hooks v2.0 service endpoints.

Tests the FastAPI router, helper functions, and CDS card generation
defined in src/attune/healthcare/fhir/cds_hooks.py.

Copyright 2026 Smart-AI-Memory
Licensed under Apache 2.0
"""

from __future__ import annotations

import uuid
from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from attune.healthcare.fhir.cds_hooks import (
    SERVICES,
    CDSCard,
    CDSHookRequest,
    CDSHookResponse,
    CDSServiceDefinition,
    CDSSource,
    _build_cards_from_decision,
    _extract_vitals_from_prefetch,
    _risk_to_indicator,
    create_cds_hooks_router,
)

# ============================================================================
# Fixtures
# ============================================================================


@pytest.fixture()
def app() -> FastAPI:
    """Create a FastAPI test application with CDS Hooks router."""
    test_app = FastAPI()
    router = create_cds_hooks_router()
    test_app.include_router(router)
    return test_app


@pytest.fixture()
def client(app: FastAPI) -> TestClient:
    """Create a TestClient for the CDS Hooks app."""
    return TestClient(app)


@pytest.fixture()
def sample_hook_request() -> dict[str, Any]:
    """Build a minimal CDS Hooks request payload for patient-view."""
    return {
        "hook": "patient-view",
        "hookInstance": str(uuid.uuid4()),
        "context": {"patientId": "patient-123"},
        "prefetch": {
            "observations": {
                "resourceType": "Bundle",
                "entry": [
                    {
                        "resource": {
                            "resourceType": "Observation",
                            "code": {
                                "coding": [{"system": "http://loinc.org", "code": "8867-4"}]
                            },
                            "valueQuantity": {"value": 72, "unit": "bpm"},
                        }
                    },
                    {
                        "resource": {
                            "resourceType": "Observation",
                            "code": {
                                "coding": [{"system": "http://loinc.org", "code": "8480-6"}]
                            },
                            "valueQuantity": {"value": 120, "unit": "mmHg"},
                        }
                    },
                    {
                        "resource": {
                            "resourceType": "Observation",
                            "code": {
                                "coding": [{"system": "http://loinc.org", "code": "8462-4"}]
                            },
                            "valueQuantity": {"value": 80, "unit": "mmHg"},
                        }
                    },
                ],
            }
        },
    }


@pytest.fixture()
def mock_decision() -> MagicMock:
    """Create a mock CDSDecision with clinical reasoning and recommendations."""
    decision = MagicMock()
    decision.overall_risk = "moderate"
    decision.confidence = 0.85

    reasoning = MagicMock()
    reasoning.narrative_summary = "Patient vitals within acceptable range with mild tachycardia."
    reasoning.differentials = ["Anxiety", "Dehydration"]
    decision.clinical_reasoning = reasoning

    decision.recommendations = [
        "Repeat vitals in 30 minutes",
        "Monitor fluid intake",
    ]
    decision.alerts = []
    decision.ecg_analysis = None
    return decision


@pytest.fixture()
def mock_critical_decision() -> MagicMock:
    """Create a mock CDSDecision with critical risk and alerts."""
    decision = MagicMock()
    decision.overall_risk = "critical"
    decision.confidence = 0.92

    reasoning = MagicMock()
    reasoning.narrative_summary = "Critical hemodynamic instability detected."
    reasoning.differentials = ["Cardiogenic shock", "Sepsis"]
    decision.clinical_reasoning = reasoning

    decision.recommendations = [
        "Initiate rapid response team",
        "Obtain STAT labs",
        "12-lead ECG",
    ]
    decision.alerts = ["Systolic BP below 90 mmHg", "ECG ST-elevation detected"]

    ecg = MagicMock()
    ecg.rhythm_classification = "sinus_tachycardia"
    ecg.heart_rate = 115.0
    ecg.pvc_burden_pct = 2.5
    ecg.hrv_sdnn = 35.0
    ecg.clinical_flags = ["ST-elevation"]
    decision.ecg_analysis = ecg

    return decision


# ============================================================================
# Service Discovery Tests
# ============================================================================


class TestServiceDiscovery:
    """Tests for GET /cds-services endpoint."""

    def test_returns_three_services(self, client: TestClient) -> None:
        """Service discovery returns exactly 3 service definitions."""
        response = client.get("/cds-services")

        assert response.status_code == 200
        body = response.json()
        assert "services" in body
        assert len(body["services"]) == 3

    def test_service_ids(self, client: TestClient) -> None:
        """Service discovery includes expected service IDs."""
        response = client.get("/cds-services")
        body = response.json()

        service_ids = {svc["id"] for svc in body["services"]}
        assert service_ids == {
            "attune-patient-view",
            "attune-order-sign",
            "attune-encounter-start",
        }

    def test_services_have_required_fields(self, client: TestClient) -> None:
        """Each service definition has all required CDS Hooks fields."""
        required_fields = {"hook", "title", "description", "id", "prefetch"}
        response = client.get("/cds-services")
        body = response.json()

        for svc in body["services"]:
            for field in required_fields:
                assert field in svc, f"Service {svc.get('id', '?')} missing field '{field}'"

    def test_patient_view_service_details(self, client: TestClient) -> None:
        """Patient-view service has correct hook and prefetch templates."""
        response = client.get("/cds-services")
        body = response.json()

        patient_view = next(
            (s for s in body["services"] if s["id"] == "attune-patient-view"), None
        )
        assert patient_view is not None
        assert patient_view["hook"] == "patient-view"
        assert "patient" in patient_view["prefetch"]
        assert "observations" in patient_view["prefetch"]


# ============================================================================
# Hook Handler Tests
# ============================================================================


class TestHookHandler:
    """Tests for POST /cds-services/{service_id} endpoint."""

    def test_invalid_service_id_returns_404(self, client: TestClient) -> None:
        """Unknown service ID returns 404 with error detail."""
        payload = {
            "hook": "patient-view",
            "hookInstance": str(uuid.uuid4()),
            "context": {"patientId": "test-001"},
        }
        response = client.post("/cds-services/nonexistent-service", json=payload)

        assert response.status_code == 404
        assert "Unknown service" in response.json()["detail"]

    def test_no_vitals_returns_informational_card(self, client: TestClient) -> None:
        """Request without prefetch vitals returns informational card."""
        payload = {
            "hook": "patient-view",
            "hookInstance": str(uuid.uuid4()),
            "context": {"patientId": "patient-999"},
            "prefetch": {},
        }
        response = client.post("/cds-services/attune-patient-view", json=payload)

        assert response.status_code == 200
        body = response.json()
        assert "cards" in body
        assert len(body["cards"]) >= 1
        assert "No recent vital signs" in body["cards"][0]["summary"]
        assert body["cards"][0]["indicator"] == "info"

    def test_no_prefetch_returns_informational_card(self, client: TestClient) -> None:
        """Request with null prefetch returns informational card."""
        payload = {
            "hook": "patient-view",
            "hookInstance": str(uuid.uuid4()),
            "context": {"patientId": "patient-999"},
        }
        response = client.post("/cds-services/attune-patient-view", json=payload)

        assert response.status_code == 200
        body = response.json()
        assert "cards" in body
        assert "No recent vital signs" in body["cards"][0]["summary"]

    @patch("attune.healthcare.fhir.cds_hooks.CDSTeam", create=True)
    def test_patient_view_returns_cards(
        self,
        mock_team_cls: MagicMock,
        client: TestClient,
        sample_hook_request: dict[str, Any],
        mock_decision: MagicMock,
    ) -> None:
        """Patient-view handler returns CDS cards from CDSTeam assessment."""
        mock_team_instance = MagicMock()
        mock_team_instance.assess = AsyncMock(return_value=mock_decision)
        mock_team_cls.return_value = mock_team_instance

        with patch(
            "attune.healthcare.fhir.cds_hooks.CDSTeam",
            mock_team_cls,
            create=True,
        ):
            response = client.post(
                "/cds-services/attune-patient-view", json=sample_hook_request
            )

        assert response.status_code == 200
        body = response.json()
        assert "cards" in body
        assert len(body["cards"]) >= 1

    @patch("attune.healthcare.fhir.cds_hooks.CDSTeam", create=True)
    def test_cards_include_source_label(
        self,
        mock_team_cls: MagicMock,
        client: TestClient,
        sample_hook_request: dict[str, Any],
        mock_decision: MagicMock,
    ) -> None:
        """Response cards include source.label = 'Attune CDS'."""
        mock_team_instance = MagicMock()
        mock_team_instance.assess = AsyncMock(return_value=mock_decision)
        mock_team_cls.return_value = mock_team_instance

        with patch(
            "attune.healthcare.fhir.cds_hooks.CDSTeam",
            mock_team_cls,
            create=True,
        ):
            response = client.post(
                "/cds-services/attune-patient-view", json=sample_hook_request
            )

        body = response.json()
        for card in body["cards"]:
            assert card["source"]["label"] == "Attune CDS"

    def test_import_error_returns_info_card(
        self,
        client: TestClient,
        sample_hook_request: dict[str, Any],
    ) -> None:
        """Import failure for CDSTeam returns graceful informational card."""
        with patch.dict("sys.modules", {"attune.agents.healthcare.cds_team": None}):
            response = client.post(
                "/cds-services/attune-patient-view", json=sample_hook_request
            )

        assert response.status_code == 200
        body = response.json()
        assert len(body["cards"]) >= 1
        # The handler catches ImportError and returns a fallback card
        card = body["cards"][0]
        assert card["indicator"] == "info"


# ============================================================================
# _extract_vitals_from_prefetch Tests
# ============================================================================


class TestExtractVitalsFromPrefetch:
    """Tests for _extract_vitals_from_prefetch helper."""

    def test_none_prefetch_returns_empty(self) -> None:
        """None prefetch returns empty dict."""
        result = _extract_vitals_from_prefetch(None)
        assert result == {}

    def test_empty_prefetch_returns_empty(self) -> None:
        """Empty dict prefetch returns empty dict."""
        result = _extract_vitals_from_prefetch({})
        assert result == {}

    def test_bundle_with_observations(self) -> None:
        """Extracts vitals from FHIR Bundle of Observations."""
        prefetch = {
            "observations": {
                "resourceType": "Bundle",
                "entry": [
                    {
                        "resource": {
                            "resourceType": "Observation",
                            "code": {
                                "coding": [
                                    {"system": "http://loinc.org", "code": "8867-4"}
                                ]
                            },
                            "valueQuantity": {"value": 72, "unit": "bpm"},
                        }
                    },
                    {
                        "resource": {
                            "resourceType": "Observation",
                            "code": {
                                "coding": [
                                    {"system": "http://loinc.org", "code": "8480-6"}
                                ]
                            },
                            "valueQuantity": {"value": 120, "unit": "mmHg"},
                        }
                    },
                ],
            }
        }

        result = _extract_vitals_from_prefetch(prefetch)
        assert result["hr"] == 72
        assert result["systolic_bp"] == 120

    def test_single_observation_resource(self) -> None:
        """Extracts vitals from a single Observation (not a Bundle)."""
        prefetch = {
            "observations": {
                "resourceType": "Observation",
                "code": {
                    "coding": [{"system": "http://loinc.org", "code": "9279-1"}]
                },
                "valueQuantity": {"value": 18, "unit": "/min"},
            }
        }

        result = _extract_vitals_from_prefetch(prefetch)
        assert result["respiratory_rate"] == 18

    def test_list_of_observations(self) -> None:
        """Extracts vitals from a list of Observation dicts."""
        prefetch = {
            "observations": [
                {
                    "code": {
                        "coding": [{"system": "http://loinc.org", "code": "8310-5"}]
                    },
                    "valueQuantity": {"value": 98.6, "unit": "F"},
                },
                {
                    "code": {
                        "coding": [{"system": "http://loinc.org", "code": "2708-6"}]
                    },
                    "valueQuantity": {"value": 97, "unit": "%"},
                },
            ]
        }

        result = _extract_vitals_from_prefetch(prefetch)
        assert result["temp_f"] == 98.6
        assert result["o2_sat"] == 97

    def test_all_loinc_codes_extracted(self) -> None:
        """All supported LOINC codes are mapped to correct vital keys."""
        loinc_entries = [
            ("8867-4", 72, "hr"),
            ("8480-6", 120, "systolic_bp"),
            ("8462-4", 80, "diastolic_bp"),
            ("9279-1", 16, "respiratory_rate"),
            ("8310-5", 98.6, "temp_f"),
            ("2708-6", 98, "o2_sat"),
        ]

        entries = []
        for code, value, _ in loinc_entries:
            entries.append(
                {
                    "resource": {
                        "resourceType": "Observation",
                        "code": {"coding": [{"code": code}]},
                        "valueQuantity": {"value": value},
                    }
                }
            )

        prefetch = {"observations": {"resourceType": "Bundle", "entry": entries}}
        result = _extract_vitals_from_prefetch(prefetch)

        for _, expected_value, key in loinc_entries:
            assert result[key] == expected_value, f"Failed for vital key '{key}'"

    def test_observation_without_value_quantity_skipped(self) -> None:
        """Observations missing valueQuantity are skipped."""
        prefetch = {
            "observations": {
                "resourceType": "Bundle",
                "entry": [
                    {
                        "resource": {
                            "resourceType": "Observation",
                            "code": {
                                "coding": [{"code": "8867-4"}]
                            },
                            # No valueQuantity
                        }
                    },
                ],
            }
        }

        result = _extract_vitals_from_prefetch(prefetch)
        assert result == {}

    def test_unknown_loinc_code_ignored(self) -> None:
        """LOINC codes not in the mapping are silently ignored."""
        prefetch = {
            "observations": {
                "resourceType": "Bundle",
                "entry": [
                    {
                        "resource": {
                            "resourceType": "Observation",
                            "code": {"coding": [{"code": "99999-9"}]},
                            "valueQuantity": {"value": 42},
                        }
                    },
                ],
            }
        }

        result = _extract_vitals_from_prefetch(prefetch)
        assert result == {}

    def test_non_dict_entries_skipped(self) -> None:
        """Non-dict items in observation list are skipped without error."""
        prefetch = {
            "observations": [
                None,
                "invalid",
                42,
                {
                    "code": {"coding": [{"code": "8867-4"}]},
                    "valueQuantity": {"value": 80},
                },
            ]
        }

        result = _extract_vitals_from_prefetch(prefetch)
        assert result == {"hr": 80}

    def test_empty_bundle_returns_empty(self) -> None:
        """Bundle with no entries returns empty dict."""
        prefetch = {
            "observations": {
                "resourceType": "Bundle",
                "entry": [],
            }
        }

        result = _extract_vitals_from_prefetch(prefetch)
        assert result == {}

    def test_missing_observations_key_returns_empty(self) -> None:
        """Prefetch without 'observations' key returns empty dict."""
        prefetch = {"patient": {"resourceType": "Patient", "id": "123"}}
        result = _extract_vitals_from_prefetch(prefetch)
        assert result == {}


# ============================================================================
# _risk_to_indicator Tests
# ============================================================================


class TestRiskToIndicator:
    """Tests for _risk_to_indicator helper."""

    def test_critical_risk_maps_to_critical(self) -> None:
        """Critical risk level maps to 'critical' indicator."""
        assert _risk_to_indicator("critical") == "critical"

    def test_high_risk_maps_to_warning(self) -> None:
        """High risk level maps to 'warning' indicator."""
        assert _risk_to_indicator("high") == "warning"

    def test_moderate_risk_maps_to_info(self) -> None:
        """Moderate risk level maps to 'info' indicator."""
        assert _risk_to_indicator("moderate") == "info"

    def test_low_risk_maps_to_info(self) -> None:
        """Low risk level maps to 'info' indicator."""
        assert _risk_to_indicator("low") == "info"

    def test_unknown_risk_defaults_to_info(self) -> None:
        """Unrecognized risk level defaults to 'info' indicator."""
        assert _risk_to_indicator("unknown") == "info"
        assert _risk_to_indicator("") == "info"
        assert _risk_to_indicator("extreme") == "info"


# ============================================================================
# _build_cards_from_decision Tests
# ============================================================================


class TestBuildCardsFromDecision:
    """Tests for _build_cards_from_decision helper."""

    def test_primary_card_for_moderate_risk(self, mock_decision: MagicMock) -> None:
        """Moderate risk decision produces a primary card with info indicator."""
        cards = _build_cards_from_decision(mock_decision)

        assert len(cards) >= 1
        primary = cards[0]
        assert primary.indicator == "info"
        assert primary.source.label == "Attune CDS"
        assert primary.uuid is not None

    def test_primary_card_for_critical_risk(self, mock_critical_decision: MagicMock) -> None:
        """Critical risk decision produces a primary card with critical indicator."""
        cards = _build_cards_from_decision(mock_critical_decision)

        primary = cards[0]
        assert primary.indicator == "critical"

    def test_primary_card_summary_from_narrative(self, mock_decision: MagicMock) -> None:
        """Primary card summary comes from clinical reasoning narrative."""
        cards = _build_cards_from_decision(mock_decision)

        primary = cards[0]
        assert "vitals" in primary.summary.lower() or "tachycardia" in primary.summary.lower()

    def test_primary_card_summary_truncated_to_140(self) -> None:
        """Primary card summary is truncated to 140 characters per CDS spec."""
        decision = MagicMock()
        decision.overall_risk = "low"
        decision.confidence = 0.7
        reasoning = MagicMock()
        reasoning.narrative_summary = "A" * 200
        reasoning.differentials = []
        decision.clinical_reasoning = reasoning
        decision.recommendations = []
        decision.alerts = []
        decision.ecg_analysis = None

        cards = _build_cards_from_decision(decision)
        assert len(cards[0].summary) <= 140

    def test_suggestions_from_recommendations(self, mock_decision: MagicMock) -> None:
        """Recommendations are mapped to CDSSuggestion objects."""
        cards = _build_cards_from_decision(mock_decision)

        primary = cards[0]
        assert len(primary.suggestions) == 2
        labels = [s.label for s in primary.suggestions]
        assert "Repeat vitals in 30 minutes" in labels
        assert "Monitor fluid intake" in labels

    def test_suggestions_capped_at_five(self) -> None:
        """Only the first 5 recommendations become suggestions."""
        decision = MagicMock()
        decision.overall_risk = "low"
        decision.confidence = 0.8
        reasoning = MagicMock()
        reasoning.narrative_summary = "Assessment complete."
        reasoning.differentials = []
        decision.clinical_reasoning = reasoning
        decision.recommendations = [f"Recommendation {i}" for i in range(10)]
        decision.alerts = []
        decision.ecg_analysis = None

        cards = _build_cards_from_decision(decision)
        assert len(cards[0].suggestions) == 5

    def test_alert_cards_generated(self, mock_critical_decision: MagicMock) -> None:
        """Alerts produce additional cards after the primary card."""
        cards = _build_cards_from_decision(mock_critical_decision)

        alert_cards = [c for c in cards if c.source.label == "Attune CDS" and c != cards[0]]
        assert len(alert_cards) == 2

    def test_ecg_alert_gets_warning_indicator(self, mock_critical_decision: MagicMock) -> None:
        """Alert containing 'ECG' gets 'warning' indicator."""
        cards = _build_cards_from_decision(mock_critical_decision)

        ecg_alert = next(
            (c for c in cards if "ECG" in (c.summary or "") and c.source.label == "Attune CDS" and c != cards[0]),
            None,
        )
        assert ecg_alert is not None
        assert ecg_alert.indicator == "warning"

    def test_ecg_analysis_card_generated(self, mock_critical_decision: MagicMock) -> None:
        """ECG analysis produces a dedicated card with rhythm details."""
        cards = _build_cards_from_decision(mock_critical_decision)

        ecg_card = next(
            (c for c in cards if c.source.label == "Attune ECG Analysis"), None
        )
        assert ecg_card is not None
        assert "Sinus Tachycardia" in ecg_card.summary
        assert "115" in ecg_card.summary
        assert ecg_card.detail is not None
        assert "PVC Burden" in ecg_card.detail

    def test_ecg_card_warning_with_clinical_flags(
        self, mock_critical_decision: MagicMock
    ) -> None:
        """ECG card gets 'warning' indicator when clinical flags are present."""
        cards = _build_cards_from_decision(mock_critical_decision)

        ecg_card = next(
            (c for c in cards if c.source.label == "Attune ECG Analysis"), None
        )
        assert ecg_card is not None
        assert ecg_card.indicator == "warning"

    def test_ecg_card_info_without_clinical_flags(self) -> None:
        """ECG card gets 'info' indicator when no clinical flags."""
        decision = MagicMock()
        decision.overall_risk = "low"
        decision.confidence = 0.9
        reasoning = MagicMock()
        reasoning.narrative_summary = "Normal."
        reasoning.differentials = []
        decision.clinical_reasoning = reasoning
        decision.recommendations = []
        decision.alerts = []

        ecg = MagicMock()
        ecg.rhythm_classification = "normal_sinus"
        ecg.heart_rate = 72.0
        ecg.pvc_burden_pct = 0.0
        ecg.hrv_sdnn = 55.0
        ecg.clinical_flags = []
        decision.ecg_analysis = ecg

        cards = _build_cards_from_decision(decision)
        ecg_card = next(
            (c for c in cards if c.source.label == "Attune ECG Analysis"), None
        )
        assert ecg_card is not None
        assert ecg_card.indicator == "info"

    def test_no_clinical_reasoning_uses_risk_summary(self) -> None:
        """Without clinical reasoning, summary falls back to risk level."""
        decision = MagicMock()
        decision.overall_risk = "high"
        decision.confidence = 0.75
        decision.clinical_reasoning = None
        decision.recommendations = []
        decision.alerts = []
        decision.ecg_analysis = None

        cards = _build_cards_from_decision(decision)
        assert "HIGH" in cards[0].summary

    def test_detail_includes_differentials(self, mock_decision: MagicMock) -> None:
        """Card detail section includes differential considerations."""
        cards = _build_cards_from_decision(mock_decision)

        primary = cards[0]
        assert primary.detail is not None
        assert "Anxiety" in primary.detail
        assert "Dehydration" in primary.detail

    def test_all_cards_have_uuids(self, mock_critical_decision: MagicMock) -> None:
        """Every generated card has a non-empty UUID."""
        cards = _build_cards_from_decision(mock_critical_decision)

        for card in cards:
            assert card.uuid is not None
            assert len(card.uuid) > 0

    def test_all_cards_have_source(self, mock_critical_decision: MagicMock) -> None:
        """Every generated card has a source with a label."""
        cards = _build_cards_from_decision(mock_critical_decision)

        for card in cards:
            assert card.source is not None
            assert card.source.label is not None
            assert len(card.source.label) > 0


# ============================================================================
# Pydantic Model Tests
# ============================================================================


class TestCDSModels:
    """Tests for CDS Hooks Pydantic models."""

    def test_cds_source_default_label(self) -> None:
        """CDSSource defaults to 'Attune CDS' label."""
        source = CDSSource()
        assert source.label == "Attune CDS"

    def test_cds_card_default_indicator(self) -> None:
        """CDSCard defaults to 'info' indicator."""
        card = CDSCard(summary="Test card")
        assert card.indicator == "info"

    def test_cds_hook_response_empty_cards(self) -> None:
        """CDSHookResponse defaults to empty cards list."""
        response = CDSHookResponse()
        assert response.cards == []

    def test_cds_service_definition_fields(self) -> None:
        """CDSServiceDefinition validates required fields."""
        svc = CDSServiceDefinition(
            hook="patient-view",
            title="Test Service",
            description="A test CDS service.",
            id="test-service",
            prefetch={"patient": "Patient/{{context.patientId}}"},
        )
        assert svc.hook == "patient-view"
        assert svc.id == "test-service"
        assert svc.prefetch is not None

    def test_cds_hook_request_minimal(self) -> None:
        """CDSHookRequest accepts minimal required fields."""
        req = CDSHookRequest(
            hook="patient-view",
            hookInstance="abc-123",
        )
        assert req.hook == "patient-view"
        assert req.prefetch is None
        assert req.context == {}


# ============================================================================
# SERVICES Registry Tests
# ============================================================================


class TestServicesRegistry:
    """Tests for the module-level SERVICES dict."""

    def test_three_services_registered(self) -> None:
        """SERVICES dict contains exactly 3 entries."""
        assert len(SERVICES) == 3

    def test_service_keys_match_ids(self) -> None:
        """Each key in SERVICES matches the service's id field."""
        for key, svc in SERVICES.items():
            assert key == svc.id

    def test_all_services_have_prefetch(self) -> None:
        """Every registered service has a non-empty prefetch dict."""
        for svc in SERVICES.values():
            assert svc.prefetch is not None
            assert len(svc.prefetch) > 0

    def test_patient_view_prefetches_observations(self) -> None:
        """Patient-view service prefetches observations with vital-signs category."""
        svc = SERVICES["attune-patient-view"]
        assert "observations" in svc.prefetch
        assert "vital-signs" in svc.prefetch["observations"]
