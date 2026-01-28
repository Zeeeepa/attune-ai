---
name: learning
description: Learning hub - evaluate sessions, view patterns, teach preferences
category: hub
aliases: [learn-hub]
tags: [learning, patterns, memory, hub]
version: "2.1"
inline: true
question:
  header: "Learning"
  question: "What would you like to do?"
  multiSelect: false
  options:
    - label: "📊 Evaluate session"
      description: "Analyze current session and extract learnings"
    - label: "🔍 View patterns"
      description: "Browse learned debugging and refactoring patterns"
    - label: "📚 Teach preferences"
      description: "Add new preferences or update existing ones"
    - label: "💡 Suggest improvements"
      description: "Get recommendations based on session analysis"
---

# Learning Management

**Aliases:** `/learn-hub`

**IMPORTANT:** This command operates on the CURRENT conversation. Do NOT start a new conversation or clear context. You have full access to the conversation history above this point.

Manage continuous learning, pattern extraction, and preferences.

## Quick Examples

```bash
/learning                      # Interactive menu
/learning "evaluate session"   # Analyze for patterns
/learning "show patterns"      # View learned patterns
```

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

---

## Evaluate Session

Analyze the CURRENT session for learning opportunities.

**Context:** You have access to ALL messages in this conversation above this command. Use that history to identify patterns.

**I will:**

1. Review the conversation history IN THIS SESSION (all messages above)
2. Identify:
   - Corrections you made to my responses
   - Preferences you expressed (coding style, verbosity, etc.)
   - Effective approaches that worked well
   - Workarounds we discovered together
3. Extract patterns with confidence scores
4. Store valuable patterns to [patterns/](patterns/) or [.claude/rules/](.claude/rules/)
5. Report what was learned

**Best after:**

- Productive debugging sessions
- When you corrected my approach
- Discovering project conventions
- Finding effective solutions

**Note:** If invoked at the start of a session with no history, will report "no patterns to evaluate".

---

## View Patterns

See patterns learned from previous sessions.

**I will:**

1. Load pattern storage
2. Display patterns by category:
   - Preferences
   - Corrections
   - Workarounds
   - Project conventions
   - Error solutions
3. Show confidence and usage stats
4. Allow filtering and search

**Pattern categories:**

| Category       | Example                    |
| -------------- | -------------------------- |
| **Preference** | "I prefer concise code"    |
| **Correction** | "Actually, use X not Y"    |
| **Workaround** | "For this error, do Z"     |
| **Project**    | "We use kebab-case here"   |
| **Error**      | "This error means..."      |

---

## Teach Something

Manually teach a preference or pattern.

**Tell me:**

- What you want me to remember
- When it applies (always, in this project, for specific tasks)
- Why (helps me understand context)

**Examples:**

- "Always use type hints in Python"
- "In this project, we use tabs not spaces"
- "When I say 'fix', I mean fix without refactoring"
- "Remember: the API is at localhost:8080"

**I will:**

1. Parse your instruction
2. Categorize the pattern
3. Store with appropriate scope
4. Confirm what was learned
5. Apply immediately going forward

---

## When NOT to Use This Hub

| If you need...       | Use instead |
| -------------------- | ----------- |
| Save session state   | `/context`  |
| Create documentation | `/docs`     |
| Debug issues         | `/dev`      |
| Run tests            | `/testing`  |

## Related Hubs

- `/context` - State and memory management
- `/agent` - Agent pattern learning
- `/workflows` - Run automated workflows
- `/plan` - Development approaches (TDD, planning, review)
