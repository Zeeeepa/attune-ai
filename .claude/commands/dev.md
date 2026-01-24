---
name: dev
description: Developer tools hub - debugging, commits, PRs, code review, quality
category: hub
aliases: [developer]
tags: [development, git, debugging, quality, hub]
version: "1.1"
---

# Developer Tools

Common development operations: debugging, version control, code review, quality validation.

## Discovery

```yaml
Question:
  header: "Task"
  question: "What development task do you need?"
  options:
    - label: "Debug issue"
      description: "Investigate and fix a bug or error"
    - label: "Create commit"
      description: "Stage changes and create a git commit"
    - label: "Create PR"
      description: "Create a pull request for review"
    - label: "Review PR"
      description: "Review an existing pull request"
    - label: "Quality check"
      description: "Validate code quality and style"
```

## Routing

Based on selection:

| Selection | Command | Description |
|-----------|---------|-------------|
| Debug issue | `/debug` | Systematic debugging workflow |
| Create commit | `/commit` | Stage and commit with good message |
| Create PR | `/pr` | Create PR with summary and test plan |
| Review PR | `/review-pr` | Review an existing PR |
| Quality check | `/quality-validator` | Code quality and style analysis |

## Quick Access

- `/debug "error message"` - Debug specific error
- `/commit` - Create commit from staged changes
- `/pr` - Create pull request
- `/review-pr 123` - Review PR #123
- `/quality-validator path/to/file` - Validate code quality

## Related Hubs

For testing-related tasks, use the `/testing` hub:

- `/test` - Run tests
- `/test-coverage` - Coverage analysis
- `/benchmark` - Performance benchmarks

## Task Selection Guide

```
Found a bug?
  ├─ Know the cause → Fix directly
  └─ Unknown cause → /debug

Made changes?
  ├─ Ready to commit → /commit
  ├─ Need tests first → /testing
  └─ Ready for review → /pr

Want to review?
  └─ Review PR → /review-pr 123
```

## When to Use Each

**Use `/debug` when:**

- Error is unclear
- Need systematic investigation
- Complex bug reproduction
- Root cause analysis needed

**Use `/commit` when:**

- Changes are complete
- Tests pass
- Ready to save progress

**Use `/pr` when:**

- Feature complete
- Ready for review
- Need to merge changes

**Use `/review-pr` when:**

- Reviewing teammate's code
- Checking PR before merge
- Providing feedback
