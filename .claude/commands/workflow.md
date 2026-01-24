---
name: workflow
description: Development workflow hub - planning, TDD, review, refactoring
category: hub
aliases: [wf]
tags: [workflow, development, planning, hub]
version: "1.0"
---

# Development Workflows

Structured approaches for common development tasks.

## Discovery

```yaml
Question:
  header: "Workflow"
  question: "What development workflow do you need?"
  options:
    - label: "Plan implementation"
      description: "Create a plan with Socratic discovery before coding"
    - label: "Test-driven development"
      description: "Write tests first, then implement (Red-Green-Refactor)"
    - label: "Code review"
      description: "Review code for quality, security, and best practices"
    - label: "Refactor code"
      description: "Restructure code without changing behavior"
```

## Routing

Based on selection:

| Selection | Command | Description |
|-----------|---------|-------------|
| Plan implementation | `/plan` | Socratic planning with explicit approval |
| Test-driven development | `/tdd` | Red-Green-Refactor cycle |
| Code review | `/review` | Comprehensive code review |
| Refactor code | `/refactor` | Safe restructuring with tests |

## Quick Access

- `/plan "feature"` - Plan a feature implementation
- `/tdd "feature"` - Start TDD for a feature
- `/review path/to/file` - Review specific code
- `/refactor path/to/file` - Refactor specific code

## Workflow Selection Guide

```
Need to build something new?
  ├─ Complex feature → /plan first, then /tdd
  └─ Simple feature → /tdd directly

Need to improve existing code?
  ├─ Quality concerns → /review first
  └─ Structure issues → /refactor

Need both?
  └─ /review → identify issues → /refactor → /tdd for new tests
```

## When to Use Each

**Use `/plan` when:**

- Building non-trivial features
- Multiple implementation approaches exist
- Need stakeholder alignment
- Architectural decisions required

**Use `/tdd` when:**

- Clear requirements exist
- Want confidence in code
- Building testable functionality
- Practicing disciplined development

**Use `/review` when:**

- Before merging code
- Inheriting unfamiliar code
- Security-sensitive changes
- Performance concerns

**Use `/refactor` when:**

- Code smells identified
- Preparing for new features
- Improving testability
- Reducing duplication
