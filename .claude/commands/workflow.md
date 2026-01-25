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

Create a plan with Socratic discovery before coding.

**Tell me:**

- What feature or change you want to implement
- Any constraints or requirements

**I will:**

1. Ask clarifying questions about requirements
2. Explore the codebase for relevant patterns
3. Identify architectural considerations
4. Present implementation options with trade-offs
5. Create a step-by-step plan
6. Get your approval before proceeding

**This enters Plan Mode** - I'll research thoroughly before proposing changes.

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

Review code for quality, security, and best practices.

**Tell me:**

- File or directory to review
- Focus areas (security, performance, style)

**I will:**

1. Read and understand the code
2. Check for:
   - Correctness and logic errors
   - Security vulnerabilities
   - Performance issues
   - Style and consistency
   - Test coverage
3. Provide structured feedback
4. Suggest specific improvements
5. Highlight what's done well

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
