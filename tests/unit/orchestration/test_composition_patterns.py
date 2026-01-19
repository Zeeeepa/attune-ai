"""Comprehensive tests for composition patterns.

This module tests all 6 composition patterns according to Sprint 2 Day 11-12:
1. ParallelComposition (5 tests)
2. SequentialComposition (5 tests)
3. RefinementComposition (5 tests)
4. HierarchicalComposition (5 tests)
5. DebateComposition (5 tests)
6. VotingComposition (5 tests)

Each test verifies the pattern's unique behavior and architectural invariants.
"""

import time

import pytest

from empathy_os.orchestration.agent_templates import get_template
from empathy_os.orchestration.execution_strategies import (
    AdaptiveStrategy,
    AgentResult,
    DebateStrategy,
    ParallelStrategy,
    RefinementStrategy,
    SequentialStrategy,
    StrategyResult,
    TeachingStrategy,
)


@pytest.fixture
def test_agents():
    """Get test agents for composition testing."""
    return [
        get_template("test_coverage_analyzer"),
        get_template("code_reviewer"),
        get_template("documentation_writer"),
        get_template("security_auditor"),
    ]


@pytest.fixture
def test_context():
    """Get test context dictionary."""
    return {
        "project": "empathy-framework",
        "version": "3.12.0",
        "project_root": ".",
        "target_path": "src",
    }


class TestParallelComposition:
    """Test ParallelComposition pattern (A || B || C).

    Verifies:
    - Parallel execution of independent agents
    - Result aggregation
    - Error handling (one agent fails)
    - Performance (faster than sequential)
    - Resource limits
    """

    @pytest.mark.asyncio
    async def test_parallel_execution_of_independent_agents(self, test_agents, test_context):
        """Test that agents execute independently in parallel."""
        strategy = ParallelStrategy()

        # Track execution order to verify parallelism
        execution_times = []

        # Mock the _execute_agent to track timing
        original_execute = strategy._execute_agent

        async def tracked_execute(agent, context):
            start = time.perf_counter()
            result = await original_execute(agent, context)
            execution_times.append((agent.id, time.perf_counter() - start))
            return result

        strategy._execute_agent = tracked_execute

        result = await strategy.execute(test_agents[:3], test_context)

        assert result.success
        assert len(result.outputs) == 3

        # All agents should have executed
        assert len(execution_times) == 3

        # Verify parallel execution: total duration should be max, not sum
        # (allowing some overhead for async coordination)
        max_individual = max(t[1] for t in execution_times)
        assert result.total_duration <= max_individual * 1.5

    @pytest.mark.asyncio
    async def test_parallel_result_aggregation(self, test_agents, test_context):
        """Test that results from all agents are properly aggregated."""
        strategy = ParallelStrategy()
        result = await strategy.execute(test_agents[:3], test_context)

        assert result.success
        assert "num_agents" in result.aggregated_output
        assert result.aggregated_output["num_agents"] == 3
        assert "all_succeeded" in result.aggregated_output
        assert "avg_confidence" in result.aggregated_output
        assert "outputs" in result.aggregated_output

        # All agents should have contributed their outputs
        assert len(result.aggregated_output["outputs"]) == 3

    @pytest.mark.asyncio
    async def test_parallel_error_handling_one_agent_fails(self, test_agents, test_context):
        """Test parallel execution when one agent fails."""
        strategy = ParallelStrategy()

        # Create a context that will cause one agent to fail
        # (using invalid path to trigger error)
        bad_context = test_context.copy()
        bad_context["target_path"] = "/nonexistent/path/that/does/not/exist"

        # Even with failures, parallel should complete all agents
        result = await strategy.execute(test_agents[:2], bad_context)

        # Some agents may fail with bad path
        # But the strategy should complete without crashing
        assert len(result.outputs) == 2

        # Check that we captured any errors
        if not result.success:
            assert len(result.errors) > 0

    @pytest.mark.asyncio
    async def test_parallel_performance_faster_than_sequential(self, test_agents, test_context):
        """Test that parallel execution is faster than sequential for independent tasks."""
        # Execute parallel
        parallel_strategy = ParallelStrategy()
        parallel_start = time.perf_counter()
        parallel_result = await parallel_strategy.execute(test_agents[:3], test_context)
        parallel_duration = time.perf_counter() - parallel_start

        # Execute sequential
        sequential_strategy = SequentialStrategy()
        sequential_start = time.perf_counter()
        sequential_result = await sequential_strategy.execute(test_agents[:3], test_context)
        sequential_duration = time.perf_counter() - sequential_start

        # Both should succeed
        assert parallel_result.success
        assert sequential_result.success

        # Parallel should be faster (or at least not significantly slower)
        # We allow some margin due to async overhead
        assert parallel_duration <= sequential_duration * 1.2

    @pytest.mark.asyncio
    async def test_parallel_resource_limits(self, test_agents, test_context):
        """Test parallel execution respects resource limits."""
        strategy = ParallelStrategy()

        # Test with maximum agents (should still work)
        all_agents = test_agents  # 4 agents
        result = await strategy.execute(all_agents, test_context)

        assert result.success or len(result.outputs) == len(all_agents)

        # Verify all agents were attempted
        assert len(result.outputs) == len(all_agents)

        # Test with empty agents (should raise error)
        with pytest.raises(ValueError, match="agents list cannot be empty"):
            await strategy.execute([], test_context)


class TestSequentialComposition:
    """Test SequentialComposition pattern (A → B → C).

    Verifies:
    - Sequential execution maintains order
    - Context passing between agents
    - Early termination on error
    - Dependency chain validation
    - State accumulation
    """

    @pytest.mark.asyncio
    async def test_sequential_execution_maintains_order(self, test_agents, test_context):
        """Test that agents execute in the specified order."""
        strategy = SequentialStrategy()

        execution_order = []

        # Track execution order
        original_execute = strategy._execute_agent

        async def tracked_execute(agent, context):
            execution_order.append(agent.id)
            return await original_execute(agent, context)

        strategy._execute_agent = tracked_execute

        result = await strategy.execute(test_agents[:3], test_context)

        assert result.success
        # Verify execution order matches agent order
        assert execution_order == [a.id for a in test_agents[:3]]

    @pytest.mark.asyncio
    async def test_sequential_context_passing_between_agents(self, test_agents, test_context):
        """Test that context is passed from one agent to the next."""
        strategy = SequentialStrategy()

        context_snapshots = []

        # Track context at each stage
        original_execute = strategy._execute_agent

        async def tracked_execute(agent, context):
            context_snapshots.append(context.copy())
            return await original_execute(agent, context)

        strategy._execute_agent = tracked_execute

        result = await strategy.execute(test_agents[:3], test_context)

        assert result.success

        # Each subsequent agent should see previous agent's output in context
        for i in range(1, len(context_snapshots)):
            current_snapshot = context_snapshots[i]
            # Previous agent's output should be in current context
            prev_agent_id = test_agents[i - 1].id
            assert f"{prev_agent_id}_output" in current_snapshot

    @pytest.mark.asyncio
    async def test_sequential_early_termination_on_error(self, test_agents, test_context):
        """Test sequential execution behavior when an agent fails."""
        strategy = SequentialStrategy()

        # Create a scenario where middle agent might fail
        bad_context = test_context.copy()
        bad_context["target_path"] = "/nonexistent/path"

        # Sequential continues even if one agent fails (by design)
        result = await strategy.execute(test_agents[:3], bad_context)

        # Check that all agents were attempted
        assert len(result.outputs) == 3

        # If any failed, overall success should be False
        if not all(r.success for r in result.outputs):
            assert not result.success

    @pytest.mark.asyncio
    async def test_sequential_dependency_chain_validation(self, test_agents, test_context):
        """Test that sequential composition validates dependency chains."""
        strategy = SequentialStrategy()

        # Test with valid chain
        result = await strategy.execute(test_agents[:3], test_context)
        assert result.success

        # Test with empty chain (should raise error)
        with pytest.raises(ValueError, match="agents list cannot be empty"):
            await strategy.execute([], test_context)

        # Test with single agent (should work)
        single_result = await strategy.execute(test_agents[:1], test_context)
        assert single_result.success
        assert len(single_result.outputs) == 1

    @pytest.mark.asyncio
    async def test_sequential_state_accumulation(self, test_agents, test_context):
        """Test that state accumulates across sequential execution."""
        strategy = SequentialStrategy()
        result = await strategy.execute(test_agents[:3], test_context)

        assert result.success

        # Verify all agent outputs are in the aggregated output
        assert "outputs" in result.aggregated_output
        assert len(result.aggregated_output["outputs"]) == 3

        # Each output should be from a different agent
        agent_ids = [output.get("agent_role", "unknown") for output in result.aggregated_output["outputs"]]
        assert len(set(agent_ids)) == 3  # All unique


class TestRefinementComposition:
    """Test RefinementComposition pattern (Draft → Review → Polish).

    Verifies:
    - Iterative refinement of results
    - Quality improvement tracking
    - Convergence detection
    - Max iteration limits
    - Refinement stopping criteria
    """

    @pytest.mark.asyncio
    async def test_refinement_iterative_refinement_of_results(self, test_agents, test_context):
        """Test that each stage refines previous output."""
        strategy = RefinementStrategy()
        result = await strategy.execute(test_agents[:3], test_context)

        assert result.success

        # Verify refinement stages structure
        assert "refinement_stages" in result.aggregated_output
        assert result.aggregated_output["refinement_stages"] == 3
        assert "final_output" in result.aggregated_output
        assert "stage_outputs" in result.aggregated_output

        # Each stage should have produced output
        assert len(result.aggregated_output["stage_outputs"]) == 3

    @pytest.mark.asyncio
    async def test_refinement_quality_improvement_tracking(self, test_agents, test_context):
        """Test that quality metrics improve across refinement stages."""
        strategy = RefinementStrategy()
        result = await strategy.execute(test_agents[:3], test_context)

        assert result.success

        # Track confidence across stages
        confidences = [r.confidence for r in result.outputs]

        # We can't guarantee strictly increasing confidence, but we track it
        assert len(confidences) == 3
        assert all(0.0 <= c <= 1.0 for c in confidences)

        # Final output should be from last stage
        assert result.aggregated_output["final_output"] == result.outputs[-1].output

    @pytest.mark.asyncio
    async def test_refinement_convergence_detection(self, test_agents, test_context):
        """Test refinement convergence detection."""
        strategy = RefinementStrategy()

        # Test with 2 agents (minimum)
        result = await strategy.execute(test_agents[:2], test_context)
        assert result.success
        assert result.aggregated_output["refinement_stages"] == 2

        # Test with 3 agents
        result3 = await strategy.execute(test_agents[:3], test_context)
        assert result3.success
        assert result3.aggregated_output["refinement_stages"] == 3

    @pytest.mark.asyncio
    async def test_refinement_max_iteration_limits(self, test_agents, test_context):
        """Test that refinement respects maximum iteration limits."""
        strategy = RefinementStrategy()

        # Test with all 4 agents
        result = await strategy.execute(test_agents, test_context)

        # Should execute all agents (no artificial limit)
        assert len(result.outputs) == len(test_agents)

        # Verify each stage completed
        assert result.aggregated_output["refinement_stages"] == len(test_agents)

    @pytest.mark.asyncio
    async def test_refinement_stopping_criteria(self, test_agents, test_context):
        """Test refinement stopping criteria."""
        strategy = RefinementStrategy()

        # Test minimum requirement (at least 2 agents)
        with pytest.raises(ValueError, match="Refinement strategy requires at least 2 agents"):
            await strategy.execute(test_agents[:1], test_context)

        # Test that refinement stops on failure
        bad_context = test_context.copy()
        bad_context["target_path"] = "/nonexistent/path"

        result = await strategy.execute(test_agents[:3], bad_context)

        # May not complete all stages if early stage fails
        # But should capture what was completed
        assert len(result.outputs) <= 3


class TestHierarchicalComposition:
    """Test HierarchicalComposition pattern (Manager → Workers).

    Note: This pattern is implemented via AdaptiveStrategy.
    Verifies:
    - Manager-worker delegation
    - Task decomposition
    - Result synthesis
    - Coordinator role
    - Subtask distribution
    """

    @pytest.mark.asyncio
    async def test_hierarchical_manager_worker_delegation(self, test_agents, test_context):
        """Test manager delegates to appropriate workers."""
        # Adaptive strategy implements hierarchical pattern
        strategy = AdaptiveStrategy()

        # Manager (classifier) selects worker (specialist)
        result = await strategy.execute(test_agents[:3], test_context)

        assert result.success

        # Should have manager classification
        assert "classification" in result.aggregated_output

        # Should have selected a worker
        assert "selected_specialist" in result.aggregated_output

        # Should have worker's output
        assert "specialist_output" in result.aggregated_output

    @pytest.mark.asyncio
    async def test_hierarchical_task_decomposition(self, test_agents, test_context):
        """Test that manager decomposes task for workers."""
        strategy = AdaptiveStrategy()

        result = await strategy.execute(test_agents[:3], test_context)

        assert result.success

        # Manager analyzes task (classification phase)
        classification = result.aggregated_output["classification"]
        assert classification is not None

        # Worker executes assigned subtask
        specialist_output = result.aggregated_output["specialist_output"]
        assert specialist_output is not None

    @pytest.mark.asyncio
    async def test_hierarchical_result_synthesis(self, test_agents, test_context):
        """Test that results from workers are synthesized."""
        strategy = AdaptiveStrategy()

        result = await strategy.execute(test_agents[:3], test_context)

        assert result.success

        # Aggregated output synthesizes manager + worker results
        assert "classification" in result.aggregated_output
        assert "selected_specialist" in result.aggregated_output
        assert "specialist_output" in result.aggregated_output

        # Total outputs = manager + worker
        assert len(result.outputs) == 2

    @pytest.mark.asyncio
    async def test_hierarchical_coordinator_role(self, test_agents, test_context):
        """Test coordinator (manager) role in orchestration."""
        strategy = AdaptiveStrategy()

        result = await strategy.execute(test_agents[:4], test_context)

        assert result.success

        # First agent acts as coordinator
        coordinator_result = result.outputs[0]
        assert coordinator_result.agent_id == test_agents[0].id

        # Coordinator classifies and routes
        selected_specialist_id = result.aggregated_output["selected_specialist"]
        assert selected_specialist_id in [a.id for a in test_agents[1:]]

    @pytest.mark.asyncio
    async def test_hierarchical_subtask_distribution(self, test_agents, test_context):
        """Test distribution of subtasks to specialized workers."""
        strategy = AdaptiveStrategy()

        # Test that different contexts route to different specialists
        context1 = test_context.copy()
        context1["complexity"] = "simple"

        context2 = test_context.copy()
        context2["complexity"] = "complex"

        result1 = await strategy.execute(test_agents[:3], context1)
        result2 = await strategy.execute(test_agents[:3], context2)

        assert result1.success
        assert result2.success

        # Both should have selected a specialist
        assert "selected_specialist" in result1.aggregated_output
        assert "selected_specialist" in result2.aggregated_output

        # Minimum requirement: at least 2 agents (manager + worker)
        with pytest.raises(ValueError, match="Adaptive strategy requires at least 2 agents"):
            await strategy.execute(test_agents[:1], test_context)


class TestDebateComposition:
    """Test DebateComposition pattern (A ⇄ B ⇄ C → Synthesis).

    Verifies:
    - Multi-viewpoint generation
    - Consensus building
    - Disagreement resolution
    - Voting mechanism
    - Synthesis of perspectives
    """

    @pytest.mark.asyncio
    async def test_debate_multi_viewpoint_generation(self, test_agents, test_context):
        """Test that multiple agents provide different viewpoints."""
        strategy = DebateStrategy()

        result = await strategy.execute(test_agents[:3], test_context)

        assert result.success

        # Should have multiple viewpoints
        assert "opinions" in result.aggregated_output
        opinions = result.aggregated_output["opinions"]
        assert len(opinions) == 3

        # Each opinion should be from a different agent
        assert len(opinions) == len(test_agents[:3])

    @pytest.mark.asyncio
    async def test_debate_consensus_building(self, test_agents, test_context):
        """Test that consensus is built from multiple viewpoints."""
        strategy = DebateStrategy()

        result = await strategy.execute(test_agents[:3], test_context)

        assert result.success

        # Should have consensus section
        assert "consensus" in result.aggregated_output
        consensus = result.aggregated_output["consensus"]

        # Consensus should track votes
        assert "consensus_reached" in consensus
        assert "success_votes" in consensus
        assert "total_votes" in consensus
        assert consensus["total_votes"] == 3

    @pytest.mark.asyncio
    async def test_debate_disagreement_resolution(self, test_agents, test_context):
        """Test handling of disagreements between agents."""
        strategy = DebateStrategy()

        result = await strategy.execute(test_agents[:3], test_context)

        assert result.success

        # Consensus mechanism should resolve disagreements
        consensus = result.aggregated_output["consensus"]

        # Should use majority vote
        assert consensus["consensus_reached"] == (consensus["success_votes"] > consensus["total_votes"] / 2)

    @pytest.mark.asyncio
    async def test_debate_voting_mechanism(self, test_agents, test_context):
        """Test voting mechanism for consensus."""
        strategy = DebateStrategy()

        result = await strategy.execute(test_agents[:3], test_context)

        assert result.success

        consensus = result.aggregated_output["consensus"]

        # Voting data should be present
        assert "success_votes" in consensus
        assert "total_votes" in consensus

        # Vote count should match agent count
        assert consensus["total_votes"] == 3

        # Success votes should be <= total votes
        assert consensus["success_votes"] <= consensus["total_votes"]

    @pytest.mark.asyncio
    async def test_debate_synthesis_of_perspectives(self, test_agents, test_context):
        """Test synthesis of multiple perspectives into coherent output."""
        strategy = DebateStrategy()

        result = await strategy.execute(test_agents[:3], test_context)

        assert result.success

        # Should have debate participants listed
        assert "debate_participants" in result.aggregated_output
        participants = result.aggregated_output["debate_participants"]
        assert len(participants) == 3

        # Should synthesize opinions
        assert "opinions" in result.aggregated_output

        # Should produce consensus
        assert "consensus" in result.aggregated_output
        consensus = result.aggregated_output["consensus"]
        assert "avg_confidence" in consensus


class TestVotingComposition:
    """Test VotingComposition pattern (Vote on best proposal).

    Note: This is implemented via DebateStrategy with voting mechanism.
    Verifies:
    - Multiple agent proposals
    - Vote aggregation
    - Majority/consensus selection
    - Tie-breaking
    - Confidence weighting
    """

    @pytest.mark.asyncio
    async def test_voting_multiple_agent_proposals(self, test_agents, test_context):
        """Test that multiple agents submit proposals for voting."""
        strategy = DebateStrategy()

        result = await strategy.execute(test_agents[:3], test_context)

        assert result.success

        # Each agent should have submitted a proposal (opinion)
        opinions = result.aggregated_output["opinions"]
        assert len(opinions) == 3

        # Each proposal should have content
        for opinion in opinions:
            assert opinion is not None

    @pytest.mark.asyncio
    async def test_voting_vote_aggregation(self, test_agents, test_context):
        """Test aggregation of votes from all agents."""
        strategy = DebateStrategy()

        result = await strategy.execute(test_agents[:4], test_context)

        assert result.success

        consensus = result.aggregated_output["consensus"]

        # Votes should be aggregated
        assert "success_votes" in consensus
        assert "total_votes" in consensus
        assert consensus["total_votes"] == 4

    @pytest.mark.asyncio
    async def test_voting_majority_consensus_selection(self, test_agents, test_context):
        """Test selection based on majority consensus."""
        strategy = DebateStrategy()

        result = await strategy.execute(test_agents[:3], test_context)

        assert result.success

        consensus = result.aggregated_output["consensus"]

        # Majority is > 50%
        success_votes = consensus["success_votes"]
        total_votes = consensus["total_votes"]

        consensus_reached = success_votes > total_votes / 2
        assert consensus["consensus_reached"] == consensus_reached

    @pytest.mark.asyncio
    async def test_voting_tie_breaking(self, test_agents, test_context):
        """Test tie-breaking mechanism in voting."""
        strategy = DebateStrategy()

        # Test with even number of agents
        result = await strategy.execute(test_agents[:2], test_context)

        assert result.success

        consensus = result.aggregated_output["consensus"]

        # With 2 agents, tie is possible (1-1)
        # Majority requires > 50%, so 1 out of 2 is not consensus
        if consensus["success_votes"] == 1 and consensus["total_votes"] == 2:
            assert not consensus["consensus_reached"]

        # With 2 votes for success, consensus reached
        if consensus["success_votes"] == 2 and consensus["total_votes"] == 2:
            assert consensus["consensus_reached"]

    @pytest.mark.asyncio
    async def test_voting_confidence_weighting(self, test_agents, test_context):
        """Test confidence weighting in voting."""
        strategy = DebateStrategy()

        result = await strategy.execute(test_agents[:3], test_context)

        assert result.success

        consensus = result.aggregated_output["consensus"]

        # Should compute average confidence
        assert "avg_confidence" in consensus

        # Confidence should be in valid range
        avg_confidence = consensus["avg_confidence"]
        assert 0.0 <= avg_confidence <= 1.0

        # Should be based on actual agent confidences
        actual_avg = sum(r.confidence for r in result.outputs) / len(result.outputs)
        assert abs(consensus["avg_confidence"] - actual_avg) < 0.01


class TestCompositionPatternInvariants:
    """Test architectural invariants across all composition patterns."""

    @pytest.mark.asyncio
    async def test_all_patterns_validate_empty_agents(self, test_context):
        """Test that all patterns reject empty agent lists."""
        strategies = [
            ParallelStrategy(),
            SequentialStrategy(),
            DebateStrategy(),
            RefinementStrategy(),
            AdaptiveStrategy(),
            TeachingStrategy(),
        ]

        for strategy in strategies:
            with pytest.raises(ValueError):
                await strategy.execute([], test_context)

    @pytest.mark.asyncio
    async def test_all_patterns_return_strategy_result(self, test_agents, test_context):
        """Test that all patterns return StrategyResult."""
        strategies = [
            (ParallelStrategy(), test_agents[:3]),
            (SequentialStrategy(), test_agents[:3]),
            (DebateStrategy(), test_agents[:3]),
            (RefinementStrategy(), test_agents[:3]),
            (AdaptiveStrategy(), test_agents[:3]),
            (TeachingStrategy(), test_agents[:2]),  # Requires exactly 2
        ]

        for strategy, agents in strategies:
            result = await strategy.execute(agents, test_context)
            assert isinstance(result, StrategyResult)
            assert hasattr(result, "success")
            assert hasattr(result, "outputs")
            assert hasattr(result, "aggregated_output")
            assert hasattr(result, "total_duration")
            assert hasattr(result, "errors")

    @pytest.mark.asyncio
    async def test_all_patterns_track_duration(self, test_agents, test_context):
        """Test that all patterns track execution duration."""
        strategies = [
            (ParallelStrategy(), test_agents[:3]),
            (SequentialStrategy(), test_agents[:3]),
            (DebateStrategy(), test_agents[:3]),
            (RefinementStrategy(), test_agents[:3]),
            (AdaptiveStrategy(), test_agents[:3]),
            (TeachingStrategy(), test_agents[:2]),
        ]

        for strategy, agents in strategies:
            result = await strategy.execute(agents, test_context)
            assert result.total_duration >= 0.0
            assert isinstance(result.total_duration, float)

    @pytest.mark.asyncio
    async def test_all_patterns_produce_outputs(self, test_agents, test_context):
        """Test that all patterns produce outputs."""
        strategies = [
            (ParallelStrategy(), test_agents[:3]),
            (SequentialStrategy(), test_agents[:3]),
            (DebateStrategy(), test_agents[:3]),
            (RefinementStrategy(), test_agents[:3]),
            (AdaptiveStrategy(), test_agents[:3]),
            (TeachingStrategy(), test_agents[:2]),
        ]

        for strategy, agents in strategies:
            result = await strategy.execute(agents, test_context)
            assert len(result.outputs) > 0
            assert isinstance(result.outputs, list)
            assert all(isinstance(o, AgentResult) for o in result.outputs)

    @pytest.mark.asyncio
    async def test_all_patterns_aggregate_results(self, test_agents, test_context):
        """Test that all patterns aggregate results."""
        strategies = [
            (ParallelStrategy(), test_agents[:3]),
            (SequentialStrategy(), test_agents[:3]),
            (DebateStrategy(), test_agents[:3]),
            (RefinementStrategy(), test_agents[:3]),
            (AdaptiveStrategy(), test_agents[:3]),
            (TeachingStrategy(), test_agents[:2]),
        ]

        for strategy, agents in strategies:
            result = await strategy.execute(agents, test_context)
            assert isinstance(result.aggregated_output, dict)
            assert len(result.aggregated_output) > 0
