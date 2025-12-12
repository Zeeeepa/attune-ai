# Empathy

**AI that predicts problems before they happen.**

[![PyPI](https://img.shields.io/pypi/v/empathy)](https://pypi.org/project/empathy/)
[![Tests](https://img.shields.io/badge/tests-2%2C040%2B%20passing-brightgreen)](https://github.com/Smart-AI-Memory/empathy/actions)
[![Coverage](https://codecov.io/gh/Smart-AI-Memory/empathy/branch/main/graph/badge.svg)](https://codecov.io/gh/Smart-AI-Memory/empathy)
[![License](https://img.shields.io/badge/license-Fair%20Source%200.9-blue)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.10+-blue)](https://www.python.org)
[![GitHub stars](https://img.shields.io/github/stars/Smart-AI-Memory/empathy?style=social)](https://github.com/Smart-AI-Memory/empathy)

Most AI tools are **reactive** - they wait for you to ask, then respond. Empathy is **anticipatory** - it predicts what you'll need and warns you before problems happen.

```bash
pip install empathy
```

## What It Does

- **🔮 Predicts issues 30-90 days ahead** - Security vulnerabilities, performance bottlenecks, compliance gaps
- **🧠 Learns patterns across domains** - Healthcare handoff protocols → deployment safety checks
- **🔌 Works with any LLM** - Claude, GPT-4, Gemini, local models via Ollama
- **🏥 Enterprise-ready** - PII scrubbing, audit logging, HIPAA/GDPR compliant
- **📦 2,000+ downloads** on PyPI, 2,040+ tests passing

## Quick Example

```python
from empathy_os import EmpathyOS

os = EmpathyOS()

# Analyze code for current AND future issues
result = await os.collaborate(
    "Review this deployment pipeline for problems",
    context={"code": pipeline_code, "team_size": 10}
)

# Get predictions, not just analysis
print(result.current_issues)      # What's wrong now
print(result.predicted_issues)    # What will break in 30-90 days
print(result.prevention_steps)    # How to prevent it
```

## The 5 Levels of AI Empathy

| Level | Name | Behavior | Example |
|-------|------|----------|---------|
| 1 | Reactive | Responds when asked | "Here's the data you requested" |
| 2 | Guided | Asks clarifying questions | "What format do you need?" |
| 3 | Proactive | Notices patterns | "I pre-fetched what you usually need" |
| **4** | **Anticipatory** | **Predicts future needs** | **"This query will timeout at 10k users"** |
| 5 | Transformative | Builds preventing structures | "Here's a framework for all future cases" |

**Empathy operates at Level 4** - predicting problems before they manifest.

## Why Empathy?

| | Empathy | SonarQube | GitHub Copilot |
|---|---------|-----------|----------------|
| **Predicts future issues** | ✅ 30-90 days ahead | ❌ | ❌ |
| **Cross-domain learning** | ✅ Healthcare → Software | ❌ | ❌ |
| **Source available** | ✅ Fair Source 0.9 | ❌ | ❌ |
| **Free for small teams** | ✅ ≤5 employees | ❌ | ❌ |
| **Local/air-gapped** | ✅ Ollama support | ❌ | ❌ |

## Get Involved

**⭐ [Star this repo](https://github.com/Smart-AI-Memory/empathy)** if you find it useful

**💬 [Join Discussions](https://github.com/Smart-AI-Memory/empathy/discussions)** - Questions, ideas, show what you built

**📖 [Read the Book](https://smartaimemory.com/book)** - Deep dive into the philosophy and implementation

**📚 [Full Documentation](docs/)** - API reference, examples, guides

## Install Options

```bash
# Basic
pip install empathy

# With all features (recommended)
pip install empathy[full]

# Development
git clone https://github.com/Smart-AI-Memory/empathy.git
cd empathy && pip install -e .[dev]
```

## What's Included

- **30+ Wizards** - Security, performance, testing, accessibility, compliance
- **Healthcare Suite** - SBAR, SOAP notes, clinical protocols (HIPAA compliant)
- **IDE Plugins** - VS Code and JetBrains extensions (examples/)
- **Enterprise Security** - PII scrubbing, secrets detection, audit logging

## License

**Fair Source License 0.9** - Free for students, educators, and teams ≤5 employees. Commercial license ($99/dev/year) for larger organizations. [Details →](LICENSE)

---

**Built by [Smart AI Memory](https://smartaimemory.com)** · [Documentation](docs/) · [Examples](examples/) · [Issues](https://github.com/Smart-AI-Memory/empathy/issues)
