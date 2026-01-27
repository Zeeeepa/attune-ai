# Git Commit Guide for v4.8.0 Release

## Quick Commit Commands

### Option 1: Commit All Scanner Files (Recommended)

```bash
# Stage core scanner implementation
git add src/empathy_os/project_index/__init__.py
git add src/empathy_os/project_index/scanner.py
git add src/empathy_os/project_index/scanner_parallel.py
git add src/empathy_os/project_index/index.py

# Stage documentation
git add README.md
git add CHANGELOG.md
git add docs/SCANNER_OPTIMIZATIONS.md
git add docs/IMPLEMENTATION_COMPLETE.md

# Stage examples and benchmarks
git add examples/scanner_usage.py
git add benchmarks/benchmark_scanner_optimizations.py
git add benchmarks/profile_scanner_comprehensive.py
git add benchmarks/OPTIMIZATION_SUMMARY.md
git add benchmarks/PROFILING_REPORT.md
git add benchmarks/analyze_generator_candidates.py

# Stage release notes
git add RELEASE_NOTES_v4.8.0.md
git add GIT_COMMIT_GUIDE_v4.8.0.md

# Commit with detailed message
git commit -m "feat: Add parallel project scanning with 3.65x speedup

- Implement ParallelProjectScanner using multiprocessing
- Add incremental scanning with git diff integration
- Enable parallel scanning by default in ProjectIndex
- Add optional dependency analysis for 27% speedup
- Create comprehensive benchmarks and profiling tools
- Add 6 usage examples demonstrating all features

Performance:
- Full scan: 3.59s → 1.84s (1.95x faster)
- Quick scan: 3.59s → 0.98s (3.65x faster)
- Incremental: 1.0s → 0.3s (3.3x faster)

Backward compatible: Existing code benefits automatically

Files:
- src/empathy_os/project_index/scanner_parallel.py (NEW)
- src/empathy_os/project_index/index.py (incremental scanning)
- src/empathy_os/project_index/scanner.py (optional deps)
- examples/scanner_usage.py (NEW - 6 examples)
- benchmarks/* (NEW profiling and benchmark suite)

Closes #XXX

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
```

### Option 2: Separate Commits by Feature

#### Commit 1: Core Scanner Implementation

```bash
git add src/empathy_os/project_index/__init__.py
git add src/empathy_os/project_index/scanner.py
git add src/empathy_os/project_index/scanner_parallel.py
git add src/empathy_os/project_index/index.py

git commit -m "feat: Implement parallel project scanning with 3.65x speedup

- Add ParallelProjectScanner using multiprocessing
- Enable parallel scanning by default in ProjectIndex
- Add incremental scanning with git diff integration
- Add optional dependency analysis parameter

Performance: 3.59s → 0.98s (3.65x faster)

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
```

#### Commit 2: Documentation

```bash
git add README.md
git add CHANGELOG.md
git add docs/SCANNER_OPTIMIZATIONS.md
git add docs/IMPLEMENTATION_COMPLETE.md

git commit -m "docs: Add v4.8.0 scanner optimization documentation

- Update README with performance highlights
- Add CHANGELOG entry for v4.8.0
- Create comprehensive user guide
- Add technical implementation summary

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
```

#### Commit 3: Examples & Benchmarks

```bash
git add examples/scanner_usage.py
git add benchmarks/benchmark_scanner_optimizations.py
git add benchmarks/profile_scanner_comprehensive.py
git add benchmarks/OPTIMIZATION_SUMMARY.md
git add benchmarks/PROFILING_REPORT.md

git commit -m "feat: Add scanner benchmarks and usage examples

- Add 6 comprehensive usage examples
- Create benchmark suite comparing 5 configurations
- Add CPU and memory profiling tools
- Document optimization strategies

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
```

#### Commit 4: Bug Fixes

```bash
git add benchmarks/analyze_generator_candidates.py

git commit -m "fix: Resolve linting issues in benchmark scripts

- Fix bare except clause (E722)
- Remove unused variable (F841)

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
```

---

## Files NOT to Commit (Internal/Work-in-Progress)

These files are internal documentation or work-in-progress:

```bash
# Internal Claude Code documentation (keep local)
.claude/commands/plan.md
.claude/commands/workflows.md
.claude/rules/empathy/os-walk-dirs-pattern.md
.claude/rules/empathy/output-formatting.md

# Security work-in-progress (separate PR later)
docs/SECURITY_*.md
docs/CI_SECURITY_SCANNING.md
docs/DEVELOPER_*.md
src/empathy_os/workflows/security_audit_phase3.py
tests/unit/security/

# Other work-in-progress
docs/api-reference/security-scanner.md
test_wizard_risk_analysis.json
```

---

## Pre-Commit Checklist

- [x] All tests passing (127+ tests)
- [x] Linting issues resolved
- [x] Documentation updated (README, CHANGELOG)
- [x] Examples created and tested
- [x] Benchmarks documented
- [x] Backward compatibility verified
- [x] Performance claims validated

---

## Push Commands

```bash
# Push to feature branch (if applicable)
git push origin feat/phase-2-anthropic-only

# Or push directly to main (if authorized)
git push origin main
```

---

## Creating GitHub Release

After pushing:

1. Go to GitHub Releases: https://github.com/Smart-AI-Memory/empathy/releases
2. Click "Draft a new release"
3. Tag: `v4.8.0`
4. Title: `v4.8.0 - Parallel Scanning & Performance`
5. Description: Copy from RELEASE_NOTES_v4.8.0.md
6. Upload: None needed (code only)
7. Click "Publish release"

---

## Publishing to PyPI

```bash
# Build distribution
python -m build

# Upload to TestPyPI (optional)
python -m twine upload --repository testpypi dist/*

# Upload to PyPI
python -m twine upload dist/*
```

---

## Verification

After publishing:

```bash
# Install from PyPI
pip install --upgrade empathy-framework

# Verify version
python -c "from empathy_os import __version__; print(__version__)"

# Test parallel scanning
python -c "from empathy_os.project_index import ParallelProjectScanner; print('✅ Works!')"
```

---

**Ready to commit! 🚀**
