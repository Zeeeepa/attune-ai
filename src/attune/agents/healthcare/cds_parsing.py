"""Response parsing for Healthcare CDS Agent Team.

Multi-strategy parsing for LLM responses from ECG and clinical reasoning agents.
Healthcare-specific regex patterns for vital signs, rhythm, and risk extraction.

Copyright 2026 Smart-AI-Memory
Licensed under Apache 2.0
"""

from __future__ import annotations

import json
import re
from typing import Any


def parse_ecg_response(text: str) -> dict[str, Any]:
    """Parse ECG analysis response from LLM using multiple strategies.

    Tries in order:
    1. XML-delimited (<analysis>...</analysis>)
    2. Markdown-fenced JSON (```json...```)
    3. Raw JSON (starts with {)
    4. Healthcare-specific regex extraction (last resort)

    Never returns None — always returns a dict.

    Args:
        text: Raw response text from LLM

    Returns:
        Parsed dict with ECG findings
    """
    if not text or not text.strip():
        return {"parse_error": "empty response"}

    text = text.strip()

    # Strategy 1: XML delimiters
    xml_match = re.search(r"<analysis>([\s\S]*?)</analysis>", text)
    if xml_match:
        try:
            return json.loads(xml_match.group(1).strip())
        except json.JSONDecodeError:
            pass

    # Strategy 2: Markdown-fenced JSON
    md_match = re.search(r"```(?:json)?\s*([\s\S]*?)```", text)
    if md_match:
        try:
            return json.loads(md_match.group(1).strip())
        except json.JSONDecodeError:
            pass

    # Strategy 3: Raw JSON
    if text.startswith("{"):
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            pass

    # Strategy 4: Healthcare-specific regex extraction
    result: dict[str, Any] = {}

    # Heart rate patterns
    hr_match = re.search(
        r"(?:heart\s*rate|HR)[:\s]+(\d+(?:\.\d+)?)\s*(?:bpm)?", text, re.IGNORECASE
    )
    if hr_match:
        result["heart_rate"] = float(hr_match.group(1))

    # Rhythm classification
    rhythm_patterns = [
        (r"normal\s+sinus\s+rhythm", "normal_sinus"),
        (r"sinus\s+tachycardia", "sinus_tachycardia"),
        (r"sinus\s+bradycardia", "sinus_bradycardia"),
        (r"atrial\s+fibrillation|a[\-\s]?fib", "possible_afib"),
        (r"frequent\s+(?:PVC|premature\s+ventricular)", "frequent_pvcs"),
    ]
    for pattern, classification in rhythm_patterns:
        if re.search(pattern, text, re.IGNORECASE):
            result["rhythm_classification"] = classification
            break

    # PVC burden
    pvc_match = re.search(
        r"PVC\s+burden[:\s]+(\d+(?:\.\d+)?)\s*%", text, re.IGNORECASE
    )
    if pvc_match:
        result["pvc_burden_pct"] = float(pvc_match.group(1))

    # HRV / SDNN
    hrv_match = re.search(
        r"(?:HRV|SDNN)[:\s]+(\d+(?:\.\d+)?)\s*(?:ms)?", text, re.IGNORECASE
    )
    if hrv_match:
        result["hrv_sdnn"] = float(hrv_match.group(1))

    # Score
    score_match = re.search(
        r"(?:score|health\s*score)[:\s]+(\d+(?:\.\d+)?)", text, re.IGNORECASE
    )
    if score_match:
        result["score"] = float(score_match.group(1))

    if result:
        result["parse_method"] = "regex"
        return result

    return {"parse_error": "no parseable content", "raw_text": text[:500]}


def parse_clinical_response(text: str) -> dict[str, Any]:
    """Parse clinical reasoning response from LLM using multiple strategies.

    Tries in order:
    1. XML-delimited (<analysis>...</analysis>)
    2. Markdown-fenced JSON (```json...```)
    3. Raw JSON (starts with {)
    4. Healthcare-specific regex extraction (last resort)

    Never returns None — always returns a dict.

    Args:
        text: Raw response text from LLM

    Returns:
        Parsed dict with clinical reasoning findings
    """
    if not text or not text.strip():
        return {"parse_error": "empty response"}

    text = text.strip()

    # Strategy 1: XML delimiters
    xml_match = re.search(r"<analysis>([\s\S]*?)</analysis>", text)
    if xml_match:
        try:
            return json.loads(xml_match.group(1).strip())
        except json.JSONDecodeError:
            pass

    # Strategy 2: Markdown-fenced JSON
    md_match = re.search(r"```(?:json)?\s*([\s\S]*?)```", text)
    if md_match:
        try:
            return json.loads(md_match.group(1).strip())
        except json.JSONDecodeError:
            pass

    # Strategy 3: Raw JSON
    if text.startswith("{"):
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            pass

    # Strategy 4: Healthcare-specific regex extraction
    result: dict[str, Any] = {}

    # Risk level
    risk_match = re.search(
        r"(?:risk\s*level|risk)[:\s]+(low|moderate|high|critical)",
        text,
        re.IGNORECASE,
    )
    if risk_match:
        result["risk_level"] = risk_match.group(1).lower()

    # Differentials (bulleted or numbered lists after "differential" keyword)
    diff_section = re.search(
        r"(?:differential|consider)[:\s]*((?:[\-\*\d\.]+\s+.+\n?)+)",
        text,
        re.IGNORECASE,
    )
    if diff_section:
        items = re.findall(r"[\-\*\d\.]+\s+(.+)", diff_section.group(1))
        result["differentials"] = [item.strip() for item in items]

    # Workup recommendations
    workup_section = re.search(
        r"(?:workup|recommend|order)[:\s]*((?:[\-\*\d\.]+\s+.+\n?)+)",
        text,
        re.IGNORECASE,
    )
    if workup_section:
        items = re.findall(r"[\-\*\d\.]+\s+(.+)", workup_section.group(1))
        result["recommended_workup"] = [item.strip() for item in items]

    # Narrative (first sentence or paragraph)
    narrative_match = re.search(r"(?:summary|assessment)[:\s]+(.+?)(?:\n|$)", text, re.IGNORECASE)
    if narrative_match:
        result["narrative_summary"] = narrative_match.group(1).strip()

    if result:
        result["parse_method"] = "regex"
        return result

    return {"parse_error": "no parseable content", "raw_text": text[:500]}
