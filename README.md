# Empathy Framework

**AI-powered developer workflows with cost optimization and pattern learning.**

Run code review, debugging, testing, and release workflows from your terminal or Claude Code. Smart tier routing saves 34-86% on LLM costs.

[![PyPI](https://img.shields.io/pypi/v/empathy-framework)](https://pypi.org/project/empathy-framework/)
[![Tests](https://img.shields.io/badge/tests-11%2C000%2B%20passing-brightgreen)](https://github.com/Smart-AI-Memory/empathy-framework/actions)
[![Coverage](https://img.shields.io/badge/coverage-68%25-yellow)](https://github.com/Smart-AI-Memory/empathy-framework)
[![Python](https://img.shields.io/badge/python-3.10+-blue)](https://www.python.org)
[![License](https://img.shields.io/badge/license-Fair%20Source%200.9-blue)](LICENSE)

```bash
pip install empathy-framework[developer]
```

---

## What's New in v4.7.0

**Security Hardened** - Fixed critical vulnerabilities (path traversal, JWT, SSRF).

**Performance** - 36% faster scanning, 39% faster init, 11,000+ tests passing.

**Hub-Based Commands** - Organized workflows into intuitive command hubs.

---

## Quick Start

### 1. Install

```bash
pip install empathy-framework[developer]
```

### 2. Configure

```bash
# Auto-detect API keys
python -m empathy_os.models.cli provider

# Or set explicitly
python -m empathy_os.models.cli provider --set anthropic
```

### 3. Use

**In Claude Code:**

```bash
/dev           # Developer tools (debug, commit, PR, review)
/testing       # Run tests, coverage, benchmarks
/docs          # Documentation generation
/release       # Release preparation
```

**CLI:**

```bash
empathy workflow run security-audit --path ./src
empathy workflow run test-coverage --target 90
empathy telemetry show  # View cost savings
```

**Python:**

```python
from empathy_os import EmpathyOS

async with EmpathyOS() as empathy:
    result = await empathy.level_2_guided(
        "Review this code for security issues"
    )
    print(result["response"])
```

---

## Command Hubs

Workflows are organized into hubs for easy discovery:

| Hub               | Command      | Description                                  |
| ----------------- | ------------ | -------------------------------------------- |
| **Developer**     | `/dev`       | Debug, commit, PR, code review, quality      |
| **Testing**       | `/testing`   | Run tests, coverage analysis, benchmarks     |
| **Documentation** | `/docs`      | Generate and manage documentation            |
| **Release**       | `/release`   | Release prep, security scan, publishing      |
| **Workflow**      | `/workflow`  | Planning, TDD, refactoring workflows         |
| **Utilities**     | `/utilities` | Project init, dependencies, profiling        |
| **Learning**      | `/learning`  | Pattern learning and session evaluation      |
| **Context**       | `/context`   | State management and memory                  |
| **Agent**         | `/agent`     | Create and manage custom agents              |

**Example usage:**

```bash
/dev                    # Show interactive menu
/dev "debug auth error" # Jump directly to debugging
/testing "run coverage" # Run coverage analysis
/release                # Start release preparation
```

---

## Cost Optimization

Smart tier routing automatically selects the right model for each task:

| Tier | Model | Use Case | Cost |
|------|-------|----------|------|
| CHEAP | Haiku / GPT-4o-mini | Formatting, simple tasks | ~$0.005/task |
| CAPABLE | Sonnet / GPT-4o | Bug fixes, code review | ~$0.08/task |
| PREMIUM | Opus / o1 | Architecture, complex design | ~$0.45/task |

**Savings by role:**

| Role | Savings |
|------|---------|
| Junior Developer | 86% |
| QA Engineer | 80% |
| Mid-Level Developer | 73% |
| Senior Developer | 65% |
| Architect | 34% |

```bash
# Track your actual savings
empathy telemetry savings --days 30
```

---

## Key Features

### Multi-Agent Workflows

```bash
# 4 parallel agents check release readiness
empathy orchestrate release-prep

# Sequential coverage improvement
empathy orchestrate test-coverage --target 90
```

### Response Caching

Up to 57% cache hit rate on similar prompts. Zero config needed.

```python
from empathy_os.workflows import SecurityAuditWorkflow

workflow = SecurityAuditWorkflow(enable_cache=True)
result = await workflow.execute(target_path="./src")
print(f"Cache hit rate: {result.cost_report.cache_hit_rate:.1f}%")
```

### Pattern Learning

Workflows learn from outcomes and improve over time:

```python
from empathy_os.orchestration.config_store import ConfigurationStore

store = ConfigurationStore()
best = store.get_best_for_task("release_prep")
print(f"Success rate: {best.success_rate:.1%}")
```

### Multi-Provider Support

```python
from empathy_llm_toolkit.providers import (
    AnthropicProvider,  # Claude
    OpenAIProvider,     # GPT-4
    GeminiProvider,     # Gemini
    LocalProvider,      # Ollama, LM Studio
)
```

---

## CLI Reference

```bash
# Provider configuration
python -m empathy_os.models.cli provider
python -m empathy_os.models.cli provider --set hybrid

# Workflows
empathy workflow list
empathy workflow run <workflow-name>

# Cost tracking
empathy telemetry show
empathy telemetry savings --days 30
empathy telemetry export --format csv

# Orchestration
empathy orchestrate release-prep
empathy orchestrate test-coverage --target 90

# Meta-workflows
empathy meta-workflow list
empathy meta-workflow run release-prep --real
```

---

## Install Options

```bash
# Individual developers (recommended)
pip install empathy-framework[developer]

# All LLM providers
pip install empathy-framework[llm]

# With caching (semantic similarity)
pip install empathy-framework[cache]

# Enterprise (auth, rate limiting)
pip install empathy-framework[enterprise]

# Healthcare (HIPAA compliance)
pip install empathy-framework[healthcare]

# Development
git clone https://github.com/Smart-AI-Memory/empathy-framework.git
cd empathy-framework && pip install -e .[dev]
```

---

## Environment Setup

```bash
# At least one provider required
export ANTHROPIC_API_KEY="sk-ant-..."
export OPENAI_API_KEY="sk-..."
export GOOGLE_API_KEY="..."

# Optional: Redis for memory
export REDIS_URL="redis://localhost:6379"
```

---

## VSCode Extension

Install the Empathy VSCode extension for:

- **Dashboard** - Health score, costs, patterns
- **One-Click Workflows** - Run from command palette
- **Memory Panel** - Manage Redis and patterns
- **Cost Tracking** - Real-time savings display

---

## Documentation

- [Quick Start Guide](docs/quickstart.md)
- [CLI Reference](docs/cli-reference.md)
- [Testing Guide](docs/testing-guide.md)
- [Keyboard Shortcuts](docs/keyboard-shortcuts.md)
- [Full Documentation](https://smartaimemory.com/framework-docs/)

---

## Security

- Path traversal protection on all file operations
- JWT authentication with rate limiting
- PII scrubbing in telemetry
- HIPAA/GDPR compliance options

See [SECURITY.md](SECURITY.md) for details.

---

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

---

## License

**Fair Source License 0.9** - Free for students, educators, and teams ≤5 employees. Commercial license for larger organizations. [Details →](LICENSE)

---

**Built by [Smart AI Memory](https://smartaimemory.com)** · [Docs](https://smartaimemory.com/framework-docs/) · [Examples](examples/) · [Issues](https://github.com/Smart-AI-Memory/empathy-framework/issues)
