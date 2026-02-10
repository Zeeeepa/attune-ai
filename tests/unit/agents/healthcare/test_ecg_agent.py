"""Tests for ECG Analyzer Agent.

Copyright 2026 Smart-AI-Memory
Licensed under Apache 2.0
"""


from src.attune.agents.healthcare.cds_agents import ECGAnalyzerAgent
from src.attune.agents.healthcare.cds_models import ECGAnalysisResult, Tier


class TestECGRuleBasedAnalysis:
    """Test rule-based ECG analysis."""

    def setup_method(self):
        """Create agent for each test."""
        self.agent = ECGAnalyzerAgent()

    def test_normal_sinus_rhythm(self):
        """Test normal sinus rhythm classification."""
        findings = self.agent._rule_based_analysis({
            "hr_mean": 80, "pvc_burden_pct": 1.0, "rr_std_ms": 80, "arrhythmia_events": 5,
        })
        assert findings["rhythm_classification"] == "normal_sinus"
        assert findings["score"] == 100.0
        assert findings["clinical_flags"] == []

    def test_sinus_tachycardia(self):
        """Test sinus tachycardia detection."""
        findings = self.agent._rule_based_analysis({
            "hr_mean": 110, "pvc_burden_pct": 0.5, "rr_std_ms": 60,
        })
        assert findings["rhythm_classification"] == "sinus_tachycardia"
        assert "TACHYCARDIA" in findings["clinical_flags"]

    def test_severe_tachycardia(self):
        """Test severe tachycardia detection."""
        findings = self.agent._rule_based_analysis({
            "hr_mean": 145, "pvc_burden_pct": 0.5, "rr_std_ms": 30,
        })
        assert "SEVERE_TACHYCARDIA" in findings["clinical_flags"]
        assert findings["score"] < 80

    def test_sinus_bradycardia(self):
        """Test sinus bradycardia detection."""
        findings = self.agent._rule_based_analysis({
            "hr_mean": 45, "pvc_burden_pct": 0.5, "rr_std_ms": 100,
        })
        assert findings["rhythm_classification"] == "sinus_bradycardia"
        assert "BRADYCARDIA" in findings["clinical_flags"]

    def test_mild_bradycardia(self):
        """Test mild bradycardia (50-60 bpm)."""
        findings = self.agent._rule_based_analysis({
            "hr_mean": 55, "pvc_burden_pct": 0.5, "rr_std_ms": 80,
        })
        assert findings["rhythm_classification"] == "sinus_bradycardia"
        assert "BRADYCARDIA" in findings["clinical_flags"]
        # Mild bradycardia should have smaller score deduction
        assert findings["score"] > 90

    def test_frequent_pvcs(self):
        """Test frequent PVC detection."""
        findings = self.agent._rule_based_analysis({
            "hr_mean": 90, "pvc_burden_pct": 15, "rr_std_ms": 60,
        })
        assert findings["rhythm_classification"] == "frequent_pvcs"
        assert "HIGH_PVC_BURDEN" in findings["clinical_flags"]

    def test_moderate_pvcs(self):
        """Test moderate PVC burden detection."""
        findings = self.agent._rule_based_analysis({
            "hr_mean": 80, "pvc_burden_pct": 7, "rr_std_ms": 60,
        })
        assert "MODERATE_PVC_BURDEN" in findings["clinical_flags"]
        # Rhythm should still be normal_sinus since PVC < 10%
        assert findings["rhythm_classification"] == "normal_sinus"

    def test_frequent_ectopy(self):
        """Test frequent ectopy flag."""
        findings = self.agent._rule_based_analysis({
            "hr_mean": 80, "pvc_burden_pct": 1, "rr_std_ms": 80, "arrhythmia_events": 200,
        })
        assert "FREQUENT_ECTOPY" in findings["clinical_flags"]

    def test_wide_hrv(self):
        """Test wide HRV detection."""
        findings = self.agent._rule_based_analysis({
            "hr_mean": 80, "pvc_burden_pct": 1, "rr_std_ms": 250,
        })
        assert "WIDE_HRV" in findings["clinical_flags"]

    def test_narrow_hrv(self):
        """Test narrow HRV detection."""
        findings = self.agent._rule_based_analysis({
            "hr_mean": 80, "pvc_burden_pct": 1, "rr_std_ms": 10,
        })
        assert "NARROW_HRV" in findings["clinical_flags"]

    def test_score_never_below_zero(self):
        """Test score is clamped at 0."""
        findings = self.agent._rule_based_analysis({
            "hr_mean": 150, "pvc_burden_pct": 20, "rr_std_ms": 5, "arrhythmia_events": 500,
        })
        assert findings["score"] >= 0.0

    def test_confidence_low_when_no_hr(self):
        """Test confidence is low when heart rate is 0."""
        findings = self.agent._rule_based_analysis({
            "hr_mean": 0, "pvc_burden_pct": 0, "rr_std_ms": 0,
        })
        assert findings["confidence"] < 0.5

    def test_confidence_reduced_without_hrv(self):
        """Test confidence is reduced when no HRV data."""
        findings = self.agent._rule_based_analysis({
            "hr_mean": 80, "pvc_burden_pct": 1,
        })
        assert findings["confidence"] <= 0.7


class TestECGAgentProcess:
    """Test ECG agent process method."""

    def setup_method(self):
        """Create agent for each test."""
        self.agent = ECGAnalyzerAgent()

    def test_process_success_with_ecg_data(self):
        """Test process returns success with valid ECG data."""
        result = self.agent.process({
            "ecg_metrics": {"hr_mean": 80, "pvc_burden_pct": 1, "rr_std_ms": 80},
        })
        assert result.success
        assert result.tier_used == Tier.CHEAP
        assert result.score == 100.0
        assert result.role == "ECG Analyzer"

    def test_process_fails_without_ecg_data(self):
        """Test process fails when no ECG data provided."""
        result = self.agent.process({})
        assert not result.success
        assert result.confidence == 0.0

    def test_process_simulated_mode_no_api_calls(self):
        """Test simulated mode makes zero API calls."""
        agent = ECGAnalyzerAgent()
        assert agent.llm_client is None  # No LLM in simulated mode
        result = agent.process({
            "ecg_metrics": {"hr_mean": 80, "pvc_burden_pct": 1, "rr_std_ms": 80},
        })
        assert result.cost == 0.0

    def test_result_to_ecg_analysis_conversion(self):
        """Test conversion from CDSAgentResult to ECGAnalysisResult."""
        result = self.agent.process({
            "ecg_metrics": {"hr_mean": 110, "pvc_burden_pct": 2, "rr_std_ms": 50},
        })
        ecg = self.agent.result_to_ecg_analysis(result)
        assert isinstance(ecg, ECGAnalysisResult)
        assert ecg.heart_rate == 110
        assert ecg.rhythm_classification == "sinus_tachycardia"
