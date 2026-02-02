"""Behavioral tests for prompts/parser.py - XML response parser.

Tests Given/When/Then pattern for XML parsing utilities.

Copyright 2026 Smart-AI-Memory
Licensed under Apache 2.0
"""

from attune.prompts.parser import Finding, ParsedResponse


class TestFinding:
    """Behavioral tests for Finding dataclass."""

    def test_finding_initializes_with_required_fields(self):
        """Given: Severity and title
        When: Creating Finding
        Then: Object initializes successfully."""
        # Given
        severity = "high"
        title = "Security vulnerability"

        # When
        finding = Finding(severity=severity, title=title)

        # Then
        assert finding.severity == severity
        assert finding.title == title

    def test_finding_has_optional_location(self):
        """Given: Finding with location
        When: Accessing location
        Then: Location is stored."""
        # Given/When
        finding = Finding(severity="medium", title="Issue", location="file.py:123")

        # Then
        assert finding.location == "file.py:123"

    def test_finding_location_defaults_to_none(self):
        """Given: Finding without location
        When: Checking location
        Then: Defaults to None."""
        # Given/When
        finding = Finding(severity="low", title="Warning")

        # Then
        assert finding.location is None

    def test_finding_has_details_field(self):
        """Given: Finding with details
        When: Accessing details
        Then: Details are stored."""
        # Given/When
        finding = Finding(
            severity="critical", title="Bug", details="Detailed explanation of the issue"
        )

        # Then
        assert "Detailed explanation" in finding.details

    def test_finding_details_defaults_to_empty_string(self):
        """Given: Finding without details
        When: Checking details
        Then: Defaults to empty string."""
        # Given/When
        finding = Finding(severity="info", title="Note")

        # Then
        assert finding.details == ""

    def test_finding_has_fix_field(self):
        """Given: Finding with suggested fix
        When: Accessing fix
        Then: Fix suggestion is stored."""
        # Given/When
        finding = Finding(
            severity="medium", title="Code smell", fix="Refactor using factory pattern"
        )

        # Then
        assert "factory pattern" in finding.fix

    def test_finding_fix_defaults_to_empty_string(self):
        """Given: Finding without fix
        When: Checking fix
        Then: Defaults to empty string."""
        # Given/When
        finding = Finding(severity="low", title="Style issue")

        # Then
        assert finding.fix == ""

    def test_finding_to_dict_includes_all_fields(self):
        """Given: Finding with all fields
        When: Converting to dict
        Then: All fields are present."""
        # Given
        finding = Finding(
            severity="high",
            title="SQL Injection",
            location="db.py:45",
            details="User input not sanitized",
            fix="Use parameterized queries",
        )

        # When
        result = finding.to_dict()

        # Then
        assert result["severity"] == "high"
        assert result["title"] == "SQL Injection"
        assert result["location"] == "db.py:45"
        assert result["details"] == "User input not sanitized"
        assert result["fix"] == "Use parameterized queries"

    def test_finding_from_dict_reconstructs_object(self):
        """Given: Dictionary with finding data
        When: Creating Finding from dict
        Then: Object is reconstructed correctly."""
        # Given
        data = {
            "severity": "critical",
            "title": "XSS Vulnerability",
            "location": "views.py:78",
            "details": "Unescaped output",
            "fix": "Use template escaping",
        }

        # When
        finding = Finding.from_dict(data)

        # Then
        assert finding.severity == "critical"
        assert finding.title == "XSS Vulnerability"
        assert finding.location == "views.py:78"

    def test_finding_from_dict_handles_missing_optional_fields(self):
        """Given: Dictionary with only required fields
        When: Creating Finding from dict
        Then: Optional fields use defaults."""
        # Given
        data = {"severity": "low", "title": "Minor issue"}

        # When
        finding = Finding.from_dict(data)

        # Then
        assert finding.location is None
        assert finding.details == ""
        assert finding.fix == ""

    def test_finding_from_dict_handles_missing_severity(self):
        """Given: Dictionary without severity
        When: Creating Finding from dict
        Then: Uses default severity."""
        # Given
        data = {"title": "Untitled issue"}

        # When
        finding = Finding.from_dict(data)

        # Then
        assert finding.severity == "medium"  # Default from from_dict


class TestParsedResponse:
    """Behavioral tests for ParsedResponse dataclass."""

    def test_parsed_response_initializes_with_required_fields(self):
        """Given: Success status and raw text
        When: Creating ParsedResponse
        Then: Object initializes."""
        # Given
        success = True
        raw = "<response>Test</response>"

        # When
        response = ParsedResponse(success=success, raw=raw)

        # Then
        assert response.success is True
        assert response.raw == raw

    def test_parsed_response_has_summary_field(self):
        """Given: ParsedResponse with summary
        When: Accessing summary
        Then: Summary is stored."""
        # Given/When
        response = ParsedResponse(success=True, raw="test", summary="Brief summary")

        # Then
        assert response.summary == "Brief summary"

    def test_parsed_response_summary_defaults_to_none(self):
        """Given: ParsedResponse without summary
        When: Checking summary
        Then: Defaults to None."""
        # Given/When
        response = ParsedResponse(success=True, raw="test")

        # Then
        assert response.summary is None

    def test_parsed_response_has_findings_list(self):
        """Given: ParsedResponse with findings
        When: Accessing findings
        Then: List of Finding objects returned."""
        # Given
        finding1 = Finding(severity="high", title="Issue 1")
        finding2 = Finding(severity="medium", title="Issue 2")

        # When
        response = ParsedResponse(success=True, raw="test", findings=[finding1, finding2])

        # Then
        assert len(response.findings) == 2
        assert response.findings[0].title == "Issue 1"

    def test_parsed_response_findings_defaults_to_empty_list(self):
        """Given: ParsedResponse without findings
        When: Checking findings
        Then: Defaults to empty list."""
        # Given/When
        response = ParsedResponse(success=True, raw="test")

        # Then
        assert response.findings == []

    def test_parsed_response_has_checklist(self):
        """Given: ParsedResponse with checklist items
        When: Accessing checklist
        Then: List of strings returned."""
        # Given/When
        response = ParsedResponse(
            success=True, raw="test", checklist=["Task 1", "Task 2", "Task 3"]
        )

        # Then
        assert len(response.checklist) == 3
        assert "Task 1" in response.checklist

    def test_parsed_response_checklist_defaults_to_empty_list(self):
        """Given: ParsedResponse without checklist
        When: Checking checklist
        Then: Defaults to empty list."""
        # Given/When
        response = ParsedResponse(success=True, raw="test")

        # Then
        assert response.checklist == []

    def test_parsed_response_has_errors_list(self):
        """Given: ParsedResponse with errors
        When: Accessing errors
        Then: List of error strings returned."""
        # Given/When
        response = ParsedResponse(success=False, raw="test", errors=["Parse error", "Invalid XML"])

        # Then
        assert len(response.errors) == 2
        assert "Parse error" in response.errors

    def test_parsed_response_errors_defaults_to_empty_list(self):
        """Given: ParsedResponse without errors
        When: Checking errors
        Then: Defaults to empty list."""
        # Given/When
        response = ParsedResponse(success=True, raw="test")

        # Then
        assert response.errors == []

    def test_parsed_response_has_extra_dict(self):
        """Given: ParsedResponse with extra data
        When: Accessing extra
        Then: Dictionary with additional data returned."""
        # Given/When
        response = ParsedResponse(
            success=True, raw="test", extra={"custom_field": "value", "count": 42}
        )

        # Then
        assert response.extra["custom_field"] == "value"
        assert response.extra["count"] == 42

    def test_parsed_response_extra_defaults_to_empty_dict(self):
        """Given: ParsedResponse without extra data
        When: Checking extra
        Then: Defaults to empty dict."""
        # Given/When
        response = ParsedResponse(success=True, raw="test")

        # Then
        assert response.extra == {}

    def test_parsed_response_to_dict_includes_all_fields(self):
        """Given: ParsedResponse with all fields populated
        When: Converting to dict
        Then: All fields are present."""
        # Given
        finding = Finding(severity="high", title="Issue")
        response = ParsedResponse(
            success=True,
            raw="<test/>",
            summary="Summary text",
            findings=[finding],
            checklist=["Task 1"],
            errors=["Error 1"],
            extra={"key": "value"},
        )

        # When
        result = response.to_dict()

        # Then
        assert result["success"] is True
        assert result["raw"] == "<test/>"
        assert result["summary"] == "Summary text"
        assert len(result["findings"]) == 1
        assert len(result["checklist"]) == 1
        assert len(result["errors"]) == 1
        assert result["extra"]["key"] == "value"

    def test_parsed_response_from_dict_reconstructs_object(self):
        """Given: Dictionary with response data
        When: Creating ParsedResponse from dict
        Then: Object is reconstructed."""
        # Given
        data = {
            "success": True,
            "raw": "<xml/>",
            "summary": "Test summary",
            "findings": [{"severity": "low", "title": "Test finding"}],
            "checklist": ["Item 1"],
            "errors": [],
            "extra": {"meta": "data"},
        }

        # When
        response = ParsedResponse.from_dict(data)

        # Then
        assert response.success is True
        assert response.summary == "Test summary"
        assert len(response.findings) == 1
        assert response.findings[0].title == "Test finding"

    def test_parsed_response_from_raw_creates_fallback(self):
        """Given: Raw text and errors
        When: Creating ParsedResponse from raw
        Then: Fallback response created."""
        # Given
        raw_text = "Unparseable response"
        errors = ["XML parse failed"]

        # When
        response = ParsedResponse.from_raw(raw_text, errors)

        # Then
        assert response.success is False
        assert response.raw == raw_text
        assert "XML parse failed" in response.errors

    def test_parsed_response_from_raw_handles_none_errors(self):
        """Given: Raw text without XML content
        When: Creating ParsedResponse from raw
        Then: Errors contains XML parsing error."""
        # Given
        raw_text = "Some text"

        # When
        response = ParsedResponse.from_raw(raw_text)

        # Then
        # When no XML content is found, the parser adds an error
        assert response.errors == ["No XML content found"]
