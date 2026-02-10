"""Tests for CDS data models and configuration.

Copyright 2026 Smart-AI-Memory
Licensed under Apache 2.0
"""

import json

from src.attune.agents.healthcare.cds_models import (
    CDS_LLM_MODE,
    DEFAULT_CDS_QUALITY_GATES,
    CDSAgentResult,
    CDSDecision,
    CDSQualityGate,
    ClinicalReasoningResult,
    ECGAnalysisResult,
    Tier,
)


class TestConfiguration:
    """Test CDS configuration constants."""

    def test_cds_llm_mode_defaults_to_simulated(self):
        """Test that CDS_LLM_MODE defaults to simulated."""
        assert CDS_LLM_MODE == "simulated"

    def test_default_quality_gates_has_expected_keys(self):
        """Test default quality gates have required keys."""
        assert "min_data_completeness" in DEFAULT_CDS_QUALITY_GATES
        assert "min_confidence" in DEFAULT_CDS_QUALITY_GATES

    def test_default_quality_gates_values_are_reasonable(self):
        """Test default quality gate values are in valid ranges."""
        assert 0.0 < DEFAULT_CDS_QUALITY_GATES["min_data_completeness"] <= 1.0
        assert 0.0 < DEFAULT_CDS_QUALITY_GATES["min_confidence"] <= 1.0


class TestECGAnalysisResult:
    """Test ECGAnalysisResult dataclass."""

    def test_construction_with_defaults(self):
        """Test default construction."""
        result = ECGAnalysisResult()
        assert result.heart_rate == 0.0
        assert result.rhythm_classification == "unknown"
        assert result.clinical_flags == []
        assert result.score == 100.0

    def test_construction_with_values(self):
        """Test construction with specific values."""
        result = ECGAnalysisResult(
            heart_rate=82.0,
            hrv_sdnn=45.0,
            rhythm_classification="normal_sinus",
            arrhythmia_events=5,
            pvc_burden_pct=1.2,
            clinical_flags=["TACHYCARDIA"],
            confidence=0.9,
            score=85.0,
        )
        assert result.heart_rate == 82.0
        assert result.clinical_flags == ["TACHYCARDIA"]


class TestClinicalReasoningResult:
    """Test ClinicalReasoningResult dataclass."""

    def test_construction_with_defaults(self):
        """Test default construction."""
        result = ClinicalReasoningResult()
        assert result.narrative_summary == ""
        assert result.differentials == []
        assert result.risk_level == "low"

    def test_construction_with_values(self):
        """Test construction with clinical data."""
        result = ClinicalReasoningResult(
            narrative_summary="CDS Advisory: Patient stable",
            differentials=["UTI", "Pneumonia"],
            recommended_workup=["CBC", "Lactate"],
            risk_level="high",
            confidence=0.85,
        )
        assert len(result.differentials) == 2
        assert result.risk_level == "high"


class TestCDSAgentResult:
    """Test CDSAgentResult dataclass."""

    def test_construction(self):
        """Test construction with required fields."""
        result = CDSAgentResult(
            agent_id="ecg-1",
            role="ECG Analyzer",
            success=True,
            tier_used=Tier.CHEAP,
        )
        assert result.success
        assert result.tier_used == Tier.CHEAP
        assert result.cost == 0.0

    def test_fields_default_correctly(self):
        """Test optional fields default to expected values."""
        result = CDSAgentResult(
            agent_id="test",
            role="Test",
            success=False,
            tier_used=Tier.CAPABLE,
        )
        assert result.findings == {}
        assert result.score == 0.0
        assert result.execution_time_ms == 0.0


class TestCDSQualityGate:
    """Test CDSQualityGate dataclass."""

    def test_passing_gate(self):
        """Test gate that passes."""
        gate = CDSQualityGate(
            name="Data Completeness",
            threshold=0.6,
            actual=0.8,
            passed=True,
        )
        assert gate.passed
        assert "PASS" in gate.message

    def test_failing_gate(self):
        """Test gate that fails."""
        gate = CDSQualityGate(
            name="Confidence",
            threshold=0.5,
            actual=0.3,
            passed=False,
        )
        assert not gate.passed
        assert "FAIL" in gate.message

    def test_post_init_generates_message(self):
        """Test __post_init__ generates message when not provided."""
        gate = CDSQualityGate(name="Test", threshold=0.5, actual=0.7, passed=True)
        assert gate.message  # Should not be empty
        assert "Test" in gate.message

    def test_custom_message_preserved(self):
        """Test that custom message is not overwritten."""
        gate = CDSQualityGate(
            name="Test",
            threshold=0.5,
            actual=0.7,
            passed=True,
            message="Custom message",
        )
        assert gate.message == "Custom message"


class TestCDSDecision:
    """Test CDSDecision dataclass."""

    def _make_decision(self) -> CDSDecision:
        """Create a test decision with all fields populated."""
        return CDSDecision(
            patient_id="test-001",
            protocol_compliance={"activated": True, "score": 3},
            trajectory={"state": "deteriorating"},
            ecg_analysis=ECGAnalysisResult(
                heart_rate=110.0,
                rhythm_classification="sinus_tachycardia",
                clinical_flags=["TACHYCARDIA"],
                score=75.0,
                confidence=0.9,
            ),
            clinical_reasoning=ClinicalReasoningResult(
                narrative_summary="CDS Advisory: Protocol activated",
                differentials=["Sepsis", "Pneumonia"],
                recommended_workup=["Blood cultures", "Lactate"],
                risk_level="high",
                confidence=0.85,
            ),
            quality_gates=[
                CDSQualityGate(name="Data", threshold=0.6, actual=0.8, passed=True),
            ],
            agent_results=[
                CDSAgentResult(
                    agent_id="ecg-1",
                    role="ECG Analyzer",
                    success=True,
                    tier_used=Tier.CHEAP,
                    score=75.0,
                ),
            ],
            alerts=["Protocol activated", "ECG: TACHYCARDIA"],
            recommendations=["Blood cultures", "Lactate"],
            overall_risk="high",
            confidence=0.85,
            cost=0.0,
        )

    def test_to_dict_is_json_serializable(self):
        """Test to_dict produces JSON-serializable output."""
        decision = self._make_decision()
        d = decision.to_dict()
        serialized = json.dumps(d)
        assert isinstance(serialized, str)
        parsed = json.loads(serialized)
        assert parsed["patient_id"] == "test-001"

    def test_to_dict_includes_all_keys(self):
        """Test to_dict includes all expected keys."""
        decision = self._make_decision()
        d = decision.to_dict()
        expected_keys = {
            "patient_id", "protocol_compliance", "trajectory",
            "ecg_analysis", "clinical_reasoning", "quality_gates",
            "agent_results", "alerts", "recommendations",
            "overall_risk", "confidence", "cost", "timestamp",
        }
        assert set(d.keys()) == expected_keys

    def test_to_dict_with_no_ecg(self):
        """Test to_dict when ecg_analysis is None."""
        decision = CDSDecision(patient_id="test")
        d = decision.to_dict()
        assert d["ecg_analysis"] is None
        assert d["clinical_reasoning"] is None

    def test_format_console_output_contains_header(self):
        """Test format_console_output includes report header."""
        decision = self._make_decision()
        output = decision.format_console_output()
        assert "CLINICAL DECISION SUPPORT REPORT" in output
        assert "test-001" in output
        assert "HIGH" in output

    def test_format_console_output_includes_ecg(self):
        """Test format_console_output includes ECG section."""
        decision = self._make_decision()
        output = decision.format_console_output()
        assert "ECG ANALYSIS" in output
        assert "sinus_tachycardia" in output

    def test_format_console_output_includes_reasoning(self):
        """Test format_console_output includes clinical reasoning."""
        decision = self._make_decision()
        output = decision.format_console_output()
        assert "CLINICAL REASONING" in output
        assert "CDS Advisory" in output

    def test_format_console_output_minimal(self):
        """Test format_console_output with minimal data."""
        decision = CDSDecision(patient_id="minimal")
        output = decision.format_console_output()
        assert "minimal" in output
        assert "CLINICAL DECISION SUPPORT REPORT" in output
