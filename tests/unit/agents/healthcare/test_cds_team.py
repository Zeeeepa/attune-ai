"""Tests for CDS Team Coordinator.

Copyright 2026 Smart-AI-Memory
Licensed under Apache 2.0
"""

import json

import pytest

from src.attune.agents.healthcare.cds_models import CDSDecision
from src.attune.agents.healthcare.cds_team import CDSTeam


@pytest.fixture
def team():
    """Create a CDSTeam instance."""
    return CDSTeam()


@pytest.mark.asyncio
async def test_assess_basic_without_ecg(team):
    """Test basic assessment without ECG data."""
    decision = await team.assess(
        patient_id="test-001",
        sensor_data={"hr": 80, "systolic_bp": 120, "respiratory_rate": 16, "o2_sat": 98},
        protocol_name="cardiac",
    )
    assert isinstance(decision, CDSDecision)
    assert decision.patient_id == "test-001"
    assert decision.ecg_analysis is None
    assert len(decision.agent_results) == 1  # Only reasoning agent


@pytest.mark.asyncio
async def test_assess_with_ecg_metrics(team):
    """Test assessment with ECG metrics runs both agents."""
    decision = await team.assess(
        patient_id="test-002",
        sensor_data={"hr": 110, "systolic_bp": 85, "respiratory_rate": 24, "o2_sat": 92},
        protocol_name="cardiac",
        ecg_metrics={"hr_mean": 110, "pvc_burden_pct": 3.0, "rr_std_ms": 50},
    )
    assert decision.ecg_analysis is not None
    assert len(decision.agent_results) == 2  # ECG + reasoning
    assert decision.ecg_analysis.heart_rate == 110


@pytest.mark.asyncio
async def test_ecg_agent_not_executed_without_metrics(team):
    """Test ECG agent is NOT executed without ecg_metrics."""
    decision = await team.assess(
        patient_id="test-003",
        sensor_data={"hr": 80},
        protocol_name="sepsis",
    )
    assert decision.ecg_analysis is None
    # Check no ECG agent in results
    ecg_agents = [r for r in decision.agent_results if "ECG" in r.role]
    assert len(ecg_agents) == 0


@pytest.mark.asyncio
async def test_phase2_receives_phase1_outputs(team):
    """Test Phase 2 reasoning receives Phase 1 data."""
    decision = await team.assess(
        patient_id="test-004",
        sensor_data={"hr": 145, "systolic_bp": 82, "respiratory_rate": 26, "o2_sat": 88},
        protocol_name="cardiac",
        ecg_metrics={"hr_mean": 145, "pvc_burden_pct": 3.5, "rr_std_ms": 40},
    )
    # Clinical reasoning should reference ECG flags in narrative
    assert decision.clinical_reasoning is not None
    assert decision.clinical_reasoning.risk_level in ("high", "critical")


@pytest.mark.asyncio
async def test_to_dict_is_json_serializable(team):
    """Test CDSDecision.to_dict() produces valid JSON."""
    decision = await team.assess(
        patient_id="test-005",
        sensor_data={"hr": 80, "systolic_bp": 120},
        protocol_name="cardiac",
    )
    d = decision.to_dict()
    serialized = json.dumps(d)
    assert isinstance(serialized, str)
    parsed = json.loads(serialized)
    assert parsed["patient_id"] == "test-005"


@pytest.mark.asyncio
async def test_quality_gates_evaluated(team):
    """Test quality gates are evaluated."""
    decision = await team.assess(
        patient_id="test-006",
        sensor_data={"hr": 80, "systolic_bp": 120, "respiratory_rate": 16, "o2_sat": 98, "temp_f": 98.6},
        protocol_name="cardiac",
    )
    assert len(decision.quality_gates) == 2
    gate_names = {g.name for g in decision.quality_gates}
    assert "Data Completeness" in gate_names
    assert "Analysis Confidence" in gate_names


@pytest.mark.asyncio
async def test_data_completeness_gate_passes_with_all_vitals(team):
    """Test data completeness gate passes with all expected vitals."""
    decision = await team.assess(
        patient_id="test-007",
        sensor_data={"hr": 80, "systolic_bp": 120, "respiratory_rate": 16, "o2_sat": 98, "temp_f": 98.6},
        protocol_name="cardiac",
    )
    data_gate = next(g for g in decision.quality_gates if g.name == "Data Completeness")
    assert data_gate.passed
    assert data_gate.actual == 1.0


@pytest.mark.asyncio
async def test_data_completeness_gate_with_partial_vitals(team):
    """Test data completeness gate with partial vitals."""
    decision = await team.assess(
        patient_id="test-008",
        sensor_data={"hr": 80},  # Only 1 of 5 expected vitals
        protocol_name="cardiac",
    )
    data_gate = next(g for g in decision.quality_gates if g.name == "Data Completeness")
    assert data_gate.actual == 0.2  # 1/5


@pytest.mark.asyncio
async def test_cost_tracking(team):
    """Test cost tracking across agents in simulated mode."""
    decision = await team.assess(
        patient_id="test-009",
        sensor_data={"hr": 80},
        protocol_name="cardiac",
        ecg_metrics={"hr_mean": 80, "pvc_burden_pct": 1, "rr_std_ms": 80},
    )
    # Simulated mode should have zero cost
    assert decision.cost == 0.0


@pytest.mark.asyncio
async def test_alerts_include_ecg_flags(team):
    """Test alerts include ECG clinical flags."""
    decision = await team.assess(
        patient_id="test-010",
        sensor_data={"hr": 145, "systolic_bp": 82},
        protocol_name="cardiac",
        ecg_metrics={"hr_mean": 145, "pvc_burden_pct": 15, "rr_std_ms": 30},
    )
    ecg_alerts = [a for a in decision.alerts if "ECG" in a]
    assert len(ecg_alerts) > 0


@pytest.mark.asyncio
async def test_recommendations_include_workup(team):
    """Test recommendations include clinical workup items."""
    decision = await team.assess(
        patient_id="test-011",
        sensor_data={"hr": 110, "systolic_bp": 85},
        protocol_name="sepsis",
    )
    # Sepsis workup should include some items
    assert len(decision.recommendations) > 0


@pytest.mark.asyncio
async def test_custom_quality_gates():
    """Test custom quality gate thresholds."""
    team = CDSTeam(quality_gates={"min_data_completeness": 0.9, "min_confidence": 0.8})
    decision = await team.assess(
        patient_id="test-012",
        sensor_data={"hr": 80},  # Only 1/5 vitals
        protocol_name="cardiac",
    )
    data_gate = next(g for g in decision.quality_gates if g.name == "Data Completeness")
    assert not data_gate.passed  # 0.2 < 0.9 threshold
