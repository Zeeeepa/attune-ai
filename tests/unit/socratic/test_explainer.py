"""Tests for the Socratic workflow explainer module.

Copyright 2026 Smart-AI-Memory
Licensed under Fair Source License 0.9
"""



class TestAudienceLevel:
    """Tests for AudienceLevel enum."""

    def test_all_levels_exist(self):
        """Test all expected audience levels exist."""
        from empathy_os.socratic.explainer import AudienceLevel

        assert hasattr(AudienceLevel, "TECHNICAL")
        assert hasattr(AudienceLevel, "BUSINESS")
        assert hasattr(AudienceLevel, "BEGINNER")

    def test_level_values(self):
        """Test audience level values."""
        from empathy_os.socratic.explainer import AudienceLevel

        assert AudienceLevel.TECHNICAL.value == "technical"
        assert AudienceLevel.BUSINESS.value == "business"
        assert AudienceLevel.BEGINNER.value == "beginner"


class TestDetailLevel:
    """Tests for DetailLevel enum."""

    def test_all_levels_exist(self):
        """Test all expected detail levels exist."""
        from empathy_os.socratic.explainer import DetailLevel

        assert hasattr(DetailLevel, "BRIEF")
        assert hasattr(DetailLevel, "STANDARD")
        assert hasattr(DetailLevel, "DETAILED")


class TestOutputFormat:
    """Tests for OutputFormat enum."""

    def test_all_formats_exist(self):
        """Test all expected output formats exist."""
        from empathy_os.socratic.explainer import OutputFormat

        assert hasattr(OutputFormat, "TEXT")
        assert hasattr(OutputFormat, "MARKDOWN")
        assert hasattr(OutputFormat, "HTML")
        assert hasattr(OutputFormat, "JSON")


class TestExplanation:
    """Tests for Explanation dataclass."""

    def test_create_explanation(self):
        """Test creating an explanation."""
        from empathy_os.socratic.explainer import (
            AudienceLevel,
            DetailLevel,
            Explanation,
        )

        explanation = Explanation(
            title="Code Review Workflow",
            summary="This workflow automates code review.",
            sections=[
                {"heading": "Overview", "content": "The workflow consists of..."},
                {"heading": "Steps", "content": "1. Analyze code..."},
            ],
            audience=AudienceLevel.TECHNICAL,
            detail_level=DetailLevel.STANDARD,
        )

        assert explanation.title == "Code Review Workflow"
        assert explanation.audience == AudienceLevel.TECHNICAL
        assert len(explanation.sections) == 2

    def test_explanation_to_text(self):
        """Test converting explanation to text."""
        from empathy_os.socratic.explainer import (
            AudienceLevel,
            DetailLevel,
            Explanation,
        )

        explanation = Explanation(
            title="Code Review",
            summary="Automated code review workflow.",
            sections=[
                {"heading": "Benefits", "content": "Improves code quality."},
            ],
            audience=AudienceLevel.BUSINESS,
            detail_level=DetailLevel.BRIEF,
        )

        text = explanation.to_text()

        assert isinstance(text, str)
        assert "Automated code review" in text

    def test_explanation_to_markdown(self):
        """Test converting explanation to markdown."""
        from empathy_os.socratic.explainer import (
            AudienceLevel,
            DetailLevel,
            Explanation,
        )

        explanation = Explanation(
            title="Technical Explanation",
            summary="Technical explanation",
            sections=[
                {"heading": "Architecture", "content": "The system uses..."},
            ],
            audience=AudienceLevel.TECHNICAL,
            detail_level=DetailLevel.DETAILED,
        )

        markdown = explanation.to_markdown()

        assert isinstance(markdown, str)
        assert "#" in markdown  # Should have headers

    def test_explanation_to_html(self):
        """Test converting explanation to HTML."""
        from empathy_os.socratic.explainer import (
            AudienceLevel,
            DetailLevel,
            Explanation,
        )

        explanation = Explanation(
            title="Simple Guide",
            summary="Simple explanation",
            sections=[],
            audience=AudienceLevel.BEGINNER,
            detail_level=DetailLevel.STANDARD,
        )

        html = explanation.to_html()

        assert isinstance(html, str)
        assert "<" in html  # Should have HTML tags

    def test_explanation_to_dict(self):
        """Test converting explanation to dict."""
        from empathy_os.socratic.explainer import (
            AudienceLevel,
            DetailLevel,
            Explanation,
        )

        explanation = Explanation(
            title="Test Workflow",
            summary="Test",
            sections=[],
            audience=AudienceLevel.TECHNICAL,
            detail_level=DetailLevel.STANDARD,
        )

        data = explanation.to_dict()

        assert isinstance(data, dict)
        assert data["title"] == "Test Workflow"
        assert data["audience"] == "technical"


class TestWorkflowExplainer:
    """Tests for WorkflowExplainer class."""

    def test_create_explainer(self):
        """Test creating a workflow explainer."""
        from empathy_os.socratic.explainer import WorkflowExplainer

        explainer = WorkflowExplainer()
        assert explainer is not None

    def test_create_explainer_with_options(self):
        """Test creating explainer with options."""
        from empathy_os.socratic.explainer import (
            AudienceLevel,
            DetailLevel,
            WorkflowExplainer,
        )

        explainer = WorkflowExplainer(
            audience=AudienceLevel.BUSINESS,
            detail_level=DetailLevel.BRIEF,
        )

        assert explainer.audience == AudienceLevel.BUSINESS
        assert explainer.detail_level == DetailLevel.BRIEF

    def test_explain_workflow_for_technical(self, sample_workflow_blueprint):
        """Test explaining workflow for technical audience."""
        from empathy_os.socratic.explainer import AudienceLevel, WorkflowExplainer

        explainer = WorkflowExplainer(audience=AudienceLevel.TECHNICAL)

        explanation = explainer.explain_workflow(sample_workflow_blueprint)

        assert explanation is not None
        assert explanation.audience == AudienceLevel.TECHNICAL
        assert len(explanation.summary) > 0

    def test_explain_workflow_for_business(self, sample_workflow_blueprint):
        """Test explaining workflow for business audience."""
        from empathy_os.socratic.explainer import AudienceLevel, WorkflowExplainer

        explainer = WorkflowExplainer(audience=AudienceLevel.BUSINESS)

        explanation = explainer.explain_workflow(sample_workflow_blueprint)

        assert explanation is not None
        assert explanation.audience == AudienceLevel.BUSINESS

    def test_explain_workflow_for_beginner(self, sample_workflow_blueprint):
        """Test explaining workflow for beginner audience."""
        from empathy_os.socratic.explainer import AudienceLevel, WorkflowExplainer

        explainer = WorkflowExplainer(audience=AudienceLevel.BEGINNER)

        explanation = explainer.explain_workflow(sample_workflow_blueprint)

        assert explanation is not None
        assert explanation.audience == AudienceLevel.BEGINNER

    def test_explain_agent(self, sample_agent_spec):
        """Test explaining individual agent."""
        from empathy_os.socratic.explainer import WorkflowExplainer

        explainer = WorkflowExplainer()

        agent_explanation = explainer.explain_agent(sample_agent_spec)

        assert agent_explanation is not None
        assert len(agent_explanation.summary) > 0


class TestLLMExplanationGenerator:
    """Tests for LLMExplanationGenerator class."""

    def test_create_generator(self):
        """Test creating an LLM explanation generator."""
        from empathy_os.socratic.explainer import LLMExplanationGenerator

        generator = LLMExplanationGenerator()
        assert generator is not None

    def test_create_generator_with_api_key(self):
        """Test creating generator with API key."""
        from empathy_os.socratic.explainer import LLMExplanationGenerator

        generator = LLMExplanationGenerator(api_key="test-api-key")
        assert generator.api_key == "test-api-key"


class TestExplainWorkflowFunction:
    """Tests for the explain_workflow convenience function."""

    def test_explain_workflow_returns_string(self, sample_workflow_blueprint):
        """Test the explain_workflow function returns string."""
        from empathy_os.socratic.explainer import explain_workflow

        result = explain_workflow(sample_workflow_blueprint)

        # Module-level function returns string (formatted output)
        assert isinstance(result, str)
        assert len(result) > 0

    def test_explain_workflow_with_audience(self, sample_workflow_blueprint):
        """Test explain_workflow with audience parameter."""
        from empathy_os.socratic.explainer import AudienceLevel, explain_workflow

        result = explain_workflow(
            sample_workflow_blueprint,
            audience=AudienceLevel.BEGINNER,
        )

        assert isinstance(result, str)

    def test_explain_workflow_with_format(self, sample_workflow_blueprint):
        """Test explain_workflow with output format."""
        from empathy_os.socratic.explainer import (
            OutputFormat,
            explain_workflow,
        )

        result = explain_workflow(
            sample_workflow_blueprint,
            format=OutputFormat.MARKDOWN,
        )

        assert "#" in result  # Markdown headers


class TestExplanationContent:
    """Tests for explanation content quality."""

    def test_technical_includes_details(self, sample_workflow_blueprint):
        """Test technical explanation includes technical details."""
        from empathy_os.socratic.explainer import (
            AudienceLevel,
            DetailLevel,
            WorkflowExplainer,
        )

        explainer = WorkflowExplainer(
            audience=AudienceLevel.TECHNICAL,
            detail_level=DetailLevel.DETAILED,
        )

        explanation = explainer.explain_workflow(sample_workflow_blueprint)

        text = explanation.to_text()

        # Should have content
        assert len(text) > 0

    def test_business_explanation_works(self, sample_workflow_blueprint):
        """Test business explanation generates valid output."""
        from empathy_os.socratic.explainer import AudienceLevel, WorkflowExplainer

        explainer = WorkflowExplainer(audience=AudienceLevel.BUSINESS)

        explanation = explainer.explain_workflow(sample_workflow_blueprint)

        assert explanation is not None

    def test_beginner_explanation_works(self, sample_workflow_blueprint):
        """Test beginner explanation generates valid output."""
        from empathy_os.socratic.explainer import AudienceLevel, WorkflowExplainer

        explainer = WorkflowExplainer(audience=AudienceLevel.BEGINNER)

        explanation = explainer.explain_workflow(sample_workflow_blueprint)

        assert explanation is not None


class TestRoleDescriptions:
    """Tests for role description mappings."""

    def test_role_descriptions_exist(self):
        """Test role descriptions are configured."""
        from empathy_os.socratic.explainer import ROLE_DESCRIPTIONS

        assert len(ROLE_DESCRIPTIONS) > 0

    def test_role_descriptions_for_all_audiences(self):
        """Test role descriptions exist for all audience levels."""
        from empathy_os.socratic.explainer import ROLE_DESCRIPTIONS, AudienceLevel

        for audience in AudienceLevel:
            assert audience in ROLE_DESCRIPTIONS
