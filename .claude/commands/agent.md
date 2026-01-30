---
name: agent
description: Agent hub - create, manage, and invoke specialized agents
category: hub
aliases: [agents]
tags: [agents, teams, orchestration, hub]
version: "2.0"
---

# Agent Management

**Aliases:** `/agents`

Create, configure, and orchestrate specialized agents.

## Quick Examples

```bash
/agent                      # Interactive menu
/agent "create code review" # Create new agent
/agent "list available"     # List agents
```

## Discovery

```yaml
Question:
  header: "Task"
  question: "What would you like to do with agents?"
  options:
    - label: "Create new agent"
      description: "Define a new specialized agent"
    - label: "Create agent team"
      description: "Assemble agents for collaborative work"
    - label: "List agents"
      description: "View available agents and their capabilities"
    - label: "Invoke agent"
      description: "Run a specific agent for a task"
```

---

## Create New Agent

Define a new specialized agent in markdown format.

**Tell me:**

- Agent name and purpose
- What tasks it should handle
- Any special tools or permissions needed

**I will:**

1. Create agent markdown file in `agents_md/`
2. Define appropriate:
   - Role and description
   - Tool permissions
   - Model tier (cheap/capable/premium)
   - Empathy level (1-5)
3. Add detailed instructions
4. Register in the agent registry

**Agent file format:**

```markdown
---
name: my-agent
description: What this agent does
role: specialist
tools: [Read, Grep, Glob]
model_tier: capable
empathy_level: 3
---

# Agent Instructions

Detailed instructions for the agent...
```

---

## Create Agent Team

Assemble multiple agents for collaborative work using one of **10 composition patterns**.

**Tell me:**

- Team purpose
- What agents should be included
- Workflow type (or let me auto-select based on task)

**I will:**

1. Select appropriate agents
2. Choose optimal composition pattern (from 10 available)
3. Set up handoff points
4. Configure aggregation of results

**Available Composition Patterns:**

| Pattern                            | When to Use               | Example                                 |
| ---------------------------------- | ------------------------- | --------------------------------------- |
| **sequential**                     | Step-by-step pipeline     | Parse → Analyze → Report                |
| **parallel**                       | Independent tasks         | Security + Quality + Performance audits |
| **debate**                         | Multiple perspectives     | 3 reviewers discuss approach            |
| **teaching**                       | Expert validates junior   | Draft (cheap) → Expert review           |
| **refinement**                     | Iterative improvement     | Draft → Review → Polish                 |
| **adaptive**                       | Dynamic routing           | Classifier → Specialist                 |
| **conditional**                    | Branch by condition       | If bug → Debugger, else Reviewer        |
| **tool_enhanced** (NEW)            | Single agent + tools      | File reader with analysis tools         |
| **prompt_cached_sequential** (NEW) | Shared large context      | 3 agents using same docs/codebase       |
| **delegation_chain** (NEW)         | Hierarchical coordination | Coordinator → Specialists (≤3 levels)   |

**NEW** = Anthropic-inspired patterns added in v5.1.4

**Team composition examples:**

```yaml
# Comprehensive code review (parallel pattern)
team: code-review-team
agents:
  - code-reviewer       # Quality check
  - security-reviewer   # Security audit
  - quality-validator   # Metrics analysis
workflow: parallel      # Run all simultaneously

# Debug and fix (sequential pattern)
team: debug-fix-team
agents:
  - debugger            # Find root cause
  - test-writer         # Write regression test
  - refactorer          # Clean up fix
workflow: sequential    # One after another

# Feature planning (delegation_chain pattern - NEW)
team: planning-team
agents:
  - planner             # Coordinator (delegates tasks)
  - architect           # Technical design specialist
  - performance-analyst # Scalability specialist
workflow: delegation_chain  # Hierarchical coordination

# Single agent with tools (tool_enhanced pattern - NEW)
team: file-analyzer
agents:
  - code-reviewer       # Single agent
tools:
  - read_file          # File reading
  - analyze_ast        # Code parsing
workflow: tool_enhanced  # Tools over multiple agents

# Large codebase analysis (prompt_cached_sequential pattern - NEW)
team: codebase-review
agents:
  - security-reviewer   # Security check
  - quality-validator   # Quality check
  - performance-analyst # Performance check
cached_context: |
  # Large codebase documentation (cached across all agents)
  [10,000 lines of architecture docs, API specs, etc.]
workflow: prompt_cached_sequential  # Shared cached context
```

**Learn more:** See [Anthropic Agent Patterns Guide](../../docs/architecture/anthropic-agent-patterns.md)

---

## List Agents

View all available agents and their capabilities.

**I will:**

1. Scan `agents_md/` directory
2. Load agent registry
3. Display:
   - Agent name and role
   - Description
   - Tools available
   - Model tier
   - Empathy level

**Available agents:**

All agents use **Socratic questioning** to guide discovery rather than just providing answers.

| Agent                    | Role               | Use Case                              |
| ------------------------ | ------------------ | ------------------------------------- |
| **architect**            | System design      | Architecture decisions, tech choices  |
| **code-reviewer**        | Quality review     | Code review, design patterns          |
| **debugger**             | Bug investigation  | Root cause analysis, hypothesis tests |
| **empathy-specialist**   | Level 4-5 empathy  | Complex user needs, trust building    |
| **performance-analyst**  | Optimization       | Bottlenecks, profiling, memory issues |
| **planner**              | Requirements       | Sprint planning, scope discovery      |
| **quality-validator**    | Code quality       | Complexity, naming, documentation     |
| **refactorer**           | Code improvement   | Clean code, pattern application       |
| **security-reviewer**    | Security audit     | Vulnerabilities, attack scenarios     |
| **test-writer**          | Test design        | Edge cases, test strategy, TDD        |

---

## Invoke Agent

Run a specific agent for a task.

**Tell me:**

- Which agent to invoke
- The task or input for the agent

**I will:**

1. Load the agent configuration
2. Set up the appropriate context
3. Run the agent with your input
4. Return the agent's output

---

## Cross-Hub Agent Integration

Agents can also be invoked from relevant hubs:

| Hub          | Related Agents                                  |
| ------------ | ----------------------------------------------- |
| `/dev`       | debugger, code-reviewer, refactorer             |
| `/testing`   | test-writer, quality-validator                  |
| `/workflows` | (runs automated multi-stage workflows)          |
| `/plan`      | planner, architect                              |
| `/docs`      | code-reviewer (documentation review)            |
| `/release`   | security-reviewer, quality-validator            |

## When to Use This Hub Directly

Use `/agent` when you want to:

- Create a new custom agent
- Compose an agent team for collaborative work
- Invoke a specific agent by name
- See all available agents and their capabilities

## Related Hubs

- `/workflows` - Run automated AI workflows (security-audit, bug-predict, etc.)
- `/plan` - Development planning (uses planner, architect)
- `/dev` - Development tools (uses debugger, code-reviewer)
- `/testing` - Testing workflows (uses test-writer)
- `/context` - Context and memory management
- `/learning` - Pattern learning
