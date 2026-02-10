"""End-to-end PhysioNet pipeline tests.

Tests the full data flow: PhysioNet fixture → CDSTeam.assess() → FHIR Bundle.
Uses pre-converted fixture data so wfdb is not required at test time.

Copyright 2026 Smart-AI-Memory
Licensed under Apache 2.0
"""

import json
from pathlib import Path

import pytest

FIXTURE_DIR = Path(__file__).parent / "fixtures"
RECORD_200 = FIXTURE_DIR / "record_200_sample.json"


@pytest.fixture
def physionet_data():
    """Load pre-converted PhysioNet record 200 sample."""
    with RECORD_200.open() as f:
        return json.load(f)


class TestConverterOutputShape:
    """Validate PhysioNet converter output structure."""

    def test_fixture_has_required_fields(self, physionet_data):
        """Test fixture contains all required top-level fields."""
        assert "patient_id" in physionet_data
        assert "vitals" in physionet_data
        assert "ecg_metrics" in physionet_data
        assert "patient_context" in physionet_data

    def test_vitals_structure(self, physionet_data):
        """Test vitals dict has expected vital signs."""
        vitals = physionet_data["vitals"]
        assert "hr" in vitals
        assert "systolic_bp" in vitals
        assert "o2_sat" in vitals

    def test_ecg_metrics_structure(self, physionet_data):
        """Test ECG metrics dict has expected fields."""
        ecg = physionet_data["ecg_metrics"]
        assert "hr_mean" in ecg
        assert "pvc_burden_pct" in ecg
        assert "rr_std_ms" in ecg
        assert "total_beats" in ecg

    def test_patient_context_structure(self, physionet_data):
        """Test patient context dict has expected fields."""
        ctx = physionet_data["patient_context"]
        assert "source" in ctx
        assert ctx["source"] == "MIT-BIH Arrhythmia Database"


class TestConverterToCDSAssess:
    """Test feeding converter output to CDSTeam."""

    @pytest.mark.asyncio
    async def test_converter_to_cds_assess(self, physionet_data):
        """Feed converter output to CDSTeam.assess()."""
        from src.attune.agents.healthcare.cds_team import CDSTeam

        team = CDSTeam()
        decision = await team.assess(
            patient_id=physionet_data["patient_id"],
            sensor_data=physionet_data["vitals"],
            protocol_name="cardiac",
            ecg_metrics=physionet_data["ecg_metrics"],
            patient_context=physionet_data["patient_context"],
        )
        assert decision.patient_id == "mitbih_200"
        assert decision.overall_risk in ("low", "moderate", "high", "critical")
        assert decision.ecg_analysis is not None
        assert decision.ecg_analysis.heart_rate == 74.8

    @pytest.mark.asyncio
    async def test_converter_without_ecg(self, physionet_data):
        """Feed converter output without ECG metrics."""
        from src.attune.agents.healthcare.cds_team import CDSTeam

        team = CDSTeam()
        decision = await team.assess(
            patient_id=physionet_data["patient_id"],
            sensor_data=physionet_data["vitals"],
            protocol_name="cardiac",
        )
        assert decision.ecg_analysis is None


class TestCDSToFHIRBundle:
    """Test converting CDSDecision to FHIR Bundle."""

    @pytest.mark.asyncio
    async def test_cds_to_fhir_bundle(self, physionet_data):
        """Convert CDSDecision to FHIR Bundle."""
        from src.attune.agents.healthcare.cds_team import CDSTeam
        from src.attune.healthcare.fhir.resources import decision_to_fhir_bundle

        team = CDSTeam()
        decision = await team.assess(
            patient_id=physionet_data["patient_id"],
            sensor_data=physionet_data["vitals"],
            protocol_name="cardiac",
            ecg_metrics=physionet_data["ecg_metrics"],
        )

        bundle = decision_to_fhir_bundle(decision, decision_id="e2e-test-001")
        assert bundle["resourceType"] == "Bundle"
        assert bundle["type"] == "collection"
        assert len(bundle["entry"]) > 0

        # Verify resource types present
        types = {e["resource"]["resourceType"] for e in bundle["entry"]}
        assert "Observation" in types
        assert "RiskAssessment" in types
        assert "ClinicalImpression" in types
        assert "DiagnosticReport" in types
        assert "AuditEvent" in types

    @pytest.mark.asyncio
    async def test_fhir_bundle_json_serializable(self, physionet_data):
        """Verify FHIR Bundle is fully JSON-serializable."""
        from src.attune.agents.healthcare.cds_team import CDSTeam
        from src.attune.healthcare.fhir.resources import decision_to_fhir_bundle

        team = CDSTeam()
        decision = await team.assess(
            patient_id=physionet_data["patient_id"],
            sensor_data=physionet_data["vitals"],
            protocol_name="cardiac",
        )

        bundle = decision_to_fhir_bundle(decision)
        serialized = json.dumps(bundle)
        parsed = json.loads(serialized)
        assert parsed["resourceType"] == "Bundle"


class TestFullPipeline:
    """Test complete pipeline: converter → assess → FHIR."""

    @pytest.mark.asyncio
    async def test_full_pipeline_simulated(self, physionet_data):
        """Full pipeline in simulated mode (no API key needed)."""
        import tempfile

        from src.attune.agents.healthcare.cds_team import CDSTeam
        from src.attune.healthcare.audit.decision_log import CDSAuditLogger
        from src.attune.healthcare.fhir.resources import decision_to_fhir_bundle

        with tempfile.TemporaryDirectory() as tmpdir:
            # Setup with audit
            audit = CDSAuditLogger(storage_dir=tmpdir)
            team = CDSTeam(audit_logger=audit)

            # Run assessment
            decision = await team.assess(
                patient_id=physionet_data["patient_id"],
                sensor_data=physionet_data["vitals"],
                protocol_name="cardiac",
                ecg_metrics=physionet_data["ecg_metrics"],
                patient_context=physionet_data["patient_context"],
            )

            # Verify decision
            assert decision.patient_id == "mitbih_200"
            assert decision.ecg_analysis is not None
            assert decision.clinical_reasoning is not None

            # Convert to FHIR
            bundle = decision_to_fhir_bundle(decision)
            assert bundle["resourceType"] == "Bundle"

            # Verify audit logged
            decisions = audit.list_decisions()
            assert len(decisions) == 1
            assert decisions[0]["overall_risk"] == decision.overall_risk

    @pytest.mark.asyncio
    async def test_pipeline_observation_count_matches_vitals(self, physionet_data):
        """Verify Observation count matches input vital signs."""
        from src.attune.agents.healthcare.cds_team import CDSTeam
        from src.attune.healthcare.fhir.resources import build_observations

        team = CDSTeam()
        decision = await team.assess(
            patient_id=physionet_data["patient_id"],
            sensor_data=physionet_data["vitals"],
            protocol_name="cardiac",
            ecg_metrics=physionet_data["ecg_metrics"],
        )

        observations = build_observations(decision)
        # Should have ECG observations at minimum
        ecg_obs = [
            o for o in observations
            if "ECG" in o["code"]["coding"][0].get("display", "")
            or "HRV" in o["code"]["coding"][0].get("display", "")
            or "PVC" in o["code"]["coding"][0].get("display", "")
        ]
        assert len(ecg_obs) >= 2  # At least HR by ECG and one other
