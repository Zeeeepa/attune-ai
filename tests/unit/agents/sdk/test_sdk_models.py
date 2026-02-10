"""Tests for SDK data models.

Tests serialization round-trips, defaults, and enum handling.

Copyright 2026 Smart-AI-Memory
Licensed under Apache 2.0
"""

from attune.agents.sdk.sdk_models import SDKAgentResult, SDKExecutionMode


class TestSDKExecutionMode:
    """Tests for SDKExecutionMode enum."""

    def test_tools_only_value(self) -> None:
        assert SDKExecutionMode.TOOLS_ONLY.value == "tools_only"

    def test_full_sdk_value(self) -> None:
        assert SDKExecutionMode.FULL_SDK.value == "full_sdk"


class TestSDKAgentResult:
    """Tests for SDKAgentResult dataclass."""

    def test_default_values(self) -> None:
        """Test that defaults are sensible."""
        result = SDKAgentResult(agent_id="test-01", role="Tester")
        assert result.success is True
        assert result.tier_used == "cheap"
        assert result.mode == SDKExecutionMode.TOOLS_ONLY
        assert result.findings == {}
        assert result.score == 0.0
        assert result.cost == 0.0
        assert result.escalated is False
        assert result.sdk_used is False
        assert result.error is None

    def test_to_dict_round_trip(self) -> None:
        """Test serialization and deserialization produce identical records."""
        original = SDKAgentResult(
            agent_id="test-02",
            role="Security Auditor",
            success=True,
            tier_used="capable",
            mode=SDKExecutionMode.FULL_SDK,
            findings={"coverage": 85.0},
            score=85.0,
            confidence=0.9,
            cost=0.05,
            execution_time_ms=1500.0,
            escalated=True,
            sdk_used=True,
            error=None,
        )
        data = original.to_dict()
        restored = SDKAgentResult.from_dict(data)

        assert restored.agent_id == original.agent_id
        assert restored.role == original.role
        assert restored.success == original.success
        assert restored.tier_used == original.tier_used
        assert restored.mode == original.mode
        assert restored.findings == original.findings
        assert restored.score == original.score
        assert restored.confidence == original.confidence
        assert restored.cost == original.cost
        assert restored.escalated == original.escalated
        assert restored.sdk_used == original.sdk_used
        assert restored.error == original.error

    def test_from_dict_with_missing_fields(self) -> None:
        """Test deserialization handles missing fields gracefully."""
        minimal = {"agent_id": "test-03", "role": "Runner"}
        result = SDKAgentResult.from_dict(minimal)
        assert result.agent_id == "test-03"
        assert result.role == "Runner"
        assert result.success is False  # default when missing
        assert result.mode == SDKExecutionMode.TOOLS_ONLY

    def test_from_dict_with_invalid_mode(self) -> None:
        """Test that invalid mode string falls back to TOOLS_ONLY."""
        data = {
            "agent_id": "test-04",
            "role": "Tester",
            "mode": "nonexistent_mode",
        }
        result = SDKAgentResult.from_dict(data)
        assert result.mode == SDKExecutionMode.TOOLS_ONLY

    def test_to_dict_includes_error(self) -> None:
        """Test that error field is serialized."""
        result = SDKAgentResult(
            agent_id="test-err",
            role="Failing Agent",
            success=False,
            error="Connection timeout",
        )
        data = result.to_dict()
        assert data["error"] == "Connection timeout"
        assert data["success"] is False

    def test_to_dict_mode_serialized_as_string(self) -> None:
        """Test that mode enum is serialized as its string value."""
        result = SDKAgentResult(
            agent_id="test-mode",
            role="Tester",
            mode=SDKExecutionMode.FULL_SDK,
        )
        data = result.to_dict()
        assert data["mode"] == "full_sdk"
