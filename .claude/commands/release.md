---
name: release
description: Release hub - preparation, publishing, security scanning
category: hub
aliases: [ship]
tags: [release, publish, security, hub]
version: "2.0"
---

# Release Management

**Aliases:** `/ship`

Prepare, validate, and publish releases.

## Quick Examples

```bash
/release                 # Interactive menu
/release "prep 1.2.0"    # Prepare specific version
/release "security scan" # Run security checks
```

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

---

## Prepare Release

Generate changelog, bump version, and run pre-release checks.

**Tell me:**

- Target version (or "patch", "minor", "major")
- Any notable changes to highlight

**I will:**

1. Run all tests
2. Check for security vulnerabilities
3. Update version in pyproject.toml/package.json
4. Generate changelog from commits
5. Verify documentation is current
6. Create pre-release checklist

**Pre-release checklist:**

- [ ] All tests passing
- [ ] No security vulnerabilities
- [ ] Changelog updated
- [ ] Version bumped correctly
- [ ] Dependencies up to date
- [ ] Documentation current

---

## Publish Release

Publish to package registry (PyPI, npm, etc.).

**Tell me:**

- Registry to publish to (default: PyPI)
- Whether this is a pre-release

**I will:**

1. Verify release branch is ready
2. Build distribution packages
3. Validate package contents
4. Publish to registry
5. Create git tag
6. Create GitHub release (if applicable)

**Before publishing:**

- Ensure CI is green
- Release PR is merged
- Changelog is complete

---

## Security Scan

Scan for vulnerabilities before release.

**I will:**

1. Run `bandit` for Python security issues
2. Run `safety` for dependency vulnerabilities
3. Check for secrets in code (`detect-secrets`)
4. Review dependency licenses
5. Report findings with severity

**Checks performed:**

| Tool             | Checks                     |
| ---------------- | -------------------------- |
| bandit           | Python code vulnerabilities |
| safety           | Dependency CVEs            |
| detect-secrets   | Hardcoded secrets          |
| pip-audit        | Known vulnerabilities      |

---

## Release Workflow

```text
1. Security scan     → Check for vulnerabilities
2. Prepare release   → Version bump, changelog, checks
3. Create commit     → Commit release changes (/dev)
4. Create PR         → Create release PR (/dev)
5. Publish           → Publish after merge
```

---

## When NOT to Use This Hub

| If you need...   | Use instead |
| ---------------- | ----------- |
| Run tests        | `/testing`  |
| Create commits   | `/dev`      |
| Review code      | `/workflow` |
| Update docs      | `/docs`     |

## Related Hubs

- `/dev` - Create commits and PRs
- `/testing` - Run tests before release
- `/utilities` - Dependency audits
