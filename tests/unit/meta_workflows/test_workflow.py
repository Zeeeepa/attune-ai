"""Unit tests for MetaWorkflow orchestrator.

Tests cover:
- Workflow initialization
- Mock agent execution
- Result storage and retrieval
- Report generation
- Error handling

Created: 2026-01-17
"""

import json
from unittest.mock import Mock, patch

import pytest

from attune.meta_workflows.models import FormResponse
from attune.meta_workflows.template_registry import TemplateRegistry
from attune.meta_workflows.workflow import (
    MetaWorkflow,
    list_execution_results,
    load_execution_result,
)


class TestMetaWorkflowInitialization:
    """Test MetaWorkflow initialization."""

    def test_init_with_template(self):
        """Test initialization with direct template."""
        registry = TemplateRegistry(storage_dir=".attune/meta_workflows/templates")
        template = registry.load_template("release-prep")

        workflow = MetaWorkflow(template=template)

        assert workflow.template == template
        assert workflow.template.template_id == "release-prep"

    def test_init_with_template_id(self):
        """Test initialization with template_id (loads template)."""
        with patch("attune.meta_workflows.workflow.TemplateRegistry") as mock_registry:
            mock_template = Mock()
            mock_template.template_id = "test_template"
            mock_registry.return_value.load_template.return_value = mock_template

            workflow = MetaWorkflow(template_id="test_template")

            assert workflow.template == mock_template
            mock_registry.return_value.load_template.assert_called_once_with("test_template")

    def test_init_with_neither_raises_error(self):
        """Test initialization without template or template_id raises error."""
        with pytest.raises(ValueError, match="Must provide either template or template_id"):
            MetaWorkflow()

    def test_init_with_invalid_template_id_raises_error(self):
        """Test initialization with non-existent template_id raises error."""
        with patch("attune.meta_workflows.workflow.TemplateRegistry") as mock_registry:
            mock_registry.return_value.load_template.return_value = None

            with pytest.raises(ValueError, match="Template not found"):
                MetaWorkflow(template_id="nonexistent")

    def test_init_with_custom_storage_dir(self, tmp_path):
        """Test initialization with custom storage directory."""
        registry = TemplateRegistry(storage_dir=".attune/meta_workflows/templates")
        template = registry.load_template("release-prep")

        storage_dir = tmp_path / "custom_storage"
        workflow = MetaWorkflow(template=template, storage_dir=str(storage_dir))

        assert workflow.storage_dir == storage_dir
        assert storage_dir.exists()  # Should be created


class TestMetaWorkflowExecution:
    """Test meta-workflow execution."""

    def test_execute_with_provided_response(self, tmp_path):
        """Test execution with pre-provided form response."""
        registry = TemplateRegistry(storage_dir=".attune/meta_workflows/templates")
        template = registry.load_template("release-prep")

        response = FormResponse(
            template_id="release-prep",
            responses={
                "security_scan": "Yes",
                "test_coverage_required": "80%",
                "quality_checks": ["Linting (ruff)"],
                "coverage_threshold": "80%",
                "publish_to": "Skip publishing",
                "create_git_tag": "No",
                "update_changelog": "No",
            },
        )

        workflow = MetaWorkflow(template=template, storage_dir=str(tmp_path))
        result = workflow.execute(form_response=response, mock_execution=True)

        assert result.success is True
        assert result.template_id == "release-prep"
        assert len(result.agents_created) > 0
        assert len(result.agent_results) == len(result.agents_created)
        assert result.total_cost > 0
        assert result.total_duration > 0

    def test_execute_mock_agents(self, tmp_path):
        """Test mock agent execution."""
        registry = TemplateRegistry(storage_dir=".attune/meta_workflows/templates")
        template = registry.load_template("release-prep")

        response = FormResponse(
            template_id="release-prep",
            responses={
                "security_scan": "Yes",
                "coverage_threshold": "80%",
                "publish_to": "Skip publishing",
                "create_git_tag": "No",
                "update_changelog": "No",
            },
        )

        workflow = MetaWorkflow(template=template, storage_dir=str(tmp_path))
        result = workflow.execute(form_response=response, mock_execution=True)

        # All mock executions should succeed
        assert all(agent_result.success for agent_result in result.agent_results)

        # Check mock result structure
        for agent_result in result.agent_results:
            assert agent_result.agent_id is not None
            assert agent_result.role is not None
            assert agent_result.cost > 0
            assert agent_result.duration > 0
            assert agent_result.tier_used in ["cheap", "capable", "premium"]
            assert isinstance(agent_result.output, dict)


class TestResultStorage:
    """Test result storage and retrieval."""

    def test_result_saved_to_disk(self, tmp_path):
        """Test that result is saved to disk."""
        registry = TemplateRegistry(storage_dir=".attune/meta_workflows/templates")
        template = registry.load_template("release-prep")

        response = FormResponse(
            template_id="release-prep",
            responses={"security_scan": "No", "coverage_threshold": "80%"},
        )

        workflow = MetaWorkflow(template=template, storage_dir=str(tmp_path))
        result = workflow.execute(form_response=response, mock_execution=True)

        # Check files exist
        run_dir = tmp_path / result.run_id
        assert run_dir.exists()
        assert (run_dir / "config.json").exists()
        assert (run_dir / "form_responses.json").exists()
        assert (run_dir / "agents.json").exists()
        assert (run_dir / "result.json").exists()
        assert (run_dir / "report.txt").exists()

    def test_config_file_content(self, tmp_path):
        """Test config file contains correct data."""
        registry = TemplateRegistry(storage_dir=".attune/meta_workflows/templates")
        template = registry.load_template("release-prep")

        response = FormResponse(template_id="release-prep", responses={"coverage_threshold": "80%"})

        workflow = MetaWorkflow(template=template, storage_dir=str(tmp_path))
        result = workflow.execute(form_response=response, mock_execution=True)

        config_file = tmp_path / result.run_id / "config.json"
        config_data = json.loads(config_file.read_text())

        assert config_data["template_id"] == "release-prep"
        assert config_data["template_name"] == "Release Preparation"
        assert config_data["run_id"] == result.run_id

    def test_report_generation(self, tmp_path):
        """Test human-readable report is generated."""
        registry = TemplateRegistry(storage_dir=".attune/meta_workflows/templates")
        template = registry.load_template("release-prep")

        response = FormResponse(
            template_id="release-prep",
            responses={"security_scan": "Yes", "coverage_threshold": "80%"},
        )

        workflow = MetaWorkflow(template=template, storage_dir=str(tmp_path))
        result = workflow.execute(form_response=response, mock_execution=True)

        report_file = tmp_path / result.run_id / "report.txt"
        report = report_file.read_text()

        # Check report contains key information
        assert "Meta-Workflow Execution Report" in report
        assert result.run_id in report
        assert "Release Preparation" in report
        assert "Summary" in report
        assert "Form Responses" in report
        assert "Agents Created" in report
        assert "Execution Results" in report
        assert "Cost Breakdown" in report


class TestResultLoading:
    """Test loading saved results."""

    def test_load_execution_result(self, tmp_path):
        """Test loading a saved execution result."""
        registry = TemplateRegistry(storage_dir=".attune/meta_workflows/templates")
        template = registry.load_template("release-prep")

        response = FormResponse(template_id="release-prep", responses={"coverage_threshold": "80%"})

        workflow = MetaWorkflow(template=template, storage_dir=str(tmp_path))
        original_result = workflow.execute(form_response=response, mock_execution=True)

        # Load the result
        loaded_result = load_execution_result(original_result.run_id, storage_dir=str(tmp_path))

        assert loaded_result.run_id == original_result.run_id
        assert loaded_result.template_id == original_result.template_id
        assert loaded_result.success == original_result.success
        assert loaded_result.total_cost == original_result.total_cost
        assert len(loaded_result.agents_created) == len(original_result.agents_created)

    def test_load_nonexistent_result_raises_error(self, tmp_path):
        """Test loading non-existent result raises error."""
        with pytest.raises(FileNotFoundError, match="Result not found"):
            load_execution_result("nonexistent-run-id", storage_dir=str(tmp_path))

    def test_list_execution_results(self, tmp_path):
        """Test listing all execution results."""
        import time

        registry = TemplateRegistry(storage_dir=".attune/meta_workflows/templates")
        template = registry.load_template("release-prep")

        response = FormResponse(template_id="release-prep", responses={"coverage_threshold": "80%"})

        # Create multiple executions
        workflow = MetaWorkflow(template=template, storage_dir=str(tmp_path))

        result1 = workflow.execute(form_response=response, mock_execution=True)
        time.sleep(1.1)  # Ensure different timestamp
        result2 = workflow.execute(form_response=response, mock_execution=True)

        # List results
        results = list_execution_results(storage_dir=str(tmp_path))

        assert len(results) == 2
        assert result1.run_id in results
        assert result2.run_id in results

        # Should be sorted (newest first)
        assert results[0] >= results[1]  # Lexicographic comparison

    def test_list_empty_directory(self, tmp_path):
        """Test listing results from empty directory."""
        results = list_execution_results(storage_dir=str(tmp_path))
        assert len(results) == 0


class TestErrorHandling:
    """Test error handling in workflow execution."""

    def test_execution_error_creates_error_result(self, tmp_path):
        """Test that execution errors are captured in result."""
        registry = TemplateRegistry(storage_dir=".attune/meta_workflows/templates")
        template = registry.load_template("release-prep")

        response = FormResponse(template_id="release-prep", responses={"coverage_threshold": "80%"})

        workflow = MetaWorkflow(template=template, storage_dir=str(tmp_path))

        # Mock agent_creator to raise error
        def mock_error(*args, **kwargs):
            raise RuntimeError("Test error")

        workflow.agent_creator.create_agents = mock_error

        # Execution should raise error
        with pytest.raises(ValueError, match="Meta-workflow execution failed"):
            workflow.execute(form_response=response, mock_execution=True)

        # But error result should be saved
        results = list_execution_results(storage_dir=str(tmp_path))
        assert len(results) == 1

        error_result = load_execution_result(results[0], storage_dir=str(tmp_path))
        assert error_result.success is False
        assert error_result.error is not None
        assert "Test error" in error_result.error


class TestAgentExecution:
    """Test agent execution logic."""

    def test_mock_execution_cost_by_tier(self, tmp_path):
        """Test mock execution assigns correct costs by tier."""
        registry = TemplateRegistry(storage_dir=".attune/meta_workflows/templates")
        template = registry.load_template("release-prep")

        # Get full quality response to create all agents
        response = FormResponse(
            template_id="release-prep",
            responses={
                "security_scan": "Yes",
                "test_coverage_required": "90%",
                "quality_checks": [
                    "Type checking (mypy)",
                    "Linting (ruff)",
                    "Security scan (bandit)",
                ],
                "coverage_threshold": "80%",
                "publish_to": "PyPI (production)",
                "create_git_tag": "Yes",
                "update_changelog": "Yes",
            },
        )

        workflow = MetaWorkflow(template=template, storage_dir=str(tmp_path))
        result = workflow.execute(form_response=response, mock_execution=True)

        # Check that costs vary by tier
        cheap_costs = [r.cost for r in result.agent_results if r.tier_used == "cheap"]
        capable_costs = [r.cost for r in result.agent_results if r.tier_used == "capable"]

        if cheap_costs:
            assert all(cost == 0.05 for cost in cheap_costs)
        if capable_costs:
            assert all(cost >= 0.15 for cost in capable_costs)

    def test_all_agents_executed(self, tmp_path):
        """Test that all created agents are executed."""
        registry = TemplateRegistry(storage_dir=".attune/meta_workflows/templates")
        template = registry.load_template("release-prep")

        response = FormResponse(
            template_id="release-prep",
            responses={"security_scan": "Yes", "coverage_threshold": "80%"},
        )

        workflow = MetaWorkflow(template=template, storage_dir=str(tmp_path))
        result = workflow.execute(form_response=response, mock_execution=True)

        # Number of results should equal number of agents
        assert len(result.agent_results) == len(result.agents_created)

        # All agent IDs should match
        agent_ids = {agent.agent_id for agent in result.agents_created}
        result_agent_ids = {result.agent_id for result in result.agent_results}
        assert agent_ids == result_agent_ids
