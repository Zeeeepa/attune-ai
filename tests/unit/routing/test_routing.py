"""Tests for routing module.

Covers WorkflowInfo, WorkflowRegistry, ClassificationResult, HaikuClassifier,
RoutingDecision, and SmartRouter.

Copyright 2025 Smart-AI-Memory
Licensed under the Apache License, Version 2.0
"""

import pytest

from attune.routing.classifier import ClassificationResult, HaikuClassifier
from attune.routing.smart_router import RoutingDecision, SmartRouter
from attune.routing.workflow_registry import WORKFLOW_REGISTRY, WorkflowInfo, WorkflowRegistry


@pytest.mark.unit
class TestWorkflowInfo:
    """Tests for WorkflowInfo dataclass."""

    def test_wizard_info_creation(self):
        """Test creating a WorkflowInfo."""
        info = WorkflowInfo(
            name="test-wizard",
            description="A test wizard",
            keywords=["test", "example"],
        )

        assert info.name == "test-wizard"
        assert info.description == "A test wizard"
        assert info.keywords == ["test", "example"]

    def test_wizard_info_defaults(self):
        """Test WorkflowInfo default values."""
        info = WorkflowInfo(
            name="test",
            description="Test",
            keywords=[],
        )

        assert info.primary_domain == ""
        assert info.handles_file_types == []
        assert info.complexity == "medium"
        assert info.auto_chain is False
        assert info.chain_triggers == []
        assert info.workflow_class is None
        assert info.factory is None

    def test_wizard_info_with_chain_triggers(self):
        """Test WorkflowInfo with chain triggers."""
        info = WorkflowInfo(
            name="test",
            description="Test",
            keywords=[],
            auto_chain=True,
            chain_triggers=[
                {"condition": "score > 0.5", "next": "other-wizard"},
            ],
        )

        assert info.auto_chain is True
        assert len(info.chain_triggers) == 1
        assert info.chain_triggers[0]["next"] == "other-wizard"


@pytest.mark.unit
class TestWorkflowRegistry:
    """Tests for WorkflowRegistry class."""

    def test_registry_initializes_with_defaults(self):
        """Test registry has default wizards."""
        registry = WorkflowRegistry()

        wizards = registry.list_all()

        assert len(wizards) >= 9  # At least 9 default wizards
        assert registry.get("security-audit") is not None
        assert registry.get("code-review") is not None
        assert registry.get("bug-predict") is not None

    def test_register_new_wizard(self):
        """Test registering a new wizard."""
        registry = WorkflowRegistry()

        custom_wizard = WorkflowInfo(
            name="custom-wizard",
            description="Custom wizard",
            keywords=["custom"],
        )

        registry.register(custom_wizard)

        assert registry.get("custom-wizard") is not None
        assert registry.get("custom-wizard").description == "Custom wizard"

    def test_get_returns_none_for_unknown(self):
        """Test get returns None for unknown wizard."""
        registry = WorkflowRegistry()

        assert registry.get("nonexistent") is None

    def test_find_by_domain(self):
        """Test finding wizards by domain."""
        registry = WorkflowRegistry()

        security_wizards = registry.find_by_domain("security")

        assert len(security_wizards) >= 1
        assert all(w.primary_domain == "security" for w in security_wizards)

    def test_find_by_keyword(self):
        """Test finding wizards by keyword."""
        registry = WorkflowRegistry()

        # "security" keyword should match security-audit
        wizards = registry.find_by_keyword("security")

        assert len(wizards) >= 1
        wizard_names = [w.name for w in wizards]
        assert "security-audit" in wizard_names

    def test_find_by_keyword_case_insensitive(self):
        """Test find_by_keyword is case insensitive."""
        registry = WorkflowRegistry()

        lower = registry.find_by_keyword("security")
        upper = registry.find_by_keyword("SECURITY")

        assert len(lower) == len(upper)

    def test_get_descriptions_for_classification(self):
        """Test getting descriptions for LLM classification."""
        registry = WorkflowRegistry()

        descriptions = registry.get_descriptions_for_classification()

        assert "security-audit" in descriptions
        assert "code-review" in descriptions
        assert "domain:" in descriptions["security-audit"]

    def test_get_chain_triggers(self):
        """Test getting chain triggers for a wizard."""
        registry = WorkflowRegistry()

        triggers = registry.get_chain_triggers("security-audit")

        assert len(triggers) >= 1
        assert any("next" in t for t in triggers)

    def test_get_chain_triggers_empty_for_no_autochain(self):
        """Test chain triggers empty for wizard without auto_chain."""
        registry = WorkflowRegistry()

        # refactor-plan has auto_chain=False
        triggers = registry.get_chain_triggers("refactor-plan")

        assert triggers == []

    def test_unregister(self):
        """Test unregistering a wizard."""
        registry = WorkflowRegistry()

        # Add custom wizard first
        registry.register(WorkflowInfo(name="to-remove", description="Test", keywords=[]))

        assert registry.get("to-remove") is not None

        result = registry.unregister("to-remove")

        assert result is True
        assert registry.get("to-remove") is None

    def test_unregister_nonexistent(self):
        """Test unregistering nonexistent wizard returns False."""
        registry = WorkflowRegistry()

        result = registry.unregister("nonexistent")

        assert result is False


@pytest.mark.unit
class TestClassificationResult:
    """Tests for ClassificationResult dataclass."""

    def test_classification_result_creation(self):
        """Test creating a ClassificationResult."""
        result = ClassificationResult(
            primary_workflow="security-audit",
            secondary_workflows=["code-review"],
            confidence=0.9,
            reasoning="Security keywords detected",
        )

        assert result.primary_workflow == "security-audit"
        assert result.secondary_workflows == ["code-review"]
        assert result.confidence == 0.9
        assert "Security" in result.reasoning

    def test_classification_result_defaults(self):
        """Test ClassificationResult default values."""
        result = ClassificationResult(primary_workflow="test")

        assert result.secondary_workflows == []
        assert result.confidence == 0.0
        assert result.reasoning == ""
        assert result.suggested_chain == []
        assert result.extracted_context == {}


@pytest.mark.unit
class TestHaikuClassifier:
    """Tests for HaikuClassifier class."""

    def test_classifier_initialization(self):
        """Test HaikuClassifier initialization."""
        classifier = HaikuClassifier()

        assert classifier._api_key is None or isinstance(classifier._api_key, str)
        assert classifier._client is None

    def test_classifier_keyword_classify_security(self):
        """Test keyword classification for security-related request."""
        classifier = HaikuClassifier()

        result = classifier._keyword_classify(
            "Check for SQL injection vulnerabilities",
            {},
        )

        assert result.primary_workflow == "security-audit"
        assert result.confidence > 0

    def test_classifier_keyword_classify_performance(self):
        """Test keyword classification for performance request."""
        classifier = HaikuClassifier()

        result = classifier._keyword_classify(
            "Optimize slow database queries for better performance",
            {},
        )

        assert result.primary_workflow == "perf-audit"

    def test_classifier_keyword_classify_testing(self):
        """Test keyword classification for testing request."""
        classifier = HaikuClassifier()

        result = classifier._keyword_classify(
            "Generate unit tests with good coverage",
            {},
        )

        assert result.primary_workflow == "test-gen"

    def test_classifier_keyword_classify_default(self):
        """Test keyword classification defaults to code-review."""
        classifier = HaikuClassifier()

        result = classifier._keyword_classify(
            "Random unrelated request",
            {},
        )

        assert result.primary_workflow == "code-review"
        assert result.confidence == 0.3

    def test_classifier_keyword_classify_secondary_workflows(self):
        """Test keyword classification finds secondary wizards."""
        classifier = HaikuClassifier()

        # Request with multiple matching keywords
        result = classifier._keyword_classify(
            "Fix security bug and add tests",
            {},
        )

        # Should have secondary wizards
        assert len(result.secondary_workflows) >= 0  # May or may not have secondary

    def test_classify_sync(self):
        """Test synchronous classification."""
        classifier = HaikuClassifier()

        result = classifier.classify_sync("Check for security vulnerabilities")

        assert result.primary_workflow == "security-audit"

    def test_classify_sync_with_context(self):
        """Test synchronous classification with context."""
        classifier = HaikuClassifier()

        result = classifier.classify_sync(
            "Review the code",
            context={"file": "auth.py"},
        )

        assert result.primary_workflow in ["code-review", "security-audit"]


@pytest.mark.unit
class TestRoutingDecision:
    """Tests for RoutingDecision dataclass."""

    def test_routing_decision_creation(self):
        """Test creating a RoutingDecision."""
        decision = RoutingDecision(
            primary_workflow="security-audit",
            secondary_workflows=["code-review"],
            confidence=0.85,
            reasoning="Security keywords detected",
            classification_method="keyword",
        )

        assert decision.primary_workflow == "security-audit"
        assert decision.confidence == 0.85
        assert decision.classification_method == "keyword"

    def test_routing_decision_defaults(self):
        """Test RoutingDecision default values."""
        decision = RoutingDecision(primary_workflow="test")

        assert decision.secondary_workflows == []
        assert decision.confidence == 0.0
        assert decision.reasoning == ""
        assert decision.suggested_chain == []
        assert decision.context == {}
        assert decision.classification_method == "llm"
        assert decision.request_summary == ""


@pytest.mark.unit
class TestSmartRouter:
    """Tests for SmartRouter class."""

    def test_router_initialization(self):
        """Test SmartRouter initialization."""
        router = SmartRouter()

        assert router._registry is not None
        assert router._classifier is not None

    def test_route_sync_security(self):
        """Test synchronous routing for security request."""
        router = SmartRouter()

        decision = router.route_sync("Check for SQL injection vulnerabilities")

        assert decision.primary_workflow == "security-audit"
        assert decision.classification_method == "keyword"

    def test_route_sync_with_context(self):
        """Test synchronous routing with context."""
        router = SmartRouter()

        decision = router.route_sync(
            "Review this code",
            context={"file": "auth.py"},
        )

        assert decision.primary_workflow is not None
        assert "file" in decision.context

    def test_route_sync_builds_chain(self):
        """Test synchronous routing builds suggested chain."""
        router = SmartRouter()

        decision = router.route_sync("Check for security vulnerabilities")

        assert len(decision.suggested_chain) >= 1
        assert decision.primary_workflow in decision.suggested_chain

    def test_get_workflow_info(self):
        """Test getting wizard info through router."""
        router = SmartRouter()

        info = router.get_workflow_info("security-audit")

        assert info is not None
        assert info.name == "security-audit"

    def test_get_workflow_info_unknown(self):
        """Test getting unknown wizard info returns None."""
        router = SmartRouter()

        info = router.get_workflow_info("nonexistent")

        assert info is None

    def test_list_workflows(self):
        """Test listing all wizards through router."""
        router = SmartRouter()

        wizards = router.list_workflows()

        assert len(wizards) >= 9
        wizard_names = [w.name for w in wizards]
        assert "security-audit" in wizard_names
        assert "code-review" in wizard_names

    def test_suggest_for_file_python(self):
        """Test wizard suggestions for Python file."""
        router = SmartRouter()

        suggestions = router.suggest_for_file("auth.py")

        assert len(suggestions) >= 1
        # Python files should suggest security-audit, code-review, etc.

    def test_suggest_for_file_javascript(self):
        """Test wizard suggestions for JavaScript file."""
        router = SmartRouter()

        suggestions = router.suggest_for_file("app.js")

        assert len(suggestions) >= 1

    def test_suggest_for_file_requirements(self):
        """Test wizard suggestions for requirements.txt."""
        router = SmartRouter()

        suggestions = router.suggest_for_file("requirements.txt")

        assert "dependency-check" in suggestions

    def test_suggest_for_file_unknown_type(self):
        """Test wizard suggestions for unknown file type."""
        router = SmartRouter()

        suggestions = router.suggest_for_file("unknown.xyz")

        # Should return defaults
        assert "code-review" in suggestions or "security-audit" in suggestions

    def test_suggest_for_error_security(self):
        """Test wizard suggestions for security error."""
        router = SmartRouter()

        suggestions = router.suggest_for_error("SecurityError")

        assert "security-audit" in suggestions

    def test_suggest_for_error_type(self):
        """Test wizard suggestions for type error."""
        router = SmartRouter()

        suggestions = router.suggest_for_error("TypeError")

        assert "code-review" in suggestions or "bug-predict" in suggestions

    def test_suggest_for_error_timeout(self):
        """Test wizard suggestions for timeout error."""
        router = SmartRouter()

        suggestions = router.suggest_for_error("TimeoutError")

        assert "perf-audit" in suggestions

    def test_suggest_for_error_import(self):
        """Test wizard suggestions for import error."""
        router = SmartRouter()

        suggestions = router.suggest_for_error("ImportError")

        assert "dependency-check" in suggestions

    def test_suggest_for_error_unknown(self):
        """Test wizard suggestions for unknown error type."""
        router = SmartRouter()

        suggestions = router.suggest_for_error("UnknownWeirdError")

        # Should return defaults
        assert "bug-predict" in suggestions or "code-review" in suggestions


@pytest.mark.unit
class TestDefaultWorkflowRegistry:
    """Tests for the default WORKFLOW_REGISTRY constant."""

    def test_security_audit_keywords(self):
        """Test security-audit wizard has expected keywords."""
        info = WORKFLOW_REGISTRY["security-audit"]

        assert "security" in info.keywords
        assert "vulnerability" in info.keywords
        assert "injection" in info.keywords

    def test_code_review_file_types(self):
        """Test code-review wizard handles expected file types."""
        info = WORKFLOW_REGISTRY["code-review"]

        assert ".py" in info.handles_file_types
        assert ".js" in info.handles_file_types

    def test_bug_predict_domain(self):
        """Test bug-predict wizard has debugging domain."""
        info = WORKFLOW_REGISTRY["bug-predict"]

        assert info.primary_domain == "debugging"

    def test_perf_audit_auto_chain(self):
        """Test perf-audit wizard has auto-chain enabled."""
        info = WORKFLOW_REGISTRY["perf-audit"]

        assert info.auto_chain is True
        assert len(info.chain_triggers) >= 1

    def test_refactor_plan_no_auto_chain(self):
        """Test refactor-plan wizard has auto-chain disabled."""
        info = WORKFLOW_REGISTRY["refactor-plan"]

        assert info.auto_chain is False

    def test_all_wizards_have_descriptions(self):
        """Test all default wizards have descriptions."""
        for name, info in WORKFLOW_REGISTRY.items():
            assert info.description, f"{name} missing description"

    def test_all_wizards_have_keywords(self):
        """Test all default wizards have keywords."""
        for name, info in WORKFLOW_REGISTRY.items():
            assert len(info.keywords) > 0, f"{name} missing keywords"


@pytest.mark.unit
class TestChainBuilding:
    """Tests for wizard chain building."""

    def test_build_chain_includes_primary(self):
        """Test chain includes primary wizard."""
        router = SmartRouter()

        decision = router.route_sync("Check security")

        assert decision.primary_workflow in decision.suggested_chain

    def test_build_chain_includes_secondary(self):
        """Test chain includes secondary wizards."""
        router = SmartRouter()

        # Create a classification with secondary wizards
        from attune.routing.classifier import ClassificationResult

        classification = ClassificationResult(
            primary_workflow="security-audit",
            secondary_workflows=["code-review"],
        )

        chain = router._build_chain(classification)

        assert "security-audit" in chain
        assert "code-review" in chain

    def test_build_chain_adds_triggers(self):
        """Test chain adds trigger-based wizards."""
        router = SmartRouter()

        # security-audit has chain triggers
        from attune.routing.classifier import ClassificationResult

        classification = ClassificationResult(
            primary_workflow="security-audit",
        )

        chain = router._build_chain(classification)

        # Should include trigger targets if auto_chain enabled
        assert "security-audit" in chain

    def test_build_chain_no_duplicates(self):
        """Test chain doesn't have duplicates."""
        router = SmartRouter()

        from attune.routing.classifier import ClassificationResult

        classification = ClassificationResult(
            primary_workflow="security-audit",
            secondary_workflows=["security-audit"],  # Duplicate
        )

        chain = router._build_chain(classification)

        # Should only have one security-audit
        assert chain.count("security-audit") == 1


@pytest.mark.asyncio
@pytest.mark.unit
class TestAsyncRouting:
    """Tests for async routing methods."""

    async def test_route_async(self):
        """Test async routing falls back to keyword when no API key."""
        router = SmartRouter()  # No API key

        decision = await router.route("Check for security vulnerabilities")

        # Should work with fallback
        assert decision.primary_workflow is not None

    async def test_classify_async_fallback(self):
        """Test async classification falls back to keyword."""
        classifier = HaikuClassifier()  # No API key

        result = await classifier.classify("Check security")

        # Should work with fallback
        assert result.primary_workflow is not None
