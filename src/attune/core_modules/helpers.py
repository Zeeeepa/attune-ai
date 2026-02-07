"""Empathy Helpers Mixin for EmpathyOS.

Extracted from EmpathyOS to improve maintainability.
Provides private helper/extension-point methods used by empathy levels 1-5.

Expected attributes on the host class:
    user_id (str): User identifier
    confidence_threshold (float): Minimum confidence for anticipatory actions
    logger (logging.Logger): Logger instance
    leverage_analyzer (LeveragePointAnalyzer): Leverage point analyzer

Copyright 2025 Smart AI Memory, LLC
Licensed under Fair Source 0.9
"""

from __future__ import annotations

import logging
from datetime import datetime
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from ..leverage_points import LeveragePoint

logger = logging.getLogger(__name__)


class EmpathyHelpersMixin:
    """Mixin providing helper methods for empathy levels.

    These are extension points that subclasses can override
    to implement domain-specific logic.
    """

    # Expected attributes (set by EmpathyOS.__init__)
    user_id: str
    confidence_threshold: float
    logger: Any  # logging.Logger

    async def _process_request(self, request: str) -> dict:
        """Process user request (implement domain logic)

        **Extension Point**: Override this method in subclasses to implement
        your specific domain logic for processing user requests.

        Args:
            request: The user's request string

        Returns:
            Dict with processed result and status

        """
        # Placeholder - implement your actual request processing
        return {"processed": request, "status": "success"}

    async def _ask_calibrated_questions(self, request: str) -> dict:
        """Voss's tactical empathy: Ask calibrated questions

        **Extension Point**: Override to implement sophisticated clarification
        logic using NLP, LLMs, or domain-specific heuristics.

        Args:
            request: The user's request string

        Returns:
            Dict with needs_clarification flag and optional questions list

        """
        # Simple heuristic - in production, use NLP/LLM
        needs_clarification = any(
            word in request.lower() for word in ["some", "a few", "many", "soon"]
        )

        if needs_clarification:
            return {
                "needs_clarification": True,
                "questions": [
                    "What are you hoping to accomplish?",
                    "How does this fit into your workflow?",
                    "What would make this most helpful right now?",
                ],
            }
        return {"needs_clarification": False}

    def _refine_request(self, original: str, clarification: dict) -> str:
        """Refine request based on clarification responses

        **Extension Point**: Override to implement domain-specific request refinement
        based on clarification questions and user responses.

        Args:
            original: Original request string
            clarification: Dict containing clarification questions and responses

        Returns:
            Refined request string with added context

        """
        # If no clarification was needed, return original
        if not clarification.get("needs_clarification", False):
            return original

        # If clarification responses exist, incorporate them
        if "responses" in clarification:
            refinements = []
            for question, response in clarification["responses"].items():
                refinements.append(f"{question}: {response}")

            refined = f"{original}\n\nClarifications:\n" + "\n".join(f"- {r}" for r in refinements)
            return refined

        # Default: return original
        return original

    def _detect_active_patterns(self, context: dict) -> list[dict]:
        """Detect patterns in user behavior"""
        patterns = []

        # Example pattern detection logic
        if context.get("repeated_action"):
            patterns.append(
                {
                    "type": "sequential",
                    "pattern": "user_always_does_X_before_Y",
                    "confidence": 0.85,
                },
            )

        return patterns

    def _design_proactive_action(self, pattern: dict) -> dict:
        """Design proactive action based on pattern"""
        return {
            "action": "prefetch_data",
            "reasoning": f"Pattern detected: {pattern['pattern']}",
            "confidence": pattern["confidence"],
        }

    def _is_safe_to_execute(self, action: dict[str, Any]) -> bool:
        """Safety check for proactive actions"""
        confidence: float = action.get("confidence", 0)
        return confidence > 0.8

    async def _execute_proactive_actions(self, actions: list[dict]) -> list[dict]:
        """Execute proactive actions

        **Extension Point**: Override to implement actual execution of proactive
        actions in your domain (e.g., file operations, API calls, UI updates).

        This default implementation simulates execution with basic validation.
        Override this method to add real action execution logic.

        Args:
            actions: List of action dicts to execute

        Returns:
            List of result dicts with action and success status

        """
        results = []
        for action in actions:
            # Validate action has required fields
            if not action.get("action"):
                results.append(
                    {"action": action, "success": False, "error": "Missing 'action' field"},
                )
                continue

            # Log the action (in production, this would execute real logic)
            self.logger.debug(
                f"Executing proactive action: {action.get('action')}",
                extra={
                    "user_id": self.user_id,
                    "action_type": action.get("action"),
                    "confidence": action.get("confidence", 0),
                },
            )

            # Simulate successful execution
            results.append(
                {"action": action, "success": True, "executed_at": datetime.now().isoformat()},
            )

        return results

    def _predict_future_bottlenecks(self, trajectory: dict) -> list[dict]:
        """Predict where system will hit friction/overload

        Uses trajectory analysis, domain knowledge, historical patterns
        """
        bottlenecks = []

        # Example: Scaling bottleneck
        if trajectory.get("feature_count_increasing"):
            current = trajectory["current_feature_count"]
            growth_rate = trajectory.get("growth_rate", 0)
            projected_3mo = current + (growth_rate * 3)

            if projected_3mo > trajectory.get("threshold", 25):
                bottlenecks.append(
                    {
                        "type": "scaling_bottleneck",
                        "area": "testing",
                        "description": "Testing burden will become unsustainable",
                        "timeframe": "2-3 months",
                        "confidence": 0.75,
                        "current_state": f"{current} features",
                        "predicted_state": f"{projected_3mo} features",
                        "impact": trajectory.get("impact", "low"),
                    },
                )

        return bottlenecks

    def _should_anticipate(self, bottleneck: dict) -> bool:
        """Safety checks for Level 4 anticipatory actions

        Validates:
        1. Confidence is above threshold
        2. Time horizon is appropriate (30-120 days)
        3. Impact justifies the intervention effort
        """
        # Check 1: Confidence threshold
        if bottleneck["confidence"] < self.confidence_threshold:
            return False

        # Check 2: Time horizon (30-120 days ideal)
        timeframe = bottleneck.get("timeframe", "")
        days = self._parse_timeframe_to_days(timeframe)

        # Too soon (<30 days) = reactive, not anticipatory
        # Too far (>120 days) = too uncertain to act on
        if days is not None and (days < 30 or days > 120):
            return False

        # Check 3: Impact justifies effort
        if bottleneck.get("impact", "low") not in ["high", "critical"]:
            return False

        return True

    def _parse_timeframe_to_days(self, timeframe: str) -> int | None:
        """Parse timeframe string to days

        Examples:
            "2-3 months" -> 75 (midpoint)
            "60 days" -> 60
            "3 weeks" -> 21

        Returns:
            Number of days, or None if unparseable

        """
        import re

        if not timeframe:
            return None

        timeframe_lower = timeframe.lower()

        # Pattern: "X days"
        match = re.search(r"(\d+)\s*days?", timeframe_lower)
        if match:
            return int(match.group(1))

        # Pattern: "X weeks"
        match = re.search(r"(\d+)\s*weeks?", timeframe_lower)
        if match:
            return int(match.group(1)) * 7

        # Pattern: "X months" or "X-Y months"
        match = re.search(r"(\d+)(?:-(\d+))?\s*months?", timeframe_lower)
        if match:
            start = int(match.group(1))
            end = int(match.group(2)) if match.group(2) else start
            midpoint = (start + end) / 2
            return int(midpoint * 30)  # Approximate 30 days/month

        # Couldn't parse - return None (will skip time validation)
        return None

    def _design_anticipatory_intervention(self, bottleneck: dict) -> dict:
        """Design structural relief for predicted bottleneck"""
        return {
            "type": "framework_design",
            "target": bottleneck["area"],
            "deliverables": ["design_doc", "implementation_plan"],
            "timeline": "Implement before threshold",
        }

    async def _execute_anticipatory_interventions(self, interventions: list[dict]) -> list[dict]:
        """Execute anticipatory interventions

        **Extension Point**: Override to implement actual execution of
        anticipatory interventions (e.g., scaling resources, provisioning
        infrastructure, preparing documentation).

        This default implementation simulates intervention execution with
        validation and logging. Override for real infrastructure changes.

        Args:
            interventions: List of intervention dicts to execute

        Returns:
            List of result dicts with intervention and success status

        """
        results = []
        for intervention in interventions:
            # Validate intervention has required fields
            if not intervention.get("type"):
                results.append(
                    {
                        "intervention": intervention,
                        "success": False,
                        "error": "Missing 'type' field",
                    },
                )
                continue

            # Log the intervention
            self.logger.info(
                f"Executing anticipatory intervention: {intervention.get('type')}",
                extra={
                    "user_id": self.user_id,
                    "intervention_type": intervention.get("type"),
                    "target": intervention.get("target"),
                    "timeline": intervention.get("timeline"),
                },
            )

            # Simulate successful intervention
            results.append(
                {
                    "intervention": intervention,
                    "success": True,
                    "executed_at": datetime.now().isoformat(),
                    "status": "intervention_deployed",
                },
            )

        return results

    def _identify_problem_classes(self, domain_context: dict) -> list[dict]:
        """Identify recurring problem classes (not individual instances)

        Use "Rule of Three":
        - Occurred at least 3 times
        - Will occur at least 3 more times
        - Affects at least 3 users/workflows
        """
        problem_classes = []

        # Example detection logic
        if domain_context.get("recurring_documentation_burden"):
            problem_classes.append(
                {
                    "class": "documentation_burden",
                    "instances": domain_context["instances"],
                    "frequency": "every_new_feature",
                },
            )

        return problem_classes

    def _design_framework(self, leverage_point: LeveragePoint) -> dict:
        """Design framework at leverage point"""
        return {
            "name": f"{leverage_point.problem_domain}_framework",
            "type": "architectural_pattern",
            "leverage_point": leverage_point.description,
            "leverage_level": leverage_point.level.value,
            "impact": "Scales to all current + future instances",
        }

    async def _implement_frameworks(self, frameworks: list[dict]) -> list[dict]:
        """Implement designed frameworks

        **Extension Point**: Override to implement actual framework deployment
        (e.g., generating code templates, creating CI/CD pipelines, deploying
        infrastructure, setting up monitoring).

        This default implementation simulates framework deployment with validation
        and logging. Override for real framework deployment logic.

        Args:
            frameworks: List of framework dicts to implement

        Returns:
            List of result dicts with framework and deployed status

        """
        results = []
        for framework in frameworks:
            # Validate framework has required fields
            if not framework.get("name"):
                results.append(
                    {"framework": framework, "deployed": False, "error": "Missing 'name' field"},
                )
                continue

            # Log the framework deployment
            self.logger.info(
                f"Deploying systems framework: {framework.get('name')}",
                extra={
                    "user_id": self.user_id,
                    "framework_name": framework.get("name"),
                    "framework_type": framework.get("type"),
                    "leverage_level": framework.get("leverage_level"),
                },
            )

            # Simulate successful deployment
            results.append(
                {
                    "framework": framework,
                    "deployed": True,
                    "deployed_at": datetime.now().isoformat(),
                    "status": "framework_active",
                    "impact_scope": "system_wide",
                },
            )

        return results
