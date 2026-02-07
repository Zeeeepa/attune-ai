---
name: agent
description: Create and manage custom AI agents
category: hub
aliases: [agents]
tags: [agent, custom, multi-agent, orchestration]
version: "1.0.0"
question:
  header: "Agent Hub"
  question: "What would you like to do with agents?"
  multiSelect: false
  options:
    - label: "Create a new agent"
      description: "Define a new specialized agent with role and tools"
    - label: "List agents"
      description: "Show all available agents and their capabilities"
    - label: "Run agent team"
      description: "Execute a multi-agent collaboration"
    - label: "Release prep"
      description: "Run the release readiness agent team (4 agents)"
---

# agent

Create and manage custom AI agents and multi-agent teams.

## Quick Shortcuts

| Shortcut | Action |
| -------- | ------ |
| `/agent create <name>` | Create a new agent definition |
| `/agent list` | List all available agents |
| `/agent run <name>` | Execute an agent or agent team |
| `/agent release-prep` | Run the release readiness agent team |

## Natural Language

Describe what you need:

- "create a code review agent"
- "what agents are available?"
- "run the release prep team"
- "I need a specialized agent for testing"

## CRITICAL: Workflow Execution Instructions

**When this command is invoked with arguments, you MUST execute the workflow, not answer ad-hoc.**

### Context Gathering (ALWAYS DO FIRST)

Before executing any action below, gather current project context:

1. Run: `git status --short`
2. Run: `git log --oneline -5`
3. Run: `git branch --show-current`

Use this context to inform agent operations (e.g., current branch, recent changes).

### Shortcut Routing (EXECUTE THESE)

| Input | Action |
| ----- | ------ |
| `/agent create <name>` | Guide through agent definition: role, tools, model tier, coordination pattern |
| `/agent list` | Scan `src/attune/agents/` directory, list agents with descriptions and capabilities |
| `/agent run <name>` | Execute the named agent or agent team |
| `/agent release-prep` | Run release readiness agent team |

### Natural Language Routing (EXECUTE THESE)

| Pattern | Action |
| ------- | ------ |
| "create", "new agent", "define" | Guide agent creation |
| "list", "available", "what agents" | List available agents |
| "run", "execute", "start" | Run specified agent |
| "release", "release-prep", "readiness" | Run release-prep agent team |

**IMPORTANT:** When arguments are provided, DO NOT just display documentation. EXECUTE the action.

### Agent Definition Format

When creating agents, use this structure in `src/attune/agents/<name>/`:

```text
<name>/
  __init__.py     # Agent exports
  agent.py        # Agent class definition
  prompts.py      # Agent-specific prompts
  tools.py        # Custom tools (optional)
```

### Available Agent Teams

| Team | Description | Location |
| ---- | ----------- | -------- |
| Release Prep | 4-agent release readiness check (security, tests, quality, docs) | `src/attune/agents/release/` |

### Coordination Patterns

Agents can use these coordination patterns:

- **Heartbeats** — Periodic health checks
- **Signals** — Direct agent-to-agent messaging
- **Events** — Pub/sub event broadcasting
- **Approvals** — Human-in-the-loop gates
- **Quality Feedback** — Output quality scoring
- **Demo Mode** — Simulated execution for testing
