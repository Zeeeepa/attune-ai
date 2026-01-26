---
name: help
description: Master navigation - overview of all available hubs and commands
category: hub
aliases: [index, commands, menu]
tags: [help, navigation, index, hub]
version: "1.0"
---

# Command Help

**Aliases:** `/index`, `/commands`, `/menu`

Overview of all available hubs and how to use them.

## Understanding Commands

When you type `/` in Claude Code, you'll see two types of commands:

| Type             | Source                             | Examples                                                                          |
| ---------------- | ---------------------------------- | --------------------------------------------------------------------------------- |
| **Project Hubs** | This project (`.claude/commands/`) | `/dev`, `/testing`, `/workflow`, `/docs`, etc.                                    |
| **Built-in**     | Claude Code itself                 | `/clear`, `/compact`, `/config`, `/cost`, `/doctor`, `/init`, `/model`, `/status` |

**This help covers the 9 Project Hubs below.** For built-in commands, see [Claude Code documentation](https://docs.anthropic.com/claude-code).

---

## Available Hubs

| Hub          | Aliases              | Purpose                                    |
| ------------ | -------------------- | ------------------------------------------ |
| `/dev`       | `/developer`         | Debugging, commits, PRs, code quality      |
| `/testing`   | `/tests`, `/test-hub`| Run tests, coverage, benchmarks            |
| `/workflow`  | `/wf`                | Planning, TDD, code review, refactoring    |
| `/docs`      | `/documentation`     | Explain code, manage docs, feature overview|
| `/agent`     | `/agents`            | Create and manage specialized agents       |
| `/context`   | `/ctx`               | Save/restore state, memory, status         |
| `/learning`  | `/learn-hub`         | Evaluate sessions, patterns, preferences   |
| `/release`   | `/ship`              | Prepare releases, publish, security scan   |
| `/utilities` | `/util`, `/utils`    | Project init, dependencies, profiling      |

## Quick Start

```bash
# Run any hub for an interactive menu
/dev
/testing
/workflow

# Or provide context directly
/dev "debug login error"
/testing "run unit tests"
/workflow "plan new feature"
```

## Finding the Right Hub

```text
What do you need to do?

Code & Git:
  └─ Debug, commit, PR, quality → /dev

Testing:
  └─ Run tests, coverage, benchmarks → /testing

Development Process:
  └─ Plan, TDD, review, refactor → /workflow

Documentation:
  └─ Explain code, write docs → /docs

Agents:
  └─ Create/manage agents → /agent

Session State:
  └─ Save/restore context, memory → /context

Learning:
  └─ Patterns, preferences → /learning

Releases:
  └─ Prep, publish, security → /release

Setup:
  └─ Init, deps, profiling → /utilities
```

## Common Tasks Quick Reference

| Task                     | Command                    |
| ------------------------ | -------------------------- |
| Debug an error           | `/dev "debug <error>"`     |
| Create a commit          | `/dev "commit"`            |
| Create a PR              | `/dev "create PR"`         |
| Run tests                | `/testing "run tests"`     |
| Check coverage           | `/testing "coverage"`      |
| Plan a feature           | `/workflow "plan <feat>"`  |
| Review code              | `/workflow "review"`       |
| Explain code             | `/docs "explain <file>"`   |
| Save session state       | `/context "save state"`    |
| Prepare release          | `/release "prep 1.0.0"`    |

## Hub Features

Each hub includes:

- **Quick Examples** - Common usage patterns
- **Discovery Menu** - Interactive option selection
- **Inline Prompts** - Detailed instructions for each option
- **When NOT to Use** - Guidance to find the right hub
- **Related Hubs** - Cross-references to related functionality

## Tips

1. **Use aliases** - `/dev` is faster than `/developer`
2. **Add context** - `/dev "debug login"` is more specific than just `/dev`
3. **Follow cross-references** - Each hub points to related hubs
4. **Use interactive menus** - Just type the hub name for guided discovery
