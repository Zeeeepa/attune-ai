---
name: release
description: Release hub - preparation, security scanning, publishing
category: hub
aliases: [ship]
tags: [release, publish, security, hub]
version: "3.0"
---

# Release Management

**Aliases:** `/ship`

Release operations powered by Socratic agents that ensure quality and security before shipping.

## Quick Examples

```bash
/release                  # Interactive menu
/release prep             # Prepare release with quality checks
/release audit            # Deep security audit
/release publish          # Publish to registry
```

## Discovery

```yaml
Question:
  header: "Task"
  question: "What release task do you need?"
  options:
    - label: "Prepare release"
      description: "Version bump, changelog, pre-release checks"
    - label: "Security audit"
      description: "Deep vulnerability scan with attack scenarios"
    - label: "Publish release"
      description: "Publish to package registry"
```

---

## Prepare Release

**Agent:** `quality-validator` | **Workflow:** `release_prep`

Prepare a release with comprehensive quality validation.

**Invoke:**

```bash
/release prep                 # Interactive version selection
/release prep patch           # Bump patch version (1.0.0 → 1.0.1)
/release prep minor           # Bump minor version (1.0.0 → 1.1.0)
/release prep major           # Bump major version (1.0.0 → 2.0.0)
/release prep 2.0.0           # Specific version
```

**The quality-validator agent will:**

1. Run all tests and verify they pass
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

**Philosophy:** Instead of just running checks, you'll hear "Tests pass, but I notice coverage dropped 5% since last release. Should we add tests before shipping?"

---

## Security Audit

**Agent:** `security-reviewer` | **Workflow:** `security_audit`

Deep security audit with attack scenario analysis.

**Invoke:**

```bash
/release audit                # Full security audit
/release audit src/api/       # Audit specific module
/release audit --critical     # Focus on critical issues only
```

**The security-reviewer agent will:**

1. Run security scanners (bandit, safety, detect-secrets)
2. Guide you through understanding each finding
3. Ask: "If an attacker controlled this input, what could they do?"
4. Prioritize by actual exploitability, not just severity scores
5. Suggest mitigations with trade-off explanations

**Scans performed:**

| Tool | Checks |
|------|--------|
| bandit | Python code vulnerabilities |
| safety | Dependency CVEs |
| detect-secrets | Hardcoded secrets |
| pip-audit | Known vulnerabilities |

**Philosophy:** Instead of "B301: pickle usage detected", you'll hear "This pickle.load is on line 45. Let's trace: where does the data come from? Could an attacker influence it?"

---

## Publish Release

Direct action for publishing to package registries.

**Invoke:**

```bash
/release publish              # Publish to default registry (PyPI)
/release publish --test       # Publish to test registry first
/release publish npm          # Publish to npm
```

**I will:**

1. Verify release branch is ready
2. Build distribution packages
3. Validate package contents
4. Publish to registry
5. Create git tag
6. Create GitHub release (if applicable)

**Before publishing:**

- [ ] CI is green
- [ ] Release PR is merged
- [ ] Changelog is complete
- [ ] Version matches intended release

---

## Release Workflow

Typical release process:

```text
1. /release audit        → Check for vulnerabilities
2. /release prep         → Version bump, changelog, checks
3. /dev commit           → Commit release changes
4. /dev pr               → Create release PR
5. (merge PR)
6. /release publish      → Publish after merge
```

---

## Agent-Skill-Workflow Mapping

| Skill | Agent | Workflow | When to Use |
|-------|-------|----------|-------------|
| `/release prep` | quality-validator | release_prep | Preparing any release |
| `/release audit` | security-reviewer | security_audit | Pre-release security check |
| `/release publish` | (none) | publishing | Publishing to registries |

---

## When to Use Each Skill

```text
Ready to start release process  → /release prep
Need security validation        → /release audit
Ready to ship after PR merged   → /release publish
```

---

## When NOT to Use This Hub

| If you need...     | Use instead |
|--------------------|-------------|
| Run tests          | `/testing` |
| Create commits     | `/dev commit` |
| Review code        | `/dev review` |
| Update docs        | `/docs` |

## Related Hubs

- `/dev` - Create commits and PRs
- `/testing` - Run tests before release
- `/docs` - Update documentation
- `/agent` - Direct agent invocation
