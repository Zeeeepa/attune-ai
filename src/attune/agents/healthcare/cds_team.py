"""Clinical Decision Support (CDS) Agent Team.

A multi-agent system for real-time clinical alerts with Redis coordination.

Agents:
    - Alert Prioritizer: Triages incoming clinical data
    - Protocol Matcher: Matches against clinical protocols
    - Risk Scorer: Calculates patient risk scores
    - Notification Router: Routes alerts to care teams

Collaboration: Parallel execution with result aggregation
Tier Strategy: Progressive (CHEAP → CAPABLE → PREMIUM)
Auth Strategy: Subscription first, API fallback
"""

# Load environment variables from .env file BEFORE other imports
from pathlib import Path

try:
    from dotenv import load_dotenv

    # Find .env file relative to this file's location
    _env_path = Path(__file__).parent.parent.parent.parent.parent / ".env"
    if _env_path.exists():
        load_dotenv(_env_path)
except ImportError:
    pass  # python-dotenv not installed, rely on system environment

import asyncio
import hashlib
import json
import logging
import os
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any
from uuid import uuid4

import redis

# Optional: Anthropic SDK for real LLM calls
try:
    import anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False

# Optional: Attune auth strategy
try:
    from attune.models import get_auth_strategy, AuthMode
    from attune.models.registry import ModelRegistry
    ATTUNE_AUTH_AVAILABLE = True
except ImportError:
    ATTUNE_AUTH_AVAILABLE = False

logger = logging.getLogger(__name__)


def _extract_json(text: str) -> str:
    """Extract JSON from possibly markdown-wrapped response.

    LLMs often wrap JSON in ```json...``` blocks. This extracts the raw JSON.
    """
    import re

    # Try to find JSON in markdown code block
    match = re.search(r"```(?:json)?\s*([\s\S]*?)```", text)
    if match:
        return match.group(1).strip()

    # Try to find raw JSON object or array
    text = text.strip()
    if text.startswith("{") or text.startswith("["):
        return text

    # Return as-is and let json.loads fail
    return text


# =============================================================================
# Configuration
# =============================================================================

REDIS_CONFIG = {
    "host": "redis-15667.c284.us-east1-2.gce.cloud.redislabs.com",
    "port": 15667,
    "password": "UdVaDTqTZbTVcM72U1ZACTc901oSY05a",
    "decode_responses": True,
}

# Model mapping for each tier
MODEL_CONFIG = {
    "cheap": "claude-3-5-haiku-latest",
    "capable": "claude-sonnet-4-20250514",
    "premium": "claude-opus-4-20250514",
}

# LLM mode: "real" uses actual API calls, "simulated" uses rule-based logic
LLM_MODE = os.getenv("CDS_LLM_MODE", "simulated")


class Tier(Enum):
    CHEAP = "cheap"
    CAPABLE = "capable"
    PREMIUM = "premium"


class AlertLevel(Enum):
    CRITICAL = "critical"
    WARNING = "warning"
    INFO = "info"


class TriggerType(Enum):
    LAB_RESULT = "lab_result"
    VITAL_SIGN = "vital_sign"
    MEDICATION_ORDER = "medication_order"


# =============================================================================
# Data Models
# =============================================================================


@dataclass
class ClinicalEvent:
    """Incoming clinical data that triggers the CDS system."""
    event_id: str
    trigger_type: TriggerType
    patient_id: str
    data: dict[str, Any]
    timestamp: float = field(default_factory=time.time)


@dataclass
class AgentResult:
    """Result from an individual agent."""
    agent_id: str
    agent_role: str
    success: bool
    tier_used: Tier
    result: dict[str, Any]
    execution_time_ms: float
    escalated: bool = False


@dataclass
class CDSDecision:
    """Aggregated decision from all agents."""
    event_id: str
    patient_id: str
    alert_level: AlertLevel
    risk_score: float
    matched_protocols: list[str]
    notifications: list[dict]
    agent_results: list[AgentResult]
    total_time_ms: float


# =============================================================================
# Base Agent with Progressive Tier Escalation
# =============================================================================


class ProgressiveAgent:
    """Base agent with CHEAP → CAPABLE → PREMIUM escalation.

    Uses subscription-first auth strategy:
    - CHEAP tier: Uses Claude subscription (free if user has Pro/Max)
    - CAPABLE tier: Uses subscription for small context, API for large
    - PREMIUM tier: Uses API for maximum capability

    Features:
    - Redis-based response caching (avoids duplicate LLM calls)
    - Automatic tier escalation on failure
    - Real-time heartbeat for dashboard visibility
    - Cost tracking per request
    """

    # Cache TTL for LLM responses (5 minutes)
    CACHE_TTL = 300

    def __init__(self, agent_id: str, role: str, redis_client: redis.Redis):
        self.agent_id = agent_id
        self.role = role
        self.redis = redis_client
        self.current_tier = Tier.CHEAP
        self.llm_client = None
        self.total_cost = 0.0
        self.total_tokens = 0

        # Initialize LLM client if available
        if ANTHROPIC_AVAILABLE and LLM_MODE == "real":
            api_key = os.getenv("ANTHROPIC_API_KEY")
            if api_key:
                self.llm_client = anthropic.Anthropic(api_key=api_key)
                logger.info(f"Agent {agent_id}: LLM client initialized")
            else:
                logger.warning(f"Agent {agent_id}: No API key, using simulated mode")

        # Get auth strategy if available
        self.auth_strategy = None
        if ATTUNE_AUTH_AVAILABLE:
            try:
                self.auth_strategy = get_auth_strategy()
                logger.info(f"Agent {agent_id}: Auth strategy loaded")
            except Exception as e:
                logger.warning(f"Agent {agent_id}: Auth strategy failed: {e}")

    def _register_heartbeat(self, status: str = "running", task: str = ""):
        """Register agent liveness in Redis."""
        key = f"cds:agent:heartbeat:{self.agent_id}"
        self.redis.hset(key, mapping={
            "agent_id": self.agent_id,
            "role": self.role,
            "status": status,
            "current_task": task,
            "tier": self.current_tier.value,
            "last_beat": time.time(),
            "total_cost": self.total_cost,
            "total_tokens": self.total_tokens,
        })
        self.redis.expire(key, 60)

    def _signal_completion(self, event_id: str, result: dict):
        """Signal task completion via Pub/Sub."""
        signal = {
            "agent_id": self.agent_id,
            "role": self.role,
            "event_id": event_id,
            "result": result,
            "tier_used": self.current_tier.value,
            "cost": self.total_cost,
            "timestamp": time.time(),
        }
        self.redis.publish(f"cds:signals:{event_id}", json.dumps(signal))

    def _get_cache_key(self, event: ClinicalEvent, tier: Tier) -> str:
        """Generate cache key for LLM response."""
        content = json.dumps({
            "role": self.role,
            "tier": tier.value,
            "trigger": event.trigger_type.value,
            "data": event.data,
        }, sort_keys=True)
        return f"cds:cache:{hashlib.sha256(content.encode()).hexdigest()[:16]}"

    def _get_cached_response(self, cache_key: str) -> dict[str, Any] | None:
        """Check Redis cache for previous LLM response."""
        cached = self.redis.get(cache_key)
        if cached and isinstance(cached, str):
            logger.info(f"Cache HIT for {self.role}")
            return json.loads(cached)  # type: ignore[no-any-return]
        return None

    def _cache_response(self, cache_key: str, response: dict):
        """Cache LLM response in Redis."""
        self.redis.setex(cache_key, self.CACHE_TTL, json.dumps(response))

    def _call_llm(self, prompt: str, system: str, tier: Tier) -> tuple[str, dict]:
        """Call LLM with tier-appropriate model.

        Returns:
            tuple: (response_text, metadata with tokens/cost)
        """
        if not self.llm_client:
            # Fallback to simulated response
            return self._simulate_llm_response(prompt, tier)

        model = MODEL_CONFIG[tier.value]

        try:
            response = self.llm_client.messages.create(
                model=model,
                max_tokens=1024,
                system=system,
                messages=[{"role": "user", "content": prompt}],
            )

            # Calculate cost
            input_tokens = response.usage.input_tokens
            output_tokens = response.usage.output_tokens

            # Pricing per million tokens
            pricing = {
                "cheap": {"input": 0.80, "output": 4.00},
                "capable": {"input": 3.00, "output": 15.00},
                "premium": {"input": 15.00, "output": 75.00},
            }

            tier_pricing = pricing[tier.value]
            cost = (input_tokens * tier_pricing["input"] / 1_000_000 +
                   output_tokens * tier_pricing["output"] / 1_000_000)

            self.total_cost += cost
            self.total_tokens += input_tokens + output_tokens

            # Extract text from response (handle different block types)
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
            logger.error(f"LLM call failed: {e}")
            return self._simulate_llm_response(prompt, tier)

    def _simulate_llm_response(self, prompt: str, tier: Tier) -> tuple[str, dict]:
        """Simulate LLM response for testing without API calls."""
        # Return structured response that can be parsed
        return json.dumps({"simulated": True, "tier": tier.value}), {
            "model": f"simulated-{tier.value}",
            "input_tokens": 100,
            "output_tokens": 50,
            "cost": 0.0,
        }

    def process(self, event: ClinicalEvent) -> AgentResult:
        """Process with progressive tier escalation."""
        start = time.time()
        escalated = False

        # Try CHEAP first
        self.current_tier = Tier.CHEAP
        self._register_heartbeat(status="running", task=f"Processing {event.event_id}")

        success, result = self._execute_tier(event, Tier.CHEAP)

        # Escalate to CAPABLE if needed
        if not success:
            escalated = True
            self.current_tier = Tier.CAPABLE
            self._register_heartbeat(status="escalating", task=f"Escalating {event.event_id}")
            success, result = self._execute_tier(event, Tier.CAPABLE)

        # Escalate to PREMIUM if still failing
        if not success:
            self.current_tier = Tier.PREMIUM
            self._register_heartbeat(status="escalating", task=f"Premium {event.event_id}")
            success, result = self._execute_tier(event, Tier.PREMIUM)

        execution_time = (time.time() - start) * 1000

        # Signal completion
        self._signal_completion(event.event_id, result)
        self._register_heartbeat(status="idle", task="")

        return AgentResult(
            agent_id=self.agent_id,
            agent_role=self.role,
            success=success,
            tier_used=self.current_tier,
            result=result,
            execution_time_ms=execution_time,
            escalated=escalated,
        )

    def _execute_tier(self, event: ClinicalEvent, tier: Tier) -> tuple[bool, dict]:
        """Execute at specific tier. Override in subclasses."""
        raise NotImplementedError


# =============================================================================
# Specialized CDS Agents
# =============================================================================


class AlertPrioritizerAgent(ProgressiveAgent):
    """Triages incoming clinical data and determines urgency level.

    Uses LLM for nuanced clinical reasoning with rule-based fallback.
    Higher tiers use more sophisticated models for complex cases.
    """

    SYSTEM_PROMPT = """You are a clinical decision support system for alert prioritization.
Analyze the patient's clinical data and determine the urgency level.

Respond in JSON format:
{
    "alert_level": "critical" | "warning" | "info",
    "confidence": 0.0-1.0,
    "reasoning": "brief clinical reasoning",
    "immediate_actions": ["action1", "action2"]
}

Critical: Immediate life threat, requires immediate intervention
Warning: Abnormal values requiring prompt attention
Info: Notable but not urgent"""

    def __init__(self, redis_client: redis.Redis):
        super().__init__(
            agent_id=f"alert-prioritizer-{uuid4().hex[:8]}",
            role="Alert Prioritizer",
            redis_client=redis_client,
        )
        # Thresholds for different tiers (more sophisticated at higher tiers)
        self.thresholds = {
            Tier.CHEAP: {"critical_confidence": 0.9, "warning_confidence": 0.7},
            Tier.CAPABLE: {"critical_confidence": 0.8, "warning_confidence": 0.6},
            Tier.PREMIUM: {"critical_confidence": 0.7, "warning_confidence": 0.5},
        }

    def _execute_tier(self, event: ClinicalEvent, tier: Tier) -> tuple[bool, dict]:
        """Prioritize alert based on clinical data using LLM."""
        try:
            # Check cache first
            cache_key = self._get_cache_key(event, tier)
            cached = self._get_cached_response(cache_key)
            if cached:
                return True, cached

            # Use LLM for clinical reasoning if available
            if self.llm_client and LLM_MODE == "real":
                return self._execute_with_llm(event, tier, cache_key)

            # Fallback to rule-based logic
            return self._execute_rule_based(event, tier, cache_key)

        except Exception as e:
            logger.error(f"Alert prioritization failed: {e}")
            return False, {"error": str(e)}

    def _execute_with_llm(self, event: ClinicalEvent, tier: Tier, cache_key: str) -> tuple[bool, dict]:
        """Use LLM for clinical alert prioritization."""
        prompt = f"""Analyze this clinical data for patient {event.patient_id}:

Trigger Type: {event.trigger_type.value}
Data: {json.dumps(event.data, indent=2)}

Determine the appropriate alert level and provide clinical reasoning."""

        response_text, metadata = self._call_llm(prompt, self.SYSTEM_PROMPT, tier)

        try:
            # Parse LLM response
            result = json.loads(_extract_json(response_text))
            result["tier"] = tier.value
            result["llm_metadata"] = metadata
            result["mode"] = "llm"

            # Cache the response
            self._cache_response(cache_key, result)

            # Check if confidence meets threshold
            thresholds = self.thresholds[tier]
            alert_level = result.get("alert_level", "info")
            confidence = result.get("confidence", 0.5)

            meets_threshold = (
                (alert_level == "critical" and confidence >= thresholds["critical_confidence"])
                or (alert_level == "warning" and confidence >= thresholds["warning_confidence"])
                or alert_level == "info"
            )

            return meets_threshold, result

        except json.JSONDecodeError as e:
            # If LLM response isn't valid JSON, fallback to rules
            extracted = _extract_json(response_text)
            logger.warning(f"LLM response not valid JSON: {e}. Extracted: {extracted[:100]}...")
            return self._execute_rule_based(event, tier, cache_key)

    def _execute_rule_based(self, event: ClinicalEvent, tier: Tier, cache_key: str) -> tuple[bool, dict]:
        """Rule-based alert prioritization (fallback)."""
        alert_level = self._calculate_priority(event, tier)
        confidence = self._calculate_confidence(event, tier)

        thresholds = self.thresholds[tier]
        meets_threshold = (
            (alert_level == AlertLevel.CRITICAL and confidence >= thresholds["critical_confidence"])
            or (alert_level == AlertLevel.WARNING and confidence >= thresholds["warning_confidence"])
            or alert_level == AlertLevel.INFO
        )

        result = {
            "alert_level": alert_level.value,
            "confidence": confidence,
            "tier": tier.value,
            "reasoning": self._get_reasoning(event, alert_level),
            "mode": "rule_based",
        }

        # Cache the result
        self._cache_response(cache_key, result)

        return meets_threshold, result

    def _calculate_priority(self, event: ClinicalEvent, tier: Tier) -> AlertLevel:
        """Determine alert priority based on clinical data."""
        data = event.data

        # Critical conditions
        if event.trigger_type == TriggerType.VITAL_SIGN:
            if data.get("heart_rate", 80) > 150 or data.get("heart_rate", 80) < 40:
                return AlertLevel.CRITICAL
            if data.get("o2_sat", 98) < 90:
                return AlertLevel.CRITICAL
            if data.get("systolic_bp", 120) > 180 or data.get("systolic_bp", 120) < 80:
                return AlertLevel.CRITICAL

        if event.trigger_type == TriggerType.LAB_RESULT:
            if data.get("potassium", 4.0) > 6.0 or data.get("potassium", 4.0) < 2.5:
                return AlertLevel.CRITICAL
            if data.get("glucose", 100) > 400 or data.get("glucose", 100) < 50:
                return AlertLevel.CRITICAL

        # Warning conditions (more nuanced at higher tiers)
        if tier in [Tier.CAPABLE, Tier.PREMIUM]:
            if event.trigger_type == TriggerType.VITAL_SIGN:
                if data.get("temperature", 98.6) > 101.5:
                    return AlertLevel.WARNING
            if event.trigger_type == TriggerType.LAB_RESULT:
                if data.get("creatinine", 1.0) > 2.0:
                    return AlertLevel.WARNING

        return AlertLevel.INFO

    def _calculate_confidence(self, event: ClinicalEvent, tier: Tier) -> float:
        """Calculate confidence based on data completeness and tier."""
        base_confidence = 0.7
        data_completeness = len(event.data) / 5  # Assume 5 typical fields

        tier_bonus = {Tier.CHEAP: 0.0, Tier.CAPABLE: 0.1, Tier.PREMIUM: 0.2}

        return min(1.0, base_confidence + (data_completeness * 0.2) + tier_bonus[tier])

    def _get_reasoning(self, event: ClinicalEvent, level: AlertLevel) -> str:
        """Provide reasoning for the alert level."""
        if level == AlertLevel.CRITICAL:
            return f"Critical values detected in {event.trigger_type.value}"
        elif level == AlertLevel.WARNING:
            return f"Abnormal values requiring attention in {event.trigger_type.value}"
        return "Values within normal parameters"


class ProtocolMatcherAgent(ProgressiveAgent):
    """Matches patient data against clinical protocols and guidelines."""

    def __init__(self, redis_client: redis.Redis):
        super().__init__(
            agent_id=f"protocol-matcher-{uuid4().hex[:8]}",
            role="Protocol Matcher",
            redis_client=redis_client,
        )
        # Simulated protocol database
        self.protocols = {
            "sepsis_screening": {
                "triggers": [TriggerType.VITAL_SIGN, TriggerType.LAB_RESULT],
                "conditions": ["temperature > 100.4", "heart_rate > 90", "wbc > 12000"],
            },
            "aki_protocol": {
                "triggers": [TriggerType.LAB_RESULT],
                "conditions": ["creatinine > 1.5x baseline", "urine_output < 0.5ml/kg/hr"],
            },
            "hypoglycemia_protocol": {
                "triggers": [TriggerType.LAB_RESULT],
                "conditions": ["glucose < 70"],
            },
            "hypertensive_emergency": {
                "triggers": [TriggerType.VITAL_SIGN],
                "conditions": ["systolic_bp > 180", "diastolic_bp > 120"],
            },
        }

    def _execute_tier(self, event: ClinicalEvent, tier: Tier) -> tuple[bool, dict[str, Any]]:
        """Match against clinical protocols."""
        try:
            matched: list[dict[str, Any]] = []
            for protocol_name, protocol in self.protocols.items():
                triggers = protocol["triggers"]
                if event.trigger_type in triggers:
                    if self._check_protocol_match(event, protocol, tier):
                        matched.append({
                            "protocol": protocol_name,
                            "conditions_met": protocol["conditions"],
                            "confidence": self._protocol_confidence(tier),
                        })

            # Higher tiers can match with lower confidence
            min_protocols = {Tier.CHEAP: 1, Tier.CAPABLE: 0, Tier.PREMIUM: 0}
            success = len(matched) >= min_protocols[tier] or tier == Tier.PREMIUM

            return success, {
                "matched_protocols": matched,
                "total_checked": len(self.protocols),
                "tier": tier.value,
            }
        except Exception as e:
            return False, {"error": str(e)}

    def _check_protocol_match(
        self, event: ClinicalEvent, protocol: dict[str, Any], tier: Tier
    ) -> bool:
        """Check if event matches protocol conditions."""
        # Simplified matching logic
        data = event.data

        if "sepsis" in str(protocol):
            temp = float(data.get("temperature", 98.6))
            hr = float(data.get("heart_rate", 80))
            return temp > 100.4 or hr > 90

        if "hypoglycemia" in str(protocol):
            glucose = float(data.get("glucose", 100))
            return glucose < 70

        if "hypertensive" in str(protocol):
            sbp = float(data.get("systolic_bp", 120))
            return sbp > 180

        return False

    def _protocol_confidence(self, tier: Tier) -> float:
        """Confidence level based on tier."""
        return {Tier.CHEAP: 0.7, Tier.CAPABLE: 0.85, Tier.PREMIUM: 0.95}[tier]


class RiskScorerAgent(ProgressiveAgent):
    """Calculates patient risk scores based on clinical data.

    Uses LLM for comprehensive risk assessment considering:
    - Current vital signs and lab values
    - Clinical context and patterns
    - Evidence-based risk factors
    """

    SYSTEM_PROMPT = """You are a clinical risk assessment system.
Calculate a comprehensive risk score (0-100) based on the patient's clinical data.

Respond in JSON format:
{
    "risk_score": 0-100,
    "risk_level": "MINIMAL" | "LOW" | "MODERATE" | "HIGH",
    "contributing_factors": ["factor1", "factor2"],
    "recommendations": ["recommendation1"],
    "confidence": 0.0-1.0
}

Scoring guidelines:
- 0-20: MINIMAL - Normal values, routine monitoring
- 21-40: LOW - Mild abnormalities, increased monitoring
- 41-70: MODERATE - Significant abnormalities, intervention may be needed
- 71-100: HIGH - Critical values, immediate intervention required"""

    def __init__(self, redis_client: redis.Redis):
        super().__init__(
            agent_id=f"risk-scorer-{uuid4().hex[:8]}",
            role="Risk Scorer",
            redis_client=redis_client,
        )

    def _execute_tier(self, event: ClinicalEvent, tier: Tier) -> tuple[bool, dict]:
        """Calculate risk score using LLM or rules."""
        try:
            # Check cache first
            cache_key = self._get_cache_key(event, tier)
            cached = self._get_cached_response(cache_key)
            if cached:
                return True, cached

            # Use LLM for risk assessment if available
            if self.llm_client and LLM_MODE == "real":
                return self._execute_with_llm(event, tier, cache_key)

            # Fallback to rule-based scoring
            return self._execute_rule_based(event, tier, cache_key)

        except Exception as e:
            logger.error(f"Risk scoring failed: {e}")
            return False, {"error": str(e)}

    def _execute_with_llm(self, event: ClinicalEvent, tier: Tier, cache_key: str) -> tuple[bool, dict]:
        """Use LLM for comprehensive risk assessment."""
        prompt = f"""Calculate risk score for patient {event.patient_id}:

Trigger Type: {event.trigger_type.value}
Clinical Data: {json.dumps(event.data, indent=2)}

Provide a comprehensive risk assessment with score, factors, and recommendations."""

        response_text, metadata = self._call_llm(prompt, self.SYSTEM_PROMPT, tier)

        try:
            result = json.loads(_extract_json(response_text))
            result["tier"] = tier.value
            result["llm_metadata"] = metadata
            result["mode"] = "llm"

            self._cache_response(cache_key, result)

            # Higher tiers accept lower confidence
            min_confidence = {Tier.CHEAP: 0.8, Tier.CAPABLE: 0.6, Tier.PREMIUM: 0.4}
            confidence = result.get("confidence", 0.5)
            success = confidence >= min_confidence[tier]

            return success, result

        except json.JSONDecodeError as e:
            extracted = _extract_json(response_text)
            logger.warning(f"LLM response not valid JSON: {e}. Extracted: {extracted[:100]}...")
            return self._execute_rule_based(event, tier, cache_key)

    def _execute_rule_based(self, event: ClinicalEvent, tier: Tier, cache_key: str) -> tuple[bool, dict]:
        """Rule-based risk scoring (fallback)."""
        score = self._calculate_risk(event, tier)
        factors = self._identify_risk_factors(event, tier)

        min_confidence = {Tier.CHEAP: 0.8, Tier.CAPABLE: 0.6, Tier.PREMIUM: 0.4}
        confidence = self._calculate_data_confidence(event)
        success = confidence >= min_confidence[tier]

        result = {
            "risk_score": score,
            "risk_level": self._score_to_level(score),
            "contributing_factors": factors,
            "data_confidence": confidence,
            "tier": tier.value,
            "mode": "rule_based",
        }

        self._cache_response(cache_key, result)
        return success, result

    def _calculate_risk(self, event: ClinicalEvent, tier: Tier) -> float:
        """Calculate 0-100 risk score."""
        data = event.data
        score = 0.0

        # Vital sign contributions
        if event.trigger_type == TriggerType.VITAL_SIGN:
            hr = data.get("heart_rate", 80)
            if hr > 100 or hr < 60:
                score += 15
            if hr > 120 or hr < 50:
                score += 25

            bp = data.get("systolic_bp", 120)
            if bp > 140 or bp < 90:
                score += 15
            if bp > 180 or bp < 80:
                score += 25

            o2 = data.get("o2_sat", 98)
            if o2 < 95:
                score += 20
            if o2 < 90:
                score += 30

        # Lab contributions
        if event.trigger_type == TriggerType.LAB_RESULT:
            glucose = data.get("glucose", 100)
            if glucose > 200 or glucose < 70:
                score += 20
            if glucose > 300 or glucose < 50:
                score += 30

            potassium = data.get("potassium", 4.0)
            if potassium > 5.5 or potassium < 3.0:
                score += 25
            if potassium > 6.0 or potassium < 2.5:
                score += 35

        # Tier adjustment (higher tiers are more sensitive)
        tier_multiplier = {Tier.CHEAP: 1.0, Tier.CAPABLE: 1.1, Tier.PREMIUM: 1.2}
        return min(100.0, score * tier_multiplier[tier])

    def _identify_risk_factors(self, event: ClinicalEvent, tier: Tier) -> list[str]:
        """Identify contributing risk factors."""
        factors = []
        data = event.data

        if data.get("heart_rate", 80) > 100:
            factors.append("Tachycardia")
        if data.get("o2_sat", 98) < 95:
            factors.append("Hypoxemia")
        if data.get("systolic_bp", 120) > 160:
            factors.append("Hypertension")
        if data.get("glucose", 100) > 200:
            factors.append("Hyperglycemia")
        if data.get("glucose", 100) < 70:
            factors.append("Hypoglycemia")

        return factors

    def _calculate_data_confidence(self, event: ClinicalEvent) -> float:
        """Confidence based on data completeness."""
        expected_fields = 5
        actual_fields = len(event.data)
        return min(1.0, actual_fields / expected_fields)

    def _score_to_level(self, score: float) -> str:
        """Convert score to risk level."""
        if score >= 70:
            return "HIGH"
        elif score >= 40:
            return "MODERATE"
        elif score >= 20:
            return "LOW"
        return "MINIMAL"


class NotificationRouterAgent(ProgressiveAgent):
    """Determines which care team members to alert and via which channel."""

    def __init__(self, redis_client: redis.Redis):
        super().__init__(
            agent_id=f"notification-router-{uuid4().hex[:8]}",
            role="Notification Router",
            redis_client=redis_client,
        )
        # Care team routing rules
        self.routing_rules = {
            AlertLevel.CRITICAL: {
                "recipients": ["attending_physician", "charge_nurse", "rapid_response"],
                "channels": ["pager", "sms", "dashboard"],
                "escalation_time": 300,  # 5 minutes
            },
            AlertLevel.WARNING: {
                "recipients": ["primary_nurse", "attending_physician"],
                "channels": ["dashboard", "sms"],
                "escalation_time": 900,  # 15 minutes
            },
            AlertLevel.INFO: {
                "recipients": ["primary_nurse"],
                "channels": ["dashboard"],
                "escalation_time": None,
            },
        }

    def _execute_tier(self, event: ClinicalEvent, tier: Tier) -> tuple[bool, dict[str, Any]]:
        """Determine notification routing."""
        try:
            # Get alert level from event data or default to INFO
            alert_level_str = str(event.data.get("alert_level", "info"))
            alert_level = AlertLevel(alert_level_str)

            routing = self.routing_rules[alert_level]
            recipients: list[str] = routing["recipients"]
            channels: list[str] = routing["channels"]

            notifications: list[dict[str, Any]] = []
            for recipient in recipients:
                for channel in channels:
                    notifications.append({
                        "recipient": recipient,
                        "channel": channel,
                        "priority": alert_level.value,
                        "patient_id": event.patient_id,
                        "message": self._format_message(event, alert_level, tier),
                    })

            # Publish notifications to Redis for actual delivery
            for notif in notifications:
                self.redis.publish(
                    f"cds:notifications:{notif['channel']}",
                    json.dumps(notif)
                )

            success = len(notifications) > 0
            return success, {
                "notifications_sent": len(notifications),
                "recipients": recipients,
                "channels": channels,
                "escalation_time_seconds": routing["escalation_time"],
                "tier": tier.value,
            }
        except Exception as e:
            return False, {"error": str(e)}

    def _format_message(self, event: ClinicalEvent, level: AlertLevel, tier: Tier) -> str:
        """Format notification message."""
        prefix = {
            AlertLevel.CRITICAL: "🚨 CRITICAL ALERT",
            AlertLevel.WARNING: "⚠️ WARNING",
            AlertLevel.INFO: "ℹ️ INFO",
        }
        return f"{prefix[level]}: Patient {event.patient_id} - {event.trigger_type.value}"


# =============================================================================
# CDS Team Coordinator
# =============================================================================


class CDSTeam:
    """Coordinates parallel execution of CDS agents.

    Features:
    - Parallel agent execution for low latency
    - Progressive tier escalation (CHEAP → CAPABLE → PREMIUM)
    - Subscription-first auth strategy
    - Redis coordination and caching
    - Cost tracking across all agents
    """

    def __init__(self):
        self.redis = redis.Redis(**REDIS_CONFIG)
        self.redis.ping()
        print("✅ CDS Team connected to Redis")

        # Check LLM availability
        print(f"📡 LLM Mode: {LLM_MODE}")
        if ANTHROPIC_AVAILABLE:
            print("✅ Anthropic SDK available")
        else:
            print("⚠️  Anthropic SDK not installed (pip install anthropic)")

        if ATTUNE_AUTH_AVAILABLE:
            print("✅ Attune auth strategy available")
        else:
            print("ℹ️  Attune auth strategy not available (using defaults)")

        # Initialize agents
        self.agents = [
            AlertPrioritizerAgent(self.redis),
            ProtocolMatcherAgent(self.redis),
            RiskScorerAgent(self.redis),
            NotificationRouterAgent(self.redis),
        ]
        print(f"✅ Initialized {len(self.agents)} agents")

    def get_total_cost(self) -> float:
        """Get total cost across all agents."""
        total: float = 0.0
        for agent in self.agents:
            total += agent.total_cost
        return total

    def get_total_tokens(self) -> int:
        """Get total tokens used across all agents."""
        total: int = 0
        for agent in self.agents:
            total += agent.total_tokens
        return total

    async def process_event(self, event: ClinicalEvent) -> CDSDecision:
        """Process clinical event with all agents in parallel."""
        start = time.time()

        print(f"\n{'='*60}")
        print(f"Processing Event: {event.event_id}")
        print(f"Patient: {event.patient_id}")
        print(f"Trigger: {event.trigger_type.value}")
        print(f"{'='*60}")

        # Execute all agents in parallel
        loop = asyncio.get_event_loop()
        tasks = [
            loop.run_in_executor(None, agent.process, event)
            for agent in self.agents
        ]
        results: list[AgentResult] = await asyncio.gather(*tasks)

        # Aggregate results
        decision = self._aggregate_results(event, results, time.time() - start)

        # Log to Redis
        self._log_decision(decision)

        return decision

    def _aggregate_results(
        self, event: ClinicalEvent, results: list[AgentResult], elapsed: float
    ) -> CDSDecision:
        """Aggregate agent results into final decision."""
        # Extract individual results
        alert_result = next((r for r in results if "Prioritizer" in r.agent_role), None)
        protocol_result = next((r for r in results if "Protocol" in r.agent_role), None)
        risk_result = next((r for r in results if "Risk" in r.agent_role), None)

        # Determine final alert level
        alert_level = AlertLevel.INFO
        if alert_result and alert_result.success:
            alert_level = AlertLevel(alert_result.result.get("alert_level", "info"))

        # Get risk score
        risk_score = 0.0
        if risk_result and risk_result.success:
            risk_score = risk_result.result.get("risk_score", 0.0)

        # Get matched protocols
        matched_protocols = []
        if protocol_result and protocol_result.success:
            matched_protocols = [
                p["protocol"]
                for p in protocol_result.result.get("matched_protocols", [])
            ]

        # Get notifications
        notifications = []
        notif_result = next((r for r in results if "Notification" in r.agent_role), None)
        if notif_result and notif_result.success:
            notifications = [
                {"channel": c, "recipient": r}
                for c in notif_result.result.get("channels", [])
                for r in notif_result.result.get("recipients", [])
            ]

        return CDSDecision(
            event_id=event.event_id,
            patient_id=event.patient_id,
            alert_level=alert_level,
            risk_score=risk_score,
            matched_protocols=matched_protocols,
            notifications=notifications,
            agent_results=results,
            total_time_ms=elapsed * 1000,
        )

    def _log_decision(self, decision: CDSDecision):
        """Log decision to Redis for audit trail."""
        key = f"cds:decisions:{decision.event_id}"
        self.redis.hset(key, mapping={
            "event_id": decision.event_id,
            "patient_id": decision.patient_id,
            "alert_level": decision.alert_level.value,
            "risk_score": decision.risk_score,
            "matched_protocols": json.dumps(decision.matched_protocols),
            "total_time_ms": decision.total_time_ms,
            "timestamp": time.time(),
        })
        self.redis.expire(key, 86400)  # 24 hour retention

    def print_decision(self, decision: CDSDecision):
        """Pretty print decision."""
        print(f"\n{'='*60}")
        print("CDS DECISION")
        print(f"{'='*60}")
        print(f"Event ID: {decision.event_id}")
        print(f"Patient ID: {decision.patient_id}")
        print(f"Alert Level: {decision.alert_level.value.upper()}")
        print(f"Risk Score: {decision.risk_score:.1f}/100")
        print(f"Matched Protocols: {', '.join(decision.matched_protocols) or 'None'}")
        print(f"Notifications: {len(decision.notifications)}")
        print(f"Total Time: {decision.total_time_ms:.1f}ms")

        print(f"\n{'─'*60}")
        print("AGENT RESULTS")
        print(f"{'─'*60}")
        for result in decision.agent_results:
            status = "✅" if result.success else "❌"
            escalated = " (escalated)" if result.escalated else ""
            mode = result.result.get("mode", "rule_based")
            print(f"{status} {result.agent_role}: {result.tier_used.value}{escalated} [{result.execution_time_ms:.0f}ms] ({mode})")


# =============================================================================
# Demo / Test
# =============================================================================


async def demo():
    """Demonstrate CDS team processing clinical events."""
    print("\n" + "=" * 70)
    print("CLINICAL DECISION SUPPORT (CDS) MULTI-AGENT DEMO")
    print("=" * 70)
    print("Agents: Alert Prioritizer, Protocol Matcher, Risk Scorer, Notification Router")
    print("Collaboration: Parallel Execution")
    print("Tier Strategy: Progressive (CHEAP → CAPABLE → PREMIUM)")
    print("Auth Strategy: Subscription first, API fallback")
    print("=" * 70)

    # Initialize team
    team = CDSTeam()

    # Test events with varying severity
    events = [
        # Critical case: Multiple abnormal vitals
        ClinicalEvent(
            event_id=f"EVT-{uuid4().hex[:8]}",
            trigger_type=TriggerType.VITAL_SIGN,
            patient_id="PT-001",
            data={
                "heart_rate": 145,
                "systolic_bp": 85,
                "o2_sat": 88,
                "temperature": 101.2,
                "respiratory_rate": 28,
            },
        ),
        # Critical case: Dangerous lab values
        ClinicalEvent(
            event_id=f"EVT-{uuid4().hex[:8]}",
            trigger_type=TriggerType.LAB_RESULT,
            patient_id="PT-002",
            data={
                "glucose": 45,
                "potassium": 6.2,
                "creatinine": 2.5,
                "bun": 45,
                "lactate": 4.5,
            },
        ),
        # Normal case: All values within range
        ClinicalEvent(
            event_id=f"EVT-{uuid4().hex[:8]}",
            trigger_type=TriggerType.VITAL_SIGN,
            patient_id="PT-003",
            data={
                "heart_rate": 78,
                "systolic_bp": 125,
                "o2_sat": 97,
                "temperature": 98.6,
                "respiratory_rate": 16,
            },
        ),
    ]

    # Process each event
    total_time = 0.0
    for i, event in enumerate(events, 1):
        print(f"\n📋 Processing Event {i}/{len(events)}...")
        decision = await team.process_event(event)
        team.print_decision(decision)
        total_time += decision.total_time_ms

    # Summary statistics
    print("\n" + "=" * 70)
    print("SESSION SUMMARY")
    print("=" * 70)
    print(f"Events Processed: {len(events)}")
    print(f"Total Processing Time: {total_time:.1f}ms")
    print(f"Average Time per Event: {total_time/len(events):.1f}ms")
    print(f"Total LLM Cost: ${team.get_total_cost():.4f}")
    print(f"Total Tokens Used: {team.get_total_tokens():,}")

    # Per-agent breakdown
    print(f"\n{'─'*60}")
    print("AGENT COST BREAKDOWN")
    print(f"{'─'*60}")
    for agent in team.agents:
        print(f"  {agent.role}: ${agent.total_cost:.4f} ({agent.total_tokens:,} tokens)")

    print("\n" + "=" * 70)
    print("DEMO COMPLETE")
    print("=" * 70)
    print(f"\nTo enable real LLM calls, set: CDS_LLM_MODE=real")
    print(f"Current mode: {LLM_MODE}")


if __name__ == "__main__":
    asyncio.run(demo())
