# Attune AI Command Reference

**One command. Every workflow.**

## /attune

The single entry point for all Attune AI workflows. Uses Socratic discovery to guide you to the right tool.

### Usage

```bash
/attune                              # Start Socratic discovery
/attune "I need to fix a bug"        # Natural language
/attune security                     # Direct shortcut
```

### Shortcuts

| Shortcut | What It Does |
| -------- | ------------ |
| `/attune security` | Run security audit (OWASP Top 10) |
| `/attune test` | Run test suite |
| `/attune coverage` | Analyze test coverage |
| `/attune perf` | Performance audit |
| `/attune review` | Code review |
| `/attune bug-predict` | Predictive bug analysis |
| `/attune test-gen` | Generate tests |
| `/attune commit` | Create commit |
| `/attune pr` | Create pull request |
| `/attune release` | Prepare release |
| `/attune debug` | Start debugging session |
| `/attune refactor` | Refactoring assistance |
| `/attune docs` | Generate documentation |
| `/attune explain` | Explain code |

### Natural Language

Just describe what you need:

```bash
/attune "find security vulnerabilities"
/attune "why is this test failing"
/attune "generate tests for config.py"
/attune "review my authentication code"
/attune "prepare for release 2.0"
```

---

## Available Workflows

| Workflow | Description | Shortcut |
| -------- | ----------- | -------- |
| `security-audit` | Vulnerability detection (OWASP Top 10) | `/attune security` |
| `perf-audit` | Performance bottleneck detection | `/attune perf` |
| `code-review` | Automated code review | `/attune review` |
| `bug-predict` | Predictive bug analysis | `/attune bug-predict` |
| `test-gen` | Test generation with coverage | `/attune test-gen` |
| `release-prep` | Multi-agent release preparation | `/attune release` |

---

## Cost Tiers

All workflows use smart tier routing to minimize costs:

| Tier | Model | Used For | Cost |
| ---- | ----- | -------- | ---- |
| CHEAP | Haiku | Triage, classification | $ |
| CAPABLE | Sonnet | Analysis, generation | $$ |
| PREMIUM | Opus | Architecture, synthesis | $$$ |

**Typical savings:** 34-86% vs premium-only.

---

## CLI Reference

If you prefer CLI over slash commands:

```bash
# Workflows
uv run attune workflow run security-audit --path src/
uv run attune workflow run perf-audit --path src/
uv run attune workflow run code-review --path src/
uv run attune workflow run bug-predict --path src/
uv run attune workflow run test-gen --path src/
uv run attune workflow run release-prep

# Testing
uv run pytest
uv run pytest --cov=src --cov-report=term-missing

# View costs
uv run attune telemetry show
```

---

## Quick Reference

```text
┌─────────────────────────────────────────────────────────────┐
│                    /attune COMMAND                          │
├─────────────────────────────────────────────────────────────┤
│ /attune              Start Socratic discovery               │
│ /attune security     Run security audit                     │
│ /attune test         Run tests                              │
│ /attune coverage     Check test coverage                    │
│ /attune perf         Performance audit                      │
│ /attune review       Code review                            │
│ /attune commit       Create commit                          │
│ /attune release      Prepare release                        │
└─────────────────────────────────────────────────────────────┘
```
