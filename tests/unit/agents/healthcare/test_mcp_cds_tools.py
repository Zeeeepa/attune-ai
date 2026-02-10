"""Tests for MCP CDS tool definitions and handlers.

Copyright 2026 Smart-AI-Memory
Licensed under Apache 2.0
"""

import json
import sys

import pytest

# Ensure MCP server is importable
sys.path.insert(0, "attune-healthcare-plugin/mcp")

from healthcare_server import HealthcareMCPServer


@pytest.fixture
def server():
    """Create an MCP server instance."""
    return HealthcareMCPServer()


class TestToolDefinitions:
    """Test tool registration and definitions."""

    def test_server_has_9_tools(self, server):
        """Test server registers 9 tools."""
        tools = server.get_tool_list()
        assert len(tools) == 9

    def test_existing_5_tools_still_present(self, server):
        """Regression check: 5 original tools are still present."""
        tool_names = {t["name"] for t in server.get_tool_list()}
        original_tools = {
            "healthcare_list_protocols",
            "healthcare_load_protocol",
            "healthcare_analyze",
            "healthcare_check_compliance",
            "healthcare_predict_trajectory",
        }
        assert original_tools.issubset(tool_names)

    def test_new_ecg_tool_defined(self, server):
        """Test healthcare_ecg_analyze tool is defined."""
        assert "healthcare_ecg_analyze" in server.tools
        tool = server.tools["healthcare_ecg_analyze"]
        schema = tool["input_schema"]
        assert "ecg_metrics" in schema["properties"]
        assert "ecg_metrics" in schema["required"]

    def test_new_cds_tool_defined(self, server):
        """Test healthcare_cds_assess tool is defined."""
        assert "healthcare_cds_assess" in server.tools
        tool = server.tools["healthcare_cds_assess"]
        schema = tool["input_schema"]
        assert "patient_id" in schema["required"]
        assert "sensor_data" in schema["required"]
        assert "protocol_name" in schema["required"]
        # Optional fields should exist but not be required
        assert "ecg_metrics" in schema["properties"]
        assert "patient_context" in schema["properties"]


class TestECGAnalyzeTool:
    """Test healthcare_ecg_analyze handler."""

    @pytest.mark.asyncio
    async def test_ecg_analyze_success(self, server):
        """Test ECG analysis with valid metrics."""
        result = await server.call_tool("healthcare_ecg_analyze", {
            "ecg_metrics": {"hr_mean": 80, "pvc_burden_pct": 1.0, "rr_std_ms": 80},
        })
        assert result["success"]
        assert result["rhythm_classification"] == "normal_sinus"
        assert result["heart_rate"] == 80
        assert "score" in result

    @pytest.mark.asyncio
    async def test_ecg_analyze_tachycardia(self, server):
        """Test ECG analysis detects tachycardia."""
        result = await server.call_tool("healthcare_ecg_analyze", {
            "ecg_metrics": {"hr_mean": 130, "pvc_burden_pct": 0.5, "rr_std_ms": 40},
        })
        assert result["success"]
        assert "SEVERE_TACHYCARDIA" in result["clinical_flags"]

    @pytest.mark.asyncio
    async def test_ecg_analyze_missing_metrics(self, server):
        """Test ECG analysis fails with missing metrics."""
        result = await server.call_tool("healthcare_ecg_analyze", {})
        assert not result["success"]
        assert "error" in result

    @pytest.mark.asyncio
    async def test_ecg_analyze_with_patient_context(self, server):
        """Test ECG analysis accepts patient context."""
        result = await server.call_tool("healthcare_ecg_analyze", {
            "ecg_metrics": {"hr_mean": 80, "pvc_burden_pct": 1.0, "rr_std_ms": 80},
            "patient_context": {"age": 65, "sex": "M", "medications": ["Metoprolol"]},
        })
        assert result["success"]


class TestCDSAssessTool:
    """Test healthcare_cds_assess handler."""

    @pytest.mark.asyncio
    async def test_cds_assess_basic(self, server):
        """Test basic CDS assessment."""
        result = await server.call_tool("healthcare_cds_assess", {
            "patient_id": "mcp-test-001",
            "sensor_data": json.dumps({"hr": 80, "systolic_bp": 120}),
            "protocol_name": "cardiac",
        })
        assert result["success"]
        assert result["patient_id"] == "mcp-test-001"
        assert "overall_risk" in result
        assert "clinical_reasoning" in result

    @pytest.mark.asyncio
    async def test_cds_assess_with_ecg(self, server):
        """Test CDS assessment with ECG metrics."""
        result = await server.call_tool("healthcare_cds_assess", {
            "patient_id": "mcp-test-002",
            "sensor_data": json.dumps({"hr": 145, "systolic_bp": 82}),
            "protocol_name": "cardiac",
            "ecg_metrics": {"hr_mean": 145, "pvc_burden_pct": 3.5, "rr_std_ms": 40},
        })
        assert result["success"]
        assert result["ecg_analysis"] is not None
        assert result["ecg_analysis"]["rhythm_classification"] == "sinus_tachycardia"

    @pytest.mark.asyncio
    async def test_cds_assess_invalid_json(self, server):
        """Test CDS assessment with invalid sensor_data JSON."""
        result = await server.call_tool("healthcare_cds_assess", {
            "patient_id": "mcp-test-003",
            "sensor_data": "not valid json",
            "protocol_name": "cardiac",
        })
        assert not result["success"]
        assert "error" in result

    @pytest.mark.asyncio
    async def test_cds_assess_wrapped_vitals(self, server):
        """Test CDS assessment with wrapped vitals format."""
        result = await server.call_tool("healthcare_cds_assess", {
            "patient_id": "mcp-test-004",
            "sensor_data": json.dumps({"vitals": {"hr": 80, "systolic_bp": 120}}),
            "protocol_name": "cardiac",
        })
        assert result["success"]


class TestUnknownTool:
    """Test handling of unknown tool names."""

    @pytest.mark.asyncio
    async def test_unknown_tool_returns_error(self, server):
        """Test unknown tool name returns error."""
        result = await server.call_tool("healthcare_nonexistent", {})
        assert not result["success"]
        assert "Unknown tool" in result["error"]
