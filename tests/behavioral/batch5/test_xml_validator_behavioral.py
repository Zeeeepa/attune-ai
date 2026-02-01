"""Behavioral tests for validation/xml_validator.py - XML validation utilities.

Tests Given/When/Then pattern for XML validation.

Copyright 2026 Smart-AI-Memory
Licensed under Apache 2.0
"""


from attune.validation.xml_validator import (
    ValidationResult,
    XMLValidator,
    validate_xml_response,
)


class TestValidationResult:
    """Behavioral tests for ValidationResult dataclass."""

    def test_validation_result_initializes_as_valid(self):
        """Given: No errors
        When: Creating ValidationResult with is_valid=True
        Then: Result is valid."""
        # Given/When
        result = ValidationResult(is_valid=True)

        # Then
        assert result.is_valid is True

    def test_validation_result_can_be_invalid(self):
        """Given: Validation error
        When: Creating ValidationResult with is_valid=False
        Then: Result is invalid."""
        # Given/When
        result = ValidationResult(is_valid=False, error_message="Parse error")

        # Then
        assert result.is_valid is False
        assert result.error_message == "Parse error"

    def test_validation_result_stores_parsed_data(self):
        """Given: Successfully parsed XML
        When: ValidationResult includes parsed_data
        Then: Data is accessible."""
        # Given
        data = {"thinking": "analysis", "answer": "result"}

        # When
        result = ValidationResult(is_valid=True, parsed_data=data)

        # Then
        assert result.parsed_data == data
        assert result.parsed_data["thinking"] == "analysis"

    def test_validation_result_tracks_fallback_usage(self):
        """Given: Fallback parsing used
        When: ValidationResult created with fallback_used=True
        Then: Flag is set."""
        # Given/When
        result = ValidationResult(is_valid=True, fallback_used=True)

        # Then
        assert result.fallback_used is True

    def test_validation_result_fallback_defaults_to_false(self):
        """Given: Standard validation
        When: ValidationResult created without fallback flag
        Then: Defaults to False."""
        # Given/When
        result = ValidationResult(is_valid=True)

        # Then
        assert result.fallback_used is False


class TestXMLValidator:
    """Behavioral tests for XMLValidator class."""

    def test_xml_validator_initializes_with_defaults(self):
        """Given: XMLValidator class
        When: Creating instance with defaults
        Then: Initializes successfully."""
        # Given/When
        validator = XMLValidator()

        # Then
        assert validator is not None
        assert validator.strict is False
        assert validator.enable_xsd is False

    def test_xml_validator_accepts_strict_mode(self):
        """Given: Strict validation required
        When: Creating validator with strict=True
        Then: Strict mode is enabled."""
        # Given/When
        validator = XMLValidator(strict=True)

        # Then
        assert validator.strict is True

    def test_xml_validator_accepts_xsd_validation(self):
        """Given: XSD validation required
        When: Creating validator with enable_xsd=True
        Then: XSD validation is enabled."""
        # Given/When
        validator = XMLValidator(enable_xsd=True)

        # Then
        assert validator.enable_xsd is True

    def test_validate_accepts_well_formed_xml(self):
        """Given: Well-formed XML string
        When: Validating XML
        Then: Returns valid result."""
        # Given
        validator = XMLValidator()
        xml_string = "<thinking>Analysis here</thinking>"

        # When
        result = validator.validate(xml_string)

        # Then
        assert result.is_valid is True
        assert result.error_message is None

    def test_validate_extracts_data_from_valid_xml(self):
        """Given: XML with nested elements
        When: Validating XML
        Then: Extracts structured data."""
        # Given
        validator = XMLValidator()
        xml_string = "<response><thinking>Analysis</thinking><answer>Result</answer></response>"

        # When
        result = validator.validate(xml_string)

        # Then
        assert result.is_valid is True
        assert "thinking" in result.parsed_data
        assert "answer" in result.parsed_data

    def test_validate_handles_malformed_xml_with_fallback(self):
        """Given: Malformed XML and non-strict mode
        When: Validating XML
        Then: Uses fallback parsing."""
        # Given
        validator = XMLValidator(strict=False)
        xml_string = "<thinking>Unclosed tag"

        # When
        result = validator.validate(xml_string)

        # Then
        # Fallback may succeed or fail depending on content
        assert result.fallback_used is True or result.is_valid is False

    def test_validate_strict_mode_rejects_malformed_xml(self):
        """Given: Malformed XML and strict mode
        When: Validating XML
        Then: Returns invalid without fallback."""
        # Given
        validator = XMLValidator(strict=True)
        xml_string = "<thinking>Unclosed tag"

        # When
        result = validator.validate(xml_string)

        # Then
        assert result.is_valid is False
        assert "parsing failed" in result.error_message.lower()

    def test_validate_handles_empty_xml(self):
        """Given: Empty XML string
        When: Validating XML
        Then: Returns error."""
        # Given
        validator = XMLValidator()
        xml_string = ""

        # When
        result = validator.validate(xml_string)

        # Then
        assert result.is_valid is False

    def test_validate_handles_xml_with_attributes(self):
        """Given: XML with attributes
        When: Validating XML
        Then: Extracts attributes."""
        # Given
        validator = XMLValidator()
        xml_string = '<response type="analysis"><content>Data</content></response>'

        # When
        result = validator.validate(xml_string)

        # Then
        assert result.is_valid is True
        assert "_attributes" in result.parsed_data


class TestValidateXMLResponse:
    """Behavioral tests for validate_xml_response convenience function."""

    def test_validate_xml_response_accepts_valid_xml(self):
        """Given: Valid XML response
        When: Calling validate_xml_response
        Then: Returns valid result."""
        # Given
        xml_response = "<thinking>Analysis</thinking><answer>Result</answer>"

        # When
        result = validate_xml_response(xml_response)

        # Then
        assert result.is_valid is True

    def test_validate_xml_response_uses_strict_mode(self):
        """Given: Malformed XML and strict=True
        When: Calling validate_xml_response
        Then: Returns invalid result."""
        # Given
        xml_response = "<thinking>Unclosed"

        # When
        result = validate_xml_response(xml_response, strict=True)

        # Then
        assert result.is_valid is False

    def test_validate_xml_response_extracts_thinking_and_answer(self):
        """Given: XML with thinking and answer tags
        When: Validating response
        Then: Both are extracted."""
        # Given
        xml_response = "<root><thinking>Step by step</thinking><answer>42</answer></root>"

        # When
        result = validate_xml_response(xml_response)

        # Then
        assert result.is_valid is True
        assert "thinking" in result.parsed_data
        assert "answer" in result.parsed_data

    def test_validate_xml_response_handles_multiple_levels(self):
        """Given: XML with multiple nesting levels
        When: Validating response
        Then: Nested data is extracted."""
        # Given
        xml_response = """
        <response>
            <analysis>
                <step1>First</step1>
                <step2>Second</step2>
            </analysis>
            <conclusion>Done</conclusion>
        </response>
        """

        # When
        result = validate_xml_response(xml_response)

        # Then
        assert result.is_valid is True
        assert "analysis" in result.parsed_data
        assert isinstance(result.parsed_data["analysis"], dict)
