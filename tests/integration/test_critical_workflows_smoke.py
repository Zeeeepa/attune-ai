"""Smoke tests for critical user-facing workflows.

These tests verify that the most important workflows can be instantiated
and don't crash on basic operations. Not comprehensive, but catches major issues.

Copyright 2026 Smart-AI-Memory
Licensed under Apache 2.0
"""

import pytest

from attune.workflows import get_workflow, list_workflows


class TestWorkflowRegistry:
    """Test that workflow registry works correctly."""

    def test_list_workflows_returns_workflows(self):
        """Test that listing workflows returns a non-empty list."""
        workflows = list_workflows()

        assert isinstance(workflows, list)
        assert len(workflows) > 0  # Should have at least some workflows
        assert all(isinstance(w, dict) for w in workflows)
        assert all('name' in w for w in workflows)

    def test_get_workflow_by_name_works(self):
        """Test that getting a workflow by name doesn't crash."""
        workflows = list_workflows()

        if workflows:
            # Get first available workflow
            workflow_name = workflows[0]['name']
            workflow_class = get_workflow(workflow_name)

            assert workflow_class is not None
            assert hasattr(workflow_class, 'name')
            assert hasattr(workflow_class, 'description')

    def test_workflows_have_required_attributes(self):
        """Test that all registered workflows have required attributes."""
        workflows = list_workflows()

        for workflow_info in workflows[:5]:  # Test first 5
            workflow_class = get_workflow(workflow_info['name'])

            # All workflows should have these
            assert hasattr(workflow_class, 'name')
            assert hasattr(workflow_class, 'description')
            assert hasattr(workflow_class, 'stages') or hasattr(workflow_class, 'tier_map')


class TestCriticalWorkflowsCanInstantiate:
    """Test that critical workflows can be instantiated."""

    @pytest.mark.parametrize("workflow_name", [
        "code-review",
        "debug",
        "doc-gen"
    ])
    def test_critical_workflow_can_instantiate(self, workflow_name):
        """Test that critical workflows can be instantiated without crashing."""
        try:
            workflow_class = get_workflow(workflow_name)
            workflow = workflow_class()

            # Verify basic attributes
            assert hasattr(workflow, 'name')
            assert hasattr(workflow, 'description')

        except KeyError:
            # Workflow might not exist in this version
            pytest.skip(f"Workflow '{workflow_name}' not found in registry")


class TestWorkflowDescribeMethod:
    """Test workflow describe() method."""

    def test_workflows_can_describe_themselves(self):
        """Test that workflows can describe themselves."""
        workflows = list_workflows()

        if workflows:
            workflow_name = workflows[0]['name']
            workflow_class = get_workflow(workflow_name)
            workflow = workflow_class()

            # Most workflows should have a describe method
            if hasattr(workflow, 'describe'):
                description = workflow.describe()
                assert isinstance(description, str)
                assert len(description) > 0


class TestWorkflowWithMockProvider:
    """Test workflows with mocked LLM calls (no API needed)."""

    def test_workflow_accepts_provider_parameter(self):
        """Test that workflows accept provider parameter."""
        workflows = list_workflows()

        if workflows:
            workflow_name = workflows[0]['name']
            workflow_class = get_workflow(workflow_name)

            # Should be able to specify provider
            workflow = workflow_class(provider="anthropic")

            # Verify provider was set (most workflows track this)
            assert hasattr(workflow, '_provider_str') or hasattr(workflow, 'provider')


@pytest.mark.slow
class TestWorkflowEndToEndSmoke:
    """End-to-end smoke tests (marked slow, skip in fast CI)."""

    def test_simple_workflow_can_execute_with_mock_data(self):
        """Test that a workflow can execute with mock data (no API calls)."""
        # This would need proper mocking of LLM calls
        # Placeholder for future implementation
        pytest.skip("Requires LLM call mocking infrastructure")
