"""Tests for the Socratic engine module.

Copyright 2026 Smart-AI-Memory
Licensed under the Apache License, Version 2.0
"""


class TestSocraticWorkflowBuilder:
    """Tests for SocraticWorkflowBuilder class."""

    def test_create_builder(self):
        """Test creating a workflow builder."""
        from attune.socratic.engine import SocraticWorkflowBuilder

        builder = SocraticWorkflowBuilder()
        assert builder is not None

    def test_start_session(self):
        """Test starting a new session."""
        from attune.socratic.engine import SocraticWorkflowBuilder
        from attune.socratic.session import SessionState

        builder = SocraticWorkflowBuilder()
        session = builder.start_session()

        assert session is not None
        assert session.state == SessionState.AWAITING_GOAL

    def test_start_session_with_goal(self, sample_goal):
        """Test starting a session with initial goal."""
        from attune.socratic.engine import SocraticWorkflowBuilder
        from attune.socratic.session import SessionState

        builder = SocraticWorkflowBuilder()
        session = builder.start_session(sample_goal)

        assert session.goal == sample_goal
        assert session.state in [SessionState.ANALYZING_GOAL, SessionState.AWAITING_ANSWERS]

    def test_set_goal(self):
        """Test setting goal on existing session."""
        from attune.socratic.engine import SocraticWorkflowBuilder

        builder = SocraticWorkflowBuilder()
        session = builder.start_session()

        session = builder.set_goal(session, "I want to automate testing")

        assert session.goal == "I want to automate testing"
        # After set_goal, goal_analysis should be populated
        assert session.goal_analysis is not None
        assert session.goal_analysis.domain is not None

    def test_get_next_questions(self, sample_session):
        """Test getting next questions."""
        from attune.socratic.engine import SocraticWorkflowBuilder
        from attune.socratic.session import SessionState

        builder = SocraticWorkflowBuilder()
        sample_session.state = SessionState.AWAITING_ANSWERS

        form = builder.get_next_questions(sample_session)

        assert form is not None
        assert len(form.fields) > 0

    def test_submit_answers(self, sample_session, sample_answers):
        """Test submitting answers."""
        from attune.socratic.engine import SocraticWorkflowBuilder

        builder = SocraticWorkflowBuilder()
        session = builder.submit_answers(sample_session, sample_answers)

        # After submit_answers, requirements should be updated
        assert session.requirements is not None

    def test_is_ready_to_generate(self, sample_session):
        """Test checking if ready to generate."""
        from attune.socratic.engine import SocraticWorkflowBuilder
        from attune.socratic.session import SessionState

        builder = SocraticWorkflowBuilder()

        # Not ready in AWAITING_ANSWERS state
        sample_session.state = SessionState.AWAITING_ANSWERS
        assert not builder.is_ready_to_generate(sample_session)

        # Ready in READY_TO_GENERATE state
        sample_session.state = SessionState.READY_TO_GENERATE
        assert builder.is_ready_to_generate(sample_session)

    def test_generate_workflow(self):
        """Test generating a workflow."""
        from attune.socratic.engine import SocraticWorkflowBuilder
        from attune.socratic.session import SessionState

        builder = SocraticWorkflowBuilder()

        # Create a session ready for generation
        session = builder.start_session("Automate code reviews for Python")
        session = builder.submit_answers(
            session,
            {
                "languages": ["python"],
                "quality_focus": ["security", "maintainability"],
            },
        )
        session.state = SessionState.READY_TO_GENERATE

        workflow = builder.generate_workflow(session)

        assert workflow is not None
        assert workflow.blueprint is not None
        assert len(workflow.blueprint.agents) > 0

    def test_get_session_summary(self, sample_session):
        """Test getting session summary."""
        from attune.socratic.engine import SocraticWorkflowBuilder

        builder = SocraticWorkflowBuilder()
        summary = builder.get_session_summary(sample_session)

        assert summary is not None
        assert "session_id" in summary
        assert "state" in summary


class TestDetectDomainFunction:
    """Tests for the detect_domain module-level function."""

    def test_detect_code_review_domain(self):
        """Test domain detection for code review."""
        from attune.socratic.engine import detect_domain

        domain, confidence = detect_domain("I want to review code quality")

        assert domain == "code_review"
        assert confidence > 0

    def test_detect_security_domain(self):
        """Test domain detection for security."""
        from attune.socratic.engine import detect_domain

        domain, confidence = detect_domain("Scan for security vulnerabilities")

        assert domain == "security"
        assert confidence > 0

    def test_detect_testing_domain(self):
        """Test domain detection for testing."""
        from attune.socratic.engine import detect_domain

        domain, confidence = detect_domain("Generate unit tests for coverage")

        assert domain == "testing"
        assert confidence > 0

    def test_detect_documentation_domain(self):
        """Test domain detection for documentation."""
        from attune.socratic.engine import detect_domain

        domain, confidence = detect_domain("Write API documentation")

        assert domain == "documentation"
        assert confidence > 0

    def test_detect_performance_domain(self):
        """Test domain detection for performance."""
        from attune.socratic.engine import detect_domain

        domain, confidence = detect_domain("Optimize for performance")

        assert domain == "performance"
        assert confidence > 0

    def test_detect_refactoring_domain(self):
        """Test domain detection for refactoring."""
        from attune.socratic.engine import detect_domain

        domain, confidence = detect_domain("Refactor this module")

        assert domain == "refactoring"
        assert confidence > 0

    def test_returns_general_for_unknown(self):
        """Test that unknown goals return general domain."""
        from attune.socratic.engine import detect_domain

        domain, confidence = detect_domain("Do something vague")

        assert domain == "general"


class TestQuestionGeneration:
    """Tests for question generation functions."""

    def test_generate_initial_questions(self):
        """Test generating initial questions."""
        from attune.socratic.engine import SocraticWorkflowBuilder

        builder = SocraticWorkflowBuilder()
        session = builder.start_session("Code review automation")

        # get_next_questions handles initial question generation internally
        form = builder.get_next_questions(session)

        assert form is not None
        assert form.round_number == 1

    def test_get_initial_form(self):
        """Test getting the initial form template."""
        from attune.socratic.engine import SocraticWorkflowBuilder

        builder = SocraticWorkflowBuilder()
        form = builder.get_initial_form()

        assert form is not None
        assert len(form.fields) > 0


class TestDomainPatterns:
    """Tests for domain pattern configuration."""

    def test_domain_patterns_exist(self):
        """Test that domain patterns are configured."""
        from attune.socratic.engine import DOMAIN_PATTERNS

        assert len(DOMAIN_PATTERNS) > 0

    def test_domain_pattern_has_required_fields(self):
        """Test domain patterns have required fields."""
        from attune.socratic.engine import DOMAIN_PATTERNS

        for pattern in DOMAIN_PATTERNS:
            assert hasattr(pattern, "domain")
            assert hasattr(pattern, "keywords")
            assert hasattr(pattern, "weight")


class TestSessionWorkflow:
    """Integration tests for the full session workflow."""

    def test_full_workflow_happy_path(self):
        """Test complete session workflow from start to generation."""
        from attune.socratic.engine import SocraticWorkflowBuilder
        from attune.socratic.session import SessionState

        builder = SocraticWorkflowBuilder()

        # 1. Start session with goal
        session = builder.start_session("Automate security code review for Python")

        # 2. Get initial questions
        form = builder.get_next_questions(session)
        assert form is not None

        # 3. Submit answers
        session = builder.submit_answers(
            session,
            {
                "languages": ["python"],
                "quality_focus": ["security"],
            },
        )

        # 4. Force ready state for test
        session.state = SessionState.READY_TO_GENERATE

        # 5. Generate workflow
        workflow = builder.generate_workflow(session)

        assert workflow is not None
        assert workflow.blueprint is not None
        assert len(workflow.blueprint.agents) > 0
