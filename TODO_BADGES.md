# 📋 Badge Tasks & Reminders

**Created:** November 12, 2025
**Target Completion:** November 13-14, 2025
**Status:** ⏳ Waiting for badge services to index package

---

## 🎯 Primary Task: Restore Dynamic Badges

**Due Date:** November 13-14, 2025 (48 hours after PyPI publish)

### Task Checklist:

- [ ] **Day 1 (Nov 13)** - Test if badges are indexed
  - [ ] Test PyPI version badge: https://img.shields.io/pypi/v/empathy-framework.svg
  - [ ] Test Python versions badge: https://img.shields.io/pypi/pyversions/empathy-framework.svg
  - [ ] Test downloads badge: https://img.shields.io/pypi/dm/empathy-framework.svg
  - [ ] If all return valid images (not errors), proceed to restore

- [ ] **Restore Badges in README.md**
  - [ ] Replace simplified badges with full dynamic badges
  - [ ] Test all badge URLs in browser
  - [ ] Verify they display correctly on GitHub
  - [ ] Commit and push changes

- [ ] **Verify on GitHub**
  - [ ] Check README displays correctly
  - [ ] All badges show proper status
  - [ ] No broken images

- [ ] **Clean Up**
  - [ ] Delete BADGES_REMINDER.md
  - [ ] Delete this TODO_BADGES.md file
  - [ ] Commit cleanup

---

## 🔧 Optional Enhancement Tasks

**Priority:** Medium
**Timeline:** Week 2-3

### CodeCov Setup
- [ ] Set up CodeCov account
- [ ] Add CODECOV_TOKEN to GitHub secrets
- [ ] Update GitHub Actions to upload coverage
- [ ] Add codecov badge to README
- [ ] Verify badge works

**Files to modify:**
- `.github/workflows/tests.yml` - Add codecov upload step

**Resources:**
- CodeCov docs: https://docs.codecov.com/docs/quick-start
- GitHub Action: https://github.com/codecov/codecov-action

### OpenSSF Scorecard Setup
- [ ] Visit https://securityscorecards.dev
- [ ] Register empathy-framework repository
- [ ] Review security recommendations
- [ ] Fix any security issues
- [ ] Add OpenSSF badge to README
- [ ] Verify badge works

**Resources:**
- OpenSSF docs: https://github.com/ossf/scorecard
- Badge info: https://securityscorecards.dev/

### GitHub Actions Status Badge
- [ ] Ensure tests.yml workflow exists
- [ ] Verify workflow runs successfully
- [ ] Add Tests badge to README
- [ ] Test badge displays correctly

**Badge URL:**
```markdown
[![Tests](https://github.com/Smart-AI-Memory/empathy-framework/actions/workflows/tests.yml/badge.svg)](https://github.com/Smart-AI-Memory/empathy-framework/actions/workflows/tests.yml)
```

---

## 📊 Additional Badge Ideas

**Priority:** Low
**Timeline:** As needed

### Quality Badges
- [ ] Code Climate maintainability
- [ ] Snyk security scan
- [ ] Better Code Hub
- [ ] Codacy code quality

### Community Badges
- [ ] Discord server (if created)
- [ ] Gitter chat
- [ ] GitHub Discussions

### Stats Badges
- [ ] Total downloads
- [ ] Contributors count
- [ ] Last commit date
- [ ] Repo size

### Documentation Badges
- [ ] Read the Docs
- [ ] Documentation coverage
- [ ] API docs status

---

## 🚨 Troubleshooting Guide

### If Badges Still Show Errors After 48 Hours:

**PyPI Badges:**
1. Clear shields.io cache: Add `?v=1` to URL
2. Try alternative badge services (badgen.net)
3. Check if package name is correct (empathy-framework)
4. Verify package is publicly visible on PyPI

**GitHub Action Badges:**
1. Check workflow file exists in `.github/workflows/`
2. Verify workflow has run at least once
3. Check workflow name matches badge URL
4. Ensure repository is public

**CodeCov Badge:**
1. Verify coverage report is being uploaded
2. Check CodeCov token is set in secrets
3. Ensure repository is linked to CodeCov account
4. Try forcing a sync on CodeCov dashboard

**OpenSSF Badge:**
1. Verify repository is registered
2. Check if first scan has completed
3. May take 24-48 hours for initial scan
4. Check badge URL format is correct

---

## 📝 Badge Restore Template

**When ready to restore, replace README badges section with:**

```markdown
[![License](https://img.shields.io/badge/License-Fair%20Source%200.9-blue.svg)](LICENSE)
[![PyPI version](https://img.shields.io/pypi/v/empathy-framework.svg)](https://pypi.org/project/empathy-framework/)
[![Python 3.10+](https://img.shields.io/pypi/pyversions/empathy-framework.svg)](https://www.python.org/downloads/)
[![Downloads](https://img.shields.io/pypi/dm/empathy-framework.svg)](https://pypi.org/project/empathy-framework/)
[![Tests](https://github.com/Smart-AI-Memory/empathy-framework/actions/workflows/tests.yml/badge.svg)](https://github.com/Smart-AI-Memory/empathy-framework/actions/workflows/tests.yml)
[![codecov](https://codecov.io/gh/Smart-AI-Memory/empathy-framework/branch/main/graph/badge.svg)](https://codecov.io/gh/Smart-AI-Memory/empathy-framework)
[![OpenSSF Scorecard](https://api.securityscorecards.dev/projects/github.com/Smart-AI-Memory/empathy-framework/badge)](https://securityscorecards.dev/viewer/?uri=github.com/Smart-AI-Memory/empathy-framework)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
```

---

## ✅ Quick Test Commands

**Test badge URLs (run on Nov 13-14):**

```bash
# Test if badges return HTTP 200 (success)
curl -I https://img.shields.io/pypi/v/empathy-framework.svg
curl -I https://img.shields.io/pypi/pyversions/empathy-framework.svg
curl -I https://img.shields.io/pypi/dm/empathy-framework.svg

# If you see "HTTP/2 200" → badges are ready!
# If you see "HTTP/2 404" or errors → wait longer
```

**Check PyPI package visibility:**

```bash
# Should return JSON with package info
curl https://pypi.org/pypi/empathy-framework/json | jq '.info.version'

# Should show: "1.6.1"
```

---

## 📅 Timeline Summary

| Date | Task | Status |
|------|------|--------|
| Nov 12 | Package published to PyPI | ✅ Done |
| Nov 12 | Simplified badges committed | ✅ Done |
| Nov 12 | Created badge reminders | ✅ Done |
| **Nov 13** | **Test badge URLs** | ⏳ Pending |
| **Nov 13-14** | **Restore dynamic badges** | ⏳ Pending |
| Nov 14 | Verify badges on GitHub | ⏳ Pending |
| Nov 14 | Clean up reminder files | ⏳ Pending |
| Week 2+ | Optional enhancements | 📋 Backlog |

---

## 🔗 Quick Links

- **Package:** https://pypi.org/project/empathy-framework/
- **Repository:** https://github.com/Smart-AI-Memory/empathy-framework
- **README:** https://github.com/Smart-AI-Memory/empathy-framework/blob/main/README.md
- **Shields.io:** https://shields.io
- **Badge Guide:** https://github.com/badges/shields

---

**Last Updated:** November 12, 2025
**Next Review:** November 13, 2025
**Owner:** Patrick Roebuck
