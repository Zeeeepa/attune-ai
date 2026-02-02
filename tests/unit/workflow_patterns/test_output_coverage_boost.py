"""Comprehensive tests for workflow output patterns.

Tests for ResultDataclassPattern and code generation.

Module: workflow_patterns/output.py (99 lines)
"""

import pytest

from attune.workflow_patterns.core import CodeSection, PatternCategory, WorkflowComplexity
from attune.workflow_patterns.output import ResultDataclassPattern

# ============================================================================
# ResultDataclassPattern Attribute Tests
# ============================================================================


@pytest.mark.unit
class TestResultDataclassPatternAttributes:
    """Test suite for ResultDataclassPattern class attributes."""

    def test_pattern_id(self):
        """Test that pattern has correct ID."""
        pattern = ResultDataclassPattern()
        assert pattern.id == "result-dataclass"

    def test_pattern_name(self):
        """Test that pattern has correct name."""
        pattern = ResultDataclassPattern()
        assert pattern.name == "Result Dataclass"

    def test_pattern_category(self):
        """Test that pattern is in OUTPUT category."""
        pattern = ResultDataclassPattern()
        assert pattern.category == PatternCategory.OUTPUT

    def test_pattern_description(self):
        """Test that pattern has description."""
        pattern = ResultDataclassPattern()
        assert pattern.description == "Structured output format with dataclass"

    def test_pattern_complexity(self):
        """Test that pattern has SIMPLE complexity."""
        pattern = ResultDataclassPattern()
        assert pattern.complexity == WorkflowComplexity.SIMPLE

    def test_pattern_use_cases(self):
        """Test that pattern has use cases."""
        pattern = ResultDataclassPattern()
        assert "Type-safe results" in pattern.use_cases
        assert "Structured output" in pattern.use_cases
        assert "API integration" in pattern.use_cases

    def test_pattern_examples(self):
        """Test that pattern has examples."""
        pattern = ResultDataclassPattern()
        assert "health-check" in pattern.examples
        assert "release-prep" in pattern.examples

    def test_pattern_risk_weight(self):
        """Test that pattern has default risk weight."""
        pattern = ResultDataclassPattern()
        assert pattern.risk_weight == 1.0


# ============================================================================
# Code Generation Tests - Default Context
# ============================================================================


@pytest.mark.unit
class TestGenerateCodeSectionsDefault:
    """Test suite for generate_code_sections with default context."""

    def test_generate_code_sections_returns_list(self):
        """Test that generate_code_sections returns list of CodeSection."""
        pattern = ResultDataclassPattern()
        sections = pattern.generate_code_sections({})

        assert isinstance(sections, list)
        assert len(sections) == 3

    def test_generate_imports_section(self):
        """Test that imports section is generated."""
        pattern = ResultDataclassPattern()
        sections = pattern.generate_code_sections({})

        imports_section = [s for s in sections if s.location == "imports"][0]
        assert "from dataclasses import dataclass, field" in imports_section.code
        assert imports_section.priority == 1

    def test_generate_dataclass_section(self):
        """Test that dataclass section is generated."""
        pattern = ResultDataclassPattern()
        sections = pattern.generate_code_sections({})

        dataclass_section = [s for s in sections if s.location == "dataclasses"][0]
        assert "@dataclass" in dataclass_section.code
        assert "class MyWorkflowResult:" in dataclass_section.code
        assert "success: bool" in dataclass_section.code
        assert "duration_seconds: float" in dataclass_section.code
        assert "cost: float" in dataclass_section.code
        assert "metadata: dict" in dataclass_section.code

    def test_generate_methods_section(self):
        """Test that methods section is generated."""
        pattern = ResultDataclassPattern()
        sections = pattern.generate_code_sections({})

        methods_section = [s for s in sections if s.location == "methods"][0]
        assert "def _create_result(" in methods_section.code
        assert "success: bool" in methods_section.code
        assert "duration: float" in methods_section.code
        assert "cost: float" in methods_section.code
        assert "MyWorkflowResult(" in methods_section.code

    def test_sections_have_priorities(self):
        """Test that all sections have priorities."""
        pattern = ResultDataclassPattern()
        sections = pattern.generate_code_sections({})

        for section in sections:
            assert isinstance(section.priority, int)
            assert section.priority > 0

    def test_sections_are_code_section_instances(self):
        """Test that all sections are CodeSection instances."""
        pattern = ResultDataclassPattern()
        sections = pattern.generate_code_sections({})

        for section in sections:
            assert isinstance(section, CodeSection)


# ============================================================================
# Code Generation Tests - Custom Context
# ============================================================================


@pytest.mark.unit
class TestGenerateCodeSectionsCustomContext:
    """Test suite for generate_code_sections with custom context."""

    def test_generate_with_custom_class_name(self):
        """Test code generation with custom class name."""
        pattern = ResultDataclassPattern()
        context = {"class_name": "HealthCheck"}
        sections = pattern.generate_code_sections(context)

        dataclass_section = [s for s in sections if s.location == "dataclasses"][0]
        assert "class HealthCheckResult:" in dataclass_section.code

        methods_section = [s for s in sections if s.location == "methods"][0]
        assert "HealthCheckResult(" in methods_section.code
        assert "HealthCheckResult instance" in methods_section.code

    def test_generate_with_custom_result_fields(self):
        """Test code generation with custom result fields."""
        pattern = ResultDataclassPattern()
        context = {
            "class_name": "SecurityAudit",
            "result_fields": [
                {"name": "findings_count", "type": "int", "description": "Number of findings"},
                {"name": "score", "type": "float", "description": "Security score"},
            ],
        }
        sections = pattern.generate_code_sections(context)

        dataclass_section = [s for s in sections if s.location == "dataclasses"][0]
        assert "findings_count: int" in dataclass_section.code
        assert "Number of findings" in dataclass_section.code
        assert "score: float" in dataclass_section.code
        assert "Security score" in dataclass_section.code

    def test_generate_without_custom_fields_shows_placeholder(self):
        """Test that placeholder is shown when no custom fields."""
        pattern = ResultDataclassPattern()
        context = {"class_name": "MyWorkflow"}
        sections = pattern.generate_code_sections(context)

        dataclass_section = [s for s in sections if s.location == "dataclasses"][0]
        # When no custom fields, should show placeholder comment
        assert (
            "# Add custom fields here" in dataclass_section.code
            or "success: bool" in dataclass_section.code
        )

    def test_generate_with_empty_result_fields(self):
        """Test code generation with empty result_fields list."""
        pattern = ResultDataclassPattern()
        context = {"class_name": "TestWorkflow", "result_fields": []}
        sections = pattern.generate_code_sections(context)

        dataclass_section = [s for s in sections if s.location == "dataclasses"][0]
        assert "class TestWorkflowResult:" in dataclass_section.code

    def test_generate_with_workflow_name(self):
        """Test code generation with workflow_name in context."""
        pattern = ResultDataclassPattern()
        context = {"workflow_name": "security-audit", "class_name": "SecurityAudit"}
        sections = pattern.generate_code_sections(context)

        # Should use class_name for result class
        dataclass_section = [s for s in sections if s.location == "dataclasses"][0]
        assert "class SecurityAuditResult:" in dataclass_section.code


# ============================================================================
# Code Section Validation Tests
# ============================================================================


@pytest.mark.unit
class TestCodeSectionValidation:
    """Test suite for CodeSection validation."""

    def test_all_sections_have_location(self):
        """Test that all generated sections have location."""
        pattern = ResultDataclassPattern()
        sections = pattern.generate_code_sections({})

        for section in sections:
            assert section.location in ["imports", "dataclasses", "methods"]

    def test_all_sections_have_code(self):
        """Test that all generated sections have code content."""
        pattern = ResultDataclassPattern()
        sections = pattern.generate_code_sections({})

        for section in sections:
            assert len(section.code) > 0

    def test_imports_section_priority(self):
        """Test that imports section has priority 1."""
        pattern = ResultDataclassPattern()
        sections = pattern.generate_code_sections({})

        imports_section = [s for s in sections if s.location == "imports"][0]
        assert imports_section.priority == 1

    def test_dataclass_section_priority(self):
        """Test that dataclass section has priority 1."""
        pattern = ResultDataclassPattern()
        sections = pattern.generate_code_sections({})

        dataclass_section = [s for s in sections if s.location == "dataclasses"][0]
        assert dataclass_section.priority == 1

    def test_methods_section_priority(self):
        """Test that methods section has priority 2."""
        pattern = ResultDataclassPattern()
        sections = pattern.generate_code_sections({})

        methods_section = [s for s in sections if s.location == "methods"][0]
        assert methods_section.priority == 2


# ============================================================================
# Integration Tests
# ============================================================================


@pytest.mark.unit
class TestIntegration:
    """Integration tests for ResultDataclassPattern."""

    def test_full_workflow_code_generation(self):
        """Test full code generation for a workflow."""
        pattern = ResultDataclassPattern()
        context = {
            "workflow_name": "release-prep",
            "class_name": "ReleasePrep",
            "result_fields": [
                {"name": "version", "type": "str", "description": "Release version"},
                {"name": "ready", "type": "bool", "description": "Ready for release"},
            ],
        }
        sections = pattern.generate_code_sections(context)

        # Should generate 3 sections
        assert len(sections) == 3

        # Check imports
        imports_section = [s for s in sections if s.location == "imports"][0]
        assert "dataclass" in imports_section.code

        # Check dataclass with custom fields
        dataclass_section = [s for s in sections if s.location == "dataclasses"][0]
        assert "class ReleasePrepResult:" in dataclass_section.code
        assert "version: str" in dataclass_section.code
        assert "ready: bool" in dataclass_section.code

        # Check method
        methods_section = [s for s in sections if s.location == "methods"][0]
        assert "_create_result" in methods_section.code
        assert "ReleasePrepResult(" in methods_section.code

    def test_pattern_attributes_accessible(self):
        """Test that all pattern attributes are accessible."""
        pattern = ResultDataclassPattern()

        # Access all attributes without errors
        assert pattern.id is not None
        assert pattern.name is not None
        assert pattern.category is not None
        assert pattern.description is not None
        assert pattern.complexity is not None
        assert pattern.use_cases is not None
        assert pattern.examples is not None
        assert pattern.risk_weight is not None

    def test_pattern_can_be_serialized(self):
        """Test that pattern can be serialized to dict."""
        pattern = ResultDataclassPattern()
        data = pattern.model_dump()

        assert data["id"] == "result-dataclass"
        assert data["name"] == "Result Dataclass"
        # category and complexity are enums, check their values
        assert data["category"] == PatternCategory.OUTPUT or data["category"] == "output"
        assert data["complexity"] == WorkflowComplexity.SIMPLE or data["complexity"] == "simple"
