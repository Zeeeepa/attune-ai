"""Healthcare Clinical Decision Support Agent Team.

A multi-agent system for clinical decision support combining:
    - ECG analysis from PhysioNet-derived metrics
    - Clinical reasoning with protocol compliance context
    - Coordinated assessment via CDSTeam

Agents:
    - ECG Analyzer: Classifies arrhythmias, computes HRV, flags clinical concerns
    - Clinical Reasoning: Contextualizes outputs with narratives and recommendations

Collaboration: Two-phase execution (gather -> reason)
Tier Strategy: Progressive (CHEAP -> CAPABLE -> PREMIUM)
Dual Mode: Rule-based (simulated) and LLM-enhanced (real)
"""

from .cds_agents import (
    CDSAgent,
    ClinicalReasoningAgent,
    ECGAnalyzerAgent,
)
from .cds_models import (
    CDS_LLM_MODE,
    CDSAgentResult,
    CDSDecision,
    CDSQualityGate,
    ClinicalReasoningResult,
    ECGAnalysisResult,
)
from .cds_team import CDSTeam

__all__ = [
    "CDSAgent",
    "CDSAgentResult",
    "CDSDecision",
    "CDSQualityGate",
    "CDSTeam",
    "CDS_LLM_MODE",
    "ClinicalReasoningAgent",
    "ClinicalReasoningResult",
    "ECGAnalyzerAgent",
    "ECGAnalysisResult",
]
