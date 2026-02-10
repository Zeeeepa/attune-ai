"""Tests for Phase 2 MCP tools: healthcare_fhir_bundle and healthcare_waveform_analyze.

Validates that the 2 new tools are properly registered alongside the original 7,
that their schemas are correct, and that the handlers produce expected results
when CDSTeam and numpy/scipy dependencies are mocked.

Copyright 2026 Smart-AI-Memory
Licensed under Apache 2.0
"""

import json
import sys
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

# Ensure MCP server is importable
sys.path.insert(0, "attune-healthcare-plugin/mcp")

from healthcare_server import HealthcareMCPServer


@pytest.fixture
def server() -> HealthcareMCPServer:
    """Create an MCP server instance."""
    return HealthcareMCPServer()


# =========================================================================
# 1. Tool count regression (was 7, now 9)
# =========================================================================


class TestToolCountRegression:
    """Verify the server now exposes exactly 9 tools after Phase 2."""

    def test_server_has_9_tools(self, server: HealthcareMCPServer) -> None:
        """Test server registers 9 tools after Phase 2 additions."""
        tools = server.get_tool_list()
        assert len(tools) == 9, (
            f"Expected 9 tools after Phase 2, got {len(tools)}. "
            f"Tool names: {[t['name'] for t in tools]}"
        )

    def test_original_7_tools_still_present(self, server: HealthcareMCPServer) -> None:
        """Regression check: all 7 original tools remain registered."""
        tool_names = {t["name"] for t in server.get_tool_list()}
        original_tools = {
            "healthcare_list_protocols",
            "healthcare_load_protocol",
            "healthcare_analyze",
            "healthcare_check_compliance",
            "healthcare_predict_trajectory",
            "healthcare_ecg_analyze",
            "healthcare_cds_assess",
        }
        missing = original_tools - tool_names
        assert not missing, f"Original tools missing after Phase 2: {missing}"


# =========================================================================
# 2. healthcare_fhir_bundle schema
# =========================================================================


class TestFHIRBundleToolSchema:
    """Verify healthcare_fhir_bundle tool definition and input schema."""

    def test_fhir_bundle_tool_is_defined(self, server: HealthcareMCPServer) -> None:
        """Test healthcare_fhir_bundle tool is present in tool registry."""
        assert "healthcare_fhir_bundle" in server.tools

    def test_fhir_bundle_tool_name_matches(self, server: HealthcareMCPServer) -> None:
        """Test tool definition has matching name field."""
        tool = server.tools["healthcare_fhir_bundle"]
        assert tool["name"] == "healthcare_fhir_bundle"

    def test_fhir_bundle_has_description(self, server: HealthcareMCPServer) -> None:
        """Test tool has a non-empty description."""
        tool = server.tools["healthcare_fhir_bundle"]
        assert "description" in tool
        assert len(tool["description"]) > 0
        assert "FHIR" in tool["description"]

    def test_fhir_bundle_required_fields(self, server: HealthcareMCPServer) -> None:
        """Test healthcare_fhir_bundle requires patient_id, sensor_data, protocol_name."""
        schema = server.tools["healthcare_fhir_bundle"]["input_schema"]
        required = set(schema["required"])
        assert required == {"patient_id", "sensor_data", "protocol_name"}

    def test_fhir_bundle_has_optional_ecg_metrics(self, server: HealthcareMCPServer) -> None:
        """Test ecg_metrics is in schema properties but not required."""
        schema = server.tools["healthcare_fhir_bundle"]["input_schema"]
        assert "ecg_metrics" in schema["properties"]
        assert "ecg_metrics" not in schema["required"]

    def test_fhir_bundle_has_optional_decision_id(self, server: HealthcareMCPServer) -> None:
        """Test decision_id is in schema properties but not required."""
        schema = server.tools["healthcare_fhir_bundle"]["input_schema"]
        assert "decision_id" in schema["properties"]
        assert "decision_id" not in schema["required"]

    def test_fhir_bundle_schema_property_types(self, server: HealthcareMCPServer) -> None:
        """Test schema property types are correct."""
        props = server.tools["healthcare_fhir_bundle"]["input_schema"]["properties"]
        assert props["patient_id"]["type"] == "string"
        assert props["sensor_data"]["type"] == "string"
        assert props["protocol_name"]["type"] == "string"
        assert props["ecg_metrics"]["type"] == "object"
        assert props["decision_id"]["type"] == "string"


# =========================================================================
# 3. healthcare_waveform_analyze schema
# =========================================================================


class TestWaveformAnalyzeToolSchema:
    """Verify healthcare_waveform_analyze tool definition and input schema."""

    def test_waveform_analyze_tool_is_defined(self, server: HealthcareMCPServer) -> None:
        """Test healthcare_waveform_analyze tool is present in tool registry."""
        assert "healthcare_waveform_analyze" in server.tools

    def test_waveform_analyze_tool_name_matches(self, server: HealthcareMCPServer) -> None:
        """Test tool definition has matching name field."""
        tool = server.tools["healthcare_waveform_analyze"]
        assert tool["name"] == "healthcare_waveform_analyze"

    def test_waveform_analyze_has_description(self, server: HealthcareMCPServer) -> None:
        """Test tool has a non-empty description mentioning waveform."""
        tool = server.tools["healthcare_waveform_analyze"]
        assert "description" in tool
        assert len(tool["description"]) > 0
        assert "waveform" in tool["description"].lower()

    def test_waveform_analyze_required_fields(self, server: HealthcareMCPServer) -> None:
        """Test healthcare_waveform_analyze requires only signal."""
        schema = server.tools["healthcare_waveform_analyze"]["input_schema"]
        required = set(schema["required"])
        assert required == {"signal"}

    def test_waveform_analyze_signal_is_array(self, server: HealthcareMCPServer) -> None:
        """Test signal property is defined as array of numbers."""
        props = server.tools["healthcare_waveform_analyze"]["input_schema"]["properties"]
        assert props["signal"]["type"] == "array"
        assert props["signal"]["items"]["type"] == "number"

    def test_waveform_analyze_sampling_rate_is_integer(self, server: HealthcareMCPServer) -> None:
        """Test sampling_rate property is defined as integer with default 360."""
        props = server.tools["healthcare_waveform_analyze"]["input_schema"]["properties"]
        assert props["sampling_rate"]["type"] == "integer"
        assert props["sampling_rate"]["default"] == 360

    def test_waveform_analyze_sampling_rate_not_required(
        self, server: HealthcareMCPServer
    ) -> None:
        """Test sampling_rate is optional (not in required list)."""
        schema = server.tools["healthcare_waveform_analyze"]["input_schema"]
        assert "sampling_rate" not in schema["required"]


# =========================================================================
# 4. healthcare_fhir_bundle handler
# =========================================================================


class TestFHIRBundleHandler:
    """Test healthcare_fhir_bundle handler with mocked CDSTeam."""

    @staticmethod
    def _make_mock_decision(patient_id: str = "pt-fhir-001") -> MagicMock:
        """Create a mock CDSDecision with the fields used by decision_to_fhir_bundle."""
        decision = MagicMock()
        decision.patient_id = patient_id
        decision.overall_risk = "moderate"
        decision.confidence = 0.85
        decision.alerts = ["Heart rate elevated"]
        decision.recommendations = ["Monitor vitals every 15 min"]
        decision.protocol_compliance = {
            "protocol_name": "cardiac",
            "current_vitals": {"hr": 110, "systolic_bp": 85},
        }
        decision.trajectory = {}
        decision.ecg_analysis = None
        decision.clinical_reasoning = MagicMock()
        decision.clinical_reasoning.narrative_summary = "Patient shows moderate risk."
        decision.clinical_reasoning.differentials = ["tachycardia", "hypovolemia"]
        decision.clinical_reasoning.recommended_workup = ["CBC", "BMP"]
        decision.clinical_reasoning.risk_level = "moderate"
        decision.clinical_reasoning.confidence = 0.85
        decision.to_dict.return_value = {"patient_id": patient_id, "overall_risk": "moderate"}
        return decision

    @pytest.mark.asyncio
    async def test_fhir_bundle_returns_success(self, server: HealthcareMCPServer) -> None:
        """Test FHIR bundle handler returns success with bundle payload."""
        mock_decision = self._make_mock_decision()

        mock_team_cls = MagicMock()
        mock_team_instance = mock_team_cls.return_value
        mock_team_instance.assess = AsyncMock(return_value=mock_decision)

        mock_bundle = {
            "resourceType": "Bundle",
            "type": "collection",
            "entry": [
                {"resource": {"resourceType": "RiskAssessment"}},
                {"resource": {"resourceType": "ClinicalImpression"}},
                {"resource": {"resourceType": "DiagnosticReport"}},
                {"resource": {"resourceType": "AuditEvent"}},
            ],
        }
        mock_to_bundle = MagicMock(return_value=mock_bundle)

        # Patch the lazy imports inside _fhir_bundle
        mock_cds_team_module = MagicMock()
        mock_cds_team_module.CDSTeam = mock_team_cls
        mock_fhir_module = MagicMock()
        mock_fhir_module.decision_to_fhir_bundle = mock_to_bundle

        with patch.dict("sys.modules", {
            "attune.agents.healthcare.cds_team": mock_cds_team_module,
            "attune.healthcare.fhir.resources": mock_fhir_module,
        }):
            result = await server.call_tool("healthcare_fhir_bundle", {
                "patient_id": "pt-fhir-001",
                "sensor_data": json.dumps({"hr": 110, "systolic_bp": 85}),
                "protocol_name": "cardiac",
            })

        assert result["success"] is True
        assert result["bundle"]["resourceType"] == "Bundle"
        assert result["resource_count"] == 4
        assert "RiskAssessment" in result["resource_types"]
        assert "AuditEvent" in result["resource_types"]

    @pytest.mark.asyncio
    async def test_fhir_bundle_passes_decision_id(self, server: HealthcareMCPServer) -> None:
        """Test decision_id argument is forwarded to decision_to_fhir_bundle."""
        mock_decision = self._make_mock_decision()

        mock_team_cls = MagicMock()
        mock_team_instance = mock_team_cls.return_value
        mock_team_instance.assess = AsyncMock(return_value=mock_decision)

        mock_to_bundle = MagicMock(return_value={
            "resourceType": "Bundle",
            "type": "collection",
            "entry": [],
        })

        mock_cds_team_module = MagicMock()
        mock_cds_team_module.CDSTeam = mock_team_cls
        mock_fhir_module = MagicMock()
        mock_fhir_module.decision_to_fhir_bundle = mock_to_bundle

        with patch.dict("sys.modules", {
            "attune.agents.healthcare.cds_team": mock_cds_team_module,
            "attune.healthcare.fhir.resources": mock_fhir_module,
        }):
            await server.call_tool("healthcare_fhir_bundle", {
                "patient_id": "pt-fhir-002",
                "sensor_data": json.dumps({"hr": 80}),
                "protocol_name": "sepsis",
                "decision_id": "custom-uuid-123",
            })

        mock_to_bundle.assert_called_once()
        _, kwargs = mock_to_bundle.call_args
        assert kwargs.get("decision_id") == "custom-uuid-123"

    @pytest.mark.asyncio
    async def test_fhir_bundle_invalid_json_returns_error(
        self, server: HealthcareMCPServer
    ) -> None:
        """Test FHIR bundle handler with invalid sensor_data JSON returns error."""
        result = await server.call_tool("healthcare_fhir_bundle", {
            "patient_id": "pt-fhir-003",
            "sensor_data": "not valid json {{",
            "protocol_name": "cardiac",
        })
        assert result["success"] is False
        assert "error" in result
        assert "JSON" in result["error"]

    @pytest.mark.asyncio
    async def test_fhir_bundle_unwraps_vitals_format(
        self, server: HealthcareMCPServer
    ) -> None:
        """Test FHIR bundle handler unwraps {"vitals": {...}} format."""
        mock_decision = self._make_mock_decision()

        mock_team_cls = MagicMock()
        mock_team_instance = mock_team_cls.return_value
        mock_team_instance.assess = AsyncMock(return_value=mock_decision)

        mock_to_bundle = MagicMock(return_value={
            "resourceType": "Bundle",
            "type": "collection",
            "entry": [],
        })

        mock_cds_team_module = MagicMock()
        mock_cds_team_module.CDSTeam = mock_team_cls
        mock_fhir_module = MagicMock()
        mock_fhir_module.decision_to_fhir_bundle = mock_to_bundle

        with patch.dict("sys.modules", {
            "attune.agents.healthcare.cds_team": mock_cds_team_module,
            "attune.healthcare.fhir.resources": mock_fhir_module,
        }):
            await server.call_tool("healthcare_fhir_bundle", {
                "patient_id": "pt-fhir-004",
                "sensor_data": json.dumps({"vitals": {"hr": 80, "systolic_bp": 120}}),
                "protocol_name": "cardiac",
            })

        # Verify CDSTeam.assess received unwrapped vitals
        mock_team_instance.assess.assert_called_once()
        _, kwargs = mock_team_instance.assess.call_args
        assert kwargs["sensor_data"] == {"hr": 80, "systolic_bp": 120}


# =========================================================================
# 5. healthcare_waveform_analyze handler
# =========================================================================


class TestWaveformAnalyzeHandler:
    """Test healthcare_waveform_analyze handler with mocked numpy/scipy."""

    @staticmethod
    def _make_waveform_mocks(
        features_dict: dict | None = None,
        nurse_summary: str = "Heart rate 72 bpm. QRS normal width (95ms).",
    ) -> tuple:
        """Create mock ECGWaveformAnalyzer and numpy for waveform tests.

        Args:
            features_dict: Override for WaveformFeatures.to_dict().
            nurse_summary: Override for format_for_nurse().

        Returns:
            Tuple of (mock_ecg_signal_module, mock_numpy_module).
        """
        if features_dict is None:
            features_dict = {
                "qrs_duration_ms": 95.0,
                "qt_interval_ms": 380.0,
                "qtc_interval_ms": 410.0,
                "st_deviation_mv": 0.02,
                "p_wave_present": True,
                "t_wave_morphology": "normal",
                "heart_rate_bpm": 72.0,
                "signal_quality": 0.85,
                "r_peak_count": 10,
                "waveform_summary": "",
            }

        mock_features = MagicMock()
        mock_features.to_dict.return_value = features_dict

        mock_analyzer_cls = MagicMock()
        mock_analyzer_instance = mock_analyzer_cls.return_value
        mock_analyzer_instance.analyze_signal.return_value = mock_features
        mock_analyzer_instance.format_for_nurse.return_value = nurse_summary

        mock_ecg_module = MagicMock()
        mock_ecg_module.ECGWaveformAnalyzer = mock_analyzer_cls

        mock_np = MagicMock()
        mock_np.array.return_value = MagicMock()
        mock_np.float64 = "float64"

        return mock_ecg_module, mock_np, mock_analyzer_cls

    @pytest.mark.asyncio
    async def test_waveform_analyze_returns_features(
        self, server: HealthcareMCPServer
    ) -> None:
        """Test waveform analysis returns extracted features when dependencies are present."""
        mock_ecg_module, mock_np, _ = self._make_waveform_mocks()

        with patch.dict("sys.modules", {
            "attune.healthcare.waveform.ecg_signal": mock_ecg_module,
            "numpy": mock_np,
        }):
            result = await server.call_tool("healthcare_waveform_analyze", {
                "signal": [0.1, 0.5, 1.2, 0.8, 0.3] * 100,
                "sampling_rate": 360,
            })

        assert result["success"] is True
        assert "nurse_summary" in result
        assert result["qrs_duration_ms"] == 95.0
        assert result["heart_rate_bpm"] == 72.0
        assert result["signal_quality"] == 0.85
        assert result["p_wave_present"] is True

    @pytest.mark.asyncio
    async def test_waveform_analyze_invalid_signal_empty_list(
        self, server: HealthcareMCPServer
    ) -> None:
        """Test waveform analysis with empty signal array returns error."""
        result = await server.call_tool("healthcare_waveform_analyze", {
            "signal": [],
        })
        assert result["success"] is False
        assert "error" in result
        assert "signal" in result["error"].lower()

    @pytest.mark.asyncio
    async def test_waveform_analyze_invalid_signal_none(
        self, server: HealthcareMCPServer
    ) -> None:
        """Test waveform analysis with None signal returns error."""
        result = await server.call_tool("healthcare_waveform_analyze", {
            "signal": None,
        })
        assert result["success"] is False
        assert "error" in result

    @pytest.mark.asyncio
    async def test_waveform_analyze_invalid_signal_not_list(
        self, server: HealthcareMCPServer
    ) -> None:
        """Test waveform analysis with non-list signal returns error."""
        result = await server.call_tool("healthcare_waveform_analyze", {
            "signal": "not a list",
        })
        assert result["success"] is False
        assert "error" in result

    @pytest.mark.asyncio
    async def test_waveform_analyze_missing_signal(
        self, server: HealthcareMCPServer
    ) -> None:
        """Test waveform analysis with no signal key returns error."""
        result = await server.call_tool("healthcare_waveform_analyze", {})
        assert result["success"] is False
        assert "error" in result

    @pytest.mark.asyncio
    async def test_waveform_analyze_default_sampling_rate(
        self, server: HealthcareMCPServer
    ) -> None:
        """Test waveform analysis uses 360 Hz default when sampling_rate omitted."""
        mock_ecg_module, mock_np, mock_analyzer_cls = self._make_waveform_mocks(
            features_dict={
                "qrs_duration_ms": 100.0,
                "qt_interval_ms": 390.0,
                "qtc_interval_ms": 415.0,
                "st_deviation_mv": 0.0,
                "p_wave_present": True,
                "t_wave_morphology": "normal",
                "heart_rate_bpm": 75.0,
                "signal_quality": 0.9,
                "r_peak_count": 8,
                "waveform_summary": "",
            },
            nurse_summary="Summary text.",
        )

        with patch.dict("sys.modules", {
            "attune.healthcare.waveform.ecg_signal": mock_ecg_module,
            "numpy": mock_np,
        }):
            await server.call_tool("healthcare_waveform_analyze", {
                "signal": [0.1, 0.2, 0.3] * 50,
            })

        # Verify analyzer was constructed with default sampling_rate=360
        mock_analyzer_cls.assert_called_once_with(sampling_rate=360)

    @pytest.mark.asyncio
    async def test_waveform_analyze_import_error_returns_helpful_message(
        self, server: HealthcareMCPServer
    ) -> None:
        """Test waveform analysis returns install instructions when numpy/scipy missing."""
        # Simulate the lazy import inside _waveform_analyze raising ImportError.
        # The method does:
        #   from attune.healthcare.waveform.ecg_signal import ECGWaveformAnalyzer
        # If that raises ImportError, the handler returns an error dict with
        # install instructions mentioning numpy and scipy.
        import builtins

        _real_import = builtins.__import__

        def _block_ecg_signal_import(name: str, *args, **kwargs):
            if name == "attune.healthcare.waveform.ecg_signal":
                raise ImportError("No module named 'numpy'")
            return _real_import(name, *args, **kwargs)

        with patch("builtins.__import__", side_effect=_block_ecg_signal_import):
            result = await server.call_tool("healthcare_waveform_analyze", {
                "signal": [0.1, 0.2, 0.3] * 50,
            })

        assert result["success"] is False
        assert "numpy" in result["error"].lower() or "scipy" in result["error"].lower()
