---
name: docs
description: Documentation hub - explain code, manage docs, feature overviews
category: hub
aliases: [documentation]
tags: [documentation, explanation, hub]
version: "2.0"
---

# Documentation

**Aliases:** `/documentation`

Create, manage, and understand documentation.

## Quick Examples

```bash
/docs                         # Interactive menu
/docs "explain auth module"   # Get code explanation
/docs "update README"         # Manage docs
```

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

---

## Explain Code

Get a detailed explanation of how code works.

**Tell me:**

- File, function, or module to explain
- Your current understanding level
- Specific aspects you're curious about

**I will:**

1. Read and analyze the code
2. Explain the high-level purpose
3. Walk through the logic step by step
4. Highlight key patterns and decisions
5. Explain connections to other code
6. Answer follow-up questions

**Good for:**

- Onboarding to unfamiliar code
- Understanding complex algorithms
- Learning patterns used in codebase
- Reviewing before making changes

---

## Manage Documentation

Create, update, or organize documentation.

**Tell me:**

- What docs need work (README, API, guides)
- What's outdated or missing
- Target audience

**I will:**

1. Review existing documentation
2. Identify gaps and outdated sections
3. Draft new or updated content
4. Ensure consistency with code
5. Format appropriately (Markdown, docstrings)

**Documentation types:**

- README.md - Project overview
- API reference - Function/class docs
- Guides - How-to tutorials
- Architecture - System design
- CHANGELOG - Version history

---

## Feature Overview

Generate a high-level overview of a feature or module.

**Tell me:**

- Feature or module to document
- Target audience (users, developers, stakeholders)
- Desired depth (summary vs detailed)

**I will:**

1. Explore the relevant code
2. Identify key components
3. Document the purpose and scope
4. Explain how to use it
5. Note any limitations or caveats
6. Format for your audience

---

## When NOT to Use This Hub

| If you need...     | Use instead |
| ------------------ | ----------- |
| Fix code issues    | `/dev`      |
| Review code        | `/workflow` |
| Run tests          | `/testing`  |
| Deploy changes     | `/release`  |

## Related Hubs

- `/dev` - Commits, PRs, debugging
- `/workflow` - Code review, refactoring
- `/learning` - Pattern documentation
