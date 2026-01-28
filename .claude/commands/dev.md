---
name: dev
description: Developer tools hub - debugging, commits, PRs, code review, refactoring
category: hub
aliases: [developer]
tags: [development, git, debugging, quality, hub]
version: "3.0"
question:
  header: "Task"
  question: "What development task do you need?"
  multiSelect: false
  options:
    - label: "🐛 Debug & analyze"
      description: "Investigate bugs, review code, refactor with guidance"
    - label: "📝 Git operations"
      description: "Create commits, pull requests, manage branches"
    - label: "✅ Quality check"
      description: "Run linting, type checking, security scans"
    - label: "⚡ Performance"
      description: "Profile code, identify bottlenecks, optimize"
---

# Developer Tools

**Aliases:** `/developer`

Development operations powered by Socratic agents that guide you through discovery.

---

**Based on your selection, I will:**

- **🐛 Debug issue** → Use the debugger agent with Socratic questioning to help you discover root causes
- **👀 Review code** → Use the code-reviewer agent to provide teaching-focused quality review
- **🔧 Refactor code** → Use the refactorer agent to guide structural improvements
- **📝 Git commit** → Stage files and create a well-formatted commit
- **🚀 Create PR** → Push changes and create a pull request with summary
- **✅ Quality check** → Run linters, type checking, and security scans

---

## Quick Direct Access

You can also invoke sub-commands directly:

```bash
/dev debug                # Start debugging
/dev review               # Code review
/dev refactor             # Refactoring
/dev commit               # Git commit
/dev pr                   # Create PR
/dev quality              # Quality check
```

---

## Debug Issue

**Agent:** `debugger` | **Workflow:** `bug_predict`

Guided debugging that helps you discover root causes yourself, not just fixes.

**Invoke:**
```bash
/dev debug                           # Start interactive debugging
/dev debug "login fails sometimes"   # With context
```

**The debugger agent will:**
1. Ask what unexpected behavior you're seeing
2. Gather context (error messages, reproduction steps)
3. Form a hypothesis together with you
4. Guide you through tracing the issue step by step
5. Help you understand *why* the fix works
6. Connect the bug to patterns for future prevention

**Philosophy:** Instead of "The bug is on line 42", you'll hear "Let's trace the execution. What value does `user_id` have when we reach line 40?"

---

## Review Code

**Agent:** `code-reviewer` | **Workflow:** `code_review`

Code review that teaches, not just critiques.

**Invoke:**
```bash
/dev review                    # Review recent changes
/dev review src/auth/          # Review specific path
/dev review --pr 123           # Review a pull request
```

**The code-reviewer agent will:**
1. Ask what kind of review you need (quick check, thorough, security-focused, learning)
2. Identify focus areas together (logic, error handling, performance, readability)
3. Guide you through discoveries using questions, not statements
4. Help you understand the *why* behind each finding
5. Offer next steps: fix checklist, explain patterns, or pair on fixes

**Philosophy:** Instead of "This violates DRY", you'll hear "I notice similar logic in these 3 places. What might happen if we need to change this behavior?"

---

## Refactor Code

**Agent:** `refactorer` | **Workflow:** `refactor_plan`

Refactoring guidance that helps you see code smells and discover better structures.

**Invoke:**
```bash
/dev refactor                           # Start refactoring session
/dev refactor src/services/order.py     # Refactor specific file
/dev refactor "this class is too big"   # With context
```

**The refactorer agent will:**
1. Understand what's driving the refactoring (hard to understand, change, or test)
2. Assess test coverage and safety
3. Guide you to see the code smell yourself
4. Explore solutions together, weighing trade-offs
5. Plan small, safe steps with verification between each

**Philosophy:** Instead of "This function is too long, split it", you'll hear "If you had to explain this function to someone, how many different things would you describe?"

---

## Git Operations

Direct actions for version control (no agent needed).

### Create Commit

```bash
/dev commit                    # Stage and commit changes
/dev commit "fix auth bug"     # With message hint
```

**I will:**
1. Run `git status` and `git diff` to review changes
2. Check recent commits for style consistency
3. Stage appropriate files (excluding secrets, large binaries)
4. Create commit with descriptive message following project conventions

**Commit format:**
```text
<type>: <short description>

<optional body explaining why>

Co-Authored-By: Claude <noreply@anthropic.com>
```

### Create PR

```bash
/dev pr                        # Create pull request
/dev pr "Add user dashboard"   # With title hint
```

**I will:**
1. Check branch status and push if needed
2. Review all commits since branching from main
3. Create PR with summary and test plan

### Review PR

```bash
/dev pr review 123             # Review PR #123
/dev pr review <url>           # Review PR by URL
```

**I will:**
1. Fetch PR details and diff
2. Invoke the **code-reviewer agent** for thorough analysis
3. Provide structured feedback with specific suggestions

---

## Quality Check

**Agent:** `quality-validator` | **Workflows:** linting, security, type checking

Quick quality validation for code.

**Invoke:**
```bash
/dev quality                   # Check recent changes
/dev quality src/api/          # Check specific path
```

**I will:**
1. Run linters (ruff, black)
2. Check type hints (mypy)
3. Scan for security issues (bandit)
4. Review against project coding standards
5. Report findings with fix suggestions

---

## Agent-Skill-Workflow Mapping

| Skill | Agent | Workflow | When to Use |
|-------|-------|----------|-------------|
| `/dev debug` | debugger | bug_predict | Investigating any bug or unexpected behavior |
| `/dev review` | code-reviewer | code_review | Reviewing code for quality, security, patterns |
| `/dev refactor` | refactorer | refactor_plan | Improving code structure or addressing smells |
| `/dev quality` | quality-validator | (linting tools) | Quick automated quality checks |
| `/dev commit` | (none) | git operations | Creating commits |
| `/dev pr` | (none) | git operations | Creating/managing pull requests |

---

## When to Use Each Skill

```
I found a bug                    → /dev debug
I want feedback on my code       → /dev review
This code is hard to work with   → /dev refactor
Quick lint/type check            → /dev quality
Ready to commit                  → /dev commit
Ready to open PR                 → /dev pr
```

---

## When NOT to Use This Hub

| If you need...         | Use instead  |
|------------------------|--------------|
| Run tests              | `/testing`   |
| Write documentation    | `/docs`      |
| Release/deploy         | `/release`   |
| Plan a feature         | `/plan`      |
| Run automated analysis | `/workflows` |
| Manage context/memory  | `/context`   |

## Related Hubs

- `/testing` - Run tests, coverage, TDD
- `/workflows` - Run automated workflows (security-audit, bug-predict, etc.)
- `/plan` - Plan features, architecture
- `/release` - Prepare and publish releases
- `/agent` - Direct agent invocation
