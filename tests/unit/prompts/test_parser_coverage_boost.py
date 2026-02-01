"""Unit tests for XML response parser.

This test suite provides comprehensive coverage for parsing structured XML
responses from LLMs, including graceful fallback for malformed content.

Copyright 2025 Smart-AI-Memory
Licensed under Fair Source License 0.9
"""

import pytest

from attune.prompts.parser import (
    Finding,
    ParsedResponse,
    XmlResponseParser,
)


@pytest.mark.unit
class TestFinding:
    """Test suite for Finding dataclass."""

    def test_create_finding_with_all_fields(self):
        """Test creating Finding with all fields."""
        finding = Finding(
            severity="high",
            title="SQL Injection Risk",
            location="auth.py:42",
            details="User input not sanitized",
            fix="Use parameterized queries",
        )

        assert finding.severity == "high"
        assert finding.title == "SQL Injection Risk"
        assert finding.location == "auth.py:42"
        assert finding.details == "User input not sanitized"
        assert finding.fix == "Use parameterized queries"

    def test_create_finding_with_defaults(self):
        """Test creating Finding with default values."""
        finding = Finding(
            severity="medium",
            title="Test Issue",
        )

        assert finding.severity == "medium"
        assert finding.title == "Test Issue"
        assert finding.location is None
        assert finding.details == ""
        assert finding.fix == ""

    def test_finding_to_dict(self):
        """Test Finding.to_dict() conversion."""
        finding = Finding(
            severity="critical",
            title="Test",
            location="file.py:10",
            details="Details here",
            fix="Fix here",
        )

        result = finding.to_dict()

        assert result == {
            "severity": "critical",
            "title": "Test",
            "location": "file.py:10",
            "details": "Details here",
            "fix": "Fix here",
        }

    def test_finding_from_dict(self):
        """Test Finding.from_dict() creation."""
        data = {
            "severity": "low",
            "title": "Minor Issue",
            "location": "test.py:5",
            "details": "Detail text",
            "fix": "Fix text",
        }

        finding = Finding.from_dict(data)

        assert finding.severity == "low"
        assert finding.title == "Minor Issue"
        assert finding.location == "test.py:5"
        assert finding.details == "Detail text"
        assert finding.fix == "Fix text"

    def test_finding_from_dict_with_missing_fields(self):
        """Test Finding.from_dict() with missing optional fields."""
        data = {"title": "Test"}

        finding = Finding.from_dict(data)

        assert finding.severity == "medium"  # default
        assert finding.title == "Test"
        assert finding.location is None
        assert finding.details == ""
        assert finding.fix == ""


@pytest.mark.unit
class TestParsedResponse:
    """Test suite for ParsedResponse dataclass."""

    def test_create_parsed_response_with_all_fields(self):
        """Test creating ParsedResponse with all fields."""
        findings = [Finding(severity="high", title="Issue 1")]
        response = ParsedResponse(
            success=True,
            raw="<response>...</response>",
            summary="Test summary",
            findings=findings,
            checklist=["Item 1", "Item 2"],
            errors=[],
            extra={"verdict": "approve"},
        )

        assert response.success is True
        assert response.raw == "<response>...</response>"
        assert response.summary == "Test summary"
        assert len(response.findings) == 1
        assert response.checklist == ["Item 1", "Item 2"]
        assert response.errors == []
        assert response.extra == {"verdict": "approve"}

    def test_create_parsed_response_with_defaults(self):
        """Test creating ParsedResponse with default values."""
        response = ParsedResponse(success=False, raw="test")

        assert response.success is False
        assert response.raw == "test"
        assert response.summary is None
        assert response.findings == []
        assert response.checklist == []
        assert response.errors == []
        assert response.extra == {}

    def test_parsed_response_to_dict(self):
        """Test ParsedResponse.to_dict() conversion."""
        findings = [Finding(severity="high", title="Test")]
        response = ParsedResponse(
            success=True,
            raw="raw text",
            summary="Summary",
            findings=findings,
            checklist=["Item 1"],
            errors=[],
            extra={"key": "value"},
        )

        result = response.to_dict()

        assert result["success"] is True
        assert result["raw"] == "raw text"
        assert result["summary"] == "Summary"
        assert len(result["findings"]) == 1
        assert result["checklist"] == ["Item 1"]
        assert result["extra"] == {"key": "value"}

    def test_parsed_response_from_dict(self):
        """Test ParsedResponse.from_dict() creation."""
        data = {
            "success": True,
            "raw": "test",
            "summary": "Summary",
            "findings": [{"severity": "high", "title": "Issue"}],
            "checklist": ["Item"],
            "errors": [],
            "extra": {"key": "val"},
        }

        response = ParsedResponse.from_dict(data)

        assert response.success is True
        assert response.summary == "Summary"
        assert len(response.findings) == 1
        assert response.findings[0].title == "Issue"
        assert response.checklist == ["Item"]

    def test_parsed_response_from_raw(self):
        """Test ParsedResponse.from_raw() fallback creation."""
        response = ParsedResponse.from_raw("Raw text content", ["Error message"])

        assert response.success is False
        assert response.raw == "Raw text content"
        assert response.summary == "Raw text content"
        assert response.errors == ["Error message"]

    def test_parsed_response_from_raw_truncates_long_summary(self):
        """Test that from_raw() truncates long text for summary."""
        long_text = "a" * 1000
        response = ParsedResponse.from_raw(long_text)

        assert len(response.summary) == 500
        assert response.raw == long_text

    def test_parsed_response_from_raw_with_empty_text(self):
        """Test ParsedResponse.from_raw() with empty text."""
        response = ParsedResponse.from_raw("")

        assert response.success is False
        assert response.raw == ""
        assert response.summary is None


@pytest.mark.unit
class TestXmlResponseParserInit:
    """Test suite for XmlResponseParser initialization."""

    def test_parser_initializes_with_fallback_enabled(self):
        """Test parser initializes with fallback_on_error enabled."""
        parser = XmlResponseParser(fallback_on_error=True)
        assert parser.fallback_on_error is True

    def test_parser_initializes_with_fallback_disabled(self):
        """Test parser initializes with fallback_on_error disabled."""
        parser = XmlResponseParser(fallback_on_error=False)
        assert parser.fallback_on_error is False

    def test_parser_defaults_to_fallback_enabled(self):
        """Test parser defaults to fallback enabled."""
        parser = XmlResponseParser()
        assert parser.fallback_on_error is True


@pytest.mark.unit
class TestXmlResponseParserParse:
    """Test suite for XmlResponseParser.parse() method."""

    def test_parse_valid_xml_response(self):
        """Test parsing valid XML response."""
        xml = """<response>
            <summary>Test summary</summary>
            <findings>
                <finding severity="high">
                    <title>Issue 1</title>
                    <location>test.py:10</location>
                    <details>Details here</details>
                    <fix>Fix here</fix>
                </finding>
            </findings>
            <remediation-checklist>
                <item>Fix issue 1</item>
                <item>Run tests</item>
            </remediation-checklist>
        </response>"""

        parser = XmlResponseParser()
        result = parser.parse(xml)

        assert result.success is True
        assert result.summary == "Test summary"
        assert len(result.findings) == 1
        assert result.findings[0].severity == "high"
        assert result.findings[0].title == "Issue 1"
        assert len(result.checklist) == 2

    def test_parse_empty_response(self):
        """Test parsing empty response."""
        parser = XmlResponseParser()
        result = parser.parse("")

        assert result.success is False
        assert result.raw == ""
        assert "Empty response" in result.errors

    def test_parse_response_without_xml(self):
        """Test parsing response with no XML content."""
        parser = XmlResponseParser()
        result = parser.parse("Just plain text, no XML")

        assert result.success is False
        assert result.raw == "Just plain text, no XML"
        assert "No XML content found" in result.errors

    def test_parse_malformed_xml_with_fallback(self):
        """Test parsing malformed XML with fallback enabled."""
        parser = XmlResponseParser(fallback_on_error=True)
        result = parser.parse("<response>Unclosed tag")

        assert result.success is False
        assert "No XML content found" in result.errors[0]

    def test_parse_malformed_xml_without_fallback(self):
        """Test parsing malformed XML with fallback disabled raises error."""
        parser = XmlResponseParser(fallback_on_error=False)

        with pytest.raises(Exception):  # ET.ParseError
            parser.parse("<response>Unclosed tag")

    def test_parse_xml_in_markdown_code_block(self):
        """Test parsing XML wrapped in markdown code block."""
        response = """Here's the result:
```xml
<response>
    <summary>Test</summary>
</response>
```"""

        parser = XmlResponseParser()
        result = parser.parse(response)

        assert result.success is True
        assert result.summary == "Test"

    def test_parse_xml_in_generic_code_block(self):
        """Test parsing XML in generic markdown code block."""
        response = """```
<response>
    <summary>Test</summary>
</response>
```"""

        parser = XmlResponseParser()
        result = parser.parse(response)

        assert result.success is True
        assert result.summary == "Test"

    def test_parse_response_without_xml_raises_when_fallback_disabled(self):
        """Test that no XML raises ValueError when fallback disabled."""
        parser = XmlResponseParser(fallback_on_error=False)

        with pytest.raises(ValueError, match="No XML content"):
            parser.parse("No XML here")


@pytest.mark.unit
class TestExtractXml:
    """Test suite for _extract_xml() method."""

    def test_extract_xml_from_markdown_xml_block(self):
        """Test extracting XML from markdown code block with xml tag."""
        parser = XmlResponseParser()
        response = "```xml\n<response>test</response>\n```"

        result = parser._extract_xml(response)
        assert result == "<response>test</response>"

    def test_extract_xml_from_generic_code_block(self):
        """Test extracting XML from generic markdown code block."""
        parser = XmlResponseParser()
        response = "```\n<response>test</response>\n```"

        result = parser._extract_xml(response)
        assert result == "<response>test</response>"

    def test_extract_xml_with_response_tags(self):
        """Test extracting XML with <response> tags."""
        parser = XmlResponseParser()
        response = "Some text <response>content</response> more text"

        result = parser._extract_xml(response)
        assert "<response>" in result
        assert "content" in result

    def test_extract_xml_direct(self):
        """Test extracting direct XML content."""
        parser = XmlResponseParser()
        response = "<response>test</response>"

        result = parser._extract_xml(response)
        assert result == "<response>test</response>"

    def test_extract_xml_returns_none_for_no_xml(self):
        """Test that _extract_xml returns None when no XML found."""
        parser = XmlResponseParser()
        result = parser._extract_xml("Just plain text")
        assert result is None


@pytest.mark.unit
class TestExtractText:
    """Test suite for _extract_text() method."""

    def test_extract_text_from_xml_element(self):
        """Test extracting text from XML element."""
        import xml.etree.ElementTree as ET

        parser = XmlResponseParser()
        root = ET.fromstring("<root><summary>Test summary</summary></root>")

        result = parser._extract_text(root, "summary")
        assert result == "Test summary"

    def test_extract_text_strips_whitespace(self):
        """Test that extracted text is stripped."""
        import xml.etree.ElementTree as ET

        parser = XmlResponseParser()
        root = ET.fromstring("<root><summary>  Text with spaces  </summary></root>")

        result = parser._extract_text(root, "summary")
        assert result == "Text with spaces"

    def test_extract_text_returns_none_for_missing_tag(self):
        """Test that _extract_text returns None for missing tag."""
        import xml.etree.ElementTree as ET

        parser = XmlResponseParser()
        root = ET.fromstring("<root></root>")

        result = parser._extract_text(root, "missing")
        assert result is None


@pytest.mark.unit
class TestExtractFindings:
    """Test suite for _extract_findings() method."""

    def test_extract_findings_from_xml(self):
        """Test extracting findings from XML."""
        import xml.etree.ElementTree as ET

        xml = """<response>
            <findings>
                <finding severity="high">
                    <title>Issue 1</title>
                    <location>file.py:10</location>
                    <details>Details</details>
                    <fix>Fix</fix>
                </finding>
                <finding severity="low">
                    <title>Issue 2</title>
                </finding>
            </findings>
        </response>"""

        parser = XmlResponseParser()
        root = ET.fromstring(xml)
        findings = parser._extract_findings(root)

        assert len(findings) == 2
        assert findings[0].severity == "high"
        assert findings[0].title == "Issue 1"
        assert findings[1].severity == "low"
        assert findings[1].title == "Issue 2"

    def test_extract_findings_returns_empty_for_no_findings(self):
        """Test that _extract_findings returns empty list when no findings."""
        import xml.etree.ElementTree as ET

        parser = XmlResponseParser()
        root = ET.fromstring("<response></response>")

        findings = parser._extract_findings(root)
        assert findings == []


@pytest.mark.unit
class TestParseFinding:
    """Test suite for _parse_finding() method."""

    def test_parse_finding_with_all_fields(self):
        """Test parsing finding with all fields."""
        import xml.etree.ElementTree as ET

        xml = """<finding severity="critical">
            <title>SQL Injection</title>
            <location>auth.py:42</location>
            <details>User input not sanitized</details>
            <fix>Use parameterized queries</fix>
        </finding>"""

        parser = XmlResponseParser()
        element = ET.fromstring(xml)
        finding = parser._parse_finding(element)

        assert finding.severity == "critical"
        assert finding.title == "SQL Injection"
        assert finding.location == "auth.py:42"
        assert finding.details == "User input not sanitized"
        assert finding.fix == "Use parameterized queries"

    def test_parse_finding_defaults_severity_to_medium(self):
        """Test that _parse_finding defaults severity to medium."""
        import xml.etree.ElementTree as ET

        xml = "<finding><title>Test</title></finding>"

        parser = XmlResponseParser()
        element = ET.fromstring(xml)
        finding = parser._parse_finding(element)

        assert finding.severity == "medium"


@pytest.mark.unit
class TestExtractChecklist:
    """Test suite for _extract_checklist() method."""

    def test_extract_remediation_checklist(self):
        """Test extracting remediation-checklist items."""
        import xml.etree.ElementTree as ET

        xml = """<response>
            <remediation-checklist>
                <item>Fix issue 1</item>
                <item>Run tests</item>
                <item>Deploy changes</item>
            </remediation-checklist>
        </response>"""

        parser = XmlResponseParser()
        root = ET.fromstring(xml)
        checklist = parser._extract_checklist(root)

        assert len(checklist) == 3
        assert checklist[0] == "Fix issue 1"
        assert checklist[1] == "Run tests"
        assert checklist[2] == "Deploy changes"

    def test_extract_generic_checklist(self):
        """Test extracting generic checklist when no remediation-checklist."""
        import xml.etree.ElementTree as ET

        xml = """<response>
            <checklist>
                <item>Item 1</item>
                <item>Item 2</item>
            </checklist>
        </response>"""

        parser = XmlResponseParser()
        root = ET.fromstring(xml)
        checklist = parser._extract_checklist(root)

        assert len(checklist) == 2
        assert checklist[0] == "Item 1"

    def test_extract_checklist_returns_empty_for_no_checklist(self):
        """Test that _extract_checklist returns empty list when no checklist."""
        import xml.etree.ElementTree as ET

        parser = XmlResponseParser()
        root = ET.fromstring("<response></response>")

        checklist = parser._extract_checklist(root)
        assert checklist == []


@pytest.mark.unit
class TestExtractExtra:
    """Test suite for _extract_extra() method."""

    def test_extract_verdict(self):
        """Test extracting verdict from XML."""
        import xml.etree.ElementTree as ET

        xml = "<response><verdict>approve</verdict></response>"

        parser = XmlResponseParser()
        root = ET.fromstring(xml)
        extra = parser._extract_extra(root)

        assert extra["verdict"] == "approve"

    def test_extract_confidence(self):
        """Test extracting confidence from XML."""
        import xml.etree.ElementTree as ET

        xml = """<response>
            <confidence level="high">Strong evidence</confidence>
        </response>"""

        parser = XmlResponseParser()
        root = ET.fromstring(xml)
        extra = parser._extract_extra(root)

        assert extra["confidence"]["level"] == "high"
        assert extra["confidence"]["reasoning"] == "Strong evidence"

    def test_extract_key_insights(self):
        """Test extracting key insights from XML."""
        import xml.etree.ElementTree as ET

        xml = """<response>
            <key-insights>
                <insight>Insight 1</insight>
                <insight>Insight 2</insight>
            </key-insights>
        </response>"""

        parser = XmlResponseParser()
        root = ET.fromstring(xml)
        extra = parser._extract_extra(root)

        assert len(extra["key_insights"]) == 2
        assert extra["key_insights"][0] == "Insight 1"

    def test_extract_suggestions(self):
        """Test extracting suggestions from XML."""
        import xml.etree.ElementTree as ET

        xml = """<response>
            <suggestions>
                <suggestion>Suggestion 1</suggestion>
                <suggestion>Suggestion 2</suggestion>
            </suggestions>
        </response>"""

        parser = XmlResponseParser()
        root = ET.fromstring(xml)
        extra = parser._extract_extra(root)

        assert len(extra["suggestions"]) == 2
        assert extra["suggestions"][0] == "Suggestion 1"

    def test_extract_extra_returns_empty_for_no_extra_fields(self):
        """Test that _extract_extra returns empty dict when no extra fields."""
        import xml.etree.ElementTree as ET

        parser = XmlResponseParser()
        root = ET.fromstring("<response></response>")

        extra = parser._extract_extra(root)
        assert extra == {}
