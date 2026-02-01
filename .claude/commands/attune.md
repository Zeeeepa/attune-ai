---
name: attune
description: AI-powered developer workflows with Socratic discovery
category: primary
aliases: [a]
tags: [navigation, discovery, socratic]
version: "3.0"
question:
  header: "What brings you here?"
  question: "What are you trying to accomplish right now?"
  multiSelect: false
  options:
    - label: "🔧 Fix or improve something"
      description: "Debug issues, review code, refactor, or improve quality"
    - label: "✅ Validate my work"
      description: "Run tests, check coverage, audit security, or verify quality"
    - label: "🚀 Ship my changes"
      description: "Commit, create PR, prepare release, or publish"
    - label: "📚 Understand or document"
      description: "Explain code, generate docs, or learn patterns"
---

# attune

Your AI-powered developer workflow assistant with Socratic discovery.

**One command. Every workflow.**

## How It Works

Type `/attune` and I'll guide you through questions to find the right workflow.

```bash
/attune                              # Start Socratic discovery
/attune "I need to fix a bug"        # Natural language
/attune debug                        # Direct shortcut
```

## Workflows by Goal

### 🔧 Fix or Improve Something

**Debugging:**

- Investigate errors and exceptions
- Trace execution flow
- Identify root causes

**Code Review:**

- Quality and pattern analysis
- Security review
- Performance review

**Refactoring:**

- Improve structure and organization
- Extract functions/classes
- Simplify complex code

### ✅ Validate My Work

**Testing:**

- Run test suites
- Generate new tests
- TDD workflow

**Coverage:**

- Analyze test coverage
- Identify gaps
- Boost coverage

**Security Audit:**

- Vulnerability scanning
- Dependency analysis
- Code security review

**Performance Audit:**

- Identify bottlenecks
- Memory analysis
- Optimization recommendations

### 🚀 Ship My Changes

**Commit:**

- Stage and commit changes
- Generate commit messages
- Follow conventional commits

**Pull Request:**

- Create PR with description
- Review checklist
- Link to issues

**Release:**

- Version bump
- Changelog generation
- Security pre-checks
- Publish to registry

### 📚 Understand or Document

**Explain Code:**

- Understand how code works
- Trace through logic
- Learn patterns used

**Generate Docs:**

- API documentation
- README updates
- Architecture docs

**Feature Overview:**

- High-level summaries
- Component relationships
- Usage examples

## Quick Shortcuts

| Shortcut | Action |
| -------- | ------ |
| `/attune debug` | Start debugging session |
| `/attune review` | Code review |
| `/attune refactor` | Refactoring session |
| `/attune test` | Run tests |
| `/attune coverage` | Coverage analysis |
| `/attune security` | Security audit |
| `/attune commit` | Create commit |
| `/attune pr` | Create pull request |
| `/attune release` | Prepare release |
| `/attune docs` | Documentation |
| `/attune explain` | Explain code |

## Natural Language

Just describe what you need:

- "find security vulnerabilities"
- "why is this test failing"
- "generate tests for config.py"
- "review my authentication code"
- "prepare for release 2.0"
- "explain how caching works"
- "this function is too long"

## Philosophy

**Socratic over menus.** I ask "What are you trying to accomplish?" not "Which tool do you want?" This helps you think about your actual goal.

**Teaching over telling.** I help you understand *why*, not just *what*.
