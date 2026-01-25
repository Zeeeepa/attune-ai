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

Assemble multiple agents for collaborative work.

**Tell me:**

- Team purpose
- What agents should be included
- Workflow type (sequential, parallel, or custom)

**I will:**

1. Select appropriate agents
2. Define the workflow
3. Set up handoff points
4. Configure aggregation of results

**Team composition example:**

```yaml
team: code-review-team
agents:
  - code-reviewer     # Quality check
  - security-reviewer # Security audit
  - architect        # Architecture review
workflow: sequential
```

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

| Agent                  | Role            | Use Case                |
| ---------------------- | --------------- | ----------------------- |
| **architect**          | System design   | Architecture decisions  |
| **code-reviewer**      | Quality review  | Code review tasks       |
| **security-reviewer**  | Security audit  | Security-sensitive code |
| **empathy-specialist** | Level 4+ work   | Complex user needs      |

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

## When NOT to Use This Hub

| If you need...        | Use instead |
| --------------------- | ----------- |
| Debug code            | `/dev`      |
| Run tests             | `/testing`  |
| Plan implementation   | `/workflow` |
| Manage context/memory | `/context`  |

## Related Hubs

- `/workflow` - Development workflows
- `/context` - Context and memory management
- `/learning` - Pattern learning
