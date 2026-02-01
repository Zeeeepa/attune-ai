---
name: pr-review
description: "Pull request review. Triggers: 'review PR', 'review pull request', 'check my PR', 'PR feedback', 'diff review', 'merge review', 'GitHub PR', 'review changes', 'what does this PR do', 'PR description'."
---

# PR Review

AI-powered pull request analysis and review.

## Quick Start

```bash
# CLI
attune workflow run pr-review --pr 123

# Legacy alias
empathy workflow run pr-review --pr 123
```

## Usage

### Via Script

```bash
python scripts/run.py --pr 123 --repo owner/repo
```

### Via Python

```python
from attune.workflows import PRReviewWorkflow

workflow = PRReviewWorkflow()
result = await workflow.execute(pr_number=123)
print(result.review)
```

## Features

- Diff analysis with context
- Breaking change detection
- Test coverage impact
- Security implications
- Suggested improvements
- Auto-generated PR description

## Output

- Summary of changes
- Risk assessment
- Review comments (inline-ready)
- Approval recommendation
