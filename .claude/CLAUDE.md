# Attune AI v2.3.3

**AI-powered developer workflows with cost optimization and intelligent routing.**

Run code review, debugging, testing, and release workflows from your terminal or Claude Code. Smart tier routing saves 34-86% on LLM costs. Skills run at $0 in Claude Code.

@./python-standards.md

---

## Quick Start

### In Claude Code (Recommended)

```bash
attune setup                    # Install /attune slash command
/attune                         # Socratic discovery guides you
/attune debug                   # Direct shortcut
```

### CLI Usage

```bash
attune workflow run security-audit --path ./src
attune workflow run test-gen --path ./src
attune telemetry show
```

### Authentication Strategy

```bash
python -m attune.models.auth_cli setup      # Interactive configuration
python -m attune.models.auth_cli status     # View current settings
python -m attune.models.auth_cli recommend src/module.py
```

---

## Key Capabilities

- **Claude-Native Architecture** - Built for Anthropic/Claude with prompt caching (90% cost reduction), extended thinking, and 200K-1M context
- **$0 in Claude Code** - Workflows run as skills through Claude's Task tool, no API costs
- **Smart Tier Routing** - Automatic model selection (Haiku/Sonnet/Opus) saves 34-86%
- **Multi-Agent Orchestration** - 6 coordination patterns: heartbeats, signals, events, approvals, quality feedback, demo mode
- **Socratic Workflows** - Interactive discovery asks targeted questions instead of requiring upfront config
- **MCP Integration** - Model Context Protocol server exposes 10 tools as native Claude Code tools
- **Authentication Strategy** - Routes between subscription (free, <2000 LOC) and API (large codebases)

---

## Installation

```bash
pip install attune-ai                  # Base: CLI + workflows + Anthropic SDK
pip install attune-ai[developer]       # + OpenAI, Google AI, agents, memory
pip install attune-ai[cache]           # + Semantic similarity caching (70% savings)
pip install attune-ai[enterprise]      # + JWT auth, rate limiting, OpenTelemetry
pip install attune-ai[healthcare]      # + HIPAA/GDPR compliance
```

Redis is optional (only needed for `[memory]` features). Core install is lightweight.

---

## Command Hubs

Use `/hub-name` to access organized workflows:

| Hub | Command | Description |
|-----|---------|-------------|
| Developer | `/dev` | Debug, commit, PR, code review, quality |
| Testing | `/testing` | Run tests, coverage analysis, benchmarks |
| Workflows | `/workflows` | Automated analysis (security, bugs, perf) |
| Plan | `/plan` | Planning, TDD, code review, refactoring |
| Docs | `/docs` | Documentation generation and management |
| Release | `/release` | Release prep, security scan, publishing |
| Agent | `/agent` | Create and manage custom agents |

Natural language routing works across all hubs:

```bash
/workflows "find security vulnerabilities"    # -> security-audit
/dev debug "authentication fails on login"    # -> debug workflow
/testing coverage --target 90                 # -> coverage analysis
```

---

## Workflows (26 Available)

**Code Analysis:** code-review, bug-predict, security-audit, perf-audit, dependency-check, refactor-plan

**Testing:** test-gen, test-coverage-boost-crew, autonomous-test-gen

**Documentation:** doc-gen, manage-documentation

**Release:** release-prep-crew, secure-release, health-check-crew

**Review:** code-review-pipeline, pr-review

```bash
attune workflow list                          # List all workflows
attune workflow run <name> --path <target>    # Run a workflow
```

---

## Coding Standards

@./rules/empathy/coding-standards-index.md

**Critical rules enforced across all code:**

- NEVER use eval() or exec()
- ALWAYS validate file paths with _validate_file_path()
- NEVER use bare except: - catch specific exceptions
- ALWAYS log exceptions before handling
- Type hints and docstrings required on all public APIs
- Minimum 80% test coverage
- Security tests required for file operations

---

## Project Structure

```text
src/attune/
├── cli/                # Main CLI with commands/ and parsers/ subpackages
├── cli_minimal.py      # Primary lightweight CLI entry point
├── workflows/          # 26 AI-powered workflows
├── models/             # Authentication strategy and LLM providers
├── mcp/                # Model Context Protocol server (10 tools)
├── dashboard/          # Agent Coordination Dashboard (6 patterns)
├── memory/             # Two-tier memory system (16 focused modules)
│   ├── short_term/     # Redis-backed: sessions, queues, streams, pubsub
│   └── long_term.py    # Persistent memory with memdocs integration
├── orchestration/      # Multi-agent coordination with _strategies/
├── meta_workflows/     # Intent detection and natural language routing
├── socratic/           # Interactive Socratic discovery workflows
├── adaptive/           # Adaptive learning workflows
├── routing/            # Smart tier routing (Haiku/Sonnet/Opus)
├── monitoring/         # Agent telemetry and monitoring
├── trust/              # Trust-building behaviors
├── validation/         # Input/output validation
├── telemetry/          # Cost tracking and cache monitoring
├── patterns/           # Pattern library with debugging subpackage
├── project_index/      # Code analysis and indexing (AST parsing)
├── test_generator/     # Test generation with templates
├── cache/              # Prompt caching strategies
├── config/             # Configuration system with sections/
├── plugins/            # Plugin system
├── resilience/         # Resilience patterns
├── scaffolding/        # TDD and workflow scaffolding
├── core.py             # EmpathyOS main class
├── coordination.py     # Team coordination
└── feedback_loops.py   # Feedback loop detection
```

---

## CLI Entry Points

| Command | Purpose |
|---------|---------|
| `attune` | Primary CLI (workflows, setup, telemetry) |
| `attune setup` | Install /attune slash command to ~/.claude/commands/ |
| `attune workflow run <name>` | Execute a workflow |
| `attune workflow list` | List available workflows |
| `attune telemetry show` | Usage tracking and cost savings |
| `attune dashboard start` | Web UI at localhost:8000 |

Legacy entry points (`empathy-legacy`, `empathy-unified`) remain for backward compatibility.

---

## Environment Setup

**In Claude Code:** No setup needed - uses your Claude subscription ($0).

**For CLI/API usage:**

```bash
export ANTHROPIC_API_KEY="sk-ant-..."           # Required for CLI workflows
export REDIS_URL="redis://localhost:6379"        # Optional: for memory features
```

---

## Documentation

- [AUTH_STRATEGY_GUIDE.md](../docs/AUTH_STRATEGY_GUIDE.md) - Authentication configuration
- [AUTH_CLI_IMPLEMENTATION.md](../docs/AUTH_CLI_IMPLEMENTATION.md) - CLI command reference
- [AUTH_WORKFLOW_INTEGRATIONS.md](../docs/AUTH_WORKFLOW_INTEGRATIONS.md) - Integration patterns
- [CHANGELOG.md](../CHANGELOG.md) - Version history and release notes
- [SECURITY.md](../SECURITY.md) - Security policy and vulnerability reporting
- [Full Documentation](https://smartaimemory.com/framework-docs/)

---

**Version:** 2.3.3 (2026-02-06)
**License:** Apache 2.0 - Free and open source
**Repository:** https://github.com/Smart-AI-Memory/attune-ai
