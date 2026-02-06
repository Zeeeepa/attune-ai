---
name: attune
description: AI-powered developer workflows with Socratic discovery
category: primary
aliases: [a]
tags: [navigation, discovery, socratic]
version: "2.2.0"
question:
  header: "What brings you here?"
  question: "What are you trying to accomplish right now?"
  multiSelect: false
  options:
    - label: "🔧 Fix or improve something"
      description: "Debug issues, review code, refactor, or improve quality"
    - label: "✅ Validate my work"
      description: "Run tests, check coverage, audit security, or verify quality"
    - label: "🚀 Ship my changes"
      description: "Commit, create PR, prepare release, or publish"
    - label: "📚 Understand or document"
      description: "Explain code, generate docs, or learn patterns"
---

# attune

Your AI-powered developer workflow assistant with Socratic discovery.

**One command. Every workflow.** Type `/attune` to browse, or jump straight to any workflow below.

## Workflow Directory

### Developer Tools — [/dev](src/attune/commands/dev.md)

| Command | Description |
| ------- | ----------- |
| [Debug](src/attune/commands/dev.md) `/dev debug` | Investigate errors, trace execution, find root causes |
| [Code Review](src/attune/commands/dev.md) `/dev review` | Quality analysis, security review, performance review |
| [Commit](src/attune/commands/dev.md) `/dev commit` | Stage and commit with conventional commit messages |
| [Pull Request](src/attune/commands/dev.md) `/dev pr` | Push branch, create PR with summary and test plan |
| [Refactor](src/attune/commands/dev.md) `/dev refactor` | Analyze structure, suggest and apply improvements |
| [Bug Predict](src/attune/commands/dev.md) `/dev quality` | Detect patterns likely to produce bugs |

### Testing — [/testing](src/attune/commands/testing.md)

| Command | Description |
| ------- | ----------- |
| [Run Tests](src/attune/commands/testing.md) `/testing run` | Execute pytest test suite |
| [Coverage](src/attune/commands/testing.md) `/testing coverage` | Run tests with coverage report and gap analysis |
| [Generate Tests](src/attune/commands/testing.md) `/testing generate` | Auto-generate behavioral tests for a module |
| [TDD](src/attune/commands/testing.md) `/testing tdd` | Test-driven development: write test first, then implement |

### Analysis Workflows — [/workflows](src/attune/commands/workflows.md)

| Command | Description |
| ------- | ----------- |
| [Security Audit](src/attune/commands/workflows.md) `/workflows security` | Scan for eval, path traversal, secrets, injection risks |
| [Bug Prediction](src/attune/commands/workflows.md) `/workflows bugs` | Detect broad exceptions, incomplete code, risky patterns |
| [Performance Audit](src/attune/commands/workflows.md) `/workflows perf` | Find bottlenecks, memory issues, optimization opportunities |
| [Code Review](src/attune/commands/workflows.md) `/workflows review` | Comprehensive quality and style analysis |
| [List Workflows](src/attune/commands/workflows.md) `/workflows list` | Show all available analysis workflows |

### Planning — [/plan](src/attune/commands/plan.md)

| Command | Description |
| ------- | ----------- |
| [Plan Feature](src/attune/commands/plan.md) `/plan feature` | Break down a feature into tasks, files, deps, and risks |
| [TDD Scaffolding](src/attune/commands/plan.md) `/plan tdd` | Design test cases first, then plan implementation |
| [Refactoring Strategy](src/attune/commands/plan.md) `/plan refactor` | Plan safe incremental refactoring steps |
| [Architecture Review](src/attune/commands/plan.md) `/plan architecture` | Evaluate architecture, propose improvements |

### Documentation — [/docs](src/attune/commands/docs.md)

| Command | Description |
| ------- | ----------- |
| [Generate Docs](src/attune/commands/docs.md) `/docs generate` | Create or update Google-style docstrings for a module |
| [Update README](src/attune/commands/docs.md) `/docs readme` | Review and improve README.md |
| [Update Changelog](src/attune/commands/docs.md) `/docs changelog` | Draft CHANGELOG entries from recent commits |
| [Explain Code](src/attune/commands/docs.md) `/docs explain` | Produce clear human-readable explanation of code |
| [Architecture Overview](src/attune/commands/docs.md) `/docs architecture` | Generate architecture docs with component relationships |

### Release — [/release](src/attune/commands/release.md)

| Command | Description |
| ------- | ----------- |
| [Prepare Release](src/attune/commands/release.md) `/release prep` | Version bump, changelog, pre-flight checks |
| [Security Scan](src/attune/commands/release.md) `/release security` | Pre-release vulnerability audit |
| [Health Check](src/attune/commands/release.md) `/release health` | Full project health: tests + coverage + lint + bandit |
| [Publish](src/attune/commands/release.md) `/release publish` | Build and publish to PyPI |

### Agents — [/agent](src/attune/commands/agent.md)

| Command | Description |
| ------- | ----------- |
| [Create Agent](src/attune/commands/agent.md) `/agent create` | Define a new specialized agent with role and tools |
| [List Agents](src/attune/commands/agent.md) `/agent list` | Show all available agents and capabilities |
| [Run Agent Team](src/attune/commands/agent.md) `/agent run` | Execute a multi-agent collaboration |
| [Healthcare CDS](src/attune/commands/agent.md) `/agent cds` | Clinical decision support multi-agent system |

### Deep Review — [/deep-review](src/attune/commands/deep-review.md)

| Command | Description |
| ------- | ----------- |
| [Full Review](src/attune/commands/deep-review.md) `/deep-review <path>` | Security + quality + test gap analysis |
| [Security Only](src/attune/commands/deep-review.md) `/deep-review security` | CWE-focused vulnerability scan |
| [Quality Only](src/attune/commands/deep-review.md) `/deep-review quality` | Code quality and style analysis |
| [Test Gaps Only](src/attune/commands/deep-review.md) `/deep-review tests` | Coverage analysis and missing test detection |

## Natural Language

Just describe what you need — no need to memorize commands:

- "find security vulnerabilities"
- "why is this test failing"
- "generate tests for config.py"
- "review my authentication code"
- "prepare for release 2.0"
- "explain how caching works"
- "this function is too long"

## CRITICAL: Workflow Execution Instructions

**When this command is invoked with arguments, you MUST execute the workflow via CLI, not answer ad-hoc.**

### No-Argument Behavior: Socratic Funnel

**When invoked without arguments (`/attune` alone), use AskUserQuestion to present a clickable 2-step discovery flow.**

**Step 1 — Goal Discovery:** Present this AskUserQuestion:

- Header: `"Attune"`
- Question: `"What are you trying to accomplish?"`
- Options (4 max):
  1. **Fix or improve code** — "/dev - Debug, review, refactor, commit, PR"
  2. **Validate my work** — "/testing + /workflows - Tests, coverage, security, perf"
  3. **Ship my changes** — "/release + /plan - Plan features, prepare release, publish"
  4. **Understand or document** — "/docs + /agent - Explain code, generate docs, manage agents"

**Step 2 — Hub Selection:** Based on their choice, present a second AskUserQuestion with the specific hubs:

- "Fix or improve code" → Options: `/dev`, `/deep-review`
- "Validate my work" → Options: `/testing run`, `/testing coverage`, `/workflows security`, `/workflows perf`
- "Ship my changes" → Options: `/release prep`, `/release health`, `/plan feature`, `/plan architecture`
- "Understand or document" → Options: `/docs generate`, `/docs explain`, `/docs changelog`, `/agent list`

**Step 3 — Execute:** Invoke the selected hub skill via the Skill tool.

**Do NOT dump the full Workflow Directory tables.** The tables above are reference documentation — the primary interface is the clickable AskUserQuestion funnel.

### Shortcut Routing (EXECUTE THESE)

When the user types a shortcut, run the corresponding CLI command:

| Input | CLI Command |
| ----- | ----------- |
| `/attune security` | `uv run attune workflow run security-audit` |
| `/attune test` | `uv run pytest` |
| `/attune coverage` | `uv run pytest --cov=src --cov-report=term-missing` |
| `/attune perf` | `uv run attune workflow run perf-audit` |
| `/attune review` | `uv run attune workflow run code-review` |
| `/attune bug-predict` | `uv run attune workflow run bug-predict` |
| `/attune test-gen` | `uv run attune workflow run test-gen` |
| `/attune commit` | Use git to stage and commit changes |
| `/attune pr` | Use gh to create a pull request |
| `/attune release` | `uv run attune workflow run release-prep` |
| `/attune debug` | Start interactive debugging session |
| `/attune refactor` | Analyze code and suggest refactoring |
| `/attune docs` | Generate documentation |
| `/attune explain` | Read and explain the specified code |

### Natural Language Routing (EXECUTE THESE)

When the user provides natural language, map to the appropriate CLI command:

| Pattern | CLI Command |
| ------- | ----------- |
| "security", "vulnerabilities", "audit" | `uv run attune workflow run security-audit` |
| "test", "tests", "run tests" | `uv run pytest` |
| "coverage", "test coverage" | `uv run pytest --cov=src --cov-report=term-missing` |
| "generate tests", "write tests" | `uv run attune workflow run test-gen` |
| "review", "code review" | `uv run attune workflow run code-review` |
| "performance", "perf", "bottleneck" | `uv run attune workflow run perf-audit` |
| "bugs", "predict bugs" | `uv run attune workflow run bug-predict` |
| "release", "ship", "publish" | `uv run attune workflow run release-prep` |

**IMPORTANT:** When arguments are provided, DO NOT just display documentation. EXECUTE the CLI command.

### CLI Reference

```bash
# Workflows
uv run attune workflow run security-audit --path <target>
uv run attune workflow run perf-audit --path <target>
uv run attune workflow run bug-predict --path <target>
uv run attune workflow run code-review --path <target>
uv run attune workflow run test-gen --path <target>
uv run attune workflow run release-prep

# Testing
uv run pytest
uv run pytest --cov=src --cov-report=term-missing
uv run pytest -k "test_name"

# Telemetry
uv run attune telemetry show
```
