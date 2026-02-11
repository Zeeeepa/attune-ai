"""Tests for core pattern models.

Copyright 2025 Smart AI Memory, LLC
Licensed under the Apache License, Version 2.0
"""

import pytest
from pydantic import ValidationError

from patterns.core import BasePattern, CodeGeneratorMixin, PatternCategory


class TestPatternCategory:
    """Test PatternCategory enum."""

    def test_all_categories_defined(self):
        """All expected categories should be defined."""
        expected = {"structural", "input", "validation", "behavior", "empathy"}
        actual = {cat.value for cat in PatternCategory}
        assert actual == expected

    def test_category_string_values(self):
        """Categories should have correct string values."""
        assert PatternCategory.STRUCTURAL.value == "structural"
        assert PatternCategory.INPUT.value == "input"
        assert PatternCategory.VALIDATION.value == "validation"
        assert PatternCategory.BEHAVIOR.value == "behavior"
        assert PatternCategory.EMPATHY.value == "empathy"


class TestBasePattern:
    """Test BasePattern model."""

    @pytest.fixture
    def valid_pattern_data(self):
        """Valid pattern data for testing."""
        return {
            "id": "test_pattern",
            "name": "Test Pattern",
            "category": "structural",
            "description": "A test pattern",
            "frequency": 10,
            "reusability_score": 0.85,
            "examples": ["wizard1", "wizard2"],
        }

    def test_create_pattern_with_valid_data(self, valid_pattern_data):
        """Should create pattern with valid data."""
        pattern = BasePattern(**valid_pattern_data)

        assert pattern.id == "test_pattern"
        assert pattern.name == "Test Pattern"
        assert pattern.category == PatternCategory.STRUCTURAL
        assert pattern.description == "A test pattern"
        assert pattern.frequency == 10
        assert pattern.reusability_score == 0.85
        assert pattern.examples == ["wizard1", "wizard2"]

    def test_pattern_category_enum_conversion(self, valid_pattern_data):
        """Category should be converted to string value due to use_enum_values."""
        pattern = BasePattern(**valid_pattern_data)
        # Pydantic's use_enum_values=True converts enum to string
        assert pattern.category == "structural"
        # But it still validates against PatternCategory enum
        assert pattern.category == PatternCategory.STRUCTURAL.value

    def test_pattern_missing_required_fields(self):
        """Should raise ValidationError if required fields missing."""
        with pytest.raises(ValidationError) as exc:
            BasePattern(id="test", name="Test")

        errors = exc.value.errors()
        missing_fields = {err["loc"][0] for err in errors}
        assert "category" in missing_fields
        assert "description" in missing_fields
        assert "frequency" in missing_fields
        assert "reusability_score" in missing_fields

    def test_pattern_invalid_category(self, valid_pattern_data):
        """Should raise ValidationError for invalid category."""
        valid_pattern_data["category"] = "invalid_category"

        with pytest.raises(ValidationError) as exc:
            BasePattern(**valid_pattern_data)

        assert "category" in str(exc.value)

    def test_pattern_frequency_negative(self, valid_pattern_data):
        """Should raise ValidationError for negative frequency."""
        valid_pattern_data["frequency"] = -1

        with pytest.raises(ValidationError):
            BasePattern(**valid_pattern_data)

    def test_pattern_reusability_out_of_range(self, valid_pattern_data):
        """Should raise ValidationError for reusability outside [0.0, 1.0]."""
        # Test > 1.0
        valid_pattern_data["reusability_score"] = 1.5
        with pytest.raises(ValidationError):
            BasePattern(**valid_pattern_data)

        # Test < 0.0
        valid_pattern_data["reusability_score"] = -0.1
        with pytest.raises(ValidationError):
            BasePattern(**valid_pattern_data)

    def test_pattern_examples_default_empty_list(self, valid_pattern_data):
        """Examples should default to empty list if not provided."""
        del valid_pattern_data["examples"]
        pattern = BasePattern(**valid_pattern_data)
        assert pattern.examples == []

    def test_pattern_to_dict(self, valid_pattern_data):
        """to_dict() should return dictionary representation."""
        pattern = BasePattern(**valid_pattern_data)
        result = pattern.to_dict()

        assert isinstance(result, dict)
        assert result["id"] == "test_pattern"
        assert result["name"] == "Test Pattern"
        assert result["category"] == "structural"  # Enum value

    def test_pattern_from_dict(self, valid_pattern_data):
        """from_dict() should create pattern from dictionary."""
        pattern = BasePattern.from_dict(valid_pattern_data)

        assert pattern.id == "test_pattern"
        assert pattern.name == "Test Pattern"
        assert pattern.category == PatternCategory.STRUCTURAL


class TestCodeGeneratorMixin:
    """Test CodeGeneratorMixin."""

    def test_generate_code_not_implemented(self):
        """generate_code() should raise NotImplementedError by default."""

        class TestPattern(CodeGeneratorMixin):
            pass

        pattern = TestPattern()

        with pytest.raises(NotImplementedError) as exc:
            pattern.generate_code()

        assert "does not implement code generation" in str(exc.value)
