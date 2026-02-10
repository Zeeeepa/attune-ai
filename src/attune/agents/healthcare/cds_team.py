"""CDS Team Coordinator for Healthcare Clinical Decision Support.

Orchestrates agents in two phases:
    Phase 1 (parallel): ClinicalProtocolMonitor + ECGAnalyzer
    Phase 2 (sequential): ClinicalReasoning with Phase 1 results

Copyright 2026 Smart-AI-Memory
Licensed under Apache 2.0
"""

from __future__ import annotations

import logging
import time
from typing import Any

from attune.agents.release.release_models import (
    REDIS_AVAILABLE,
    redis_lib,
)

from .cds_agents import ClinicalReasoningAgent, ECGAnalyzerAgent
from .cds_models import (
    DEFAULT_CDS_QUALITY_GATES,
    CDSDecision,
    CDSQualityGate,
)

logger = logging.getLogger(__name__)


class CDSTeam:
    """Coordinates CDS agent execution in two phases.

    Phase 1 (parallel):
        - ClinicalProtocolMonitor.analyze() — protocol compliance + trajectory
        - ECGAnalyzerAgent.process() — arrhythmia classification + HRV (if ECG data)

    Phase 2 (sequential):
        - ClinicalReasoningAgent.process() — narrative, differentials, workup

    Features:
        - Two-phase execution (gather -> reason)
        - Optional Redis coordination
        - Quality gate evaluation
        - Cost tracking across all agents

    Args:
        quality_gates: Custom quality gate thresholds
        redis_url: Optional Redis URL for coordination
        protocol_directory: Directory for clinical protocol definitions
        audit_logger: Optional CDSAuditLogger for decision audit trail
    """

    def __init__(
        self,
        quality_gates: dict[str, Any] | None = None,
        redis_url: str | None = None,
        protocol_directory: str | None = None,
        audit_logger: Any | None = None,
    ) -> None:
        self.quality_gates_config = {**DEFAULT_CDS_QUALITY_GATES}
        if quality_gates:
            self.quality_gates_config.update(quality_gates)

        self.audit_logger = audit_logger

        # Connect to Redis if available
        self.redis: Any | None = None
        if redis_url and REDIS_AVAILABLE:
            try:
                self.redis = redis_lib.from_url(redis_url)
                self.redis.ping()
                logger.info("CDS team connected to Redis")
            except Exception as e:  # noqa: BLE001
                # INTENTIONAL: Redis is optional for local development
                logger.info(f"Redis not available (non-fatal): {e}")
                self.redis = None

        self.protocol_directory = protocol_directory

        # Agents initialized per-request to ensure clean state
        self.total_cost = 0.0

    async def assess(
        self,
        patient_id: str,
        sensor_data: dict[str, Any],
        protocol_name: str,
        ecg_metrics: dict[str, Any] | None = None,
        patient_context: dict[str, Any] | None = None,
    ) -> CDSDecision:
        """Run full CDS assessment for a patient.

        Args:
            patient_id: Patient identifier
            sensor_data: Current vital signs (flat dict: hr, systolic_bp, etc.)
            protocol_name: Protocol to check (sepsis, cardiac, etc.)
            ecg_metrics: Optional ECG metrics from PhysioNet converter
            patient_context: Optional patient demographics/medications

        Returns:
            CDSDecision with consolidated assessment
        """
        start = time.time()
        self.total_cost = 0.0
        agent_results = []

        # =====================================================================
        # Phase 1: Gather (parallel)
        # =====================================================================

        # Task 1a: Protocol monitor analysis
        monitor_result = await self._run_protocol_monitor(
            patient_id, sensor_data, protocol_name,
        )

        protocol_compliance = monitor_result.get("protocol_compliance", {})
        trajectory = monitor_result.get("trajectory", {})
        alerts = monitor_result.get("alerts", [])
        recommendations = monitor_result.get("recommendations", [])
        current_vitals = monitor_result.get("current_vitals", sensor_data)

        # Task 1b: ECG analysis (only if ECG data provided)
        ecg_agent_result = None
        ecg_analysis = None
        if ecg_metrics:
            ecg_agent = ECGAnalyzerAgent(redis_client=self.redis)
            ecg_agent_result = ecg_agent.process({
                "ecg_metrics": ecg_metrics,
                "patient_context": patient_context or {},
            })
            ecg_analysis = ecg_agent.result_to_ecg_analysis(ecg_agent_result)
            agent_results.append(ecg_agent_result)
            self.total_cost += ecg_agent_result.cost

            # Add ECG flags to alerts
            for flag in ecg_analysis.clinical_flags:
                alerts.append({
                    "type": "ecg_flag",
                    "severity": "warning",
                    "message": f"ECG: {flag}",
                })

        # =====================================================================
        # Phase 2: Reason (sequential — needs Phase 1 results)
        # =====================================================================

        reasoning_agent = ClinicalReasoningAgent(redis_client=self.redis)
        reasoning_context = {
            "protocol_compliance": protocol_compliance,
            "trajectory": trajectory,
            "ecg_analysis": ecg_agent_result.findings if ecg_agent_result else {},
            "current_vitals": current_vitals,
            "protocol_name": protocol_name,
        }
        reasoning_result = reasoning_agent.process(reasoning_context)
        clinical_reasoning = reasoning_agent.result_to_clinical_reasoning(reasoning_result)
        agent_results.append(reasoning_result)
        self.total_cost += reasoning_result.cost

        # Add reasoning recommendations to the list
        for item in clinical_reasoning.recommended_workup:
            if item not in recommendations:
                recommendations.append(item)

        # =====================================================================
        # Quality Gates
        # =====================================================================

        quality_gates = self._evaluate_quality_gates(
            sensor_data, protocol_compliance, agent_results,
        )

        # =====================================================================
        # Synthesize Decision
        # =====================================================================

        # Flatten alerts to strings
        alert_strings = []
        for a in alerts:
            if isinstance(a, dict):
                alert_strings.append(a.get("message", str(a)))
            else:
                alert_strings.append(str(a))

        elapsed = time.time() - start

        decision = CDSDecision(
            patient_id=patient_id,
            protocol_compliance=protocol_compliance,
            trajectory=trajectory,
            ecg_analysis=ecg_analysis,
            clinical_reasoning=clinical_reasoning,
            quality_gates=quality_gates,
            agent_results=agent_results,
            alerts=alert_strings,
            recommendations=recommendations,
            overall_risk=clinical_reasoning.risk_level,
            confidence=clinical_reasoning.confidence,
            cost=self.total_cost,
        )

        # Log to audit trail if logger is configured
        if self.audit_logger is not None:
            try:
                self.audit_logger.log_decision(
                    decision,
                    request_context={
                        "protocol_name": protocol_name,
                        "has_ecg": ecg_metrics is not None,
                        "execution_time_ms": round(elapsed * 1000, 1),
                    },
                )
            except Exception as e:  # noqa: BLE001
                # INTENTIONAL: Audit failure should not break CDS assessment
                logger.error(f"Audit logging failed (non-fatal): {e}")

        return decision

    async def _run_protocol_monitor(
        self,
        patient_id: str,
        sensor_data: dict[str, Any],
        protocol_name: str,
    ) -> dict[str, Any]:
        """Run ClinicalProtocolMonitor.analyze() as async.

        Args:
            patient_id: Patient identifier
            sensor_data: Vital signs dict
            protocol_name: Protocol name

        Returns:
            Monitor analysis result dict
        """
        try:
            from attune_healthcare.monitors.clinical_protocol_monitor import (
                ClinicalProtocolMonitor,
            )

            monitor = ClinicalProtocolMonitor(self.protocol_directory)
            result = await monitor.analyze({
                "patient_id": patient_id,
                "sensor_data": sensor_data,
                "protocol_name": protocol_name,
            })
            return result

        except ImportError:
            logger.warning(
                "attune_healthcare not installed. "
                "Install with: pip install attune-healthcare"
            )
            return {
                "error": "attune_healthcare not installed",
                "protocol_compliance": {},
                "trajectory": {},
                "alerts": [],
                "recommendations": [],
                "current_vitals": sensor_data,
            }
        except Exception as e:
            logger.error(f"Protocol monitor failed: {e}")
            return {
                "error": str(e),
                "protocol_compliance": {},
                "trajectory": {},
                "alerts": [],
                "recommendations": [],
                "current_vitals": sensor_data,
            }

    def _evaluate_quality_gates(
        self,
        sensor_data: dict[str, Any],
        protocol_compliance: dict[str, Any],
        agent_results: list[Any],
    ) -> list[CDSQualityGate]:
        """Evaluate CDS quality gates.

        Args:
            sensor_data: Input vital signs
            protocol_compliance: Protocol compliance result
            agent_results: List of CDSAgentResult

        Returns:
            List of evaluated CDSQualityGate objects
        """
        gates: list[CDSQualityGate] = []

        # Gate 1: Data completeness
        expected_vitals = {"hr", "systolic_bp", "respiratory_rate", "temp_f", "o2_sat"}
        present_vitals = {k for k in sensor_data if k in expected_vitals}
        completeness = len(present_vitals) / len(expected_vitals) if expected_vitals else 0.0
        threshold = self.quality_gates_config["min_data_completeness"]

        gates.append(
            CDSQualityGate(
                name="Data Completeness",
                threshold=threshold,
                actual=completeness,
                passed=completeness >= threshold,
                clinical=True,
            )
        )

        # Gate 2: Analysis confidence
        avg_confidence = 0.0
        if agent_results:
            avg_confidence = sum(r.confidence for r in agent_results) / len(agent_results)
        conf_threshold = self.quality_gates_config["min_confidence"]

        gates.append(
            CDSQualityGate(
                name="Analysis Confidence",
                threshold=conf_threshold,
                actual=avg_confidence,
                passed=avg_confidence >= conf_threshold,
                clinical=True,
            )
        )

        return gates
