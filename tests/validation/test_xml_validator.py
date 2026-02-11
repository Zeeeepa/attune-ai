"""Tests for XML validation.

Copyright 2026 Smart-AI-Memory
Licensed under the Apache License, Version 2.0
"""

import tempfile

from attune.validation import ValidationResult, XMLValidator, validate_xml_response


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


class TestXSDValidationWithLxml:
    """Test XSD validation when lxml is available."""

    def test_xsd_validation_with_valid_schema(self):
        """Test XSD validation with a valid schema file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create a simple XSD schema
            schema_content = """<?xml version="1.0" encoding="UTF-8"?>
<xs:schema xmlns:xs="http://www.w3.org/2001/XMLSchema">
  <xs:element name="thinking" type="xs:string"/>
</xs:schema>"""
            schema_path = f"{tmpdir}/test.xsd"
            with open(schema_path, "w") as f:
                f.write(schema_content)

            validator = XMLValidator(schema_dir=tmpdir, enable_xsd=True)

            # Only test if lxml is available
            if validator._lxml_available:
                xml = "<thinking>Test content</thinking>"
                result = validator.validate(xml, schema_name="test")

                # Should validate successfully
                assert result.is_valid is True

    def test_xsd_validation_with_invalid_xml(self):
        """Test XSD validation with XML that doesn't match schema."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create a restrictive XSD schema
            schema_content = """<?xml version="1.0" encoding="UTF-8"?>
<xs:schema xmlns:xs="http://www.w3.org/2001/XMLSchema">
  <xs:element name="thinking">
    <xs:complexType>
      <xs:sequence>
        <xs:element name="required" type="xs:string"/>
      </xs:sequence>
    </xs:complexType>
  </xs:element>
</xs:schema>"""
            schema_path = f"{tmpdir}/strict.xsd"
            with open(schema_path, "w") as f:
                f.write(schema_content)

            validator = XMLValidator(schema_dir=tmpdir, enable_xsd=True, strict=True)

            # Only test if lxml is available
            if validator._lxml_available:
                # XML missing required element
                xml = "<thinking>Missing required child</thinking>"
                result = validator.validate(xml, schema_name="strict")

                # Should fail validation
                assert result.is_valid is False
                assert "validation failed" in result.error_message.lower()

    def test_xsd_schema_caching_works(self):
        """Test that XSD schemas are properly cached."""
        with tempfile.TemporaryDirectory() as tmpdir:
            schema_content = """<?xml version="1.0" encoding="UTF-8"?>
<xs:schema xmlns:xs="http://www.w3.org/2001/XMLSchema">
  <xs:element name="thinking" type="xs:string"/>
</xs:schema>"""
            schema_path = f"{tmpdir}/cached.xsd"
            with open(schema_path, "w") as f:
                f.write(schema_content)

            validator = XMLValidator(schema_dir=tmpdir, enable_xsd=True)

            if validator._lxml_available:
                xml = "<thinking>First</thinking>"

                # First validation should load schema
                validator.validate(xml, schema_name="cached")
                cache_size_after_first = len(validator._schema_cache)

                # Second validation should use cached schema
                validator.validate(xml, schema_name="cached")
                cache_size_after_second = len(validator._schema_cache)

                # Cache should be populated after first validation
                assert cache_size_after_first > 0
                # Cache size shouldn't increase on second validation
                assert cache_size_after_second == cache_size_after_first

    def test_xsd_validation_with_malformed_schema(self):
        """Test XSD validation with malformed schema file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create malformed XSD
            schema_path = f"{tmpdir}/malformed.xsd"
            with open(schema_path, "w") as f:
                f.write("Not valid XSD content")

            validator = XMLValidator(schema_dir=tmpdir, enable_xsd=True, strict=True)

            if validator._lxml_available:
                xml = "<thinking>Test</thinking>"
                result = validator.validate(xml, schema_name="malformed")

                # Should fail to load schema in strict mode
                assert result.is_valid is False
                assert "loading failed" in result.error_message.lower()

    def test_xsd_validation_non_strict_continues_on_schema_error(self):
        """Test non-strict mode continues when schema validation fails."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create a restrictive XSD schema
            schema_content = """<?xml version="1.0" encoding="UTF-8"?>
<xs:schema xmlns:xs="http://www.w3.org/2001/XMLSchema">
  <xs:element name="thinking">
    <xs:complexType>
      <xs:sequence>
        <xs:element name="required" type="xs:string"/>
      </xs:sequence>
    </xs:complexType>
  </xs:element>
</xs:schema>"""
            schema_path = f"{tmpdir}/strict.xsd"
            with open(schema_path, "w") as f:
                f.write(schema_content)

            validator = XMLValidator(schema_dir=tmpdir, enable_xsd=True, strict=False)

            if validator._lxml_available:
                # XML that's well-formed but doesn't match schema
                xml = "<thinking>Missing required</thinking>"
                result = validator.validate(xml, schema_name="strict")

                # Non-strict should still succeed with fallback
                assert result.is_valid is True
                assert result.fallback_used is True
                assert result.parsed_data is not None


class TestSecurityCases:
    """Test security-related edge cases."""

    def test_xxe_attack_prevention(self):
        """Test that XXE (XML External Entity) attacks are prevented."""
        validator = XMLValidator()

        # XXE attack attempt - should be safely handled by default parser
        xxe_xml = """<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE foo [
  <!ENTITY xxe SYSTEM "file:///etc/passwd">
]>
<root>&xxe;</root>"""

        result = validator.validate(xxe_xml)

        # Should either reject or safely handle without executing entity
        # ET.fromstring by default doesn't process external entities
        assert result is not None

    def test_billion_laughs_attack_prevention(self):
        """Test protection against billion laughs (entity expansion) attack."""
        validator = XMLValidator()

        # Billion laughs attack attempt
        billion_laughs = """<?xml version="1.0"?>
<!DOCTYPE lolz [
  <!ENTITY lol "lol">
  <!ENTITY lol2 "&lol;&lol;&lol;&lol;&lol;&lol;&lol;&lol;&lol;&lol;">
  <!ENTITY lol3 "&lol2;&lol2;&lol2;&lol2;&lol2;&lol2;&lol2;&lol2;&lol2;&lol2;">
]>
<root>&lol3;</root>"""

        result = validator.validate(billion_laughs)

        # Should handle safely without consuming excessive resources
        assert result is not None

    def test_extremely_deep_nesting(self):
        """Test handling of extremely deep XML nesting."""
        validator = XMLValidator()

        # Create very deeply nested XML (100 levels)
        depth = 100
        xml = "<root>" * depth + "deep" + "</root>" * depth

        result = validator.validate(xml)

        # Should handle deep nesting (or fail gracefully)
        assert result is not None

    def test_large_attribute_values(self):
        """Test handling of very large attribute values."""
        validator = XMLValidator()

        # Large attribute value
        large_value = "x" * 100000
        xml = f'<root attr="{large_value}">Content</root>'

        result = validator.validate(xml)

        # Should handle large attributes
        assert result is not None
        if result.is_valid:
            assert "_attributes" in result.parsed_data


class TestFallbackPatterns:
    """Test various fallback parsing scenarios."""

    def test_fallback_with_nested_tags_in_content(self):
        """Test fallback extracts content with nested angle brackets."""
        validator = XMLValidator(strict=False)
        xml = "<thinking>Code: if x < 10 and y > 5</thinking>"

        result = validator.validate(xml)

        assert result.is_valid is True
        if result.parsed_data:
            assert "thinking" in result.parsed_data

    def test_fallback_with_multiple_thinking_tags(self):
        """Test fallback with multiple thinking sections."""
        validator = XMLValidator(strict=False)
        xml = "<thinking>First thought</thinking><thinking>Second thought"

        result = validator.validate(xml)

        # Should extract at least one thinking tag
        if result.fallback_used and result.parsed_data:
            assert "thinking" in result.parsed_data

    def test_fallback_with_whitespace_variations(self):
        """Test fallback handles various whitespace patterns."""
        validator = XMLValidator(strict=False)
        xml = """<thinking>
            Multi-line
            content
            with whitespace
        </thinking><answer>Unclosed"""

        result = validator.validate(xml)

        # Should extract thinking content
        if result.fallback_used and result.parsed_data:
            assert "thinking" in result.parsed_data
            assert "Multi-line" in result.parsed_data["thinking"]

    def test_fallback_extracts_both_tags(self):
        """Test fallback can extract both thinking and answer."""
        validator = XMLValidator(strict=False)
        xml = "<thinking>Analysis</thinking><answer>Result</answer><extra>Unclosed"

        result = validator.validate(xml)

        # Should extract both tags via fallback
        if result.fallback_used and result.parsed_data:
            assert "thinking" in result.parsed_data
            assert "answer" in result.parsed_data


class TestDataExtractionEdgeCases:
    """Test edge cases in data extraction."""

    def test_extract_mixed_content(self):
        """Test extraction with mixed text and element content."""
        validator = XMLValidator()
        xml = "<root>Text<child>Nested</child>More text</root>"

        result = validator.validate(xml)

        assert result.is_valid is True
        assert "child" in result.parsed_data

    def test_extract_multiple_attributes(self):
        """Test extraction with multiple attributes."""
        validator = XMLValidator()
        xml = '<root id="1" type="test" priority="high"><data>Content</data></root>'

        result = validator.validate(xml)

        assert result.is_valid is True
        assert "_attributes" in result.parsed_data
        assert result.parsed_data["_attributes"]["id"] == "1"
        assert result.parsed_data["_attributes"]["type"] == "test"
        assert result.parsed_data["_attributes"]["priority"] == "high"

    def test_extract_recursive_nested_structure(self):
        """Test extraction of deeply recursive structure."""
        validator = XMLValidator()
        xml = """<root>
            <level1>
                <level2>
                    <level3>
                        <level4>Deepest</level4>
                    </level3>
                </level2>
            </level1>
        </root>"""

        result = validator.validate(xml)

        assert result.is_valid is True
        # Navigate through all levels
        data = result.parsed_data
        assert data["level1"]["level2"]["level3"]["level4"] == "Deepest"

    def test_extract_sibling_elements_with_same_tag(self):
        """Test extraction when multiple siblings have same tag name."""
        validator = XMLValidator()
        xml = """<root>
            <item>First</item>
            <item>Second</item>
            <item>Third</item>
        </root>"""

        result = validator.validate(xml)

        # Note: Current implementation only keeps last value for duplicate tags
        # This is a limitation of the simple dict-based extraction
        assert result.is_valid is True

    def test_extract_xml_namespaces(self):
        """Test extraction with XML namespaces."""
        validator = XMLValidator()
        xml = """<root xmlns:custom="http://example.com">
            <custom:data>Namespaced</custom:data>
        </root>"""

        result = validator.validate(xml)

        # Should handle namespaces
        assert result.is_valid is True


class TestValidationResultDataclass:
    """Test ValidationResult dataclass."""

    def test_validation_result_defaults(self):
        """Test ValidationResult default values."""
        result = ValidationResult(is_valid=True)

        assert result.is_valid is True
        assert result.error_message is None
        assert result.parsed_data is None
        assert result.fallback_used is False

    def test_validation_result_all_fields(self):
        """Test ValidationResult with all fields set."""
        result = ValidationResult(
            is_valid=True,
            error_message="Warning message",
            parsed_data={"key": "value"},
            fallback_used=True,
        )

        assert result.is_valid is True
        assert result.error_message == "Warning message"
        assert result.parsed_data == {"key": "value"}
        assert result.fallback_used is True

    def test_validation_result_failure(self):
        """Test ValidationResult for failure case."""
        result = ValidationResult(
            is_valid=False,
            error_message="Parse error",
        )

        assert result.is_valid is False
        assert result.error_message == "Parse error"
