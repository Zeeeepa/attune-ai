# Attune AI

**AI-powered developer workflows with cost optimization and intelligent routing.**

Run code review, debugging, testing, and release workflows from your terminal or Claude Code. Smart tier routing saves 34-86% on LLM costs.

[![PyPI](https://img.shields.io/pypi/v/attune-ai?color=blue)](https://pypi.org/project/attune-ai/)
[![Tests](https://github.com/Smart-AI-Memory/attune-ai/actions/workflows/test.yml/badge.svg)](https://github.com/Smart-AI-Memory/attune-ai/actions/workflows/test.yml)
[![Python](https://img.shields.io/badge/python-3.10+-blue)](https://www.python.org)
[![License](https://img.shields.io/badge/license-Apache%202.0-blue)](LICENSE)

```bash
pip install attune-ai[developer]
```

---

## Key Features

### Claude-Native Architecture

Attune AI is built exclusively for Anthropic/Claude, unlocking features impossible with multi-provider abstraction:

- **Prompt Caching** - 90% cost reduction on repeated prompts
- **Flexible Context** - 200K via subscription, up to 1M via API for large codebases
- **Extended Thinking** - Access Claude's internal reasoning process
- **Advanced Tool Use** - Optimized for agentic workflows

### Multi-Agent Orchestration

Full support for custom agents and Anthropic LLM agents:

- **Agent Coordination Dashboard** - Real-time monitoring with 6 coordination patterns
- **Custom Agents** - Build specialized agents for your workflow needs
- **Inter-Agent Communication** - Heartbeats, signals, events, and approval gates

### Intelligent Cost Optimization

- **$0 in Claude Code** - Workflows run as skills through Claude's Task tool
- **Smart Tier Routing** - Automatically selects the right model for each task
- **Authentication Strategy** - Routes between subscription and API based on codebase size

### Socratic Workflows

Workflows guide you through discovery instead of requiring upfront configuration:

- **Interactive Discovery** - Asks targeted questions to understand your needs
- **Context Gathering** - Collects relevant code, errors, and constraints
- **Dynamic Agent Creation** - Assembles the right team based on your answers

---

## Quick Start

### 1. Install

```bash
pip install attune-ai[developer]
```

### 2. Configure

```bash
# Auto-detect API keys
python -m attune.models.cli provider

# Or configure authentication strategy
python -m attune.models.auth_cli setup
```

### 3. Use in Claude Code

```bash
/dev           # Developer tools (debug, commit, PR, review)
/testing       # Run tests, coverage analysis, benchmarks
/workflows     # Automated analysis (security, bugs, perf)
/plan          # Planning, TDD, code review, refactoring
/docs          # Documentation generation
/release       # Release preparation

# Natural language support:
/workflows "find security issues"
/plan "review my code"
```

### 4. Use via CLI

```bash
attune workflow run security-audit --path ./src
attune workflow run test-coverage --target 90
attune telemetry show  # View cost savings
```

---

## Command Hubs

Workflows are organized into hubs for easy discovery:

| Hub               | Command       | Description                                  |
| ----------------- | ------------- | -------------------------------------------- |
| **Developer**     | `/dev`        | Debug, commit, PR, code review, quality      |
| **Testing**       | `/testing`    | Run tests, coverage analysis, benchmarks     |
| **Documentation** | `/docs`       | Generate and manage documentation            |
| **Release**       | `/release`    | Release prep, security scan, publishing      |
| **Workflows**     | `/workflows`  | Automated analysis (security, bugs, perf)    |
| **Plan**          | `/plan`       | Planning, TDD, code review, refactoring      |
| **Agent**         | `/agent`      | Create and manage custom agents              |

**Natural Language Routing:**

```bash
/workflows "find security vulnerabilities"  # → security-audit
/workflows "check code performance"         # → perf-audit
/plan "review my code"                      # → code-review
```

---

## Cost Optimization

### Skills = $0 (Claude Code)

When using Claude Code, workflows run as skills through the Task tool - **no API costs**:

```bash
/dev           # $0 - uses your Claude subscription
/testing       # $0
/release       # $0
```

### API Mode (CI/CD, Automation)

For programmatic use, smart tier routing saves 34-86%:

| Tier    | Model         | Use Case                     | Cost    |
| ------- | ------------- | ---------------------------- | ------- |
| CHEAP   | Haiku         | Formatting, simple tasks     | ~$0.005 |
| CAPABLE | Sonnet        | Bug fixes, code review       | ~$0.08  |
| PREMIUM | Opus          | Architecture, complex design | ~$0.45  |

```bash
# Track API usage and savings
attune telemetry savings --days 30
```

---

## MCP Server Integration

Attune AI includes a Model Context Protocol (MCP) server that exposes all workflows as native Claude Code tools:

- **10 Tools Available** - security_audit, bug_predict, code_review, test_generation, performance_audit, release_prep, and more
- **Automatic Discovery** - Claude Code finds tools via `.claude/mcp.json`
- **Natural Language Access** - Describe your need and Claude invokes the appropriate tool

```bash
# Verify MCP integration
echo '{"method":"tools/list","params":{}}' | PYTHONPATH=./src python -m attune.mcp.server
```

---

## Agent Coordination Dashboard

Real-time monitoring with 6 coordination patterns:

- Agent heartbeats and status tracking
- Inter-agent coordination signals
- Event streaming across agent workflows
- Approval gates for human-in-the-loop
- Quality feedback and performance metrics
- Demo mode with test data generation

```bash
# Launch dashboard (requires Redis)
python examples/dashboard_demo.py
# Open http://localhost:8000
```

---

## Authentication Strategy

Intelligent routing between Claude subscription and Anthropic API:

```bash
# Interactive setup
python -m attune.models.auth_cli setup

# View current configuration
python -m attune.models.auth_cli status

# Get recommendation for a file
python -m attune.models.auth_cli recommend src/module.py
```

**Automatic routing:**

- Small/medium modules (<2000 LOC) → Claude subscription (free)
- Large modules (>2000 LOC) → Anthropic API (pay for what you need)

---

## Installation Options

```bash
# Individual developers (recommended)
pip install attune-ai[developer]

# With caching (semantic similarity)
pip install attune-ai[cache]

# Enterprise (auth, rate limiting)
pip install attune-ai[enterprise]

# Development
git clone https://github.com/Smart-AI-Memory/attune-ai.git
cd attune-ai && pip install -e .[dev]
```

---

## Environment Setup

```bash
# Required: Anthropic API key
export ANTHROPIC_API_KEY="sk-ant-..."

# Optional: Redis for Agent Dashboard and memory
export REDIS_URL="redis://localhost:6379"
```

---

## Security

- Path traversal protection on all file operations
- JWT authentication with rate limiting
- PII scrubbing in telemetry
- HIPAA/GDPR compliance options
- Automated security scanning with 82% accuracy

```bash
# Run security audit
attune workflow run security-audit --path ./src
```

See [SECURITY.md](SECURITY.md) for vulnerability reporting.

---

## Documentation

- [Quick Start Guide](docs/quickstart.md)
- [CLI Reference](docs/cli-reference.md)
- [Authentication Strategy Guide](docs/AUTH_STRATEGY_GUIDE.md)
- [Full Documentation](https://smartaimemory.com/framework-docs/)

---

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

---

## License

**Apache License 2.0** - Free and open source. Use it, modify it, build commercial products with it. [Details →](LICENSE)

---

## Acknowledgements

Special thanks to:

- **[Anthropic](https://www.anthropic.com/)** - For Claude AI and the Model Context Protocol
- **[LangChain](https://github.com/langchain-ai/langchain)** - Agent framework powering our orchestration
- **[FastAPI](https://github.com/tiangolo/fastapi)** - Modern Python web framework

[View Full Acknowledgements →](ACKNOWLEDGEMENTS.md)

---

**Built by [Smart AI Memory](https://smartaimemory.com)** · [Docs](https://smartaimemory.com/framework-docs/) · [Issues](https://github.com/Smart-AI-Memory/attune-ai/issues)
