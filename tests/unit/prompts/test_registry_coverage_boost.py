"""Unit tests for XML prompt templates registry.

This test suite provides comprehensive coverage for the built-in prompt template
registry, ensuring all templates are properly configured and accessible.

Copyright 2025 Smart-AI-Memory
Licensed under Fair Source License 0.9
"""

import pytest

from empathy_os.prompts.registry import (
    BUG_ANALYSIS_RESPONSE,
    BUILTIN_TEMPLATES,
    CODE_REVIEW_RESPONSE,
    DEPENDENCY_CHECK_RESPONSE,
    DOC_GEN_RESPONSE,
    PERF_AUDIT_RESPONSE,
    REFACTOR_PLAN_RESPONSE,
    RELEASE_PREP_RESPONSE,
    RESEARCH_RESPONSE,
    SECURITY_AUDIT_RESPONSE,
    TEST_GEN_RESPONSE,
    get_template,
    list_templates,
    register_template,
)
from empathy_os.prompts.templates import XmlPromptTemplate


@pytest.mark.unit
class TestBuiltinTemplatesDict:
    """Test suite for BUILTIN_TEMPLATES dictionary."""

    def test_builtin_templates_is_dict(self):
        """Test that BUILTIN_TEMPLATES is a dictionary."""
        assert isinstance(BUILTIN_TEMPLATES, dict)

    def test_builtin_templates_has_expected_keys(self):
        """Test that BUILTIN_TEMPLATES contains all expected template names."""
        expected_templates = {
            "security-audit",
            "code-review",
            "research",
            "bug-analysis",
            "perf-audit",
            "refactor-plan",
            "test-gen",
            "doc-gen",
            "release-prep",
            "dependency-check",
        }

        assert set(BUILTIN_TEMPLATES.keys()) == expected_templates

    def test_all_builtin_templates_are_xml_prompt_template_instances(self):
        """Test that all template values are XmlPromptTemplate instances."""
        for name, template in BUILTIN_TEMPLATES.items():
            assert isinstance(
                template, XmlPromptTemplate
            ), f"{name} is not an XmlPromptTemplate"

    def test_all_builtin_templates_have_name(self):
        """Test that all templates have a name field."""
        for name, template in BUILTIN_TEMPLATES.items():
            assert hasattr(template, "name"), f"{name} missing name attribute"
            assert template.name == name

    def test_all_builtin_templates_have_schema_version(self):
        """Test that all templates have a schema_version."""
        for name, template in BUILTIN_TEMPLATES.items():
            assert hasattr(
                template, "schema_version"
            ), f"{name} missing schema_version"
            assert template.schema_version == "1.0"

    def test_all_builtin_templates_have_response_format(self):
        """Test that all templates have a response_format."""
        for name, template in BUILTIN_TEMPLATES.items():
            assert hasattr(
                template, "response_format"
            ), f"{name} missing response_format"
            assert isinstance(template.response_format, str)
            assert len(template.response_format) > 0


@pytest.mark.unit
class TestGetTemplate:
    """Test suite for get_template function."""

    def test_get_template_returns_template_for_valid_name(self):
        """Test that get_template returns template for valid name."""
        template = get_template("security-audit")

        assert template is not None
        assert isinstance(template, XmlPromptTemplate)
        assert template.name == "security-audit"

    def test_get_template_returns_none_for_invalid_name(self):
        """Test that get_template returns None for invalid name."""
        template = get_template("nonexistent-template")
        assert template is None

    def test_get_template_returns_none_for_empty_string(self):
        """Test that get_template returns None for empty string."""
        template = get_template("")
        assert template is None

    def test_get_template_for_all_builtin_templates(self):
        """Test that get_template works for all built-in templates."""
        template_names = [
            "security-audit",
            "code-review",
            "research",
            "bug-analysis",
            "perf-audit",
            "refactor-plan",
            "test-gen",
            "doc-gen",
            "release-prep",
            "dependency-check",
        ]

        for name in template_names:
            template = get_template(name)
            assert template is not None, f"get_template failed for {name}"
            assert template.name == name

    def test_get_template_returns_same_instance(self):
        """Test that get_template returns same instance on multiple calls."""
        template1 = get_template("code-review")
        template2 = get_template("code-review")

        assert template1 is template2


@pytest.mark.unit
class TestListTemplates:
    """Test suite for list_templates function."""

    def test_list_templates_returns_list(self):
        """Test that list_templates returns a list."""
        templates = list_templates()
        assert isinstance(templates, list)

    def test_list_templates_contains_all_builtin_templates(self):
        """Test that list_templates returns all built-in template names."""
        templates = list_templates()

        expected_templates = [
            "security-audit",
            "code-review",
            "research",
            "bug-analysis",
            "perf-audit",
            "refactor-plan",
            "test-gen",
            "doc-gen",
            "release-prep",
            "dependency-check",
        ]

        assert set(templates) == set(expected_templates)

    def test_list_templates_returns_strings(self):
        """Test that list_templates returns list of strings."""
        templates = list_templates()

        assert all(isinstance(t, str) for t in templates)

    def test_list_templates_count_matches_builtin_count(self):
        """Test that list_templates returns same count as BUILTIN_TEMPLATES."""
        templates = list_templates()
        assert len(templates) == len(BUILTIN_TEMPLATES)


@pytest.mark.unit
class TestRegisterTemplate:
    """Test suite for register_template function."""

    def test_register_template_adds_new_template(self):
        """Test that register_template adds a new template."""
        # Create a custom template
        custom_template = XmlPromptTemplate(
            name="custom-test",
            schema_version="1.0",
            response_format="<response>Custom format</response>",
        )

        # Get count before registration
        before_count = len(list_templates())

        # Register template
        register_template("custom-test", custom_template)

        # Verify it was added
        assert get_template("custom-test") is not None
        assert len(list_templates()) == before_count + 1

        # Clean up
        del BUILTIN_TEMPLATES["custom-test"]

    def test_register_template_overwrites_existing(self):
        """Test that register_template overwrites existing template."""
        # Get original
        original = get_template("security-audit")

        # Register replacement
        replacement = XmlPromptTemplate(
            name="security-audit-v2",
            schema_version="2.0",
            response_format="<response>New format</response>",
        )
        register_template("security-audit", replacement)

        # Verify it was replaced
        current = get_template("security-audit")
        assert current is replacement
        assert current.schema_version == "2.0"

        # Restore original
        BUILTIN_TEMPLATES["security-audit"] = original

    def test_register_template_accessible_via_get_template(self):
        """Test that registered template is accessible via get_template."""
        custom = XmlPromptTemplate(
            name="test-accessible",
            schema_version="1.0",
            response_format="<response>Test</response>",
        )

        register_template("test-accessible", custom)

        retrieved = get_template("test-accessible")
        assert retrieved is custom

        # Clean up
        del BUILTIN_TEMPLATES["test-accessible"]

    def test_register_template_appears_in_list_templates(self):
        """Test that registered template appears in list_templates output."""
        custom = XmlPromptTemplate(
            name="test-listed",
            schema_version="1.0",
            response_format="<response>Test</response>",
        )

        register_template("test-listed", custom)

        templates = list_templates()
        assert "test-listed" in templates

        # Clean up
        del BUILTIN_TEMPLATES["test-listed"]


@pytest.mark.unit
class TestResponseFormatConstants:
    """Test suite for response format string constants."""

    def test_security_audit_response_is_string(self):
        """Test that SECURITY_AUDIT_RESPONSE is a non-empty string."""
        assert isinstance(SECURITY_AUDIT_RESPONSE, str)
        assert len(SECURITY_AUDIT_RESPONSE) > 0

    def test_code_review_response_is_string(self):
        """Test that CODE_REVIEW_RESPONSE is a non-empty string."""
        assert isinstance(CODE_REVIEW_RESPONSE, str)
        assert len(CODE_REVIEW_RESPONSE) > 0

    def test_research_response_is_string(self):
        """Test that RESEARCH_RESPONSE is a non-empty string."""
        assert isinstance(RESEARCH_RESPONSE, str)
        assert len(RESEARCH_RESPONSE) > 0

    def test_bug_analysis_response_is_string(self):
        """Test that BUG_ANALYSIS_RESPONSE is a non-empty string."""
        assert isinstance(BUG_ANALYSIS_RESPONSE, str)
        assert len(BUG_ANALYSIS_RESPONSE) > 0

    def test_perf_audit_response_is_string(self):
        """Test that PERF_AUDIT_RESPONSE is a non-empty string."""
        assert isinstance(PERF_AUDIT_RESPONSE, str)
        assert len(PERF_AUDIT_RESPONSE) > 0

    def test_refactor_plan_response_is_string(self):
        """Test that REFACTOR_PLAN_RESPONSE is a non-empty string."""
        assert isinstance(REFACTOR_PLAN_RESPONSE, str)
        assert len(REFACTOR_PLAN_RESPONSE) > 0

    def test_test_gen_response_is_string(self):
        """Test that TEST_GEN_RESPONSE is a non-empty string."""
        assert isinstance(TEST_GEN_RESPONSE, str)
        assert len(TEST_GEN_RESPONSE) > 0

    def test_doc_gen_response_is_string(self):
        """Test that DOC_GEN_RESPONSE is a non-empty string."""
        assert isinstance(DOC_GEN_RESPONSE, str)
        assert len(DOC_GEN_RESPONSE) > 0

    def test_release_prep_response_is_string(self):
        """Test that RELEASE_PREP_RESPONSE is a non-empty string."""
        assert isinstance(RELEASE_PREP_RESPONSE, str)
        assert len(RELEASE_PREP_RESPONSE) > 0

    def test_dependency_check_response_is_string(self):
        """Test that DEPENDENCY_CHECK_RESPONSE is a non-empty string."""
        assert isinstance(DEPENDENCY_CHECK_RESPONSE, str)
        assert len(DEPENDENCY_CHECK_RESPONSE) > 0


@pytest.mark.unit
class TestTemplateIntegrity:
    """Test suite for verifying template integrity and structure."""

    def test_security_audit_template_uses_correct_response_format(self):
        """Test that security-audit template uses SECURITY_AUDIT_RESPONSE."""
        template = get_template("security-audit")
        assert template.response_format == SECURITY_AUDIT_RESPONSE

    def test_code_review_template_uses_correct_response_format(self):
        """Test that code-review template uses CODE_REVIEW_RESPONSE."""
        template = get_template("code-review")
        assert template.response_format == CODE_REVIEW_RESPONSE

    def test_research_template_uses_correct_response_format(self):
        """Test that research template uses RESEARCH_RESPONSE."""
        template = get_template("research")
        assert template.response_format == RESEARCH_RESPONSE

    def test_bug_analysis_template_uses_correct_response_format(self):
        """Test that bug-analysis template uses BUG_ANALYSIS_RESPONSE."""
        template = get_template("bug-analysis")
        assert template.response_format == BUG_ANALYSIS_RESPONSE

    def test_perf_audit_template_uses_correct_response_format(self):
        """Test that perf-audit template uses PERF_AUDIT_RESPONSE."""
        template = get_template("perf-audit")
        assert template.response_format == PERF_AUDIT_RESPONSE

    def test_refactor_plan_template_uses_correct_response_format(self):
        """Test that refactor-plan template uses REFACTOR_PLAN_RESPONSE."""
        template = get_template("refactor-plan")
        assert template.response_format == REFACTOR_PLAN_RESPONSE

    def test_test_gen_template_uses_correct_response_format(self):
        """Test that test-gen template uses TEST_GEN_RESPONSE."""
        template = get_template("test-gen")
        assert template.response_format == TEST_GEN_RESPONSE

    def test_doc_gen_template_uses_correct_response_format(self):
        """Test that doc-gen template uses DOC_GEN_RESPONSE."""
        template = get_template("doc-gen")
        assert template.response_format == DOC_GEN_RESPONSE

    def test_release_prep_template_uses_correct_response_format(self):
        """Test that release-prep template uses RELEASE_PREP_RESPONSE."""
        template = get_template("release-prep")
        assert template.response_format == RELEASE_PREP_RESPONSE

    def test_dependency_check_template_uses_correct_response_format(self):
        """Test that dependency-check template uses DEPENDENCY_CHECK_RESPONSE."""
        template = get_template("dependency-check")
        assert template.response_format == DEPENDENCY_CHECK_RESPONSE


@pytest.mark.unit
class TestResponseFormatStructure:
    """Test suite for validating XML structure in response formats."""

    def test_security_audit_response_contains_xml_tags(self):
        """Test that SECURITY_AUDIT_RESPONSE contains expected XML tags."""
        assert "<response>" in SECURITY_AUDIT_RESPONSE
        assert "<summary>" in SECURITY_AUDIT_RESPONSE
        assert "<findings>" in SECURITY_AUDIT_RESPONSE
        assert "<remediation-checklist>" in SECURITY_AUDIT_RESPONSE

    def test_code_review_response_contains_verdict(self):
        """Test that CODE_REVIEW_RESPONSE contains verdict tag."""
        assert "<verdict>" in CODE_REVIEW_RESPONSE

    def test_perf_audit_response_contains_performance_score(self):
        """Test that PERF_AUDIT_RESPONSE contains performance-score tag."""
        assert "<performance-score>" in PERF_AUDIT_RESPONSE

    def test_release_prep_response_contains_checklist(self):
        """Test that RELEASE_PREP_RESPONSE contains checklist tag."""
        assert "<checklist>" in RELEASE_PREP_RESPONSE
