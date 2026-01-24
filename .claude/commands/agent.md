---
name: agent
description: Agent hub - create, manage, and invoke specialized agents
category: hub
aliases: [agents]
tags: [agents, teams, orchestration, hub]
version: "1.0"
---

# Agent Management

Create, configure, and orchestrate specialized agents.

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

## Routing

Based on selection:

| Selection | Command | Description |
|-----------|---------|-------------|
| Create new agent | `/create-agent` | Define agent with markdown format |
| Create agent team | `/create-team` | Assemble multi-agent workflow |
| List agents | `/agents list` | Show all available agents |
| Invoke agent | `/agents invoke` | Run specific agent |

## Quick Access

- `/create-agent "name"` - Create new agent
- `/create-team "team-name"` - Create agent team
- `/agents list` - List all agents
- `/agents invoke architect` - Invoke architect agent

## Agent Types

| Agent | Role | Use Case |
|-------|------|----------|
| **architect** | System design | Architecture decisions |
| **code-reviewer** | Quality review | Code review tasks |
| **security-reviewer** | Security audit | Security-sensitive code |
| **empathy-specialist** | Level 4+ anticipation | Complex user needs |

## Agent Format

Agents are defined in markdown with YAML frontmatter:

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

Detailed instructions in markdown...
```

## Team Composition

Teams combine agents for complex workflows:

```yaml
team: code-review-team
agents:
  - code-reviewer     # Quality check
  - security-reviewer # Security audit
  - architect        # Architecture review
workflow: sequential
```

## When to Use Each

**Use `/create-agent` when:**

- Need specialized capability
- Recurring task pattern
- Want consistent behavior
- Building reusable workflows

**Use `/create-team` when:**

- Complex multi-step task
- Multiple perspectives needed
- Collaborative workflow
- Quality gates required

**Use `/agents list` when:**

- Exploring capabilities
- Finding right agent
- Checking agent status

**Use `/agents invoke` when:**

- Know which agent needed
- Running specific workflow
- Testing agent behavior
