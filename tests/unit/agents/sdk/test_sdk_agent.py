"""Tests for SDKAgent.

Tests tier escalation, graceful degradation when SDK is not installed,
cost tracking, and persistent state integration.

Copyright 2026 Smart-AI-Memory
Licensed under Apache 2.0
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any
from unittest.mock import MagicMock

from attune.agents.sdk.sdk_agent import SDKAgent
from attune.agents.sdk.sdk_models import SDKAgentResult, SDKExecutionMode
from attune.agents.state.store import AgentStateStore


class TestSDKAgentDefaults:
    """Tests for SDKAgent initialization and defaults."""

    def test_default_agent_id_generated(self) -> None:
        """Test that a unique ID is generated when none is provided."""
        agent = SDKAgent(role="Test Agent")
        assert agent.agent_id.startswith("sdk-agent-")
        assert len(agent.agent_id) > len("sdk-agent-")

    def test_explicit_agent_id(self) -> None:
        """Test that an explicit ID is preserved."""
        agent = SDKAgent(agent_id="my-agent", role="Test Agent")
        assert agent.agent_id == "my-agent"

    def test_default_tier_is_cheap(self) -> None:
        """Test that initial tier is CHEAP."""
        agent = SDKAgent(role="Tester")
        assert agent.current_tier.value == "cheap"

    def test_default_mode_is_tools_only(self) -> None:
        """Test that default execution mode is TOOLS_ONLY."""
        agent = SDKAgent(role="Tester")
        assert agent.mode == SDKExecutionMode.TOOLS_ONLY

    def test_cost_starts_at_zero(self) -> None:
        """Test that cost starts at zero."""
        agent = SDKAgent(role="Tester")
        assert agent.total_cost == 0.0
        assert agent.total_tokens == 0


class TestSDKAgentTierEscalation:
    """Tests for progressive tier escalation."""

    def test_process_returns_result_without_llm(self) -> None:
        """Test that process returns a result even without LLM client."""
        agent = SDKAgent(role="No-LLM Agent")
        agent.llm_client = None  # Ensure no LLM

        result = agent.process({"query": "test"})

        assert isinstance(result, SDKAgentResult)
        assert result.agent_id == agent.agent_id
        assert result.role == "No-LLM Agent"
        # Without an LLM, _execute_tier returns empty response -> failure
        # -> escalation -> still failure at all tiers
        assert result.escalated is True

    def test_successful_execution_no_escalation(self) -> None:
        """Test that successful CHEAP execution avoids escalation."""
        agent = SDKAgent(role="Quick Agent")

        # Mock _execute_tier to succeed on first call
        call_count = 0

        def mock_execute(input_data: dict, tier: Any) -> tuple[bool, dict]:
            nonlocal call_count
            call_count += 1
            return True, {"score": 90.0, "confidence": 0.9, "result": "ok"}

        agent._execute_tier = mock_execute  # type: ignore[assignment]
        result = agent.process({"query": "test"})

        assert result.success is True
        assert result.escalated is False
        assert result.tier_used == "cheap"
        assert call_count == 1

    def test_escalation_to_capable(self) -> None:
        """Test escalation from CHEAP to CAPABLE."""
        agent = SDKAgent(role="Escalating Agent")
        tiers_tried: list[str] = []

        def mock_execute(input_data: dict, tier: Any) -> tuple[bool, dict]:
            tiers_tried.append(tier.value)
            if tier.value == "cheap":
                return False, {"error": "too complex"}
            return True, {"score": 80.0, "confidence": 0.8}

        agent._execute_tier = mock_execute  # type: ignore[assignment]
        result = agent.process({"query": "test"})

        assert result.success is True
        assert result.escalated is True
        assert result.tier_used == "capable"
        assert tiers_tried == ["cheap", "capable"]

    def test_escalation_to_premium(self) -> None:
        """Test escalation through all tiers."""
        agent = SDKAgent(role="Premium Agent")
        tiers_tried: list[str] = []

        def mock_execute(input_data: dict, tier: Any) -> tuple[bool, dict]:
            tiers_tried.append(tier.value)
            if tier.value == "premium":
                return True, {"score": 95.0, "confidence": 0.95}
            return False, {"error": "needs upgrade"}

        agent._execute_tier = mock_execute  # type: ignore[assignment]
        result = agent.process({"query": "complex"})

        assert result.success is True
        assert result.escalated is True
        assert result.tier_used == "premium"
        assert tiers_tried == ["cheap", "capable", "premium"]

    def test_all_tiers_fail(self) -> None:
        """Test that failure at all tiers produces failed result."""
        agent = SDKAgent(role="Failing Agent")

        def mock_execute(input_data: dict, tier: Any) -> tuple[bool, dict]:
            return False, {"error": "always fails"}

        agent._execute_tier = mock_execute  # type: ignore[assignment]
        result = agent.process({"query": "impossible"})

        assert result.success is False
        assert result.escalated is True
        assert result.tier_used == "premium"
        assert result.error == "always fails"


class TestSDKAgentStateIntegration:
    """Tests for persistent state store integration."""

    def test_process_records_state_on_success(self, tmp_path: Path) -> None:
        """Test that successful execution is recorded in state store."""
        store = AgentStateStore(storage_dir=str(tmp_path))
        agent = SDKAgent(
            agent_id="stateful-agent",
            role="Stateful",
            state_store=store,
        )

        def mock_execute(input_data: dict, tier: Any) -> tuple[bool, dict]:
            return True, {"score": 90.0, "confidence": 0.9}

        agent._execute_tier = mock_execute  # type: ignore[assignment]
        agent.process({"query": "test"})

        state = store.get_agent_state("stateful-agent")
        assert state is not None
        assert state.total_executions == 1
        assert state.successful_executions == 1
        assert state.execution_history[0].status == "completed"

    def test_process_records_state_on_failure(self, tmp_path: Path) -> None:
        """Test that failed execution is recorded in state store."""
        store = AgentStateStore(storage_dir=str(tmp_path))
        agent = SDKAgent(
            agent_id="failing-stateful",
            role="Failing",
            state_store=store,
        )

        def mock_execute(input_data: dict, tier: Any) -> tuple[bool, dict]:
            return False, {"error": "always fails"}

        agent._execute_tier = mock_execute  # type: ignore[assignment]
        agent.process({"query": "test"})

        state = store.get_agent_state("failing-stateful")
        assert state is not None
        assert state.total_executions == 1
        assert state.failed_executions == 1
        assert state.execution_history[0].status == "failed"

    def test_process_works_without_state_store(self) -> None:
        """Test that process works when state_store is None."""
        agent = SDKAgent(role="Stateless", state_store=None)

        def mock_execute(input_data: dict, tier: Any) -> tuple[bool, dict]:
            return True, {"score": 80.0}

        agent._execute_tier = mock_execute  # type: ignore[assignment]
        result = agent.process({"query": "test"})
        assert result.success is True


class TestSDKAgentHeartbeat:
    """Tests for Redis heartbeat integration."""

    def test_heartbeat_called_when_redis_available(self) -> None:
        """Test that heartbeat is registered when Redis is provided."""
        mock_redis = MagicMock()
        agent = SDKAgent(role="Heart Agent", redis_client=mock_redis)

        agent._register_heartbeat(status="running", task="Testing")

        mock_redis.hset.assert_called_once()
        mock_redis.expire.assert_called_once()

    def test_heartbeat_noop_without_redis(self) -> None:
        """Test that heartbeat is a no-op without Redis."""
        agent = SDKAgent(role="No Redis")
        # Should not raise
        agent._register_heartbeat(status="running", task="Testing")

    def test_heartbeat_handles_redis_error(self) -> None:
        """Test that Redis errors don't crash the agent."""
        mock_redis = MagicMock()
        mock_redis.hset.side_effect = ConnectionError("Redis down")
        agent = SDKAgent(role="Resilient", redis_client=mock_redis)

        # Should not raise
        agent._register_heartbeat(status="running", task="Testing")


class TestSDKAgentGracefulDegradation:
    """Tests for graceful degradation when SDK is not installed."""

    def test_sdk_not_available_uses_fallback(self) -> None:
        """Test that missing SDK still allows agent to function."""
        agent = SDKAgent(
            role="Fallback Agent",
            mode=SDKExecutionMode.FULL_SDK,
        )
        # Force no LLM client to test the pure fallback path
        agent.llm_client = None
        text, meta = agent._call_sdk_query("test prompt", agent.current_tier)
        assert text == ""
        assert meta.get("sdk") is False

    def test_execute_tier_handles_empty_response(self) -> None:
        """Test that empty LLM response is handled gracefully."""
        agent = SDKAgent(role="Empty Response")
        agent.llm_client = None

        success, findings = agent._execute_tier({"data": "test"}, agent.current_tier)
        assert success is False
        assert "error" in findings

    def test_execute_tier_parses_json_response(self) -> None:
        """Test that JSON responses are parsed correctly."""
        agent = SDKAgent(role="JSON Agent")

        # Mock _call_sdk_query to return valid JSON
        json_response = json.dumps({"score": 95.0, "issues": []})

        def mock_query(prompt: str, tier: Any) -> tuple[str, dict]:
            return json_response, {"model": "test", "sdk": False}

        agent._call_sdk_query = mock_query  # type: ignore[assignment]

        success, findings = agent._execute_tier({"data": "test"}, agent.current_tier)
        assert success is True
        assert findings["score"] == 95.0

    def test_execute_tier_handles_non_json_response(self) -> None:
        """Test that non-JSON responses are captured as raw text."""
        agent = SDKAgent(role="Text Agent")

        def mock_query(prompt: str, tier: Any) -> tuple[str, dict]:
            return "This is not JSON", {"model": "test", "sdk": False}

        agent._call_sdk_query = mock_query  # type: ignore[assignment]

        success, findings = agent._execute_tier({"data": "test"}, agent.current_tier)
        assert success is True
        assert findings["raw_response"] == "This is not JSON"
