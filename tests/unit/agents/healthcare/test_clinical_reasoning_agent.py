"""Tests for Clinical Reasoning Agent.

Copyright 2026 Smart-AI-Memory
Licensed under Apache 2.0
"""


from src.attune.agents.healthcare.cds_agents import ClinicalReasoningAgent
from src.attune.agents.healthcare.cds_models import ClinicalReasoningResult, Tier


class TestTemplateReasoning:
    """Test template-based clinical reasoning."""

    def setup_method(self):
        """Create agent for each test."""
        self.agent = ClinicalReasoningAgent()

    def test_sepsis_activated_critical(self):
        """Test reasoning for activated sepsis with critical trajectory."""
        findings = self.agent._template_reasoning(
            protocol_compliance={"activated": True, "score": 3, "deviations": ["SBP<=100"]},
            trajectory={"state": "critical"},
            ecg_analysis={"clinical_flags": ["TACHYCARDIA"]},
            current_vitals={"hr": 110, "systolic_bp": 85},
            protocol_name="sepsis",
        )
        assert findings["risk_level"] == "critical"
        assert "CDS Advisory:" in findings["narrative_summary"]
        assert "ACTIVATED" in findings["narrative_summary"]
        assert "Blood cultures" in str(findings["recommended_workup"])
        assert "Urinary tract infection" in findings["differentials"]

    def test_cardiac_stable_not_activated(self):
        """Test reasoning for stable cardiac, not activated."""
        findings = self.agent._template_reasoning(
            protocol_compliance={"activated": False, "score": 0},
            trajectory={"state": "stable"},
            ecg_analysis={},
            current_vitals={"hr": 75},
            protocol_name="cardiac",
        )
        assert findings["risk_level"] == "low"
        assert "not met" in findings["narrative_summary"]

    def test_respiratory_deteriorating(self):
        """Test reasoning for deteriorating respiratory patient."""
        findings = self.agent._template_reasoning(
            protocol_compliance={"activated": True, "score": 2},
            trajectory={"state": "deteriorating", "time_to_critical_hours": 3.5},
            ecg_analysis={},
            current_vitals={"respiratory_rate": 28, "o2_sat": 89},
            protocol_name="respiratory",
        )
        assert findings["risk_level"] in ("high", "critical")
        assert "deteriorating" in findings["narrative_summary"]
        assert "3.5" in findings["narrative_summary"]
        assert "Arterial blood gas" in str(findings["recommended_workup"])
        assert "Pulmonary embolism" in findings["differentials"]

    def test_post_operative_protocol(self):
        """Test post-operative protocol differentials and workup."""
        findings = self.agent._template_reasoning(
            protocol_compliance={"activated": True, "score": 1},
            trajectory={"state": "stable"},
            ecg_analysis={},
            current_vitals={},
            protocol_name="post_operative",
        )
        assert "Surgical site infection" in findings["differentials"]
        assert "Surgical wound assessment" in str(findings["recommended_workup"])

    def test_unknown_protocol_provides_defaults(self):
        """Test unknown protocol name provides generic differentials."""
        findings = self.agent._template_reasoning(
            protocol_compliance={"activated": False},
            trajectory={"state": "stable"},
            ecg_analysis={},
            current_vitals={},
            protocol_name="unknown_protocol",
        )
        assert "Non-specific clinical finding" in findings["differentials"]

    def test_ecg_flags_included_in_narrative(self):
        """Test ECG flags appear in narrative."""
        findings = self.agent._template_reasoning(
            protocol_compliance={"activated": False},
            trajectory={"state": "stable"},
            ecg_analysis={"clinical_flags": ["BRADYCARDIA", "WIDE_HRV"]},
            current_vitals={},
            protocol_name="cardiac",
        )
        assert "BRADYCARDIA" in findings["narrative_summary"]
        assert "WIDE_HRV" in findings["narrative_summary"]

    def test_improving_trajectory(self):
        """Test improving trajectory reflected in narrative."""
        findings = self.agent._template_reasoning(
            protocol_compliance={"activated": False},
            trajectory={"state": "improving"},
            ecg_analysis={},
            current_vitals={},
            protocol_name="sepsis",
        )
        assert "improvement" in findings["narrative_summary"]
        assert findings["risk_level"] == "low"

    def test_confidence_increases_with_more_data(self):
        """Test confidence is higher with more data available."""
        # Minimal data
        findings_minimal = self.agent._template_reasoning(
            protocol_compliance={},
            trajectory={},
            ecg_analysis={},
            current_vitals={},
            protocol_name="cardiac",
        )

        # Full data
        findings_full = self.agent._template_reasoning(
            protocol_compliance={"activated": True, "score": 2},
            trajectory={"state": "stable"},
            ecg_analysis={"clinical_flags": ["TACHYCARDIA"]},
            current_vitals={"hr": 110},
            protocol_name="cardiac",
        )

        assert findings_full["confidence"] > findings_minimal["confidence"]

    def test_risk_level_mapping(self):
        """Test risk score to level mapping."""
        # Low risk: no activation, stable, no ECG flags
        findings = self.agent._template_reasoning(
            protocol_compliance={"activated": False},
            trajectory={"state": "stable"},
            ecg_analysis={},
            current_vitals={},
            protocol_name="cardiac",
        )
        assert findings["risk_level"] == "low"

        # Critical risk: activated + critical + ECG flags
        findings = self.agent._template_reasoning(
            protocol_compliance={"activated": True},
            trajectory={"state": "critical"},
            ecg_analysis={"clinical_flags": ["SEVERE_TACHYCARDIA", "HIGH_PVC_BURDEN"]},
            current_vitals={},
            protocol_name="cardiac",
        )
        assert findings["risk_level"] == "critical"


class TestClinicalReasoningProcess:
    """Test Clinical Reasoning agent process method."""

    def setup_method(self):
        """Create agent for each test."""
        self.agent = ClinicalReasoningAgent()

    def test_process_returns_success(self):
        """Test process returns success."""
        result = self.agent.process({
            "protocol_compliance": {"activated": False},
            "trajectory": {"state": "stable"},
            "ecg_analysis": {},
            "current_vitals": {"hr": 75},
            "protocol_name": "cardiac",
        })
        assert result.success
        assert result.tier_used == Tier.CHEAP

    def test_process_simulated_no_api_calls(self):
        """Test simulated mode makes no API calls."""
        assert self.agent.llm_client is None
        result = self.agent.process({
            "protocol_compliance": {},
            "trajectory": {},
            "protocol_name": "sepsis",
        })
        assert result.cost == 0.0

    def test_result_to_clinical_reasoning_conversion(self):
        """Test conversion to ClinicalReasoningResult."""
        result = self.agent.process({
            "protocol_compliance": {"activated": True, "score": 3},
            "trajectory": {"state": "critical"},
            "protocol_name": "sepsis",
        })
        cr = self.agent.result_to_clinical_reasoning(result)
        assert isinstance(cr, ClinicalReasoningResult)
        assert cr.risk_level in ("high", "critical")
        assert len(cr.differentials) > 0
        assert "CDS Advisory:" in cr.narrative_summary

    def test_score_correlates_with_risk(self):
        """Test score is lower for higher risk."""
        result_low = self.agent.process({
            "protocol_compliance": {"activated": False},
            "trajectory": {"state": "stable"},
            "protocol_name": "cardiac",
        })
        result_high = self.agent.process({
            "protocol_compliance": {"activated": True, "score": 3},
            "trajectory": {"state": "critical"},
            "ecg_analysis": {"clinical_flags": ["SEVERE_TACHYCARDIA"]},
            "protocol_name": "cardiac",
        })
        assert result_low.score > result_high.score
