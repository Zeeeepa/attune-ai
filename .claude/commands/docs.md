---
name: docs
description: Documentation hub - explain code, manage docs, feature overviews
category: hub
aliases: [documentation]
tags: [documentation, explanation, hub]
version: "1.0"
---

# Documentation

Create, manage, and understand documentation.

## Discovery

```yaml
Question:
  header: "Task"
  question: "What documentation task do you need?"
  options:
    - label: "Explain code"
      description: "Get an explanation of how code works"
    - label: "Manage documentation"
      description: "Create, update, or organize docs"
    - label: "Feature overview"
      description: "Generate overview of a feature or module"
```

## Routing

Based on selection:

| Selection | Command | Description |
|-----------|---------|-------------|
| Explain code | `/explain` | Detailed code explanation |
| Manage documentation | `/manage-docs` | Documentation management |
| Feature overview | `/feature-overview` | High-level feature summary |

## Quick Access

- `/explain path/to/file.py` - Explain specific code
- `/explain function_name` - Explain a function
- `/manage-docs` - Start doc management
- `/feature-overview "feature"` - Generate feature overview

## Documentation Types

| Type | Use Case | Command |
|------|----------|---------|
| Code explanation | Understanding unfamiliar code | `/explain` |
| API docs | Documenting public interfaces | `/manage-docs` |
| Feature docs | User-facing documentation | `/feature-overview` |
| Architecture | System design docs | `/manage-docs` |

## When to Use Each

**Use `/explain` when:**

- Onboarding to new codebase
- Understanding complex logic
- Reviewing unfamiliar code
- Learning patterns used

**Use `/manage-docs` when:**

- Docs need updating
- Creating new documentation
- Organizing existing docs
- Checking doc coverage

**Use `/feature-overview` when:**

- Documenting for users
- Creating release notes
- Stakeholder communication
- Feature handoff
