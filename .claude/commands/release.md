---
name: release
description: Release hub - preparation, publishing, security scanning
category: hub
aliases: [ship]
tags: [release, publish, security, hub]
version: "1.0"
---

# Release Management

Prepare, validate, and publish releases.

## Discovery

```yaml
Question:
  header: "Task"
  question: "What release task do you need?"
  options:
    - label: "Prepare release"
      description: "Generate changelog, bump version, pre-release checks"
    - label: "Publish release"
      description: "Publish to package registry (PyPI, npm, etc.)"
    - label: "Security scan"
      description: "Scan for vulnerabilities before release"
```

## Routing

Based on selection:

| Selection | Command | Description |
|-----------|---------|-------------|
| Prepare release | `/release-prep` | Pre-release preparation workflow |
| Publish release | `/publish` | Publish to package registry |
| Security scan | `/security-scan` | Vulnerability scanning |

## Quick Access

- `/release-prep` - Start release preparation
- `/release-prep 1.2.0` - Prep specific version
- `/publish` - Publish to registry
- `/security-scan` - Run security checks

## Release Workflow

```
1. /security-scan     → Check for vulnerabilities
2. /release-prep      → Version bump, changelog, checks
3. /dev (commit)      → Commit release changes
4. /dev (pr)          → Create release PR
5. /publish           → Publish after merge
```

## Pre-Release Checklist

The `/release-prep` command verifies:

- [ ] All tests passing
- [ ] No security vulnerabilities
- [ ] Changelog updated
- [ ] Version bumped correctly
- [ ] Dependencies up to date
- [ ] Documentation current

## When to Use Each

**Use `/release-prep` when:**

- Ready to create a release
- Need to bump version
- Want automated changelog
- Running pre-release checks

**Use `/publish` when:**

- Release PR merged
- Ready to push to registry
- Want to tag release

**Use `/security-scan` when:**

- Before any release
- After adding dependencies
- Regular security audits
- CI/CD pipeline check
