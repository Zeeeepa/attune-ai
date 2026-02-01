---
description: Extending Agent Composition Patterns with Anthropic Guidelines: System architecture overview with components, data flow, and design decisions. Understand the framework internals.
---

# Extending Agent Composition Patterns with Anthropic Guidelines

**Version:** 1.0
**Created:** 2026-01-29
**Purpose:** Add Anthropic-recommended patterns to Empathy's 7 composition patterns

---

## Current Composition Patterns (7)

**Location:** `src/attune/orchestration/execution_strategies.py`

1. **Sequential** (A → B → C) - Linear pipeline
2. **Parallel** (A || B || C) - Concurrent execution
3. **Debate** (A ⇄ B ⇄ C → Synthesis) - Multi-agent deliberation
4. **Teaching** (Junior → Expert validation) - Mentor-student
5. **Refinement** (Draft → Review → Polish) - Iterative improvement
6. **Adaptive** (Classifier → Specialist) - Dynamic routing
7. **Conditional** (if X then A else B) - Branching logic

---

## Proposed Anthropic-Based Extensions (3 New Patterns)

Based on Anthropic's agent guidelines, we can add three powerful patterns:

### Pattern 8: Tool-Enhanced Agent (Anthropic: Tools > Multiple Agents)

**Concept:** Single agent with rich tool access outperforms multiple specialized agents.

**When to use:**
- Task requires multiple capabilities (read, parse, analyze, write)
- Reduced LLM calls = lower cost
- Simpler coordination than multi-agent

**Implementation:**

```python
from attune.orchestration.execution_strategies import ExecutionStrategy
from typing import Any

class ToolEnhancedStrategy(ExecutionStrategy):
    """Single agent with comprehensive tool access.

    Anthropic Pattern: Use tools over multiple agents when possible.

    Example:
        # Instead of: FileReader → Parser → Analyzer → Writer
        # Use: Single agent with [read, parse, analyze, write] tools
    """

    def __init__(self, tools: list[dict[str, Any]]):
        """Initialize with tool definitions.

        Args:
            tools: List of tool definitions in Anthropic format
                [
                    {
                        "name": "read_file",
                        "description": "Read a file from disk",
                        "input_schema": {...}
                    },
                    ...
                ]
        """
        self.tools = tools

    async def execute(
        self,
        agents: list[AgentTemplate],
        context: dict[str, Any]
    ) -> StrategyResult:
        """Execute single agent with tool access.

        Args:
            agents: Single agent (others ignored)
            context: Execution context with task

        Returns:
            Result with tool usage trace
        """
        if not agents:
            return StrategyResult(
                success=False,
                outputs=[],
                aggregated_output={},
                errors=["No agent provided"]
            )

        agent = agents[0]  # Use first agent only

        # Execute with tool access
        result = await self._execute_with_tools(
            agent=agent,
            context=context,
            tools=self.tools
        )

        return StrategyResult(
            success=result["success"],
            outputs=[AgentResult(
                agent_id=agent.agent_id,
                success=result["success"],
                output=result["output"],
                confidence=result.get("confidence", 1.0),
                duration_seconds=result.get("duration", 0.0),
            )],
            aggregated_output=result["output"],
            total_duration=result.get("duration", 0.0),
        )

    async def _execute_with_tools(
        self,
        agent: AgentTemplate,
        context: dict[str, Any],
        tools: list[dict[str, Any]]
    ) -> dict[str, Any]:
        """Execute agent with tool use enabled."""
        from attune.models import LLMClient

        client = LLMClient()

        # Agent makes tool use decisions
        response = await client.call(
            prompt=context["task"],
            tools=tools,
            tier=agent.tier,
            workflow_id=f"tool-enhanced:{agent.agent_id}",
        )

        return {
            "success": True,
            "output": response,
            "confidence": 1.0,
            "duration": response.get("duration", 0.0),
        }
```

**Example usage:**

```python
# Define tools
tools = [
    {
        "name": "read_file",
        "description": "Read a file from disk",
        "input_schema": {
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "File path"}
            },
            "required": ["path"]
        }
    },
    {
        "name": "analyze_code",
        "description": "Analyze Python code for issues",
        "input_schema": {
            "type": "object",
            "properties": {
                "code": {"type": "string", "description": "Code to analyze"}
            },
            "required": ["code"]
        }
    },
    {
        "name": "write_report",
        "description": "Write analysis report to file",
        "input_schema": {
            "type": "object",
            "properties": {
                "path": {"type": "string"},
                "content": {"type": "string"}
            },
            "required": ["path", "content"]
        }
    }
]

# Single agent with tools (cheaper than 3 agents)
strategy = ToolEnhancedStrategy(tools=tools)
agent = AgentTemplate(
    agent_id="code-analyzer",
    role="Code Analyzer",
    tier="capable",
)

result = await strategy.execute(
    agents=[agent],
    context={"task": "Analyze src/main.py and write report"}
)

# Agent autonomously:
# 1. Uses read_file tool
# 2. Uses analyze_code tool
# 3. Uses write_report tool
# All in single conversation!
```

---

### Pattern 9: Prompt-Cached Sequential (Anthropic: Efficient Caching)

**Concept:** Sequential agents that share cached context (system prompts, common data).

**When to use:**
- Multiple agents need same background information
- Large context that doesn't change (docs, code files)
- Cost optimization for repeated workflows

**Implementation:**

```python
class PromptCachedSequentialStrategy(ExecutionStrategy):
    """Sequential execution with shared cached context.

    Anthropic Pattern: Cache large unchanging contexts across agent calls.

    Example:
        # All agents share cached codebase context
        # Only task-specific prompts vary
        # Saves ~90% of prompt tokens on subsequent calls
    """

    def __init__(self, cached_context: str | None = None):
        """Initialize with optional cached context.

        Args:
            cached_context: Large unchanging context to cache
                (e.g., documentation, code files, guidelines)
        """
        self.cached_context = cached_context

    async def execute(
        self,
        agents: list[AgentTemplate],
        context: dict[str, Any]
    ) -> StrategyResult:
        """Execute agents sequentially with shared cache.

        Args:
            agents: List of agents to execute in order
            context: Execution context with task

        Returns:
            Result with cumulative outputs
        """
        from attune.models import LLMClient
        import time

        client = LLMClient()
        outputs = []
        current_output = context.get("input", {})
        start_time = time.time()

        for agent in agents:
            # Build prompt with cached context
            if self.cached_context:
                full_prompt = f"""
{self.cached_context}

---

Current task: {context['task']}
Previous output: {current_output}
"""
            else:
                full_prompt = f"{context['task']}\n\nPrevious: {current_output}"

            # Execute with caching enabled
            response = await client.call(
                prompt=full_prompt,
                system_prompt=agent.system_prompt,
                tier=agent.tier,
                workflow_id=f"cached-seq:{agent.agent_id}",
                enable_caching=True,  # Anthropic prompt caching
            )

            result = AgentResult(
                agent_id=agent.agent_id,
                success=True,
                output=response,
                confidence=1.0,
                duration_seconds=response.get("duration", 0.0),
            )

            outputs.append(result)
            current_output = response["content"]

        return StrategyResult(
            success=True,
            outputs=outputs,
            aggregated_output={"final_output": current_output},
            total_duration=time.time() - start_time,
        )
```

**Example usage:**

```python
# Load large unchanging context (cached across all agents)
with open("codebase_context.txt") as f:
    cached_context = f.read()  # 50,000 tokens of code/docs

strategy = PromptCachedSequentialStrategy(cached_context=cached_context)

agents = [
    AgentTemplate(agent_id="parser", role="Code Parser", tier="cheap"),
    AgentTemplate(agent_id="analyzer", role="Analyzer", tier="capable"),
    AgentTemplate(agent_id="recommender", role="Advisor", tier="premium"),
]

result = await strategy.execute(
    agents=agents,
    context={"task": "Review authentication flow"}
)

# Cost savings:
# - First call: 50,000 input tokens (full cost)
# - Subsequent calls: 500 input tokens (only task-specific)
# - 99% token reduction on cached portion
```

---

### Pattern 10: Delegation Chain (Anthropic: Shallow Hierarchies)

**Concept:** Coordinator delegates to specialists, specialists can delegate further (max 3 levels).

**When to use:**
- Complex tasks requiring domain expertise
- Need specialized sub-agents for specific aspects
- Maintain Anthropic's "shallow hierarchy" guideline

**Implementation:**

```python
class DelegationChainStrategy(ExecutionStrategy):
    """Hierarchical delegation with max depth enforcement.

    Anthropic Pattern: Keep agent hierarchies shallow (≤3 levels).

    Example:
        Level 1: Coordinator (analyzes task)
        Level 2: Domain specialists (security, performance, quality)
        Level 3: Sub-specialists (SQL injection, XSS, etc.)
        Level 4: ❌ NOT ALLOWED (too deep)
    """

    MAX_DEPTH = 3

    def __init__(self, max_depth: int = 3):
        """Initialize with depth limit.

        Args:
            max_depth: Maximum delegation depth (default: 3)
        """
        self.max_depth = min(max_depth, self.MAX_DEPTH)

    async def execute(
        self,
        agents: list[AgentTemplate],
        context: dict[str, Any]
    ) -> StrategyResult:
        """Execute delegation chain with depth tracking.

        Args:
            agents: Hierarchical agent structure
            context: Execution context with task

        Returns:
            Result with delegation trace
        """
        current_depth = context.get("_delegation_depth", 0)

        if current_depth >= self.max_depth:
            return StrategyResult(
                success=False,
                outputs=[],
                aggregated_output={},
                errors=[f"Max delegation depth ({self.max_depth}) exceeded"]
            )

        # Execute coordinator (first agent)
        coordinator = agents[0]

        # Coordinator analyzes and delegates
        delegation_plan = await self._plan_delegation(
            coordinator=coordinator,
            task=context["task"],
            specialists=agents[1:],  # Available specialists
        )

        # Execute delegated tasks
        results = []
        for sub_task in delegation_plan["sub_tasks"]:
            specialist_id = sub_task["specialist_id"]
            specialist = self._find_specialist(specialist_id, agents)

            if specialist:
                # Recursive delegation (with depth tracking)
                sub_context = {
                    **context,
                    "task": sub_task["task"],
                    "_delegation_depth": current_depth + 1,
                }

                sub_result = await self._execute_specialist(
                    specialist=specialist,
                    context=sub_context,
                )

                results.append(sub_result)

        # Synthesize results
        final_output = await self._synthesize_results(
            coordinator=coordinator,
            results=results,
            original_task=context["task"],
        )

        return StrategyResult(
            success=True,
            outputs=results,
            aggregated_output=final_output,
            total_duration=sum(r.duration_seconds for r in results),
        )

    async def _plan_delegation(
        self,
        coordinator: AgentTemplate,
        task: str,
        specialists: list[AgentTemplate],
    ) -> dict[str, Any]:
        """Coordinator plans delegation strategy."""
        from attune.models import LLMClient

        client = LLMClient()

        specialist_descriptions = "\n".join([
            f"- {s.agent_id}: {s.role}"
            for s in specialists
        ])

        prompt = f"""Break down this task and assign to specialists:

Task: {task}

Available specialists:
{specialist_descriptions}

Return JSON:
{{
    "sub_tasks": [
        {{"specialist_id": "...", "task": "..."}},
        ...
    ]
}}"""

        response = await client.call(
            prompt=prompt,
            tier=coordinator.tier,
            workflow_id=f"delegation:{coordinator.agent_id}",
        )

        import json
        return json.loads(response["content"])

    async def _execute_specialist(
        self,
        specialist: AgentTemplate,
        context: dict[str, Any],
    ) -> AgentResult:
        """Execute specialist agent."""
        from attune.models import LLMClient

        client = LLMClient()

        response = await client.call(
            prompt=context["task"],
            system_prompt=specialist.system_prompt,
            tier=specialist.tier,
            workflow_id=f"specialist:{specialist.agent_id}",
        )

        return AgentResult(
            agent_id=specialist.agent_id,
            success=True,
            output=response,
            confidence=1.0,
            duration_seconds=response.get("duration", 0.0),
        )

    def _find_specialist(
        self,
        specialist_id: str,
        agents: list[AgentTemplate]
    ) -> AgentTemplate | None:
        """Find specialist by ID."""
        for agent in agents:
            if agent.agent_id == specialist_id:
                return agent
        return None

    async def _synthesize_results(
        self,
        coordinator: AgentTemplate,
        results: list[AgentResult],
        original_task: str,
    ) -> dict[str, Any]:
        """Coordinator synthesizes specialist results."""
        from attune.models import LLMClient

        client = LLMClient()

        specialist_reports = "\n\n".join([
            f"## {r.agent_id}\n{r.output.get('content', '')}"
            for r in results
        ])

        prompt = f"""Synthesize these specialist reports:

Original task: {original_task}

{specialist_reports}

Provide cohesive final analysis."""

        response = await client.call(
            prompt=prompt,
            tier=coordinator.tier,
            workflow_id=f"synthesis:{coordinator.agent_id}",
        )

        return {
            "synthesis": response["content"],
            "specialist_reports": [r.output for r in results],
            "delegation_depth": len(results),
        }
```

**Example usage:**

```python
# Define hierarchy (max 3 levels)
strategy = DelegationChainStrategy(max_depth=3)

agents = [
    # Level 1: Coordinator
    AgentTemplate(
        agent_id="code-review-coordinator",
        role="Code Review Coordinator",
        tier="premium",
    ),

    # Level 2: Domain specialists
    AgentTemplate(
        agent_id="security-specialist",
        role="Security Expert",
        tier="capable",
    ),
    AgentTemplate(
        agent_id="performance-specialist",
        role="Performance Expert",
        tier="capable",
    ),
    AgentTemplate(
        agent_id="quality-specialist",
        role="Code Quality Expert",
        tier="capable",
    ),
]

result = await strategy.execute(
    agents=agents,
    context={"task": "Review src/api/auth.py for production readiness"}
)

# Execution flow:
# 1. Coordinator analyzes task → delegates to 3 specialists
# 2. Each specialist analyzes their domain
# 3. Coordinator synthesizes results
# Max depth: 2 levels (within Anthropic's guideline)
```

---

## Summary: Extended Pattern Library

| Pattern | Type | Anthropic Alignment | Use Case |
|---------|------|---------------------|----------|
| 1. Sequential | Original | ✅ Workflows | Linear pipelines |
| 2. Parallel | Original | ✅ Orchestrator | Independent tasks |
| 3. Debate | Original | ✅ Evaluator | Multi-perspective |
| 4. Teaching | Original | ✅ Evaluator | Knowledge transfer |
| 5. Refinement | Original | ✅ Evaluator | Iterative improvement |
| 6. Adaptive | Original | ✅ Orchestrator | Dynamic routing |
| 7. Conditional | Original | ✅ Orchestrator | Branching logic |
| **8. Tool-Enhanced** | **NEW** | ✅ **Tools > Agents** | **Multi-capability tasks** |
| **9. Prompt-Cached** | **NEW** | ✅ **Caching** | **Repeated workflows** |
| **10. Delegation Chain** | **NEW** | ✅ **Shallow hierarchies** | **Complex specialization** |

---

## Integration Steps

### 1. Add New Strategies to codebase

**File:** `src/attune/orchestration/execution_strategies.py`

Add the three new strategy classes after the existing 7 patterns.

### 2. Register in Strategy Factory

**File:** `src/attune/orchestration/strategy_factory.py`

```python
STRATEGY_MAP = {
    # Existing...
    "sequential": SequentialStrategy,
    "parallel": ParallelStrategy,
    "debate": DebateStrategy,
    "teaching": TeachingStrategy,
    "refinement": RefinementStrategy,
    "adaptive": AdaptiveStrategy,
    "conditional": ConditionalStrategy,

    # New Anthropic-inspired patterns
    "tool_enhanced": ToolEnhancedStrategy,
    "prompt_cached": PromptCachedSequentialStrategy,
    "delegation_chain": DelegationChainStrategy,
}
```

### 3. Update Documentation

Update `pyproject.toml` description:

```toml
description = "AI collaboration framework... dynamic agent composition (10 patterns)..."
```

### 4. Add Tests

**File:** `tests/unit/test_anthropic_patterns.py`

```python
import pytest
from attune.orchestration.execution_strategies import (
    ToolEnhancedStrategy,
    PromptCachedSequentialStrategy,
    DelegationChainStrategy,
)

@pytest.mark.asyncio
async def test_tool_enhanced_strategy():
    """Test single agent with tools."""
    # Test implementation...

@pytest.mark.asyncio
async def test_prompt_cached_sequential():
    """Test cached context sharing."""
    # Test implementation...

@pytest.mark.asyncio
async def test_delegation_chain_depth_limit():
    """Test max depth enforcement."""
    # Test implementation...
```

---

## Benefits of Extension

**Cost Optimization:**
- Pattern 8: Reduces LLM calls (1 agent vs 3+)
- Pattern 9: Saves 90%+ on cached prompts
- Pattern 10: Efficient specialization (shallow hierarchy)

**Performance:**
- Pattern 8: Single conversation (no coordination overhead)
- Pattern 9: Fast cache hits
- Pattern 10: Parallel specialist execution

**Anthropic Alignment:**
- ✅ Follows "tools > agents" principle
- ✅ Uses prompt caching effectively
- ✅ Maintains shallow hierarchies (≤3 levels)

---

## Next Steps

1. **Implement patterns** in `execution_strategies.py`
2. **Add to strategy factory** for automatic discovery
3. **Write comprehensive tests** for each pattern
4. **Update documentation** (guides, examples)
5. **Benchmark performance** vs existing patterns
6. **Create migration guide** for existing workflows

Would you like me to implement these three new patterns in the codebase?
