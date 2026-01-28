---
name: context
description: Context management hub - state, memory, status/profile
category: hub
aliases: [ctx]
tags: [context, memory, state, profile, hub]
version: "2.0"
question:
  header: "Context"
  question: "What context operation do you need?"
  multiSelect: false
  options:
    - label: "📊 Show status"
      description: "Display current session state, tasks, and context"
    - label: "💭 View memory"
      description: "Browse and search learned patterns and preferences"
    - label: "💾 Save state"
      description: "Preserve current state for later resumption"
    - label: "📝 Edit CLAUDE.md"
      description: "Update project memory and instructions"
---

# Context Management

**Aliases:** `/ctx`

Manage session context, state preservation, and memory.

## Quick Examples

```bash
/context                 # Interactive menu
/context "save state"    # Compact current context
/context "check memory"  # View stored memories
```

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

---

## Save State (Compact)

Preserve current state before context window resets.

**I will:**

1. Summarize current session progress
2. Extract key decisions and context
3. Generate SBAR handoff format:
   - **S**ituation: What we're working on
   - **B**ackground: Relevant history
   - **A**ssessment: Current state
   - **R**ecommendation: Next steps
4. Save to `.claude/compact-state.md`
5. Store in cross-session memory

**When to compact:**

- Context window getting full (~80%)
- Before a long break
- Significant milestone reached
- Handing off to another session

---

## Restore State

Load previously saved state from a past session.

**Tell me:**

- Session to restore (or use most recent)

**I will:**

1. Load compact state from memory
2. Restore the SBAR context
3. Resume from where we left off
4. Confirm understanding of current task

**Stored in:** `.claude/compact-state.md`

---

## Manage Memory

Store and retrieve persistent memory across sessions.

**Tell me:**

- What to store or retrieve
- Memory type (fact, preference, project info)

**I will:**

1. Access cross-session memory
2. Store new memories with context
3. Retrieve relevant memories
4. Update or delete as needed

**Memory types:**

- **Facts:** Project-specific information
- **Preferences:** Your coding style, tools
- **Patterns:** Learned behaviors
- **Context:** Project state

---

## Status & Profile

View session status or update your preferences.

**Status shows:**

- Current empathy level (1-5)
- Detected patterns
- Session progress
- Context usage

**Profile shows:**

- Your preferences
- Learned patterns
- Settings

**Tell me:**

- "status" to view current session
- "profile" to view/update preferences

---

## When NOT to Use This Hub

| If you need...     | Use instead  |
| ------------------ | ------------ |
| Create commits     | `/dev`       |
| Run tests          | `/testing`   |
| Plan features      | `/plan`      |
| Run workflows      | `/workflows` |
| Learn patterns     | `/learning`  |

## Related Hubs

- `/learning` - Pattern management
- `/agent` - Agent configuration
- `/dev` - Development tasks
