---
name: context
description: Context management hub - state, memory, status/profile
category: hub
aliases: [ctx]
tags: [context, memory, state, profile, hub]
version: "1.0"
---

# Context Management

Manage session context, state preservation, and memory.

## Discovery

```yaml
Question:
  header: "Action"
  question: "What would you like to do with context?"
  options:
    - label: "Save state (compact)"
      description: "Preserve current state before context window resets"
    - label: "Restore state"
      description: "Load previously saved state from a past session"
    - label: "Manage memory"
      description: "Store and retrieve persistent memory across sessions"
    - label: "Status & profile"
      description: "View session status, patterns, or update preferences"
```

## Routing

Based on selection:

| Selection | Command | Description |
|-----------|---------|-------------|
| Save state | `/compact` | Save collaboration state with SBAR handoff |
| Restore state | `/restore` | Restore from previously compacted session |
| Manage memory | `/memory` | Access persistent memory storage |
| Status & profile | `/status` | View status, then `/profile` for preferences |

## Quick Access

If you know what you need:

- `/compact` - Save state now
- `/restore` - Restore previous state
- `/memory` - Access memory storage
- `/status` - Check current status
- `/profile` - View/update user profile

## When to Use Each

**Use `/compact` when:**

- Context window is getting full
- Before a long break
- Handing off to another session
- Important progress to preserve

**Use `/restore` when:**

- Starting a new session
- Continuing previous work
- Need to recover state

**Use `/memory` when:**

- Store important information persistently
- Retrieve facts from previous sessions
- Manage cross-session knowledge

**Use `/status` or `/profile` when:**

- Want to see current empathy level (`/status`)
- Check detected patterns (`/status`)
- Review session progress (`/status`)
- Update your preferences (`/profile`)
- Review your settings (`/profile`)
