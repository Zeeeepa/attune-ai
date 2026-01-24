---
name: learning
description: Learning hub - evaluate sessions, view patterns, teach preferences
category: hub
aliases: [learn-hub]
tags: [learning, patterns, memory, hub]
version: "1.0"
---

# Learning Management

Manage continuous learning, pattern extraction, and preferences.

## Discovery

```yaml
Question:
  header: "Action"
  question: "What would you like to do with learning?"
  options:
    - label: "Evaluate session"
      description: "Analyze current session for learning opportunities"
    - label: "View patterns"
      description: "See patterns learned from previous sessions"
    - label: "Teach something"
      description: "Manually teach a preference or pattern"
```

## Routing

Based on selection:

| Selection | Command | Description |
|-----------|---------|-------------|
| Evaluate session | `/evaluate` | Assess session quality and extract patterns |
| View patterns | `/patterns` | List all learned patterns for your user |
| Teach something | `/learn` | Explicitly teach a preference or rule |

## Quick Access

- `/evaluate` - Evaluate current session
- `/patterns` - View learned patterns
- `/learn "preference"` - Teach a preference directly

## Learning Categories

Patterns are categorized as:

| Category | Example |
|----------|---------|
| **Preference** | "I prefer concise code" |
| **Correction** | "Actually, use X not Y" |
| **Workaround** | "For this error, do Z" |
| **Project** | "We use kebab-case here" |
| **Error** | "This error means..." |

## When to Use Each

**Use `/evaluate` when:**

- Session had valuable corrections
- Want to extract patterns automatically
- Before ending a productive session

**Use `/patterns` when:**

- Curious what's been learned
- Want to verify a pattern exists
- Debugging unexpected behavior

**Use `/learn` when:**

- Have a clear preference to teach
- Want immediate pattern capture
- Correcting a misunderstanding
