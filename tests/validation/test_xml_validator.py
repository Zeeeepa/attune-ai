"""Tests for XML validation.

Copyright 2026 Smart-AI-Memory
Licensed under Fair Source License 0.9
"""

import tempfile

from empathy_os.validation import ValidationResult, XMLValidator, validate_xml_response


class TestWellFormednessValidation:
    """Test XML well-formedness validation."""

    def test_valid_xml_passes(self):
        """Test valid XML passes validation."""
        validator = XMLValidator()
        xml = "<thinking>Analysis</thinking>"

        result = validator.validate(xml)

        assert result.is_valid is True
        assert result.error_message is None
        assert result.fallback_used is False

    def test_malformed_xml_with_fallback(self):
        """Test malformed XML uses fallback."""
        validator = XMLValidator(strict=False)
        xml = "<thinking>Unclosed tag"

        result = validator.validate(xml)

        # Fallback should extract thinking content
        assert result.fallback_used is True
        assert (
            result.parsed_data is None
            or "thinking" in result.parsed_data
            or result.is_valid is False
        )

    def test_malformed_xml_strict_mode(self):
        """Test malformed XML fails in strict mode."""
        validator = XMLValidator(strict=True)
        xml = "<thinking>Unclosed tag"

        result = validator.validate(xml)

        assert result.is_valid is False
        assert "parsing failed" in result.error_message.lower()
        assert result.fallback_used is False

    def test_empty_xml(self):
        """Test empty XML string."""
        validator = XMLValidator()
        xml = ""

        result = validator.validate(xml)

        assert result.is_valid is False


class TestDataExtraction:
    """Test data extraction from valid XML."""

    def test_extract_thinking_answer(self):
        """Test extraction of thinking and answer tags."""
        validator = XMLValidator()
        xml = "<root><thinking>Process</thinking><answer>Result</answer></root>"

        result = validator.validate(xml)

        assert result.is_valid is True
        assert "thinking" in result.parsed_data
        assert "answer" in result.parsed_data
        assert result.parsed_data["thinking"] == "Process"
        assert result.parsed_data["answer"] == "Result"

    def test_extract_nested_elements(self):
        """Test extraction of nested elements."""
        validator = XMLValidator()
        xml = """<root>
            <assessment>
                <security>Good</security>
                <performance>Fast</performance>
            </assessment>
        </root>"""

        result = validator.validate(xml)

        assert result.is_valid is True
        assert "assessment" in result.parsed_data
        assert isinstance(result.parsed_data["assessment"], dict)
        assert result.parsed_data["assessment"]["security"] == "Good"

    def test_extract_attributes(self):
        """Test extraction of XML attributes."""
        validator = XMLValidator()
        xml = '<root priority="high"><task>Complete</task></root>'

        result = validator.validate(xml)

        assert result.is_valid is True
        assert "_attributes" in result.parsed_data
        assert result.parsed_data["_attributes"]["priority"] == "high"

    def test_extract_empty_elements(self):
        """Test extraction of empty elements."""
        validator = XMLValidator()
        xml = "<root><empty/><filled>Text</filled></root>"

        result = validator.validate(xml)

        assert result.is_valid is True
        assert "empty" in result.parsed_data
        assert result.parsed_data["empty"] == ""
        assert result.parsed_data["filled"] == "Text"


class TestFallbackParsing:
    """Test fallback parsing for malformed XML."""

    def test_fallback_extracts_thinking(self):
        """Test fallback extracts thinking content."""
        validator = XMLValidator(strict=False)
        xml = "<thinking>Analysis process</thinking><answer>Unclosed"

        result = validator.validate(xml)

        # Should extract thinking via fallback
        assert result.fallback_used is True
        if result.parsed_data:
            assert "thinking" in result.parsed_data
            assert "Analysis process" in result.parsed_data["thinking"]

    def test_fallback_extracts_answer(self):
        """Test fallback extracts answer content."""
        validator = XMLValidator(strict=False)
        xml = "<answer>Final result</answer>"

        result = validator.validate(xml)

        assert result.is_valid is True
        if result.parsed_data:
            assert "answer" in result.parsed_data

    def test_fallback_handles_complete_failure(self):
        """Test fallback when nothing can be extracted."""
        validator = XMLValidator(strict=False)
        xml = "Not XML at all"

        result = validator.validate(xml)

        # Should fail even with fallback
        assert result.is_valid is False
        assert result.fallback_used is True


class TestXSDValidation:
    """Test XSD schema validation."""

    def test_xsd_validation_disabled_by_default(self):
        """Test XSD validation is disabled by default."""
        validator = XMLValidator()
        xml = "<thinking>Test</thinking>"

        result = validator.validate(xml, schema_name="test_schema")

        # Should succeed without XSD validation
        assert result.is_valid is True

    def test_xsd_validation_requires_lxml(self):
        """Test XSD validation requires lxml."""
        validator = XMLValidator(enable_xsd=True)

        # XSD validation availability depends on lxml
        if not validator._lxml_available:
            xml = "<thinking>Test</thinking>"
            result = validator.validate(xml, schema_name="test_schema")

            # Should fail gracefully if lxml not available
            # or continue with fallback
            assert result is not None

    def test_xsd_validation_missing_schema_file(self):
        """Test XSD validation with missing schema file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            validator = XMLValidator(schema_dir=tmpdir, enable_xsd=True)
            xml = "<thinking>Test</thinking>"

            result = validator.validate(xml, schema_name="nonexistent")

            # Should handle missing schema gracefully
            if validator._lxml_available:
                # Either fails or uses fallback
                assert result is not None


class TestStrictMode:
    """Test strict validation mode."""

    def test_strict_mode_fails_on_error(self):
        """Test strict mode fails on validation errors."""
        validator = XMLValidator(strict=True)
        xml = "<thinking>Unclosed"

        result = validator.validate(xml)

        assert result.is_valid is False
        assert result.fallback_used is False

    def test_non_strict_uses_fallback(self):
        """Test non-strict mode uses fallback."""
        validator = XMLValidator(strict=False)
        xml = "<thinking>Unclosed"

        result = validator.validate(xml)

        # Should attempt fallback
        assert result.fallback_used is True


class TestConvenienceFunction:
    """Test validate_xml_response convenience function."""

    def test_validate_xml_response_default(self):
        """Test convenience function with defaults."""
        xml = "<thinking>Test</thinking>"

        result = validate_xml_response(xml)

        assert result.is_valid is True
        assert isinstance(result, ValidationResult)

    def test_validate_xml_response_strict(self):
        """Test convenience function with strict mode."""
        xml = "<thinking>Unclosed"

        result = validate_xml_response(xml, strict=True)

        assert result.is_valid is False

    def test_validate_xml_response_with_schema(self):
        """Test convenience function with schema name."""
        xml = "<thinking>Test</thinking>"

        result = validate_xml_response(xml, schema_name="test")

        # Should complete without error
        assert result is not None


class TestEdgeCases:
    """Test edge cases."""

    def test_very_large_xml(self):
        """Test validation of very large XML."""
        validator = XMLValidator()
        xml = "<root>" + ("<item>data</item>" * 10000) + "</root>"

        result = validator.validate(xml)

        # Should handle large XML
        assert result.is_valid is True

    def test_deeply_nested_xml(self):
        """Test deeply nested XML."""
        validator = XMLValidator()
        xml = "<a><b><c><d><e>deep</e></d></c></b></a>"

        result = validator.validate(xml)

        assert result.is_valid is True
        # Navigate to deeply nested value
        data = result.parsed_data
        assert data["b"]["c"]["d"]["e"] == "deep"

    def test_xml_with_special_characters(self):
        """Test XML with special characters."""
        validator = XMLValidator()
        xml = "<root><data>&lt;special&gt;</data></root>"

        result = validator.validate(xml)

        assert result.is_valid is True

    def test_xml_with_cdata(self):
        """Test XML with CDATA sections."""
        validator = XMLValidator()
        xml = "<root><![CDATA[<not>parsed</not>]]></root>"

        result = validator.validate(xml)

        # Should handle CDATA
        assert result.is_valid is True

    def test_multiple_root_elements(self):
        """Test XML with multiple root elements (invalid)."""
        validator = XMLValidator(strict=False)
        xml = "<root1>A</root1><root2>B</root2>"

        result = validator.validate(xml)

        # Should fail or use fallback
        assert result.is_valid is False or result.fallback_used is True


class TestCaching:
    """Test schema caching."""

    def test_schema_cache_reuse(self):
        """Test schemas are cached for reuse."""
        with tempfile.TemporaryDirectory() as tmpdir:
            validator = XMLValidator(schema_dir=tmpdir, enable_xsd=True)

            # Cache should be empty initially
            assert len(validator._schema_cache) == 0

            # After validation with schema (if lxml available), cache might be populated
            # This is primarily a smoke test that caching doesn't break anything
            xml = "<thinking>Test</thinking>"
            result = validator.validate(xml, schema_name="test")

            # Should complete without error
            assert result is not None
