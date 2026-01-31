"""Tests for XML prompt configuration.

Module: prompts/config.py (77 lines)
"""

import pytest

from empathy_os.prompts.config import XmlPromptConfig

# ============================================================================
# XmlPromptConfig Creation Tests
# ============================================================================


@pytest.mark.unit
class TestXmlPromptConfigCreation:
    """Test suite for XmlPromptConfig creation."""

    def test_create_default_config(self):
        """Test creating XmlPromptConfig with defaults."""
        # When
        config = XmlPromptConfig()

        # Then
        assert config.enabled is False
        assert config.schema_version == "1.0"
        assert config.enforce_response_xml is False
        assert config.fallback_on_parse_error is True
        assert config.template_name is None
        assert config.custom_template is None
        assert config.extra == {}

    def test_create_with_custom_values(self):
        """Test creating XmlPromptConfig with custom values."""
        # When
        config = XmlPromptConfig(
            enabled=True,
            schema_version="2.0",
            enforce_response_xml=True,
            fallback_on_parse_error=False,
            template_name="test_template",
            custom_template="<xml>test</xml>",
            extra={"key": "value"}
        )

        # Then
        assert config.enabled is True
        assert config.schema_version == "2.0"
        assert config.enforce_response_xml is True
        assert config.fallback_on_parse_error is False
        assert config.template_name == "test_template"
        assert config.custom_template == "<xml>test</xml>"
        assert config.extra == {"key": "value"}


# ============================================================================
# merge_with Tests
# ============================================================================


@pytest.mark.unit
class TestMergeWith:
    """Test suite for merge_with method."""

    def test_merge_overwrites_enabled(self):
        """Test that merge_with overwrites enabled when other is True."""
        # Given
        base = XmlPromptConfig(enabled=False)
        other = XmlPromptConfig(enabled=True)

        # When
        merged = base.merge_with(other)

        # Then
        assert merged.enabled is True

    def test_merge_preserves_base_when_other_false(self):
        """Test that merge preserves base enabled when other is False."""
        # Given
        base = XmlPromptConfig(enabled=True)
        other = XmlPromptConfig(enabled=False)

        # When
        merged = base.merge_with(other)

        # Then
        assert merged.enabled is True

    def test_merge_combines_extra_dicts(self):
        """Test that merge combines extra dictionaries."""
        # Given
        base = XmlPromptConfig(extra={"a": 1, "b": 2})
        other = XmlPromptConfig(extra={"b": 3, "c": 4})

        # When
        merged = base.merge_with(other)

        # Then
        assert merged.extra == {"a": 1, "b": 3, "c": 4}  # other takes precedence

    def test_merge_template_name(self):
        """Test that merge uses other template_name if set."""
        # Given
        base = XmlPromptConfig(template_name="base_template")
        other = XmlPromptConfig(template_name="other_template")

        # When
        merged = base.merge_with(other)

        # Then
        assert merged.template_name == "other_template"

    def test_merge_preserves_base_template_when_other_none(self):
        """Test that merge preserves base template when other is None."""
        # Given
        base = XmlPromptConfig(template_name="base_template")
        other = XmlPromptConfig(template_name=None)

        # When
        merged = base.merge_with(other)

        # Then
        assert merged.template_name == "base_template"


# ============================================================================
# from_dict Tests
# ============================================================================


@pytest.mark.unit
class TestFromDict:
    """Test suite for from_dict class method."""

    def test_from_dict_with_all_fields(self):
        """Test from_dict with all fields provided."""
        # Given
        data = {
            "enabled": True,
            "schema_version": "2.0",
            "enforce_response_xml": True,
            "fallback_on_parse_error": False,
            "template_name": "test",
            "custom_template": "<xml/>",
            "extra": {"key": "val"}
        }

        # When
        config = XmlPromptConfig.from_dict(data)

        # Then
        assert config.enabled is True
        assert config.schema_version == "2.0"
        assert config.enforce_response_xml is True
        assert config.fallback_on_parse_error is False
        assert config.template_name == "test"
        assert config.custom_template == "<xml/>"
        assert config.extra == {"key": "val"}

    def test_from_dict_with_defaults(self):
        """Test from_dict uses defaults for missing fields."""
        # Given
        data = {}

        # When
        config = XmlPromptConfig.from_dict(data)

        # Then
        assert config.enabled is False
        assert config.schema_version == "1.0"
        assert config.enforce_response_xml is False
        assert config.fallback_on_parse_error is True
        assert config.template_name is None
        assert config.custom_template is None
        assert config.extra == {}


# ============================================================================
# to_dict Tests
# ============================================================================


@pytest.mark.unit
class TestToDict:
    """Test suite for to_dict method."""

    def test_to_dict_with_defaults(self):
        """Test to_dict with default values."""
        # Given
        config = XmlPromptConfig()

        # When
        data = config.to_dict()

        # Then
        assert data == {
            "enabled": False,
            "schema_version": "1.0",
            "enforce_response_xml": False,
            "fallback_on_parse_error": True,
            "template_name": None,
            "custom_template": None,
            "extra": {}
        }

    def test_to_dict_with_custom_values(self):
        """Test to_dict with custom values."""
        # Given
        config = XmlPromptConfig(
            enabled=True,
            schema_version="2.0",
            enforce_response_xml=True,
            fallback_on_parse_error=False,
            template_name="test",
            custom_template="<xml/>",
            extra={"key": "value"}
        )

        # When
        data = config.to_dict()

        # Then
        assert data["enabled"] is True
        assert data["schema_version"] == "2.0"
        assert data["enforce_response_xml"] is True
        assert data["fallback_on_parse_error"] is False
        assert data["template_name"] == "test"
        assert data["custom_template"] == "<xml/>"
        assert data["extra"] == {"key": "value"}


# ============================================================================
# Round-trip Tests
# ============================================================================


@pytest.mark.unit
class TestRoundTrip:
    """Test suite for round-trip serialization."""

    def test_round_trip_from_dict_to_dict(self):
        """Test that from_dict and to_dict are inverses."""
        # Given
        original_data = {
            "enabled": True,
            "schema_version": "2.0",
            "enforce_response_xml": True,
            "fallback_on_parse_error": False,
            "template_name": "test",
            "custom_template": "<xml/>",
            "extra": {"key": "value"}
        }

        # When
        config = XmlPromptConfig.from_dict(original_data)
        result_data = config.to_dict()

        # Then
        assert result_data == original_data
