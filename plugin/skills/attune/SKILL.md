---
name: attune
description: AI-powered developer workflows hub. Use this as the main entry point for attune-ai capabilities. Guides users through Socratic discovery to find the right workflow, or routes directly when intent is clear. Triggers on: "attune", "help me with code", "analyze my project", "developer workflow", "what can you help with".
---

# attune-ai

Main entry point for AI-powered developer workflows.

## Socratic Discovery

When user intent is unclear, guide through discovery:

### Step 1: Understand the Goal

Ask: **"What do you need help with?"**

| Option | Routes To |
|--------|-----------|
| Analyze code quality/security | → Analysis workflows |
| Improve testing | → Testing workflows |
| Prepare for release | → Release workflows |
| Review changes | → Review workflows |
| Generate documentation | → Documentation workflows |
| Something else | → Clarify further |

### Step 2: Narrow Down

Based on selection, ask follow-up:

**Analysis selected:**
- "What concerns you most? Security, bugs, performance, or all?"

**Testing selected:**
- "Do you want to generate new tests, improve coverage, or maintain existing tests?"

**Release selected:**
- "Full release prep, or specific checks (security scan, health check)?"

### Step 3: Gather Context

Before running, confirm:
- Target path (default: current directory)
- Any specific focus areas
- Output preferences

### Step 4: Execute

Route to appropriate workflow with gathered parameters.

---

## Direct Access (Power Users)

When intent is clear from natural language, skip Socratic flow and execute directly.

**Pattern matching:**

| User Says | Action |
|-----------|--------|
| "security audit on src/" | → security-audit --path src/ |
| "find bugs in api/" | → bug-predict --path api/ |
| "generate tests for config.py" | → test-gen --path config.py |
| "review my PR" | → pr-review |
| "prepare release" | → release-prep |
| "check dependencies" | → dependency-check |

---

## Available Workflows

### Analysis
- **security-audit**: Vulnerability scanning (OWASP Top 10)
- **bug-predict**: Predictive bug analysis
- **perf-audit**: Performance bottleneck detection
- **dependency-check**: Package security and health

### Testing
- **test-gen**: Generate unit tests
- **test-coverage**: Coverage analysis and improvement

### Code Quality
- **code-review**: Automated code review
- **pr-review**: Pull request analysis
- **refactor-plan**: Refactoring roadmap

### Release
- **release-prep**: Multi-agent release verification
- **health-check**: Parallel project health assessment

### Documentation
- **document-gen**: Auto-generate docs from code
- **research-synthesis**: Research and knowledge synthesis

### Utilities
- **batch-processing**: 50% cost savings via batch API

---

## CLI Reference

```bash
# Socratic mode (guided)
attune

# Direct execution
attune workflow run security-audit --path ./src
attune workflow run test-gen --path ./module.py
attune orchestrate release-prep

# Legacy aliases (backwards compatible)
empathy workflow run security-audit
```

---

## Cost Optimization

All workflows use 3-tier routing:

| Tier | Model | Use Case |
|------|-------|----------|
| CHEAP | Haiku | Triage, classification |
| CAPABLE | Sonnet | Analysis, generation |
| PREMIUM | Opus | Architecture, synthesis |

Typical savings: **34-86%** vs premium-only.

---

## More Info

- Website: https://attune-ai.org
- Docs: https://attune-ai.org/docs
- GitHub: https://github.com/Smart-AI-Memory/attune-ai
