---
name: workflow
description: Development workflow hub - planning, TDD, review, refactoring
category: hub
aliases: [wf]
tags: [workflow, development, planning, hub]
version: "2.0"
---

# Development Workflows

**Aliases:** `/wf`

Structured approaches for common development tasks.

## Quick Examples

```bash
/workflow                      # Interactive menu
/workflow "plan auth feature"  # Start planning
/workflow "refactor utils"     # Start refactoring
```

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

---

## Plan Implementation

Create a plan with structured Socratic discovery before coding.

### Step 1: Understand the Change

```yaml
Question:
  header: "Change Type"
  question: "What kind of change are you planning?"
  options:
    - label: "New feature"
      description: "Adding entirely new functionality"
    - label: "Enhancement"
      description: "Improving or extending existing functionality"
    - label: "Bug fix"
      description: "Correcting broken behavior"
    - label: "Refactor"
      description: "Restructuring without changing behavior"
```

### Step 2: Clarify Constraints

```yaml
Question:
  header: "Constraints"
  question: "What constraints should I consider?"
  multiSelect: true
  options:
    - label: "Backward compatible"
      description: "Must not break existing APIs or behavior"
    - label: "Performance critical"
      description: "Speed or memory usage is important"
    - label: "Security sensitive"
      description: "Handles auth, user data, or system access"
    - label: "Minimal changes"
      description: "Prefer smallest possible footprint"
```

### Step 3: Socratic Exploration

After reading the codebase, I'll ask clarifying questions like:

**For patterns:**
"I see the codebase uses [pattern X] for similar features. Should we follow this pattern, or is there a reason to do something different?"

**For trade-offs:**

"There are two approaches here:

- Option A: [description] - simpler but less flexible
- Option B: [description] - more complex but extensible

What matters more for this feature: simplicity or flexibility?"

**For scope:**
"This change will touch [X, Y, Z]. Are all of these okay to modify, or should some be off-limits?"

### Step 4: Plan Approval

Before any code changes, I'll present:

1. Summary of what I understood
2. Files I plan to modify
3. Step-by-step approach
4. Risks or concerns

**This enters Plan Mode** - I'll research thoroughly and get your approval before proceeding.

---

## Test-Driven Development

Write tests first, then implement (Red-Green-Refactor).

**Tell me:**

- What functionality to implement
- Expected behavior and edge cases

**I will:**

1. **RED:** Write failing tests that define expected behavior
2. Run tests to confirm they fail
3. **GREEN:** Write minimal code to make tests pass
4. Run tests to confirm they pass
5. **REFACTOR:** Improve code while keeping tests green
6. Repeat for each requirement

**TDD benefits:**

- Clear requirements before coding
- Confidence in correctness
- Built-in regression tests
- Better design through testability

---

## Code Review

Review code using Socratic questioning to help you understand issues.

### Step 1: Review Focus

```yaml
Question:
  header: "Focus"
  question: "What kind of review do you need?"
  options:
    - label: "Quick sanity check"
      description: "High-level review for obvious issues"
    - label: "Thorough review"
      description: "Deep dive into all aspects"
    - label: "Security focused"
      description: "Priority on vulnerabilities and risks"
    - label: "Learning review"
      description: "Help me understand best practices"
```

### Step 2: Socratic Feedback

> **Philosophy:** Teach, don't just tell

Instead of: "Line 42 has a bug"
I'll ask: "What do you think happens when `users` is empty on line 42?"

Instead of: "This violates DRY"
I'll ask: "I notice similar logic in these 3 places. What might happen if we need to change this behavior?"

Instead of: "Security issue here"
I'll ask: "Let's trace how user input flows through this function. What validation happens before line 78?"

### Step 3: Guided Discovery

For each issue found, I'll guide your understanding:

```text
"Looking at getUserProfile() on line 47.
What happens if the user doesn't exist?"

[Wait for your response]

"And on line 52, you're accessing user.email.
What would happen if getUserProfile returned null?"
```

**I will:**

1. Read and understand the code
2. Identify issues through questions, not lectures
3. Help you discover problems yourself
4. Explain the *why*, not just the *what*
5. Highlight what's done well (reinforce good patterns)

---

## Refactor Code

Restructure code without changing behavior.

**Tell me:**

- What code to refactor
- Why (code smell, performance, readability)

**I will:**

1. Understand current behavior
2. Ensure tests exist (or create them)
3. Apply refactoring patterns:
   - Extract method/class
   - Rename for clarity
   - Remove duplication
   - Simplify conditionals
4. Verify behavior unchanged
5. Run tests after each change

**Safety first:** Refactoring without tests is risky.

---

## Workflow Selection Guide

```text
Need to build something new?
  ├─ Complex feature → Plan first, then TDD
  └─ Simple feature → TDD directly

Need to improve existing code?
  ├─ Quality concerns → Review first
  └─ Structure issues → Refactor

Need both?
  └─ Review → identify issues → Refactor → TDD for new tests
```

---

## Invoke Socratic Agents

For deeper analysis, invoke specialized agents via `/agent`:

| Agent          | Use When                                            |
| -------------- | --------------------------------------------------- |
| **planner**    | Complex requirements discovery, sprint planning     |
| **architect**  | System design decisions, technology choices         |
| **refactorer** | Code improvement with pattern guidance and examples |

**Example:** `/agent "invoke planner for user authentication feature"`

---

## When NOT to Use This Hub

| If you need...       | Use instead |
| -------------------- | ----------- |
| Run existing tests   | `/testing`  |
| Create commit/PR     | `/dev`      |
| Write documentation  | `/docs`     |
| Deploy changes       | `/release`  |

## Related Hubs

- `/dev` - Debugging, commits, PRs
- `/testing` - Run tests, coverage
- `/docs` - Documentation
- `/agent` - Invoke planner, architect, refactorer agents
