"""Unit tests for MetaOrchestrator escalation decision logic.

Tests cover:
- Escalation decision making
- Stagnation detection
- Agent team creation
- Prompt building
"""

import pytest
from datetime import datetime

from attune.workflows.progressive.core import (
    EscalationConfig,
    FailureAnalysis,
    Tier,
    TierResult,
)
from attune.workflows.progressive.orchestrator import MetaOrchestrator


class TestMetaOrchestrator:
    """Test MetaOrchestrator class."""

    def test_init(self):
        """Test orchestrator initialization."""
        orchestrator = MetaOrchestrator()
        assert orchestrator is not None
        assert orchestrator.tier_history is not None

    def test_should_escalate_syntax_errors(self):
        """Test escalation with multiple syntax errors."""
        orchestrator = MetaOrchestrator()
        config = EscalationConfig()

        # Create result with syntax errors
        analysis = FailureAnalysis(
            test_pass_rate=0.75,
            coverage_percent=70.0,
            assertion_depth=4.0,
            confidence_score=0.80,
            syntax_errors=[
                SyntaxError("error 1"),
                SyntaxError("error 2"),
                SyntaxError("error 3"),
                SyntaxError("error 4"),
            ],
        )

        result = TierResult(
            tier=Tier.CHEAP,
            model="gpt-4o-mini",
            attempt=2,  # Met min attempts
            timestamp=datetime.now(),
            failure_analysis=analysis,
        )

        should_escalate, reason = orchestrator.should_escalate(
            Tier.CHEAP, result, attempt=2, config=config
        )

        # Multiple syntax errors should trigger escalation
        assert should_escalate is True
        assert "syntax" in reason.lower()

    def test_should_not_escalate_good_quality(self):
        """Test no escalation with good quality."""
        orchestrator = MetaOrchestrator()
        config = EscalationConfig()

        # Create result with excellent CQS (well above threshold)
        analysis = FailureAnalysis(
            test_pass_rate=0.95,
            coverage_percent=90.0,
            assertion_depth=9.0,  # Will give 90 for assertion quality
            confidence_score=0.95,
        )

        result = TierResult(
            tier=Tier.CHEAP,
            model="gpt-4o-mini",
            attempt=2,  # Met min attempts
            timestamp=datetime.now(),
            failure_analysis=analysis,
            # Add generated items with high quality scores
            generated_items=[
                {"quality_score": 95},
                {"quality_score": 90},
                {"quality_score": 92},
                {"quality_score": 88},
                {"quality_score": 91},
            ],
        )

        # CQS should be: 0.4*95 + 0.25*90 + 0.2*90 + 0.15*95 = 92.5
        # Success rate: 5/5 = 100% (all above 80 threshold)
        # Both well above escalation thresholds
        should_escalate, reason = orchestrator.should_escalate(
            Tier.CHEAP, result, attempt=2, config=config
        )

        # Excellent quality should not escalate
        assert should_escalate is False

    def test_should_escalate_min_attempts_not_met(self):
        """Test no escalation when minimum attempts not met."""
        orchestrator = MetaOrchestrator()
        config = EscalationConfig(cheap_min_attempts=2)

        # Even with poor quality, should not escalate on first attempt
        analysis = FailureAnalysis(
            test_pass_rate=0.50,
            coverage_percent=45.0,
        )

        result = TierResult(
            tier=Tier.CHEAP,
            model="gpt-4o-mini",
            attempt=1,  # First attempt
            timestamp=datetime.now(),
            failure_analysis=analysis,
        )

        should_escalate, reason = orchestrator.should_escalate(
            Tier.CHEAP, result, attempt=1, config=config
        )

        # Should not escalate (min attempts not met)
        assert should_escalate is False
        assert "attempt" in reason.lower()

    def test_detect_stagnation_consecutive_runs(self):
        """Test stagnation detection with consecutive low improvement."""
        orchestrator = MetaOrchestrator()

        # Simulate CQS history with minimal improvement (<5 points each)
        cqs_history = [75.0, 76.0, 77.0]  # Only 1 point improvement each

        # Check if stagnation detected
        is_stagnant, reason = orchestrator._detect_stagnation(
            cqs_history, improvement_threshold=5.0, consecutive_limit=2
        )

        # With <5 point improvement per run, should detect stagnation
        assert is_stagnant is True
        assert "consecutive" in reason.lower() or "stagnation" in reason.lower()

    def test_detect_no_stagnation_with_improvement(self):
        """Test no stagnation detected when improvements are good."""
        orchestrator = MetaOrchestrator()

        # CQS history with good improvements (>5 points)
        cqs_history = [70.0, 78.0, 86.0]  # 8-point improvements

        is_stagnant, reason = orchestrator._detect_stagnation(
            cqs_history, improvement_threshold=5.0, consecutive_limit=2
        )

        # Good improvements should not be stagnant
        assert is_stagnant is False

    def test_create_agent_team_cheap_tier(self):
        """Test agent team creation for cheap tier."""
        orchestrator = MetaOrchestrator()

        team = orchestrator.create_agent_team(Tier.CHEAP, failure_context=None)

        # Cheap tier should have minimal team
        assert team is not None
        assert isinstance(team, list)

    def test_create_agent_team_capable_tier(self):
        """Test agent team creation for capable tier with failure context."""
        orchestrator = MetaOrchestrator()

        failure_context = {
            "previous_tier": Tier.CHEAP,
            "previous_cqs": 65.0,
            "failures": [],
        }

        team = orchestrator.create_agent_team(Tier.CAPABLE, failure_context)

        # Capable tier should have more agents
        assert team is not None
        assert isinstance(team, list)

    def test_create_agent_team_premium_tier(self):
        """Test agent team creation for premium tier."""
        orchestrator = MetaOrchestrator()

        failure_context = {
            "previous_tier": Tier.CAPABLE,
            "previous_cqs": 75.0,
            "failures": [],
        }

        team = orchestrator.create_agent_team(Tier.PREMIUM, failure_context)

        # Premium tier should have full team
        assert team is not None
        assert isinstance(team, list)

    def test_build_tier_prompt_cheap(self):
        """Test prompt building for cheap tier."""
        orchestrator = MetaOrchestrator()

        prompt = orchestrator.build_tier_prompt(
            tier=Tier.CHEAP, base_task="Generate tests for app.py", failure_context=None
        )

        assert prompt is not None
        assert isinstance(prompt, str)
        assert len(prompt) > 0

    def test_build_tier_prompt_capable_with_context(self):
        """Test prompt building for capable tier with failure context."""
        orchestrator = MetaOrchestrator()

        failure_context = {
            "previous_tier": Tier.CHEAP,
            "cqs": 65.0,
            "failures": [{"error": "async syntax error"}],
        }

        prompt = orchestrator.build_tier_prompt(
            tier=Tier.CAPABLE,
            base_task="Generate tests for async functions",
            failure_context=failure_context,
        )

        assert prompt is not None
        assert isinstance(prompt, str)
        assert len(prompt) > 100  # Should be enhanced

    def test_build_tier_prompt_premium(self):
        """Test prompt building for premium tier."""
        orchestrator = MetaOrchestrator()

        failure_context = {
            "previous_tier": Tier.CAPABLE,
            "cqs": 75.0,
            "cheap_cqs": 65.0,
            "failures": [],
        }

        prompt = orchestrator.build_tier_prompt(
            tier=Tier.PREMIUM,
            base_task="Generate tests for complex async code",
            failure_context=failure_context,
        )

        assert prompt is not None
        assert isinstance(prompt, str)
        assert len(prompt) > 100  # Premium prompt should be comprehensive

    def test_should_escalate_low_quality_after_min_attempts(self):
        """Test escalation with low quality after meeting min attempts."""
        orchestrator = MetaOrchestrator()
        config = EscalationConfig()

        # Create result with low CQS
        analysis = FailureAnalysis(
            test_pass_rate=0.50,
            coverage_percent=45.0,
            assertion_depth=2.0,
            confidence_score=0.60,
        )

        result = TierResult(
            tier=Tier.CHEAP,
            model="gpt-4o-mini",
            attempt=2,  # Met minimum attempts
            timestamp=datetime.now(),
            failure_analysis=analysis,
        )

        should_escalate, reason = orchestrator.should_escalate(
            Tier.CHEAP, result, attempt=2, config=config
        )

        # Low CQS after min attempts should trigger escalation
        assert should_escalate is True


class TestMetaOrchestratorEdgeCases:
    """Test edge cases and error handling."""

    def test_escalate_from_premium_tier(self):
        """Test escalation decision from premium tier (should not escalate)."""
        orchestrator = MetaOrchestrator()
        config = EscalationConfig()

        # Even with poor quality at premium tier
        analysis = FailureAnalysis(test_pass_rate=0.60, coverage_percent=50.0)

        result = TierResult(
            tier=Tier.PREMIUM,
            model="claude-opus-4",
            attempt=1,
            timestamp=datetime.now(),
            failure_analysis=analysis,
        )

        should_escalate, reason = orchestrator.should_escalate(
            Tier.PREMIUM, result, attempt=1, config=config
        )

        # Cannot escalate beyond premium
        assert should_escalate is False
        assert "premium" in reason.lower() or "final" in reason.lower()

    def test_detect_stagnation_insufficient_history(self):
        """Test stagnation detection with insufficient history."""
        orchestrator = MetaOrchestrator()

        # Only 1 data point - cannot detect stagnation (need consecutive_limit + 1)
        cqs_history = [75.0]

        is_stagnant, reason = orchestrator._detect_stagnation(
            cqs_history, improvement_threshold=5.0, consecutive_limit=2
        )

        assert is_stagnant is False
        assert "insufficient" in reason.lower() or "history" in reason.lower()
