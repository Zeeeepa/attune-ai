---
name: docs
description: Documentation generation and management
category: hub
aliases: [doc, documentation]
tags: [documentation, readme, api-docs, changelog]
version: "1.0.0"
question:
  header: "Documentation Hub"
  question: "What documentation do you need?"
  multiSelect: false
  options:
    - label: "Generate API docs"
      description: "Create docstrings and API reference for a module"
    - label: "Update README"
      description: "Update or generate README.md"
    - label: "Update CHANGELOG"
      description: "Add entries to CHANGELOG.md for recent changes"
    - label: "Explain code"
      description: "Generate human-readable explanation of code"
---

# docs

Documentation generation and management hub.

## Quick Shortcuts

| Shortcut | Action |
| -------- | ------ |
| `/docs generate <path>` | Generate or update docstrings for module |
| `/docs readme` | Review and suggest README improvements |
| `/docs changelog` | Draft CHANGELOG entries from recent commits |
| `/docs explain <path>` | Read code and produce explanation |
| `/docs architecture` | Generate architecture overview |

## Natural Language

Describe what you need:

- "add docstrings to the config module"
- "update the README"
- "what changed since the last release?"
- "explain how the workflow engine works"
- "generate architecture docs"

## CRITICAL: Workflow Execution Instructions

**When this command is invoked with arguments, you MUST execute the workflow, not answer ad-hoc.**

### Context Gathering (ALWAYS DO FIRST)

Before executing any action below, gather current project context:

1. Run: `git status --short`
2. Run: `git log --oneline -5`
3. Run: `git branch --show-current`
4. Run: `git log --oneline --since="2 weeks ago"` (recent changes for changelog)

Use this context to inform documentation updates (e.g., what changed recently, current branch).

### Shortcut Routing (EXECUTE THESE)

| Input | Action |
| ----- | ------ |
| `/docs generate <path>` | Read module at path, add or update Google-style docstrings for all public APIs |
| `/docs readme` | Read current README.md, suggest and apply improvements |
| `/docs changelog` | Read recent git log, draft CHANGELOG.md entries in Keep a Changelog format |
| `/docs explain <path>` | Read code at path, produce clear human-readable explanation |
| `/docs architecture` | Scan project structure, generate architecture overview with component relationships |

### Natural Language Routing (EXECUTE THESE)

| Pattern | Action |
| ------- | ------ |
| "docstrings", "api docs", "generate docs" | Generate docstrings for specified module |
| "readme", "README" | Review and update README.md |
| "changelog", "what changed", "release notes" | Draft CHANGELOG entries |
| "explain", "how does", "what does" | Explain code at specified path |
| "architecture", "overview", "structure" | Generate architecture documentation |

**IMPORTANT:** When arguments are provided, DO NOT just display documentation. EXECUTE the action.

### Documentation Standards

When generating documentation, follow these standards:

- **Docstrings:** Google-style format with Args, Returns, Raises sections
- **CHANGELOG:** Keep a Changelog format (Added, Changed, Fixed, Removed)
- **README:** Clear user journey with time estimates
- **Architecture:** Component diagrams with relationships and data flow
