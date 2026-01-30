"""Behavioral tests for workflows/base.py - core workflow execution.

Tests the BaseWorkflow class which is the foundation for ALL workflows.
Target: 90%+ coverage for this critical 908-line module.

Copyright 2026 Smart-AI-Memory
Licensed under Apache 2.0
"""

from unittest.mock import AsyncMock, patch

import pytest

from empathy_os.workflows.base import (
    BaseWorkflow,
    CostReport,
    ModelProvider,
    ModelTier,
    WorkflowResult,
    _build_provider_models,
    _get_history_store,
    _load_workflow_history,
)

# =============================================================================
# Test Enums and Helper Functions
# =============================================================================


class TestModelTier:
    """Test ModelTier enum functionality."""

    def test_model_tier_values(self):
        """Test enum values are correct."""
        assert ModelTier.CHEAP.value == "cheap"
        assert ModelTier.CAPABLE.value == "capable"
        assert ModelTier.PREMIUM.value == "premium"

    def test_model_tier_to_unified(self):
        """Test conversion to unified ModelTier."""
        from empathy_os.models import ModelTier as UnifiedModelTier

        cheap = ModelTier.CHEAP.to_unified()
        assert isinstance(cheap, UnifiedModelTier)
        assert cheap.value == "cheap"


class TestModelProvider:
    """Test ModelProvider enum functionality."""

    def test_model_provider_values(self):
        """Test enum values are correct."""
        assert ModelProvider.ANTHROPIC.value == "anthropic"
        assert ModelProvider.OPENAI.value == "openai"

    def test_model_provider_to_unified(self):
        """Test conversion to unified ModelProvider."""
        from empathy_os.models import ModelProvider as UnifiedModelProvider

        anthropic = ModelProvider.ANTHROPIC.to_unified()
        assert isinstance(anthropic, UnifiedModelProvider)


class TestBuildProviderModels:
    """Test _build_provider_models helper function."""

    def test_build_provider_models_returns_dict(self):
        """Test that function returns provider->tier->model mapping."""
        models = _build_provider_models()

        assert isinstance(models, dict)
        assert len(models) > 0
        # Should have ModelProvider keys
        assert all(isinstance(k, ModelProvider) for k in models.keys())


class TestWorkflowHistory:
    """Test workflow history functions."""

    def test_get_history_store_returns_store(self, tmp_path, monkeypatch):
        """Test _get_history_store returns history store object."""
        monkeypatch.chdir(tmp_path)
        history_store = _get_history_store()

        assert history_store is not None
        # It returns a WorkflowHistoryStore object with record_run and query_runs methods
        assert hasattr(history_store, "record_run")
        assert hasattr(history_store, "query_runs")
        assert hasattr(history_store, "get_stats")

    def test_load_workflow_history_returns_empty_if_missing(self, tmp_path):
        """Test _load_workflow_history returns empty list if file doesn't exist."""
        history_file = tmp_path / "test_history.json"

        history = _load_workflow_history(str(history_file))

        assert isinstance(history, list)
        assert len(history) == 0
        # Function doesn't create file - just returns empty list
        assert not history_file.exists()

    def test_load_workflow_history_loads_existing(self, tmp_path):
        """Test _load_workflow_history loads existing history."""
        import json

        history_file = tmp_path / "history.json"
        test_data = [{"workflow": "test", "timestamp": "2026-01-01"}]
        history_file.write_text(json.dumps(test_data))

        loaded = _load_workflow_history(str(history_file))

        assert loaded == test_data

    def test_save_workflow_run_appends_to_history(self, tmp_path):
        """Test WorkflowHistoryStore.record_run stores run data."""
        import uuid
        from datetime import datetime

        # Create a temporary database for this test
        db_path = tmp_path / "test_history.db"

        # Create a mock WorkflowResult with correct CostReport signature
        mock_result = WorkflowResult(
            success=True,
            stages=[],
            final_output={"test": "data"},
            cost_report=CostReport(
                total_cost=1.23,
                baseline_cost=2.50,
                savings=1.27,
                savings_percent=50.8,
            ),
            started_at=datetime.now(),
            completed_at=datetime.now(),
            total_duration_ms=100,
        )

        # Use WorkflowHistoryStore directly with isolated db
        from empathy_os.workflows.history import WorkflowHistoryStore
        store = WorkflowHistoryStore(str(db_path))

        # Save a run
        run_id = str(uuid.uuid4())
        store.record_run(
            run_id=run_id,
            workflow_name="test_workflow",
            provider="anthropic",
            result=mock_result,
        )

        # Verify it was saved
        stats = store.get_stats()
        assert stats["total_runs"] == 1
        assert stats["total_cost"] > 0

        store.close()

    def test_get_workflow_stats_calculates_totals(self, tmp_path):
        """Test WorkflowHistoryStore.get_stats returns expected keys."""
        # Create isolated test database
        db_path = tmp_path / "test_stats.db"

        # Use WorkflowHistoryStore directly
        from empathy_os.workflows.history import WorkflowHistoryStore
        store = WorkflowHistoryStore(str(db_path))

        # Get stats from empty database
        stats = store.get_stats()

        # Verify expected keys are present
        assert "total_runs" in stats
        assert "total_cost" in stats
        assert "by_workflow" in stats
        assert "by_provider" in stats

        # New empty database should have 0 runs
        assert stats["total_runs"] == 0
        assert stats["total_cost"] == 0.0

        store.close()


# =============================================================================
# Concrete Workflow Implementation for Testing
# =============================================================================


class SimpleTestWorkflow(BaseWorkflow):
    """Simple concrete workflow for testing BaseWorkflow."""

    name = "test_workflow"
    description = "Simple test workflow"
    stages = ["analyze", "synthesize"]
    tier_map = {
        "analyze": ModelTier.CHEAP,
        "synthesize": ModelTier.CAPABLE,
    }

    def __init__(self, **kwargs):
        """Initialize with minimal config."""
        super().__init__(**kwargs)

    async def run_stage(
        self, stage_name: str, tier: ModelTier, input_data: dict, context: dict
    ) -> dict:
        """Run a single workflow stage (implementation for abstract method)."""
        # Simple mock implementation for testing
        return {
            "content": f"Mock result for {stage_name}",
            "usage": {"input_tokens": 10, "output_tokens": 20},
        }


# =============================================================================
# Test BaseWorkflow Core Methods
# =============================================================================


class TestBaseWorkflowInitialization:
    """Test BaseWorkflow initialization."""

    def test_workflow_initializes_with_required_params(self):
        """Test workflow can be initialized."""
        workflow = SimpleTestWorkflow()

        assert workflow.name == "test_workflow"
        assert workflow.default_provider == ModelProvider.ANTHROPIC
        assert "analyze" in workflow.stages
        assert "synthesize" in workflow.stages

    def test_workflow_has_cost_tracking(self):
        """Test workflow initializes cost tracking."""
        workflow = SimpleTestWorkflow()

        assert hasattr(workflow, "total_cost")
        assert workflow.total_cost == 0.0
        assert hasattr(workflow, "total_input_tokens")
        assert hasattr(workflow, "total_output_tokens")


class TestWorkflowModelSelection:
    """Test model selection logic."""

    def test_get_model_for_tier_returns_correct_model(self):
        """Test get_model_for_tier returns model for tier."""
        workflow = SimpleTestWorkflow()

        cheap_model = workflow.get_model_for_tier(ModelTier.CHEAP)
        assert "haiku" in cheap_model.lower()

        capable_model = workflow.get_model_for_tier(ModelTier.CAPABLE)
        assert "sonnet" in capable_model.lower()

    def test_get_tier_for_stage_returns_stage_hint(self):
        """Test get_tier_for_stage returns stage's tier_hint."""
        workflow = SimpleTestWorkflow()

        tier = workflow.get_tier_for_stage("analyze")
        assert tier == ModelTier.CHEAP

        tier2 = workflow.get_tier_for_stage("synthesize")
        assert tier2 == ModelTier.CAPABLE


class TestWorkflowStageExecution:
    """Test workflow stage execution."""

    @pytest.mark.asyncio
    async def test_call_llm_makes_api_request(self):
        """Test _call_llm makes LLM API request."""
        workflow = SimpleTestWorkflow()

        # Mock the LLM executor
        mock_executor = AsyncMock()
        mock_executor.execute_with_caching = AsyncMock(
            return_value={
                "content": "test response",
                "usage": {"input_tokens": 10, "output_tokens": 20},
            }
        )

        with patch.object(workflow, "_get_executor", return_value=mock_executor):
            result = await workflow._call_llm(
                tier=ModelTier.CHEAP, user_prompt="test prompt", context={}
            )

            assert result["content"] == "test response"
            mock_executor.execute_with_caching.assert_called_once()

    @pytest.mark.asyncio
    async def test_run_stage_executes_stage(self):
        """Test run_stage executes a workflow stage."""
        workflow = SimpleTestWorkflow()

        # Mock _call_llm
        with patch.object(
            workflow,
            "_call_llm",
            new=AsyncMock(
                return_value={
                    "content": "stage result",
                    "usage": {"input_tokens": 5, "output_tokens": 10},
                }
            ),
        ):
            result = await workflow.run_stage(
                stage_name="analyze",
                tier=ModelTier.CHEAP,
                input_data={"text": "analyze this"},
                context={},
            )

            assert "content" in result
            assert result["content"] == "stage result"

    def test_should_skip_stage_defaults_to_false(self):
        """Test should_skip_stage returns False by default."""
        workflow = SimpleTestWorkflow()

        should_skip, reason = workflow.should_skip_stage("analyze", {"text": "test"})

        assert should_skip is False
        assert reason is None

    def test_validate_output_defaults_to_true(self):
        """Test validate_output returns True by default."""
        workflow = SimpleTestWorkflow()

        is_valid, error = workflow.validate_output({"content": "result"})

        assert is_valid is True
        assert error is None


class TestWorkflowCostCalculation:
    """Test cost calculation methods."""

    def test_calculate_cost_returns_float(self):
        """Test _calculate_cost returns cost for tier."""
        workflow = SimpleTestWorkflow()

        cost = workflow._calculate_cost(
            tier=ModelTier.CHEAP, input_tokens=100, output_tokens=50
        )

        assert isinstance(cost, float)
        assert cost > 0

    def test_calculate_baseline_cost_uses_premium(self):
        """Test _calculate_baseline_cost uses premium pricing."""
        workflow = SimpleTestWorkflow()

        baseline = workflow._calculate_baseline_cost(input_tokens=100, output_tokens=50)

        assert isinstance(baseline, float)
        assert baseline > 0

        # Baseline should be more expensive than cheap tier
        cheap_cost = workflow._calculate_cost(ModelTier.CHEAP, 100, 50)
        assert baseline > cheap_cost

    def test_generate_cost_report_creates_report(self):
        """Test _generate_cost_report creates CostReport."""
        workflow = SimpleTestWorkflow()
        workflow.total_cost = 1.23
        workflow.total_input_tokens = 100
        workflow.total_output_tokens = 50

        report = workflow._generate_cost_report()

        assert isinstance(report, CostReport)
        assert report.total_cost == 1.23
        assert report.input_tokens == 100
        assert report.output_tokens == 50


class TestWorkflowComplexityAssessment:
    """Test complexity assessment."""

    def test_assess_complexity_returns_tier_str(self):
        """Test _assess_complexity returns tier recommendation."""
        workflow = SimpleTestWorkflow()

        # Simple input
        complexity = workflow._assess_complexity({"text": "short"})
        assert complexity in ["cheap", "capable", "premium"]

        # Complex input
        long_text = "word " * 500  # Long input
        complexity2 = workflow._assess_complexity({"text": long_text})
        assert complexity2 in ["cheap", "capable", "premium"]


class TestWorkflowDescribe:
    """Test workflow description."""

    def test_describe_returns_string(self):
        """Test describe() returns workflow description."""
        workflow = SimpleTestWorkflow()

        description = workflow.describe()

        assert isinstance(description, str)
        assert "test_workflow" in description.lower()
        assert "analyze" in description.lower()


# =============================================================================
# Integration Test: Full Workflow Execution
# =============================================================================


class TestFullWorkflowExecution:
    """Integration test for complete workflow execution."""

    @pytest.mark.asyncio
    async def test_execute_runs_all_stages(self):
        """Test execute() runs all stages and returns result."""
        workflow = SimpleTestWorkflow()

        # Mock _call_llm to avoid real API calls
        with patch.object(
            workflow,
            "_call_llm",
            new=AsyncMock(
                return_value={
                    "content": "mock response",
                    "usage": {"input_tokens": 10, "output_tokens": 20},
                }
            ),
        ):
            result = await workflow.execute(text="test input")

            assert isinstance(result, WorkflowResult)
            assert result.workflow_name == "test_workflow"
            assert result.stages_executed  # List of executed stages
            assert result.cost_report.total_cost >= 0


# Run with:
# pytest tests/behavioral/test_workflow_base_behavioral.py -v --cov=src/empathy_os/workflows/base.py --cov-report=term-missing -n 0
