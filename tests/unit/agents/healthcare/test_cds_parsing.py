"""Tests for CDS response parsing.

Copyright 2026 Smart-AI-Memory
Licensed under Apache 2.0
"""

import json

from src.attune.agents.healthcare.cds_parsing import (
    parse_clinical_response,
    parse_ecg_response,
)


class TestParseECGResponse:
    """Test ECG response parsing."""

    def test_empty_response_returns_parse_error(self):
        """Test empty string returns parse error."""
        result = parse_ecg_response("")
        assert result == {"parse_error": "empty response"}

    def test_none_response_returns_parse_error(self):
        """Test None returns parse error."""
        result = parse_ecg_response(None)
        assert result == {"parse_error": "empty response"}

    def test_whitespace_only_returns_parse_error(self):
        """Test whitespace-only returns parse error."""
        result = parse_ecg_response("   \n  ")
        assert result == {"parse_error": "empty response"}

    def test_raw_json_parsed(self):
        """Test raw JSON is parsed correctly."""
        data = {"heart_rate": 82, "rhythm_classification": "normal_sinus"}
        result = parse_ecg_response(json.dumps(data))
        assert result["heart_rate"] == 82
        assert result["rhythm_classification"] == "normal_sinus"

    def test_markdown_fenced_json_parsed(self):
        """Test markdown-fenced JSON is parsed."""
        text = 'Analysis:\n```json\n{"heart_rate": 110, "pvc_burden_pct": 5.2}\n```'
        result = parse_ecg_response(text)
        assert result["heart_rate"] == 110
        assert result["pvc_burden_pct"] == 5.2

    def test_xml_delimited_json_parsed(self):
        """Test XML-delimited JSON is parsed."""
        text = '<analysis>{"heart_rate": 95, "score": 80}</analysis>'
        result = parse_ecg_response(text)
        assert result["heart_rate"] == 95
        assert result["score"] == 80

    def test_regex_fallback_heart_rate(self):
        """Test regex extracts heart rate from text."""
        result = parse_ecg_response("HR: 110 bpm, PVC burden: 5.2%")
        assert result["heart_rate"] == 110.0
        assert result["pvc_burden_pct"] == 5.2
        assert result["parse_method"] == "regex"

    def test_regex_fallback_hrv(self):
        """Test regex extracts HRV from text."""
        result = parse_ecg_response("SDNN: 45 ms")
        assert result["hrv_sdnn"] == 45.0

    def test_regex_fallback_rhythm_classification(self):
        """Test regex extracts rhythm classification."""
        result = parse_ecg_response("This shows sinus tachycardia with HR: 120 bpm")
        assert result["rhythm_classification"] == "sinus_tachycardia"
        assert result["heart_rate"] == 120.0

    def test_regex_normal_sinus_rhythm(self):
        """Test regex detects normal sinus rhythm."""
        result = parse_ecg_response("Normal sinus rhythm detected. Heart rate: 75 bpm")
        assert result["rhythm_classification"] == "normal_sinus"

    def test_regex_bradycardia(self):
        """Test regex detects sinus bradycardia."""
        result = parse_ecg_response("Sinus bradycardia noted")
        assert result["rhythm_classification"] == "sinus_bradycardia"

    def test_regex_afib(self):
        """Test regex detects atrial fibrillation."""
        result = parse_ecg_response("Possible atrial fibrillation")
        assert result["rhythm_classification"] == "possible_afib"

    def test_regex_frequent_pvcs(self):
        """Test regex detects frequent PVCs."""
        result = parse_ecg_response("Frequent PVC complexes observed")
        assert result["rhythm_classification"] == "frequent_pvcs"

    def test_unparseable_returns_error(self):
        """Test unparseable text returns error with raw text."""
        result = parse_ecg_response("completely random text with no medical content")
        assert "parse_error" in result
        assert "raw_text" in result

    def test_xml_strategy_priority_over_regex(self):
        """Test XML strategy takes priority over regex."""
        text = '<analysis>{"heart_rate": 99}</analysis> HR: 120 bpm'
        result = parse_ecg_response(text)
        assert result["heart_rate"] == 99  # XML wins


class TestParseClinicalResponse:
    """Test clinical response parsing."""

    def test_empty_response_returns_parse_error(self):
        """Test empty string returns parse error."""
        result = parse_clinical_response("")
        assert result == {"parse_error": "empty response"}

    def test_raw_json_parsed(self):
        """Test raw JSON is parsed correctly."""
        data = {
            "risk_level": "high",
            "differentials": ["sepsis", "pneumonia"],
            "recommended_workup": ["CBC", "Lactate"],
        }
        result = parse_clinical_response(json.dumps(data))
        assert result["risk_level"] == "high"
        assert len(result["differentials"]) == 2

    def test_xml_delimited_json_parsed(self):
        """Test XML-delimited JSON is parsed."""
        data = {"risk_level": "critical", "narrative_summary": "CDS Advisory: urgent"}
        text = f"<analysis>{json.dumps(data)}</analysis>"
        result = parse_clinical_response(text)
        assert result["risk_level"] == "critical"

    def test_markdown_fenced_json_parsed(self):
        """Test markdown-fenced JSON is parsed."""
        data = {"risk_level": "moderate"}
        text = f"```json\n{json.dumps(data)}\n```"
        result = parse_clinical_response(text)
        assert result["risk_level"] == "moderate"

    def test_regex_fallback_risk_level(self):
        """Test regex extracts risk level."""
        result = parse_clinical_response("Risk level: CRITICAL")
        assert result["risk_level"] == "critical"
        assert result["parse_method"] == "regex"

    def test_regex_risk_level_variants(self):
        """Test regex handles different risk level formats."""
        for text, expected in [
            ("Risk: low", "low"),
            ("Risk level: moderate", "moderate"),
            ("Risk level: HIGH", "high"),
        ]:
            result = parse_clinical_response(text)
            assert result["risk_level"] == expected, f"Failed for: {text}"

    def test_unparseable_returns_error(self):
        """Test unparseable text returns error."""
        result = parse_clinical_response("no useful medical data here at all")
        assert "parse_error" in result
