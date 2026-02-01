---
name: attune
description: AI-powered developer workflows with Socratic discovery
aliases: [a]
---

# attune-ai

Your AI-powered developer workflow assistant.

## How It Works

**New to attune?** Just type `/attune` and I'll guide you through discovering the right workflow for your needs.

**Know what you want?** Just describe it naturally:
- "find security vulnerabilities in src/"
- "generate tests for config.py"
- "prepare for release"

## Guided Discovery

```
/attune

→ What do you need help with?
  1. Analyze code (security, bugs, performance)
  2. Improve testing
  3. Prepare for release
  4. Review changes
  5. Generate documentation
```

## Direct Access

Skip the menu - just ask:

| Say This | Runs This |
|----------|-----------|
| "security audit on src/" | security-audit |
| "find bugs" | bug-predict |
| "check performance" | perf-audit |
| "generate tests" | test-gen |
| "review my code" | code-review |
| "prepare release" | release-prep |

## All Workflows

**Analysis**: security-audit, bug-predict, perf-audit, dependency-check
**Testing**: test-gen, test-coverage
**Code**: code-review, pr-review, refactor-plan
**Release**: release-prep, health-check
**Docs**: document-gen, research-synthesis
**Utils**: batch-processing

## CLI

```bash
# Primary
attune workflow run <name> [options]
attune orchestrate <name>

# Legacy (still works)
empathy workflow run <name>
```

## More Info

https://attune-ai.org
