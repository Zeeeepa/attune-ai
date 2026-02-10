"""CDS agents for Healthcare Clinical Decision Support.

Base CDSAgent class with progressive tier escalation, and concrete agent
implementations for ECG analysis and clinical reasoning.

Copyright 2026 Smart-AI-Memory
Licensed under Apache 2.0
"""

from __future__ import annotations

import json
import logging
import os
import time
from typing import Any
from uuid import uuid4

from attune.agents.release.release_models import (
    ANTHROPIC_AVAILABLE,
    MODEL_CONFIG,
    Tier,
    anthropic,
)

from .cds_models import (
    CDS_LLM_MODE,
    CDSAgentResult,
    ClinicalReasoningResult,
    ECGAnalysisResult,
)
from .cds_parsing import parse_clinical_response, parse_ecg_response

logger = logging.getLogger(__name__)


# =============================================================================
# Base CDS Agent with Progressive Tier Escalation
# =============================================================================


class CDSAgent:
    """Base agent with CHEAP -> CAPABLE -> PREMIUM escalation for CDS.

    Features:
        - Progressive tier escalation on failure
        - Optional Redis heartbeats (no-op when unavailable)
        - Real Anthropic API calls with rule-based fallback
        - Multi-strategy response parsing

    Args:
        agent_id: Unique identifier for this agent instance
        role: Human-readable role name
        redis_client: Optional Redis connection for coordination
    """

    def __init__(
        self,
        agent_id: str,
        role: str,
        redis_client: Any | None = None,
    ) -> None:
        self.agent_id = agent_id
        self.role = role
        self.redis = redis_client
        self.current_tier = Tier.CHEAP
        self.llm_client: Any | None = None
        self.total_cost = 0.0
        self.total_tokens = 0

        # Initialize LLM client if available and in real mode
        if ANTHROPIC_AVAILABLE and CDS_LLM_MODE == "real":
            api_key = os.getenv("ANTHROPIC_API_KEY")
            if api_key:
                self.llm_client = anthropic.Anthropic(api_key=api_key)
                logger.info(f"Agent {agent_id}: LLM client initialized")
            else:
                logger.info(f"Agent {agent_id}: No API key, using rule-based mode")

    def _register_heartbeat(self, status: str = "running", task: str = "") -> None:
        """Register agent liveness in Redis (no-op if unavailable)."""
        if self.redis is None:
            return
        try:
            key = f"cds:agent:heartbeat:{self.agent_id}"
            self.redis.hset(
                key,
                mapping={
                    "agent_id": self.agent_id,
                    "role": self.role,
                    "status": status,
                    "current_task": task,
                    "tier": self.current_tier.value,
                    "last_beat": time.time(),
                },
            )
            self.redis.expire(key, 60)
        except Exception as e:  # noqa: BLE001
            # INTENTIONAL: Redis is optional, don't fail on connection issues
            logger.debug(f"Heartbeat failed (non-fatal): {e}")

    def _call_llm(self, prompt: str, system: str, tier: Tier) -> tuple[str, dict[str, Any]]:
        """Call LLM with tier-appropriate model.

        Args:
            prompt: User prompt
            system: System prompt
            tier: Model tier to use

        Returns:
            Tuple of (response_text, metadata)
        """
        if not self.llm_client:
            return "", {"model": "rule_based", "cost": 0.0}

        model = MODEL_CONFIG[tier.value]

        try:
            response = self.llm_client.messages.create(
                model=model,
                max_tokens=1024,
                system=system,
                messages=[{"role": "user", "content": prompt}],
            )

            input_tokens = response.usage.input_tokens
            output_tokens = response.usage.output_tokens

            pricing = {
                "cheap": {"input": 0.80, "output": 4.00},
                "capable": {"input": 3.00, "output": 15.00},
                "premium": {"input": 15.00, "output": 75.00},
            }
            tier_pricing = pricing[tier.value]
            cost = (
                input_tokens * tier_pricing["input"] / 1_000_000
                + output_tokens * tier_pricing["output"] / 1_000_000
            )

            self.total_cost += cost
            self.total_tokens += input_tokens + output_tokens

            response_text = ""
            if response.content:
                first_block = response.content[0]
                if hasattr(first_block, "text"):
                    response_text = first_block.text  # type: ignore[union-attr]

            return response_text, {
                "model": model,
                "input_tokens": input_tokens,
                "output_tokens": output_tokens,
                "cost": cost,
            }

        except Exception as e:
            logger.error(f"LLM call failed for {self.role}: {e}")
            return "", {"model": "fallback", "cost": 0.0, "error": str(e)}

    def process(self, context: dict[str, Any]) -> CDSAgentResult:
        """Process with progressive tier escalation.

        Args:
            context: Input context dict (agent-specific fields)

        Returns:
            CDSAgentResult with findings and score
        """
        start = time.time()

        # Try CHEAP first
        self.current_tier = Tier.CHEAP
        self._register_heartbeat(status="running", task="Analyzing")

        success, findings = self._execute_tier(context, Tier.CHEAP)

        # Escalate to CAPABLE if needed
        if not success:
            self.current_tier = Tier.CAPABLE
            self._register_heartbeat(status="escalating", task="Retrying")
            success, findings = self._execute_tier(context, Tier.CAPABLE)

        # Escalate to PREMIUM if still failing
        if not success:
            self.current_tier = Tier.PREMIUM
            self._register_heartbeat(status="escalating", task="Premium retry")
            success, findings = self._execute_tier(context, Tier.PREMIUM)

        execution_time = (time.time() - start) * 1000

        self._register_heartbeat(status="idle", task="")

        return CDSAgentResult(
            agent_id=self.agent_id,
            role=self.role,
            success=success,
            tier_used=self.current_tier,
            findings=findings,
            score=findings.get("score", 0.0),
            confidence=findings.get("confidence", 0.8 if success else 0.3),
            cost=self.total_cost,
            execution_time_ms=execution_time,
        )

    def _execute_tier(
        self, context: dict[str, Any], tier: Tier
    ) -> tuple[bool, dict[str, Any]]:
        """Execute at specific tier. Override in subclasses.

        Args:
            context: Input context
            tier: Current tier

        Returns:
            Tuple of (success, findings_dict)
        """
        raise NotImplementedError


# =============================================================================
# ECG Analyzer Agent
# =============================================================================


class ECGAnalyzerAgent(CDSAgent):
    """Classifies arrhythmias from PhysioNet-derived metrics.

    Rule-based analysis always runs; LLM interpretation is optional.

    Input context keys:
        ecg_metrics: Dict with hr_mean, hr_min, hr_max, total_beats,
            arrhythmia_events, pvc_burden_pct, rr_mean_ms, rr_std_ms
        patient_context: Optional dict with age, sex, medications
    """

    SYSTEM_PROMPT = (
        "You are a clinical ECG analyst. Analyze the following ECG metrics and "
        "patient context. Provide a clinical interpretation. Respond in JSON:\n"
        '{"heart_rate": N, "rhythm_classification": "...", "pvc_burden_pct": N, '
        '"hrv_sdnn": N, "clinical_flags": ["..."], "score": 0-100, '
        '"confidence": 0.0-1.0, "interpretation": "..."}'
    )

    def __init__(self, redis_client: Any | None = None) -> None:
        super().__init__(
            agent_id=f"ecg-analyzer-{uuid4().hex[:8]}",
            role="ECG Analyzer",
            redis_client=redis_client,
        )

    def _execute_tier(
        self, context: dict[str, Any], tier: Tier
    ) -> tuple[bool, dict[str, Any]]:
        """Run ECG analysis."""
        ecg_metrics = context.get("ecg_metrics", {})
        patient_context = context.get("patient_context", {})

        if not ecg_metrics:
            return False, {
                "error": "No ECG metrics provided",
                "score": 0.0,
                "confidence": 0.0,
            }

        # Rule-based analysis always runs
        findings = self._rule_based_analysis(ecg_metrics)
        findings["mode"] = "rule_based"
        findings["tier"] = tier.value

        # LLM enhancement if available
        if self.llm_client and CDS_LLM_MODE == "real":
            prompt = (
                f"ECG Metrics:\n{json.dumps(ecg_metrics, indent=2)}\n\n"
                f"Patient Context:\n{json.dumps(patient_context, indent=2)}\n\n"
                f"Rule-based findings:\n{json.dumps(findings, indent=2)}"
            )
            response_text, _meta = self._call_llm(prompt, self.SYSTEM_PROMPT, tier)
            if response_text:
                llm_findings = parse_ecg_response(response_text)
                if "parse_error" not in llm_findings:
                    # Merge LLM interpretation into findings
                    if "interpretation" in llm_findings:
                        findings["llm_interpretation"] = llm_findings["interpretation"]
                    if "clinical_flags" in llm_findings:
                        # Union of rule-based and LLM flags
                        existing = set(findings.get("clinical_flags", []))
                        existing.update(llm_findings["clinical_flags"])
                        findings["clinical_flags"] = sorted(existing)
                    findings["mode"] = "llm_enhanced"

        return True, findings

    def _rule_based_analysis(self, ecg_metrics: dict[str, Any]) -> dict[str, Any]:
        """Perform rule-based ECG analysis.

        Args:
            ecg_metrics: Dict with hr_mean, pvc_burden_pct, rr_std_ms, etc.

        Returns:
            Analysis findings dict
        """
        hr_mean = ecg_metrics.get("hr_mean", 0.0)
        pvc_burden = ecg_metrics.get("pvc_burden_pct", 0.0)
        rr_std = ecg_metrics.get("rr_std_ms", 0.0)
        arrhythmia_events = ecg_metrics.get("arrhythmia_events", 0)

        clinical_flags: list[str] = []
        score = 100.0

        # HR assessment
        if hr_mean < 50:
            rhythm = "sinus_bradycardia"
            clinical_flags.append("BRADYCARDIA")
            score -= 15
        elif hr_mean < 60:
            rhythm = "sinus_bradycardia"
            clinical_flags.append("BRADYCARDIA")
            score -= 5
        elif hr_mean <= 100:
            rhythm = "normal_sinus"
        elif hr_mean <= 120:
            rhythm = "sinus_tachycardia"
            clinical_flags.append("TACHYCARDIA")
            score -= 10
        else:
            rhythm = "sinus_tachycardia"
            clinical_flags.append("SEVERE_TACHYCARDIA")
            score -= 25

        # PVC burden assessment
        if pvc_burden > 10:
            rhythm = "frequent_pvcs"
            clinical_flags.append("HIGH_PVC_BURDEN")
            score -= 20
        elif pvc_burden > 5:
            clinical_flags.append("MODERATE_PVC_BURDEN")
            score -= 10

        # Frequent ectopy
        if arrhythmia_events > 100:
            clinical_flags.append("FREQUENT_ECTOPY")
            score -= 10

        # HRV assessment (SDNN proxy from rr_std_ms)
        if rr_std > 0:
            if rr_std > 200:
                clinical_flags.append("WIDE_HRV")
                score -= 10
            elif rr_std < 20:
                clinical_flags.append("NARROW_HRV")
                score -= 15

        score = max(0.0, score)

        # Confidence based on data quality
        confidence = 0.9
        if hr_mean == 0:
            confidence = 0.1
        elif not rr_std:
            confidence = 0.7

        return {
            "heart_rate": hr_mean,
            "hrv_sdnn": rr_std,
            "rhythm_classification": rhythm,
            "arrhythmia_events": arrhythmia_events,
            "pvc_burden_pct": pvc_burden,
            "clinical_flags": clinical_flags,
            "score": score,
            "confidence": confidence,
        }

    def result_to_ecg_analysis(self, result: CDSAgentResult) -> ECGAnalysisResult:
        """Convert CDSAgentResult to ECGAnalysisResult.

        Args:
            result: Agent result from process()

        Returns:
            Typed ECGAnalysisResult
        """
        f = result.findings
        return ECGAnalysisResult(
            heart_rate=f.get("heart_rate", 0.0),
            hrv_sdnn=f.get("hrv_sdnn", 0.0),
            rhythm_classification=f.get("rhythm_classification", "unknown"),
            arrhythmia_events=f.get("arrhythmia_events", 0),
            pvc_burden_pct=f.get("pvc_burden_pct", 0.0),
            clinical_flags=f.get("clinical_flags", []),
            confidence=result.confidence,
            score=result.score,
        )


# =============================================================================
# Clinical Reasoning Agent
# =============================================================================


class ClinicalReasoningAgent(CDSAgent):
    """Produces clinical narrative, differentials, and recommended workup.

    Template-based (simulated) + Anthropic API (real).

    Input context keys:
        protocol_compliance: Dict from ClinicalProtocolMonitor
        trajectory: Dict with state, time_to_critical, trends
        ecg_analysis: Optional ECGAnalysisResult-like dict
        current_vitals: Dict with hr, systolic_bp, etc.
        protocol_name: Protocol name (sepsis, cardiac, etc.)
    """

    SYSTEM_PROMPT = (
        "You are a clinical decision support advisor. Analyze the following clinical "
        "data and provide a structured assessment. ALWAYS prefix your narrative with "
        "'CDS Advisory:' to indicate this is decision support, not a diagnosis.\n\n"
        "Respond in JSON:\n"
        '{"narrative_summary": "CDS Advisory: ...", '
        '"differentials": ["..."], "recommended_workup": ["..."], '
        '"risk_level": "low|moderate|high|critical", "confidence": 0.0-1.0}'
    )

    # Differentials by protocol
    PROTOCOL_DIFFERENTIALS = {
        "sepsis": [
            "Urinary tract infection",
            "Pneumonia",
            "Intra-abdominal infection",
            "Cellulitis / soft tissue infection",
            "Bacteremia (primary)",
        ],
        "cardiac": [
            "Acute coronary syndrome",
            "Heart failure exacerbation",
            "Arrhythmia (new onset)",
            "Pulmonary embolism",
            "Hypertensive emergency",
        ],
        "respiratory": [
            "Pulmonary embolism",
            "COPD exacerbation",
            "Pneumonia",
            "Acute respiratory distress syndrome",
            "Pneumothorax",
        ],
        "post_operative": [
            "Surgical site infection",
            "Post-operative hemorrhage",
            "Venous thromboembolism",
            "Atelectasis / pneumonia",
            "Anastomotic leak",
        ],
    }

    # Workup by protocol
    PROTOCOL_WORKUP = {
        "sepsis": [
            "Blood cultures x2",
            "Serum lactate",
            "CBC with differential",
            "Comprehensive metabolic panel",
            "Urinalysis with culture",
            "Procalcitonin",
        ],
        "cardiac": [
            "12-lead ECG",
            "Troponin (serial)",
            "BNP / NT-proBNP",
            "Chest X-ray",
            "Echocardiogram",
            "CBC, BMP",
        ],
        "respiratory": [
            "Arterial blood gas",
            "Chest X-ray",
            "CT pulmonary angiography (if PE suspected)",
            "D-dimer",
            "CBC with differential",
            "Sputum culture",
        ],
        "post_operative": [
            "CBC with differential",
            "Comprehensive metabolic panel",
            "Surgical wound assessment",
            "CT with contrast (if anastomotic leak suspected)",
            "Blood cultures (if febrile)",
            "Duplex ultrasound (if DVT suspected)",
        ],
    }

    def __init__(self, redis_client: Any | None = None) -> None:
        super().__init__(
            agent_id=f"clinical-reasoning-{uuid4().hex[:8]}",
            role="Clinical Reasoning",
            redis_client=redis_client,
        )

    def _execute_tier(
        self, context: dict[str, Any], tier: Tier
    ) -> tuple[bool, dict[str, Any]]:
        """Run clinical reasoning."""
        protocol_compliance = context.get("protocol_compliance", {})
        trajectory = context.get("trajectory", {})
        ecg_analysis = context.get("ecg_analysis", {})
        current_vitals = context.get("current_vitals", {})
        protocol_name = context.get("protocol_name", "general")

        # Template reasoning always runs
        findings = self._template_reasoning(
            protocol_compliance, trajectory, ecg_analysis,
            current_vitals, protocol_name,
        )
        findings["mode"] = "template"
        findings["tier"] = tier.value

        # LLM enhancement if available
        if self.llm_client and CDS_LLM_MODE == "real":
            prompt = (
                f"Protocol: {protocol_name}\n"
                f"Compliance: {json.dumps(protocol_compliance, indent=2)}\n"
                f"Trajectory: {json.dumps(trajectory, indent=2)}\n"
                f"ECG Analysis: {json.dumps(ecg_analysis, indent=2)}\n"
                f"Current Vitals: {json.dumps(current_vitals, indent=2)}\n\n"
                f"Template assessment:\n{json.dumps(findings, indent=2)}"
            )
            response_text, _meta = self._call_llm(prompt, self.SYSTEM_PROMPT, tier)
            if response_text:
                llm_findings = parse_clinical_response(response_text)
                if "parse_error" not in llm_findings:
                    # Prefer LLM narrative if available
                    if "narrative_summary" in llm_findings:
                        findings["narrative_summary"] = llm_findings["narrative_summary"]
                    if "differentials" in llm_findings:
                        findings["differentials"] = llm_findings["differentials"]
                    if "recommended_workup" in llm_findings:
                        findings["recommended_workup"] = llm_findings["recommended_workup"]
                    if "risk_level" in llm_findings:
                        findings["risk_level"] = llm_findings["risk_level"]
                    findings["mode"] = "llm_enhanced"

        return True, findings

    def _template_reasoning(
        self,
        protocol_compliance: dict[str, Any],
        trajectory: dict[str, Any],
        ecg_analysis: dict[str, Any],
        current_vitals: dict[str, Any],
        protocol_name: str,
    ) -> dict[str, Any]:
        """Generate template-based clinical reasoning.

        Args:
            protocol_compliance: Protocol compliance data
            trajectory: Trajectory prediction data
            ecg_analysis: ECG analysis findings (may be empty)
            current_vitals: Current vital sign values
            protocol_name: Protocol name for differential lookup

        Returns:
            Clinical reasoning findings dict
        """
        activated = protocol_compliance.get("activated", False)
        compliance_score = protocol_compliance.get("score", 0)
        deviations = protocol_compliance.get("deviations", [])
        traj_state = trajectory.get("state", "stable")
        time_to_critical = trajectory.get("time_to_critical_hours")

        # Build narrative
        narrative_parts = ["CDS Advisory:"]

        if activated:
            narrative_parts.append(
                f"Protocol {protocol_name} is ACTIVATED (score {compliance_score})."
            )
        else:
            narrative_parts.append(
                f"Protocol {protocol_name} screening criteria not met."
            )

        if traj_state == "critical":
            narrative_parts.append("Trajectory indicates CRITICAL state.")
        elif traj_state == "deteriorating":
            if time_to_critical:
                narrative_parts.append(
                    f"Trajectory is deteriorating. "
                    f"Estimated time to critical: {time_to_critical:.1f} hours."
                )
            else:
                narrative_parts.append("Trajectory is deteriorating.")
        elif traj_state == "stable":
            narrative_parts.append("Trajectory is stable.")
        elif traj_state == "improving":
            narrative_parts.append("Trajectory shows improvement.")

        if deviations:
            narrative_parts.append(
                f"Deviations: {', '.join(str(d) for d in deviations[:3])}."
            )

        # ECG flags in narrative
        ecg_flags = ecg_analysis.get("clinical_flags", [])
        if ecg_flags:
            narrative_parts.append(f"ECG concerns: {', '.join(ecg_flags)}.")

        narrative = " ".join(narrative_parts)

        # Differentials from protocol mapping
        differentials = self.PROTOCOL_DIFFERENTIALS.get(
            protocol_name, ["Non-specific clinical finding"]
        )

        # Workup from protocol mapping
        workup = self.PROTOCOL_WORKUP.get(
            protocol_name, ["CBC", "BMP", "Vital sign trending"]
        )

        # Risk calculation
        risk_score = 0
        if activated:
            risk_score += 2
        if traj_state == "critical":
            risk_score += 3
        elif traj_state == "deteriorating":
            risk_score += 2
        if ecg_flags:
            risk_score += len(ecg_flags)

        if risk_score >= 5:
            risk_level = "critical"
        elif risk_score >= 3:
            risk_level = "high"
        elif risk_score >= 1:
            risk_level = "moderate"
        else:
            risk_level = "low"

        # Confidence based on data availability
        confidence = 0.7
        if current_vitals:
            confidence += 0.1
        if ecg_analysis:
            confidence += 0.1
        if activated:
            confidence += 0.1
        confidence = min(1.0, confidence)

        # Score: inverse of risk (100 = perfectly healthy)
        score_map = {"low": 90.0, "moderate": 70.0, "high": 40.0, "critical": 15.0}
        score = score_map.get(risk_level, 50.0)

        return {
            "narrative_summary": narrative,
            "differentials": differentials,
            "recommended_workup": workup,
            "risk_level": risk_level,
            "score": score,
            "confidence": confidence,
        }

    def result_to_clinical_reasoning(
        self, result: CDSAgentResult
    ) -> ClinicalReasoningResult:
        """Convert CDSAgentResult to ClinicalReasoningResult.

        Args:
            result: Agent result from process()

        Returns:
            Typed ClinicalReasoningResult
        """
        f = result.findings
        return ClinicalReasoningResult(
            narrative_summary=f.get("narrative_summary", ""),
            differentials=f.get("differentials", []),
            recommended_workup=f.get("recommended_workup", []),
            risk_level=f.get("risk_level", "low"),
            confidence=result.confidence,
        )
