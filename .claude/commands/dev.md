---
name: dev
description: Developer tools hub - debugging, commits, PRs, code review, quality
category: hub
aliases: [developer]
tags: [development, git, debugging, quality, hub]
version: "2.0"
---

# Developer Tools

**Aliases:** `/developer`

Common development operations: debugging, version control, code review, quality validation.

## Quick Examples

```bash
/dev                     # Interactive menu
/dev "debug login error" # Jump to debugging with context
/dev "commit changes"    # Jump to commit workflow
```

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
    - label: "PR workflow"
      description: "Create or review a pull request"
    - label: "Quality check"
      description: "Validate code quality and style"
```

---

## Debug Issue

Systematic debugging workflow for investigating errors.

**Tell me:**

1. What error or unexpected behavior are you seeing?
2. When does it occur? (always, sometimes, specific conditions)
3. Any error messages or stack traces?

**I will:**

1. Analyze the error context
2. Search for related code and recent changes
3. Identify potential root causes
4. Suggest fixes with explanations
5. Help verify the fix works

**Tips:**

- Paste the full error message/stack trace
- Mention what you've already tried
- Share relevant file paths if known

---

## Create Commit

Stage changes and create a well-formatted git commit.

**I will:**

1. Run `git status` to see changes
2. Run `git diff` to review what changed
3. Check recent commit style for consistency
4. Stage appropriate files (not secrets or large binaries)
5. Create commit with descriptive message

**Commit message format:**

```text
<type>: <short description>

<optional body explaining why>

Co-Authored-By: Claude <noreply@anthropic.com>
```

**Types:** feat, fix, refactor, docs, test, chore

---

## Create PR

Create a pull request with summary and test plan.

**I will:**

1. Check current branch and remote status
2. Review all commits since branching from main
3. Push branch if needed
4. Create PR with:
   - Clear title
   - Summary of changes (bullet points)
   - Test plan checklist

**Before creating:**

- Ensure tests pass
- Ensure commits are clean
- Ensure branch is up to date

---

## Review PR

Review an existing pull request for quality and correctness.

**Tell me:**

- PR number or URL

**I will:**

1. Fetch PR details and diff
2. Review for:
   - Code correctness
   - Security issues
   - Performance concerns
   - Style consistency
   - Test coverage
3. Provide structured feedback
4. Suggest specific improvements

---

## Quality Check

Validate code quality, style, and best practices.

**Tell me:**

- File or directory to check (or leave blank for recent changes)

**I will:**

1. Run linters (ruff, black)
2. Check type hints (mypy)
3. Scan for security issues (bandit)
4. Review against coding standards
5. Report findings with fix suggestions

---

## When NOT to Use This Hub

| If you need...      | Use instead |
| ------------------- | ----------- |
| Run tests           | `/testing`  |
| Write documentation | `/docs`     |
| Release/deploy      | `/release`  |
| Plan a feature      | `/workflow` |
| Manage context      | `/context`  |

## Related Hubs

- `/testing` - Run tests, coverage, benchmarks
- `/workflow` - Plan features, TDD, refactoring
- `/release` - Prepare and publish releases
