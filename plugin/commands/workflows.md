---
name: workflows
description: Run automated AI workflows with cost-optimized 3-tier model routing
aliases: [wf, workflow]
---

# Automated Workflows

Run cost-optimized AI workflows for security, testing, and code analysis.

## Quick Start

```bash
/workflows                           # Interactive menu
/workflows security-audit            # Run security analysis
/workflows bug-predict ./src         # Predict bugs in src/
```

## Available Workflows

| Workflow | Description |
|----------|-------------|
| `security-audit` | Vulnerability detection (OWASP Top 10) |
| `bug-predict` | Predictive bug analysis |
| `perf-audit` | Performance bottleneck detection |
| `code-review` | Automated code review |
| `test-gen` | Test generation with coverage |
| `release-prep` | Multi-agent release preparation |

## Natural Language

Use plain English:
- "find security vulnerabilities" → security-audit
- "check code performance" → perf-audit
- "predict bugs" → bug-predict

## Cost Tiers

| Tier | Model | Used For |
|------|-------|----------|
| CHEAP | Haiku | Triage, classification |
| CAPABLE | Sonnet | Analysis, generation |
| PREMIUM | Opus | Architecture, synthesis |

Typical savings: 34-86% vs premium-only.
