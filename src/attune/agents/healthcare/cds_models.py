"""Data models and configuration for Healthcare CDS Agent Team.

Enums, configuration constants, and dataclasses for ECG analysis,
clinical reasoning, quality gates, and CDS decision reports.

Copyright 2026 Smart-AI-Memory
Licensed under Apache 2.0
"""

from __future__ import annotations

import logging
import os
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from attune.agents.release.release_models import (
    Tier,
)

logger = logging.getLogger(__name__)


# =============================================================================
# Configuration
# =============================================================================

# LLM mode: "real" uses API calls, "simulated" uses rule-based analysis
CDS_LLM_MODE = os.getenv("CDS_LLM_MODE", "simulated")

# Default quality gate thresholds for CDS assessments
DEFAULT_CDS_QUALITY_GATES = {
    "min_data_completeness": 0.6,  # At least 60% of expected vitals present
    "min_confidence": 0.5,  # Minimum confidence for clinical output
}


# =============================================================================
# Data Models
# =============================================================================


@dataclass
class ECGAnalysisResult:
    """Result from ECG analysis.

    Attributes:
        heart_rate: Mean heart rate (bpm)
        hrv_sdnn: Heart rate variability SDNN proxy (ms)
        rhythm_classification: Sinus rhythm classification
        arrhythmia_events: Total arrhythmia events detected
        pvc_burden_pct: Premature ventricular complex burden (%)
        clinical_flags: List of clinical concern flags
        confidence: Analysis confidence (0.0-1.0)
        score: Health score (0-100, higher is healthier)
        waveform_features: Optional dict of morphological features from
            ECG waveform analysis (QRS width, ST segment, QT interval, etc.)
    """

    heart_rate: float = 0.0
    hrv_sdnn: float = 0.0
    rhythm_classification: str = "unknown"
    arrhythmia_events: int = 0
    pvc_burden_pct: float = 0.0
    clinical_flags: list[str] = field(default_factory=list)
    confidence: float = 0.0
    score: float = 100.0
    waveform_features: dict[str, Any] | None = None


@dataclass
class ClinicalReasoningResult:
    """Result from clinical reasoning.

    Attributes:
        narrative_summary: Clinical narrative with CDS Advisory prefix
        differentials: Differential considerations for the condition
        recommended_workup: Recommended diagnostic workup
        risk_level: Overall risk assessment (low, moderate, high, critical)
        confidence: Reasoning confidence (0.0-1.0)
    """

    narrative_summary: str = ""
    differentials: list[str] = field(default_factory=list)
    recommended_workup: list[str] = field(default_factory=list)
    risk_level: str = "low"
    confidence: float = 0.0


@dataclass
class CDSAgentResult:
    """Result from an individual CDS agent.

    Attributes:
        agent_id: Unique agent identifier
        role: Human-readable role name
        success: Whether the agent completed successfully
        tier_used: Final tier used (after any escalation)
        findings: Structured findings dict
        score: Numeric score (0-100)
        confidence: Confidence in the result (0.0-1.0)
        cost: LLM API cost in USD
        execution_time_ms: Wall-clock time in milliseconds
    """

    agent_id: str
    role: str
    success: bool
    tier_used: Tier
    findings: dict[str, Any] = field(default_factory=dict)
    score: float = 0.0
    confidence: float = 0.0
    cost: float = 0.0
    execution_time_ms: float = 0.0


@dataclass
class CDSQualityGate:
    """Quality gate for CDS assessment.

    Attributes:
        name: Gate identifier
        threshold: Minimum acceptable value
        actual: Measured value
        passed: Whether gate passed
        clinical: Whether this gate has clinical significance
        message: Human-readable status message
    """

    name: str
    threshold: float
    actual: float = 0.0
    passed: bool = False
    clinical: bool = True
    message: str = ""

    def __post_init__(self) -> None:
        """Generate message if not provided."""
        if not self.message:
            status = "PASS" if self.passed else "FAIL"
            self.message = (
                f"{self.name}: {status} "
                f"(actual: {self.actual:.2f}, threshold: {self.threshold:.2f})"
            )


@dataclass
class CDSDecision:
    """Aggregated CDS decision report.

    Attributes:
        patient_id: Patient identifier
        protocol_compliance: Protocol compliance results from ClinicalProtocolMonitor
        trajectory: Vital sign trajectory prediction
        ecg_analysis: ECG analysis result (None if no ECG data)
        clinical_reasoning: Clinical reasoning result
        quality_gates: Quality gate evaluations
        agent_results: Individual agent outputs
        alerts: Clinical alerts
        recommendations: Clinical recommendations
        overall_risk: Overall risk level (low, moderate, high, critical)
        confidence: Overall confidence (0.0-1.0)
        cost: Total LLM API cost in USD
        timestamp: Decision timestamp
    """

    patient_id: str
    protocol_compliance: dict[str, Any] = field(default_factory=dict)
    trajectory: dict[str, Any] = field(default_factory=dict)
    ecg_analysis: ECGAnalysisResult | None = None
    clinical_reasoning: ClinicalReasoningResult | None = None
    quality_gates: list[CDSQualityGate] = field(default_factory=list)
    agent_results: list[CDSAgentResult] = field(default_factory=list)
    alerts: list[str] = field(default_factory=list)
    recommendations: list[str] = field(default_factory=list)
    overall_risk: str = "low"
    confidence: float = 0.0
    cost: float = 0.0
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> dict[str, Any]:
        """Convert decision to dictionary for JSON serialization."""
        return {
            "patient_id": self.patient_id,
            "protocol_compliance": self.protocol_compliance,
            "trajectory": self.trajectory,
            "ecg_analysis": {
                "heart_rate": self.ecg_analysis.heart_rate,
                "hrv_sdnn": self.ecg_analysis.hrv_sdnn,
                "rhythm_classification": self.ecg_analysis.rhythm_classification,
                "arrhythmia_events": self.ecg_analysis.arrhythmia_events,
                "pvc_burden_pct": self.ecg_analysis.pvc_burden_pct,
                "clinical_flags": self.ecg_analysis.clinical_flags,
                "confidence": self.ecg_analysis.confidence,
                "score": self.ecg_analysis.score,
                "waveform_features": self.ecg_analysis.waveform_features,
            }
            if self.ecg_analysis
            else None,
            "clinical_reasoning": {
                "narrative_summary": self.clinical_reasoning.narrative_summary,
                "differentials": self.clinical_reasoning.differentials,
                "recommended_workup": self.clinical_reasoning.recommended_workup,
                "risk_level": self.clinical_reasoning.risk_level,
                "confidence": self.clinical_reasoning.confidence,
            }
            if self.clinical_reasoning
            else None,
            "quality_gates": [
                {
                    "name": g.name,
                    "threshold": g.threshold,
                    "actual": g.actual,
                    "passed": g.passed,
                    "clinical": g.clinical,
                    "message": g.message,
                }
                for g in self.quality_gates
            ],
            "agent_results": {
                r.role: {
                    "success": r.success,
                    "score": r.score,
                    "confidence": r.confidence,
                    "tier_used": r.tier_used.value,
                    "cost": r.cost,
                    "findings": r.findings,
                }
                for r in self.agent_results
            },
            "alerts": self.alerts,
            "recommendations": self.recommendations,
            "overall_risk": self.overall_risk,
            "confidence": self.confidence,
            "cost": self.cost,
            "timestamp": self.timestamp,
        }

    def format_console_output(self) -> str:
        """Format decision for console display."""
        lines = []
        lines.append("=" * 70)
        lines.append("CLINICAL DECISION SUPPORT REPORT")
        lines.append("=" * 70)
        lines.append("")

        lines.append(f"Patient: {self.patient_id}")
        lines.append(f"Risk Level: {self.overall_risk.upper()}")
        lines.append(f"Confidence: {self.confidence:.0%}")
        lines.append(f"Cost: ${self.cost:.4f}")
        lines.append("")

        # Alerts
        if self.alerts:
            lines.append("-" * 70)
            lines.append("ALERTS")
            lines.append("-" * 70)
            for alert in self.alerts:
                lines.append(f"  ! {alert}")
            lines.append("")

        # Protocol compliance
        if self.protocol_compliance:
            lines.append("-" * 70)
            lines.append("PROTOCOL COMPLIANCE")
            lines.append("-" * 70)
            activated = self.protocol_compliance.get("activated", False)
            score = self.protocol_compliance.get("score", 0)
            lines.append(f"  Activated: {activated}")
            lines.append(f"  Score: {score}")
            deviations = self.protocol_compliance.get("deviations", [])
            for dev in deviations:
                lines.append(f"  - {dev}")
            lines.append("")

        # ECG Analysis
        if self.ecg_analysis:
            lines.append("-" * 70)
            lines.append("ECG ANALYSIS")
            lines.append("-" * 70)
            lines.append(f"  Heart Rate: {self.ecg_analysis.heart_rate:.0f} bpm")
            lines.append(f"  Rhythm: {self.ecg_analysis.rhythm_classification}")
            lines.append(f"  PVC Burden: {self.ecg_analysis.pvc_burden_pct:.1f}%")
            lines.append(f"  HRV (SDNN): {self.ecg_analysis.hrv_sdnn:.1f} ms")
            lines.append(f"  Score: {self.ecg_analysis.score:.0f}/100")
            if self.ecg_analysis.clinical_flags:
                lines.append(f"  Flags: {', '.join(self.ecg_analysis.clinical_flags)}")
            lines.append("")

        # Clinical Reasoning
        if self.clinical_reasoning:
            lines.append("-" * 70)
            lines.append("CLINICAL REASONING")
            lines.append("-" * 70)
            lines.append(f"  Risk: {self.clinical_reasoning.risk_level.upper()}")
            if self.clinical_reasoning.narrative_summary:
                lines.append(f"  {self.clinical_reasoning.narrative_summary}")
            if self.clinical_reasoning.differentials:
                lines.append("  Differentials:")
                for diff in self.clinical_reasoning.differentials:
                    lines.append(f"    - {diff}")
            if self.clinical_reasoning.recommended_workup:
                lines.append("  Workup:")
                for item in self.clinical_reasoning.recommended_workup:
                    lines.append(f"    - {item}")
            lines.append("")

        # Quality Gates
        if self.quality_gates:
            lines.append("-" * 70)
            lines.append("QUALITY GATES")
            lines.append("-" * 70)
            for gate in self.quality_gates:
                icon = "PASS" if gate.passed else "FAIL"
                lines.append(f"  [{icon}] {gate.message}")
            lines.append("")

        # Recommendations
        if self.recommendations:
            lines.append("-" * 70)
            lines.append("RECOMMENDATIONS")
            lines.append("-" * 70)
            for rec in self.recommendations:
                lines.append(f"  - {rec}")
            lines.append("")

        lines.append("=" * 70)
        return "\n".join(lines)
