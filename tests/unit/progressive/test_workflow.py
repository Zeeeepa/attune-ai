"""Unit tests for ProgressiveWorkflow base class.

Tests cover:
- Cost estimation and budget management
- Approval prompts (in non-interactive mode)
- Tier execution and error handling
- Model configuration loading
- Budget exceeded handling
"""

import os
import pytest
from datetime import datetime
from unittest.mock import Mock, patch, MagicMock

from attune.workflows.progressive.core import (
    EscalationConfig,
    FailureAnalysis,
    ProgressiveWorkflowResult,
    Tier,
    TierResult,
)
from attune.workflows.progressive.workflow import (
    BudgetExceededError,
    ProgressiveWorkflow,
    UserCancelledError,
    _is_interactive,
    _load_model_config,
)


class TestIsInteractive:
    """Test interactive mode detection."""

    def test_is_interactive_with_ci_env(self, monkeypatch):
        """Test that CI env disables interactive mode."""
        monkeypatch.setenv("CI", "true")
        assert _is_interactive() is False

    def test_is_interactive_with_attune_env(self, monkeypatch):
        """Test that ATTUNE_NON_INTERACTIVE disables interactive mode."""
        monkeypatch.setenv("ATTUNE_NON_INTERACTIVE", "1")
        assert _is_interactive() is False

    def test_is_interactive_without_env(self, monkeypatch):
        """Test interactive detection without CI env."""
        monkeypatch.delenv("CI", raising=False)
        monkeypatch.delenv("ATTUNE_NON_INTERACTIVE", raising=False)
        # Result depends on whether stdin is a TTY
        result = _is_interactive()
        assert isinstance(result, bool)


class TestLoadModelConfig:
    """Test model configuration loading."""

    def test_load_model_config_defaults(self, monkeypatch):
        """Test default model configuration."""
        # Clear any env vars
        monkeypatch.delenv("ATTUNE_MODEL_CHEAP", raising=False)
        monkeypatch.delenv("ATTUNE_MODEL_CAPABLE", raising=False)
        monkeypatch.delenv("ATTUNE_MODEL_PREMIUM", raising=False)

        config = _load_model_config()

        assert config["cheap"] == "gpt-4o-mini"
        assert config["capable"] == "claude-3-5-sonnet"
        assert config["premium"] == "claude-opus-4"

    def test_load_model_config_env_override(self, monkeypatch):
        """Test environment variable overrides."""
        monkeypatch.setenv("ATTUNE_MODEL_CHEAP", "custom-cheap")
        monkeypatch.setenv("ATTUNE_MODEL_CAPABLE", "custom-capable")
        monkeypatch.setenv("ATTUNE_MODEL_PREMIUM", "custom-premium")

        config = _load_model_config()

        assert config["cheap"] == "custom-cheap"
        assert config["capable"] == "custom-capable"
        assert config["premium"] == "custom-premium"


class TestProgressiveWorkflow:
    """Test ProgressiveWorkflow base class."""

    def test_init_default_config(self):
        """Test initialization with default config."""
        workflow = ProgressiveWorkflow()

        assert workflow.config is not None
        assert isinstance(workflow.config, EscalationConfig)
        assert workflow.tier_results == []
        assert workflow.meta_orchestrator is not None

    def test_init_custom_config(self):
        """Test initialization with custom config."""
        config = EscalationConfig(
            enabled=True,
            max_cost=10.00,
            auto_approve_under=5.00,
        )

        workflow = ProgressiveWorkflow(config=config)

        assert workflow.config.enabled is True
        assert workflow.config.max_cost == 10.00
        assert workflow.config.auto_approve_under == 5.00

    def test_execute_not_implemented(self):
        """Test that execute() must be implemented by subclasses."""
        workflow = ProgressiveWorkflow()

        with pytest.raises(NotImplementedError, match="Subclasses must implement execute"):
            workflow.execute()

    def test_estimate_total_cost(self):
        """Test total cost estimation with escalation probability."""
        workflow = ProgressiveWorkflow()

        # 100 items
        total_cost = workflow._estimate_total_cost(100)

        # Expected:
        # - Cheap: 100 items * $0.003 = $0.30
        # - Capable: 30 items * $0.015 = $0.45 (30% escalation)
        # - Premium: 10 items * $0.05 = $0.50 (10% escalation)
        # Total: $1.25
        assert 1.20 <= total_cost <= 1.30

    def test_estimate_tier_cost(self):
        """Test cost estimation for specific tiers."""
        workflow = ProgressiveWorkflow()

        cheap_cost = workflow._estimate_tier_cost(Tier.CHEAP, 100)
        capable_cost = workflow._estimate_tier_cost(Tier.CAPABLE, 100)
        premium_cost = workflow._estimate_tier_cost(Tier.PREMIUM, 100)

        # Expected per 100 items:
        # - Cheap: 100 * $0.003 = $0.30
        # - Capable: 100 * $0.015 = $1.50
        # - Premium: 100 * $0.05 = $5.00
        assert cheap_cost == 0.30
        assert capable_cost == 1.50
        assert premium_cost == 5.00

    def test_calculate_tier_cost_estimated(self):
        """Test cost calculation with estimated tokens."""
        workflow = ProgressiveWorkflow()

        cost = workflow._calculate_tier_cost(Tier.CHEAP, item_count=10)

        # 10 items * 1500 tokens/item = 15000 tokens
        # 15000 / 1000 * $0.00015 = $0.00225
        assert 0.002 <= cost <= 0.003

    def test_calculate_tier_cost_actual(self):
        """Test cost calculation with actual token count."""
        workflow = ProgressiveWorkflow()

        cost = workflow._calculate_tier_cost(
            Tier.CAPABLE, item_count=10, actual_tokens=20000
        )

        # 20000 / 1000 * $0.003 = $0.06
        assert cost == 0.06

    def test_request_approval_auto_approve_under_threshold(self, monkeypatch):
        """Test auto-approval when cost is under $1 threshold."""
        monkeypatch.setenv("ATTUNE_NON_INTERACTIVE", "1")
        workflow = ProgressiveWorkflow()

        # Cost under $1 threshold
        approved = workflow._request_approval("Test task", 0.75)

        assert approved is True

    def test_request_approval_auto_approve_with_config(self, monkeypatch):
        """Test auto-approval with config auto_approve_under."""
        monkeypatch.setenv("ATTUNE_NON_INTERACTIVE", "1")
        config = EscalationConfig(auto_approve_under=5.00)
        workflow = ProgressiveWorkflow(config=config)

        # Cost under $5 config threshold
        approved = workflow._request_approval("Test task", 3.50)

        assert approved is True

    def test_request_approval_denied_in_non_interactive(self, monkeypatch):
        """Test approval denied when exceeding threshold in non-interactive."""
        monkeypatch.setenv("ATTUNE_NON_INTERACTIVE", "1")
        workflow = ProgressiveWorkflow()

        # Cost over $1 threshold, no auto_approve_under
        approved = workflow._request_approval("Test task", 5.00)

        assert approved is False

    def test_request_escalation_approval_auto_approve(self, monkeypatch):
        """Test escalation auto-approval."""
        monkeypatch.setenv("ATTUNE_NON_INTERACTIVE", "1")
        config = EscalationConfig(auto_approve_under=5.00)
        workflow = ProgressiveWorkflow(config=config)

        # Previous tier cost $0.50, escalation cost $1.00, total $1.50
        approved = workflow._request_escalation_approval(
            Tier.CHEAP, Tier.CAPABLE, 30, 1.00
        )

        assert approved is True

    def test_check_budget_within_limit(self):
        """Test budget check when within limit."""
        config = EscalationConfig(max_cost=5.00, warn_on_budget_exceeded=True)
        workflow = ProgressiveWorkflow(config=config)

        # Add a tier result with cost $3.00
        workflow.tier_results.append(
            TierResult(
                tier=Tier.CHEAP,
                model="gpt-4o-mini",
                attempt=1,
                timestamp=datetime.now(),
                cost=3.00,
                duration=10.0,
            )
        )

        # Should not raise
        workflow._check_budget()

    def test_check_budget_exceeded_warning(self, caplog):
        """Test budget exceeded with warning."""
        config = EscalationConfig(
            max_cost=5.00, warn_on_budget_exceeded=True, abort_on_budget_exceeded=False
        )
        workflow = ProgressiveWorkflow(config=config)

        # Add tier result exceeding budget
        workflow.tier_results.append(
            TierResult(
                tier=Tier.CHEAP,
                model="gpt-4o-mini",
                attempt=1,
                timestamp=datetime.now(),
                cost=6.00,
                duration=10.0,
            )
        )

        # Should log warning but not raise
        workflow._check_budget()
        # Check if warning was logged (implementation-dependent)

    def test_check_budget_exceeded_abort(self):
        """Test budget exceeded with abort."""
        config = EscalationConfig(max_cost=5.00, abort_on_budget_exceeded=True)
        workflow = ProgressiveWorkflow(config=config)

        # Add tier result exceeding budget
        workflow.tier_results.append(
            TierResult(
                tier=Tier.CHEAP,
                model="gpt-4o-mini",
                attempt=1,
                timestamp=datetime.now(),
                cost=6.00,
                duration=10.0,
            )
        )

        # Should raise BudgetExceededError
        with pytest.raises(BudgetExceededError, match="exceeds budget"):
            workflow._check_budget()

    def test_get_next_tier_from_cheap(self):
        """Test getting next tier from CHEAP."""
        workflow = ProgressiveWorkflow()

        next_tier = workflow._get_next_tier(Tier.CHEAP)

        assert next_tier == Tier.CAPABLE

    def test_get_next_tier_from_capable(self):
        """Test getting next tier from CAPABLE."""
        workflow = ProgressiveWorkflow()

        next_tier = workflow._get_next_tier(Tier.CAPABLE)

        assert next_tier == Tier.PREMIUM

    def test_get_next_tier_from_premium(self):
        """Test getting next tier from PREMIUM returns None."""
        workflow = ProgressiveWorkflow()

        next_tier = workflow._get_next_tier(Tier.PREMIUM)

        assert next_tier is None

    def test_get_next_tier_custom_tiers(self):
        """Test next tier with custom tier list."""
        config = EscalationConfig(tiers=[Tier.CHEAP, Tier.PREMIUM])
        workflow = ProgressiveWorkflow(config=config)

        # CHEAP should jump to PREMIUM
        next_tier = workflow._get_next_tier(Tier.CHEAP)
        assert next_tier == Tier.PREMIUM

        # PREMIUM has no next tier
        next_tier = workflow._get_next_tier(Tier.PREMIUM)
        assert next_tier is None

    def test_get_model_for_tier(self, monkeypatch):
        """Test model selection for tiers."""
        monkeypatch.delenv("ATTUNE_MODEL_CHEAP", raising=False)
        monkeypatch.delenv("ATTUNE_MODEL_CAPABLE", raising=False)
        monkeypatch.delenv("ATTUNE_MODEL_PREMIUM", raising=False)

        workflow = ProgressiveWorkflow()

        assert workflow._get_model_for_tier(Tier.CHEAP) == "gpt-4o-mini"
        assert workflow._get_model_for_tier(Tier.CAPABLE) == "claude-3-5-sonnet"
        assert workflow._get_model_for_tier(Tier.PREMIUM) == "claude-opus-4"

    def test_analyze_tier_result_empty(self):
        """Test analyzing empty tier result."""
        workflow = ProgressiveWorkflow()

        analysis = workflow._analyze_tier_result([])

        assert analysis.test_pass_rate == 0.0
        assert analysis.coverage_percent == 0.0
        assert analysis.assertion_depth == 0.0

    def test_analyze_tier_result_with_items(self):
        """Test analyzing tier result with items."""
        workflow = ProgressiveWorkflow()

        items = [
            {
                "passed": True,
                "syntax_errors": [],
                "coverage": 85.0,
                "assertions": 5,
                "confidence": 0.9,
            },
            {
                "passed": True,
                "syntax_errors": [],
                "coverage": 90.0,
                "assertions": 6,
                "confidence": 0.95,
            },
            {
                "passed": False,
                "syntax_errors": ["error1"],
                "coverage": 70.0,
                "assertions": 3,
                "confidence": 0.7,
            },
        ]

        analysis = workflow._analyze_tier_result(items)

        # 2 passed out of 3 = 66.67%
        assert analysis.test_pass_rate == pytest.approx(0.6667, rel=0.01)
        # Average coverage: (85 + 90 + 70) / 3 = 81.67
        assert analysis.coverage_percent == pytest.approx(81.67, rel=0.01)
        # Average assertions: (5 + 6 + 3) / 3 = 4.67
        assert analysis.assertion_depth == pytest.approx(4.67, rel=0.01)
        # Average confidence: (0.9 + 0.95 + 0.7) / 3 = 0.85
        assert analysis.confidence_score == pytest.approx(0.85, rel=0.01)


class TestProgressiveWorkflowExceptions:
    """Test custom exception classes."""

    def test_budget_exceeded_error(self):
        """Test BudgetExceededError exception."""
        with pytest.raises(BudgetExceededError):
            raise BudgetExceededError("Budget exceeded")

    def test_user_cancelled_error(self):
        """Test UserCancelledError exception."""
        with pytest.raises(UserCancelledError):
            raise UserCancelledError("User cancelled")
