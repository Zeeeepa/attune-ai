"""Tests for prompts module.

Covers PromptContext, Finding, ParsedResponse, and XmlResponseParser.

Copyright 2025 Smart-AI-Memory
Licensed under Fair Source License 0.9
"""

import pytest

from empathy_os.prompts.context import PromptContext
from empathy_os.prompts.parser import Finding, ParsedResponse, XmlResponseParser


@pytest.mark.unit
class TestPromptContext:
    """Tests for PromptContext dataclass."""

    def test_basic_creation(self):
        """Test creating a basic PromptContext."""
        ctx = PromptContext(
            role="developer",
            goal="write code",
        )

        assert ctx.role == "developer"
        assert ctx.goal == "write code"
        assert ctx.instructions == []
        assert ctx.constraints == []
        assert ctx.input_type == "code"
        assert ctx.input_payload == ""
        assert ctx.extra == {}

    def test_full_creation(self):
        """Test creating a PromptContext with all fields."""
        ctx = PromptContext(
            role="security analyst",
            goal="find vulnerabilities",
            instructions=["Check for SQL injection", "Check for XSS"],
            constraints=["Be specific", "Prioritize critical issues"],
            input_type="code",
            input_payload="def foo(): pass",
            extra={"language": "python"},
        )

        assert ctx.role == "security analyst"
        assert len(ctx.instructions) == 2
        assert len(ctx.constraints) == 2
        assert ctx.extra["language"] == "python"

    def test_role_required(self):
        """Test that role is required."""
        with pytest.raises(ValueError, match="role is required"):
            PromptContext(role="", goal="test")

    def test_goal_required(self):
        """Test that goal is required."""
        with pytest.raises(ValueError, match="goal is required"):
            PromptContext(role="test", goal="")

    def test_for_security_audit(self):
        """Test security audit factory method."""
        ctx = PromptContext.for_security_audit(
            code="def vulnerable(): eval(input())",
            findings_summary="1 critical issue found",
            risk_level="high",
        )

        assert "security" in ctx.role.lower()
        assert ctx.input_type == "code"
        assert ctx.input_payload == "def vulnerable(): eval(input())"
        assert ctx.extra["findings_summary"] == "1 critical issue found"
        assert ctx.extra["risk_level"] == "high"
        assert len(ctx.instructions) > 0

    def test_for_code_review(self):
        """Test code review factory method."""
        ctx = PromptContext.for_code_review(
            code_or_diff="+ new_line()",
            input_type="diff",
            context="Adding new feature",
        )

        assert "review" in ctx.goal.lower()
        assert ctx.input_type == "diff"
        assert ctx.input_payload == "+ new_line()"
        assert ctx.extra["context"] == "Adding new feature"

    def test_for_code_review_defaults(self):
        """Test code review with defaults."""
        ctx = PromptContext.for_code_review(
            code_or_diff="def foo(): pass",
        )

        assert ctx.input_type == "code"

    def test_for_research(self):
        """Test research factory method."""
        ctx = PromptContext.for_research(
            question="What is the best caching strategy?",
            context="High-traffic web application",
        )

        assert "research" in ctx.goal.lower()
        assert ctx.input_type == "question"
        assert ctx.input_payload == "What is the best caching strategy?"
        assert ctx.extra["context"] == "High-traffic web application"

    def test_with_extra(self):
        """Test with_extra creates new context."""
        original = PromptContext(
            role="developer",
            goal="write code",
            extra={"a": 1},
        )

        new_ctx = original.with_extra(b=2, c=3)

        # Original unchanged
        assert "b" not in original.extra

        # New has both
        assert new_ctx.extra["a"] == 1
        assert new_ctx.extra["b"] == 2
        assert new_ctx.extra["c"] == 3

    def test_with_extra_overwrite(self):
        """Test with_extra can overwrite existing keys."""
        original = PromptContext(
            role="developer",
            goal="write code",
            extra={"key": "old"},
        )

        new_ctx = original.with_extra(key="new")

        assert original.extra["key"] == "old"
        assert new_ctx.extra["key"] == "new"


@pytest.mark.unit
class TestFinding:
    """Tests for Finding dataclass."""

    def test_basic_creation(self):
        """Test creating a basic Finding."""
        finding = Finding(
            severity="high",
            title="SQL Injection",
        )

        assert finding.severity == "high"
        assert finding.title == "SQL Injection"
        assert finding.location is None
        assert finding.details == ""
        assert finding.fix == ""

    def test_full_creation(self):
        """Test creating a Finding with all fields."""
        finding = Finding(
            severity="critical",
            title="Remote Code Execution",
            location="src/app.py:42",
            details="User input passed to eval()",
            fix="Use ast.literal_eval() instead",
        )

        assert finding.severity == "critical"
        assert finding.location == "src/app.py:42"
        assert "eval" in finding.details
        assert "literal_eval" in finding.fix

    def test_to_dict(self):
        """Test Finding serialization."""
        finding = Finding(
            severity="medium",
            title="Missing Input Validation",
            location="src/api.py:100",
            details="User input not sanitized",
            fix="Add input validation",
        )

        data = finding.to_dict()

        assert data["severity"] == "medium"
        assert data["title"] == "Missing Input Validation"
        assert data["location"] == "src/api.py:100"

    def test_from_dict(self):
        """Test Finding deserialization."""
        data = {
            "severity": "low",
            "title": "Deprecated API",
            "location": "src/old.py:5",
            "details": "Using deprecated function",
            "fix": "Update to new API",
        }

        finding = Finding.from_dict(data)

        assert finding.severity == "low"
        assert finding.title == "Deprecated API"
        assert finding.location == "src/old.py:5"

    def test_from_dict_defaults(self):
        """Test Finding from_dict with minimal data."""
        data = {"title": "Test"}

        finding = Finding.from_dict(data)

        assert finding.severity == "medium"  # default
        assert finding.title == "Test"
        assert finding.location is None

    def test_roundtrip(self):
        """Test Finding serialization roundtrip."""
        original = Finding(
            severity="high",
            title="Test Finding",
            location="test.py:1",
            details="Details here",
            fix="Fix here",
        )

        data = original.to_dict()
        restored = Finding.from_dict(data)

        assert restored.severity == original.severity
        assert restored.title == original.title
        assert restored.location == original.location


@pytest.mark.unit
class TestParsedResponse:
    """Tests for ParsedResponse dataclass."""

    def test_basic_creation(self):
        """Test creating a basic ParsedResponse."""
        response = ParsedResponse(
            success=True,
            raw="<response>test</response>",
        )

        assert response.success is True
        assert response.raw == "<response>test</response>"
        assert response.summary is None
        assert response.findings == []
        assert response.checklist == []
        assert response.errors == []

    def test_full_creation(self):
        """Test creating a ParsedResponse with all fields."""
        response = ParsedResponse(
            success=True,
            raw="<response>...</response>",
            summary="Found 2 issues",
            findings=[
                Finding(severity="high", title="Issue 1"),
                Finding(severity="low", title="Issue 2"),
            ],
            checklist=["Fix issue 1", "Fix issue 2"],
            extra={"verdict": "needs work"},
        )

        assert len(response.findings) == 2
        assert len(response.checklist) == 2
        assert response.extra["verdict"] == "needs work"

    def test_from_raw(self):
        """Test creating fallback response from raw text."""
        response = ParsedResponse.from_raw(
            "No XML here, just plain text",
            ["No XML content found"],
        )

        assert response.success is False
        assert "No XML" in response.errors[0]
        assert response.summary == "No XML here, just plain text"[:500]

    def test_from_raw_long_text(self):
        """Test that from_raw truncates long text for summary."""
        long_text = "x" * 1000
        response = ParsedResponse.from_raw(long_text)

        assert len(response.summary) == 500

    def test_to_dict(self):
        """Test ParsedResponse serialization."""
        response = ParsedResponse(
            success=True,
            raw="<response>test</response>",
            summary="Test summary",
            findings=[Finding(severity="high", title="Test")],
            checklist=["Item 1"],
            extra={"key": "value"},
        )

        data = response.to_dict()

        assert data["success"] is True
        assert data["summary"] == "Test summary"
        assert len(data["findings"]) == 1
        assert data["checklist"] == ["Item 1"]

    def test_from_dict(self):
        """Test ParsedResponse deserialization."""
        data = {
            "success": True,
            "raw": "<response>...</response>",
            "summary": "Summary",
            "findings": [{"severity": "high", "title": "Test"}],
            "checklist": ["Item"],
            "errors": [],
            "extra": {"key": "value"},
        }

        response = ParsedResponse.from_dict(data)

        assert response.success is True
        assert len(response.findings) == 1
        assert response.findings[0].title == "Test"


@pytest.mark.unit
class TestXmlResponseParser:
    """Tests for XmlResponseParser class."""

    @pytest.fixture
    def parser(self):
        """Create a parser instance."""
        return XmlResponseParser()

    def test_parse_empty_response(self, parser):
        """Test parsing empty response."""
        result = parser.parse("")

        assert result.success is False
        assert "Empty response" in result.errors[0]

    def test_parse_no_xml(self, parser):
        """Test parsing response with no XML."""
        result = parser.parse("This is just plain text without any XML")

        assert result.success is False
        assert result.raw == "This is just plain text without any XML"

    def test_parse_simple_xml(self, parser):
        """Test parsing simple XML response."""
        xml = """
        <response>
            <summary>Found 1 issue</summary>
        </response>
        """

        result = parser.parse(xml)

        assert result.success is True
        assert result.summary == "Found 1 issue"

    def test_parse_xml_in_markdown(self, parser):
        """Test parsing XML inside markdown code block."""
        response = """
        Here's the analysis:

        ```xml
        <response>
            <summary>Test summary</summary>
        </response>
        ```

        Let me know if you need more details.
        """

        result = parser.parse(response)

        assert result.success is True
        assert result.summary == "Test summary"

    def test_parse_xml_in_generic_code_block(self, parser):
        """Test parsing XML in generic code block."""
        response = """
        ```
        <response>
            <summary>Generic block</summary>
        </response>
        ```
        """

        result = parser.parse(response)

        assert result.success is True
        assert result.summary == "Generic block"

    def test_parse_findings(self, parser):
        """Test parsing findings from XML."""
        xml = """
        <response>
            <findings>
                <finding severity="critical">
                    <title>SQL Injection</title>
                    <location>src/db.py:42</location>
                    <details>User input passed directly to query</details>
                    <fix>Use parameterized queries</fix>
                </finding>
                <finding severity="medium">
                    <title>Missing Validation</title>
                </finding>
            </findings>
        </response>
        """

        result = parser.parse(xml)

        assert result.success is True
        assert len(result.findings) == 2
        assert result.findings[0].severity == "critical"
        assert result.findings[0].title == "SQL Injection"
        assert result.findings[0].location == "src/db.py:42"
        assert result.findings[1].severity == "medium"

    def test_parse_findings_items(self, parser):
        """Test parsing findings with item tags."""
        xml = """
        <response>
            <findings>
                <item severity="high">
                    <title>Issue 1</title>
                </item>
            </findings>
        </response>
        """

        result = parser.parse(xml)

        assert len(result.findings) == 1
        assert result.findings[0].severity == "high"

    def test_parse_checklist(self, parser):
        """Test parsing remediation checklist."""
        xml = """
        <response>
            <remediation-checklist>
                <item>Update dependencies</item>
                <item>Add input validation</item>
                <item>Enable HTTPS</item>
            </remediation-checklist>
        </response>
        """

        result = parser.parse(xml)

        assert len(result.checklist) == 3
        assert "Update dependencies" in result.checklist

    def test_parse_generic_checklist(self, parser):
        """Test parsing generic checklist tag."""
        xml = """
        <response>
            <checklist>
                <item>Step 1</item>
                <item>Step 2</item>
            </checklist>
        </response>
        """

        result = parser.parse(xml)

        assert len(result.checklist) == 2

    def test_parse_extra_verdict(self, parser):
        """Test parsing extra verdict field."""
        xml = """
        <response>
            <verdict>Approved with minor changes</verdict>
        </response>
        """

        result = parser.parse(xml)

        assert result.extra["verdict"] == "Approved with minor changes"

    def test_parse_extra_confidence(self, parser):
        """Test parsing extra confidence field."""
        xml = """
        <response>
            <confidence level="high">Based on multiple sources</confidence>
        </response>
        """

        result = parser.parse(xml)

        assert result.extra["confidence"]["level"] == "high"
        assert "multiple sources" in result.extra["confidence"]["reasoning"]

    def test_parse_extra_suggestions(self, parser):
        """Test parsing extra suggestions field."""
        xml = """
        <response>
            <suggestions>
                <suggestion>Use type hints</suggestion>
                <suggestion>Add docstrings</suggestion>
            </suggestions>
        </response>
        """

        result = parser.parse(xml)

        assert len(result.extra["suggestions"]) == 2
        assert "type hints" in result.extra["suggestions"][0]

    def test_parse_invalid_xml_fallback(self, parser):
        """Test that invalid XML falls back gracefully."""
        # XML that looks valid to regex but is malformed
        result = parser.parse("<response><broken>xml</response>")

        assert result.success is False
        assert "parse error" in result.errors[0].lower() or "no xml" in result.errors[0].lower()

    def test_parse_invalid_xml_no_fallback(self):
        """Test that invalid XML raises when fallback disabled."""
        parser = XmlResponseParser(fallback_on_error=False)

        with pytest.raises(Exception):  # ET.ParseError
            parser.parse("<broken>xml")

    def test_parse_no_xml_no_fallback(self):
        """Test that no XML raises when fallback disabled."""
        parser = XmlResponseParser(fallback_on_error=False)

        with pytest.raises(ValueError, match="No XML content"):
            parser.parse("Plain text without XML")

    def test_extract_xml_response_tags(self, parser):
        """Test extracting XML with response tags from mixed content."""
        content = """
        Some text before
        <response>
            <summary>Inner content</summary>
        </response>
        Some text after
        """

        result = parser.parse(content)

        assert result.success is True
        assert result.summary == "Inner content"
