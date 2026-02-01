---
name: code-review
description: "Automated code review. Triggers: 'review my code', 'code review', 'check my implementation', 'feedback on code', 'best practices', 'code quality', 'style check', 'lint', 'critique this code', 'what's wrong with this code'."
---

# Code Review

AI-powered code review with actionable feedback.

## Quick Start

```bash
# CLI (primary)
attune workflow run code-review --path ./src

# Legacy alias
empathy workflow run code-review --path ./src

# Natural language:
"review my code in src/"
"give me feedback on this implementation"
"check code quality"
```

## Usage

### Via MCP Tool

The `code_review` tool is available via MCP:

```python
# Invoked automatically when you describe:
"Review this code"
"Check my implementation"
"Give feedback on my changes"
```

### Via Python

```python
from attune.workflows import CodeReviewWorkflow

workflow = CodeReviewWorkflow()
result = await workflow.execute(target_path="./src/module.py")
print(result.suggestions)
```

## Review Categories

- **Style**: Naming conventions, formatting, consistency
- **Logic**: Potential bugs, edge cases, error handling
- **Performance**: Inefficiencies, optimization opportunities
- **Security**: Vulnerability patterns, unsafe practices
- **Maintainability**: Complexity, documentation, testability

## Output

Returns structured review with:
- Issue severity and category
- Specific file and line references
- Explanation of the issue
- Suggested fix with code examples
